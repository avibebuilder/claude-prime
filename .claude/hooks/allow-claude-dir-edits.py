#!/usr/bin/env python3
"""
Auto-approve permission requests for .claude/ directory edits,
but ONLY when running with --dangerously-skip-permissions (bypassPermissions mode).

Workaround for https://github.com/anthropics/claude-code/issues/36168
In bypass mode Claude should never prompt, but may be restricted to ask for .claude/ files.
Remove this hook if you consider it a security risk.
"""
import json
import sys

payload = json.load(sys.stdin)

if payload.get("permission_mode") != "bypassPermissions":
    sys.exit(0)

tool_name = payload.get("tool_name", "")
tool_input = payload.get("tool_input", {})

allow = False

if tool_name in ("Write", "Edit"):
    file_path = tool_input.get("file_path", "")
    if "/.claude/" in file_path or file_path.endswith("/.claude"):
        allow = True

elif tool_name == "Bash":
    command = tool_input.get("command", "")
    # Check if the bash command targets a .claude/ path
    if "/.claude/" in command or command.endswith("/.claude"):
        allow = True

if allow:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {"behavior": "allow"},
        }
    }))

sys.exit(0)
