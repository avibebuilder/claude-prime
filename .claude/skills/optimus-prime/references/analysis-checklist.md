# Project Analysis Checklist

Non-obvious things to look for during codebase analysis. Skip the obvious (stack detection, folder scanning) — Claude already does that well.

## Placement Decision: Rule vs CLAUDE.md vs Docs

For each detected convention, apply the **rule test**:

> "If an agent edits a file matching this path without knowing this, will it produce incorrect code?"

| Answer | Where | Example |
|--------|-------|---------|
| **Yes** → Guardrail | `.claude/rules/<name>.md` with `paths:` | "Must use `cn()` not `clsx()`", "API responses use `ResponseWrapper`" |
| **No** → Always-on context | `CLAUDE.md` (brief), `docs/` (human docs), or `.claude/project/` (agent-optimized, optional) — referenced from CLAUDE.md | "Feature-based folder structure", "Auth uses JWT with refresh" |

## Red Flags (likely guardrails)

These patterns often trip up agents even with the right skill loaded — strong candidates for rules:

- "We don't use TypeScript strict mode"
- "All components are client-side"
- "We use raw SQL, not ORM"
- "Custom authentication system"
- "Monorepo with special conventions"

## Questions Worth Answering

1. **What hard constraints exist?** → Things that cause wrong code if missed → `.claude/rules/`
2. **What always-on context does the agent need?** → `CLAUDE.md`
3. **What existing docs can agents reference on-demand?** → Point from CLAUDE.md
