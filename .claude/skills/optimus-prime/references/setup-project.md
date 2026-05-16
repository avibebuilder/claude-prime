# Full Project Setup Workflow

Default workflow for both fresh prime and re-prime. SKILL.md has the mode split, principles, and Placement Decision Matrix; this file is the step-by-step. Steps 3–5 are the matrix applied in order.

## Step 1: Analyze the Repo and Existing Config

Explore the codebase deeply. The goal is to understand what makes this project unique — what conventions, patterns, and constraints Claude needs to know to work well here.

Summarize:
- stack, package manager, workspace shape, major app boundaries
- test/lint/typecheck commands actually used
- conventions, patterns, and project-specific utilities
- existing docs worth referencing from `CLAUDE.md`
- existing Claude config that should be preserved, refined, or removed

Use [analysis-checklist.md](../references/analysis-checklist.md) for non-obvious inspection targets.

## Step 2: Present the Discussion Summary

Before changing meaningful files, report back using the Output Format from SKILL.md (Current State / Proposed Changes / Files to Touch, plus Decisions and Risks when non-empty).

**Apply the Placement Decision Matrix here.** For every detected need from Step 1, name the layer it belongs in and the test that put it there. If a need fails every test, it does not get added — generic boilerplate degrades context quality.

Analysis is safe to run immediately. Overwrites, deletions, or wholesale regeneration require user confirmation.

## Step 3: Create Project Skills

Skills are the foundation. Everything else depends on having the right domain knowledge in place.

Review existing `.claude/skills/` first. Prefer refining strong project skills over creating new ones.

For each skill the project needs:
1. **Identify the gap** — what domain knowledge is missing or weak?
2. **Check starters** — does `.claude/starter-skills/` have reference material for this domain? If so, pass it as input to skill-creator.
3. **Run `/skill-creator`** — every skill must be created through skill-creator. This ensures quality, proper structure, and project-specific fit (CREATE skill only - don't optimize it this phase)

Starters are reference material that accelerate skill-creator — they are not standalone templates to copy into the project. A starter for "frontend-development" doesn't mean the project gets a generic frontend skill; it means skill-creator has a head start when building a skill fitted to this project's specific frontend stack and patterns.

**Gate:** important frameworks and domains should have skill coverage before you move on to rules or CLAUDE.md.

## Step 4: Identify Path-Scoped Rules (if any)

Rules are optional. Zero rules is a valid outcome.

A rule is a **correctness guardrail**, not a knowledge file. Path scoping is its delivery mechanism — it only fires when an edited file matches `paths:`. If something has no natural path scope, or a skill could teach it, it is not a rule.

Rule test:
> With the relevant skill activated, will code still be wrong without this information?

- **Yes** → path-scoped `.claude/rules/<name>.md` with `paths:`
- **No** → skill, CLAUDE.md, or on-demand reference

Red flags — something is **not** a rule:
- it applies broadly to a language or framework rather than this repo
- a reusable skill should already teach it
- it is informative context, not a correctness guardrail

Do not modify `_apply-all.md`. It is a universal boilerplate rule from prime, not project config.

**Gate:** review proposed rules with the user before creating them.

## Step 5: Generate or Refine CLAUDE.md

CLAUDE.md is the **always-on entry point** — project identity, commands, stack, key architecture, and pointers to on-demand references. Keep it lean; detail belongs in docs, skills, or on-demand references.

Priorities:
- identity, commands, stack summary — concise
- key architecture decisions that affect most tasks
- pointers to existing docs, READMEs, and on-demand references
- do not duplicate what skills already teach
- do not mention rules or skills here (they auto-attach by path)
- prefer refining a good existing CLAUDE.md over regenerating it

If existing docs are too verbose for agents, an optional `.claude/project/` reference layer can hold dense, agent-oriented references.

## Step 6: Offer CLAUDE.local.md Setup

Ask whether the user wants to have personal, gitignored preferences — role, sandbox URLs, preferred test data, workflow quirks. If yes, create or refine `CLAUDE.local.md` and ensure `.gitignore` covers it.

## Step 7: Domain Documentation (only if it adds value)

If important business logic is undocumented, use `/create-doc` to populate `docs/` with durable explanations — business rules, domain concepts, workflows, state machines. Reference these from CLAUDE.md rather than duplicating them into always-on context.

## Step 8: Clean Up Carefully

Cleanup targets:
1. `.claude/starter-skills/` after starters have been used as reference
2. skills that clearly do not fit the target repo
3. obsolete Claude config being intentionally replaced

### Protected skills (never delete during priming)

Keep these regardless of stack — they are workflow, meta, or universal utility skills:

- **Workflow:** `cook`, `fix`, `test`, `review-code`, `ask`, `discuss`, `give-plan`, `create-doc`, `diagnose`
- **Meta / tooling:** `optimus-prime`, `prime-sync`, `skill-creator`, `self-evolve`
- **Universal utilities:** `docs-seeker`, `media-processor`

Capability skills like `frontend-design` or `agent-browser` may be removed when the project clearly does not need them (e.g. `frontend-design` in a backend-only repo). When unsure, keep the skill and ask the user.

**Gate:** list proposed deletions and confirm before removing anything.

## Step 9: Verify

Spot-check:
- references in `CLAUDE.md` and skill tables point to real files
- skills are project-specific, not generic boilerplate
- stated stack and commands match repo evidence
- proposed rules actually pass the rule test
- `CLAUDE.md` stays compact enough to earn its always-on status

For ongoing config health checks, recommend `/self-evolve`.

## Step 10: Offer Skill Optimization

Everything is set up and working. Now offer optimization for the new skills that were created. **Always emphasize upfront that full optimization takes meaningful time and tokens** — the user should make an informed call.

**Run sequentially — never in parallel.** `/skill-creator` runs are CPU/memory-heavy and lag the user's machine when concurrent. Applies to both full and description-only modes — finish one before starting the next.

The two optimization modes:

| Option | What it does | Pros | Cons |
|---|---|---|---|
| **Description optimization only** | Optimizes skill descriptions for highest invocation accuracy | Fast, low cost | Skills may have weak instructions that only surface during real use |
| **Full optimization** | Runs evals loop + self-improve iterations + description optimization | Skills are battle-tested before the user depends on them. Catches instruction gaps, wrong behaviors, and weak triggers early | Takes meaningful time and tokens |

Recommend based on the number of new skills created:

- **≤3 new skills** — recommend **full optimization for all** of them. The volume is small enough that the time/token cost is acceptable for skills the user will rely on daily.
- **>3 new skills** — recommend a **split strategy**: full optimization for **core skills only** + description optimization for the rest. Full-optimizing every skill at this volume is too slow and too expensive.
  - **Propose which skills are core, with reasoning** — use what you know about the project (stack, primary workflows, which skills will fire most often, which carry the highest blast radius if they misbehave) to nominate 2–3 core skills. Show your picks with one-line justification for each, then let the user confirm or swap. Do not dump the full list and ask "which are core?" — that pushes the thinking onto the user.

In all cases, let the user override the recommendation or skip optimization entirely.

## Output Summary

```
./CLAUDE.md                       # Always-on project context
./CLAUDE.local.md                 # Personal preferences(gitignored, optional)
./docs/                           # Domain knowledge (optional)
.claude/
├── rules/
│   └── <name>.md                 # Path-scoped guardrails (optional)
└── skills/
    └── <project-skill>/          # Project-specific skills via skill-creator
```
