# Refactoring an Existing Skill

## When to Refactor

- SKILL.md >150 lines
- Slow activation / context overflow
- Low relevance ratio (<50% of loaded content used)

## Step 1: Analyze Current State

```bash
wc -l skill-name/SKILL.md
wc -l skill-name/references/*.md 2>/dev/null
```

Identify: Total lines, content categories, what's loaded vs used.

## Step 2: Categorize Content

| Category | Move To | Example |
|----------|---------|---------|
| Detailed explanations | references/ | API docs, schemas |
| Multi-step procedures | workflows/ | Creation steps |
| Code examples | references/examples.md | Good/bad patterns |
| Quick commands | Keep in SKILL.md | Script invocations |
| Navigation/overview | Keep in SKILL.md | Links, summaries |

## Step 3: Create Target Structure

```bash
mkdir -p skill-name/{references,workflows}
```

## Step 4: Extract Content

1. Create new file in appropriate folder
2. Copy content, ensure within guidelines (<500 for references, <200 for workflows)
3. If exceeds guideline, consider splitting further
4. Replace original with link: `See [topic.md](./references/topic.md)`

## Step 5: Refactor SKILL.md

**Keep only:** Overview, quick start commands, navigation links, brief script descriptions.

**Target:** <80 lines (leave room for growth)

## Step 6: Verify

```bash
wc -l skill-name/SKILL.md
wc -l skill-name/references/*.md
scripts/validate_skill.py skill-name/
```

Target guidelines: SKILL.md <150, references <500, workflows <200 (soft limits)

## Step 7: Test Cold Start

1. Clear context, trigger skill, count lines loaded
2. Target: <500 lines on first activation

## Before/After Example

**Before:** `SKILL.md` (870 lines)
**After:** `SKILL.md` (181 lines) + references/ (3 files) + workflows/ (2 files)
**Result:** 79% reduction, 4.8x token efficiency
