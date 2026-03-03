# BiomeJS Configuration

Fast, unified linter and formatter replacing ESLint + Prettier.

## Why Biome

- **Speed**: 10-100x faster than ESLint/Prettier
- **Unified**: Single tool for formatting + linting + import sorting
- **Zero config**: Sensible defaults, minimal setup

## Configuration

### biome.json

```json
{
  "$schema": "https://biomejs.dev/schemas/2.0.5/schema.json",
  "root": true,

  "files": {
    "includes": [
      "**/*.ts",
      "**/*.tsx",
      "**/*.js",
      "**/*.jsx",
      "**/*.json",
      "**/*.css",
      "!!.claude",
      "!!plans"
    ]
  },

  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  },

  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100,
    "lineEnding": "lf"
  },

  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "a11y": {
        "useSemanticElements": "off",
        "useKeyWithClickEvents": "off"
      },
      "correctness": {
        "noUnusedImports": {
          "level": "error",
          "fix": "safe"
        }
      },
      "nursery": {
        "useSortedClasses": {
          "level": "warn",
          "fix": "safe",
          "options": {
            "functions": ["cn", "clsx", "cva", "tw"]
          }
        }
      }
    }
  },

  "assist": {
    "enabled": true,
    "actions": {
      "source": {
        "organizeImports": {
          "level": "on",
          "options": {
            "groups": [
              ":NODE:",
              ":PACKAGE:",
              ":BLANK_LINE:",
              ":ALIAS:",
              ":BLANK_LINE:",
              ":PATH:"
            ]
          }
        }
      }
    }
  },

  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "jsxQuoteStyle": "double",
      "trailingCommas": "all",
      "semicolons": "always",
      "arrowParentheses": "always"
    }
  },

  "json": {
    "parser": {
      "allowComments": true,
      "allowTrailingCommas": true
    }
  },

  "css": {
    "formatter": { "enabled": true }
  },

  "overrides": [
    {
      "includes": ["*.config.js", "*.config.ts"],
      "linter": {
        "rules": {
          "style": { "noDefaultExport": "off" }
        }
      }
    }
  ]
}
```

### VSCode Settings

`.vscode/settings.json`:

```json
{
  "editor.defaultFormatter": "biomejs.biome",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.addMissingImports": "always",
    "source.organizeImports.biome": "always",
    "source.fixAll.biome": "always"
  },
  "[javascript]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[json]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[jsonc]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "biome.enabled": true,
  "biome.requireConfiguration": true
}
```

## Key Features

### Tailwind Class Sorting

The `useSortedClasses` rule sorts Tailwind classes in:

- `className` and `class` attributes
- Utility functions: `cn()`, `clsx()`, `cva()`, tagged templates

Classes are sorted following Tailwind's recommended order (layout, flexbox, spacing, etc.).

> **Note:** The config uses `"fix": "safe"` to enable auto-fix on save. Default is `"unsafe"` which requires manual application.

### Import Ordering

Groups configured via `assist.actions.source.organizeImports`:

| Matcher        | Description                      |
| -------------- | -------------------------------- |
| `:NODE:`       | Node.js built-ins (`fs`, `path`) |
| `:PACKAGE:`    | npm packages                     |
| `:ALIAS:`      | Path aliases (`@/`, `~/`, `#`)   |
| `:PATH:`       | Relative imports (`./`, `../`)   |
| `:BLANK_LINE:` | Insert separator                 |

## Gotchas

| Issue                      | Reality                                         |
| -------------------------- | ----------------------------------------------- |
| `source.addMissingImports` | **VSCode/TypeScript feature**, not Biome        |
| Custom Tailwind config     | `useSortedClasses` ignores `tailwind.config.js` |
| Screen variants            | Not yet supported in class sorting              |
| Import organizing          | Use `biome check`, not `biome format`           |

## Advanced Setup

### Domains

Framework-specific rules auto-detected from `package.json`:

```json
"linter": {
  "domains": {
    "react": "recommended",
    "next": "recommended"
  }
}
```

Biome surfaces relevant rules (e.g., React Hooks, Next.js patterns) without manual configuration.

### Pre-commit Hooks

Native `--staged` support (v1.7+) eliminates need for lint-staged:

```bash
# .husky/pre-commit
npx biome check --staged --write
```

Setup: `npx husky init && echo 'npx biome check --staged --write' > .husky/pre-commit`

### CI/CD

```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: biomejs/setup-biome@v2
      - run: biome ci .
```

The `biome ci` command exits non-zero on any issue (no auto-fix).

## CLI Commands

```bash
# All-in-one (format + lint + organize imports)
biome check --write .

# CI mode (check without writing)
biome check .

# Format only
biome format --write .

# Lint only
biome lint --write .
```
