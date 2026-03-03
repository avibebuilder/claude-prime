# Error Handling

## AppException

Custom exception with error codes for frontend handling.

```python
# src/core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.middlewares.request_id_middleware import get_request_id


class AppException(HTTPException):
    """Custom exception with error_code for frontend"""

    def __init__(self, status_code: int, message: str, error_code: str | None = None):
        super().__init__(status_code=status_code, detail=message)
        self.error_code = error_code
```

## Exception Handlers

```python
# src/core/exceptions.py
def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions with standardized format"""
        request_id = get_request_id()

        status_code = exc.status_code
        message = exc.detail
        error_code = getattr(exc, "error_code", None)

        logger.error(
            f"[{request_id}] HTTPException: {status_code} - {message}",
            extra={
                "request_id": request_id,
                "status_code": status_code,
                "error_code": error_code,
            },
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "request_id": request_id,
                "message": message,
                "error_code": error_code,
            },
        )

    @app.exception_handler(Exception)
    async def catch_all_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch unhandled exceptions"""
        request_id = get_request_id()

        logger.error(
            f"[{request_id}] Unhandled: {exc.__class__.__name__}",
            extra={
                "request_id": request_id,
                "exception_type": exc.__class__.__name__,
                "exception_message": str(exc),
            },
        )

        return JSONResponse(
            status_code=500,
            content={
                "request_id": request_id,
                "message": "Internal server error",
                "error_code": None,
            },
        )
```

## Registration

```python
# src/main.py
from src.core.exceptions import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
```

## Error Codes

Define error codes per module:

```python
# src/modules/auth/auth_constants.py
class AuthErrorCode:
    USER_EXISTED = "user_existed"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_INACTIVE = "account_inactive"


# src/modules/users/user_constants.py
class UserErrorCode:
    USER_NOT_FOUND = "user_not_found"
    CANNOT_SELF_MODIFY = "cannot_self_modify"
```

## Using in Services

```python
from src.core.exceptions import AppException
from src.modules.auth.auth_constants import AuthErrorCode


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise AppException(400, "Email already registered", AuthErrorCode.USER_EXISTED)
    ...


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if not user:
        raise AppException(401, "Invalid email or password")

    if not user.is_active:
        raise AppException(403, "Account is inactive", AuthErrorCode.ACCOUNT_INACTIVE)
    ...
```

## Response Format

**Success:**
```json
{
  "data": { ... },
  "message": null
}
```

**Error:**
```json
{
  "request_id": "req_abc123xyz",
  "message": "Email already registered",
  "error_code": "user_existed"
}
```

## HTTP Status Codes

| Status | Use Case |
|--------|----------|
| 400 | Bad request, validation error |
| 401 | Authentication required |
| 403 | Forbidden (authenticated but not authorized) |
| 404 | Resource not found |
| 409 | Conflict (duplicate resource) |
| 422 | Validation error (Pydantic) |
| 500 | Internal server error |

## Frontend Integration

Frontend can use `error_code` for:
- Displaying localized messages
- Conditional UI logic
- Form field highlighting

```typescript
// Frontend example
if (error.error_code === "user_existed") {
  setFieldError("email", "This email is already registered");
}
```

## Best Practices

1. **Always include request_id** - For debugging and support
2. **Use error codes** - Machine-readable for frontend
3. **Generic 500 message** - Never expose internal errors
4. **Log all errors** - With request_id for tracing
5. **Consistent format** - Same structure for all errors
