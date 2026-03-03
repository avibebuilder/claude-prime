# Workflow Skill Patterns

Patterns specific to workflow-type skills (task runners like /cook, /fix, /discuss).
These extend the general skill principles in [design-principles.md](./design-principles.md).

## Thinking Directives (Optional)

Add after frontmatter, before `## Role`, only when enhanced reasoning is needed:

| Directive | When to Use |
|-----------|-------------|
| `Ultrathink.` | Complex analysis, planning, strategy |
| `Think harder.` | Focused debugging, code review |
| *(none)* | Standard reasoning - default, sufficient for most |

**Placement:** After YAML frontmatter closing `---`, before first `##` heading.

## Context Assessment

Workflow skills should check conversation history before starting to avoid duplicate work.

```markdown
## Context Assessment
Before starting, analyze conversation history:
- **[Condition 1]?** -> Skip [Phase X]
- **[Condition 2]?** -> Skip [Phase Y]
- Start from earliest incomplete phase
```

**When to skip phases:**
- Research already done -> Skip research phase
- Plan already approved -> Skip planning phase
- Same code already reviewed -> Focus on changes only

**Key principle:** Start from earliest incomplete phase (linear progression).

## Gates

Gates = checkpoints requiring user approval before continuing.

**When to use gates:**
- Before implementation (after planning)
- Before destructive actions
- After discovering scope changes
- Before final delivery

**Format:** `**GATE**: [What needs approval]`

## Role Boundaries

Effective roles define what they DON'T do:

| Skill | Does | Does NOT |
|-------|------|----------|
| /ask | Answer questions | Implement code |
| /test | Run tests | Fix failures |
| /review | Critique code | Apply fixes |
| /discuss | Debate options | Implement |

Pattern: "Your job is to X - not to Y."

## Skill Delegation

Workflow skills should delegate to other skills instead of reimplementing their logic. This is DRY — each skill owns its domain.

| Instead of... | Delegate to... |
|---------------|----------------|
| Running tests inline | Execute `/test` |
| Reviewing code inline | Execute `/review-code` |
| Fixing failures inline | Use `/fix` |
| Complex planning | Execute `/give-plan` |

```markdown
### 5. Test & Fix
- Execute `/test` on implemented files
- If FAIL → use `/fix` to address failures, re-test
- After 3 attempts, ask user for guidance
```

**Skill-to-skill delegation is encouraged.** It ensures consistent behavior whether invoked standalone or as part of a workflow.

**Agent delegation is NOT.** Skills should NOT reference specific agents or describe spawning patterns. The orchestrator decides how to execute agents.

## Isolation Patterns

Use `context: fork` in frontmatter when a skill benefits from running in an isolated context:

| Use `context: fork` when | Stay inline when |
|--------------------------|------------------|
| Heavy output (research, analysis) | Light interaction (ask, discuss) |
| Independent, self-contained task | Needs conversation history |
| Read-only exploration | Iterative back-and-forth |

Combine with `agent:` to run in a specific agent type:
```yaml
context: fork
agent: the-mechanic   # runs in the-mechanic's execution profile
```

## `$ARGUMENTS` Placeholder

Workflow skills receive user input via the `$ARGUMENTS` placeholder inside a tagged section at the end of the SKILL.md:

```markdown
## [Input Section Name]

<[tag-name]>$ARGUMENTS</[tag-name]>
```

The tag name should match the skill name (hyphens replaced with underscores).

## Required Sections

Every workflow skill MUST have:

| Section | Purpose |
|---------|---------|
| Frontmatter | `name` + `description` |
| Role | Who + Primary action + Boundaries |
| Process | Numbered steps with gates |
| Constraints | Explicit boundaries |
| Input | `$ARGUMENTS` placeholder |

## Anti-Patterns

| Bad | Good |
|-----|------|
| Vague role | Specific role + boundaries |
| No gates | Gates at critical points |
| Scope creep allowed | Explicit constraints |
| Being deferential | Being honest |
| Referencing specific agents | Delegating to skills |
| "Spawn subagent to explore" | "Explore codebase" or "Execute `/research`" |
| "Spawn subagent to run /test" | "Execute `/test`" |
| Asking ritual questions | Only ask when answers change direction |

## Quality Checklist

- [ ] Frontmatter has name + description
- [ ] Role states what it does AND doesn't do
- [ ] Process has numbered steps
- [ ] Gates at critical decision points
- [ ] Delegates to other skills instead of reimplementing (test, review, fix, plan)
- [ ] No references to specific agents by name
- [ ] Constraints list explicit boundaries
- [ ] $ARGUMENTS placeholder present
- [ ] Guidance at right altitude (not too vague, not too prescriptive)
- [ ] Avoids generic AI patterns (anti-convergence)
