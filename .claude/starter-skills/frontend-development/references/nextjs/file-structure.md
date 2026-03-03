# Next.js File Structure

## Directory Layout

```
public/                          # Static serving assets (images, fonts)
src/
├── middleware.ts                # Auth/routing middleware
├── apis/                        # API service layer
│   └── campaign-api.ts
├── app/                         # App Router ONLY (pages, layouts)
│   ├── layout.tsx
│   ├── (auth)/                  # Protected routes (with AuthGuard)
│   │   ├── layout.tsx
│   │   └── campaigns/page.tsx
│   └── (public)/                # Public routes
│       └── auth/login/page.tsx
├── assets/                      # Bundled assets (SVGs), non serving as static assets
├── components/                  # Shared/reusable components
│   └── auth-guard.tsx
├── containers/                  # Page-level logic (delegate from app/)
│   └── campaigns/
│       ├── campaigns-container.tsx
│       ├── constants/           # Feature-scoped constants
│       └── components/          # Feature-scoped components
│           └── campaign-card.tsx
├── contexts/                    # Shared React contexts
│   └── user-context.tsx
├── hooks/                       # Shared Custom hooks
│   └── use-redirect-from-url.ts
├── lib/
│   ├── clients/                 # API & Query clients
│   │   └── api-client.ts
│   ├── constants/               # Shared app constants
│   │   └── query-key-constants.ts
│   └── utils/                   # Shared Utilities
│       └── common-util.ts
├── stores/                      # Zustand state management
│   └── app/
│       └── example-slice.ts
└── styles/
```

## Rules

- **ONLY** Next.js files in `app/` (page, layout, loading, error)
- **ALWAYS** delegate logic to `containers/`
- **NEVER** put business logic in `app/` pages

## Page → Container Pattern

```tsx
// app/campaigns/page.tsx (thin wrapper)
export default function CampaignsPage() {
  return <CampaignsContainer />;
}

// containers/campaigns/campaigns-container.tsx (all logic)
export function CampaignsContainer() {
  // Logic here
}
```
