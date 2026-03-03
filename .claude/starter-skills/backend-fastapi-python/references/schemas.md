# Schemas

## Pydantic Schemas for API

Schemas define request/response shapes. Separate from SQLModel entities.

## Core Schemas

```python
# src/core/schemas.py
from pydantic import BaseModel, Field, computed_field


class ApiResponse[T](BaseModel):
    """Generic API response wrapper"""
    data: T | None = None
    message: str | None = None


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class CommonQueryParams(PaginationParams):
    """Common query parameters with search and sort"""
    q: str | None = Field(default=None, description="Search query")
    sort_by: list[str] = Field(
        default_factory=list,
        description="Sort fields with direction (e.g., 'name:asc', 'created_at:desc')",
    )


class PaginatedResponse[T](BaseModel):
    """Paginated list response"""
    items: list[T]
    total: int
    page: int
    limit: int

    @computed_field
    @property
    def total_pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit
```

## Request Schemas

Naming: `{Action}Request`

```python
# src/modules/auth/auth_schemas.py
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateUserRequest(BaseModel):
    """Partial update - all fields optional"""
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
```

## Response Schemas

Naming: `{Entity}Response`

```python
# src/modules/auth/auth_schemas.py
from pydantic import BaseModel


class AuthUserResponse(BaseModel):
    model_config = {"from_attributes": True}  # Enable ORM mode

    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str  # Property from model
    is_admin: bool


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime
```

## Using in Routes

```python
from src.core.schemas import ApiResponse, PaginatedResponse
from src.modules.users.user_schemas import UserResponse


@router.get("", response_model=ApiResponse[PaginatedResponse[UserResponse]])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PaginatedResponse[UserResponse]]:
    users, total = await user_service.list_users(db, page, limit)

    return ApiResponse(
        data=PaginatedResponse(
            items=users,
            total=total,
            page=page,
            limit=limit,
        )
    )


@router.post("/register", response_model=ApiResponse[AuthUserResponse])
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[User]:
    user = await auth_service.register_user(db, data)
    return ApiResponse(data=user)
```

## Key Patterns

### ORM Mode

```python
class UserResponse(BaseModel):
    model_config = {"from_attributes": True}  # Pydantic v2
    # Allows: UserResponse.model_validate(user_orm_object)
```

### Partial Updates

```python
class UpdateUserRequest(BaseModel):
    # All optional for PATCH
    first_name: str | None = None
    last_name: str | None = None
```

### Validation

```python
from pydantic import EmailStr, Field

email: EmailStr  # Email validation
password: str = Field(min_length=8)  # Length constraint
page: int = Field(ge=1)  # Greater than or equal
limit: int = Field(ge=1, le=100)  # Range
```

### Generic Types (Python 3.12+)

```python
class ApiResponse[T](BaseModel):
    data: T | None = None

# Usage
ApiResponse[UserResponse]
ApiResponse[PaginatedResponse[UserResponse]]
```

## Best Practices

1. **Separate request/response schemas** - Don't reuse models
2. **Use `from_attributes=True`** - For ORM to Pydantic conversion
3. **Validate at boundaries** - Request schemas validate input
4. **Explicit response shapes** - Response schemas define output
5. **Generic wrapper** - `ApiResponse[T]` for consistency
