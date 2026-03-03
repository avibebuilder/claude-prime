# TanStack Query Conventions

Full docs: https://tanstack.com/query/latest/docs/framework/react/overview

## Query Key Factory

- **ALWAYS** define query keys in `lib/constants/query-key-constants.ts` using the factory pattern
- **NEVER** use flat string keys — use hierarchical arrays for granular invalidation

```tsx
// lib/constants/query-key-constants.ts
export const QUERY_KEY = {
  USER: {
    all: ['user'] as const,
    lists: () => [...QUERY_KEY.USER.all, 'list'] as const,
    list: (filters?: UserFilters) => [...QUERY_KEY.USER.lists(), filters] as const,
    details: () => [...QUERY_KEY.USER.all, 'detail'] as const,
    detail: (id: string) => [...QUERY_KEY.USER.details(), id] as const,
  },
} as const;
// invalidate QUERY_KEY.USER.all -> clears ALL user queries
// invalidate QUERY_KEY.USER.lists() -> clears only lists, keeps details
```

## queryOptions Factory

- **ALWAYS** colocate queryKey + queryFn + options into a `queryOptions` factory — single source of truth for hooks, prefetching, and cache reads

```tsx
// lib/queries/user-queries.ts
export const userQueries = {
  list: (filters?: UserFilters) => queryOptions({
    queryKey: QUERY_KEY.USER.list(filters),
    queryFn: () => getUsersApi(filters),
  }),
  detail: (id: string) => queryOptions({
    queryKey: QUERY_KEY.USER.detail(id),
    queryFn: () => getUserApi(id),
    staleTime: 5 * 60 * 1000,
  }),
};
// Same factory everywhere: useQuery(userQueries.detail(id)), queryClient.prefetchQuery(...)
```

## Mutation + Invalidation

- **ALWAYS** invalidate related queries in `onSuccess`

```tsx
const mutation = useMutation({
  mutationFn: createUser,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: QUERY_KEY.USER.all });
  },
});
```

## Optimistic Updates

Pick based on scope:
- **UI variables** (single component): use `mutation.variables` + `isPending` inline. No cache manipulation.
- **Cache manipulation** (multiple components): modify cache in `onMutate`, rollback on error:

```tsx
useMutation({
  mutationFn: updateUser,
  onMutate: async (newData) => {
    const key = QUERY_KEY.USER.detail(newData.id);
    await queryClient.cancelQueries({ queryKey: key });
    const previous = queryClient.getQueryData(key);
    queryClient.setQueryData(key, (old) => ({ ...old, ...newData }));
    return { previous };
  },
  onError: (_err, newData, context) => {
    queryClient.setQueryData(QUERY_KEY.USER.detail(newData.id), context?.previous);
  },
  onSettled: (_data, _err, newData) => {
    queryClient.invalidateQueries({ queryKey: QUERY_KEY.USER.detail(newData.id) });
  },
});
```

## SSR Hydration (Next.js)

- **ALWAYS** create a new `QueryClient` per request — shared instances leak data between users

```tsx
export default async function Page({ params }: { params: { id: string } }) {
  const queryClient = new QueryClient(); // new per request!
  await queryClient.prefetchQuery(userQueries.detail(params.id));
  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <UserDetail /> {/* useQuery(userQueries.detail(id)) picks up prefetched data */}
    </HydrationBoundary>
  );
}
```

## Error Handling

- **NEVER** toast detailed error messages (security risk) — log details server-side
- **ALWAYS** show generic messages client-side

```tsx
onError: () => toast.error('Failed to save. Please try again.')
// NEVER: onError: (error) => toast.error(error.message)
```
