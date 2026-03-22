#!/usr/bin/env python3
"""
Stage 1: Signal Extraction — Pure Python, $0 cost, every session.

Runs on SessionStart. Analyzes the PREVIOUS session's JSONL for
correction/frustration/positive signals using scoring-based detection.
Stores signals in SQLite. Triggers Stage 2 (pattern analysis) if gate is met.
"""

import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

# Shared DB module (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from self_improve_db import get_db, get_project_root, cleanup_old_data

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MIN_USER_MESSAGES = 4  # Skip short sessions
SIGNAL_GATE = 5  # Unanalyzed signals needed to trigger analysis
CONTEXT_BEFORE = 5  # Messages to keep before trigger
CONTEXT_AFTER = 3  # Messages to keep after trigger
MAX_CANDIDATES = 3  # How many recent sessions to check
RESUME_DELTA_THRESHOLD = 4  # Min new user messages to re-extract a resumed session
ANALYSIS_COOLDOWN_MINUTES = 10  # Min minutes between analysis runs


def log(msg: str) -> None:
    print(f"[self-improve-extract] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------


def normalize(text: str) -> str:
    """Lowercase, collapse repeated chars (nooo→no, stooop→stop)."""
    text = text.lower().strip()
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)  # Keep max 2 repeats
    return text


# ---------------------------------------------------------------------------
# Scoring-based signal indicators
# ---------------------------------------------------------------------------
# Each indicator has a weight. A message triggers a signal when its total
# score meets the threshold. This replaces single-pattern-match to catch
# messages like "no no it's not working like that" where no single pattern
# is definitive but multiple weak indicators combine into a clear signal.

MAX_USER_MSG_LEN = 500  # Skip messages longer than this (likely discussion, not correction)

# Correction indicators: (pattern, weight)
# Strong (2): clearly directive — user telling Claude it did wrong
# Weak (1): negative language that needs corroboration
CORRECTION_INDICATORS = [
    # Strong (2) — clearly directive, user telling Claude it did wrong
    (re.compile(r"\bi\s+(?:said|say|told|meant?)\b", re.IGNORECASE), 2),
    (re.compile(r"\bi\s+didn'?t\s+(?:ask|say|want|mean)\b", re.IGNORECASE), 2),
    (re.compile(r"\bnot\s+what\s+i\b", re.IGNORECASE), 2),
    (re.compile(r"\bpls?\s+(?:don'?t|no)\b", re.IGNORECASE), 2),
    (re.compile(r"\bstop\s+(?:doing|it|that|this)\b", re.IGNORECASE), 2),
    (re.compile(r"\balr(?:ea)?dy\b.*\btold\b", re.IGNORECASE), 2),
    (re.compile(r"\bwhy\s+(?:you|did\s+(?:you|u)|u)\b", re.IGNORECASE), 2),
    (re.compile(r"\bno[,.\s]+not\b", re.IGNORECASE), 2),
    (re.compile(r"\bdon'?t\s+(?:do|change|add|remove|delete|touch|use|modify|make|put)\b", re.IGNORECASE), 2),
    (re.compile(r"\brevert\s+(?:it|that|this|the|back)\b", re.IGNORECASE), 2),
    (re.compile(r"\bundo\s+(?:it|that|this|the)\b", re.IGNORECASE), 2),
    # Quality complaints — user saying Claude's output is bad
    (re.compile(r"\b(?:you|it|that|this)\b.*\b(?:bad|terrible|awful|horrible|ugly)\b", re.IGNORECASE), 2),
    (re.compile(r"\b(?:a\s+)?mess(?:y|ed\s+up)?\b", re.IGNORECASE), 1),
    (re.compile(r"\bbrok(?:e|en)\b", re.IGNORECASE), 1),
    # Weak (1) — need corroboration from other indicators
    (re.compile(r"\bwrong\b", re.IGNORECASE), 1),
    (re.compile(r"\bdnt\b", re.IGNORECASE), 1),
    # Very weak (0.5) — common words, only meaningful when combined with others
    (re.compile(r"\bnot\b", re.IGNORECASE), 0.5),
    (re.compile(r"\bno\b", re.IGNORECASE), 0.5),
]

CORRECTION_THRESHOLD = 2  # Minimum score to trigger a correction signal

# Frustration indicators: (pattern, weight)
# Strong (2): unambiguous emotional markers
# Weak (1): ambiguous alone, need corroboration
FRUSTRATION_INDICATORS = [
    (re.compile(r"\?{3,}"), 2),
    (re.compile(r"!{3,}"), 2),
    (re.compile(r"\bc'?mon\b", re.IGNORECASE), 2),
    (re.compile(r"\bcome\s+on\b", re.IGNORECASE), 2),
    (re.compile(r"\bomg\b", re.IGNORECASE), 2),
    (re.compile(r"\bwtf\b", re.IGNORECASE), 2),
    (re.compile(r"\bwth\b", re.IGNORECASE), 2),
    (re.compile(r"\bugh+\b", re.IGNORECASE), 2),
    (re.compile(r"\bsigh\b", re.IGNORECASE), 2),
    (re.compile(r"\bagain\s*[?!]", re.IGNORECASE), 2),
    (re.compile(r"\bsrsly\b", re.IGNORECASE), 2),
    # Profanity — strong frustration signal
    (re.compile(r"\bf+u+c+k+", re.IGNORECASE), 2),
    (re.compile(r"\bshit+\b", re.IGNORECASE), 2),
    (re.compile(r"\b(?:what\s+)?the\s+hell\b", re.IGNORECASE), 2),
    (re.compile(r"\bdamn(?:it)?\b", re.IGNORECASE), 1),
    (re.compile(r"\bcrap\b", re.IGNORECASE), 1),
    # Disbelief — often signals frustration
    (re.compile(r"\bwhat\s*\?", re.IGNORECASE), 1),
    (re.compile(r"\breally\s*\?", re.IGNORECASE), 1),
    (re.compile(r"\bhuh\s*\?", re.IGNORECASE), 1),
    (re.compile(r"\bexcuse\s+me\b", re.IGNORECASE), 2),
    # Weak — ambiguous alone, need corroboration
    (re.compile(r"\bserious(?:ly)?\b", re.IGNORECASE), 1),
]

FRUSTRATION_THRESHOLD = 2

# Positive indicators: confirming a non-obvious approach worked well
POSITIVE_INDICATORS = [
    (re.compile(r"\bperfect\b", re.IGNORECASE), 2),
    (re.compile(r"\bexactly\b", re.IGNORECASE), 2),
    (re.compile(r"\blove\s+it\b", re.IGNORECASE), 2),
    (re.compile(r"\bthat(?:'?s|s)?\s+it\b", re.IGNORECASE), 2),
    (re.compile(r"\bnailed\s+it\b", re.IGNORECASE), 2),
    (re.compile(r"\b(?:great|good|nice)\s+job\b", re.IGNORECASE), 2),
    (re.compile(r"\bwell\s+done\b", re.IGNORECASE), 2),
    (re.compile(r"\bmuch\s+better\b", re.IGNORECASE), 2),
    (re.compile(r"\bawesome\b", re.IGNORECASE), 2),
    (re.compile(r"\bthis\s+is\s+what\s+i\s+(?:need|want)\b", re.IGNORECASE), 2),
]

POSITIVE_THRESHOLD = 2

# Markers that identify injected system content (not real user messages)
SYSTEM_CONTENT_MARKERS = [
    "Base directory for this skill:",
    "<system-reminder>",
    "<command-name>",
    "<command-message>",
    "<local-command-caveat>",
]


# ---------------------------------------------------------------------------
# Parse session JSONL into event sequence
# ---------------------------------------------------------------------------


def _is_system_content(text: str) -> bool:
    """Check if a user message is actually injected system content."""
    for marker in SYSTEM_CONTENT_MARKERS:
        if marker in text:
            return True
    return False


def parse_session(session_path: str) -> list[dict]:
    """Parse session JSONL into a flat list of events.

    Filters out injected system content (skills, system reminders, commands)
    that appears as "type": "user" in the JSONL but isn't real user speech.
    """
    events = []

    with open(session_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            rec_type = record.get("type")
            message = record.get("message", {})
            content = message.get("content")

            if rec_type == "user":
                text = ""
                if isinstance(content, list):
                    texts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            texts.append(block["text"])
                        elif isinstance(block, str):
                            texts.append(block)
                    text = " ".join(texts).strip()
                elif isinstance(content, str):
                    text = content.strip()

                if text and not _is_system_content(text):
                    events.append(
                        {"role": "user", "text": text, "tool_name": None, "tool_file": None}
                    )

            elif rec_type == "assistant" and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_name = block.get("name", "?")
                        tool_input = block.get("input", {})
                        tool_file = tool_input.get("file_path") or tool_input.get("path") or None
                        brief = json.dumps(tool_input, ensure_ascii=False)
                        if len(brief) > 150:
                            brief = brief[:147] + "..."
                        events.append(
                            {
                                "role": "assistant_tool",
                                "text": f"{tool_name}({brief})",
                                "tool_name": tool_name,
                                "tool_file": str(tool_file) if tool_file else None,
                            }
                        )
                    elif isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "").strip()
                        if text:
                            events.append(
                                {
                                    "role": "assistant_text",
                                    "text": text,
                                    "tool_name": None,
                                    "tool_file": None,
                                }
                            )

    return events


# ---------------------------------------------------------------------------
# Context extraction
# ---------------------------------------------------------------------------


def get_context(events: list[dict], idx: int) -> dict:
    """Get surrounding messages for context around a trigger event."""
    start = max(0, idx - CONTEXT_BEFORE)
    end = min(len(events), idx + CONTEXT_AFTER + 1)

    def fmt(e: dict) -> str:
        role = "USER" if e["role"] == "user" else "CLAUDE"
        return f"{role}: {e['text'][:200]}"

    return {
        "before": [fmt(e) for e in events[start:idx]],
        "after": [fmt(e) for e in events[idx + 1 : end]],
    }


# ---------------------------------------------------------------------------
# Signal detection
# ---------------------------------------------------------------------------


def preceded_by_action(events: list[dict], idx: int, window: int = 3) -> bool:
    """Check if a user message was preceded by Claude Edit/Write/Bash."""
    for j in range(max(0, idx - window), idx):
        if events[j]["role"] == "assistant_tool" and events[j]["tool_name"] in (
            "Edit",
            "Write",
            "Bash",
        ):
            return True
    return False


def _score_indicators(text: str, indicators: list[tuple]) -> int:
    """Sum weights of all matching indicators in text."""
    score = 0
    for pattern, weight in indicators:
        if pattern.search(text):
            score += weight
    return score


def detect_signals(events: list[dict]) -> list[dict]:
    """Scan events for correction/frustration/positive signals using scoring."""
    signals = []
    seen_triggers = set()

    for i, event in enumerate(events):
        if event["role"] != "user":
            continue

        text = event["text"]

        # Skip long messages — likely discussion, not correction
        if len(text.strip()) > MAX_USER_MSG_LEN:
            continue

        normalized = normalize(text)
        trigger_key = text[:300]

        if trigger_key in seen_triggers:
            continue

        has_action = preceded_by_action(events, i)

        # --- Correction (score-based) ---
        score = _score_indicators(normalized, CORRECTION_INDICATORS)
        # Boost: short message right after Claude action = more likely a correction
        # Only boost if there's already some signal (score >= 1), to avoid
        # promoting completely innocent messages like "it's not a big deal"
        if has_action and len(text.strip()) < 100 and score >= 1:
            score += 1
        if score >= CORRECTION_THRESHOLD:
            confidence = "high" if (score >= 3 or has_action) else "medium"
            signals.append(
                {
                    "signal_type": "correction",
                    "confidence": confidence,
                    "trigger_msg": trigger_key,
                    "context": get_context(events, i),
                }
            )
            seen_triggers.add(trigger_key)
            continue

        # --- Frustration (score-based) ---
        score = _score_indicators(normalized, FRUSTRATION_INDICATORS)
        if score >= FRUSTRATION_THRESHOLD:
            signals.append(
                {
                    "signal_type": "frustration",
                    "confidence": "high" if has_action else "medium",
                    "trigger_msg": trigger_key,
                    "context": get_context(events, i),
                }
            )
            seen_triggers.add(trigger_key)
            continue

        # --- Positive (skip very short messages to reduce noise) ---
        if len(text.strip()) > 10:
            score = _score_indicators(normalized, POSITIVE_INDICATORS)
            if score >= POSITIVE_THRESHOLD:
                signals.append(
                    {
                        "signal_type": "positive",
                        "confidence": "medium",
                        "trigger_msg": trigger_key,
                        "context": get_context(events, i),
                    }
                )
                seen_triggers.add(trigger_key)

    return signals


# ---------------------------------------------------------------------------
# Find previous session JSONL
# ---------------------------------------------------------------------------


def find_candidate_sessions(project_root: str) -> list[str]:
    """Find up to MAX_CANDIDATES recent session JSONLs (excluding current)."""
    projects_dir = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    encoded = project_root.replace("/", "-")
    session_dir = os.path.join(projects_dir, encoded)

    if not os.path.isdir(session_dir):
        return []

    jsonl_files = sorted(
        glob.glob(os.path.join(session_dir, "*.jsonl")),
        key=os.path.getmtime,
        reverse=True,
    )

    # Skip index 0 (current session), return next N candidates
    return jsonl_files[1 : 1 + MAX_CANDIDATES] if len(jsonl_files) >= 2 else []


def count_user_messages(session_path: str) -> int:
    """Quick count of user messages in a session JSONL."""
    count = 0
    with open(session_path, "r", encoding="utf-8") as f:
        for line in f:
            if '"type":"user"' in line or '"type": "user"' in line:
                count += 1
    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _should_process(conn: sqlite3.Connection, session_id: str, session_path: str) -> bool:
    """Decide if a session needs (re-)extraction.

    Returns True if:
    - Session was never extracted, OR
    - Session was extracted but has grown by RESUME_DELTA_THRESHOLD+ user messages (resumed session)
    """
    current_count = count_user_messages(session_path)
    row = conn.execute(
        "SELECT extracted, message_count FROM sessions WHERE session_id = ?", (session_id,)
    ).fetchone()

    if not row or not row["extracted"]:
        if current_count < MIN_USER_MESSAGES:
            # Mark short sessions so we don't re-check them every time
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "INSERT OR REPLACE INTO sessions (session_id, extracted, signal_count, message_count, created_at) "
                "VALUES (?, 1, 0, ?, ?)",
                (session_id, current_count, now),
            )
            conn.commit()
            return False
        return True

    # Already extracted — check if resumed with enough new messages
    prev_count = row["message_count"] or 0
    delta = current_count - prev_count
    if delta >= RESUME_DELTA_THRESHOLD:
        log(f"Session {session_id} grew by {delta} messages (resumed), re-extracting")
        # Clear old signals for this session before re-extraction
        conn.execute("DELETE FROM signals WHERE session_id = ? AND analyzed = 0", (session_id,))
        conn.commit()
        return True

    return False


def _is_inline_mode() -> bool:
    """Check if Claude was invoked with -p/--print (inline mode)."""
    try:
        ppid = os.getppid()
        result = subprocess.run(
            ["ps", "-p", str(ppid), "-o", "args="],
            capture_output=True, text=True, timeout=2,
        )
        tokens = result.stdout.strip().split()
        return "-p" in tokens or "--print" in tokens
    except Exception:
        return False


def main() -> None:
    if _is_inline_mode():
        return

    project_root = get_project_root()

    candidates = find_candidate_sessions(project_root)
    if not candidates:
        return

    conn = get_db(project_root)
    try:
        for session_path in candidates:
            session_id = os.path.splitext(os.path.basename(session_path))[0]

            if not _should_process(conn, session_id, session_path):
                continue

            # Parse and detect signals
            msg_count = count_user_messages(session_path)
            log(f"Extracting signals from session {session_id}")
            events = parse_session(session_path)
            signals = detect_signals(events)

            # Store signals
            now = datetime.now(timezone.utc).isoformat()
            for sig in signals:
                conn.execute(
                    "INSERT INTO signals (session_id, signal_type, confidence, trigger_msg, context, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        session_id,
                        sig["signal_type"],
                        sig["confidence"],
                        sig["trigger_msg"],
                        json.dumps(sig["context"], ensure_ascii=False),
                        now,
                    ),
                )

            # Mark session as extracted with message count
            conn.execute(
                "INSERT OR REPLACE INTO sessions (session_id, extracted, signal_count, message_count, created_at) "
                "VALUES (?, 1, ?, ?, ?)",
                (session_id, len(signals), msg_count, now),
            )
            conn.commit()

            log(f"Extracted {len(signals)} signals from session {session_id}")
            break  # Process one session per SessionStart to keep hook fast

        # Check gate and trigger analysis if needed
        _check_gate_and_trigger(conn, project_root)

        # Cleanup old data every run
        cleanup_old_data(conn)

    finally:
        conn.close()


def _check_gate_and_trigger(conn: sqlite3.Connection, project_root: str) -> None:
    """If enough unanalyzed signals and cooldown elapsed, launch pattern analysis."""
    row = conn.execute("SELECT COUNT(*) as cnt FROM signals WHERE analyzed = 0").fetchone()
    unanalyzed = row["cnt"] if row else 0

    if unanalyzed < SIGNAL_GATE:
        return

    # Batch cooldown: skip if last analysis was too recent
    last_batch = conn.execute(
        "SELECT MAX(created_at) as last_at FROM proposals"
    ).fetchone()
    if last_batch and last_batch["last_at"]:
        try:
            last_dt = datetime.fromisoformat(last_batch["last_at"].replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds() / 60
            if elapsed < ANALYSIS_COOLDOWN_MINUTES:
                log(f"Gate met ({unanalyzed} signals) but cooldown active ({elapsed:.0f}m < {ANALYSIS_COOLDOWN_MINUTES}m). Skipping.")
                return
        except (ValueError, TypeError):
            pass  # Can't parse — proceed with analysis

    log(f"Gate met: {unanalyzed} unanalyzed signals. Launching pattern analysis.")

    analyzer = os.path.join(project_root, ".claude", "hooks", "self-improve", "self-improve-analyze.py")
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    subprocess.Popen(
        ["python3", analyzer],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=project_root,
        env=env,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(0)  # Never crash the session
