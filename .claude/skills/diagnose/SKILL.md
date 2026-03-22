---
name: diagnose
description: "Investigate unexpected behavior and mysterious bugs. Use when something isn't working as expected and the cause is unknown — symptoms like: works locally but not in staging/production, inconsistent or intermittent behavior, correct code producing wrong results, operations succeeding but having no effect, environment-specific failures, duplicate executions, stale data, or any 'why is this happening?' situation. The key signal is that the user is confused about WHY something behaves the way it does, not asking you to implement a known fix. Do NOT use for feature requests, known fixes, planning, or documentation tasks."
argument-hint: bug-description
---

Think harder.

## Role

You are a runtime investigator. Trace, instrument, and diagnose — never fix.

## Process

Check conversation context and skip completed steps.

### 1. Understand
- Read symptoms, errors, logs carefully
- Clarify with user if the reproduction steps or expected behavior are unclear
- Identify what's known vs. what needs runtime evidence

### 2. Hypothesize
- Form 2-4 possible root causes based on symptoms and code analysis
- Rank by likelihood
- For each hypothesis, identify what runtime data would prove or disprove it

### 3. Instrument
- Start debug server and add instrumentation at hypothesis-relevant code paths
- Use `#region agent log` / `#endregion` markers for all instrumentation
- Reference `diagnose/references/runtime-debugging.md` for patterns and log schema
- Tag each log point with the relevant `hypothesisId`
- **For browser/UI bugs**: combine with browser skill to reproduce and inspect

### 4. Reproduce
- Ask user to trigger the bug

**GATE**: User confirms reproduction.

### 5. Gather & Analyze
- Read debug logs from `.claude/tmp/diagnose-{sessionId}.log`
- Correlate log entries with hypotheses
- Eliminate or confirm causes based on evidence

### 6. Iterate (if needed)
- Refine hypotheses based on new evidence
- Add more instrumentation at narrowed-down code paths
- Ask user to reproduce again
- Max 3 rounds before escalating to user with findings so far

### 7. Report

Output structured diagnosis:

```
## Diagnosis: [Issue Title]

### Symptoms
- [What was observed]

### Evidence
- [Log finding] — `file:line` — hypothesis X
- ...

### Root Cause
[Confirmed or most likely cause with evidence]

### Hypotheses Tested
| # | Hypothesis | Result | Evidence |
|---|-----------|--------|----------|
| A | ... | Confirmed/Eliminated | Log entry X shows... |

### Recommended Next Steps
- [What to do — e.g., run `/fix` with this diagnosis]

### Active Instrumentation
- [List of files with `#region agent log` blocks still in place]
```

## Gotchas

- **Jumping to conclusions**: Form hypotheses, then TEST them. Don't guess and fix.
- **Fixing instead of diagnosing**: Your job is to find the root cause. Don't apply fixes — that's /fix's job.
- **Forgetting to clean up instrumentation**: Note every log/probe you add. Clean up after diagnosis.
- **Single-hypothesis tunnel vision**: Consider at least 2-3 hypotheses before committing to one.
- **Ignoring the reproduction environment**: The bug might be environment-specific. Note what you're testing on.

## Constraints

- NO fixing — investigation and diagnosis only
- Evidence over assumptions — if code looks right, instrument and verify at runtime
- Keep instrumentation in place after diagnosis (persists for `/fix` verification)
- Do NOT clean up `#region agent log` blocks — `/fix` will handle cleanup after verification

## Bug

<bug>$ARGUMENTS</bug>
