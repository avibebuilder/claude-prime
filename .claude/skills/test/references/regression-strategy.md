# Regression Strategy

When to go beyond targeted tests and run broader verification. The core question: **could this change break something outside its immediate scope?**

## Blast Radius Assessment

Not every change needs regression testing. A CSS change to a single component has near-zero blast radius. A change to a shared utility used by 40 files has enormous blast radius.

### High Blast Radius (run broader regression)

- **Shared utilities / helpers** — changes to functions used across many modules
- **Core types / interfaces** — modifying a type that many components depend on
- **Configuration changes** — env vars, build config, routing tables, middleware ordering
- **Database schema** — migrations that alter existing columns or constraints
- **Authentication / authorization** — any change to auth flow affects every protected resource
- **Package upgrades** — especially major version bumps of core dependencies
- **Build system changes** — webpack/vite config, babel plugins, PostCSS

### Low Blast Radius (targeted tests sufficient)

- **New files** — adding a new component, endpoint, or utility that nothing depends on yet
- **Leaf component changes** — modifying a component that no other component imports
- **Test file changes** — changes isolated to test files
- **Documentation / comments** — no runtime effect
- **Scoped CSS** — styles that can't leak (CSS modules, scoped styles, Tailwind classes)

### How to assess blast radius

```bash
# 1. What files changed?
git diff --name-only

# 2. For each changed file, who imports it?
# In Claude Code, prefer the Grep tool over raw grep/rg.
# Conceptually:
#   Grep pattern="import.*from.*changed-module" glob="*.{ts,tsx}" output_mode="files_with_matches"

# 3. For shared changes, how many dependents?
# If > 5 files depend on what changed, regression is warranted
```

## Regression Test Selection

Once you've determined regression testing is needed, be strategic about what to run:

### Concentric rings approach

1. **Ring 1: Direct dependents** — files that import the changed module
2. **Ring 2: Feature-level** — the full test suite for the feature area
3. **Ring 3: Full suite** — everything

Start from Ring 1. Only expand to Ring 2 if Ring 1 reveals issues or the change is particularly risky. Ring 3 is for high-risk changes (auth, shared types, core config) or when you need maximum confidence before a release.

### Smart test targeting

Most test frameworks support running subsets:
```bash
# By file pattern
jest --testPathPattern="auth"
pytest -k "test_auth"

# By directory
jest tests/api/
pytest tests/integration/

# By tag/marker (if the project uses them)
pytest -m "critical"
jest --selectProjects="core"
```

## When NOT to Regress

- The change is purely additive (new feature, no modifications to existing code)
- The change is cosmetic (copy changes, comment updates)
- Targeted tests already cover all affected paths
- The project has no test suite (there's nothing to regress against — note this as a gap)

## Interpreting Regression Results

- **Unrelated test failures**: Check if these tests were already failing before your change (`git stash`, run tests, `git stash pop`). Pre-existing failures are not your regression.
- **Flaky tests**: If a test fails inconsistently, it's flaky — not a regression. Note it but don't block on it.
- **Slow suites**: If the full suite takes > 5 minutes, prefer targeted regression (Ring 1-2) unless the change is high-risk.
