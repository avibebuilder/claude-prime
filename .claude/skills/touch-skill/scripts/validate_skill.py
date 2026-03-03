#!/usr/bin/env python3
"""
Skill validator - validates structure, naming, line counts, and workflow conventions.

Usage:
    python validate_skill.py <skill-directory>
    python validate_skill.py <skill-directory> --type=workflow

Examples:
    python validate_skill.py .claude/skills/frontend-development
    python validate_skill.py .claude/skills/cook --type=workflow
"""

import sys
import re
from pathlib import Path

MAX_LINES_FOR_SKILLS = 150
MAX_LINES_FOR_REFERENCES = 500
MAX_LINES_FOR_WORKFLOWS = 200
MAX_DESCRIPTION_CHARS = 600
AGGREGATE_DESCRIPTION_BUDGET = 16_000
AGGREGATE_SKILL_THRESHOLD = 15

WORKFLOW_REQUIRED_SECTIONS = ["role", "constraints"]


def count_lines(file_path):
    return len(file_path.read_text().splitlines())


def extract_frontmatter(content):
    """Extract and validate YAML frontmatter. Returns (frontmatter_str, errors, warnings)."""
    errors = []
    warnings = []

    if not content.startswith("---"):
        return None, ["No YAML frontmatter found (must start with ---)"], []

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, ["Invalid frontmatter format (missing closing ---)"], []

    frontmatter = match.group(1)

    if "name:" not in frontmatter:
        errors.append("Missing 'name' in frontmatter")
    if "description:" not in frontmatter:
        errors.append("Missing 'description' in frontmatter")
    elif "[TODO" in frontmatter:
        warnings.append("Frontmatter contains TODO placeholders")

    return frontmatter, errors, warnings


def validate_name(frontmatter):
    """Validate skill name format."""
    errors = []
    name_match = re.search(r"name:\s*(.+)", frontmatter)
    if not name_match:
        return errors

    name = name_match.group(1).strip().strip("\"'")
    if not re.match(r"^[a-z0-9-]+$", name):
        errors.append(f"Name '{name}' should be hyphen-case (lowercase, digits, hyphens)")
    if name.startswith("-") or name.endswith("-") or "--" in name:
        errors.append(f"Name '{name}' cannot start/end with hyphen or have consecutive hyphens")

    return errors


def extract_description(skill_md_path):
    """Extract description field from a SKILL.md frontmatter."""
    try:
        content = skill_md_path.read_text()
    except (OSError, UnicodeDecodeError):
        return None
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    desc_match = re.search(r'description:\s*["\']?(.+?)["\']?\s*$', match.group(1), re.MULTILINE)
    return desc_match.group(1).strip() if desc_match else None


def validate_description(frontmatter):
    """Validate description quality."""
    errors = []
    warnings = []

    desc_match = re.search(r'description:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
    if not desc_match:
        return errors, warnings

    description = desc_match.group(1).strip()

    if "<" in description or ">" in description:
        errors.append("Description cannot contain angle brackets (< or >)")

    if len(description) < 50:
        warnings.append("Description is short (aim for 50+ chars with action triggers)")

    if len(description) > MAX_DESCRIPTION_CHARS:
        warnings.append(
            f"Description is {len(description)} chars (max: {MAX_DESCRIPTION_CHARS}). "
            f"Shorten to stay within per-skill budget."
        )

    trigger_phrases = ["use this skill when", "use this skill", "use when", "use this"]
    if not any(phrase in description.lower() for phrase in trigger_phrases):
        warnings.append(
            "Description should include trigger phrase "
            "(e.g., 'Use this skill when creating..., building..., implementing...')"
        )

    return errors, warnings


def validate_line_counts(skill_path):
    """Validate line counts for SKILL.md and reference files."""
    warnings = []

    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        lines = count_lines(skill_md)
        if lines > MAX_LINES_FOR_SKILLS:
            warnings.append(
                f"SKILL.md has {lines} lines (guideline: <{MAX_LINES_FOR_SKILLS}). "
                f"Consider splitting if covering multiple concepts."
            )

    for subdir, limit, label in [
        ("references", MAX_LINES_FOR_REFERENCES, "references"),
        ("workflows", MAX_LINES_FOR_WORKFLOWS, "workflows"),
    ]:
        sub_path = skill_path / subdir
        if sub_path.exists():
            for md_file in sub_path.glob("*.md"):
                lines = count_lines(md_file)
                if lines > limit:
                    warnings.append(f"{label}/{md_file.name} has {lines} lines (guideline: <{limit}).")

    return warnings


def validate_aggregate_budget(skill_path):
    """Check total description budget across all sibling skills."""
    warnings = []
    skills_dir = skill_path.parent
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

    if len(skill_dirs) <= AGGREGATE_SKILL_THRESHOLD:
        return warnings

    total = sum(len(desc) for d in skill_dirs if (desc := extract_description(d / "SKILL.md")))

    if total > AGGREGATE_DESCRIPTION_BUDGET:
        pct = round(total / AGGREGATE_DESCRIPTION_BUDGET * 100, 1)
        warnings.append(
            f"Aggregate description budget exceeded: {total}/{AGGREGATE_DESCRIPTION_BUDGET} chars ({pct}%)."
        )

    return warnings


# --- Workflow-specific checks ---


def validate_thinking_directive(content):
    """Check for thinking directive format if present."""
    warnings = []
    match = re.search(r"^---\n.*?\n---\n+(.+?)(?:\n|$)", content, re.DOTALL)
    if match:
        first_line = match.group(1).strip()
        if "ultrathink" in first_line.lower() and first_line != "Ultrathink.":
            warnings.append(f"Thinking directive format: '{first_line}' (use exact: 'Ultrathink.')")
        elif "think harder" in first_line.lower() and first_line != "Think harder.":
            warnings.append(f"Thinking directive format: '{first_line}' (use exact: 'Think harder.')")
    return warnings


def validate_workflow_sections(content):
    """Validate workflow-specific required sections."""
    errors = []
    warnings = []
    content_lower = content.lower()

    for section in WORKFLOW_REQUIRED_SECTIONS:
        if f"## {section}" not in content_lower:
            errors.append(f"Missing required section: ## {section.title()}")

    has_process = any(f"## {s}" in content_lower for s in ["process", "phases", "lifecycle"])
    if not has_process and not re.search(r"^\d+\.", content, re.MULTILINE):
        warnings.append("No '## Process' section or numbered steps found")

    if "$ARGUMENTS" not in content:
        errors.append("Missing $ARGUMENTS placeholder")

    return errors, warnings


def validate_constraints_quality(content):
    """Check constraints section has explicit boundaries."""
    warnings = []
    content_lower = content.lower()
    boundary_indicators = ["constraint", "will not", "won't", "- no ", "- do not", "- don't"]
    if not any(indicator in content_lower for indicator in boundary_indicators):
        warnings.append("No explicit constraints or boundaries found in Constraints section")
    return warnings


# --- Main validation ---


def validate_skill(skill_path, skill_type=None):
    """Validate a skill directory."""
    path = Path(skill_path)

    if path.is_dir():
        skill_file = path / "SKILL.md"
    elif path.name == "SKILL.md":
        skill_file = path
        path = path.parent
    else:
        return False, [f"Expected a skill directory or SKILL.md file: {path}"], []

    if not skill_file.exists():
        return False, ["SKILL.md not found"], []

    content = skill_file.read_text(encoding="utf-8", errors="replace")
    all_errors = []
    all_warnings = []

    # Frontmatter
    frontmatter, errors, warnings = extract_frontmatter(content)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    if not frontmatter:
        return False, all_errors, all_warnings

    # Name and description
    all_errors.extend(validate_name(frontmatter))
    desc_errors, desc_warnings = validate_description(frontmatter)
    all_errors.extend(desc_errors)
    all_warnings.extend(desc_warnings)

    # Line counts
    all_warnings.extend(validate_line_counts(path))

    # Aggregate budget
    all_warnings.extend(validate_aggregate_budget(path))

    # Workflow-specific checks
    if skill_type == "workflow":
        all_warnings.extend(validate_thinking_directive(content))

        errors, warnings = validate_workflow_sections(content)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

        all_warnings.extend(validate_constraints_quality(content))

    # TODOs
    todo_count = content.count("[TODO")
    if todo_count > 0:
        all_warnings.append(f"Found {todo_count} TODO placeholder(s) - complete before use")

    return len(all_errors) == 0, all_errors, all_warnings


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    if not args:
        print("Usage: python validate_skill.py <skill-directory> [--type=workflow]")
        print("\nExamples:")
        print("  python validate_skill.py .claude/starter-skills/frontend-development")
        print("  python validate_skill.py .claude/skills/cook --type=workflow")
        sys.exit(1)

    skill_path = args[0]
    skill_type = None
    for flag in flags:
        if flag.startswith("--type="):
            skill_type = flag.split("=", 1)[1]

    valid, errors, warnings = validate_skill(skill_path, skill_type)

    print(f"Validating: {skill_path}")
    if skill_type:
        print(f"Type: {skill_type}")
    print()

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if valid:
        print("Skill is valid!")
        sys.exit(0)
    else:
        print("Errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
