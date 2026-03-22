--
# MUST READ before acting

## Agent Discipline

- ZERO ASSUMPTIONS — If you haven't read it, fetched it, or verified it **in this conversation**, you don't know it — including your trained knowledge, must not trust it since it's stale or wrong. Find and give evidence before claiming anything. This applies equally to answering questions, explaining behavior, and implementing code — not just "before acting." Code describes intent, not actual state — verify runtime state (running logs, DB contents, deployed files,..) from the source of truth, not from reading the code that manages it.
- TRY BEFORE GIVING UP — Before declaring something impossible, read-only, blocked, or too hard, attempt it or explicitly test the constraint. Do not cite limitations without first verifying them.
- MUST be PROACTIVELY thorough — explore, read, and understand before proposing or doing anything. Laziness (skimming, guessing, skipping steps, not checking) is the #1 failure mode.
- ALWAYS use `date +%Y%m%d%H%M%S` command to get latest timestamp, DO NOT use your provided time data since it may be stale
- WHEN installing packages, MUST find and install the latest version. DO NOT use versions from training data — they are stale
- MUST check `.claude/project/` for project-specific context before acting — it contains architecture decisions, common things like commands, scripts and constraints that aren't visible in the code alone. Skipping this leads to solutions that ignore how the project actually works.
- ALWAYS load relevant skill(s) BEFORE any work in that domain — before exploring, planning, or writing code. The skill comes first, not right before implementation. No exceptions — even for small changes, even if you already read the file, even if your trained knowledge covers the topic.
- AFTER reading a media (mostly images) if this is complicated (UI designs, dense screenshots, artworks, charts), MUST use `/media-processor` skill for better understanding — your built-in vision has limited accuracy on visually complex content.

## Code Quality

- DO NOT over-engineer or prematurely optimize
- DO NOT go out of scope of user requests
- Our code must remain clean. ALWAYS align with existing codebase structure, style, and patterns
- DO NOT reinvent the wheel: MUST search for existing solutions FIRST — codebase, packages, libraries, CLI flags (`--help`), built-in tool capabilities, and documented workflows (scripts, skill files, workflow docs) — before implementing workarounds or manual alternatives. If an established process or pattern exists, use or extend it — never invent a parallel approach from scratch. Prefer established, well-maintained solutions over custom code.
- MUST NOT add unnecessary, obvious, or progress comments to code. Code should be self-documenting. Only add comments for non-obvious logic or complex business rules.
- SOLVE the root cause, not the symptom. When a user reports an example, treat it as a symptom of a broader problem — find the generic solution that covers all cases, not a narrow patch for that one example.
- If we are still developing (not pushed/merged code yet), modify files directly — there's no need to maintain backward compatibility or add fallbacks or additional migration files

## Safety

- DO NOT run commands that are not documented in project configuration or documentation — only use commands found in package.json scripts, Makefile, CI config, or project docs
- MUST NOT run dev servers, build commands, database migrations, or start the project without explicit user approval. **STOP and ASK the user first — do NOT execute then ask. Ask BEFORE touching the Bash tool.** If the user hasn't said yes, tell them the exact command they can run themselves. For verification after code changes, use type checking, linting, or tests instead — the user is already running the project.

--