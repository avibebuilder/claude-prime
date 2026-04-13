# Full Project Setup Workflow

## Prerequisites

- claude-prime boilerplate copied to project
- Project has existing codebase to analyze

## Step 1: Analyze Codebase

Explore the project and summarize what you find (stack, patterns, conventions). Use [analysis-checklist.md](../references/analysis-checklist.md) for non-obvious things to look for.

## Step 2: Skill Coverage Check

Skills are the foundation — everything else (rules, CLAUDE.md) depends on having the right domain knowledge in place first. Check skill coverage before creating any other config.

Check `.claude/starter-skills/` for starters that match the detected stack. For each match:

1. **Copy** the starter folder to `.claude/skills/`
2. **Prune** files/folders for technologies not in the project (e.g., remove `nextjs/` if no Next.js, remove `trpc-tanstack.md` if no tRPC, remove `axios.md` if no Axios, remove `biome.md` if no Biome)
3. **Adapt** generic parts that don't match the project's specific tool choices (e.g., starter has Biome patterns but project uses ESLint → replace Biome references with ESLint generic knowledge)
4. **Update references** — remove pruned files from overview files and SKILL.md reference tables

If no starter matches the detected stack, flag it for Step 3.

## Step 3: Create Skills (for stacks without starters)

For stacks with **no matching starter**, use `/skill-creator` to autonomously create skills:

```
/skill-creator <stack-name>
```

Provide `/skill-creator` with the stack name and any project-specific context discovered in Step 1. Ask it to do creation and optimization autonomously.

**Gate: All general frameworks must have skill coverage before proceeding.**

## Step 4: Identify Path-Scoped Rules (if any)

Rules are optional — zero rules is a valid outcome. Only create rules for project-specific constraints where code would be wrong even with the right skill loaded.

Apply the **rule test**: "With the relevant skill activated, will an agent still produce incorrect code without knowing this?"
- **Yes** → rule (e.g., "Must use `cn()` not `clsx()` in tsx" — project-specific utility choice)
- **No** → already covered by skills or CLAUDE.md

**Red flags** that something is NOT a rule — it probably belongs in a skill instead:
- Applies to all files (`**/*.swift`, `**/*.ts`) → general knowledge
- A skill already teaches it → redundant auto-attach bloating context
- It's a language/framework feature, not a project decision

Don't modify `_apply-all.md` — it's a boilerplate default, not project-specific.

**Gate: If rules are proposed, review with user before creating.**

## Step 5: Generate CLAUDE.md

Let Claude generate CLAUDE.md naturally — it already does a good job with project overview, commands, tech stack, architecture, and conventions. Only guide what Claude doesn't do by default:

- **Do NOT reference rules** — they're auto-attached, mentioning them in CLAUDE.md wastes tokens
- **Add on-demand reference pointers** — if the project has `docs/`, READMEs, or other reference files, add pointers so agents know where to look
- **Keep it under ~200 lines** — if larger, move detailed content out and reference it
- **Optional: `.claude/project/`** — if the project's existing docs are too verbose for agent consumption, suggest creating `.claude/project/` with dense, scannable agent-optimized references. Not a default step.

## Step 6: Offer CLAUDE.local.md Setup

Ask the user if they want to set up personal preferences (gitignored, not shared):
- Their role and context
- Sandbox/staging URLs
- Preferred test data
- Workflow quirks

If yes, create `CLAUDE.local.md` with their preferences. Ensure `.gitignore` includes `CLAUDE.local.md`.

## Step 7: Create Domain Documentation

If project has business logic worth documenting, use:
```
/create-doc
```

`./docs/` is for **WHAT the code does** (domain knowledge):
- Business rules and algorithms (scoring, ranking, pricing)
- Domain concepts and workflows (campaign lifecycle, user journey)
- Feature specifications
- State machines and business logic

**This is distinct from CLAUDE.md (always-on context) and `.claude/rules/` (guardrails). CLAUDE.md can reference `docs/` files for on-demand loading.**

## Step 8: Clean Up

1. Delete `.claude/starter-skills/` — starters have been processed in Step 3
2. Remove any skills from `.claude/skills/` that don't match the project stack (e.g., `frontend-design` in a backend-only project, `agent-browser` if not needed)

### Protected skills (never delete)

- **Workflow:** `cook`, `fix`, `test`, `review-code`, `research`, `ask`, `discuss`, `give-plan`, `create-doc`, `diagnose`
- **Meta/tooling:** `optimus-prime`, `prime-sync`, `skill-creator`, `self-evolve`
- **Utilities:** `docs-seeker`, `media-processor`

**Gate: List skills to remove and confirm with user before deleting.**

## Step 9: Verify Setup

Verify the setup is correct. Focus on things that are easy to get wrong:

- **Broken references** — check that all file paths in CLAUDE.md and skill reference tables actually exist
- **Starter cleanup** — `.claude/starter-skills/` should be deleted
- **Accuracy spot-check** — verify stated tech stack matches actual dependencies, and "All X lives in Y" claims are accurate (grep to confirm)
- **CLAUDE.md size** — flag if over 200 lines

For deeper ongoing config analysis, run `/self-evolve` after priming.

## Output Summary

```
./CLAUDE.md                       # Always-on project context (~200 lines)
./CLAUDE.local.md                 # Personal preferences (gitignored, optional)
./docs/                           # Domain knowledge (optional)
.claude/
├── rules/
│   └── <name>.md                 # Path-scoped guardrails (optional)
└── skills/
    └── <new-stack>/              # Generated skills (if any)
```
