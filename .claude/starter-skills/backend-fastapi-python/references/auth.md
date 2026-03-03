# Auth (Example Implementation)

> **Note:** This is an example implementation using JWT cookies. Adapt to your specific requirements.

## Overview

Cookie-based JWT authentication with:
- Access token (short-lived, 15 min)
- Refresh token (long-lived, 7 days)
- HttpOnly cookies for security

## Configuration

```python
# src/modules/auth/auth_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_ignore_empty=True,
        extra="ignore",
    )

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth (optional)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""


auth_settings = AuthConfig()  # type: ignore
```

## Token Utilities

```python
# src/modules/auth/auth_utils.py
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt

from src.modules.auth.auth_config import auth_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": user_id, "exp": expire, "type": "access"}
    return jwt.encode(
        payload, auth_settings.JWT_SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM
    )


def create_refresh_token(user_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(
        payload, auth_settings.JWT_SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token, auth_settings.JWT_SECRET_KEY, algorithms=[auth_settings.JWT_ALGORITHM]
    )
```

## Auth Routes

```python
# src/modules/auth/auth_router.py
from fastapi import APIRouter, Depends, Request, Response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    user = await auth_service.authenticate_user(db, data.email, data.password)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Set HttpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",  # Stricter for refresh
        max_age=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return ApiResponse(message="Login successful")


@router.post("/logout")
async def logout(response: Response) -> ApiResponse[None]:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return ApiResponse(message="Logged out successfully")


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    refresh_token_value = request.cookies.get("refresh_token")
    if not refresh_token_value:
        raise AppException(401, "Refresh token required")

    try:
        payload = decode_token(refresh_token_value)

        if payload.get("type") != "refresh":
            raise AppException(401, "Invalid token type")

        user_id = payload.get("sub")
        user = await auth_service.get_user_by_id(db, user_id)

        if not user or not user.is_active:
            raise AppException(401, "Invalid token")

        # Issue new access token
        new_access_token = create_access_token(user.id)

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="lax",
            max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return ApiResponse(message="Token refreshed")
    except Exception:
        raise AppException(401, "Invalid refresh token")
```

## Cookie Settings

| Setting | Access Token | Refresh Token |
|---------|--------------|---------------|
| httponly | True | True |
| secure | production only | production only |
| samesite | lax | strict |
| max_age | 15 min | 7 days |

## Security Considerations

1. **HttpOnly** - Prevents JavaScript access (XSS protection)
2. **Secure** - HTTPS only in production
3. **SameSite** - CSRF protection
4. **Short access token** - Limits exposure window
5. **Refresh token rotation** - Consider rotating on each use

## Alternative: Bearer Token

If using Authorization header instead of cookies:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    ...
```
