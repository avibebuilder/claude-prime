# React Patterns & Conventions

## Component Conventions

- **ALWAYS** use `function` syntax for components (not arrow functions)
- **ALWAYS** use named exports (no `export default` except Next.js pages/layouts)
- **NEVER** use `React.FC` — use explicit props typing: `function MyComponent({ title }: Props)`
- **ALWAYS** prefix handlers with `handle` (`handleClick`, `handleSubmit`)
- **ALWAYS** prefix callback props with `on` (`onClick`, `onSubmit`)

### Function vs Arrow Usage

| Use `function` | Use arrow `=>` |
|----------------|----------------|
| Components | Inline event handlers |
| Reused utility functions | Array methods (`.map`, `.filter`) |
| Complex event handlers | Callback arguments |
| Custom hooks | Small one-line utilities |

## Hook Conventions

- Custom hooks **MUST** return objects (not arrays)
  - Arrays break when consumers don't need all values
  - Objects allow destructuring only what's needed

```tsx
// WRONG
return [value, setValue, reset] as const;

// RIGHT
return { value, setValue, reset };
```

## React 19 Hooks

> Applies when React 19+ is detected. Reference: https://react.dev/blog/2024/12/05/react-19

**ALWAYS** prefer React 19 built-in hooks over manual implementations:

| Old Pattern | React 19 Replacement |
|-------------|---------------------|
| `useFormState` (react-dom) | `useActionState` |
| Manual pending state tracking | `useFormStatus` |
| Manual state + rollback logic | `useOptimistic` |
| `useEffect` for data fetching | `use()` with Suspense |

## Immutable Array Methods

**ALWAYS** prefer immutable array methods — `.sort()` mutates in place and breaks React state/props.

| Mutating (NEVER) | Immutable (ALWAYS) |
|-------------------|--------------------|
| `.sort()` | `.toSorted()` |
| `.reverse()` | `.toReversed()` |
| `.splice()` | `.toSpliced()` |
| direct index assignment | `.with(index, value)` |

## Context

> Reference: https://react.dev/reference/react/createContext

| Use Context | Use Zustand/Query |
|-------------|-------------------|
| Server-provided data (user session) | Client UI state |
| Theme/locale settings | Complex state logic |
| Rarely changing data | Frequently changing data |

- **ALWAYS** create a custom hook wrapper — never expose `useContext` directly
- **ALWAYS** throw error if used outside provider
- **ALWAYS** use `undefined` as default value (not `null`) for type safety
- **NEVER** store frequently changing data in Context (causes full subtree re-renders)

## Forms (RHF + Zod + shadcn)

> Setup guide: https://ui.shadcn.com/docs/components/form

**Required stack**: `react-hook-form` + `@hookform/resolvers` + `zod` + `@/components/ui/form` (shadcn)

- **MUST** initialize ALL fields in `defaultValues`
- **ALWAYS** use `FormMessage` for errors (never custom error display)
- **ALWAYS** spread `{...field}` on inputs when props match
- **NEVER** manually manage `id`/`htmlFor`/ARIA attributes

**Hierarchy (STRICT)**: `Form → form → FormField → FormItem → FormLabel/FormControl/FormMessage`

Context-based wiring depends on this exact nesting. Breaking the hierarchy breaks auto-wiring of labels, error messages, and accessibility attributes.

When input props don't match field props, map explicitly:

```tsx
<FormControl>
  <CustomSelect onSelectChange={field.onChange} customValue={field.value} />
</FormControl>
```

## Lazy Loading

- **ALWAYS** lazy load pages, modals, sheets, dialogs with `React.lazy`
- **ALWAYS** wrap lazy components in `Suspense`
- **ALWAYS** use named exports → `.then(m => ({ default: m.ComponentName }))`
- Use `lazyRetry` wrapper for pages if available in project (handles chunk load errors)
