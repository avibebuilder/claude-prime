# Skill Requirements (Non-Negotiable)

## Line Limits (Soft, accept exceptions)

| File Type | Guideline | Rationale |
|-----------|-----------|-----------|
| SKILL.md | ~150 lines | Entry point should be scannable |
| Reference files | ~500 lines each | Detailed technical content allowed |
| Workflow files | ~200 lines each | Step-by-step procedures |
| Scripts | No limit | Must work, have tests |

These are **soft limits** (warnings, not errors). Complex skills like `agent-browser` or `media-processor` may exceed when justified.

**When to split:** File covers multiple distinct topics or concepts.

## Description Character Budgets

Skill descriptions (the `description` field in YAML frontmatter) are loaded into Claude Code's context window. Budget constraints prevent context bloat.

| Constraint | Limit | Scope |
|------------|-------|-------|
| Per-skill max | 600 chars | Each individual `description` field |
| Aggregate budget | 16,000 chars | Sum of all skill descriptions combined |

**Per-skill (always checked):** Descriptions exceeding 600 characters produce a warning. Keep descriptions concise -- front-load trigger phrases and key capabilities.

**Aggregate (checked when >15 skills exist):** When the skills directory contains more than 15 skills, the validator sums all description lengths and warns if the total exceeds 16,000 characters. The warning reports current total, budget, and percentage used.

## Naming Conventions

**Skill name:**
- Hyphen-case: `my-skill-name`
- Lowercase letters, digits, hyphens only
- Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`
- Max 40 characters
- Must match directory name exactly

**Invalid names:**
- `-skill` (starts with hyphen)
- `skill-` (ends with hyphen)
- `my--skill` (consecutive hyphens)
- `MySkill` (uppercase)

## Skill Organization

Combine related tools into capability-focused skills:

**Bad:** Individual tool skills
- `cloudflare`, `docker`, `gcloud`, `vercel`

**Good:** Workflow-capability groups
- `devops` (handles all deployment tools)

## Script Requirements

1. **Platform:** Prefer Node.js or Python (not Bash—Windows compatibility)
2. **Dependencies:** Include `requirements.txt` (Python) or `package.json` (Node)
3. **Tests:** Always write tests, run until passing
4. **Manual verification:** Run scripts with real use cases

## .env Hierarchy

Scripts must respect this order:
```
process.env (highest priority)
  ↓
.claude/skills/{skill}/.env
  ↓
.claude/skills/.env
  ↓
.claude/.env (lowest priority)
```

Create `.env.example` showing required variables.

## Writing Style

**Use:** Imperative/infinitive form (verb-first)
- "To create a skill, run..."
- "Execute scripts in order"

**Avoid:** Second person
- "You should create..."
- "If you need to..."
