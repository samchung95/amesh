from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import warnings
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from threading import RLock
from typing import Any, Literal, get_args, get_origin

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from amesh.domain.runner import RunnerPolicy

_REDACTED = "[REDACTED]"
_SECRET_REFERENCE = re.compile(r"^secret://([A-Za-z0-9][A-Za-z0-9_.-]{0,127})$")
_RENAMED_SETTINGS = {
    "admin_token": "amesh_admin_token",
    "telemetry_enabled": "product_telemetry_enabled",
}
_SECRET_LOCK = RLock()
_RUNTIME_SECRET_VALUES: tuple[str, ...] = ()


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
    object_storage_backend: Literal["s3", "azure", "gcs"] = "s3"
    object_storage_region: str = "us-east-1"
    object_storage_bucket: str = "amesh"
    object_storage_access_key: SecretStr = SecretStr("minio")
    object_storage_secret_key: SecretStr = SecretStr("minio-development-only")
    object_storage_workload_identity: bool = False
    object_storage_encryption_key_id: str | None = None
    object_storage_proxy_url: str | None = None
    object_storage_ca_file: str | None = None
    object_storage_azure_account_url: str | None = None
    object_storage_azure_account_key: SecretStr | None = None
    object_storage_gcs_project: str | None = None
    object_storage_gcs_endpoint: str | None = None
    object_storage_gcs_credentials_file: str | None = None
    object_storage_consistency_attempts: int = Field(default=5, ge=1, le=20)
    object_storage_consistency_delay_seconds: float = Field(default=0.1, ge=0, le=30)
    object_storage_spool_memory_bytes: int = Field(
        default=8 * 1024 * 1024,
        ge=64 * 1024,
        le=128 * 1024 * 1024,
    )
    object_storage_gc_safety_window_seconds: int = Field(default=86_400, ge=0)
    auth_mode: str = "development"
    auth_policy: Literal["local", "hybrid", "federated-only"] = "local"
    amesh_admin_token: SecretStr = SecretStr("development-token")
    amesh_token_pepper: SecretStr = SecretStr("development-token-pepper")
    amesh_previous_token_pepper: SecretStr | None = None
    auth_session_idle_seconds: int = Field(default=1_800, ge=60, le=86_400)
    auth_session_absolute_seconds: int = Field(default=43_200, ge=300, le=2_592_000)
    auth_session_rotation_seconds: int = Field(default=900, ge=30, le=86_400)
    auth_session_overlap_seconds: int = Field(default=30, ge=0, le=300)
    auth_login_rate_limit_per_minute: int = Field(default=30, ge=1, le=10_000)
    auth_login_max_failures: int = Field(default=5, ge=2, le=100)
    auth_login_lock_seconds: int = Field(default=900, ge=30, le=86_400)
    tenancy_mode: Literal["single", "multi"] = "single"
    single_tenant_slug: str = "default"
    worker_group: str = "default"
    kubernetes_context: str | None = None
    kubernetes_task_namespace: str = "amesh-tasks"
    execution_runner_mode: Literal["local", "kubernetes"] = "kubernetes"
    runner_policies: tuple[RunnerPolicy, ...] = ()
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
    plugin_trust_mode: Literal["development", "signed-only"] = "signed-only"
    network_public_exposure: bool = False
    network_tls_terminated: bool = False
    product_telemetry_enabled: bool = Field(
        default=False,
        json_schema_extra={"reloadable": True},
    )
    product_update_checks_enabled: bool = Field(
        default=False,
        json_schema_extra={"reloadable": True},
    )
    log_level: str = Field(default="INFO", json_schema_extra={"reloadable": True})

    @model_validator(mode="after")
    def validate_token_pepper(self) -> Settings:
        pepper = self.amesh_token_pepper.get_secret_value()
        if not pepper:
            raise ValueError("AMESH_TOKEN_PEPPER cannot be empty")
        if self.app_env != "development" and pepper == "development-token-pepper":
            raise ValueError("production requires an externally supplied AMESH_TOKEN_PEPPER")
        if self.app_env != "development" and self.auth_mode == "development":
            raise ValueError("production cannot use development authentication")
        if (
            self.app_env != "development"
            and self.object_storage_backend == "s3"
            and not self.object_storage_workload_identity
            and self.object_storage_secret_key.get_secret_value() == "minio-development-only"
        ):
            raise ValueError("production requires external object-storage credentials or identity")
        if (
            self.app_env != "development"
            and self.network_public_exposure
            and not self.network_tls_terminated
        ):
            raise ValueError("public production exposure requires trusted TLS termination")
        if self.auth_session_idle_seconds > self.auth_session_absolute_seconds:
            raise ValueError(
                "AUTH_SESSION_IDLE_SECONDS cannot exceed the absolute session lifetime"
            )
        if self.auth_session_rotation_seconds > self.auth_session_absolute_seconds:
            raise ValueError(
                "AUTH_SESSION_ROTATION_SECONDS cannot exceed the absolute session lifetime"
            )
        if not self.database_url.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use postgresql+asyncpg")
        if self.database_read_replica_url is not None and not (
            self.database_read_replica_url.startswith("postgresql+asyncpg://")
        ):
            raise ValueError("DATABASE_READ_REPLICA_URL must use postgresql+asyncpg")
        if self.object_storage_backend == "azure" and self.object_storage_azure_account_url is None:
            raise ValueError("OBJECT_STORAGE_AZURE_ACCOUNT_URL is required for the Azure backend")
        if (
            self.object_storage_backend == "gcs"
            and not self.object_storage_workload_identity
            and self.object_storage_gcs_credentials_file is None
        ):
            raise ValueError(
                "GCS requires workload identity or OBJECT_STORAGE_GCS_CREDENTIALS_FILE"
            )
        if self.log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR or CRITICAL")
        return self


class ConfigurationLoadError(ValueError):
    """Raised with a secret-free summary when a configuration source is invalid."""


class NonReloadableConfigurationChanged(ConfigurationLoadError):
    """Raised when a reload attempts to change a restart-required setting."""

    def __init__(self, fields: Sequence[str]) -> None:
        self.fields = tuple(sorted(fields))
        super().__init__(f"restart-required settings changed: {', '.join(self.fields)}")


class ConfigurationEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    value: Any
    source: str
    reloadable: bool
    secret: bool


class ConfigurationSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: int = 1
    version: int = Field(ge=1)
    fingerprint: str
    loaded_at: datetime
    precedence: tuple[str, ...] = (
        "defaults",
        "ordered configuration files",
        "environment variables",
        "command-line --set overrides",
    )
    entries: tuple[ConfigurationEntry, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class LoadedConfiguration:
    settings: Settings
    provenance: Mapping[str, str]
    warnings: tuple[str, ...]
    loaded_at: datetime

    def snapshot(self, version: int) -> ConfigurationSnapshot:
        dumped = self.settings.model_dump(mode="json")
        entries = tuple(
            ConfigurationEntry(
                name=name,
                value=_REDACTED if _field_is_secret(name) else dumped[name],
                source=self.provenance[name],
                reloadable=_field_is_reloadable(name),
                secret=_field_is_secret(name),
            )
            for name in sorted(Settings.model_fields)
        )
        fingerprint_payload = [
            {
                "name": entry.name,
                "value": entry.value,
                "source": entry.source,
                "reloadable": entry.reloadable,
            }
            for entry in entries
        ]
        fingerprint = hashlib.sha256(
            json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return ConfigurationSnapshot(
            version=version,
            fingerprint=fingerprint,
            loaded_at=self.loaded_at,
            entries=entries,
            warnings=self.warnings,
        )


ConfigurationLoader = Callable[[], LoadedConfiguration]


class ConfigurationManager:
    """Atomically publishes fully validated process-configuration snapshots."""

    def __init__(self, loader: ConfigurationLoader) -> None:
        self._loader = loader
        self._loaded = loader()
        self._version = 1
        self._lock = RLock()

    @property
    def settings(self) -> Settings:
        with self._lock:
            return self._loaded.settings

    def snapshot(self) -> ConfigurationSnapshot:
        with self._lock:
            return self._loaded.snapshot(self._version)

    def reload(self) -> ConfigurationSnapshot:
        candidate = self._loader()
        with self._lock:
            current_values = self._loaded.settings.model_dump()
            candidate_values = candidate.settings.model_dump()
            changed = {
                name
                for name in Settings.model_fields
                if current_values[name] != candidate_values[name]
            }
            blocked = changed - reloadable_setting_names()
            if blocked:
                _publish_runtime_secrets(self._loaded.settings)
                raise NonReloadableConfigurationChanged(tuple(blocked))
            if changed:
                self._loaded = candidate
                self._version += 1
            return self._loaded.snapshot(self._version)


def _annotation_contains_secret(annotation: object) -> bool:
    if annotation is SecretStr:
        return True
    origin = get_origin(annotation)
    return origin is not None and any(
        _annotation_contains_secret(arg) for arg in get_args(annotation)
    )


def _field_is_secret(name: str) -> bool:
    return _annotation_contains_secret(Settings.model_fields[name].annotation)


def _field_is_reloadable(name: str) -> bool:
    metadata = Settings.model_fields[name].json_schema_extra or {}
    return bool(metadata.get("reloadable")) if isinstance(metadata, dict) else False


def reloadable_setting_names() -> frozenset[str]:
    return frozenset(name for name in Settings.model_fields if _field_is_reloadable(name))


def security_baseline_findings(settings: Settings) -> tuple[str, ...]:
    findings: list[str] = []
    if settings.app_env != "development" and settings.auth_mode == "development":
        findings.append("CRITICAL: development authentication is enabled")
    if (
        settings.app_env != "development"
        and settings.amesh_token_pepper.get_secret_value() == "development-token-pepper"
    ):
        findings.append("CRITICAL: development token pepper is configured")
    if settings.app_env != "development" and settings.plugin_trust_mode != "signed-only":
        findings.append("CRITICAL: unsigned plugins are permitted")
    if (
        settings.app_env != "development"
        and settings.network_public_exposure
        and not settings.network_tls_terminated
    ):
        findings.append("CRITICAL: public exposure lacks trusted TLS termination")
    return tuple(findings)


def _default_values() -> dict[str, object]:
    values: dict[str, object] = {}
    for name, field in Settings.model_fields.items():
        values[name] = deepcopy(field.get_default(call_default_factory=True))
    return values


def _normalized_name(name: str) -> str:
    return name.strip().replace("-", "_").lower()


def _migrate_names(
    values: Mapping[str, object],
    *,
    source: str,
    notices: list[str],
) -> dict[str, object]:
    normalized = {_normalized_name(str(name)): value for name, value in values.items()}
    for old, new in _RENAMED_SETTINGS.items():
        if old not in normalized:
            continue
        notice = f"{old.upper()} is deprecated; migrated to {new.upper()}"
        notices.append(notice)
        warnings.warn(f"{source}: {notice}", DeprecationWarning, stacklevel=3)
        if new not in normalized:
            normalized[new] = normalized[old]
        del normalized[old]
    return normalized


def _load_file(path: Path) -> Mapping[str, object]:
    if not path.is_file():
        raise ConfigurationLoadError(f"configuration file unavailable: {path}")
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content) if path.suffix.lower() == ".json" else yaml.safe_load(content)
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ConfigurationLoadError(f"configuration file is invalid: {path}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigurationLoadError(f"configuration file root must be a mapping: {path}")
    return {str(key): value for key, value in data.items()}


def _parse_cli(argv: Sequence[str]) -> tuple[tuple[Path, ...], dict[str, str]]:
    files: list[Path] = []
    overrides: dict[str, str] = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--config":
            if index + 1 >= len(argv):
                raise ConfigurationLoadError("--config requires a file path")
            files.append(Path(argv[index + 1]))
            index += 2
            continue
        if token.startswith("--config="):
            files.append(Path(token.split("=", 1)[1]))
        elif token == "--set":
            if index + 1 >= len(argv):
                raise ConfigurationLoadError("--set requires NAME=VALUE")
            _store_cli_override(overrides, argv[index + 1])
            index += 2
            continue
        elif token.startswith("--set="):
            _store_cli_override(overrides, token.split("=", 1)[1])
        index += 1
    return tuple(files), overrides


def _store_cli_override(overrides: dict[str, str], assignment: str) -> None:
    name, separator, value = assignment.partition("=")
    if not separator or not name.strip():
        raise ConfigurationLoadError("--set requires NAME=VALUE")
    overrides[name] = value


def _environment_values(environment: Mapping[str, str]) -> dict[str, str]:
    casefolded = {key.casefold(): value for key, value in environment.items()}
    names = set(Settings.model_fields) | set(_RENAMED_SETTINGS)
    return {name: casefolded[name.casefold()] for name in names if name.casefold() in casefolded}


def _secret_directory(
    environment: Mapping[str, str],
    explicit: Path | None,
) -> Path | None:
    if explicit is not None:
        return explicit
    value = next(
        (value for key, value in environment.items() if key.casefold() == "amesh_secrets_dir"),
        None,
    )
    return Path(value) if value else None


def _resolve_secret_references(
    values: dict[str, object],
    provenance: dict[str, str],
    secret_directory: Path | None,
) -> None:
    for name, value in tuple(values.items()):
        if not isinstance(value, str) or not value.startswith("secret://"):
            continue
        match = _SECRET_REFERENCE.fullmatch(value)
        if match is None or not _field_is_secret(name):
            raise ConfigurationLoadError(f"invalid secret reference for {name.upper()}")
        if secret_directory is None:
            raise ConfigurationLoadError(
                f"AMESH_SECRETS_DIR is required for secret reference {name.upper()}"
            )
        secret_path = secret_directory / match.group(1)
        try:
            secret = secret_path.read_text(encoding="utf-8").rstrip("\r\n")
        except (OSError, UnicodeError) as exc:
            raise ConfigurationLoadError(
                f"secret reference unavailable for {name.upper()}"
            ) from exc
        if not secret:
            raise ConfigurationLoadError(f"secret reference is empty for {name.upper()}")
        values[name] = secret
        provenance[name] = f"{provenance[name]}+secret:{match.group(1)}"


def _publish_runtime_secrets(settings: Settings) -> None:
    values = tuple(
        sorted(
            {
                secret
                for name in Settings.model_fields
                if _field_is_secret(name)
                for secret in [_secret_value(getattr(settings, name))]
                if secret
            },
            key=len,
            reverse=True,
        )
    )
    global _RUNTIME_SECRET_VALUES
    with _SECRET_LOCK:
        _RUNTIME_SECRET_VALUES = values


def _secret_value(value: object) -> str | None:
    if isinstance(value, SecretStr):
        return value.get_secret_value()
    return None


def redact_runtime_text(value: str) -> str:
    with _SECRET_LOCK:
        secrets_to_redact = _RUNTIME_SECRET_VALUES
    for secret in secrets_to_redact:
        value = value.replace(secret, _REDACTED)
    return value


def load_configuration(
    *,
    config_files: Sequence[Path] | None = None,
    environment: Mapping[str, str] | None = None,
    argv: Sequence[str] = (),
    secrets_dir: Path | None = None,
) -> LoadedConfiguration:
    environment = os.environ if environment is None else environment
    cli_files, cli_overrides = _parse_cli(argv)
    configured_paths = config_files
    if configured_paths is None:
        configured = next(
            (value for key, value in environment.items() if key.casefold() == "amesh_config_files"),
            "",
        )
        configured_paths = tuple(Path(value) for value in configured.split(os.pathsep) if value)
    paths = (*configured_paths, *cli_files)
    values = _default_values()
    provenance = {name: "default" for name in Settings.model_fields}
    notices: list[str] = []

    def merge(source_values: Mapping[str, object], source: str, *, strict: bool) -> None:
        migrated = _migrate_names(source_values, source=source, notices=notices)
        unknown = sorted(set(migrated) - set(Settings.model_fields))
        if strict and unknown:
            raise ConfigurationLoadError(
                f"unknown configuration setting(s) in {source}: {', '.join(unknown)}"
            )
        for name, value in migrated.items():
            if name in Settings.model_fields:
                values[name] = value
                provenance[name] = source

    for path in paths:
        merge(_load_file(path), f"file:{path}", strict=True)
    merge(_environment_values(environment), "environment", strict=False)
    merge(cli_overrides, "command-line", strict=True)
    _resolve_secret_references(values, provenance, _secret_directory(environment, secrets_dir))
    try:
        settings = Settings.model_validate(values)
    except ValidationError as exc:
        fields = sorted(
            {
                str(error["loc"][0]) if error["loc"] else "configuration"
                for error in exc.errors(include_input=False)
            }
        )
        raise ConfigurationLoadError(
            f"configuration validation failed for: {', '.join(fields)}"
        ) from None
    _publish_runtime_secrets(settings)
    return LoadedConfiguration(
        settings=settings,
        provenance=provenance,
        warnings=tuple(dict.fromkeys(notices)),
        loaded_at=datetime.now(UTC),
    )


@lru_cache
def get_configuration_manager() -> ConfigurationManager:
    return ConfigurationManager(lambda: load_configuration(argv=sys.argv[1:]))


def get_settings() -> Settings:
    return get_configuration_manager().settings
