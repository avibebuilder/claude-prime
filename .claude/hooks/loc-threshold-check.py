#!/usr/bin/env python3
"""
LOC Threshold Check - PostToolUse Hook

Analyzes files modified via Write/Edit tools and suggests modularization
for files exceeding the line count threshold. Non-blocking implementation.

Exit Codes:
    0 - Success (non-blocking, allows continuation)
"""

import json
import os
import sys

# Constants
LOC_THRESHOLD = 300
DEBUG = os.environ.get("LOC_THRESHOLD_CHECK_DEBUG") == "true"


def debug_log(message: str) -> None:
    """Log diagnostic info to stderr (opt-in via env var)."""
    if DEBUG:
        print(f"[loc-threshold-check] {message}", file=sys.stderr)


def main() -> None:
    try:
        # Read hook payload from stdin
        stdin = sys.stdin.read().strip()

        if not stdin:
            sys.exit(0)

        payload = json.loads(stdin)
        debug_log(f"Hook triggered for tool: {payload.get('tool_name', 'unknown')}")

        # Extract file path from tool input
        file_path = payload.get("tool_input", {}).get("file_path")

        if not file_path:
            debug_log("No file path in payload; skipping.")
            sys.exit(0)

        # Skip .claude directory files
        if "/.claude/" in file_path or file_path.startswith(".claude"):
            debug_log(f"Skipping .claude path: {file_path}")
            sys.exit(0)

        # Check if file exists
        if not os.path.isfile(file_path):
            debug_log(f"File not found at path: {file_path}")
            sys.exit(0)

        # Read file and count lines
        with open(file_path, "r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)

        debug_log(f"File {file_path} has {lines} LOC.")

        # Check if modularization suggestion is warranted
        if lines > LOC_THRESHOLD:
            relative_path = os.path.relpath(file_path, os.getcwd())
            debug_log(f"LOC threshold exceeded for {relative_path}.")

            output = {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": "\n".join([
                        f"⚠️ ACTION NEEDED: {relative_path} has {lines} LOC (threshold: {LOC_THRESHOLD}).",
                        "Complete your current task first, then consider to modularize this file:",
                        "- Identify logical boundaries (functions, classes, concerns)",
                        "- Extract into separate files or modules but align with existing project structure",
                        "- Use descriptive names for LLM tool discoverability (Grep, Glob)",
                    ]),
                },
            }

            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Log error but don't block execution
        print(
            json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": f"LOC threshold check error: {e}",
                }
            }),
            file=sys.stderr,
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
