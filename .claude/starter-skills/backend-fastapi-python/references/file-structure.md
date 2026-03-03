# File Structure

## Project Layout

```
project/
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── core/                # Shared infrastructure
│   │   ├── __init__.py
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── constants.py     # Global constants
│   │   ├── database.py      # Async engine + session factory
│   │   ├── dependencies.py  # Global dependencies
│   │   ├── exceptions.py    # AppException + handlers
│   │   ├── logging.py       # Loguru setup
│   │   ├── schemas.py       # ApiResponse, PaginatedResponse
│   │   ├── utils.py         # Shared utilities (ID generation)
│   │   └── middlewares/
│   │       ├── __init__.py
│   │       ├── request_id_middleware.py
│   │       └── logging_middleware.py
│   ├── models/              # SQLModel definitions
│   │   ├── __init__.py
│   │   ├── base_model.py    # BaseSQLModel
│   │   └── user_model.py
│   └── modules/             # Feature modules
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── auth_config.py
│       │   ├── auth_constants.py
│       │   ├── auth_dependencies.py
│       │   ├── auth_router.py
│       │   ├── auth_schemas.py
│       │   ├── auth_service.py
│       │   └── auth_utils.py
│       └── users/
│           ├── __init__.py
│           ├── user_constants.py
│           ├── user_dependencies.py
│           ├── user_router.py
│           ├── user_schemas.py
│           ├── user_service.py
│           └── user_utils.py
├── pyproject.toml
├── .env
└── .env.example
```

## Module Structure

Each feature module follows consistent naming:

```
modules/{module}/
├── __init__.py
├── {module}_config.py       # Module-specific settings (optional)
├── {module}_constants.py    # Error codes, enums
├── {module}_dependencies.py # FastAPI dependencies
├── {module}_router.py       # API routes
├── {module}_schemas.py      # Pydantic models
├── {module}_service.py      # Business logic
└── {module}_utils.py        # Helper functions (optional)
```

## File Naming Rules

| Type | Pattern | Example |
|------|---------|---------|
| Module router | `{module}_router.py` | `auth_router.py` |
| Module service | `{module}_service.py` | `auth_service.py` |
| Module schemas | `{module}_schemas.py` | `auth_schemas.py` |
| Module dependencies | `{module}_dependencies.py` | `auth_dependencies.py` |
| Module constants | `{module}_constants.py` | `auth_constants.py` |
| Module config | `{module}_config.py` | `auth_config.py` |
| Module utils | `{module}_utils.py` | `auth_utils.py` |

## Import Conventions

Use absolute imports from `src`:

```python
# Good
from src.core.config import settings
from src.core.database import get_db
from src.modules.auth.auth_service import authenticate_user

# Bad - relative imports
from ..core.config import settings
from .auth_service import authenticate_user
```

## Core vs Modules

**`core/`** - Shared infrastructure used across all modules:
- Configuration management
- Database connection
- Exception handling
- Common schemas (ApiResponse, PaginatedResponse)
- Middleware
- Utilities

**`modules/`** - Feature-specific code:
- Each module is self-contained
- Module can depend on `core/` and `models/`
- Modules should minimize cross-dependencies
- If modules share logic, extract to `core/`
