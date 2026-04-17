# Project Analysis Checklist

What to inspect before proposing changes. The goal is to understand what makes this project unique — what conventions, patterns, and constraints Claude needs to know to work well here.

## 1. Existing Claude Config

Check what is already present and whether it looks intentional:
- `CLAUDE.md`, `CLAUDE.local.md`
- `.claude/skills/` — existing project skills
- `.claude/rules/` — path-scoped files besides `_apply-all.md`
- `.claude/project/` — agent-oriented references
- `.claude/starter-skills/` — unprocessed reference material

Answer:
- What should be preserved as intentional project knowledge?
- What is generic, stale, duplicated, or unfinished?
- Which files are personal vs team-shared?

## 2. Skill Needs

Identify what domain knowledge Claude needs for this project:
- What frameworks, libraries, and tools does the project actually use?
- Which domains need dedicated skills? (e.g., frontend framework, backend API, deployment)
- Do any existing skills in `.claude/skills/` already cover these well?
- Are there starters in `.claude/starter-skills/` that provide useful reference for building skills via `/skill-creator`?

Focus on what the project needs, not what starters happen to be available.

## 3. Signals Worth Closer Attention

Conventions agents commonly miss:
- custom response wrappers, error envelopes, or API shapes
- non-default utility choices (`cn()` vs `clsx()`, custom fetch client, internal form library)
- monorepo boundaries or ownership rules
- unusual test/lint/typecheck commands
- deployment constraints that influence code shape
- generated-code boundaries — files that must not be edited directly

These are candidates for placement decisions, not automatic rules.

## 4. Existing Docs Worth Reusing

Prefer pointing to good docs over duplicating them into `CLAUDE.md`:
- root and package-level READMEs
- architecture docs, ADRs, runbooks
- onboarding docs
- CI config, scripts, or Make targets that reveal canonical commands

## 5. Facts to Verify Before Claiming Them

Do not assert conventions without evidence:
- package manager and workspace layout
- frontend/backend boundaries
- test/lint/typecheck commands actually in use
- whether TypeScript/ESLint/Biome/Prettier are really present
- whether "all X lives in Y" is actually true
- whether a supposed shared utility is the standard path
