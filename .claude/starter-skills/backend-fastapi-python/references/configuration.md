# Configuration

## pydantic-settings Pattern

Use `pydantic-settings` for type-safe configuration with environment variable support.

### Global Settings

```python
# src/core/config.py
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_ignore_empty=True,
        extra="ignore",
    )

    # App
    ENVIRONMENT: Literal["development", "production"] = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Computed fields for derived values
    @computed_field
    @property
    def DEBUG(self) -> bool:
        return self.ENVIRONMENT == "development"

    @computed_field
    @property
    def LOG_LEVEL(self) -> str:
        return "debug" if self.ENVIRONMENT == "development" else "info"

    # Database
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # CORS - handle comma-separated string
    CORS_ORIGINS_STR: str = Field(default="", alias="CORS_ORIGINS")

    @computed_field
    @property
    def CORS_ORIGINS(self) -> list[str]:
        if not self.CORS_ORIGINS_STR:
            return []
        return [i.strip() for i in self.CORS_ORIGINS_STR.split(",") if i.strip()]


# Singleton instance
settings = Settings()  # type: ignore
```

### Module-Specific Config

Each module can have its own settings class:

```python
# src/modules/auth/auth_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.config import settings


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_ignore_empty=True,
        extra="ignore",
    )

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Computed from global settings
    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        return f"{settings.BASE_URL}/auth/google/callback"


auth_settings = AuthConfig()  # type: ignore
```

## Best Practices

### Use computed_field for Derived Values

```python
# Good - computed from other settings
@computed_field
@property
def DATABASE_URL(self) -> str:
    return f"postgresql+asyncpg://..."

# Bad - duplicating logic
DATABASE_URL: str  # Would need to be set manually
```

### Handle Complex Types

```python
# Comma-separated list from env
CORS_ORIGINS_STR: str = Field(default="", alias="CORS_ORIGINS")

@computed_field
@property
def CORS_ORIGINS(self) -> list[str]:
    return [i.strip() for i in self.CORS_ORIGINS_STR.split(",") if i.strip()]
```

### Type Annotations

```python
# Use Literal for constrained values
ENVIRONMENT: Literal["development", "production"] = "development"

# Use Optional with defaults
DEBUG: bool = False
```

### Environment File

```bash
# .env.example
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_DB=myapp

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Auth
JWT_SECRET_KEY=your-secret-key-here
```
