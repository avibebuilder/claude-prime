# File Naming Conventions

## Naming Rules

- **ALWAYS** kebab-case for ALL filenames and directories
  - ✅ `user-profile.tsx`, `api-client.ts`
  - ❌ `UserProfile.tsx`, `userProfile.tsx`, `user_profile.tsx`
- **NEVER** use index files (`index.ts`, `index.tsx`)

## Searchable Names

Filenames MUST be searchable (using grep) and specific:

```
✅ login-container.tsx     (search "login-container" = 1 result)
✅ auth-api.ts             (search "auth-api" = 1 result)
✅ query-key-constants.ts  (search "query-key" = found)

❌ container.tsx           (search "container" = 100+ results)
❌ api.ts                  (useless)
❌ constants.ts            (too generic)
```

## Non-Component Files

Pattern: `{name}-{parent-folder}.ts`

```
✅ constants/app-config-constants.ts
✅ types/user-profile-types.ts
✅ lib/dayjs-lib.ts

❌ app-config.ts
❌ user-profile.ts
```

## Component Files

Pattern: `{descriptive-name}.tsx` (folder provides context)

```
✅ interview-session-table.tsx
✅ login-form.tsx
✅ campaign-card.tsx
```

## Type Placement (LOCAL SCOPE PREFERRED)

**Rule:** If type is NOT shared across multiple features → LOCAL scope.

| Scope | Location |
|-------|----------|
| Component-specific | Define directly in component file |
| Feature-specific | `{feature}/interfaces/` or `{feature}/types/` |
| Global (truly shared) | `src/lib/types/` |

## Performance Conventions

### Barrel File Imports

- **NEVER** import from barrel files (`index.ts` re-exports). Import directly from source files
- Barrel files with thousands of re-exports add 200-800ms import time

```tsx
// ✅ Direct import from source
import { Button } from "@/components/ui/button";

// ❌ Barrel file (loads everything)
import { Button } from "@/components/ui";
```

### Long Lists Performance

- **ALWAYS** use `content-visibility: auto` with `contain-intrinsic-size` for long off-screen lists
- Browser skips rendering ~990/1000 off-screen items (10x faster initial render)

```css
.list-item {
  content-visibility: auto;
  contain-intrinsic-size: auto 50px; /* estimated height */
}
```

## Framework-Specific Structure

- **Next.js**: See [nextjs/file-structure.md](./nextjs/file-structure.md)
- **React**: See [react/file-structure.md](./react/file-structure.md)
