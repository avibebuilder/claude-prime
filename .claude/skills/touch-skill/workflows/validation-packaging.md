# Validation & Packaging

## Validation

### Quick Validate

```bash
scripts/validate_skill.py <path/to/skill>
```

**Checks performed:**
- SKILL.md exists
- Valid YAML frontmatter
- Required fields: `name`, `description`
- Name is hyphen-case
- Description quality
- Line counts (soft limits: SKILL.md <150, references <500, workflows <200)

### Validation Rules

| Rule | Requirement |
|------|-------------|
| SKILL.md | Must exist |
| Frontmatter | Must start with `---` |
| name | Required, hyphen-case, matches directory |
| description | Required, no angle brackets |
| SKILL.md lines | <150 (soft) |
| Reference file lines | <500 each (soft) |
| Workflow file lines | <200 each (soft) |

### Fixing Validation Errors

**"SKILL.md not found"**
- Ensure file is named exactly `SKILL.md` (uppercase)

**"No YAML frontmatter found"**
- File must start with `---` on first line

**"Name should be hyphen-case"**
- Use lowercase letters, digits, hyphens only
- No consecutive hyphens, no leading/trailing hyphens

**"SKILL.md has X lines (guideline: <150)"**
- Consider splitting content into references/ or workflows/
- See [refactor-skill.md](./refactor-skill.md)

## Packaging

### Create Package

```bash
scripts/package_skill.py <path/to/skill>
```

**Optional output directory:**
```bash
scripts/package_skill.py <path/to/skill> ./dist
```

### What Packaging Does

1. **Validates** skill automatically (runs validate_skill)
2. **Creates** zip file if validation passes
3. **Maintains** directory structure in zip

### Package Contents

```
my-skill.zip
└── my-skill/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── (other resources)
```

### Distribution

Share the zip file. Recipients can:
1. Unzip to `.claude/skills/`
2. Skill activates automatically based on description

## Pre-Packaging Checklist

- [ ] `scripts/validate_skill.py` passes
- [ ] Line counts within soft guidelines (SKILL.md <150, refs <500, workflows <200)
- [ ] Scripts have tests that pass
- [ ] No TODO placeholders remaining
- [ ] Description lists trigger scenarios
- [ ] Cold start loads <500 lines
