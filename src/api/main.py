import os
import uuid

import redis as redis_client
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

import structlog
from api.database import SessionLocal
from api.logging_config import configure_logging, get_logger
from api.routers import auth

configure_logging()
logger = get_logger(__name__)

_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

_REDIS_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/1")

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title="Argus",
    version="0.1.0",
    docs_url="/docs" if os.environ.get("DEBUG", "false").lower() == "true" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if os.environ.get("DEBUG", "false").lower() == "true" else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.clear_contextvars()
        response.headers["X-Request-ID"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"
        return response


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path != "/health":
            logger.info(
                "http_request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                client=request.client.host if request.client else "unknown",
            )
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.get("/health", include_in_schema=False)
def health_check():
    checks: dict[str, str] = {"status": "ok", "database": "ok", "redis": "ok"}

    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("health_database_error", error=str(exc))
        checks["database"] = "error"
        checks["status"] = "degraded"
    finally:
        session.close()

    try:
        client = redis_client.from_url(_REDIS_URL, socket_connect_timeout=2)
        client.ping()
    except Exception as exc:
        logger.error("health_redis_error", error=str(exc))
        checks["redis"] = "error"
        checks["status"] = "degraded"

    status_code = 200 if checks["status"] == "ok" else 503
    return JSONResponse(content=checks, status_code=status_code)


app.include_router(auth.router)

# Additional routers registered as they are implemented:
# from api.security import require_authenticated_user
# from fastapi import Depends
# from api.routers import investigations, modules, ws
# app.include_router(investigations.router, prefix="/api/v1", dependencies=[Depends(require_authenticated_user)])
# app.include_router(modules.router, prefix="/api/v1", dependencies=[Depends(require_authenticated_user)])
# app.include_router(ws.router)
