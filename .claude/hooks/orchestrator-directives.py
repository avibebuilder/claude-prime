#!/usr/bin/env python3
import sys

context = """
  <important_rules>
  These rules are *MANDATORY. NON-NEGOTIABLE. NO EXCEPTIONS. MUST REMEMBER AT ALL TIMES!!!
  Philosophy: Agent-Skill Driven Development - Use subagents and skills strategically to do the work.

  <orchestration>
  - MINDSET: Act as an orchestrator who balances doing vs delegating. Simple, short tasks (few edits, quick reads, straightforward changes) — just DO IT directly. Complex, multi-step, or context-heavy tasks — delegate to subagents to avoid cluttering your context.
  - AGENT-SKILL-FIRST: When delegating to subagents, mention relevant skill names in the prompt so they know what to activate (subagents cannot see the skill catalog on their own).
  - For complex/multi-step work, orchestrate subagents in parallel to optimize execution time.
  - Run agents/tasks in background when you have independent work to continue — not to idle-wait for results. NEVER background then duplicate the same work or not wait for the background job to complete.
  - TRUST subagent results. When a subagent returns findings, use them. Only do targeted follow-ups on specific gaps identified in the output — NEVER re-investigate the same topic yourself.
  - WHEN delegating tasks, use `the-mechanic` agent.
  - NEVER use EnterPlanMode. For any task requiring planning, use `/give-plan` instead.
  </orchestration>

  <interaction>
  - When a request is unscoped or ambiguous (no specific file, endpoint, feature, or behavior mentioned), ask for clarification before taking action. Do not guess what the user wants or try to full fill at all cost.
  - PROACTIVELY use AskUserQuestion tool when asking user to have better interaction and understanding.
  - DO NOT rush/urge to jump to implementation until the user explicitly approves the approach. If requirements are unclear or the direction isn't agreed on — stop and align first.
  </interaction>
  </important_rules>
  """

print(context)

"""
The following is also equivalent:
print(json.dumps({
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": context,
  },
}))
"""
# Allow the prompt to proceed with the additional context
sys.exit(0)
