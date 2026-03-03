# Turborepo Caching

## How Caching Works

1. Turborepo calculates a fingerprint (hash) based on:
   - Source file contents
   - Dependencies (internal + external)
   - Environment variables
   - turbo.json configuration

2. Checks local cache first, then remote cache
3. On hit: restores outputs instantly
4. On miss: executes task, stores outputs

## Configuring Outputs

**Required for caching to work.**

```json
{
  "tasks": {
    "build": {
      "outputs": [
        "dist/**",
        ".next/**",
        "!.next/cache/**"    // Exclude Next.js internal cache
      ]
    }
  }
}
```

**Empty outputs = logs-only caching:**
```json
{
  "tasks": {
    "lint": {
      "outputs": []          // Only cache success/failure + logs
    }
  }
}
```

## Configuring Inputs

Override what affects the cache hash.

```json
{
  "tasks": {
    "build": {
      "inputs": [
        "$TURBO_DEFAULT$",   // Include standard inputs
        "!README.md",        // Exclude docs
        "!**/*.test.ts",     // Exclude tests
        "!**/__mocks__/**"   // Exclude mocks
      ]
    }
  }
}
```

**Default inputs (`$TURBO_DEFAULT$`):**
- All files tracked by git
- Excluding files in `.gitignore`

## Environment Variables

**Affecting cache hash:**
```json
{
  "globalEnv": ["CI", "NODE_ENV"],
  "tasks": {
    "build": {
      "env": ["API_URL", "FEATURE_*"]
    }
  }
}
```

**Framework Inference:**
Turborepo automatically includes:
- `NEXT_PUBLIC_*` for Next.js
- `VITE_*` for Vite
- `REACT_APP_*` for Create React App

**Runtime-only (not affecting hash):**
```json
{
  "tasks": {
    "deploy": {
      "passThroughEnv": ["AWS_SECRET_KEY"]
    }
  }
}
```

## Local Cache

Located at `node_modules/.cache/turbo` by default.

**Clear local cache:**
```bash
turbo run build --force
```

**Custom cache location:**
```bash
TURBO_CACHE_DIR=/path/to/cache turbo run build
```

## Remote Caching

### Vercel Remote Cache (Recommended)

Free for all Vercel plans.

**Setup:**
```bash
# Authenticate
npx turbo login

# Link project
npx turbo link
```

**CI/CD Environment Variables:**
```bash
TURBO_TOKEN=<your-token>
TURBO_TEAM=<your-team>
```

### Self-Hosted Remote Cache

Using [turborepo-remote-cache](https://github.com/ducktors/turborepo-remote-cache).

**Manual login:**
```bash
npx turbo login --manual --api-url=https://your-cache.example.com
```

**Config file (.turbo/config.json):**
```json
{
  "teamId": "team_xxx",
  "apiUrl": "https://your-cache.example.com"
}
```

**Storage providers:**
- AWS S3
- Google Cloud Storage
- Azure Blob Storage
- Local filesystem

### Artifact Signing

For security-sensitive environments.

**turbo.json:**
```json
{
  "remoteCache": {
    "signature": true
  }
}
```

**Environment:**
```bash
TURBO_REMOTE_CACHE_SIGNATURE_KEY=your-secret-key
```

## Debugging Cache

### Dry Run
```bash
turbo run build --dry-run
```

Shows what would run without executing.

### Task Summary
```bash
turbo run build --summarize
```

Generates `.turbo/runs/<run-id>/summary.json` with:
- All inputs affecting hash
- Environment variables
- Outputs
- Cache status

### Comparing Hashes

When cache misses unexpectedly:
1. Run `--summarize` on both environments
2. Compare `summary.json` files
3. Look for differences in inputs/env

### Common Cache Miss Causes

| Cause | Solution |
|-------|----------|
| Different env vars | Add to `env` or `globalEnv` |
| Unstable timestamps | Exclude from inputs |
| Different Node versions | Pin Node version |
| OS differences | Check file encoding |

## When NOT to Cache

- Tasks faster than network round-trip to remote
- Tasks with enormous outputs (>100MB)
- Dev servers (`"cache": false`)
- Tasks with inherently unstable outputs

## CI/CD Best Practices

**GitHub Actions:**
```yaml
- name: Setup Turbo Cache
  uses: actions/cache@v3
  with:
    path: node_modules/.cache/turbo
    key: turbo-${{ github.sha }}
    restore-keys: |
      turbo-

- name: Build
  run: pnpm turbo build
  env:
    TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
    TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

**Cache warming:**
```bash
# Pull remote cache before build
turbo run build --remote-only
```

## Resources

- [Caching](https://turborepo.com/docs/crafting-your-repository/caching)
- [Remote Caching](https://turborepo.com/docs/core-concepts/remote-caching)
- [turborepo-remote-cache](https://github.com/ducktors/turborepo-remote-cache)
