# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

# Project overview

A boilerplate toolkit that supercharges Claude Code with skills, commands, and workflows for agent-skill-driven development.

# Context engineering philosophy

Context engineering is about curating the optimal set of tokens to maximize desired model behavior. Unlike prompt engineering (crafting perfect prompts), context engineering considers the holistic state available to the LLM at any moment.

## Core Principles

### 1. Context is a Finite Resource
Models have limited attention budgets that degrade as context grows (context rot). Goal: **find the smallest high-signal set of tokens** that maximizes desired outcomes. Every token competes for attention.

### 2. Right-Altitude Prompting
Concrete but not hardcoded. Find the Goldilocks zone.

| Too Low (Brittle) | Too Vague | Right Altitude |
|-------------------|-----------|----------------|
| "Use Tailwind's blue-500" | "Make it look good" | "Use project's existing color system" |
| "Set font-size to 16px" | "Use appropriate sizing" | "Match surrounding components" |

### 3. Avoid Railroading Claude
Claude will generally try to stick to your instructions, and because Skills are so reusable you’ll want to be careful of being too specific in your instructions. Give Claude the information it needs, but give it the flexibility to adapt to the situation

### 4. Don’t State the Obvious
Claude Code knows a lot about your codebase, and Claude knows a lot about coding, including many default opinions. If you’re publishing a skill that is primarily about knowledge, try to focus on information that pushes Claude out of its normal way of thinking.

### 5. Anti-Convergence Patterns
LLMs default to high-probability outputs. Counter by listing what to avoid, suggesting uncommon alternatives, varying examples, and breaking monotony.

### 6. Just-in-Time Context Retrieval
Don't load everything upfront. Maintain lightweight identifiers (file paths, URLs) and retrieve dynamically at runtime.

### 7. Sub-Agent Architecture
Specialized sub-agents handle focused tasks with **clean context windows**, returning condensed summaries. Prevents context pollution, enables long-horizon tasks.

### 8. Structured External Memory
Use filesystem as extended memory. Write persistent notes/plans outside context window. Maintain todo lists in recent attention span.

### 9. Error Preservation
**Keep failures visible in context.** Failed attempts inform better strategies.



## Tool Design Principles

- **Self-contained:** Each tool independently understandable
- **Minimal overlap:** If engineers can't definitively choose the right tool, agents won't either
- **Descriptive parameters:** Unambiguous input names and descriptions
- **Token efficient:** Minimize wasted exploration

---

*Sources: [Anthropic - Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Manus - Context Engineering Lessons](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)*

# System architecture

## Skills (`.claude/skills/`)

| Type | When to create | Examples |
|------|---------------|----------|
| **Workflow skill** | Repeatable process with clear actions and instructions | `/give-plan`, `/cook`, `/fix`, `/test`, `/research` |
| **Domain knowledge skill** | Domain has project-specific patterns the agent must follow | Created per-project during priming or via `/skill-creator` |


## Starter Skills (`.claude/starter-skills/`)

Template skill kits shipped with the prime repo. During priming, `optimus-prime` copies relevant starters into the target project's `.claude/skills/`, adapts generic parts, and deletes the `starter-skills/` folder.

**Hub-and-spoke pattern**: Complex skills use SKILL.md as the hub (always loaded, <500 lines) that dispatches to spoke files (`references/`, `workflows/`, `templates/`) loaded on demand. This keeps the main file focused while supporting deep reference content.

## Knowledge system

| Layer | Location | Loading | Content |
|-------|----------|---------|---------|
| **CLAUDE.md** | `CLAUDE.md` | Always | Entry point — project identity, commands, stack, on-demand reference pointers |
| **Skills** | `.claude/skills/` | On-demand by agent | Framework/library knowledge, workflows |
| **Rules** | `.claude/rules/` | Auto-attached by path | Guardrails — wrong code if missed |
| **Agent memory** | `.claude/agent-memory-local/` | Auto-injected per agent | Runtime-discovered knowledge |

**Rule test**: "With the relevant skill activated, will an agent still produce incorrect code without this?" Yes -> rule. No -> skill. Rules are optional.

**Memory test**: "Can this only be learned by working in the project, not authored upfront?" Yes -> agent memory. No -> skill or rule.

On-demand references can live anywhere — just point to them from CLAUDE.md. Use `docs/` for human documentation. For complex projects where human docs are too verbose for agents, `.claude/project/` can optionally hold agent-optimized references (dense, scannable format).

## Configuration scope

| Put here | When |
|----------|------|
| `CLAUDE.md` | Team-shared instructions checked into source control — architecture, coding standards, common workflows |
| `CLAUDE.local.md` | Personal preferences for this project (gitignored) — your role, sandbox URLs, preferred test data, workflow quirks |
| `.claude/rules/_apply-all.md` | Universal rules for all agents (main + subagents) |
| `.claude/hooks/orchestrator-directives.py` | Orchestrator-only behavioral rules (main agent only) |

