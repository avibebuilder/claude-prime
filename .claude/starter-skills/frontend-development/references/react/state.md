# State Management

## Three-Layer Strategy

| Layer | Tool | Use Case |
|-------|------|----------|
| **Server State** | TanStack Query | API data, caching, sync |
| **Client State** | Zustand | UI state, preferences |
| **Component State** | useState/Context | Local, prop drilling |

**Rule**: Use the right layer. **NEVER** store server data in Zustand.

## Zustand Slice Pattern

### Define Slice

```tsx
// stores/app/example-slice.ts
import { type StateCreator } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface ExampleSlice {
  value: string;
  setValue: (v: string) => void;
}

export const createExampleSlice: StateCreator<
  ExampleSlice,
  [['zustand/immer', never]]
> = immer((set) => ({
  value: '',
  setValue: (v) => set((state) => { state.value = v }),  // Immer mutation
}));
```

### Compose Store

```tsx
// stores/app/use-app-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { createExampleSlice } from './example-slice';
import { createOtherSlice } from './other-slice';

type AppStore = ExampleSlice & OtherSlice;

export const useAppStore = create<AppStore>()(
  persist(
    (...args) => ({
      ...createExampleSlice(...args),
      ...createOtherSlice(...args),
    }),
    {
      name: 'app-store',
      partialize: (state) => ({ value: state.value }),  // What to persist
    }
  )
);
```

### Usage

```tsx
const value = useAppStore((s) => s.value);
const setValue = useAppStore((s) => s.setValue);
```

## Rules

- **ALWAYS** use slices for store organization
- **ALWAYS** use immer middleware for mutations
- **ALWAYS** use partialize to control persistence
- **NEVER** store API data in Zustand (use TanStack Query)
