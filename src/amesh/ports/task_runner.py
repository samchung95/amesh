from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator

from amesh.domain.runner import (
    RunnerExtension,
    RunnerId,
    RunnerNetworkAccess,
    RunnerNetworkPolicy,
    RunnerSecurityPolicy,
)
from amesh.observability import current_trace_context, normalize_trace_context

_REDACTED = "[REDACTED]"


def redact_runner_text(value: str, secret_values: Iterable[str]) -> str:
    """Redact secret fragments from runner output before it reaches a sink."""

    redacted = value
    for secret in sorted({item for item in secret_values if item}, key=len, reverse=True):
        redacted = redacted.replace(secret, _REDACTED)
    return redacted


def redact_runner_payload(value: Any, secret_values: Iterable[str]) -> Any:
    """Redact runner payload strings and secret-bearing compound field names."""

    secrets = tuple(secret_values)
    if isinstance(value, Mapping):
        return {
            key: _REDACTED if _runner_secret_field(key) else redact_runner_payload(item, secrets)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_runner_payload(item, secrets) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_runner_payload(item, secrets) for item in value)
    if isinstance(value, str):
        return redact_runner_text(value, secrets)
    return value


def _runner_secret_field(value: object) -> bool:
    normalized = "".join(character for character in str(value).casefold() if character.isalnum())
    if normalized in {
        "apikey",
        "authorization",
        "credential",
        "credentials",
        "password",
        "secret",
        "secrets",
        "token",
    }:
        return True
    return normalized.startswith(
        ("authorization", "credential", "password", "secret")
    ) or normalized.endswith(("apikey", "credential", "password", "secret", "token"))


class RunnerOutputRedactor:
    """Redact streamed output without leaking secrets split across chunks."""

    def __init__(self, secret_values: Iterable[str]) -> None:
        self._secrets = tuple(
            sorted({item for item in secret_values if item}, key=len, reverse=True)
        )
        self._pending = ""
        self._retained_chars = max((len(item) for item in self._secrets), default=1) - 1

    def feed(self, value: str) -> str:
        if not self._secrets:
            return value
        self._pending += value
        if len(self._pending) <= self._retained_chars:
            return ""
        boundary = len(self._pending) - self._retained_chars
        for secret in self._secrets:
            for start in range(max(0, boundary - len(secret) + 1), boundary):
                overlap = self._pending[start:boundary]
                if overlap and secret.startswith(overlap):
                    boundary = start
                    break
        emitted, self._pending = self._pending[:boundary], self._pending[boundary:]
        return redact_runner_text(emitted, self._secrets)

    def flush(self) -> str:
        emitted = self._pending
        self._pending = ""
        return redact_runner_text(emitted, self._secrets)


class ScopedRunnerCredential(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    scope: str = Field(min_length=1, max_length=128)
    environment_variable: str = Field(
        alias="environmentVariable",
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    )
    value: SecretStr = Field(repr=False)


class RunnerRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    contract_version: Literal["1.0"] = Field(default="1.0", alias="contractVersion")
    tenant_id: str
    namespace: str = "default"
    worker_group: str | None = None
    execution_id: str
    task_run_id: str
    attempt_id: str
    fencing_token: int = Field(ge=1)
    command: list[str] = Field(default_factory=list)
    image: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)
    credentials: tuple[ScopedRunnerCredential, ...] = ()
    input_files: dict[str, str] = Field(default_factory=dict)
    working_directory: str | None = None
    standard_input: str | None = Field(default=None, alias="standardInput")
    resource_limits: dict[str, Any] = Field(default_factory=dict)
    network_policy: RunnerNetworkPolicy = Field(default_factory=RunnerNetworkPolicy)
    security_policy: RunnerSecurityPolicy = Field(default_factory=RunnerSecurityPolicy)
    extension: RunnerExtension | None = None
    timeout_seconds: float | None = Field(default=None, gt=0)
    cancel_grace_seconds: float = Field(default=1, ge=0)
    output_limit_bytes: int | None = Field(default=None, alias="outputLimitBytes", ge=1)
    trace_context: dict[str, str] = Field(
        default_factory=current_trace_context,
        alias="traceContext",
    )

    @field_validator("trace_context", mode="before")
    @classmethod
    def validate_trace_context(cls, value: object) -> dict[str, str]:
        return normalize_trace_context(value)

    @model_validator(mode="after")
    def validate_execution_payload(self) -> RunnerRequest:
        if not self.command and self.image is None:
            raise ValueError("runner request requires a command or image")
        credential_names = [item.environment_variable for item in self.credentials]
        if len(credential_names) != len(set(credential_names)):
            raise ValueError("runner credential environment variables must be unique")
        overlap = set(credential_names).intersection(self.environment)
        if overlap:
            raise ValueError(
                "runner credentials conflict with environment variables: "
                + ", ".join(sorted(overlap))
            )
        return self


class RunnerLogStream(StrEnum):
    STDOUT = "STDOUT"
    STDERR = "STDERR"
    SYSTEM = "SYSTEM"


class RunnerLog(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    sequence: int = Field(ge=0)
    stream: RunnerLogStream
    level: Literal["INFO", "ERROR"] = "INFO"
    message: str
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="occurredAt",
    )


class RunnerMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)

    duration_seconds: float = Field(default=0, ge=0)
    cpu_seconds: float | None = Field(default=None, ge=0)
    peak_memory_bytes: int | None = Field(default=None, ge=0)


class RunnerDiagnostics(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    runner: RunnerId
    external_id: str | None = Field(default=None, alias="externalId")
    reason: str | None = None
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class RunnerStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class StaleRunnerAttemptError(RuntimeError):
    """Raised when cancellation targets an inactive or superseded runner attempt."""


class UnsupportedRunnerRequest(ValueError):
    def __init__(self, runner: RunnerId, reasons: tuple[str, ...]) -> None:
        self.runner = runner
        self.reasons = reasons
        super().__init__(f"runner {runner.value!r} does not support: {', '.join(reasons)}")


class RunnerCapabilities(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    runner: RunnerId
    contract_versions: tuple[Literal["1.0"], ...] = Field(
        default=("1.0",),
        alias="contractVersions",
    )
    accepts_command: bool = Field(default=True, alias="acceptsCommand")
    requires_command: bool = Field(default=False, alias="requiresCommand")
    accepts_image: bool = Field(default=False, alias="acceptsImage")
    requires_image: bool = Field(default=False, alias="requiresImage")
    supports_files: bool = Field(default=False, alias="supportsFiles")
    supports_working_directory: bool = Field(default=False, alias="supportsWorkingDirectory")
    supports_standard_input: bool = Field(default=False, alias="supportsStandardInput")
    supports_resources: bool = Field(default=False, alias="supportsResources")
    network_access: tuple[RunnerNetworkAccess, ...] = Field(
        default=(RunnerNetworkAccess.INHERIT,),
        alias="networkAccess",
    )
    supports_security_policy: bool = Field(default=False, alias="supportsSecurityPolicy")
    supports_scoped_credentials: bool = Field(default=True, alias="supportsScopedCredentials")
    supports_reconciliation: bool = Field(default=True, alias="supportsReconciliation")
    extension_type: RunnerId = Field(alias="extensionType")
    cancellation_escalation: tuple[str, ...] = Field(alias="cancellationEscalation")
    platforms: tuple[str, ...] = ()
    features: tuple[str, ...] = ()


class RunnerResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    runner: RunnerId
    exit_code: int | None
    signal: int | None = None
    status: RunnerStatus
    logs: tuple[RunnerLog, ...] = ()
    metrics: RunnerMetrics = Field(default_factory=RunnerMetrics)
    outputs: dict[str, Any] = Field(default_factory=dict)
    artifact_uris: list[str] = Field(default_factory=list)
    diagnostics: RunnerDiagnostics


class RunnerReconciliationResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    runner: RunnerId
    cleaned_attempts: tuple[str, ...] = Field(default=(), alias="cleanedAttempts")
    retained_attempts: tuple[str, ...] = Field(default=(), alias="retainedAttempts")


def validate_runner_request(capabilities: RunnerCapabilities, request: RunnerRequest) -> None:
    reasons: list[str] = []
    if request.contract_version not in capabilities.contract_versions:
        reasons.append(f"contract version {request.contract_version}")
    if request.command and not capabilities.accepts_command:
        reasons.append("command")
    if capabilities.requires_command and not request.command:
        reasons.append("missing command")
    if request.image is not None and not capabilities.accepts_image:
        reasons.append("image")
    if capabilities.requires_image and request.image is None:
        reasons.append("missing image")
    if request.input_files and not capabilities.supports_files:
        reasons.append("files")
    if request.working_directory is not None and not capabilities.supports_working_directory:
        reasons.append("working directory")
    if request.standard_input is not None and not capabilities.supports_standard_input:
        reasons.append("standard input")
    if request.resource_limits and not capabilities.supports_resources:
        reasons.append("resource limits")
    if request.network_policy.access not in capabilities.network_access:
        reasons.append(f"network access {request.network_policy.access.value}")
    if not request.security_policy.is_default and not capabilities.supports_security_policy:
        reasons.append("security policy")
    if request.credentials and not capabilities.supports_scoped_credentials:
        reasons.append("scoped credentials")
    if request.extension is not None and request.extension.type is not capabilities.extension_type:
        reasons.append(f"extension type {request.extension.type.value}")
    if reasons:
        raise UnsupportedRunnerRequest(capabilities.runner, tuple(reasons))


class TaskRunner(Protocol):
    @property
    def capabilities(self) -> RunnerCapabilities: ...

    async def run(self, request: RunnerRequest) -> RunnerResult: ...

    async def cancel(self, attempt_id: str, fencing_token: int) -> None: ...

    async def reconcile(
        self,
        active_attempts: Mapping[str, int],
    ) -> RunnerReconciliationResult: ...
