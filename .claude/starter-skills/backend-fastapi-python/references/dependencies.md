# Dependencies

## FastAPI Dependency Injection

Dependencies are reusable components injected into routes using `Depends()`.

## Database Dependency

```python
# src/core/database.py
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

Usage:
```python
@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    ...
```

## Authentication Dependencies

Build composable auth chain:

```python
# src/modules/auth/auth_dependencies.py
from fastapi import Depends, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.exceptions import AppException
from src.models.user_model import User
from src.modules.auth.auth_service import get_user_by_id
from src.modules.auth.auth_utils import decode_token


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Optional auth - returns None if no valid token"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        return None

    try:
        payload = decode_token(access_token)
        user_id = payload.get("sub")

        if not user_id or not isinstance(user_id, str):
            return None

        user = await get_user_by_id(db, user_id)
        if not user or not user.is_active:
            return None

        return user
    except (JWTError, Exception):
        return None


async def require_auth(
    user: User | None = Depends(get_current_user),
) -> User:
    """Required auth - raises 401 if no user"""
    if not user:
        raise AppException(401, "Authentication required")
    return user


async def require_admin(
    user: User = Depends(require_auth),
) -> User:
    """Required admin - raises 403 if not admin"""
    if not user.is_admin:
        raise AppException(403, "Admin access required")
    return user
```

## Dependency Chain

```
get_current_user (optional)
       ↓
  require_auth (required)
       ↓
  require_admin (admin only)
```

## Using in Routes

```python
# Optional auth - user might be None
@router.get("/public")
async def public_endpoint(
    user: User | None = Depends(get_current_user),
):
    if user:
        # Logged in user
        ...
    else:
        # Anonymous user
        ...


# Required auth
@router.get("/me")
async def get_profile(
    user: User = Depends(require_auth),
):
    return ApiResponse(data=user)


# Admin only
@router.get("/users")
async def list_users(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Only admins reach here
    ...


# Unused dependency (for side effects like auth check)
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    _admin: User = Depends(require_admin),  # Underscore = unused
    db: AsyncSession = Depends(get_db),
):
    ...
```

## Custom Dependencies

### Query Parameters

```python
from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20


def pagination(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit)


@router.get("/items")
async def list_items(pagination: PaginationParams = Depends(pagination)):
    offset = (pagination.page - 1) * pagination.limit
    ...
```

### Resource Ownership

```python
async def get_own_post(
    post_id: str,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> Post:
    post = await post_service.get_by_id(db, post_id)
    if not post:
        raise AppException(404, "Post not found")
    if post.user_id != user.id:
        raise AppException(403, "Not your post")
    return post


@router.patch("/posts/{post_id}")
async def update_post(
    data: UpdatePostRequest,
    post: Post = Depends(get_own_post),
    db: AsyncSession = Depends(get_db),
):
    ...
```

## Best Practices

1. **Chain dependencies** - Build on top of each other
2. **Single responsibility** - One dependency, one concern
3. **Use `_` prefix** - For unused but required dependencies
4. **Return domain objects** - Not raw data
5. **Raise AppException** - Consistent error handling
