# Database

## Async SQLAlchemy Setup

### Engine and Session Factory

```python
# src/core/database.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL in development
    future=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent lazy load errors
)


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

### Using in Routes

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db


@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    # Use db session here
    pass
```

## Alembic Migrations

### Setup

```bash
# Initialize alembic
alembic init alembic
```

### Configure env.py

```python
# alembic/env.py
from src.core.config import settings
from src.models import *  # Import all models

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", ""))
target_metadata = BaseSQLModel.metadata
```

### Common Commands

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one
alembic downgrade -1

# Show current
alembic current
```

## Query Patterns

### Basic CRUD

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_model import User


# Get by ID
async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


# Get by unique field
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


# Create
async def create_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# Update
async def update_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# Delete
async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()
```

### Pagination with FastCRUD

```python
from fastcrud import FastCRUD

user_crud: FastCRUD = FastCRUD(User)

async def list_users_paginated(
    db: AsyncSession,
    page: int,
    limit: int,
    sort_by: list[str],
) -> dict:
    offset = (page - 1) * limit

    # Parse sort_by (e.g., ["created_at:desc"])
    sort_columns = []
    sort_orders = []
    for item in sort_by:
        if ":" in item:
            col, order = item.split(":", 1)
            sort_columns.append(col)
            sort_orders.append(order)

    return await user_crud.get_multi(
        db=db,
        offset=offset,
        limit=limit,
        sort_columns=sort_columns or ["created_at"],
        sort_orders=sort_orders or ["desc"],
        return_total_count=True,
    )
```

### Filtering

```python
# Simple filters
filters = {"is_active": True, "is_admin": False}

# OR conditions across fields
filters["_or"] = {
    "first_name__ilike": f"%{query}%",
    "last_name__ilike": f"%{query}%",
    "email__ilike": f"%{query}%",
}

result = await user_crud.get_multi(db=db, **filters)
```

## Best Practices

1. **Always use `expire_on_commit=False`** - Prevents lazy loading errors after commit
2. **Use `await db.refresh(obj)`** - Get updated values after commit
3. **Prefer `scalar_one_or_none()`** - For single object queries
4. **Use transactions explicitly** when needed - Default autocommit per operation
