# Tailwind CSS v4 in Monorepos

Tailwind v4 uses CSS-first configuration (`@theme`, `@source`) instead of `tailwind.config.js`. Key challenge in monorepos: automatic content detection only scans downward from CSS file location.

## v3 to v4 Changes

| Aspect | Tailwind v3 | Tailwind v4 |
|--------|-------------|-------------|
| Config | `tailwind.config.js` | CSS with `@theme` directive |
| Content paths | `content: [...]` | Auto-detect + `@source` |
| Import | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| PostCSS plugin | `tailwindcss` | `@tailwindcss/postcss` |
| Vite plugin | N/A | `@tailwindcss/vite` (preferred) |

## Content Detection Across Packages

Auto-detection **does not traverse parent directories**. Use `@source` for explicit package paths.

**Explicit package sources:**
```css
/* apps/web/src/globals.css */
@import "tailwindcss";

@source "../../packages/ui/src/**/*.{ts,tsx}";
@source "../../packages/shared/components/**/*.{ts,tsx}";
```

**Set base path (scan from monorepo root):**
```css
@import "tailwindcss" source("../../");
```

**Disable auto-detection entirely:**
```css
@import "tailwindcss" source(none);
@source "../app";
@source "../packages/ui";
```

## Shared Design System Package

Recommended: centralized package exporting theme tokens.

**Structure:**
```
packages/
  design-system/
    src/
      theme.css
    package.json
```

**`packages/design-system/src/theme.css`:**
```css
@theme {
  /* Colors */
  --color-brand-50: oklch(0.97 0.01 250);
  --color-brand-500: oklch(0.55 0.2 250);
  --color-brand-900: oklch(0.25 0.1 250);

  /* Typography */
  --font-display: "Inter", sans-serif;
  --font-body: "Open Sans", sans-serif;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;

  /* Breakpoints */
  --breakpoint-3xl: 1920px;
}
```

**`packages/design-system/package.json`:**
```json
{
  "name": "@repo/design-system",
  "exports": {
    "./theme.css": "./src/theme.css"
  }
}
```

**Consuming in apps/packages:**
```css
@import "tailwindcss";
@import "@repo/design-system/theme.css";
```

Theme variables in `@theme` become both CSS custom properties AND utility classes.

## CSS Import Patterns

**Pattern A: Single entry point (recommended)**
```css
/* apps/web/src/globals.css */
@import "tailwindcss";
@import "@repo/design-system/theme.css";
@source "../../packages/ui/src";
@source "../components";
```

**Pattern B: Namespace prefixing (for isolation)**
```css
@import "tailwindcss" prefix(ui);
```

Generates `ui:bg-blue-500` etc. Useful for component libraries to avoid conflicts.

## Build Configuration

**Vite (preferred - 3.78x faster):**
```typescript
// vite.config.ts
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
});
```

**PostCSS (Next.js, etc.):**
```javascript
// postcss.config.js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

**turbo.json:**
```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    }
  }
}
```

## Migration

```bash
# Automated upgrade
npx @tailwindcss/upgrade

# Manual: legacy config still works via @config
@config "../../tailwind.config.js";
```

## Common Issues

**Missing styles from packages:**
- Automatic detection doesn't traverse `../` paths
- Solution: Add explicit `@source` for each package

**VS Code IntelliSense:**
- May need temporary `tailwind.config.js` for autocomplete
- Configure `tailwindCSS.experimental.configFile` in settings

**Different apps need different utilities:**
- Use `source(none)` + explicit `@source` per app
- Consider namespace prefixing for shared libraries

## Quick Start

```bash
# New monorepo with Tailwind v4
pnpm dlx create-turbo@latest -e with-tailwind
```

## Resources

- [Tailwind CSS v4 Blog](https://tailwindcss.com/blog/tailwindcss-v4)
- [Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Source Detection](https://tailwindcss.com/docs/detecting-classes-in-source-files)
- [Turborepo Tailwind Guide](https://turborepo.com/docs/guides/tools/tailwind)
