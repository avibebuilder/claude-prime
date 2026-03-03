#!/usr/bin/env python3
"""
Workflow Skill Initializer - Creates a new workflow-type skill from template

Usage:
    init_workflow_skill.py <skill-name> --path <path> [--type <none|analysis|execution>]

Examples:
    init_workflow_skill.py my-skill --path .claude/skills
    init_workflow_skill.py debug-helper --path .claude/skills --type execution
"""

import sys
from pathlib import Path

TEMPLATE = '''---
name: {skill_name}
description: "{description_placeholder}"
---

{thinking_directive}

## Context Assessment
Before starting, analyze conversation history:
- **[TODO: Condition 1]?** -> Skip [Phase X]
- **[TODO: Condition 2]?** -> Skip [Phase Y]
- Start from earliest incomplete phase

## Role

You are a [TODO: role]. Your job is to [TODO: PRIMARY ACTION] - not to [TODO: boundary].

## Process

### 1. [TODO: First step]
- [Details]

### 2. [TODO: Second step]
- [Details]
- Delegate to `/test`, `/review-code`, `/fix`, or `/give-plan` if applicable

**GATE**: [If user approval needed]

### 3. [TODO: Final step]
- [Details]

## Guardrails

**Holy Trinity:**
- **YAGNI**: [TODO: context-specific application]
- **KISS**: [TODO: context-specific application]
- **DRY**: [TODO: context-specific application]

**Communication:**
- Be brutally honest, not sycophantic
- [TODO: Additional rules]

**Constraints:**
- [TODO: What this skill will NOT do]
- [TODO: Explicit boundaries]

## {input_section}

<{tag_name}>$ARGUMENTS</{tag_name}>
'''

THINKING_DIRECTIVES = {
    'none': '',  # Default - no directive
    'analysis': 'Ultrathink.',
    'execution': 'Think harder.'
}


def title_case_name(name):
    """Convert hyphenated name to Title Case."""
    return ' '.join(word.capitalize() for word in name.split('-'))


def create_workflow_skill(skill_name, path, skill_type='none'):
    """Create a new workflow skill directory and SKILL.md from template."""
    output_path = Path(path).resolve()

    if not output_path.exists():
        print(f"Error: Path does not exist: {output_path}")
        return None

    # Create skill directory
    skill_dir = output_path / skill_name
    if skill_dir.exists():
        print(f"Error: Skill directory already exists: {skill_dir}")
        return None

    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"

    # Generate content
    title = title_case_name(skill_name)
    thinking = THINKING_DIRECTIVES.get(skill_type, THINKING_DIRECTIVES['analysis'])

    content = TEMPLATE.format(
        skill_name=skill_name,
        description_placeholder=f"[TODO: What /{skill_name} does]",
        thinking_directive=thinking,
        input_section=title,
        tag_name=skill_name.replace('-', '_')
    )

    try:
        skill_file.write_text(content)
        print(f"Created: {skill_file}")
        if thinking:
            print(f"\nThinking directive: {thinking}")
        else:
            print("\nThinking directive: none (default)")
        print("\nNext steps:")
        print("1. Edit SKILL.md - complete all TODOs")
        print("2. Update frontmatter name and description")
        print("3. Define role boundaries")
        print("4. Add process steps with gates")
        print(f"5. Validate: python validate_workflow_skill.py {skill_dir}")
        return skill_file
    except Exception as e:
        print(f"Error creating skill: {e}")
        # Clean up on failure
        if skill_file.exists():
            skill_file.unlink()
        if skill_dir.exists():
            skill_dir.rmdir()
        return None


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: init_workflow_skill.py <skill-name> --path <path> [--type <none|analysis|execution>]")
        print("\nThinking types (optional):")
        print("  none      - No directive (default) - standard reasoning")
        print("  analysis  - Ultrathink. - complex planning/strategy")
        print("  execution - Think harder. - focused debugging/review")
        print("\nExamples:")
        print("  init_workflow_skill.py my-skill --path .claude/skills")
        print("  init_workflow_skill.py planner --path .claude/skills --type analysis")
        print("  init_workflow_skill.py debugger --path .claude/skills --type execution")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    # Parse optional --type
    skill_type = 'none'
    if len(sys.argv) >= 6 and sys.argv[4] == '--type':
        skill_type = sys.argv[5]
        if skill_type not in THINKING_DIRECTIVES:
            print(f"Error: Invalid type '{skill_type}'. Use 'none', 'analysis', or 'execution'")
            sys.exit(1)

    result = create_workflow_skill(skill_name, path, skill_type)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
