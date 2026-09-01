from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import sys
import tempfile
import warnings
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from threading import RLock
from typing import Any, Literal, get_args, get_origin
from urllib.parse import urlsplit

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from amesh.domain.runner import DockerImagePolicy, KubernetesRunnerProfile, RunnerPolicy
from amesh.domain.scripts import ScriptTaskPolicy

_REDACTED = "[REDACTED]"
_SECRET_REFERENCE = re.compile(r"^secret://([A-Za-z0-9][A-Za-z0-9_.-]{0,127})$")
_RENAMED_SETTINGS = {
    "admin_token": "amesh_admin_token",
    "telemetry_enabled": "product_telemetry_enabled",
}
_SECRET_LOCK = RLock()
_RUNTIME_SECRET_VALUES: tuple[str, ...] = ()
_SERVICE_ROLES = frozenset(
    {"webserver", "executor", "scheduler", "worker", "indexer", "maintenance"}
)


class TrustedPluginApproval(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(pattern=r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$", max_length=255)
    version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
            r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
            r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
        )
    )
    content_digest: str = Field(
        alias="contentDigest",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )


class IsolatedPluginServiceConfig(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(pattern=r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$", max_length=255)
    version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
            r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
            r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
        )
    )
    content_digest: str = Field(
        alias="contentDigest",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )
    launcher: Literal["local-process"] = "local-process"
    command: tuple[str, ...] = Field(min_length=1)
    environment: dict[str, str] = Field(default_factory=dict)
    platform_apis: tuple[str, ...] = Field(default=(), alias="platformApis")
    startup_timeout_seconds: float = Field(default=10, alias="startupTimeoutSeconds", gt=0)
    heartbeat_timeout_seconds: float = Field(default=5, alias="heartbeatTimeoutSeconds", gt=0)
    wall_time_seconds: float = Field(default=300, alias="wallTimeSeconds", gt=0)
    cancel_grace_seconds: float = Field(default=1, alias="cancelGraceSeconds", ge=0)
    token_ttl_seconds: int = Field(default=600, alias="tokenTtlSeconds", ge=30, le=3600)
    max_output_bytes: int = Field(
        default=8 * 1024 * 1024,
        alias="maxOutputBytes",
        ge=1024,
        le=128 * 1024 * 1024,
    )
    memory_bytes: int | None = Field(default=None, alias="memoryBytes", ge=4 * 1024 * 1024)
    cpu_seconds: float | None = Field(default=None, alias="cpuSeconds", gt=0)
    max_concurrency: int = Field(default=1, alias="maxConcurrency", ge=1, le=128)

    @field_validator("command")
    @classmethod
    def validate_command(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item or "\x00" in item for item in value):
            raise ValueError("isolated plugin command entries must be non-empty and NUL-free")
        return value


class IdentityGroupMapping(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    external: str = Field(min_length=1, max_length=512)
    platform_group: str = Field(
        alias="platformGroup",
        pattern=r"^[a-z0-9][a-z0-9._-]{0,127}$",
    )


class IdentityProviderConfig(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,127}$")
    kind: Literal["oidc", "saml", "ldap"]
    display_name: str = Field(alias="displayName", min_length=1, max_length=255)
    domains: tuple[str, ...] = ()
    tenants: tuple[str, ...] = ()
    subject_claim: str = Field(default="sub", alias="subjectClaim", min_length=1)
    email_claim: str = Field(default="email", alias="emailClaim", min_length=1)
    display_claim: str = Field(default="name", alias="displayClaim", min_length=1)
    groups_claim: str = Field(default="groups", alias="groupsClaim", min_length=1)
    group_mappings: tuple[IdentityGroupMapping, ...] = Field(
        default=(),
        alias="groupMappings",
    )
    default_tenant: str | None = Field(default=None, alias="defaultTenant")
    default_role: str | None = Field(default=None, alias="defaultRole")
    issuer_url: str | None = Field(default=None, alias="issuerUrl")
    client_id: str | None = Field(default=None, alias="clientId")
    client_secret_file: str | None = Field(default=None, alias="clientSecretFile")
    redirect_uri: str | None = Field(default=None, alias="redirectUri")
    scopes: tuple[str, ...] = ("openid", "profile", "email")
    clock_skew_seconds: int = Field(default=60, alias="clockSkewSeconds", ge=0, le=300)
    idp_entity_id: str | None = Field(default=None, alias="idpEntityId")
    sso_url: str | None = Field(default=None, alias="ssoUrl")
    slo_url: str | None = Field(default=None, alias="sloUrl")
    idp_signing_cert_files: tuple[str, ...] = Field(
        default=(),
        alias="idpSigningCertFiles",
    )
    sp_entity_id: str | None = Field(default=None, alias="spEntityId")
    acs_url: str | None = Field(default=None, alias="acsUrl")
    sp_cert_file: str | None = Field(default=None, alias="spCertFile")
    sp_private_key_file: str | None = Field(default=None, alias="spPrivateKeyFile")
    next_sp_cert_file: str | None = Field(default=None, alias="nextSpCertFile")
    ldap_host: str | None = Field(default=None, alias="ldapHost")
    ldap_port: int = Field(default=636, alias="ldapPort", ge=1, le=65535)
    ldap_start_tls: bool = Field(default=False, alias="ldapStartTls")
    ldap_ca_file: str | None = Field(default=None, alias="ldapCaFile")
    ldap_user_dn_template: str | None = Field(default=None, alias="ldapUserDnTemplate")
    ldap_group_search_base: str | None = Field(default=None, alias="ldapGroupSearchBase")
    ldap_group_filter: str = Field(
        default="(member={user_dn})",
        alias="ldapGroupFilter",
        min_length=1,
    )
    ldap_group_name_attribute: str = Field(
        default="cn",
        alias="ldapGroupNameAttribute",
        min_length=1,
    )

    @field_validator("domains")
    @classmethod
    def normalize_domains(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip().lower() for item in value)
        if any(not item or "." not in item for item in normalized):
            raise ValueError("identity provider domains must be DNS suffixes")
        return normalized

    @model_validator(mode="after")
    def validate_protocol_configuration(self) -> IdentityProviderConfig:
        if self.kind == "oidc":
            oidc_required = (
                self.issuer_url,
                self.client_id,
                self.client_secret_file,
                self.redirect_uri,
            )
            if any(item is None for item in oidc_required):
                raise ValueError(
                    "OIDC providers require issuerUrl, clientId, clientSecretFile and redirectUri"
                )
        elif self.kind == "saml":
            saml_required = (
                self.idp_entity_id,
                self.sso_url,
                self.sp_entity_id,
                self.acs_url,
                self.sp_cert_file,
                self.sp_private_key_file,
            )
            if any(item is None for item in saml_required) or not self.idp_signing_cert_files:
                raise ValueError(
                    "SAML providers require IdP/SP endpoints, SP key pair and signing certificates"
                )
        elif (
            self.ldap_host is None
            or self.ldap_ca_file is None
            or self.ldap_user_dn_template is None
        ):
            raise ValueError("LDAP providers require ldapHost, ldapCaFile and ldapUserDnTemplate")
        if self.default_role is not None and self.default_tenant is None:
            raise ValueError("identity provider defaultRole requires defaultTenant")
        return self


class ScimProviderConfig(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,127}$")
    tenant: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,127}$")
    role: str = Field(default="viewer", pattern=r"^[a-z0-9][a-z0-9._-]{0,127}$")
    token_file: str = Field(alias="tokenFile", min_length=1)


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
    object_storage_backend: Literal["local", "s3", "azure", "gcs"] = "s3"
    object_storage_local_root: str = Field(
        default_factory=lambda: str(Path.home() / ".amesh" / "storage"),
        min_length=1,
        max_length=4096,
    )
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
    identity_providers: tuple[IdentityProviderConfig, ...] = ()
    scim_providers: tuple[ScimProviderConfig, ...] = ()
    tenancy_mode: Literal["single", "multi"] = "single"
    single_tenant_slug: str = "default"
    worker_group: str = "default"
    kubernetes_context: str | None = None
    kubernetes_task_namespace: str = "amesh-tasks"
    kubernetes_runner_profiles: tuple[KubernetesRunnerProfile, ...] = ()
    execution_runner_mode: Literal["local", "docker", "kubernetes"] = "kubernetes"
    local_process_runner_enabled: bool | None = None
    docker_runner_enabled: bool = False
    docker_runner_endpoint: str | None = None
    docker_image_policy: DockerImagePolicy = Field(default_factory=DockerImagePolicy)
    docker_signature_verification_command: tuple[str, ...] = ()
    docker_vulnerability_verification_command: tuple[str, ...] = ()
    runner_policies: tuple[RunnerPolicy, ...] = ()
    script_task_policy: ScriptTaskPolicy = Field(default_factory=ScriptTaskPolicy)
    worker_poll_seconds: float = Field(default=5.0, gt=0)
    worker_recovery_grace_seconds: float = Field(default=120.0, ge=0)
    worker_recovery_batch_size: int = Field(default=100, ge=1, le=1000)
    worker_reconciliation_interval_seconds: float = Field(default=60.0, ge=5)
    worker_reconciliation_max_repairs: int = Field(default=10, ge=1, le=100)
    worker_reconciliation_stuck_after_seconds: int = Field(default=300, ge=30, le=86_400)
    core_http_allowed_private_hosts: tuple[str, ...] = ()
    core_http_max_response_bytes: int = Field(default=10 * 1024 * 1024, ge=1, le=128 * 1024 * 1024)
    core_http_max_pages: int = Field(default=100, ge=1, le=10_000)
    core_http_max_redirects: int = Field(default=5, ge=0, le=20)
    model_continuation_key_id: str = Field(default="primary", min_length=1, max_length=255)
    model_continuation_encryption_key: SecretStr | None = None
    model_continuation_previous_key_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    model_continuation_previous_encryption_key: SecretStr | None = None
    agent_session_pi_worker_command: tuple[str, ...] = Field(
        default=("node", "harnesses/pi/src/worker.mjs"),
        min_length=2,
        max_length=16,
    )
    agent_session_harness: str = Field(default="pi", min_length=1, max_length=64)
    agent_session_max_frame_bytes: int = Field(default=1_048_576, ge=4_096, le=16 * 1024 * 1024)
    model_engine_state_root: str = Field(
        default_factory=lambda: str(Path.home() / ".amesh" / "model-engines"),
        min_length=1,
        max_length=4096,
    )
    model_engine_codex_command: tuple[str, ...] = Field(
        default=("codex", "app-server", "--stdio"),
        min_length=1,
        max_length=16,
    )
    model_engine_copilot_command: tuple[str, ...] = Field(
        default=("copilot",),
        min_length=1,
        max_length=16,
    )
    model_engine_max_frame_bytes: int = Field(
        default=1_048_576,
        ge=4_096,
        le=16 * 1024 * 1024,
    )
    model_engine_timeout_seconds: float = Field(default=120.0, gt=0, le=3_600)
    model_engine_cancel_grace_seconds: float = Field(default=2.0, gt=0, le=60)
    webhook_signing_key: SecretStr = Field(
        default=SecretStr("amesh-webhook-development-signing-key"), min_length=32
    )
    webhook_delivery_timeout_seconds: float = Field(default=10.0, gt=0, le=300)
    webhook_delivery_batch_size: int = Field(default=100, ge=1, le=1_000)
    service_role: str = Field(default="webserver", min_length=1, max_length=32)
    service_enabled_roles: tuple[str, ...] = ()
    service_instance_name: str | None = Field(default=None, min_length=1, max_length=256)
    service_failure_zone: str | None = Field(default=None, min_length=1, max_length=256)
    service_heartbeat_seconds: float = Field(default=5.0, ge=1, le=60)
    service_stale_after_seconds: float = Field(default=20.0, ge=2, le=300)
    service_cycle_seconds: float = Field(default=5.0, ge=0.1, le=300)
    compact_shutdown_grace_seconds: float = Field(default=30.0, ge=1, le=300)
    preflight_timeout_seconds: float = Field(default=10.0, gt=0, le=120)
    readiness_check_storage: bool = False
    plugin_trust_mode: Literal["development", "signed-only"] = "signed-only"
    plugin_directories: tuple[str, ...] = ()
    plugin_registries: tuple[str, ...] = ()
    plugin_install_root: str = Field(
        default_factory=lambda: str(Path(tempfile.gettempdir()) / "amesh-plugins"),
        min_length=1,
        max_length=4096,
    )
    plugin_registry_timeout_seconds: float = Field(default=10.0, gt=0, le=300)
    plugin_registry_root: str = Field(
        default_factory=lambda: str(Path(tempfile.gettempdir()) / "amesh-plugin-registry"),
        min_length=1,
        max_length=4096,
    )
    plugin_registry_signing_key_id: str = Field(default="local", min_length=1, max_length=255)
    plugin_registry_signing_key: SecretStr = SecretStr("amesh-registry-development-signing-key")
    plugin_registry_verification_keys: dict[str, SecretStr] = Field(default_factory=dict)
    plugin_registry_allowed_origins: tuple[str, ...] = ()
    plugin_registry_mirrors: dict[str, str] = Field(default_factory=dict)
    plugin_registry_proxy_url: str | None = Field(default=None, max_length=2048)
    plugin_registry_offline: bool = False
    trusted_plugin_approvals: tuple[TrustedPluginApproval, ...] = ()
    trusted_plugin_callback_timeout_seconds: float = Field(default=30.0, gt=0, le=3600)
    trusted_plugin_lifecycle_timeout_seconds: float = Field(default=10.0, gt=0, le=300)
    trusted_plugin_failure_threshold: int = Field(default=5, ge=1, le=100)
    trusted_plugin_reset_seconds: float = Field(default=30.0, gt=0, le=3600)
    trusted_plugin_quarantine_threshold: int = Field(default=10, ge=1, le=1000)
    isolated_plugin_services: tuple[IsolatedPluginServiceConfig, ...] = ()
    isolated_plugin_monitor_interval_seconds: float = Field(default=0.05, gt=0, le=5)
    network_public_exposure: bool = False
    network_tls_terminated: bool = False
    network_inbound_tls_mode: Literal["disabled", "direct", "trusted-proxy"] = "disabled"
    network_tls_certificate_file: str | None = Field(default=None, max_length=4096)
    network_tls_private_key_file: str | None = Field(default=None, max_length=4096)
    network_tls_client_ca_file: str | None = Field(default=None, max_length=4096)
    network_tls_client_auth: Literal["none", "optional", "required"] = "none"
    network_tls_minimum_version: Literal["TLSv1.2", "TLSv1.3"] = "TLSv1.2"
    network_tls_ciphers: str = Field(
        default="ECDHE+AESGCM:ECDHE+CHACHA20",
        min_length=1,
        max_length=2048,
    )
    network_trusted_proxy_ranges: tuple[str, ...] = ()
    network_external_base_url: str | None = Field(default=None, max_length=2048)
    network_http_proxy_url: SecretStr | None = None
    network_https_proxy_url: SecretStr | None = None
    network_no_proxy: tuple[str, ...] = ()
    network_outbound_ca_file: str | None = Field(default=None, max_length=4096)
    network_outbound_client_certificate_file: str | None = Field(default=None, max_length=4096)
    network_outbound_client_key_file: str | None = Field(default=None, max_length=4096)
    network_egress_allowed_hosts: tuple[str, ...] = ("*",)
    network_diagnostic_hosts: tuple[str, ...] = ()
    network_topology: Literal["compact", "split"] = "compact"
    network_private_endpoint: bool = False
    product_telemetry_enabled: bool = Field(
        default=False,
        json_schema_extra={"reloadable": True},
    )
    product_update_checks_enabled: bool = Field(
        default=False,
        json_schema_extra={"reloadable": True},
    )
    log_level: str = Field(default="INFO", json_schema_extra={"reloadable": True})
    log_destination: Literal["stdout", "file", "syslog"] = "stdout"
    log_file_path: str | None = Field(default=None, max_length=4096)
    log_syslog_address: str = Field(default="127.0.0.1:514", min_length=3, max_length=512)
    log_queue_capacity: int = Field(default=10_000, ge=100, le=1_000_000)
    otel_exporter_otlp_endpoint: str | None = Field(default=None, max_length=2048)
    otel_exporter_otlp_headers: dict[str, SecretStr] = Field(default_factory=dict)
    otel_batch_queue_size: int = Field(default=2_048, ge=128, le=65_536)
    otel_batch_size: int = Field(default=512, ge=1, le=8_192)
    otel_export_timeout_seconds: float = Field(default=5, gt=0, le=60)

    @field_validator("docker_image_policy", mode="before")
    @classmethod
    def parse_docker_image_policy(cls, value: object) -> object:
        return json.loads(value) if isinstance(value, str) else value

    @field_validator("model_engine_codex_command", "model_engine_copilot_command")
    @classmethod
    def validate_model_engine_command(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not entry or "\x00" in entry for entry in value):
            raise ValueError("model engine command entries must be non-empty and NUL-free")
        return value

    @field_validator("script_task_policy", mode="before")
    @classmethod
    def parse_script_task_policy(cls, value: object) -> object:
        return json.loads(value) if isinstance(value, str) else value

    @field_validator("kubernetes_runner_profiles", mode="before")
    @classmethod
    def parse_kubernetes_runner_profiles(cls, value: object) -> object:
        return json.loads(value) if isinstance(value, str) else value

    @field_validator(
        "docker_signature_verification_command",
        "docker_vulnerability_verification_command",
        mode="before",
    )
    @classmethod
    def parse_docker_verifier_command(cls, value: object) -> object:
        return json.loads(value) if isinstance(value, str) else value

    @field_validator(
        "plugin_directories",
        "plugin_registries",
        "core_http_allowed_private_hosts",
        "plugin_registry_allowed_origins",
        "plugin_registry_mirrors",
        "plugin_registry_verification_keys",
        "trusted_plugin_approvals",
        "isolated_plugin_services",
        "identity_providers",
        "scim_providers",
        "otel_exporter_otlp_headers",
        "network_trusted_proxy_ranges",
        "network_no_proxy",
        "network_egress_allowed_hosts",
        "network_diagnostic_hosts",
        "service_enabled_roles",
        mode="before",
    )
    @classmethod
    def parse_plugin_sources(cls, value: object) -> object:
        return json.loads(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_token_pepper(self) -> Settings:
        if self.service_role not in _SERVICE_ROLES:
            raise ValueError(f"SERVICE_ROLE must be one of {sorted(_SERVICE_ROLES)}")
        if (self.model_continuation_previous_key_id is None) != (
            self.model_continuation_previous_encryption_key is None
        ):
            raise ValueError(
                "MODEL_CONTINUATION_PREVIOUS_KEY_ID and "
                "MODEL_CONTINUATION_PREVIOUS_ENCRYPTION_KEY must be set together"
            )
        enabled_roles = self.service_enabled_roles or (self.service_role,)
        if len(enabled_roles) != len(set(enabled_roles)):
            raise ValueError("SERVICE_ENABLED_ROLES must contain unique roles")
        unknown_roles = sorted(set(enabled_roles) - _SERVICE_ROLES)
        if unknown_roles:
            raise ValueError(
                f"SERVICE_ENABLED_ROLES contains unknown roles: {', '.join(unknown_roles)}"
            )
        if self.service_role not in enabled_roles:
            raise ValueError("SERVICE_ENABLED_ROLES must include SERVICE_ROLE")
        self.service_enabled_roles = enabled_roles
        pepper = self.amesh_token_pepper.get_secret_value()
        if not pepper:
            raise ValueError("AMESH_TOKEN_PEPPER cannot be empty")
        if self.app_env != "development" and pepper == "development-token-pepper":
            raise ValueError("production requires an externally supplied AMESH_TOKEN_PEPPER")
        if self.app_env != "development" and self.auth_mode == "development":
            raise ValueError("production cannot use development authentication")
        if (
            self.app_env != "development"
            and self.webhook_signing_key.get_secret_value()
            == "amesh-webhook-development-signing-key"
        ):
            raise ValueError("production requires an externally supplied WEBHOOK_SIGNING_KEY")
        if (
            self.app_env != "development"
            and self.object_storage_backend == "s3"
            and not self.object_storage_workload_identity
            and self.object_storage_secret_key.get_secret_value() == "minio-development-only"
        ):
            raise ValueError("production requires external object-storage credentials or identity")
        approval_identities = [
            (item.name, item.version, item.content_digest) for item in self.trusted_plugin_approvals
        ]
        if len(approval_identities) != len(set(approval_identities)):
            raise ValueError("TRUSTED_PLUGIN_APPROVALS must contain unique exact identities")
        isolated_identities = [
            (item.name, item.version, item.content_digest) for item in self.isolated_plugin_services
        ]
        if len(isolated_identities) != len(set(isolated_identities)):
            raise ValueError("ISOLATED_PLUGIN_SERVICES must contain unique exact identities")
        provider_ids = [item.id for item in self.identity_providers]
        scim_ids = [item.id for item in self.scim_providers]
        if len(provider_ids) != len(set(provider_ids)):
            raise ValueError("IDENTITY_PROVIDERS must contain unique provider ids")
        if len(scim_ids) != len(set(scim_ids)):
            raise ValueError("SCIM_PROVIDERS must contain unique provider ids")
        overlap = set(approval_identities).intersection(isolated_identities)
        if overlap:
            raise ValueError("a plugin identity cannot use both trusted and isolated runtime tiers")
        if (
            self.app_env != "development"
            and self.network_public_exposure
            and self.network_inbound_tls_mode == "disabled"
        ):
            raise ValueError("public production exposure requires trusted TLS termination")
        if self.network_inbound_tls_mode == "direct" and (
            self.network_tls_certificate_file is None or self.network_tls_private_key_file is None
        ):
            raise ValueError(
                "direct inbound TLS requires NETWORK_TLS_CERTIFICATE_FILE and "
                "NETWORK_TLS_PRIVATE_KEY_FILE"
            )
        if (
            self.network_inbound_tls_mode == "trusted-proxy"
            and not self.network_trusted_proxy_ranges
        ):
            raise ValueError(
                "trusted-proxy TLS requires at least one NETWORK_TRUSTED_PROXY_RANGES entry"
            )
        if self.network_tls_client_auth != "none":
            if self.network_inbound_tls_mode != "direct":
                raise ValueError("TLS client authentication requires direct inbound TLS")
            if self.network_tls_client_ca_file is None:
                raise ValueError("TLS client authentication requires NETWORK_TLS_CLIENT_CA_FILE")
        if (self.network_outbound_client_certificate_file is None) != (
            self.network_outbound_client_key_file is None
        ):
            raise ValueError("outbound mTLS requires both client certificate and private key files")
        for value in self.network_trusted_proxy_ranges:
            try:
                ipaddress.ip_network(value, strict=False)
            except ValueError as exc:
                raise ValueError(f"invalid trusted proxy range: {value}") from exc
        for field_name, configured_url in (
            ("NETWORK_EXTERNAL_BASE_URL", self.network_external_base_url),
            (
                "NETWORK_HTTP_PROXY_URL",
                self.network_http_proxy_url.get_secret_value()
                if self.network_http_proxy_url is not None
                else None,
            ),
            (
                "NETWORK_HTTPS_PROXY_URL",
                self.network_https_proxy_url.get_secret_value()
                if self.network_https_proxy_url is not None
                else None,
            ),
        ):
            if configured_url is None:
                continue
            parsed = urlsplit(configured_url)
            allowed_schemes = (
                {"https"}
                if field_name == "NETWORK_EXTERNAL_BASE_URL"
                else {
                    "http",
                    "https",
                }
            )
            if parsed.scheme not in allowed_schemes or not parsed.hostname:
                raise ValueError(f"{field_name} must be an absolute {sorted(allowed_schemes)} URL")
            if field_name == "NETWORK_EXTERNAL_BASE_URL" and (
                parsed.username is not None or parsed.query or parsed.fragment
            ):
                raise ValueError(
                    "NETWORK_EXTERNAL_BASE_URL cannot contain credentials or query data"
                )
        if not self.network_egress_allowed_hosts:
            raise ValueError("NETWORK_EGRESS_ALLOWED_HOSTS cannot be empty")
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
        if self.log_destination == "file" and self.log_file_path is None:
            raise ValueError("LOG_FILE_PATH is required when LOG_DESTINATION=file")
        if self.otel_batch_size > self.otel_batch_queue_size:
            raise ValueError("OTEL_BATCH_SIZE cannot exceed OTEL_BATCH_QUEUE_SIZE")
        return self

    @property
    def is_local_process_runner_enabled(self) -> bool:
        if self.local_process_runner_enabled is not None:
            return self.local_process_runner_enabled
        return self.tenancy_mode == "single"

    @property
    def effective_kubernetes_runner_profiles(self) -> tuple[KubernetesRunnerProfile, ...]:
        if self.kubernetes_runner_profiles:
            return self.kubernetes_runner_profiles
        return (
            KubernetesRunnerProfile(
                name="default",
                context=self.kubernetes_context,
                namespace=self.kubernetes_task_namespace,
            ),
        )


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
        and settings.plugin_registry_signing_key.get_secret_value()
        == "amesh-registry-development-signing-key"
    ):
        findings.append("CRITICAL: development plugin registry signing key is configured")
    if (
        settings.app_env != "development"
        and settings.webhook_signing_key.get_secret_value()
        == "amesh-webhook-development-signing-key"
    ):
        findings.append("CRITICAL: development webhook signing key is configured")
    if (
        settings.app_env != "development"
        and settings.network_public_exposure
        and settings.network_inbound_tls_mode == "disabled"
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
