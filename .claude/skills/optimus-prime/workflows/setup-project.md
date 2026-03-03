# Full Project Setup Workflow

## Prerequisites

- claude-prime boilerplate copied to project
- Project has existing codebase to analyze

## Step 1: Analyze Codebase

Explore project structure:
```
- Check package.json / requirements.txt / go.mod
- Scan folder structure
- Read existing config files (eslint, tsconfig, etc.)
- Sample key files for patterns
```

Use [analysis-checklist.md](../references/analysis-checklist.md) as guide.

## Step 2: Document Findings

Create analysis summary:
- Detected stack (frontend, backend, database)
- Detected patterns (architecture, naming, etc.)
- Project-specific conventions

## Step 3: Skill Coverage Check (REQUIRED)

**STOP. Before creating any project context, check skill coverage.**

Check `.claude/starter-skills/` for starters that match the detected stack. For each match:

1. **Copy** the starter folder to `.claude/skills/`
2. **Prune** files/folders for technologies not in the project (e.g., remove `nextjs/` if no Next.js, remove `trpc-tanstack.md` if no tRPC, remove `axios.md` if no Axios, remove `biome.md` if no Biome)
3. **Adapt** generic parts that don't match the project's specific tool choices (e.g., starter has Biome patterns but project uses ESLint → replace Biome references with ESLint generic knowledge)
4. **Update references** — remove pruned files from overview files and SKILL.md reference tables

If no starter matches the detected stack, flag it for Step 4 (create via `/touch-skill`).

**DO NOT skip this step. DO NOT use project rules as substitute for missing skills.**

## Step 4: Create/Extend Skills (for stacks without starters)

For stacks flagged in Step 3 that had **no matching starter**, create skills from scratch:

```
/touch-skill <stack-name>
```

**Gate: All general frameworks must have skill coverage before proceeding.**

## Step 5: Create Project References

```bash
mkdir -p .claude/project
```

**On-demand references** — loaded when agents need context, not auto-attached:
- Architecture decisions and folder structure
- Project overview and domain context
- Deviations from skill defaults (overrides)

**DO NOT put here:**
- Hard constraints that cause wrong code if missed (belongs in `.claude/rules/`)
- General framework knowledge (belongs in skills)
- Business logic / domain rules (belongs in `./docs/`)

## Step 6: Identify Path-Scoped Rules (if any)

**Rules are optional.** Not every project needs them. Only create rules for project-specific constraints that skills can't cover.

For each detected convention, apply the **rule test**:

> "With the relevant skill activated, will an agent still produce incorrect code without knowing this?"

| Answer | Where | Example |
|--------|-------|---------|
| **Yes** | `.claude/rules/<name>.md` with `paths:` | "Must use `cn()` not `clsx()` in tsx" (project-specific utility choice) |
| **No** | Already covered by skills or `.claude/project/` | "Use @MainActor for UI code" (any Swift skill teaches this) |

### Red flags — NOT a rule

- **Applies to all files** (`**/*.swift`, `**/*.ts`) → probably general knowledge, belongs in skill
- **Skill already teaches this** → redundant auto-attach that bloats context
- **Language/framework feature, not a project decision** → skill
- **"Important" ≠ "must auto-attach"** → importance doesn't justify duplication

**If nothing passes the rule test, skip this step entirely. Zero rules is a valid outcome.**

### Rule file format

```markdown
---
description: Brief description of what these rules enforce
paths:
  - "src/**/*.tsx"
  - "src/**/*.ts"
---

- Concise guardrail bullet points only
- Each rule: wrong code if missed
```

### Best Practices

- **Keep rule files short** — guardrails, not documentation. Long files bloat auto-attached context.
- **One topic per file** — e.g., `frontend.md`, `api.md`, not `everything.md`
- **Descriptive filenames** — filename should indicate what rules cover
- **Organize with subdirectories** — group related rules (e.g., `rules/frontend/`, `rules/backend/`)
- **Be specific** — "Use 2-space indentation" not "Format code properly"
- **Use structure** — bullet points grouped under descriptive markdown headings
- **Scope paths precisely** — broad paths (`**/*.ts`) attach to more files. Use narrow paths when possible.

**DO NOT put here:**
- General framework knowledge (belongs in skills)
- Architecture/structure context (belongs in `.claude/project/`)

**Should not modify `_apply-all.md`** — it's a boilerplate default for agent behavior, not a project-specific rule.

**Gate: If rules are proposed, review with user before creating.**

## Step 7: Create CLAUDE.md

Copy `templates/CLAUDE.template.md` to `./CLAUDE.md`

### Content Boundary Rules

**CLAUDE.md is entry point only. Soft limit: ~100 lines.**

| ✓ Include | ✗ Do NOT Include |
|-----------|------------------|
| Project overview (1-2 sentences) | CLI commands with explanations |
| Project references table (`.claude/project/`) | Code examples/patterns |
| Repository structure (basic tree) | Tech stack details |
| Quick reference links | Environment variables |
| | Rules (auto-attached, don't mention) |

### Customize

1. Add project overview (1-2 sentences)
2. Update project references table to reference actual `.claude/project/` files
3. Update repository structure tree (max 15 lines)
4. Add quick reference links (URLs only, no explanations)

**Rules are auto-attached — do NOT reference them in CLAUDE.md.**

**If CLAUDE.md exceeds 100 lines, move content to `.claude/project/` files.**

## Step 8: Create Domain Documentation

If project has business logic worth documenting, use:
```
/create-doc
```

`./docs/` is for **WHAT the code does** (domain knowledge):
- Business rules and algorithms (scoring, ranking, pricing)
- Domain concepts and workflows (campaign lifecycle, user journey)
- Feature specifications
- State machines and business logic

**This is distinct from `.claude/project/` (HOW context) and `.claude/rules/` (guardrails).**

## Step 9: Clean Up

1. Delete `.claude/starter-skills/` — starters have been processed in Step 3
2. Remove any skills from `.claude/skills/` that don't match the project stack (e.g., `frontend-design` in a backend-only project, `agent-browser` if not needed)

### Protected skills (never delete)

- **Workflow:** `cook`, `fix`, `test`, `review-code`, `research`, `ask`, `discuss`, `give-plan`, `create-doc`
- **Meta/tooling:** `optimus-prime`, `prime-sync`, `touch-skill`, `convo-analysis`
- **Utilities:** `docs-seeker`, `repomix`, `media-processor`

**Gate: List skills to remove and confirm with user before deleting.**

## Step 10: Verify Setup

Checklist:
- [ ] Skill coverage complete (starters + `/touch-skill`)
- [ ] Unrelated skills removed, `.claude/starter-skills/` deleted
- [ ] `.claude/rules/` contains ONLY short guardrail files, if any (wrong code if missed)
- [ ] `.claude/project/` contains ONLY on-demand references (architecture, structure)
- [ ] `./CLAUDE.md` is under 100 lines
- [ ] `./CLAUDE.md` references project folder and docs
- [ ] Domain docs created (optional)

## Output Summary

```
./CLAUDE.md                       # Entry point (~100 lines)
./docs/                           # Domain knowledge (optional)
.claude/
├── rules/
│   └── <name>.md                 # Path-scoped guardrails (optional)
├── project/
│   └── *.md                      # On-demand references
└── skills/
    └── <new-stack>/              # Generated skills (if any)
```
