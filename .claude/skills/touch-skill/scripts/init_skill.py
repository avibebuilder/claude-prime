#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path>

Examples:
    init_skill.py my-new-skill --path .claude/skills
    init_skill.py api-helper --path skills/private
"""

import sys
from pathlib import Path

# Template directory relative to this script
TEMPLATES_DIR = Path(__file__).parent.parent / 'templates'

# Fallback templates if external files not found
DEFAULT_SKILL_TEMPLATE = """---
name: {skill_name}
description: "[TODO: What this skill does and when to use it. Include trigger scenarios.]"
---

# {skill_title}

[TODO: 1-2 sentences explaining what this skill enables]

## Quick Start

[TODO: Essential commands or first steps]

## References

[TODO: Link to reference files if needed]

---

**Keep under 150 lines.**
"""

DEFAULT_SCRIPT_TEMPLATE = '''#!/usr/bin/env python3
"""
{skill_name} - [TODO: Brief description]
"""

import sys


def main():
    """Main entry point."""
    print("Script executed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

DEFAULT_REFERENCE_TEMPLATE = """# [TODO: Reference Title]

## Overview

[TODO: Brief description]

---

**Keep under 500 lines.**
"""


def load_template(template_name, fallback):
    """Load template from file or use fallback."""
    template_path = TEMPLATES_DIR / template_name
    if template_path.exists():
        return template_path.read_text()
    return fallback


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def init_skill(skill_name, path):
    """Initialize a new skill directory with templates."""
    skill_dir = Path(path).resolve() / skill_name

    if skill_dir.exists():
        print(f"Error: Skill directory already exists: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"Error creating directory: {e}")
        return None

    skill_title = title_case_skill_name(skill_name)

    # Create SKILL.md
    skill_template = load_template('skill-template.md', DEFAULT_SKILL_TEMPLATE)
    skill_content = skill_template.format(skill_name=skill_name, skill_title=skill_title)
    (skill_dir / 'SKILL.md').write_text(skill_content)
    print("Created SKILL.md")

    # Create scripts/ with example
    scripts_dir = skill_dir / 'scripts'
    scripts_dir.mkdir(exist_ok=True)
    script_template = load_template('script-template.py', DEFAULT_SCRIPT_TEMPLATE)
    script_content = script_template.format(skill_name=skill_name, filename='example.py')
    example_script = scripts_dir / 'example.py'
    example_script.write_text(script_content)
    example_script.chmod(0o755)
    print("Created scripts/example.py")

    # Create references/ with example
    refs_dir = skill_dir / 'references'
    refs_dir.mkdir(exist_ok=True)
    ref_template = load_template('reference-template.md', DEFAULT_REFERENCE_TEMPLATE)
    (refs_dir / 'example.md').write_text(ref_template)
    print("Created references/example.md")

    print(f"\nSkill '{skill_name}' initialized at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md - complete TODOs, update description")
    print("2. Customize or delete example files")
    print("3. Run: scripts/quick_validate.py <skill-path>")

    return skill_dir


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: init_skill.py <skill-name> --path <path>")
        print("\nSkill name requirements:")
        print("  - Hyphen-case (e.g., 'my-skill')")
        print("  - Lowercase letters, digits, hyphens only")
        print("  - Max 40 characters")
        print("\nExamples:")
        print("  init_skill.py my-skill --path .claude/skills")
        print("  init_skill.py api-helper --path skills/private")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    print(f"Initializing skill: {skill_name}")
    print(f"Location: {path}\n")

    result = init_skill(skill_name, path)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
