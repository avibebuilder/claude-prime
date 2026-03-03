# Project Analysis Checklist

## Stack Detection

| Category | Look For | Files to Check |
|----------|----------|----------------|
| **Frontend** | React, Vue, Angular, Svelte | `package.json`, `*.tsx`, `*.vue` |
| **Backend** | Express, NestJS, FastAPI, Django | `package.json`, `requirements.txt`, `main.ts` |
| **Database** | Prisma, TypeORM, SQLAlchemy, Drizzle | `schema.prisma`, `ormconfig.ts`, `alembic/` |
| **Styling** | Tailwind, CSS Modules, Styled Components | `tailwind.config.*`, `*.module.css` |
| **Testing** | Jest, Vitest, Pytest | `jest.config.*`, `vitest.config.*`, `pytest.ini` |

## Convention Detection

### Code Style
- ESLint/Prettier config → coding standards
- TypeScript strict mode → type conventions
- Import ordering → module organization

### Architecture Patterns
- Folder structure → feature-based vs layer-based
- State management → Redux, Zustand, Context
- API patterns → REST, GraphQL, tRPC

### Project-Specific Rules
- Naming conventions (files, components, functions)
- Component patterns (client vs server, HOCs, hooks)
- Error handling approach
- Logging standards

## Placement Decision: Rule vs Reference

For each detected convention, apply the **rule test**:

> "If an agent edits a file matching this path without knowing this, will it produce incorrect code?"

| Answer | Where | Example |
|--------|-------|---------|
| **Yes** → Guardrail | `.claude/rules/<name>.md` with `paths:` | "Must use `cn()` not `clsx()`", "API responses use `ResponseWrapper`" |
| **No** → Guidance | `.claude/project/*.md` | "Feature-based folder structure", "Auth uses JWT with refresh" |

**Keep rule files short.** If it needs paragraphs of explanation, it's guidance, not a guardrail.

## Starter Skills Matching

After detecting the stack, browse `.claude/starter-skills/` for relevant domain starter skills. Copy matching starters to `.claude/skills/` and adapt tooling-specific parts if needed (e.g., swap Biome references for ESLint). For stacks without a matching starter, create a new skill via `/touch-skill`.

## Questions to Answer

1. **What stack is this?** → Browse `.claude/starter-skills/` for matching starters, use `/touch-skill` for uncovered stacks
2. **What hard constraints exist?** → Guardrails → `.claude/rules/` (auto-attached)
3. **What architectural context is useful?** → References → `.claude/project/` (on-demand)

## Red Flags (Likely guardrails — `.claude/rules/`)

- "We don't use TypeScript strict mode"
- "All components are client-side"
- "We use raw SQL, not ORM"
- "Custom authentication system"
- "Monorepo with special conventions"
