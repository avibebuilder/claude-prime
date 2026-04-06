---
name: self-evolve
description: >
  The single config quality skill. Two modes: (1) Default — review/wire pending self-improvement proposals. (2) Audit — analyzes skills, rules, CLAUDE.md, project refs, hooks, and agents against the actual codebase to find inaccuracies, trigger overlaps, stale references, and weak rules, then fixes them. Trigger on 'self-evolve', 'evolve', 'config health check', 'audit config', 'check claude setup', 'apply this rule', 'reorganize rules', 'ok' (when proposals are pending). NOT for improving individual skills (use skill-creator), diagnosing code bugs (use diagnose), or fixing broken code (use fix).
argument-hint: scope-or-focus-area
---

Ultrathink for full/scoped analysis. For `quick` scope and proposal review (no args), skip extended thinking.

**Context**: On primed target projects, fix locally and report upstream issues. On claude-prime itself, fix directly.

## Scope

| Argument | Effect | Speed |
|----------|--------|-------|
| (none) | Review/wire pending proposals. If none pending, ask user to fall back to full audit or not | fast~long |
| `full` | Full audit: all components + pending proposals | long |
| `skills` | Skill triggers, references, knowledge | medium |
| `rules` | Rule strength, relevance, overlap | medium |
| `claude-md` | CLAUDE.md accuracy and completeness | medium |
| `quick` | Quick health check (see below) — report only, no fixes | fast |

### Quick scope checklist

Skip Phase 1. Run only these 5 checks, report results:
1. Every `.claude/skills/*/SKILL.md` has `name:` and `description:` in frontmatter
2. All file paths in skill reference tables exist
3. All on-demand reference paths in CLAUDE.md exist (docs/, READMEs, etc.)
4. CLAUDE.md is under 200 lines
5. All hook scripts in `.claude/settings.json` point to files that exist and are executable

---

## Wire Mode: Apply Self-Improvement Proposals

When scope is `(none)`, or when pending proposals exist and user says "ok":

**Fetching proposals**: Query the DB for pending proposals:
```bash
python3 $CLAUDE_PROJECT_DIR/.claude/hooks/self-improve/self_improve_db.py resolve list
```
If no CLI `list` command exists, query directly:
```bash
sqlite3 $CLAUDE_PROJECT_DIR/.claude/local-data/self-improve.db "SELECT id, theme, content, rationale FROM proposals WHERE status='pending' ORDER BY created_at"
```
Show each proposal with its rationale. For each, ask the user to approve or reject.

### Step 1: Classify — where does it belong?

| Test | Question | If Yes |
|------|----------|--------|
| **Rule test** | "With the relevant skill activated, will an agent still produce incorrect code without this?" | → Rule (`.claude/rules/`) |
| **Skill test** | "Is this a repeatable process or workflow, not a constraint?" | → Skill (`.claude/skills/`) — rare |
| **On-demand ref test** | "Is this project-specific architecture or context, not a behavioral rule?" | → On-demand reference (wherever docs live — `docs/`, READMEs, etc.) pointed from CLAUDE.md |
| **Personal pref test** | "Is this specific to this user (role, sandbox URLs, preferred test data, workflow quirks) — not team-shared?" | → `CLAUDE.local.md` (gitignored, never shared) |
| **Default** | None clearly match? | → Rule (safest default) |

~90% of proposals become rules. The pipeline detects behavioral corrections, and corrections are rules by definition.

**CLAUDE.md vs CLAUDE.local.md**: Team-shared instructions go in `CLAUDE.md` (checked into source control). Personal preferences go in `CLAUDE.local.md` (gitignored). When wiring, always ask: "Would every team member need this, or just this user?"

### Step 2: Read existing content, check for overlap

Read all files in the target location. Scan for semantic overlap — does an existing rule/section already cover this?

### Step 3: Place — merge or add

- **If overlap exists**: merge into existing entry — expand/refine/strengthen, don't create near-duplicates
- **If distinct**: add under the most relevant section header

**Writing quality** — proposals describe specific incidents, but rules must work for the general case:

1. **Generalize from the incident.** The proposal says "Claude changed the pass dot when user meant N/A dot." The rule should address the *class*: "When multiple UI elements match an ambiguous reference, confirm which one before changing any." Don't encode the specific incident — encode the pattern.
2. **Ground in reasoning, not commands.** "ALWAYS confirm ambiguous references" is brittle — the agent doesn't know when it applies. "Because acting on the wrong target wastes a correction cycle, confirm which element when multiple candidates match" gives the agent judgment for edge cases.
3. **Trim while merging.** When adding to an existing rule file, read what's already there. If existing entries are redundant with the new content or with each other, consolidate. The goal after merging is a *tighter* file, not a longer one.
4. **Watch for accumulation.** If 3+ proposals have landed in the same file or section, that's a restructuring signal — the section may need splitting, or the underlying skill needs fixing instead of piling on more rules.
5. **Think from the agent's perspective.** Before finalizing, ask: "If I were an agent reading this rule for the first time with no context about the incident, would I understand *when* and *why* to apply it?" If the answer requires knowledge of the original proposal, rewrite.
6. **Re-read with fresh eyes.** After merging, re-read the entire section (not just your addition). Does the new content flow with the existing entries, or does it feel bolted on? Revise for coherence.

### Step 4: Verify — lightweight smoke test

The proposal's `rationale` describes the original failure. Use it to check the rule actually works:

1. **Construct a replay prompt** — extract the failure scenario from the rationale and write a minimal prompt that would trigger the same mistake (e.g., "Here's a UI with both pass and N/A dots. Change the dot color." — ambiguous on purpose).
2. **Spawn a subagent** with the new/updated rule file loaded. Give it the replay prompt against the current project (or a scratch context if the project isn't relevant).
3. **Check the result** — did the agent avoid the failure pattern? Specifically: did it ask for clarification, follow the new constraint, or otherwise behave differently than the original failure?
4. **If it fails**: revise the rule wording and re-verify once. If it still fails, flag to the user — the rule may need a different approach or the failure may not be addressable through rules alone.

Keep this fast — one prompt, one check, ~2 minutes. This is a smoke test, not an eval suite.

### Step 5: Resolve

Update the proposal status in the DB after user decision:

```bash
# If approved (after wiring):
python3 $CLAUDE_PROJECT_DIR/.claude/hooks/self-improve/self_improve_db.py resolve <id> approved

# If rejected:
python3 $CLAUDE_PROJECT_DIR/.claude/hooks/self-improve/self_improve_db.py resolve <id> rejected
```

### Step 6: Confirm

Tell the user: **what** was placed, **where** (file + section), **why** that location, and **whether verification passed**.

### Manual reorganization

When invoked for rule reorganization (not proposals): read all `.claude/rules/`, identify duplicates/misplaced rules, propose consolidation plan, apply on approval.

---

## Audit Mode: Proactive Config Analysis

When scope is `full`, `skills`, `rules`, `claude-md`, or `quick`. Also when `(none)` and no pending proposals found:

### Phase 1: Understand the Project

1. Read `package.json`, `pyproject.toml`, `go.mod`, or equivalent — know the stack
2. Scan top-level directory structure — know the architecture
3. Read CLAUDE.md — know what config claims about the project
4. Read `.claude/settings.json` — know what hooks are configured
5. If `.claude/hooks/self-improve/` exists, check for pending proposals by reading `.claude/local-data/self-improve.db` (SQLite). Query: `SELECT id, theme, content, rationale FROM proposals WHERE status='pending'`. Note them so you don't duplicate work.

### Phase 2: Analyze

Read `references/quality-dimensions.md` for mechanical check scripts, known trigger overlap zones, and conflict resolution rules.

**Skills** — for each domain skill (skip workflow skills for deep analysis, but DO check their trigger boundaries):

1. **Reference validity**: Extract all file paths from SKILL.md. Glob each — does it exist? Flag broken references as CRITICAL.
2. **Trigger boundaries**: Read this skill's description alongside ALL other descriptions. Look for two skills claiming the same phrasing pattern, or domain skills overlapping with `ask`, `discuss`, `give-plan`, `fix`, or `diagnose`.
3. **Knowledge accuracy**: For factual claims (file paths, tools, architecture), grep to verify. Sample 2-3 claims per skill.
4. **Completeness**: Flag CRITICAL gaps only. Report MODERATE gaps but don't fix them.

**Rules** — for each rule file:

1. **Strength**: If it uses "consider", "try to", "generally" — flag as MODERATE. Rules must be imperatives.
2. **Relevance**: Search the codebase for the pattern it protects. If gone → CRITICAL (stale).
3. **Cross-layer overlap**: If a skill already teaches it, the rule is redundant — flag as MODERATE.

**CLAUDE.md**:

1. **Factual accuracy**: Grep to verify "All X lives in Y" and "We use Z" claims.
2. **Reference validity**: Verify all on-demand reference paths in CLAUDE.md exist.
3. **Length**: Flag if over 200 lines.
4. **Cross-layer consistency**: Flag contradictions between CLAUDE.md, skills, and rules.

**CLAUDE.local.md** (if exists):

1. **Separation of concerns**: Flag any team-shared instructions that belong in `CLAUDE.md` instead. Personal file should only contain user-specific content (role, sandbox URLs, preferred test data, workflow quirks).
2. **Conflicts**: Flag contradictions with `CLAUDE.md` or rules — personal prefs must not override team guardrails.
3. **Staleness**: Check for references to paths, URLs, or tools that no longer exist.

**Hooks and settings**:
1. Verify each hook script path exists and is executable.
2. Check event types are appropriate for the script's purpose.

### Phase 3: Fix

**Severity**: CRITICAL (wrong code/skill, broken refs) → fix. MODERATE (suboptimal output) → fix if easy. LOW (style) → report only.

**What to fix**: broken refs, inaccurate facts, trigger overlaps in domain skills, weak rules, stale rules, redundant cross-layer content, broken hooks, orphaned project refs.

**What NOT to fix**: workflow skill descriptions (report for skill-creator), substantial completeness gaps (report as recommendation), things that work.

### Phase 4: Verify

For each fix: re-read, re-run the specific check, confirm it passes. Check no new broken refs introduced.

### Phase 5: Report

```markdown
## Self-Evolve Report

**Project**: {name}
**Scope**: {scope}
**Pending proposals**: {N or "pipeline not installed"}

### Fixed ({N})
| Component | Issue | Severity | What Changed |
|-----------|-------|----------|--------------|

### Detected but Not Fixed ({N})
| Component | Issue | Severity | Why Not Fixed |
|-----------|-------|----------|---------------|

### Upstream Recommendations (omit when running on claude-prime itself)
| Pattern | Affected Starter/Template | Suggested Fix |
|---------|--------------------------|---------------|

### Health: {verdict}
```

**Health verdicts**: HEALTHY (0 CRITICAL, ≤2 MODERATE) | NEEDS ATTENTION (unfixed MODERATE or 1 CRITICAL) | CRITICAL ISSUES (2+ CRITICAL)

If clean: "Config is healthy. Checked {N} skills, {N} rules, CLAUDE.md ({N} lines), CLAUDE.local.md ({present/absent}), {N} project refs, {N} hooks, {N} agents."

## Constraints

- **Stay in your lane.** Audits and fixes config quality + wires proposals. Does NOT create skills, prime projects, or fix code bugs.
- **Fix what's broken, not what's working.**
- **Respect knowledge layers.** Skills teach, rules guard, refs provide context.
- **Context-dependent.** Primed projects: fix locally, report upstream. Claude-prime: fix directly.
- **Don't bloat.** If a fix requires 50+ new lines, report as recommendation.
- **Don't weaken when merging.** Combined version must be at least as strong as the original.
