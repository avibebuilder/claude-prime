# Audit Checklists

## Skills
For each domain skill (skip workflow skills for deep analysis, but DO check their trigger boundaries):

1. **Reference validity**: Extract all file paths from SKILL.md. Glob each — does it exist? Flag broken references as CRITICAL.
2. **Trigger boundaries**: Read this skill's description alongside ALL other descriptions. Look for two skills claiming the same phrasing pattern, or domain skills overlapping with `ask`, `discuss`, `give-plan`, `fix`, or `diagnose`.
3. **Knowledge accuracy**: For factual claims (file paths, tools, architecture), grep to verify. Sample 2-3 claims per skill.
4. **Completeness**: Flag CRITICAL gaps only. Report MODERATE gaps but don't fix them.

## Rules
For each rule file:

1. **Strength**: If it uses "consider", "try to", "generally" — flag as MODERATE. Rules must be imperatives.
2. **Relevance**: Search the codebase for the pattern it protects. If gone → CRITICAL (stale).
3. **Cross-layer overlap**: If a skill already teaches it, the rule is redundant — flag as MODERATE.

## CLAUDE.md
1. **Factual accuracy**: Grep to verify "All X lives in Y" and "We use Z" claims.
2. **Reference validity**: Verify all on-demand reference paths exist.
3. **Length**: Flag if over 200 lines.
4. **Cross-layer consistency**: Flag contradictions between CLAUDE.md, skills, and rules.

## CLAUDE.local.md (if exists)
1. **Separation of concerns**: Flag team-shared instructions that belong in `CLAUDE.md`. Personal file should only contain user-specific content (role, sandbox URLs, preferred test data, workflow quirks).
2. **Conflicts**: Flag contradictions with `CLAUDE.md` or rules — personal prefs must not override team guardrails.
3. **Staleness**: Check for references to paths, URLs, or tools that no longer exist.

## Hooks and settings
1. Verify each hook script path exists and is executable.
2. Check event types are appropriate for the script's purpose.

---

## Report Template

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

If clean: "Config is healthy. Checked {N} skills, {N} rules, CLAUDE.md ({N} lines), CLAUDE.local.md ({present/absent}), {N} project refs, {N} hooks, {N} agents."
