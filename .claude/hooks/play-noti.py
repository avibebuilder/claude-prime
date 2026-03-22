#!/usr/bin/env python3
"""Cross-platform notification sound player for Stop hook."""

import os
import platform
import subprocess
import sys


def main():
    if os.environ.get("CLAUDE_SILENT"):
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sound_file = os.path.join(project_dir, ".claude", "noti.mp3")

    if not os.path.isfile(sound_file):
        sys.exit(0)

    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["afplay", sound_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            for player in ["paplay", "aplay", "ffplay"]:
                if _command_exists(player):
                    args = [player, "-nodisp", "-autoexit", sound_file] if player == "ffplay" else [player, sound_file]
                    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break
        elif system == "Windows":
            subprocess.Popen(
                ["powershell", "-c", f'(New-Object Media.SoundPlayer "{sound_file}").PlaySync()'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except FileNotFoundError:
        pass


def _command_exists(cmd: str) -> bool:
    try:
        subprocess.run(["which", cmd], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


if __name__ == "__main__":
    main()
