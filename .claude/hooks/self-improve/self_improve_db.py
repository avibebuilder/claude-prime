#!/usr/bin/env python3
"""
Shared database module for the self-improvement pipeline.

Provides schema, connection factory, and helper queries used by all three stages.
Usage as module: from self_improve_db import get_db, get_project_root
Usage as CLI:   python3 self_improve_db.py resolve list
                python3 self_improve_db.py resolve <id>[,<id>,...] approved|rejected
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

ANNOUNCEMENT_MARKER = "🧠"

SCHEMA = """
CREATE TABLE IF NOT EXISTS signals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    confidence  TEXT NOT NULL,
    trigger_msg TEXT NOT NULL,
    context     TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    analyzed    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS proposals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id        TEXT NOT NULL,
    theme           TEXT NOT NULL,
    signal_ids      TEXT NOT NULL,
    content         TEXT NOT NULL,
    rationale       TEXT NOT NULL,
    status          TEXT DEFAULT 'pending',
    created_at      TEXT NOT NULL,
    resolved_at     TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id    TEXT PRIMARY KEY,
    extracted     INTEGER DEFAULT 0,
    signal_count  INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def get_project_root() -> str:
    """Derive project root from CLAUDE_PROJECT_DIR or script location."""
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return env_root
    # Script is at .claude/hooks/self-improve/self_improve_db.py — go up 3 levels
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_db(project_root: str) -> sqlite3.Connection:
    """Open (and auto-create) the self-improve SQLite database."""
    db_path = os.path.join(project_root, ".claude", "local-data", "self-improve.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    # Migrate: add message_count column if missing (existing DBs)
    try:
        conn.execute("SELECT message_count FROM sessions LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE sessions ADD COLUMN message_count INTEGER DEFAULT 0")
        conn.commit()
    conn.row_factory = sqlite3.Row
    return conn


def cleanup_old_data(conn: sqlite3.Connection, days: int = 9) -> None:
    """Delete all data older than `days` (signals, proposals, sessions, invocations)."""
    conn.execute(
        "DELETE FROM signals WHERE created_at < datetime('now', ?)",
        (f"-{days} days",),
    )
    conn.execute(
        "DELETE FROM proposals WHERE created_at < datetime('now', ?)",
        (f"-{days} days",),
    )
    conn.execute(
        "DELETE FROM sessions WHERE created_at < datetime('now', ?)",
        (f"-{days} days",),
    )
    conn.commit()


def list_pending_proposals(project_root: str) -> None:
    """Print pending proposals as JSON for CLI consumers."""
    conn = get_db(project_root)
    try:
        rows = conn.execute(
            "SELECT id, theme, content, rationale FROM proposals WHERE status = 'pending' ORDER BY created_at"
        ).fetchall()
        print(
            json.dumps(
                [dict(row) for row in rows],
                indent=2,
            )
        )
    finally:
        conn.close()


def resolve_proposal(project_root: str, proposal_ids: list[int], status: str) -> None:
    """Mark one or more proposals as approved or rejected."""
    conn = get_db(project_root)
    try:
        now = datetime.now(timezone.utc).isoformat()
        for proposal_id in proposal_ids:
            conn.execute(
                "UPDATE proposals SET status = ?, resolved_at = ? WHERE id = ?",
                (status, now, proposal_id),
            )
        conn.commit()
        if len(proposal_ids) == 1:
            print(f"Proposal {proposal_ids[0]} marked as {status}")
        else:
            print(f"Proposals {','.join(map(str, proposal_ids))} marked as {status}")

        # If no more pending proposals, clear announcement and reset dismiss count
        remaining = conn.execute(
            "SELECT COUNT(*) as cnt FROM proposals WHERE status = 'pending'"
        ).fetchone()
        if remaining[0] == 0:
            clear_announcement(project_root)
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES ('dismiss_count', '0')"
            )
            conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# settings.local.json announcement helpers
# ---------------------------------------------------------------------------

def _settings_local_path(project_root: str) -> str:
    return os.path.join(project_root, ".claude", "settings.local.json")


def _read_settings_local(project_root: str) -> dict:
    path = _settings_local_path(project_root)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _write_settings_local(project_root: str, data: dict) -> None:
    path = _settings_local_path(project_root)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def set_announcement(project_root: str, message: str) -> None:
    """Add a self-improve announcement to settings.local.json."""
    data = _read_settings_local(project_root)
    announcements = data.get("companyAnnouncements", [])
    # Remove existing self-improve announcements
    announcements = [a for a in announcements if not a.startswith(ANNOUNCEMENT_MARKER)]
    announcements.append(message)
    data["companyAnnouncements"] = announcements
    _write_settings_local(project_root, data)


def clear_announcement(project_root: str) -> None:
    """Remove self-improve announcements from settings.local.json."""
    data = _read_settings_local(project_root)
    announcements = data.get("companyAnnouncements", [])
    filtered = [a for a in announcements if not a.startswith(ANNOUNCEMENT_MARKER)]
    if filtered:
        data["companyAnnouncements"] = filtered
    elif "companyAnnouncements" in data:
        del data["companyAnnouncements"]
    else:
        return  # Nothing to clear
    _write_settings_local(project_root, data)


# ---------------------------------------------------------------------------
# CLI interface for resolve
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "resolve" and sys.argv[2] == "list":
        list_pending_proposals(get_project_root())
    elif len(sys.argv) >= 4 and sys.argv[1] == "resolve":
        try:
            id_arg = sys.argv[2]
            prop_ids = [int(x.strip()) for x in id_arg.split(",")]
            new_status = sys.argv[3]
            if new_status not in ("approved", "rejected"):
                print(f"Invalid status: {new_status}. Use 'approved' or 'rejected'.")
                sys.exit(1)
            resolve_proposal(get_project_root(), prop_ids, new_status)
        except ValueError:
            print(f"Invalid proposal ID(s): {sys.argv[2]}")
            sys.exit(1)
    else:
        print("Usage: python3 self_improve_db.py resolve list")
        print("       python3 self_improve_db.py resolve <id>[,<id>,...] approved|rejected")
        sys.exit(1)
