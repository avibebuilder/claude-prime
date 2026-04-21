#!/usr/bin/env python3
"""Lightweight task tracker for AI agent workflows. Stores named task files in .tasks/ at project root."""

import argparse
import json
import os
import sys
import time

TASKS_DIR = os.path.join(os.getcwd(), ".tasks")
REVIEW_STATUSES = {"pending", "approved", "changes_requested"}
TASKS_FILE = None

MIN_TITLE_LEN = 12
MIN_DESC_LEN = 40
MIN_EXPECTED_LEN = 20

RUBRIC_HINT = """
Writing a good task — three fields, three jobs:
  title     Imperative verb + concrete artifact.  e.g. "Add packages/db scaffolding"
  desc      Body: why, scope (in/out), files, constraints.  Enough for a cold pickup.
  expected  Observable check: command, file, or behavior.  NOT "matches the plan".

See .claude/scripts/tasks-authoring.md for the full rubric.
"""


def now():
    return time.strftime("%Y%m%d%H%M%S")


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def validate_length(value, min_len, field):
    trimmed = value.strip() if value else ""
    if len(trimmed) < min_len:
        fail(f"{field} too short ({len(trimmed)} chars, need >= {min_len}).\n{RUBRIC_HINT}")
    return trimmed


def normalize_task_file_name(name):
    if not name:
        name = now()
    name = name.strip()
    if not name:
        fail("Task file name cannot be empty")
    if name in {".", ".."}:
        fail("Task file name is invalid")
    if os.path.basename(name) != name or any(sep in name for sep in {"/", "\\"}):
        fail("Task file name must be a simple name under .tasks/")
    if not name.endswith(".json"):
        name += ".json"
    return name


def load():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE) as f:
        return json.load(f)


def save(tasks):
    os.makedirs(TASKS_DIR, exist_ok=True)
    tmp = TASKS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(tasks, f, indent=2)
    os.replace(tmp, TASKS_FILE)


def find_task(tasks, tid):
    for task in tasks:
        if task["id"] == tid:
            return task
    return None


def require_task(tasks, tid):
    task = find_task(tasks, tid)
    if task is None:
        fail(f"Task #{tid} not found")
    return task


def set_optional_field(task, key, value):
    if value in {None, "-", "none"}:
        task.pop(key, None)
        return
    task[key] = value


def parse_blocked_by(raw, tasks, *, current_task_id=None):
    if raw is None:
        return None
    if not raw.strip():
        return []
    try:
        blocked_by = [int(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError:
        fail("--blocked-by must be a comma-separated list of task ids")
    existing_ids = {task["id"] for task in tasks}
    for blocked_id in blocked_by:
        if blocked_id not in existing_ids:
            fail(f"Task #{blocked_id} not found (referenced in --blocked-by)")
        if current_task_id is not None and blocked_id == current_task_id:
            fail("A task cannot be blocked by itself")
    return blocked_by


def review_status(task):
    return task.get("review", {}).get("status", "pending")


def review_summary(task):
    review = task.get("review")
    if not review:
        return "pending"
    summary = review["status"]
    if review.get("by"):
        summary += f" by {review['by']}"
    return summary


def is_blocked(task, tasks):
    blocked_by = task.get("blocked_by", [])
    if not blocked_by:
        return False
    not_done_ids = {entry["id"] for entry in tasks if entry["status"] != "done"}
    return any(blocked_id in not_done_ids for blocked_id in blocked_by)


def next_action(task):
    if task["status"] == "pending":
        return "implement"
    if not task.get("evidence"):
        return "verify"
    if review_status(task) != "approved":
        return "review"
    return "done"


def format_task(task, tasks):
    mark = "x" if task["status"] == "done" else "~" if task["status"] == "in_progress" else " "
    parts = [f"  [{mark}] #{task['id']}: {task['title']}"]
    if "expected" in task:
        parts.append(f"expect: {task['expected']}")
    if "owner" in task:
        parts.append(f"owner: {task['owner']}")
    if "role" in task:
        parts.append(f"role: {task['role']}")
    if "reviewer" in task:
        parts.append(f"reviewer: {task['reviewer']}")
    if "evidence" in task:
        parts.append(f"evidence: {task['evidence']}")
    if "blocked_by" in task:
        parts.append(f"blocked by: {', '.join(f'#{blocked_id}' for blocked_id in task['blocked_by'])}")
    parts.append(f"review: {review_summary(task)}")
    if task["status"] != "done" and is_blocked(task, tasks):
        parts.append("BLOCKED")
    else:
        parts.append(f"next: {next_action(task)}")
    return " | ".join(parts)


def cmd_add(args):
    tasks = load()
    title = validate_length(args.title, MIN_TITLE_LEN, "title")
    desc = validate_length(args.desc, MIN_DESC_LEN, "desc")
    expected = validate_length(args.expected, MIN_EXPECTED_LEN, "expected")
    blocked_by = parse_blocked_by(args.blocked_by, tasks)
    task_id = max((task["id"] for task in tasks), default=0) + 1
    task = {
        "id": task_id,
        "title": title,
        "desc": desc,
        "expected": expected,
        "status": "pending",
        "created": now(),
    }
    if blocked_by:
        task["blocked_by"] = blocked_by
    if args.owner:
        task["owner"] = args.owner
    if args.role:
        task["role"] = args.role
    if args.reviewer:
        task["reviewer"] = args.reviewer
    tasks.append(task)
    save(tasks)
    print(format_task(task, tasks))
    print(f"saved to: {TASKS_FILE}")


def cmd_update(args):
    tasks = load()
    task = require_task(tasks, args.id)
    updated = False
    if args.title is not None:
        task["title"] = validate_length(args.title, MIN_TITLE_LEN, "title")
        updated = True
    if args.desc is not None:
        task["desc"] = validate_length(args.desc, MIN_DESC_LEN, "desc")
        updated = True
    if args.expected is not None:
        task["expected"] = validate_length(args.expected, MIN_EXPECTED_LEN, "expected")
        updated = True
    if args.owner is not None:
        set_optional_field(task, "owner", args.owner)
        updated = True
    if args.role is not None:
        set_optional_field(task, "role", args.role)
        updated = True
    if args.reviewer is not None:
        set_optional_field(task, "reviewer", args.reviewer)
        updated = True
    if args.blocked_by is not None:
        blocked_by = parse_blocked_by(args.blocked_by, tasks, current_task_id=args.id)
        if blocked_by:
            task["blocked_by"] = blocked_by
        else:
            task.pop("blocked_by", None)
        updated = True
    if not updated:
        fail("Nothing to update. Provide one of: --title, --desc, --expected, --blocked-by, --owner, --role, --reviewer")
    save(tasks)
    print(f"Updated #{args.id}")


def cmd_assign(args):
    tasks = load()
    task = require_task(tasks, args.id)
    if task["status"] == "done":
        fail(f"Task #{args.id} is already done")
    task["owner"] = args.owner
    if args.role:
        task["role"] = args.role
    if task["status"] == "pending":
        task["status"] = "in_progress"
    task["updated"] = now()
    save(tasks)
    print(f"Assigned #{args.id} to {task['owner']}")


def cmd_verify(args):
    tasks = load()
    task = require_task(tasks, args.id)
    if task["status"] == "done":
        fail(f"Task #{args.id} is already done")
    task["evidence"] = args.evidence
    task["verified_at"] = now()
    if task["status"] == "pending":
        task["status"] = "in_progress"
    save(tasks)
    print(f"Verified #{args.id}")


def cmd_review(args):
    tasks = load()
    task = require_task(tasks, args.id)
    review = {
        "status": args.decision,
        "at": now(),
    }
    reviewer = args.by or task.get("reviewer")
    if reviewer:
        review["by"] = reviewer
        task.setdefault("reviewer", reviewer)
    if args.note:
        review["note"] = args.note
    task["review"] = review
    if task["status"] == "pending":
        task["status"] = "in_progress"
    save(tasks)
    print(f"Reviewed #{args.id}: {args.decision}")


def cmd_done(args):
    tasks = load()
    task = require_task(tasks, args.id)
    if is_blocked(task, tasks):
        fail(f"Task #{args.id} is still blocked")
    if not task.get("evidence"):
        fail(f"Task #{args.id} is missing verification evidence. Run: tasks.py --task-file <name> verify {args.id} \"...\"")
    if review_status(task) != "approved":
        fail(f"Task #{args.id} is missing approved review. Run: tasks.py --task-file <name> review {args.id} approved")
    task["status"] = "done"
    task["completed"] = now()
    save(tasks)
    print(f"Completed #{args.id}")


def cmd_list(args):
    tasks = load()
    if args.json:
        print(json.dumps(tasks, indent=2))
        return
    if not tasks:
        print("No tasks")
        return
    for task in tasks:
        print(format_task(task, tasks))


def cmd_show(args):
    tasks = load()
    task = require_task(tasks, args.id)
    if args.json:
        print(json.dumps(task, indent=2))
        return
    print(f"#{task['id']}: {task['title']}")
    print(f"status: {task['status']}")
    if "desc" in task:
        print(f"desc: {task['desc']}")
    if "expected" in task:
        print(f"expected: {task['expected']}")
    if "owner" in task:
        print(f"owner: {task['owner']}")
    if "role" in task:
        print(f"role: {task['role']}")
    if "reviewer" in task:
        print(f"reviewer: {task['reviewer']}")
    if "blocked_by" in task:
        print(f"blocked by: {', '.join(f'#{blocked_id}' for blocked_id in task['blocked_by'])}")
    if "evidence" in task:
        print(f"evidence: {task['evidence']}")
    print(f"review: {review_summary(task)}")
    if "review" in task and task["review"].get("note"):
        print(f"review note: {task['review']['note']}")
    print(f"next: {'blocked' if is_blocked(task, tasks) else next_action(task)}")


def cmd_next(args):
    tasks = load()
    ready = [task for task in tasks if task["status"] != "done" and not is_blocked(task, tasks)]
    if not ready:
        print("No unblocked unfinished tasks")
        return
    for task in ready:
        print(format_task(task, tasks))


def cmd_clear(args):
    tasks = [task for task in load() if task["status"] != "done"]
    save(tasks)
    print("Cleared completed tasks")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Lightweight task tracker for AI agent workflows.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Writing a good task
-------------------
Three fields, three jobs:
  title     Imperative verb + concrete artifact.  >=12 chars.
  desc      Body: why, scope (in/out), files, constraints.  >=40 chars.
  expected  Observable check: command, file, or behavior.  >=20 chars.

Good:
  title     "Add packages/db scaffolding"
  desc      "Create packages/db with workspace deps on env/contracts. Out of scope:
             schema and migrations (task #7). Must import env from @workspace/env,
             never process.env."
  expected  "pnpm -F db typecheck passes; packages/db/src/index.ts exports db"

Bad:
  title     "Scaffold shared packages"       <- umbrella, no artifact
  desc      "scaffold the packages"          <- no context for cold pickup
  expected  "minimal valid manifests"        <- unverifiable

See .claude/scripts/tasks-authoring.md for the full rubric.

Examples:
  # Add a task (title, desc, expected all required)
  %(prog)s add "<title>" "<desc>" "<expected>"

  # Add a task blocked by others
  %(prog)s add "<title>" "<desc>" "<expected>" --blocked-by 1,2

  # Update a field
  %(prog)s update 1 --desc "<new body>"

  # Verify completion and approve
  %(prog)s verify 1 "All tests pass, manually verified on staging"
  %(prog)s review 1 approved --by bob

  # Mark done (requires evidence + approved review)
  %(prog)s done 1

  # Use a named task file
  %(prog)s --task-file sprint-42 list
        """,
    )
    parser.add_argument(
        "--task-file",
        default=None,
        metavar="NAME",
        help="task file name under .tasks/ (default: timestamp-based name)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    # add
    p_add = subparsers.add_parser(
        "add",
        help="create a new task",
        description="Create a new task. See the top-level --help for the authoring rubric.",
    )
    p_add.add_argument("title", help="imperative verb + concrete artifact (>=12 chars)")
    p_add.add_argument("desc", help="body: why, scope, files, constraints (>=40 chars)")
    p_add.add_argument("expected", help="observable check: command, file, or behavior (>=20 chars)")
    p_add.add_argument("--blocked-by", metavar="IDS", help="comma-separated task IDs this task is blocked by")
    p_add.add_argument("--owner", metavar="NAME", help="task owner")
    p_add.add_argument("--role", metavar="ROLE", help="owner role")
    p_add.add_argument("--reviewer", metavar="NAME", help="reviewer name")
    p_add.set_defaults(func=cmd_add)

    # update
    p_update = subparsers.add_parser("update", help="update fields on an existing task")
    p_update.add_argument("id", type=int, metavar="ID", help="task ID")
    p_update.add_argument("--title", metavar="TEXT", help="new title (>=12 chars)")
    p_update.add_argument("--desc", metavar="TEXT", help="new body (>=40 chars)")
    p_update.add_argument("--expected", metavar="TEXT", help="new expected outcome (>=20 chars)")
    p_update.add_argument("--blocked-by", metavar="IDS", help='comma-separated task IDs (empty string to clear)')
    p_update.add_argument("--owner", metavar="NAME", help='owner (use "none" to clear)')
    p_update.add_argument("--role", metavar="ROLE", help='role (use "none" to clear)')
    p_update.add_argument("--reviewer", metavar="NAME", help='reviewer (use "none" to clear)')
    p_update.set_defaults(func=cmd_update)

    # assign
    p_assign = subparsers.add_parser("assign", help="assign a task to an owner and mark it in-progress")
    p_assign.add_argument("id", type=int, metavar="ID", help="task ID")
    p_assign.add_argument("owner", help="owner name")
    p_assign.add_argument("--role", metavar="ROLE", help="owner role")
    p_assign.set_defaults(func=cmd_assign)

    # verify
    p_verify = subparsers.add_parser("verify", help="record verification evidence for a task")
    p_verify.add_argument("id", type=int, metavar="ID", help="task ID")
    p_verify.add_argument("evidence", help="verification evidence")
    p_verify.set_defaults(func=cmd_verify)

    # review
    p_review = subparsers.add_parser("review", help="record a review decision for a task")
    p_review.add_argument("id", type=int, metavar="ID", help="task ID")
    p_review.add_argument("decision", choices=["approved", "changes_requested"], help="review decision")
    p_review.add_argument("--by", metavar="NAME", help="reviewer name")
    p_review.add_argument("--note", metavar="TEXT", help="review note")
    p_review.set_defaults(func=cmd_review)

    # done
    p_done = subparsers.add_parser("done", help="mark a verified and approved task as done")
    p_done.add_argument("id", type=int, metavar="ID", help="task ID")
    p_done.set_defaults(func=cmd_done)

    # list
    p_list = subparsers.add_parser("list", help="list all tasks")
    p_list.add_argument("--json", action="store_true", help="output as JSON")
    p_list.set_defaults(func=cmd_list)

    # show
    p_show = subparsers.add_parser("show", help="show details for a single task")
    p_show.add_argument("id", type=int, metavar="ID", help="task ID")
    p_show.add_argument("--json", action="store_true", help="output as JSON")
    p_show.set_defaults(func=cmd_show)

    # next
    p_next = subparsers.add_parser("next", help="show unblocked, unfinished tasks ready for work")
    p_next.set_defaults(func=cmd_next)

    # clear
    p_clear = subparsers.add_parser("clear", help="remove completed tasks from the task file")
    p_clear.set_defaults(func=cmd_clear)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    TASKS_FILE = os.path.join(TASKS_DIR, normalize_task_file_name(args.task_file))

    args.func(args)
