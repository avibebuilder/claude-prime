# Tailwind CSS v4 Patterns

Critical v4 changes and anti-patterns. For full docs: https://tailwindcss.com/docs

## CSS-First Configuration

- No `tailwind.config.js` in v4 — configure in CSS with `@theme`
- Use `@theme inline` to map CSS variables to Tailwind utilities
- Use `@plugin` directive for plugins (replaces `require()` in config)

```css
@import "tailwindcss";

@plugin "@tailwindcss/typography";

@theme inline {
  --color-primary: var(--primary);
  --color-background: var(--background);
  --font-sans: var(--font-geist-sans);
}
```

## Anti-Patterns

- **NEVER** use `@apply` — deprecated in v4
- **NEVER** double-wrap color values: `hsl(var(--background))` is wrong — v4 handles color functions automatically, use `var(--background)` directly
- **NEVER** use `dark:` prefix for semantic colors — they auto-switch via CSS variables
- **NEVER** put `:root` or `.dark` selectors inside `@layer base` — define them outside layers
- **NEVER** nest `@theme` inside `.dark {}` — v4 does not support nested `@theme`
- **NEVER** install `tailwindcss-animate` or `tw-animate-css` — deprecated in v4, use built-in animation utilities
