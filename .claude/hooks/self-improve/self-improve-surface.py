#!/usr/bin/env python3
"""
Stage 3: Surface Proposals — runs on SessionStart, rate-limited.

Checks SQLite for pending proposals and surfaces them via:
- companyAnnouncements in settings.local.json (user-facing UI message)
- stdout (structured context for Claude to act on when user says 'self-evolve' or similar)

Uses exponential backoff: shows after 1, 3, 6, 9, 12 sessions.
Max 5 attempts per cycle. 4-hour threshold resets the cycle.
"""

import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from self_improve_db import (
    get_db,
    get_project_root,
    set_announcement,
    clear_announcement,
    ANNOUNCEMENT_MARKER,
)

HOURS_THRESHOLD = 4
BACKOFF_THRESHOLDS = [1, 3, 6, 9, 12]
MAX_DISMISS = len(BACKOFF_THRESHOLDS)


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
    conn = get_db(project_root)

    try:
        # --- Increment session counter ---
        row = conn.execute(
            "SELECT value FROM config WHERE key = 'session_count'"
        ).fetchone()
        session_count = int(row["value"]) + 1 if row else 1
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES ('session_count', ?)",
            (str(session_count),),
        )

        # --- Get dismiss count ---
        row = conn.execute(
            "SELECT value FROM config WHERE key = 'dismiss_count'"
        ).fetchone()
        dismiss_count = int(row["value"]) if row else 0

        # --- Get last surface time ---
        row = conn.execute(
            "SELECT value FROM config WHERE key = 'last_surface_at'"
        ).fetchone()
        last_surface = row["value"] if row else "1970-01-01T00:00:00+00:00"

        conn.commit()

        # --- Check 4-hour reset ---
        try:
            last_dt = datetime.fromisoformat(last_surface.replace("Z", "+00:00"))
        except ValueError:
            last_dt = datetime.min.replace(tzinfo=timezone.utc)
        time_ok = (datetime.now(timezone.utc) - last_dt) > timedelta(
            hours=HOURS_THRESHOLD
        )

        if time_ok:
            dismiss_count = 0
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES ('dismiss_count', '0')"
            )
            conn.commit()

        # --- Check if we've maxed out attempts ---
        if dismiss_count >= MAX_DISMISS:
            clear_announcement(project_root)
            return

        # --- Check if session count meets backoff threshold ---
        threshold = BACKOFF_THRESHOLDS[dismiss_count]
        if session_count < threshold:
            clear_announcement(project_root)
            return

        # --- Fetch pending proposals ---
        rows = conn.execute(
            "SELECT id, theme, content, rationale "
            "FROM proposals WHERE status = 'pending' ORDER BY created_at"
        ).fetchall()

        if rows:
            _surface_proposals(conn, rows, dismiss_count, project_root)
        else:
            clear_announcement(project_root)

    finally:
        conn.close()


def _surface_proposals(conn, rows, dismiss_count: int, project_root: str) -> None:
    """Surface pending proposals via announcement + structured stdout."""
    n = len(rows)

    # --- Write user-facing announcement to settings.local.json ---
    announcement = (
        f"{ANNOUNCEMENT_MARKER} I have {n} self-improvement proposal"
        f"{'s' if n != 1 else ''} from recent sessions! "
        f'Say "/self-evolve" or similar to review.'
    )
    set_announcement(project_root, announcement)

    print(
        "<self_improve_surface>"
        f"You have {n} pending self-improvement proposal(s). "
        "The user may not see a UI banner (e.g. VS Code extension). "
        "At the END of your first response (after addressing whatever the user asked), "
        "briefly hint user that we have {n} thing(s) for self-improvements, let open a new tab/conversation and run /self-evolve to review them. (format: > your-text with funny tones and emojis) "
        "Keep it to one short sentence — do not interrupt their workflow or front-load it."
        "</self_improve_surface>"
    )

    # --- Update counters --- 
    conn.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES ('session_count', '0')"
    )
    conn.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES ('dismiss_count', ?)",
        (str(dismiss_count + 1),),
    )
    conn.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES ('last_surface_at', ?)",
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[self-improve-surface] Error: {e}", file=sys.stderr)
        sys.exit(0)  # Never crash the session
