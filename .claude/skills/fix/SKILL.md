---
name: fix
description: "Fix bugs and broken behavior. Use when the user reports something going wrong: errors, crashes, incorrect results, or unexpected behavior. This includes API errors (500, 404, 403), cross-origin/CORS problems, database exceptions, frontend crashes or rendering failures, wrong data (duplicates, off-by-one, wrong dates, timezone problems), broken forms or submissions, configuration issues causing runtime failures, and regressions where working features broke. Trigger whenever the user describes a symptom — an error message, a wrong result, a crash, a misbehaving UI element, or a request that fails. Do NOT use for new features, code explanations, architecture questions, research, or comparisons."
argument-hint: issue
---

Think harder.

## Role

You are a root cause fixer. Assess evidence, fix what's clear, and escalate to `/diagnose` when it's not.

## Process

Check conversation context and skip completed steps.

### 1. Triage

Assess whether there is enough evidence to fix directly:

| Signal | Action |
|--------|--------|
| Clear error message + obvious code bug (typo, wrong variable, missing null check) | Fix directly — skip to step 3 |
| Code looks correct but behavior is wrong | Invoke `/diagnose` first |
| Vague symptoms, no clear error path | Invoke `/diagnose` first |
| Diagnosis already exists in context (from prior `/diagnose`) | Use existing diagnosis — proceed to step 2 |

**If you're about to guess, stop and debug instead.**

### 2. Plan (if needed)

- Execute `/give-plan` for multi-file or architectural fixes
- Skip for obvious single-file bug fixes or simple tasks

**GATE**: User approves fix approach before implementation.

### 3. Fix

- Apply minimal fix that addresses the root cause
- Change only what's necessary
- Follow existing code patterns
- Do NOT remove any `#region agent log` instrumentation

### 4. Verify

Two-layer verification:

- Execute `/test` to verify tests pass
- If debug instrumentation exists: ask user to reproduce → read debug logs → confirm the runtime behavior has changed
- **For frontend/UI fixes**: may use browser skill to verify

**GATE**: Tests pass AND runtime evidence confirms fix (if instrumentation exists).

### 5. Cleanup

Review instrumentation left from debugging:

- Search for all `#region agent log` / `#endregion` blocks
- Remove temporary debug logs
- If any reveal valuable observability gaps → suggest converting to proper logging (user decides)
- Stop debug server if running
- Delete debug log files

## Gotchas

- **Fixing symptoms, not causes**: A null check at the crash site is rarely the real fix. Trace back to where the bad value originates.
- **Guessing without evidence**: If you're about to add a "maybe this will fix it" change, stop and use /diagnose instead.
- **Scope expansion**: Fix the reported bug. Don't refactor the surrounding code.
- **Forgetting instrumentation cleanup**: After fixing, remove ALL `#region agent log` blocks. Search the entire affected area.
- **Breaking other tests**: Run the full relevant test suite, not just the test for the fixed bug.

## Constraints

- Fix the actual cause, not symptoms
- NO workarounds that mask problems
- Don't refactor unrelated code
- If evidence is insufficient, invoke `/diagnose` — don't guess

## Issue

<issue>$ARGUMENTS</issue>
