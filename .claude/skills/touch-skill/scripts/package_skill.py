#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable zip file of a skill folder

Usage:
    python package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python package_skill.py .claude/skills/my-skill
    python package_skill.py .claude/skills/my-skill ./dist
"""

import sys
import zipfile
from pathlib import Path
from quick_validate import validate_skill


def package_skill(skill_path, output_dir=None):
    """Package a skill folder into a zip file."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"Error: Path is not a directory: {skill_path}")
        return None

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation
    print("Validating skill...")
    valid, errors, warnings = validate_skill(skill_path)

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if not valid:
        print("\nValidation failed:")
        for e in errors:
            print(f"  - {e}")
        print("\nFix errors before packaging.")
        return None

    print("Validation passed!\n")

    # Determine output location
    skill_name = skill_path.name
    output_path = Path(output_dir).resolve() if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)
    zip_filename = output_path / f"{skill_name}.zip"

    # Create zip
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

        print(f"\nPackaged to: {zip_filename}")
        return zip_filename

    except Exception as e:
        print(f"Error creating zip: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <path/to/skill-folder> [output-directory]")
        print("\nExample:")
        print("  python package_skill.py .claude/skills/my-skill")
        print("  python package_skill.py .claude/skills/my-skill ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Packaging skill: {skill_path}")
    if output_dir:
        print(f"Output: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
