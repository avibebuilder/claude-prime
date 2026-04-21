# Writing good tasks for `tasks.py`

The tracker stores tasks as JSON. The tool enforces three required fields: `title`, `desc`, `expected`. Getting these right is the difference between tasks a cold-context agent can pick up and tasks that are useless without the conversation that created them.

## The cold-pickup test

Before you save a task, imagine a different agent opens this JSON file tomorrow with no other context. Can they:

1. Tell **what artifact** they're producing?
2. Know **what's in and out of scope**?
3. Run **a command or check** to prove it's done?

If any answer is no, the task isn't finished being written.

## The three fields

### `title` — imperative verb + concrete artifact

A scannable label. Names the action and the artifact.

- Good: `Add packages/db scaffolding`
- Good: `Expose clearNodeResults in FlowContext`
- Good: `Wire Clear-all button into FlowCanvas`
- Bad: `Scaffold shared packages` — umbrella, no artifact
- Bad: `Reset root workspace foundation` — vague verb, no artifact
- Bad: `Verify scaffold` — not an action, no target

Test: if you can substitute the title into "commit message: ..." and it reads sensibly, it's probably right.

### `desc` — body

The "ticket description." Minimum ~40 chars, but usually several lines. Must carry:

- **Why** this task exists (link to the broader intent)
- **Scope**: what's in, what's out (especially what belongs to *other* tasks)
- **Files / APIs / patterns** involved
- **Constraints** a reader could otherwise violate

Example:

> Create `packages/db` with workspace deps on `env` and `contracts`. Out of scope: schema definitions and migrations (task #7). Constraint: must import env from `@workspace/env`, never `process.env` directly. Follows the same layout as `packages/contracts`.

If the desc is a one-line restatement of the title, it's wrong. If it references an external plan without naming what's in it, it's wrong — a cold pickup can't read your plan.

### `expected` — observable check

How you prove it's done. Shape it as a command to run, a file to grep, or a behavior to trigger.

- Good: `pnpm -F db typecheck passes; packages/db/src/index.ts exports db; appears in pnpm list -r`
- Good: `FlowToolbar renders Clear-all button when nodeResults.size > 0; clicking resets nodeResults Map to empty`
- Bad: `Matches the plan` — unverifiable, external reference
- Bad: `Minimal valid manifests` — what counts as minimal?
- Bad: `Works correctly` — empty signal

If you can't imagine the command that would verify it, rewrite.

## Granularity: one atomically verifiable unit

A task should be finishable and verifiable as one thing. Signals you need to split:

- `expected` contains "and" across independent artifacts
- Different files could reasonably be tested or reviewed in isolation
- Partial progress leaves the task stuck in `in_progress` for obvious subparts

Signals you're splitting too thin:

- Adjacent tasks share the same `expected` check
- A task's only verification is "it imports cleanly" with no behavioral claim
- You'd never realistically stop between these tasks

Rule of thumb: if the tester would run one command to verify the task, it's probably the right size.

## Dependencies: `blocked_by`

Set `--blocked-by` whenever a task needs artifacts from an earlier task to be verifiable. `tasks.py next` uses this to surface genuinely ready work. Leaving it blank when a dependency exists silently breaks that signal.

Examples:

- Task 4 "Verify scaffold" needs tasks 2 and 3 done first → `--blocked-by 2,3`
- Task "Add auth middleware" needs task "Add session store" first → yes, set it
- Two unrelated bug fixes in different packages → no

## Anti-patterns to catch in review

- **Section-title desc**: `Reset root workspace foundation` → what artifact?
- **Bundled task**: one task covering 5 packages → split per package
- **Plan-reference-only expected**: `Matches the bootstrap plan` → inline the check
- **Evidence-shaped expected**: `tsc passes, biome passes` written before work starts → fine if that really is the criterion, suspicious if it's just boilerplate
- **Missing blocked_by**: multiple pending tasks with obvious order dependency → always link them
- **Identical timestamps across 6 tasks**: upfront dump with zero iteration → usually paired with coarse granularity; re-examine

## When no plan exists

If you're authoring tasks without a preceding plan doc, each task's `desc` must stand fully alone — there's no external source of truth to point at. This is the hardest case and where most vagueness creeps in. Write more, not less.

## When a plan exists

A `desc` can reference a plan section (`See docs/bootstrap.md#shared-packages`) but must also include anything a reader would need that isn't in that section — constraints local to this task, adjustments, scope trims. The plan is the source of truth for design; the task is the source of truth for *this unit of execution*.
