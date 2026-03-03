# React File Structure

For React apps with Vite + React Router.

## Directory Layout

```
public/                          # Static serving assets (images, fonts)
src/
├── App.tsx
├── main.tsx                     # Entry point
├── apis/                        # API service layer
│   └── user-api.ts
├── assets/                      # Bundled assets (SVGs), non serving as static assets
├── components/                  # Shared/reusable components
│   └── auth-guard.tsx
├── contexts/                    # Shared React contexts
│   └── user-context.tsx
├── hooks/                       # Shared Custom hooks
│   └── use-auth.ts
├── lib/
│   ├── clients/                 # API & Query clients
│   │   └── api-client.ts
│   ├── constants/               # Shared App constants
│   │   └── query-key-constants.ts
│   └── utils/                   # Utilities
│       └── react-lazy-retry-util.ts
├── pages/                       # Page components by feature
│   ├── root-layout.tsx
│   ├── auth/
│   │   ├── auth-layout.tsx
│   │   └── login/
│   │       └── login-page.tsx
│   ├── users/
│   │   ├── users-page.tsx
│   │   ├── constants/           # Page/Feature-scoped constants
│   │   └── components/          # Page-scoped components
│   │       └── users-table/
│   └── errors/
│       └── notfound-page.tsx
├── routes/                      # React Router config (split by feature)
│   ├── app-routes.tsx
│   └── user-routes.tsx
├── stores/                      # Zustand state management
│   └── app/
│       └── example-slice.ts
└── styles/
```

## Rules

- **ALWAYS** named exports for pages (required for lazy loading)
- **ALWAYS** split routes by feature in `routes/`
- **ALWAYS** use `lazyRetry` for page lazy loading (handles chunk errors)
- **NEVER** default exports for lazy-loaded components

## Page Structure

```tsx
// pages/users/users-page.tsx
import { UsersTable } from './components/users-table/users-table';

export function UsersPage() {
  return (
    <div className="flex flex-col">
      <UsersTable />
    </div>
  );
}
```

## Route Configuration

```tsx
// routes/app-routes.tsx
import lazyRetry from '@/lib/utils/react-lazy-retry-util';

const UsersPage = lazyRetry(() =>
  import('@/pages/users/users-page').then((m) => ({ default: m.UsersPage }))
);

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AuthGuard />}>
        <Route element={<RootLayout />}>
          <Route path="users/*" element={<UserRoutes />} />
        </Route>
      </Route>
    </Routes>
  );
}
```