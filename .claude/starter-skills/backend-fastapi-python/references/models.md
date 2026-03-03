# Models

## SQLModel Overview

SQLModel combines SQLAlchemy and Pydantic. Models serve as both ORM entities and data validation.

## Base Model

Define a base class with common fields:

```python
# src/models/base_model.py
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

from src.core.utils import generate_id


class BaseSQLModel(SQLModel):
    id: str = Field(default_factory=generate_id, primary_key=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(UTC),
        ),
    )
```

### ID Generation

```python
# src/core/utils.py
from nanoid import generate as _nanoid_generate

NANOID_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def generate_id(size: int = 14) -> str:
    """Generate alphanumeric ID using nanoid with custom alphabet"""
    return _nanoid_generate(alphabet=NANOID_ALPHABET, size=size)
```

## Entity Models

```python
# src/models/user_model.py
from datetime import datetime
from typing import Literal

from sqlalchemy import ARRAY, Column, DateTime, String
from sqlmodel import Field

from src.models.base_model import BaseSQLModel

AuthProvider = Literal["email", "google"]


class User(BaseSQLModel, table=True):
    __tablename__ = "users"

    # Required fields
    first_name: str
    last_name: str
    email: str = Field(unique=True, index=True)

    # Authentication
    hashed_password: str | None = None
    auth_providers: list[str] = Field(
        sa_column=Column(ARRAY(String), nullable=False, server_default='{"email"}')
    )
    google_id: str | None = Field(default=None, unique=True, index=True)

    # Profile
    avatar_url: str | None = None

    # Permissions
    is_active: bool = True
    is_admin: bool = False

    # Analytics
    last_sign_in_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # Computed properties
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

## Field Patterns

### Required vs Optional

```python
# Required - no default
first_name: str

# Optional with default
avatar_url: str | None = None
is_active: bool = True
```

### Unique and Indexed

```python
email: str = Field(unique=True, index=True)
google_id: str | None = Field(default=None, unique=True, index=True)
```

### Array Fields (PostgreSQL)

```python
from sqlalchemy import ARRAY, Column, String

auth_providers: list[str] = Field(
    sa_column=Column(ARRAY(String), nullable=False, server_default='{"email"}')
)
```

### DateTime with Timezone

```python
from sqlalchemy import Column, DateTime

last_sign_in_at: datetime | None = Field(
    default=None,
    sa_column=Column(DateTime(timezone=True), nullable=True)
)
```

### Auto-update Timestamp

```python
updated_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=lambda: datetime.now(UTC),
    ),
)
```

## Model Export

Export all models from `__init__.py` for Alembic:

```python
# src/models/__init__.py
from src.models.base_model import BaseSQLModel
from src.models.user_model import User

__all__ = ["BaseSQLModel", "User"]
```

## Best Practices

1. **Always inherit from `BaseSQLModel`** - Consistent id, created_at, updated_at
2. **Use `table=True`** - Required for ORM mapping
3. **Set `__tablename__`** - Explicit table name
4. **Use timezone-aware datetime** - `DateTime(timezone=True)`
5. **Index frequently queried fields** - `Field(index=True)`
6. **Use properties for computed values** - Not stored in DB
