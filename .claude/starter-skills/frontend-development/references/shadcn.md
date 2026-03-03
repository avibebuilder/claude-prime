# shadcn/ui Usage Rules

## Class Merging

- **ALWAYS** use `cn()` from `@/lib/utils` for conditional/merged classes
- **NEVER** use template literals for class conditionals

```tsx
// ✅ Using cn()
<div className={cn("base-class", isActive && "active-class")} />

// ❌ Don't use template literals
<div className={`base-class ${isActive ? 'active-class' : ''}`} />
```

## Base UI over Radix

> Migration guide: https://github.com/shadcn-ui/ui/discussions/9562

- **ALWAYS** prefer Base UI (`base-vega` style) over Radix for new projects
- For new projects: `npx shadcn@latest init` → select Base UI
- For existing projects: migrate component-by-component, not big-bang
- Base UI uses `@base-ui-components/react` (single package) instead of multiple `@radix-ui/react-*`
- **Key API difference**: Base UI has no `asChild` — remove it when migrating
- Positioning uses Floating UI (`@floating-ui/react`) instead of Radix popover internals

## Component Selection (follow this order)

When you need a UI component:

1. **Check existing codebase** — is it already built?
2. **Check shadcn/ui** — to use base component if available, but for complex use cases, also check step 3 before deciding
3. **Check Dice UI registry** (https://www.diceui.com/docs) — Dice UI extends shadcn with 50+ components including: data tables, phone input, mask input, tags input, file upload, kanban, color picker, combobox, rating, time picker, and more. **ALWAYS** check here before composing or building custom.
4. **Compose from primitives** — combine shadcn/ui + Dice UI components
5. **Build custom** — last resort, only if none of the above work

- **NEVER** modify files in `src/components/ui/` without approval
- **NEVER** skip step 3 — Dice UI likely has what you need before deciding to build custom

## Form Components

Forms use shadcn/ui form components with RHF + Zod.

→ See [react/patterns.md](../react/patterns.md) for form rules and hierarchy.

## Dice UI Installation

```bash
npx shadcn@latest add https://www.diceui.com/r/[component]
```
