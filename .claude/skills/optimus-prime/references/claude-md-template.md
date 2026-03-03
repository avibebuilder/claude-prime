# CLAUDE.md Structure Guide

## Purpose

`./CLAUDE.md` is the **entry point only** for Claude in any project. It provides navigation to detailed content - NOT the content itself.

## Size Guideline

**Soft limit: ~100 lines**

If your CLAUDE.md exceeds 100 lines, you're likely including content that belongs in `.claude/project/` files.

## Content Boundaries

| Content Type | CLAUDE.md | .claude/project/ |
|--------------|-----------|------------------|
| Project overview (1-2 sentences) | ✓ | |
| Project rules table (references) | ✓ | |
| Repository structure (basic tree) | ✓ | |
| Quick reference links | ✓ | |
| CLI commands with explanations | ✗ | `commands.md` |
| Code examples/patterns | ✗ | `conventions.md` |
| Tech stack details | ✗ | `architecture.md` |
| Environment variables | ✗ | `architecture.md` |
| Known pitfalls/gotchas | ✗ | `pitfalls.md` |
| Detailed workflows | ✗ | relevant `.md` file |

## Prohibited in CLAUDE.md

These MUST live in `.claude/project/` files instead:

1. **Code examples** - No code blocks showing patterns
2. **Command lists** - No detailed CLI command explanations
3. **Detailed patterns** - No API conventions, decorators usage, etc.
4. **Environment variables** - No env var lists
5. **Inline documentation** - No explanations that belong in separate files

## Required Sections

### 1. Header
```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.
```

### 2. Project Overview
One to two sentences describing what the project does. Keep it brief.

### 3. Project Rules (References Only)
```markdown
## Project Rules

| File | Content |
|------|---------|
| [conventions.md](.claude/project/conventions.md) | Code patterns, API conventions |
| [commands.md](.claude/project/commands.md) | CLI commands and scripts |
| [pitfalls.md](.claude/project/pitfalls.md) | Known gotchas |
```

### 4. Repository Structure
Basic tree showing top-level organization. Max 10-15 lines.

### 5. Quick Reference (Links Only)
```markdown
## Quick Reference

| Resource | Location |
|----------|----------|
| API docs | http://localhost:3000/api-docs |
| Schema | `path/to/schema` |
```

### 6. Critical Rules (Always Loaded)

**Exception to on-demand loading.** Critical Rules are rules that MUST be remembered every conversation. They are NOT loaded on demand - they stay in CLAUDE.md.

```markdown
## Critical Rules

**IMPORTANT:** ALWAYS check `.claude/project/` before implementation.
**IMPORTANT:** Project rules take precedence over skill guidelines.
**IMPORTANT:** Analyze skills catalog and activate needed skills.
```

**What belongs here:**
- Rules that must be enforced every single conversation
- Reminders that prevent common mistakes
- Process requirements (check X before Y)

**What does NOT belong here:**
- Content that duplicates `.claude/project/` files
- Detailed explanations (keep rules concise)
- Anything that can be loaded on-demand when needed

## Key Principles

1. **Entry point only** - Reference files, never duplicate content
2. **Dynamic loading** - Details are loaded on-demand from referenced files
3. **Scannable** - Should be readable in under 30 seconds
4. **Under 100 lines** - If longer, content belongs elsewhere
