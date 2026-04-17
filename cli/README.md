# claude-prime

**Open source Claude Code CLI for developers who want repeatable AI coding workflows without the setup mess.**

Claude Prime installs the missing layer around Claude Code: reusable skills, slash-command workflows, rules, hooks, project context, and interactive setup helpers. It is designed for the real pain points teams hit with AI coding assistants: too much manual setup, repeated prompts, inconsistent output, and poor onboarding across repositories.

## Install

```bash
npx claude-prime install
```

Install a specific version:

```bash
npx claude-prime install --version 1.2.0
```

## Commands

| Command | Description |
|---------|-------------|
| `claude-prime install` | Download Claude Prime, install it into the current directory, and run initialization |
| `claude-prime init` | Configure or reconfigure an existing Claude Prime installation |

## What the CLI does

1. Downloads the latest Claude Prime release
2. Extracts the `.claude/` toolkit into your repository
3. Runs interactive setup for `.gitignore`, environment files, and optional MCP configuration
4. Lets you open Claude Code and run `/optimus-prime` to tailor the toolkit to your stack

## Why developers install it

- One-command Claude Code setup
- Better context engineering for real repositories
- Reusable workflows instead of repeated prompts
- More consistent AI coding output across teams
- Open source customization for your own standards

## Example workflows

```bash
# Jump straight to implementation
/cook Add user authentication with Google OAuth

# Debug and fix issues
/fix The checkout flow returns 500 when cart is empty

# Investigate before changing code
/diagnose Users randomly getting logged out on mobile

# Plan before implementing
/give-plan Migrate from REST to GraphQL

# Review your changes
/review-code
```

## Requirements

- Node.js >= 18

## Alternative install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/avibebuilder/claude-prime/main/install.sh)
```

## Links

- [GitHub](https://github.com/avibebuilder/claude-prime)
- [Full README and language versions](https://github.com/avibebuilder/claude-prime#readme)

## License

[MIT](https://github.com/avibebuilder/claude-prime/blob/main/LICENSE)
