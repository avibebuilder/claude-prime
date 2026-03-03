# Axios Client Patterns

## Client Setup

```tsx
// lib/clients/api-client.ts
import axios from "axios";
import { APP_CONFIG } from "@/lib/constants/app-config-constants";

export const apiClient = axios.create({
  baseURL: APP_CONFIG.API_URL,
  withCredentials: true,
  paramsSerializer: { indexes: null },
});
```

## Token Refresh Interceptor

Auto-refresh on 401, redirect on failure:

```tsx
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    if (error.response?.status === 401 && !config._unretryable) {
      try {
        await apiClient.post("/auth/refresh", null, { _unretryable: true });
        return apiClient(config); // Retry original
      } catch {
        if (typeof window !== "undefined") {
          window.location.href = "/auth/login";
        }
      }
    }
    return Promise.reject(error);
  }
);
```

## API Service Layer

Create typed functions in `apis/` folder:

```tsx
// apis/auth-api.ts
import type { ApiResponse, LoginRequest, User } from "@/types";
import { apiClient } from "@/lib/clients/api-client";

export async function loginApi(data: LoginRequest) {
  return (await apiClient.post<ApiResponse<null>>("/auth/login", data)).data;
}

export async function getMeApi() {
  return (await apiClient.get<ApiResponse<User>>("/auth/me")).data;
}

export async function logoutApi() {
  return (await apiClient.post<ApiResponse<null>>("/auth/logout")).data;
}
```

## Usage with TanStack Query

```tsx
const { data } = useQuery({
  queryKey: [QUERY_KEY.AUTH.ME],
  queryFn: getMeApi,
});

const { mutate } = useMutation({
  mutationFn: loginApi,
  onSuccess: () =>
    queryClient.invalidateQueries({ queryKey: [QUERY_KEY.AUTH.ME] }),
});
```

## Rules

- **ALWAYS** create typed API functions in `apis/` folder
- **ALWAYS** use `withCredentials: true` for cookie auth
- **ALWAYS** use `paramsSerializer: { indexes: null }` if backend are Python FastAPI
- **ALWAYS** return `.data` from API functions
- **NEVER** store tokens in localStorage (use httpOnly cookies)
