# tRPC + TanStack Query Conventions

## Data Layer Strategy

- **ALWAYS** use tRPC + TanStack for ALL data operations if project is using tRPC
- **NEVER** create Server Actions - use tRPC procedures
- **NEVER** create custom API routes (except webhooks, tRPC endpoint)

## File Structure

```
src/trpc/
├── trpc-init.ts
├── trpc-client.tsx
├── trpc-server.tsx
├── trpc-context.ts
└── routers/
    └── {feature}-router.ts  # kebab-case
```

## Server Component Data

### Pure Server (no client interactivity)

```tsx
import { caller } from '@/trpc/trpc-server';

export default async function Page({ params }: Props) {
  const data = await caller.feature.getData({ id: params.id });
  return <div>{data.title}</div>;
}
```

### Server + Client Interactivity

```tsx
import { HydrateClient, prefetch, trpc } from '@/trpc/trpc-server';

export default async function Page() {
  await prefetch(trpc.feature.getData.queryOptions({ id }));

  return (
    <HydrateClient>
      <ClientComponent />
    </HydrateClient>
  );
}
```

## Client Component Patterns

```tsx
// Queries
const { data } = useQuery(trpc.feature.getData.queryOptions({ id }));

// Mutations
const mutation = useMutation(trpc.feature.create.mutationOptions());

// Invalidation
queryClient.invalidateQueries({ queryKey: trpc.feature.getData.queryKey() });
```

## Procedure Security

| Procedure | Use When |
|-----------|----------|
| `publicProcedure` | No auth needed |
| `protectedProcedure` | Authenticated users |
| `adminProcedure` | Admin role required |

- **NEVER** duplicate auth logic - rely on middleware

## Input Validation

- **ALWAYS** Zod schema directly in `.input()`

```tsx
// ✅ Direct schema
.input(z.object({ id: z.string().uuid() }))

// ❌ Don't extract to variable
const schema = z.object({ id: z.string().uuid() });
.input(schema)
```

## Type Exports

- **ALWAYS** use inference pattern

```tsx
export type Result = Awaited<ReturnType<typeof router.procedure>>;
```
