# Turborepo Configuration

## turbo.json Basics

Located at repository root. Supports `.json` or `.jsonc`.

**Minimal Configuration:**
```json
{
  "$schema": "https://turborepo.com/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}
```

**Full Configuration:**
```json
{
  "$schema": "https://turborepo.com/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "globalEnv": ["CI", "NODE_ENV"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "env": ["MY_API_URL"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "dependsOn": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

## Task Configuration

### dependsOn

Defines task execution order.

| Type | Syntax | Description |
|------|--------|-------------|
| Topological | `"^build"` | Run in dependencies first |
| Same-package | `"lint"` | Run another task first |
| Arbitrary | `"web#build"` | Run specific package's task |

**Examples:**
```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]        // Build deps first
    },
    "test": {
      "dependsOn": ["build"]         // Build same package first
    },
    "deploy": {
      "dependsOn": ["web#build"]     // Specific package task first
    },
    "lint": {
      "dependsOn": []                // No dependencies
    }
  }
}
```

### outputs

Files/directories to cache. **Required for caching.**

```json
{
  "build": {
    "outputs": [
      "dist/**",
      ".next/**",
      "!.next/cache/**"   // Exclude patterns
    ]
  }
}
```

### inputs

Override default inputs for cache hash calculation.

```json
{
  "build": {
    "inputs": [
      "$TURBO_DEFAULT$",  // Standard inputs
      "!README.md",       // Exclude files
      "!**/*.test.ts"
    ]
  }
}
```

### env

Environment variables affecting task hash.

```json
{
  "build": {
    "env": [
      "MY_API_URL",
      "MY_API_*"          // Wildcards supported
    ]
  }
}
```

### passThroughEnv

Environment variables passed at runtime (not affecting hash).

```json
{
  "dev": {
    "passThroughEnv": ["AWS_SECRET_KEY"]
  }
}
```

### cache

Disable caching for a task.

```json
{
  "dev": {
    "cache": false
  }
}
```

### persistent

Mark long-running tasks (dev servers).

```json
{
  "dev": {
    "persistent": true,
    "cache": false
  }
}
```

## Global Configuration

```json
{
  "globalDependencies": [
    ".env",
    "**/.env.*local",
    "tsconfig.json"
  ],
  "globalEnv": [
    "CI",
    "NODE_ENV",
    "VERCEL_ENV"
  ],
  "globalPassThroughEnv": [
    "AWS_SECRET_KEY"
  ]
}
```

## Package Configurations

Individual packages can extend root config.

**packages/ui/turbo.json:**
```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": ["dist/**", "types/**"]
    }
  }
}
```

## Running Tasks

**Basic:**
```bash
turbo run build
turbo build              # Shorthand
turbo build lint test    # Multiple tasks
```

**Filtering:**
```bash
turbo build --filter=web
turbo build --filter=web...       # With dependents
turbo build --filter=...web       # With dependencies
turbo build --filter="[main]"     # Changed since main
```

**Package-Specific:**
```bash
turbo run web#build
```

**Options:**
```bash
turbo build --dry-run            # Preview without executing
turbo build --summarize          # Generate run summary
turbo build --continue           # Continue on errors
turbo build --concurrency=4      # Limit parallel tasks
turbo build --force              # Bypass cache
```

## Common Patterns

**Next.js App:**
```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_*"]
    }
  }
}
```

**TypeScript Library:**
```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", "*.d.ts"]
    },
    "typecheck": {
      "dependsOn": ["^typecheck"]
    }
  }
}
```

**Test with Coverage:**
```json
{
  "tasks": {
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "env": ["CI"]
    }
  }
}
```

## Resources

- [Turborepo Configuration](https://turborepo.com/docs/reference/configuration)
- [Configuring Tasks](https://turborepo.com/docs/crafting-your-repository/configuring-tasks)
- [Running Tasks](https://turborepo.com/docs/crafting-your-repository/running-tasks)
