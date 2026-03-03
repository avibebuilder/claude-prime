# Creating a New Skill

## Prerequisites

- Clear understanding of skill purpose
- Concrete usage examples from user

## Step 1: Gather Requirements

**Questions:** "What functionality?", "Example scenarios?", "What triggers this skill?"

**Conclude when:** Clear sense of functionality the skill should support.

## Step 2: Plan Reusable Contents

For each usage example, analyze what resources help when executing repeatedly:

| Pattern | Resource Type | Example |
|---------|--------------|---------|
| Same code rewritten | scripts/ | `rotate_pdf.py` |
| Same boilerplate needed | assets/ | `starter-template/` |
| Same info re-discovered | references/ | `schema.md` |
| Multi-step procedure | workflows/ | `deployment.md` |

## Step 3: Initialize

```bash
scripts/init_skill.py <skill-name> --path <output-dir>
```

Creates: SKILL.md template, scripts/, references/, assets/ example files.

## Step 4: Implement Resources

1. Create scripts/ (if needed)—write tests first
2. Create references/ (if needed)—<500 lines each
3. Create assets/ (if needed)
4. Delete unneeded example files

## Step 5: Complete SKILL.md

**Answer:** Purpose (1-2 sentences), when to use (triggers), how to use (reference resources).

**Writing style:** Imperative form ("Execute...", "Run...")

**Structure:** Overview → Quick Start → Resources links

## Step 6: Validate

```bash
scripts/validate_skill.py <path/to/skill>
```

Checks: YAML frontmatter, naming, line counts (soft limits), description quality.

## Step 7: Package (Optional)

```bash
scripts/package_skill.py <path/to/skill>
```

## Common Mistakes

- Putting everything in SKILL.md (split into references)
- Skipping tests for scripts
- Vague descriptions ("A skill for X")
- Not testing cold start activation
