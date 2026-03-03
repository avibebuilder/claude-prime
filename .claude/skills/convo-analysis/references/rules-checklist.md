# Rules Checklist

Dynamic sources to check against when analyzing conversation behavior.

## Mandatory Rule Loading

**BEFORE analyzing any turn, MUST load ALL applicable rules:**

### Core Rules (Always Load)
| Source | Path | Must Read |
|--------|------|-----------|
| Orchestrator Directives | `.claude/hooks/orchestrator-directives.py` | ✓ Always |
| Apply-All Rules | `.claude/rules/_apply-all.md` | ✓ Always |
| Project Rules | `.claude/project/*` | ✓ Always |
| Core Principles | `CLAUDE.md` | ✓ Always |

### Contextual Rules (Based on Conversation)
| Source | Path | When to Load |
|--------|------|--------------|
| Commands | `.claude/commands/{invoked}.md` | When command was used |
| Skills | `.claude/skills/{activated}/SKILL.md` | When skill was activated |
| Agents | `.claude/agents/{spawned}.md` | When agent was spawned |

**Analysis without rule loading = incomplete analysis. Do not skip.**

---

## Analysis Process

1. **Load rules** - Read ALL core rules + contextual rules from conversation
2. **Classify each user message** by type (direct-request, meta-request, mixed-content, clarification)
3. **Identify commands/skills/agents** used in the conversation
4. **Compare actual vs expected** behavior against LOADED rules FOR BOTH parties
5. **Assign contribution percentages** based on observed issues

## What to Check

### User Message Patterns

#### Message Types
| Type | Indicators | Example |
|------|------------|---------|
| Direct Request | Clear action verb, single intent | "Fix the login bug" |
| Meta-Request | "here is...", "this conversation...", sharing context | "Here is my conversation with Claude..." |
| Mixed Content | Quoted content + actual request in same message | Pasted logs + "help me fix this" |
| Clarification | Responding to AI question | "Yes, use the second approach" |
| Feedback | Commenting on AI behavior | "I expected you to use /research" |

#### User Behavior Patterns

| Good | Bad | Impact |
|------|-----|--------|
| Clear request boundaries | Mixed quoted + actual content | AI analyzes wrong subject |
| Explicit context markers | Assumed AI knows context | AI makes wrong assumptions |
| One intent per message | Multiple buried requests | AI misses secondary requests |
| States expected approach | Only states desired outcome | AI picks wrong method |
| Uses code blocks for quotes | Inline pasted content | AI can't distinguish quote from request |

### AI Behavior Patterns

#### IMPORTANT: MUST ALWAYS analyze from orchestrator-directives.py and _apply-all.md
- Did AI follow agent-skill-driven rules?
- Did AI follow code quality rules?
- Extract actual rule text for accurate comparison

#### From Command Files
- Did AI follow the Process steps in order?
- Did AI respect GATE checkpoints?
- Did AI stay within Role boundaries?
- Did AI follow Guardrails (Holy Trinity)?

#### Universal AI Patterns

| Good | Bad |
|------|-----|
| Asked clarifying question | Assumed requirements |
| Waited for approval at gates | Proceeded without gate |
| Delegated appropriately | Did everything in main context |
| Stayed in scope | Added unrequested features |
| Identified unclear request | Guessed intent from ambiguous message |

## Contribution Assessment

When issues occur, assess contribution from both parties. For example

| Scenario | User Contribution | AI Contribution |
|----------|-------------------|-----------------|
| Unclear request + AI guessed | 70% | 30% (should have asked) |
| Clear request + AI ignored rules | 10% | 90% |
| Mixed content + AI wrong focus | 60% | 40% (should have clarified scope) |
| Clear request + AI followed rules | 0% | 0% (no issue) |
