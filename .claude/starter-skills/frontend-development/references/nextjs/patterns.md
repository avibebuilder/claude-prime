# Next.js Patterns

## Server-First Architecture

- Default = Server Component. Only add `'use client'` when you need interactivity, state, or browser APIs
- **NEVER** `'use client'` on entire page — extract ONLY the interactive leaf components
- Server Components CAN import Client Components. Client Components CANNOT import Server Components
- Pass server data to Client Components as props — props MUST be serializable (no functions, classes, Date objects)
- Minimize client serialization — the RSC/Client boundary serializes ALL object properties. Only pass fields the client actually uses

## Routing Patterns

- **ALWAYS** use route groups `(folder)` for separating layouts (e.g., `(public)` vs `(authenticated)`)
- Route groups do NOT affect URL paths — they are organizational only

## API Routes

- API routes ONLY for: webhooks, external API endpoints, tRPC endpoint
- **NEVER** create custom API routes for internal data operations
- Internal data fetching → use tRPC procedures or Server Components with direct DB/service calls

## Security

- **ALWAYS** verify auth inside each Server Action — never rely solely on middleware or layout guards
- Server Actions are exposed as public HTTP endpoints. Treat them like API routes for authorization

## Next.js 15+ Async APIs

> Applies when Next.js 15+ is detected.

- `params` and `searchParams` are now `Promise<...>` — **MUST** `await` in pages, layouts, route handlers, and `generateMetadata`
- Use `React.use()` for non-async components that need to unwrap params
- `cookies()` and `headers()` are async — **ALWAYS** await them
- `fetch()` requests are no longer cached by default — use explicit `{ next: { revalidate, tags } }` for caching

```tsx
// WRONG (Next.js 14 style)
function Page({ params }: { params: { id: string } }) {
  return <div>{params.id}</div>;
}

// RIGHT (Next.js 15+)
async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <div>{id}</div>;
}
```

## Suspense

- `useSearchParams()` without a Suspense boundary causes the entire page to fall back to CSR
- **ALWAYS** wrap components using `useSearchParams()` in `<Suspense>`

Official docs: https://nextjs.org/docs
