# Skill Anatomy

## What Skills Are

Skills = modular packages extending Claude's capabilities with specialized knowledge, workflows, and tools.

Think: "onboarding guides" for specific domains—transform Claude from general-purpose to specialized agent.

## What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for file formats or APIs
3. **Domain expertise** - Company knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, assets for repetitive tasks

## Directory Structure

```
.claude/skills/
└── skill-name/
    ├── SKILL.md (required)
    │   ├── YAML frontmatter (name, description required)
    │   └── Markdown instructions
    └── Bundled Resources (optional)
        ├── scripts/      - Executable code
        ├── references/   - Documentation loaded on-demand
        ├── workflows/    - Step-by-step procedures
        ├── templates/    - Reusable file templates
        └── assets/       - Output files (images, fonts, templates)
```

## SKILL.md Requirements

**File name:** `SKILL.md` (uppercase)
**Line limit:** ~150 lines (soft guideline)

### YAML Frontmatter

```yaml
---
name: skill-name                    # Required: hyphen-case, matches directory
description: "..."                  # Required: when/why to use this skill
argument-hint: hint-text            # Optional: shown during autocomplete
disable-model-invocation: true      # Optional: prevent auto-invocation, manual /name only
user-invocable: false               # Optional: hide from / menu, background knowledge only
context: fork                       # Optional: run in isolated subagent context
agent: agent-name                   # Optional: which agent to use when context: fork
allowed-tools: Read, Grep, Glob    # Optional: restrict tools when skill is active
model: sonnet                       # Optional: model override when skill is active
---
```

### Frontmatter Decision Guide

| Want | Field |
|------|-------|
| User-only trigger (deploy, sync) | `disable-model-invocation: true` |
| Claude-only knowledge (conventions) | `user-invocable: false` |
| Run in isolated context (research) | `context: fork` |
| Run in specific agent (research in the-mechanic) | `context: fork` + `agent: the-mechanic` |
| Restrict tool access (read-only reviewer) | `allowed-tools: Read, Grep, Glob` |

### Metadata Quality

`name` and `description` determine when Claude activates the skill.

**Good description pattern:**
```
[Capability]. Use this skill when [action], [action], [action], or [action]. [Outcome].
```

**Example:**
```
"Frontend implementation patterns. Use this skill when creating components, building pages, styling UI, or fetching data. Provides rules for file structure and component syntax."
```

**Bad description:**
- Vague: "A skill for doing things"
- Tech-centric without actions: "React, Next.js, TypeScript patterns"
- Numbered lists: "(1) X, (2) Y, (3) Z" — use natural prose instead

### SKILL.md Body Design

**Philosophy (WHY) in SKILL.md:**
- Core principles and rules
- When/why to use certain patterns
- Key conventions as brief statements

**Patterns (HOW) in references:**
- Code examples and templates
- Detailed implementation guides
- Edge cases and variations

```
SKILL.md  = Philosophy (WHY) - always loaded, understand intent
references/ = Patterns (HOW) - loaded on-demand, see implementation
```

**Rules:**
1. Never duplicate content between SKILL.md and references
2. Never put foundational philosophy only in references (gets skipped)
3. Keep SKILL.md to principles, link to references for details
4. **Never put code blocks in SKILL.md** - all syntax examples, command snippets, and implementation patterns belong in references (code blocks = HOW = references)
