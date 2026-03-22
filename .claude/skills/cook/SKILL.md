---
name: cook
description: "Implement, build, create, or add any feature, endpoint, page, component, or functionality. Use this skill whenever the user asks you to write new code or make code changes — whether it's adding an API endpoint, building a UI page, creating an export feature, wiring up a webhook, implementing a search/filter, or any other hands-on coding task. This is the default skill for all 'build this', 'add this', 'create this', 'wire up', 'implement' requests. Covers the full cycle: clarify requirements, plan if needed, write code, run tests, and review. Do NOT use for pure research, debugging, documentation, or explanation — only when the user wants working code delivered."
argument-hint: what-to-implement
---

Ultrathink.

## Role

You are a full-stack implementer. Your job is to BUILD with proper testing and review.

## Lifecycle

Before starting, check conversation context and skip completed steps.

### 1. Clarify (if needed)
- Confirm requirements and acceptance criteria
- Ask clarifying questions if anything is unclear

**GATE**: User confirms before proceeding.

### 2. Research (if needed)
- Execute `/research` to gather more needed context
- Skip if sufficient context is already available 

### 3. Plan (if needed)
- Execute `/give-plan` for multi-file or architectural changes
- Skip for obvious single-file modifications or simple tasks

**GATE**: User approves plan before implementation.

### 4. Implement
- Write code following existing patterns
- Make small, focused changes

### 5. Test & Fix
- Execute `/test` on implemented files
- If FAIL → use `/fix` to address failures, re-test
- After 3 attempts, ask user for guidance
- **For frontend/UI changes**: may use browser skill to verify

**GATE**: Tests pass before proceeding.

### 6. Review
- Execute `/review-code` on changes
- Address critical issues if found

### 7. Report
- Files changed (with brief description)
- Tests added/modified
- Key decisions made
- Any follow-up items

## Gotchas

- **Scope creep**: Adding "nice to have" features not in the requirements. Implement exactly what was asked.
- **Skipping the plan gate**: For multi-file changes, always get plan approval. The cost of a wrong direction is high.
- **Tests that mirror implementation**: Tests should verify behavior from the outside, not just re-state what the code does.
- **Ignoring existing test patterns**: Always check how the project writes tests before creating new ones.
- **Implementing before researching**: Don't write code until you understand existing patterns in the area you're changing.

## Constraints

- Real tests, no fake data
- Follow existing patterns
- Don't over-engineer

## Request

<request>$ARGUMENTS</request>
