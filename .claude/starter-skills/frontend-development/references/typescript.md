# TypeScript Conventions

## Type vs Interface

- **ALWAYS** `interface` for object shapes and props
- **ONLY** use `type` for:
  - Unions: `type Status = 'loading' | 'success' | 'error'`
  - Primitives: `type UserId = string`
  - Zod inference: `type FormData = z.infer<typeof schema>`
  - Database inference: `type User = Tables<'users'>`
  - Complex mapped types

```typescript
// ✅ Interface for objects
interface UserProfileProps {
  user: User;
  onUpdate: (data: Partial<User>) => void;
}

// ✅ Type for unions/inference
type Status = 'loading' | 'success' | 'error';
type CreateUserInput = z.infer<typeof createUserSchema>;
```

## Constants & Enums

- **NEVER** use `enum` - use `as const` instead
- **ALWAYS** SCREAMING_SNAKE_CASE for constants

```typescript
// ✅ as const pattern
const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  SYSTEM_ADMIN: 'system_admin',
} as const;

type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES];
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Props interface | `{Component}Props` | `ButtonProps` |
| Interfaces/Types | PascalCase | `UserProfile` |
| Constants | SCREAMING_SNAKE_CASE | `API_BASE_URL` |
| Variables/Functions | camelCase | `fetchUser` |
| Event handlers | `handle*` | `handleSubmit` |
| Callback props | `on*` | `onSubmit` |

## Code Style

- **ALWAYS** curly braces for block statements (if, for, while)
- Arrow functions CAN skip braces for simple expressions

```typescript
// ✅ Always braces for blocks
if (condition) { doSomething(); }
for (const item of items) { process(item); }

// ✅ Arrow functions - braces optional for simple
const getName = (user: User) => user.name;
items.filter(item => item.active);
```

## Imports

- **ALWAYS** use `type` keyword for type-only imports

```typescript
import type { User } from './types';
import { someFunction, type SomeType } from './module';
```
