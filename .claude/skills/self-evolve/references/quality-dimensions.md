# Self-Evolve Checklists

Non-obvious traps and mechanical checks only. Nothing Claude would do anyway.

## Mechanical Checks

### Reference integrity
```bash
# In a skill directory — verify all referenced files exist
grep -oE '(references|workflows|scripts|templates)/[^\s\)]+' SKILL.md | while read p; do
  [ -e "$p" ] || echo "BROKEN: $p"
done

# In project root — verify CLAUDE.md on-demand references exist
grep -oE '\./[^\s\)]+\.md' CLAUDE.md | while read p; do
  [ -e "$p" ] || echo "BROKEN: $p"
done
```

## Staleness Signals

- `git log --oneline -5 -- src/database/` shows heavy churn but database skill unchanged → likely stale
- New directory `src/grpc/` appeared but no skill covers it → gap
- `git log --diff-filter=R -- src/lib/db.ts` shows rename but skill still references old path → broken
- Dependency major version bumped (React 18→19) but skill references old patterns → outdated

## Conflict Resolution Priority

When the same fact is stated differently across layers:
- **Rules win over skills** — rules are guardrails, wrong code if missed
- **Project refs win over CLAUDE.md** — refs are more detailed, CLAUDE.md is just an entry point
- **Orphaned on-demand refs are invisible** — if a reference file exists but CLAUDE.md doesn't point to it, agents will never load it

