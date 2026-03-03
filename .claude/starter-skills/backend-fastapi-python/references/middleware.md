# Middleware

## Middleware Types

FastAPI supports two middleware patterns:
1. **ASGI Middleware** - Lower level, more control
2. **BaseHTTPMiddleware** - Simpler, higher level

## Request ID Middleware (ASGI)

```python
# src/core/middlewares/request_id_middleware.py
from collections.abc import Callable
from contextvars import ContextVar

from src.core.utils import generate_id

# Context variable for request-scoped ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get current request ID from context"""
    return request_id_var.get()


class RequestIDMiddleware:
    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        # Only process HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get or generate request ID
        headers_dict = dict(scope["headers"])
        request_id = headers_dict.get(b"x-request-id")

        if not request_id:
            request_id = f"req_{generate_id()}".encode()
            headers_dict[b"x-request-id"] = request_id
            scope["headers"] = list(headers_dict.items())

        # Set in context for use in handlers
        request_id_var.set(request_id.decode())

        await self.app(scope, receive, send)
```

## Logging Middleware (BaseHTTPMiddleware)

```python
# src/core/middlewares/logging_middleware.py
import time

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("x-request-id", "unknown")
        start_time = time.time()

        # Request info
        method = request.method
        path = request.url.path
        query = request.url.query
        path_with_query = f"{path}?{query}" if query else path

        # Client IP (handle proxy headers)
        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"

        # Log request
        logger.info(
            f"[{request_id}] Req: {client_ip} {method} {path_with_query}",
            extra={
                "request_id": request_id,
                "client_ip": client_ip,
                "method": method,
                "path": path,
            },
        )

        # Process request
        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"[{request_id}] Res: {response.status_code} ({duration:.3f}s)",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": duration,
            },
        )

        return response
```

## Registration Order

```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.middlewares.logging_middleware import RequestLoggingMiddleware
from src.core.middlewares.request_id_middleware import RequestIDMiddleware

app = FastAPI()

# CORS first (outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware (execution order: last added = first executed)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
```

**Execution order:**
```
Request → RequestIDMiddleware → RequestLoggingMiddleware → CORS → Route
Response ← RequestIDMiddleware ← RequestLoggingMiddleware ← CORS ← Route
```

## Using Context Variables

```python
# In exception handlers
from src.core.middlewares.request_id_middleware import get_request_id

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    request_id = get_request_id()
    logger.error(f"[{request_id}] Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"request_id": request_id, "message": "Internal error"},
    )
```

## CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # List of allowed origins
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
```

## Best Practices

1. **Use ASGI for performance** - Lower overhead than BaseHTTPMiddleware
2. **Use BaseHTTPMiddleware for simplicity** - When you need Request/Response objects
3. **Order matters** - Last added = first executed
4. **Use context variables** - For request-scoped data (request ID, user)
5. **Log request ID everywhere** - For tracing
