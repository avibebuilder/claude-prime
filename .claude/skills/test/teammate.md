# Tester handoff (`/test` in an isolated teammate)

When a caller just authored the code being verified, spawn a **tester** — an isolated teammate that runs `/test` on the caller's behalf.

## Why isolation matters

The agent that just authored the code carries the narrative of *what it was trying to do*. That narrative biases judgment. A teammate with zero prior context evaluates the code on its merits, not on the intent behind it.

## Primary mechanism: TeamCreate

1. Create a team with `TeamCreate` named for the unit of work (e.g., `verify-auth-fix`). Use `isolation: "worktree"` when verification will execute code or mutate shared state; skip the worktree for read-only static checks.

## Fallback: Agent subagent

If team infrastructure is unavailable, spawn directly via `Agent` with `subagent_type: "general-purpose"`, `skills: test` and the same `isolation` setting. You lose team persistence but keep the context isolation.

## The tester MUST use the `/test` skill

The whole point is that the teammate applies `/test`'s process and report format. Make this non-negotiable in the prompt:

> Read `.claude/skills/test/SKILL.md` first and follow it exactly — it is your working instructions. If the `/test` skill is available as a Skill tool in your harness, invoke it. Do not improvise.

A teammate that skips the skill defeats the purpose.

## Collaborate, don't just delegate

The teammate is a collaborator, not a one-shot worker. Encourage it to:

- Ask when the claim, scope, or target is ambiguous instead of guessing
- Flag assumptions the prompt forced it to make
- Push back on framing, payload gaps, or missing context
- Surface findings mid-task when waiting to the end would waste effort

On the team path, use `SendMessage` for back-and-forth. On the subagent path, the teammate has only its return message — it surfaces questions and pushback there. Either way, treat teammate questions as the collaboration working, not a sign that it's stuck.

## What the prompt must include

Pass *facts*, not justifications. The teammate forms its own view.

- **Claim** — what must be true, copied from acceptance criteria or the bug report
- **Changed files** — explicit paths (a blind teammate exploring the full tree wastes tokens)
- **Regression surface** — nearby behavior that could plausibly break
- **Infra constraints** — what's already running vs. what the teammate must not start itself

## What to leave out

- Your design justifications — they anchor the teammate's judgment
- Your confidence in the work — the teammate forms its own
- Pre-emptive defense of anything the teammate might flag

If context genuinely matters, the code itself should carry it (comment, docstring, commit message). If it doesn't, that gap is itself a finding.

## What the teammate returns

A Verification Report per `/test`'s output format: Claim, Verdict, Evidence, Failures, Gaps, Suite Stats.

## Team lifecycle

- **Keep the teammate alive across rounds of the same work.** Message the existing teammate with the next round's input instead of re-spawning — accumulated context makes each round sharper.
- **New unit of work → new team.** When switching to a different feature or bug, shut the old team down via `SendMessage` with `{type: "shutdown_request"}` and create a fresh one. Stale context from prior work is worse than starting clean.
