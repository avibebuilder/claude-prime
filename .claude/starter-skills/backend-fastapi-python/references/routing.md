# Routing

## APIRouter Pattern

Each module has its own router file.

### Router Definition

```python
# src/modules/auth/auth_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.schemas import ApiResponse
from src.modules.auth import auth_service
from src.modules.auth.auth_schemas import LoginRequest, AuthUserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ApiResponse[None])
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    await auth_service.authenticate_user(db, data.email, data.password)
    return ApiResponse(message="Login successful")


@router.get("/me", response_model=ApiResponse[AuthUserResponse])
async def get_me(
    user: User = Depends(require_auth),
) -> ApiResponse[User]:
    return ApiResponse(data=user)
```

### Router Registration

```python
# src/main.py
from fastapi import APIRouter, FastAPI

from src.modules.auth.auth_router import router as auth_router
from src.modules.users.user_router import router as user_router

app = FastAPI(
    title="My API",
    root_path="/api",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Version prefix
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_router)
v1_router.include_router(user_router)

app.include_router(v1_router)
```

## Route Patterns

### CRUD Endpoints

```python
router = APIRouter(prefix="/users", tags=["users"])

# List with pagination
@router.get("", response_model=ApiResponse[PaginatedResponse[UserResponse]])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    q: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PaginatedResponse[UserResponse]]:
    ...

# Get single
@router.get("/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[User]:
    ...

# Create
@router.post("", response_model=ApiResponse[UserResponse], status_code=201)
async def create_user(
    data: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[User]:
    ...

# Update (partial)
@router.patch("/{user_id}", response_model=ApiResponse[UserResponse])
async def update_user(
    user_id: str,
    data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[User]:
    ...

# Delete
@router.delete("/{user_id}", response_model=ApiResponse[None])
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    ...
```

### Query Parameters

```python
from fastapi import Query

@router.get("")
async def list_items(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),

    # Search
    q: str | None = Query(None, description="Search query"),

    # Filters
    is_active: bool | None = Query(None, description="Filter by status"),

    # Sort (multiple values)
    sort_by: list[str] = Query(
        default_factory=list,
        description="Sort fields (e.g., 'created_at:desc')",
    ),
):
    ...
```

### Path Parameters

```python
@router.get("/{user_id}")
async def get_user(user_id: str):
    ...

@router.get("/{user_id}/posts/{post_id}")
async def get_user_post(user_id: str, post_id: str):
    ...
```

### Request Body

```python
@router.post("")
async def create_user(data: CreateUserRequest):
    ...

@router.patch("/{user_id}")
async def update_user(user_id: str, data: UpdateUserRequest):
    ...
```

### Response and Cookies

```python
from fastapi import Response

@router.post("/login")
async def login(data: LoginRequest, response: Response):
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=60 * 15,  # 15 minutes
    )
    return ApiResponse(message="Login successful")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return ApiResponse(message="Logged out")
```

## Best Practices

1. **Use `response_model`** - Explicit response typing
2. **Group related routes** - One router per module
3. **Version your API** - `/v1/` prefix
4. **Use Query for validation** - Built-in parameter validation
5. **Inject dependencies** - `Depends()` for db, auth
6. **Return domain objects** - Let `response_model` handle serialization
