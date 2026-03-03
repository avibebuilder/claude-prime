# Skill Design Principles

## Core Philosophy: Skills ≠ Documentation

Skills = **active workflow knowledge** for development tasks
Documentation = **passive reference material**

| Skill Mindset | Documentation Mindset |
|---------------|----------------------|
| "ability to deploy" | "Cloudflare docs" |
| "how to design UI" | "Tailwind reference" |

Each skill teaches Claude *how to perform a task*, not *what a tool does*.

## Progressive Disclosure (3 Tiers)

| Tier | Content | When Loaded | Size |
|------|---------|-------------|------|
| 1 | Metadata (name + description) | Always | ~100 words |
| 2 | SKILL.md body | On activation | ~150 lines |
| 3 | references/workflows/scripts | On demand | Unlimited* |

*Scripts execute without loading into context.

**Metrics improvement:** 4.8x token efficiency, activation 500ms→<100ms, relevance 10%→90%

## Right-Altitude Prompting

Guidance should be concrete but not hardcoded.

**Too Low:** "Use Tailwind's blue-500" / "Set font-size to 16px"
**Too Vague:** "Make it look good" / "Use appropriate colors"
**Right Altitude:** "Use project's existing color system" / "Match surrounding components"

## Anti-Convergence Patterns

LLMs default to high-probability outputs. Counter this by:

1. **List what to avoid:** "Avoid Inter fonts—overused", "Skip purple gradients—AI cliché"
2. **Suggest uncommon alternatives:** "Consider X even though Y is more common"
3. **Include variety in examples:** Multiple valid approaches

## Cold-Start Testing

1. Clear context completely
2. Activate skill with trigger phrase
3. Count tokens loaded

**Targets:** Initial load <500 lines. If over: split into references.

## Success Metrics

| Metric | Poor | Good |
|--------|------|------|
| SKILL.md lines | >200 | <150 |
| Initial load tokens | >5000 | <1500 |
| Relevant info ratio | <50% | >90% |

## Workflow-Capability Organization

**Bad:** One skill per tool (`cloudflare/`, `docker/`, `gcloud/`)
**Good:** Skills by capability (`devops/` → deployment, infrastructure)

Organize by **what you're doing**, not **what tool you're using**.
