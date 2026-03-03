# Skill Examples: Good vs Bad

## Exemplary: docs-seeker (pure knowledge)

```
docs-seeker/
└── SKILL.md (~120 lines)         ← Self-contained knowledge skill
```

**Why it works:**
- Declarative knowledge the AI applies with judgment
- No scripts wrapping what the AI already does natively (URL construction, intent detection)
- Source priority chain, URL patterns, and known mappings in one file
- Zero maintenance burden — no tests, no dependencies

## Anti-Pattern: Monolithic Skill

```
my-skill/
└── SKILL.md (1,131 lines)        ← Everything in one file
```

**Problems:** Loads irrelevant info 90% of time, slow activation, context overflow.

## Refactoring Example

**Before:** 870 lines in one SKILL.md
**After:** 181 lines + 8 reference files + 5 workflow files
**Results:** 79% reduction, 4.8x token efficiency

## Writing Patterns

### Good: Script-First
```markdown
Execute scripts—they handle URL construction:
scripts/process.py input.txt
```

### Bad: Inline Everything
```markdown
First, construct the URL by taking the base...
Then parse the response... (200 more lines)
```

### Good: Link to Details
```markdown
See [errors.md](./references/errors.md) for fallback strategies.
```

### Bad: Embed Details
```markdown
Error 404: handle by... Error 500: fallback to... (50 more lines)
```

## Checklist

- [ ] SKILL.md ~150 lines (complex skills may exceed)
- [ ] Scripts have tests?
- [ ] Navigation links, not embedded content?
- [ ] Cold start loads <500 lines total?
