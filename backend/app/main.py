from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings

try:
    import sentry_sdk
except Exception:  # pragma: no cover - optional during local bootstrap
    sentry_sdk = None


def create_app() -> FastAPI:
    settings = get_settings()

    if settings.sentry_dsn and sentry_sdk is not None:
        sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["infra"])
    def root() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.app_name,
            "message": "SATI IA API online",
            "health": "/health",
            "docs": "/docs",
            "api": settings.api_prefix,
            "frontend": settings.frontend_url,
        }

    @app.get("/health", tags=["infra"])
    def healthcheck() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.app_name,
            "environment": settings.environment,
        }

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
