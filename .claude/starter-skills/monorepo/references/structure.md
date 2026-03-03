# Monorepo Structure

## Recommended Directory Layout

```
my-monorepo/
├── apps/                     # Deployable applications
│   ├── web/                  # Frontend app
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── api/                  # Backend service
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── mobile/               # Mobile app
│       └── package.json
├── packages/                 # Shared libraries
│   ├── ui/                   # Component library
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── utils/                # Shared utilities
│   │   └── package.json
│   ├── config/               # Shared configuration
│   │   └── package.json
│   └── types/                # Shared TypeScript types
│       └── package.json
├── tools/                    # Build/dev tooling
│   ├── eslint-config/
│   │   └── package.json
│   └── tsconfig/
│       └── package.json
├── package.json              # Root package.json
├── pnpm-workspace.yaml       # Workspace config
├── pnpm-lock.yaml            # Single lockfile
└── turbo.json                # Turborepo config
```

## Package Naming

**Use namespace prefix:**
```json
{
  "name": "@acme/utils"
}
```

Benefits:
- Avoids npm registry conflicts
- Clear organizational ownership
- Easier filtering: `--filter "@acme/*"`

**Naming conventions:**
- `@org/app-*` for applications
- `@org/pkg-*` or `@org/lib-*` for libraries
- `@org/config-*` for configuration packages

## Root package.json

```json
{
  "name": "my-monorepo",
  "private": true,
  "packageManager": "pnpm@9.0.0",
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "typecheck": "turbo run typecheck",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "typescript": "^5.3.0"
  }
}
```

## pnpm-workspace.yaml

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
  - 'tools/*'

catalog:
  typescript: ^5.3.0
  eslint: ^9.0.0
  prettier: ^3.0.0
```

## TypeScript Configuration

### Root tsconfig.json (optional)

Only for IDE support; packages define their own configs.

```json
{
  "files": [],
  "references": [
    { "path": "apps/web" },
    { "path": "apps/api" },
    { "path": "packages/ui" },
    { "path": "packages/utils" }
  ]
}
```

### Shared Base Config (tools/tsconfig/base.json)

```json
{
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "bundler",
    "isolatedModules": true,
    "declaration": true,
    "declarationMap": true
  }
}
```

### Package tsconfig.json

```json
{
  "extends": "@acme/tsconfig/base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

## ESLint Configuration

### Shared Config Package (tools/eslint-config)

```javascript
// tools/eslint-config/index.js
module.exports = {
  extends: ['eslint:recommended'],
  rules: {
    // shared rules
  }
};
```

### Package Usage

```javascript
// apps/web/.eslintrc.js
module.exports = {
  extends: ['@acme/eslint-config'],
  // package-specific overrides
};
```

## Internal Package Dependencies

**packages/ui/package.json:**
```json
{
  "name": "@acme/ui",
  "version": "0.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "@acme/utils": "workspace:*"
  },
  "peerDependencies": {
    "react": "^18.0.0"
  }
}
```

**apps/web/package.json:**
```json
{
  "name": "@acme/web",
  "private": true,
  "dependencies": {
    "@acme/ui": "workspace:*",
    "@acme/utils": "workspace:*",
    "react": "^18.2.0"
  }
}
```

## Environment Variables

### Per-Environment Files

```
apps/web/
├── .env.local           # Local development (gitignored)
├── .env.development     # Development defaults
├── .env.production      # Production defaults
└── .env.example         # Template (committed)
```

### turbo.json Global Dependencies

```json
{
  "globalDependencies": [
    ".env",
    "**/.env.local",
    "**/.env.development",
    "**/.env.production"
  ]
}
```

## Common Patterns

### Just-In-Time Package Building

Apps consume source directly (no pre-build needed).

**packages/utils/package.json:**
```json
{
  "main": "./src/index.ts",
  "types": "./src/index.ts"
}
```

**apps/web/tsconfig.json:**
```json
{
  "compilerOptions": {
    "paths": {
      "@acme/utils": ["../../packages/utils/src"]
    }
  }
}
```

### Pre-Built Packages

Traditional approach; packages build to dist.

```json
{
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "scripts": {
    "build": "tsc"
  }
}
```

## Anti-Patterns

- **Cross-package `../` imports** - Always use proper dependencies
- **Duplicate dependencies** - Hoist shared deps to root
- **Missing `private: true`** on apps - Prevents accidental publish
- **No lockfile** - Causes non-deterministic builds
- **Individual lockfiles per package** - Should be single root lockfile

## Resources

- [Structuring a Repository | Turborepo](https://turborepo.com/docs/crafting-your-repository/structuring-a-repository)
- [Internal Packages | Turborepo](https://turborepo.com/docs/core-concepts/internal-packages)
