from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "SATI IA API"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/sati"
    cors_origins: str = "http://localhost:5173,http://localhost:8031"
    frontend_url: str = "http://localhost:8031"

    auth_cookie_name: str = "sati_session"
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"
    auth_cookie_domain: str | None = None
    session_ttl_hours: int = 168

    sentry_dsn: str | None = None

    seed_admin_email: str | None = None
    seed_admin_name: str = "Vitor Lescowicz"
    seed_admin_password: str | None = None
    whatsapp_verify_token: str | None = None
    whatsapp_default_tenant_slug: str = "tenda-rj"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
