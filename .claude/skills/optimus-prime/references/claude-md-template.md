# CLAUDE.md Structure Guide

## Purpose

`./CLAUDE.md` is the **entry point only** for Claude in any project. It provides navigation to detailed content - NOT the content itself.

## Size Guideline

**Soft limit: ~200 lines**

If your CLAUDE.md exceeds 200 lines, you're likely including content that belongs in `.claude/project/` files.

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

### 2b. Architecture Constraints (if applicable)
If the project has **unconventional architecture that contradicts common assumptions**, surface it immediately after the overview. Example patterns that MUST be called out prominently:
- "There is NO backend API" (client-side-only data access)
- "No database ORM — raw SQL only"
- "No REST endpoints — everything is event-driven"
- "Frontend is statically deployed — no SSR/server"

These "no X" patterns are critical because Claude will default to the conventional approach without them. Use bold text and state both what the project does NOT do and what it does instead.

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

## Key Principles

1. **Entry point only** - Reference files, never duplicate content
2. **Dynamic loading** - Details are loaded on-demand from referenced files
3. **Scannable** - Should be readable in under 30 seconds
4. **Under 200 lines** - If longer, content belongs elsewhere
