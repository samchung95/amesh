from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Process configuration.

    The foundation intentionally keeps configuration small. Future settings must preserve typed,
    layered validation and secret redaction described by EPIC-003.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = Field(default=8000, ge=1, le=65535)
    database_url: str = "postgresql+asyncpg://amesh:amesh@localhost:5432/amesh"
    object_storage_endpoint: str = "http://localhost:9000"
    object_storage_bucket: str = "amesh"
    auth_mode: str = "development"
    amesh_admin_token: SecretStr = SecretStr("development-token")
    kubernetes_context: str | None = None
    kubernetes_task_namespace: str = "amesh-tasks"
    worker_poll_seconds: float = Field(default=5.0, gt=0)
    worker_recovery_grace_seconds: float = Field(default=120.0, ge=0)
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
