# Starter Skills

Common domain starter skill kits for quick reuse during project priming. These are pre-built templates for frequently needed domains — if a starter skill doesn't exist for your stack, Claude Prime will create one tailored to your project during priming.

## How they work

During priming, `optimus-prime` copies relevant starter-skills into the target project's `.claude/skills/` directory, where they become active skills tailored to that project. For domains not covered by starter skills, Claude Prime generates new skills from scratch based on your project's stack and patterns.

This folder is deleted from target projects after priming. Final skills live in `.claude/skills/`.
