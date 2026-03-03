# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

<!-- Brief description (1-2 sentences) of what this project does -->

## Project References

<!-- TODO: Reference specific files. Rules in .claude/rules/ are auto-attached — do NOT list them here. -->
- Architecture: `./.claude/project/architecture.md`
- Overview: `./.claude/project/overview.md`

## Repository Structure

```
project/
├── src/           # Source code
├── docs/          # Domain documentation
└── .claude/
    ├── rules/     # Path-scoped guardrails (auto-attached)
    └── project/   # On-demand references
```

<!-- Customize to match actual structure. Keep under 15 lines. -->

## Quick Reference

| Resource | Location |
|----------|----------|
| Docs | `./docs/` |

<!-- Links only - no explanations -->

## Critical Rules

**IMPORTANT:** ALWAYS check `.claude/project/` for project-specific context before implementation.

**IMPORTANT:** Analyze the skills catalog and activate the skills that are needed for the task during the process.

<!--
REMINDER: This file should stay under 100 lines.
All details (commands, code patterns, env vars) belong in .claude/project/ files.
-->
