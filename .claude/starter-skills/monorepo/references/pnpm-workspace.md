# pnpm Workspaces

## pnpm-workspace.yaml

Required at repository root to define workspace packages.

**Basic Configuration:**
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
  - 'tools/*'
```

**With Catalogs (pnpm 9.5+):**
```yaml
packages:
  - 'apps/*'
  - 'packages/*'

catalog:
  react: ^18.2.0
  react-dom: ^18.2.0
  typescript: ^5.3.0

catalogs:
  react17:
    react: ^17.0.2
```

**Exclusions:**
```yaml
packages:
  - 'packages/*'
  - '!packages/legacy'  # Exclude specific package
```

## Workspace Protocol

Ensures dependencies resolve from local workspace only.

**Syntax Variants:**
```json
{
  "dependencies": {
    "foo": "workspace:*",      // Always latest local version
    "bar": "workspace:~",      // Patch-level semver on publish
    "qar": "workspace:^",      // Minor-level semver on publish
    "zoo": "workspace:^1.5.0", // Specific range
    "alias": "workspace:foo@*" // Aliased package reference
  }
}
```

**Adding Workspace Dependencies:**
```bash
# Explicit workspace protocol
pnpm add @awesome/utils@workspace:* --filter @awesome/api-client

# Shorthand (defaults to workspace:^)
pnpm add @awesome/utils --workspace --filter @awesome/api-client
```

**Publishing Behavior:**
- `workspace:*` becomes exact version (e.g., `1.2.3`)
- `workspace:^` becomes `^1.2.3`
- `workspace:~` becomes `~1.2.3`

**Best Practice:** Prefer `workspace:*` for internal links during development.

## Filtering

Run commands on specific package subsets.

**By Package Name:**
```bash
pnpm --filter <package_name> <command>
pnpm -F <package_name> <command>
pnpm --filter "@scope/*" build
```

**By Directory:**
```bash
pnpm --filter "./apps/**" test
pnpm --filter {apps/*} dev
```

**Dependency Selection:**
```bash
pnpm --filter <pkg>... build    # Package AND its dependencies
pnpm --filter ...<pkg> test     # Package AND its dependents
pnpm --filter ...^<pkg> lint    # Only dependents (exclude pkg)
```

**Multiple Filters:**
```bash
pnpm --filter ...foo --filter bar --filter baz... test
```

**Exclusions:**
```bash
pnpm --filter "./packages/*" --filter "!./packages/legacy" build
```

## Recursive Commands

```bash
pnpm -r build                              # All workspace packages
pnpm -r --include-workspace-root lint      # Include root project
pnpm -r --parallel dev                     # Parallel (ignore topo order)
pnpm -r --workspace-concurrency=4 build    # Control concurrency
pnpm -r --stream build                     # Stream output with prefix
pnpm -r --parallel --aggregate-output build # Aggregate (good for CI)
```

## Catalog Protocol (pnpm 9.5+)

Centralize dependency versions across packages.

**In pnpm-workspace.yaml:**
```yaml
catalog:
  react: ^18.2.0
  typescript: ^5.3.0
```

**In package.json:**
```json
{
  "dependencies": {
    "react": "catalog:",
    "typescript": "catalog:"
  }
}
```

**Named Catalogs:**
```yaml
catalogs:
  frontend:
    react: ^18.2.0
  backend:
    express: ^4.18.0
```

```json
{
  "dependencies": {
    "react": "catalog:frontend"
  }
}
```

## Common Commands

```bash
# Install all workspace dependencies
pnpm install

# Add dev dependency to root
pnpm add -D -w typescript

# Add dependency to specific package
pnpm add lodash --filter @acme/utils

# Run script in all packages
pnpm -r run build

# Update internal dependencies
pnpm update --recursive --latest
```

## Resources

- [pnpm Workspaces](https://pnpm.io/workspaces)
- [pnpm Filtering](https://pnpm.io/filtering)
- [pnpm Catalogs](https://pnpm.io/catalogs)
