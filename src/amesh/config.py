from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
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
    database_read_replica_url: str | None = None
    database_pool_size: int = Field(default=10, ge=1, le=100)
    database_max_overflow: int = Field(default=10, ge=0, le=100)
    database_pool_timeout_seconds: float = Field(default=30, gt=0)
    database_pool_recycle_seconds: int = Field(default=1_800, ge=30)
    database_prepared_statement_cache_size: int = Field(default=100, ge=0, le=1_000)
    database_tls_mode: Literal["disable", "require", "verify-full"] = "disable"
    database_tls_ca_file: str | None = None
    database_slow_query_seconds: float = Field(default=0.5, gt=0)
    object_storage_endpoint: str = "http://localhost:9000"
    object_storage_region: str = "us-east-1"
    object_storage_bucket: str = "amesh"
    object_storage_access_key: SecretStr = SecretStr("minio")
    object_storage_secret_key: SecretStr = SecretStr("minio-development-only")
    auth_mode: str = "development"
    amesh_admin_token: SecretStr = SecretStr("development-token")
    amesh_token_pepper: SecretStr = SecretStr("development-token-pepper")
    amesh_previous_token_pepper: SecretStr | None = None
    tenancy_mode: Literal["single", "multi"] = "single"
    single_tenant_slug: str = "default"
    worker_group: str = "default"
    kubernetes_context: str | None = None
    kubernetes_task_namespace: str = "amesh-tasks"
    worker_poll_seconds: float = Field(default=5.0, gt=0)
    worker_recovery_grace_seconds: float = Field(default=120.0, ge=0)
    worker_reconciliation_interval_seconds: float = Field(default=60.0, ge=5)
    worker_reconciliation_max_repairs: int = Field(default=10, ge=1, le=100)
    worker_reconciliation_stuck_after_seconds: int = Field(default=300, ge=30, le=86_400)
    service_role: str = Field(default="webserver", min_length=1, max_length=32)
    service_instance_name: str | None = Field(default=None, min_length=1, max_length=256)
    service_failure_zone: str | None = Field(default=None, min_length=1, max_length=256)
    service_heartbeat_seconds: float = Field(default=5.0, ge=1, le=60)
    service_stale_after_seconds: float = Field(default=20.0, ge=2, le=300)
    service_cycle_seconds: float = Field(default=5.0, ge=0.1, le=300)
    product_telemetry_enabled: bool = False
    log_level: str = "INFO"

    @model_validator(mode="after")
    def validate_token_pepper(self) -> Settings:
        pepper = self.amesh_token_pepper.get_secret_value()
        if not pepper:
            raise ValueError("AMESH_TOKEN_PEPPER cannot be empty")
        if self.app_env != "development" and pepper == "development-token-pepper":
            raise ValueError("production requires an externally supplied AMESH_TOKEN_PEPPER")
        if not self.database_url.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use postgresql+asyncpg")
        if self.database_read_replica_url is not None and not (
            self.database_read_replica_url.startswith("postgresql+asyncpg://")
        ):
            raise ValueError("DATABASE_READ_REPLICA_URL must use postgresql+asyncpg")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
