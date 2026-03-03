# Services

## Service Layer Pattern

Services contain business logic. They are **stateless functions**, not classes.

## Structure

```python
# src/modules/auth/auth_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.models.user_model import User
from src.modules.auth.auth_constants import AuthErrorCode
from src.modules.auth.auth_schemas import RegisterRequest
from src.modules.auth.auth_utils import hash_password, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    # Check existing
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise AppException(400, "Email already registered", AuthErrorCode.USER_EXISTED)

    # Create user
    hashed = hash_password(data.password)
    user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=hashed,
        auth_providers=["email"],
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if not user or not user.hashed_password:
        raise AppException(401, "Invalid email or password")

    if not verify_password(password, user.hashed_password):
        raise AppException(401, "Invalid email or password")

    if not user.is_active:
        raise AppException(403, "Account is inactive")

    # Update last sign in
    user.last_sign_in_at = datetime.now(UTC)
    db.add(user)
    await db.commit()

    return user
```

## Key Conventions

### Function Signature

```python
# First parameter is always db session
async def some_operation(
    db: AsyncSession,
    # Required parameters
    entity_id: str,
    data: SomeRequest,
    # Optional parameters with defaults
    include_deleted: bool = False,
) -> ReturnType:
    ...
```

### Error Handling

```python
from src.core.exceptions import AppException
from src.modules.users.user_constants import UserErrorCode

async def update_user(db: AsyncSession, user_id: str, data: UpdateUserRequest) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise AppException(404, "User not found", UserErrorCode.USER_NOT_FOUND)

    # Business rule validation
    if user_id == current_admin_id and data.is_admin is False:
        raise AppException(
            400,
            "Cannot demote yourself",
            UserErrorCode.CANNOT_SELF_MODIFY,
        )

    # Update and save
    ...
```

### Using FastCRUD for Complex Queries

```python
from fastcrud import FastCRUD
from typing import Any

user_crud: FastCRUD = FastCRUD(User)


async def list_users_paginated(
    db: AsyncSession,
    page: int,
    limit: int,
    q: str | None,
    is_active: bool | None,
    sort_by: list[str],
) -> dict:
    # Build filters
    filters: dict[str, Any] = {}

    if is_active is not None:
        filters["is_active"] = is_active

    # OR search across fields
    if q:
        filters["_or"] = {
            "first_name__ilike": f"%{q}%",
            "last_name__ilike": f"%{q}%",
            "email__ilike": f"%{q}%",
        }

    # Parse sort
    sort_columns = []
    sort_orders = []
    for item in sort_by:
        if ":" in item:
            col, order = item.split(":", 1)
            sort_columns.append(col)
            sort_orders.append(order)

    offset = (page - 1) * limit

    return await user_crud.get_multi(
        db=db,
        offset=offset,
        limit=limit,
        sort_columns=sort_columns or ["created_at"],
        sort_orders=sort_orders or ["desc"],
        return_total_count=True,
        **filters,
    )
```

## Utils vs Services

**Services** (`*_service.py`):
- Business logic
- Database operations
- Validation rules

**Utils** (`*_utils.py`):
- Pure functions
- No database
- Reusable helpers

```python
# src/modules/auth/auth_utils.py (utils - no db)
import bcrypt
from jose import jwt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": expire, "type": "access"}
    return jwt.encode(payload, secret, algorithm=algorithm)
```

## Best Practices

1. **Stateless functions** - No class instances, no shared state
2. **db as first param** - Consistent signature across all services
3. **Raise AppException** - With error codes for frontend
4. **Single responsibility** - One function, one operation
5. **Composition** - Services can call other services
6. **No HTTP concerns** - No Request/Response objects in services
