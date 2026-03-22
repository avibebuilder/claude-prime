#!/usr/bin/env python3
"""
Stage 2: Pattern Analysis — Sonnet, batched, only when gate is met.

Reads unanalyzed signals from SQLite, sends them to Sonnet for pattern
detection, and stores proposals back in the database.

Called by self-improve-extract.py in the background when signal gate is met.
"""

import fcntl
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from self_improve_db import get_db, get_project_root

MAX_PROPOSALS = 2

ANALYSIS_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "patterns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "signal_ids": {"type": "array", "items": {"type": "integer"}},
                    "proposed_change": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["theme", "signal_ids", "proposed_change", "rationale"],
            },
        },
        "noise": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "signal_id": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["signal_id", "reason"],
            },
        },
    },
    "required": ["patterns", "noise"],
})

LOG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "local-data", "analysis-last.log"
)


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [self-improve-analyze] {msg}\n"
    print(line, end="", file=sys.stderr)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Collect existing rules (for dedup)
# ---------------------------------------------------------------------------


def get_existing_rules(project_root: str) -> list[str]:
    """List existing rule files so Sonnet can avoid duplicates."""
    rules_dir = os.path.join(project_root, ".claude", "rules")
    if not os.path.isdir(rules_dir):
        return []

    rules = []
    for fpath in glob.glob(os.path.join(rules_dir, "*.md")):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            rules.append(f"File: {os.path.basename(fpath)}\n{content[:500]}")
        except Exception:
            pass
    return rules


# ---------------------------------------------------------------------------
# Build analysis prompt
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT = """Analyze these behavioral signals from Claude Code sessions. Find recurring PATTERNS worth fixing.

## Signals

{signals_json}

## Existing rules (DO NOT duplicate)

{existing_rules}

## Instructions

1. Group related signals by theme (use short-kebab-name for theme)
2. ONLY propose changes for patterns seen 2+ times across DIFFERENT sessions
3. Single occurrences are noise — put them in the noise array
4. Users are NOT always right — verify technical merit
5. Positive signals: note non-obvious approaches only

## Rules
- Max {max_proposals} patterns
- Keep each proposed_change under 100 words
- Empty patterns array if nothing recurs — forcing insights is worse than none
- Do NOT suggest where to put the change — just describe WHAT should change
- If an existing rule already covers the theme, return empty patterns — do NOT create a duplicate"""


def build_prompt(signals: list[dict], existing_rules: list[str]) -> str:
    """Build the analysis prompt with signals and existing rules."""
    signals_formatted = json.dumps(
        [
            {
                "id": s["id"],
                "session_id": s["session_id"],
                "signal_type": s["signal_type"],
                "confidence": s["confidence"],
                "trigger_msg": s["trigger_msg"],
                "context": json.loads(s["context"]) if isinstance(s["context"], str) else s["context"],
            }
            for s in signals
        ],
        indent=2,
        ensure_ascii=False,
    )

    rules_text = "\n\n".join(existing_rules) if existing_rules else "(no existing rules)"

    return ANALYSIS_PROMPT.format(
        signals_json=signals_formatted,
        existing_rules=rules_text,
        max_proposals=MAX_PROPOSALS,
    )


# ---------------------------------------------------------------------------
# Run claude CLI
# ---------------------------------------------------------------------------


def run_analysis(prompt: str, project_root: str) -> dict | None:
    """Call claude -p --model sonnet and return parsed JSON."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    env["CLAUDE_SILENT"] = "1"

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json", "--model", "sonnet", "--json-schema", ANALYSIS_SCHEMA],
            capture_output=True,
            text=True,
            cwd=project_root,
            env=env,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        log("claude -p timed out after 120s")
        return None
    except FileNotFoundError:
        log("claude CLI not found on PATH")
        return None

    if result.returncode != 0:
        log(f"claude -p exited {result.returncode}: {result.stderr[:200]}")
        return None

    # Parse outer JSON wrapper
    try:
        outer = json.loads(result.stdout)
    except json.JSONDecodeError:
        log(f"Failed to parse claude output: {result.stdout[:200]}...{result.stdout[-20:]}")
        return None

    # With --json-schema, result is in structured_output (already a dict)
    structured = outer.get("structured_output")
    if isinstance(structured, dict):
        return structured

    # Fallback: parse from result text (when --json-schema is not used)
    inner_text = outer.get("result", "")
    if not inner_text:
        log("Empty result from claude")
        return None

    inner_text = inner_text.strip()
    if inner_text.startswith("```"):
        inner_text = re.sub(r"^```[a-z]*\n?", "", inner_text)
        inner_text = re.sub(r"\n?```\s*$", "", inner_text)

    try:
        return json.loads(inner_text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", inner_text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        log(f"Failed to parse analysis JSON: {inner_text[:200]}")
        return None


# ---------------------------------------------------------------------------
# Store proposals
# ---------------------------------------------------------------------------


def _theme_words(theme: str) -> set[str]:
    """Extract words from a theme for fuzzy matching."""
    return set(re.findall(r"[a-z]+", theme.lower()))


def _is_duplicate_theme(conn, theme: str) -> bool:
    """Check if a pending proposal with a similar theme already exists."""
    existing = conn.execute(
        "SELECT theme FROM proposals WHERE status = 'pending'"
    ).fetchall()

    new_words = _theme_words(theme)
    if not new_words:
        return False

    for row in existing:
        existing_words = _theme_words(row["theme"])
        if not existing_words:
            continue
        overlap = len(new_words & existing_words)
        union = len(new_words | existing_words)
        # Exact match or >50% word overlap = duplicate
        if row["theme"] == theme or (union > 0 and overlap / union > 0.5):
            return True

    return False


def store_proposals(conn, analysis: dict, batch_id: str) -> int:
    """Write proposals from analysis result into DB, skipping duplicates. Returns count."""
    patterns = analysis.get("patterns", [])
    now = datetime.now(timezone.utc).isoformat()
    written = 0
    skipped = 0

    for pattern in patterns[:MAX_PROPOSALS]:
        proposed_change = pattern.get("proposed_change", "")
        if not proposed_change:
            continue

        theme = pattern.get("theme", "untitled")
        if _is_duplicate_theme(conn, theme):
            skipped += 1
            log(f"Skipping duplicate theme: {theme}")
            continue

        conn.execute(
            "INSERT INTO proposals "
            "(batch_id, theme, signal_ids, content, rationale, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (
                batch_id,
                theme,
                json.dumps(pattern.get("signal_ids", [])),
                proposed_change,
                pattern.get("rationale", ""),
                now,
            ),
        )
        written += 1

    conn.commit()
    if skipped:
        log(f"Skipped {skipped} duplicate proposal(s)")
    return written


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Clear log file at start of each run
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        open(LOG_FILE, "w").close()
    except OSError:
        pass

    project_root = get_project_root()
    conn = get_db(project_root)

    try:
        # Fetch unanalyzed signals
        rows = conn.execute(
            "SELECT id, session_id, signal_type, confidence, trigger_msg, context, created_at "
            "FROM signals WHERE analyzed = 0 ORDER BY created_at"
        ).fetchall()

        if not rows:
            log("No unanalyzed signals")
            return

        signals = [dict(r) for r in rows]
        signal_ids = [s["id"] for s in signals]

        log(f"Analyzing {len(signals)} signals from {len(set(s['session_id'] for s in signals))} sessions")

        # Get existing rules for context
        existing_rules = get_existing_rules(project_root)

        # Build prompt and run analysis
        prompt = build_prompt(signals, existing_rules)
        analysis = run_analysis(prompt, project_root)

        if analysis is None:
            log("Analysis failed")
            return

        # Store proposals
        batch_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        prop_count = store_proposals(conn, analysis, batch_id)

        # Mark all signals as analyzed
        placeholders = ",".join("?" for _ in signal_ids)
        conn.execute(
            f"UPDATE signals SET analyzed = 1 WHERE id IN ({placeholders})",
            signal_ids,
        )
        conn.commit()

        log(f"Done. {prop_count} proposals from {len(signals)} signals.")

    finally:
        conn.close()


if __name__ == "__main__":
    # File lock: claude -p triggers SessionStart hooks, which can spawn
    # another analyzer while this one is still running (chain reaction).
    lock_path = os.path.join(os.path.dirname(LOG_FILE), "analyze.lock")
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.exit(0)  # Another instance is running, exit silently

    try:
        main()
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
