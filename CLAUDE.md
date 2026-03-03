# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

# Project overview

A boilerplate toolkit that supercharges Claude Code with skills, commands, and workflows for agent-skill-driven development.

# Context engineering philosophy

Context engineering is about curating the optimal set of tokens to maximize desired model behavior. Unlike prompt engineering which focuses on crafting perfect prompts, context engineering considers the holistic state available to the LLM at any moment.

## Core Principles

### 1. Context is a Finite Resource
Models have limited "attention budgets" that degrade as context grows (context rot). The goal: **find the smallest high-signal set of tokens** that maximizes desired outcomes. Every token competes for attention—be ruthless about what enters context.

### 2. Right-Altitude Prompting
Guidance should be concrete but not hardcoded—find the Goldilocks zone.

| Too Low (Brittle) | Too Vague | Right Altitude |
|-------------------|-----------|----------------|
| "Use Tailwind's blue-500" | "Make it look good" | "Use project's existing color system" |
| "Set font-size to 16px" | "Use appropriate sizing" | "Match surrounding components" |

### 3. Anti-Convergence Patterns
LLMs default to high-probability outputs. Counter this by:
- **List what to avoid:** "Skip purple gradients—AI cliché", "Avoid Inter fonts—overused"
- **Suggest uncommon alternatives:** "Consider X even though Y is more common"
- **Vary examples:** Show multiple valid approaches, not just one pattern
- **Break monotony:** Introduce controlled variation in templates and phrasing

### 4. Just-in-Time Context Retrieval
Don't load everything upfront. Maintain lightweight identifiers (file paths, URLs) and retrieve dynamically at runtime. This mirrors human cognition—discover relevant context through exploration as each interaction informs the next decision.

### 5. Sub-Agent Architecture
Specialized sub-agents handle focused tasks with **clean context windows**, returning condensed summaries to the orchestrating agent. This prevents context pollution and enables long-horizon tasks. Delegate for results; keep context for decisions.

### 6. Structured External Memory
Use filesystem as extended memory—unlimited and persistent. Key practices:
- Write persistent notes/plans outside context window
- Keep compression reversible (preserve URLs even if dropping content)
- Maintain todo lists to keep objectives in recent attention span
- Preserve architectural decisions across sessions

### 7. Error Preservation
**Keep failures visible in context.** Cleaning up error traces prevents the model from learning and adjusting future actions. Failed attempts inform better strategies.

## Tool Design Principles

- **Self-contained:** Each tool should be independently understandable
- **Minimal overlap:** If engineers can't definitively choose the right tool, agents won't either
- **Descriptive parameters:** Unambiguous input names and descriptions
- **Token efficient:** Design to minimize wasted exploration

---

*Sources: [Anthropic - Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Manus - Context Engineering Lessons](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)*

# System architecture

## Skills (`.claude/skills/`)

| Type | When to create | Examples |
|------|---------------|----------|
| **Workflow skill** | A repeatable process that should be consistent across sessions with clear actions, tasks and instructions | `/give-plan`, `/cook`, `/fix`, `/test`, `/research` |
| **Domain knowledge skill** | A domain has project-specific patterns the agent must follow, act as add-on knowledge for the agent when needed | Created per-project during priming or via `/touch-skill` |

## Starter Skills (`.claude/starter-skills/`)

Sample domain starter skill kits shipped with the prime repo. During priming, `optimus-prime` copies relevant starters into the target project's `.claude/skills/`, where they become active skills. The `starter-skills/` folder is deleted from target projects after priming — final skills live in `.claude/skills/`.

## Subagents (`.claude/agents/`)

Unit of execution profile when we need to isolate context or have specialized behavior. Skills can specify which agent to run in via frontmatter.

## Knowledge system

| Layer | Location | Loading | Content |
|-------|----------|---------|---------|
| **Skills** | `.claude/skills/` | On-demand by agent | General framework/library knowledge |
| **Rules** | `.claude/rules/` | Auto-attached by path | Guardrails — wrong code if missed |
| **Project references** | `.claude/project/` | On-demand via CLAUDE.md | Architecture, structure, domain context |
| **Agent memory** | `.claude/agent-memory-local/` | Auto-injected per agent | Runtime-discovered knowledge from doing work |

Rule test: "With the relevant skill activated, will an agent still produce incorrect code without this?" Yes → rule. No → skill or project reference. Rules are optional — zero rules is valid.

Memory test: "Can this only be learned by working in the project, not authored upfront?" Yes → agent memory. No → skill, rule, or project reference.

## Configuration scope

| Put here | When |
|----------|------|
| `CLAUDE.md` | Entry point, references `.claude/project/` for on-demand context |
| `.claude/rules/_apply-all.md` | Universal rules for all agents (main + subagents) |
| `.claude/hooks/orchestrator-directives.py` | Orchestrator-only behavioral rules (main agent only) |