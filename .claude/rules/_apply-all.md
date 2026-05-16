--
You MUST READ before acting

These rules are MANDATORY. NON-NEGOTIABLE. NO EXCEPTIONS. MUST FOLLOW AT ALL TIMES!!!

## Interaction

- When a request is unscoped or ambiguous, ask for clarification — don't guess or try to fulfill at all cost. EXCEPTION: for factual gaps you can fill with tools (Read, Grep, Glob, web search, etc.), investigate first and continue to ask if still unclear.
- PROACTIVELY use AskUserQuestion tool when asking the user, for better interaction and understanding.
- DO NOT rush/urge to jump to implementation until the user explicitly approves the approach. If requirements are unclear or the direction isn't agreed on — stop and align first.
- WORKTREE CLEANUP — After a subagent spawned with `isolation: "worktree"` completes and you've collected its outputs, clean up with `git worktree remove <path>`. Do not leave orphaned worktrees behind.

## Agent Discipline

- SKILL FIRST — ALWAYS load relevant skill(s) BEFORE any work in that domain — before exploring, planning, or writing code. No exceptions — even for small changes, even if you already read the file, even if your trained knowledge covers the topic.
- ZERO ASSUMPTIONS — If you haven't read it, fetched it, or verified it **in this conversation**, you don't know it — trained knowledge is stale or wrong. Find and give evidence before claiming anything. This applies equally to answering questions, explaining behavior, and implementing code. Proactively explore, read, and understand before proposing or doing anything — laziness (skimming, guessing, skipping steps) is the #1 failure mode. Verify runtime state (logs, DB contents, deployed files) from the source of truth, not from code that manages it.
- TRY BEFORE GIVING UP — Before declaring something impossible, read-only, blocked, or too hard, attempt it or explicitly test the constraint. Do not cite limitations without first verifying them.
- FRESH TIMESTAMPS — ALWAYS use `date +%Y%m%d%H%M%S` to get the latest timestamp. DO NOT use your provided time data since it may be stale.
- FRESH PACKAGES — WHEN installing packages, MUST find and install the latest version. DO NOT use versions from training data — they are stale.
- MEDIA ACCURACY — AFTER reading a media file, if it is visually complex (UI designs, dense screenshots, artworks, charts), MUST use `/media-processor` skill. Built-in vision has limited accuracy on complex visual content.
- PLAN MODE — When Claude Code's native plan mode is active, you MUST invoke the `give-plan` skill first before producing any plan. Plan mode provides the workflow structure (propose → approve → execute); `give-plan` shapes *how* to plan (ground in code, pick the right altitude, surface risks, right-size the artifact, stop-and-wait).

## Code Quality

- DO NOT over-engineer or prematurely optimize
- TRACE THE RIPPLE — After every change (rename, move, delete, interface change), grep for all references and update every affected call site, import, config entry, and doc in the same pass.
- ALWAYS align with existing codebase structure, style, and patterns
- DO NOT reinvent the wheel: MUST search for existing solutions FIRST — codebase, packages, libraries, CLI flags (`--help`), built-in tool capabilities, and documented workflows (scripts, skill files, workflow docs) — before implementing workarounds or manual alternatives. If an established process or pattern exists, use or extend it — never invent a parallel approach from scratch. Prefer established, well-maintained solutions over custom code.
- MUST NOT add unnecessary, obvious, or progress comments to code. Code should be self-documenting. Only add comments for non-obvious logic or complex business rules. Over-commenting is prohibited.
- SOLVE the root cause, not the symptom. When a user reports an example, treat it as a symptom of a broader problem — find the generic solution that covers all cases, not a narrow patch for that one example.
- NO PREMATURE COMPAT — If code is still developing - not pushed/merged yet, modify files directly. No backward compatibility shims, fallbacks, or additional migration files.

## Safety

- DO NOT run commands that are not documented in project configuration or documentation — only use commands found in package.json scripts, Makefile, CI config, or project docs
- MUST NOT run dev servers, build commands, database migrations, or start the project without explicit user approval. **STOP and ASK the user first — do NOT execute then ask. Ask BEFORE touching the Bash tool.** If the user hasn't said yes, tell them the exact command they can run themselves. For verification after code changes, use type checking, linting, or tests instead — the user is already running the project.

--