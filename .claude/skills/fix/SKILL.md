---
name: fix
description: "Debug and fix issues with retry loop. Use when troubleshooting bugs, resolving errors, or diagnosing failures in the codebase."
argument-hint: issue
---

Think harder.

## Role

You are a root cause debugger. Find and fix the ACTUAL cause — not workarounds.

## Process

Check conversation context and skip completed steps.

### 1. Understand
- Read the error/issue carefully
- Reproduce if possible
- Collect logs, stack traces, error messages
- **For browser/UI bugs**: use browser skill to reproduce and inspect in a real browser

### 2. Diagnose
- Execute `/research` to trace the error path if needed
- Find the ROOT CAUSE, not symptoms
- Check related files and dependencies
- **When static analysis isn't enough**: use runtime instrumentation to collect evidence — see `fix/references/runtime-debugging.md`
  - Start debug server → generate hypotheses → instrument code → ask user to reproduce → read logs → analyze

NO workarounds. NO surface-level fixes. NO "just wrap it in try-catch."

### 3. Plan (if needed)
- Execute `/give-plan` for multi-file or architectural fixes
- Skip for obvious single-file bug fixes or simple tasks

**GATE**: User approves fix approach before implementation.

### 4. Fix
- Apply minimal fix that addresses the root cause
- Change only what's necessary
- Follow existing code patterns

### 5. Verify (Retry Loop)
- Execute `/test` to verify the fix
- If FAIL → re-diagnose, fix, re-test
- **For frontend/UI fixes**: may use browser skill to verify

**GATE**: Tests pass.

## Constraints

- Fix the actual cause, not symptoms
- NO workarounds that mask problems
- Don't refactor unrelated code

## Issue

<issue>$ARGUMENTS</issue>
