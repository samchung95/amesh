"""Provider-neutral tool discovery, policy and invocation contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID, uuid4

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    StringConstraints,
    field_validator,
    model_validator,
)

from .identity import NamespaceId, NaturalId
from .resources import canonical_hash

TOOL_PROVIDER_CONTRACT_VERSION = "amesh.tool-provider/v1"
ToolName = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$",
        min_length=1,
        max_length=255,
    ),
]
ProviderKey = ToolName


class ToolProviderKind(StrEnum):
    MCP = "mcp"
    PLUGIN = "plugin"


class ToolImpact(StrEnum):
    READ_ONLY = "READ_ONLY"
    IDEMPOTENT_WRITE = "IDEMPOTENT_WRITE"
    HIGH_IMPACT = "HIGH_IMPACT"


class ToolInvocationState(StrEnum):
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    AMBIGUOUS = "AMBIGUOUS"


class ToolProviderRef(BaseModel):
    """Exact provider identity used by discovery, policy and agent pins."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: ToolProviderKind
    key: ProviderKey
    revision: int = Field(ge=1)


class ToolDescriptor(BaseModel):
    """A provider-independent description of one callable tool."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    provider: ToolProviderRef
    name: ToolName
    description: str = Field(default="", max_length=4096)
    input_schema: dict[str, Any] = Field(alias="inputSchema")
    output_schema: dict[str, Any] | None = Field(default=None, alias="outputSchema")
    impact: ToolImpact = ToolImpact.HIGH_IMPACT
    secret_scopes: tuple[NaturalId, ...] = Field(default=(), alias="secretScopes")
    allowed_egress: tuple[str, ...] = Field(default=(), alias="allowedEgress")
    filesystem_read_roots: tuple[str, ...] = Field(default=(), alias="filesystemReadRoots")
    filesystem_write_roots: tuple[str, ...] = Field(default=(), alias="filesystemWriteRoots")

    @field_validator("input_schema", "output_schema")
    @classmethod
    def validate_schema(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        try:
            Draft202012Validator.check_schema(value)
        except SchemaError as exc:
            raise ValueError(f"invalid tool schema: {exc.message}") from exc
        return value

    @field_validator(
        "secret_scopes",
        "allowed_egress",
        "filesystem_read_roots",
        "filesystem_write_roots",
    )
    @classmethod
    def validate_unique_paths(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("tool policy declarations must be unique")
        if any(not item or item.strip() != item for item in value):
            raise ValueError("tool policy declarations must be non-empty and trimmed")
        return value

    @field_validator("allowed_egress")
    @classmethod
    def reject_wildcard_egress(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(item == "*" or "*" in item for item in value):
            raise ValueError("tool egress cannot contain wildcards")
        return value

    @property
    def schema_digest(self) -> str:
        """Digest only the callable schema, preserving existing MCP pin semantics."""

        return "sha256:" + canonical_hash(
            {
                "name": self.name,
                "inputSchema": self.input_schema,
                "outputSchema": self.output_schema,
            }
        )

    @property
    def digest(self) -> str:
        return "sha256:" + canonical_hash(self.model_dump(mode="json", by_alias=True))


class ToolDiscovery(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    contract_version: str = Field(default=TOOL_PROVIDER_CONTRACT_VERSION, alias="contractVersion")
    provider: ToolProviderRef
    tools: tuple[ToolDescriptor, ...]
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_tools(self) -> ToolDiscovery:
        if any(item.provider != self.provider for item in self.tools):
            raise ValueError("discovered tool provider identity does not match the discovery")
        names = tuple(item.name for item in self.tools)
        if len(names) != len(set(names)):
            raise ValueError("discovered tool names must be unique")
        expected = "sha256:" + canonical_hash(
            {
                "provider": self.provider.model_dump(mode="json", by_alias=True),
                "tools": tuple(
                    item.model_dump(mode="json", by_alias=True, exclude_none=True)
                    for item in sorted(self.tools, key=lambda value: value.name)
                ),
            }
        )
        if self.digest != expected:
            raise ValueError("tool discovery digest does not match its contents")
        return self

    def tool(self, name: str) -> ToolDescriptor:
        selected = next((item for item in self.tools if item.name == name), None)
        if selected is None:
            raise PermissionError(f"tool {name!r} is not exposed by provider {self.provider.key!r}")
        return selected

    @classmethod
    def from_tools(
        cls, provider: ToolProviderRef, tools: tuple[ToolDescriptor, ...]
    ) -> ToolDiscovery:
        ordered = tuple(sorted(tools, key=lambda value: value.name))
        digest = "sha256:" + canonical_hash(
            {
                "provider": provider.model_dump(mode="json", by_alias=True),
                "tools": tuple(
                    item.model_dump(mode="json", by_alias=True, exclude_none=True)
                    for item in ordered
                ),
            }
        )
        return cls(provider=provider, tools=ordered, digest=digest)


class ToolProviderRevision(BaseModel):
    """Tenant-scoped provider pin used when resolving agent capabilities."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    provider: ToolProviderRef
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    namespace: NamespaceId
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    tools: tuple[ToolDescriptor, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_tools(self) -> ToolProviderRevision:
        if any(item.provider != self.provider for item in self.tools):
            raise ValueError("provider revision tool identity does not match provider")
        names = tuple(item.name for item in self.tools)
        if len(names) != len(set(names)):
            raise ValueError("provider revision tool names must be unique")
        return self

    def tool(self, name: str) -> ToolDescriptor:
        selected = next((item for item in self.tools if item.name == name), None)
        if selected is None:
            raise LookupError(f"tool {name!r} is not exposed by provider {self.provider.key!r}")
        return selected


class ToolPolicy(BaseModel):
    """Deny-first authority boundary shared by every provider kind."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    allowed_tools: tuple[ToolName, ...] = Field(alias="allowedTools")
    secret_scopes: tuple[NaturalId, ...] = Field(default=(), alias="secretScopes")
    allowed_egress: tuple[str, ...] = Field(default=(), alias="allowedEgress")
    filesystem_read_roots: tuple[str, ...] = Field(default=(), alias="filesystemReadRoots")
    filesystem_write_roots: tuple[str, ...] = Field(default=(), alias="filesystemWriteRoots")
    allow_high_impact: bool = Field(default=False, alias="allowHighImpact")

    @field_validator(
        "allowed_tools",
        "secret_scopes",
        "allowed_egress",
        "filesystem_read_roots",
        "filesystem_write_roots",
    )
    @classmethod
    def validate_unique_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("tool policy values must be unique")
        return value

    @field_validator("allowed_egress")
    @classmethod
    def reject_wildcard_egress(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(item == "*" or "*" in item for item in value):
            raise ValueError("tool policy egress cannot contain wildcards")
        return value

    @property
    def digest(self) -> str:
        return "sha256:" + canonical_hash(self.model_dump(mode="json", by_alias=True))


class ToolInvocationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    provider: ToolProviderRef
    tool_name: ToolName = Field(alias="toolName")
    arguments: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = Field(default="default", alias="tenantId", min_length=1, max_length=255)
    namespace: str = Field(default="default", min_length=1, max_length=255)
    execution_id: UUID = Field(default_factory=uuid4, alias="executionId")
    task_run_id: UUID = Field(default_factory=uuid4, alias="taskRunId")
    attempt: int = Field(default=1, ge=1)
    invocation_id: UUID = Field(default_factory=uuid4, alias="invocationId")
    invocation_key: str | None = Field(default=None, alias="invocationKey", max_length=255)
    request_hash_override: str | None = Field(
        default=None,
        alias="requestHashOverride",
        pattern=r"^[0-9a-f]{64}$",
    )
    timeout_seconds: float | None = Field(default=30, alias="timeoutSeconds", gt=0)
    allow_write: bool = Field(default=False, alias="allowWrite")
    approval_granted: bool = Field(default=False, alias="approvalGranted")
    secret_values: tuple[SecretStr, ...] = Field(default=(), alias="secretValues", repr=False)


class ToolInvocationEvidence(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    contract_version: str = Field(default=TOOL_PROVIDER_CONTRACT_VERSION, alias="contractVersion")
    provider: ToolProviderRef
    tool_name: ToolName = Field(alias="toolName")
    schema_digest: str = Field(alias="schemaDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    invocation_id: UUID = Field(alias="invocationId")
    request_hash: str = Field(alias="requestHash", pattern=r"^[0-9a-f]{64}$")
    policy_digest: str = Field(alias="policyDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    state: ToolInvocationState
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="startedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    ambiguous_external_outcome: bool = Field(default=False, alias="ambiguousExternalOutcome")
    error: str | None = Field(default=None, max_length=4096)


class ToolInvocationResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    output: dict[str, Any]
    evidence: ToolInvocationEvidence


def request_hash(request: ToolInvocationRequest, descriptor: ToolDescriptor) -> str:
    if request.request_hash_override is not None:
        return request.request_hash_override
    return canonical_hash(
        {
            "provider": request.provider.model_dump(mode="json", by_alias=True),
            "tool": request.tool_name,
            "schemaDigest": descriptor.schema_digest,
            "arguments": redact_values(request.arguments, request.secret_values),
        }
    )


def redact_values(value: Any, secrets: tuple[SecretStr, ...]) -> Any:
    if isinstance(value, str):
        result = value
        for secret in secrets:
            raw = secret.get_secret_value()
            if raw:
                result = result.replace(raw, "[REDACTED]")
        return result
    if isinstance(value, dict):
        return {str(key): redact_values(item, secrets) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [redact_values(item, secrets) for item in value]
    return value


class ToolProviderError(RuntimeError):
    """Base error for provider-neutral tool operations."""


class ToolPolicyDenied(ToolProviderError):
    pass


class ToolSchemaError(ToolProviderError):
    pass


class ToolInputValidationError(ToolSchemaError):
    """The supplied tool arguments do not satisfy the pinned input schema."""


class AmbiguousToolInvocation(ToolProviderError):
    """An unfinished external call must not be silently repeated after restart."""


def validate_tool_arguments(descriptor: ToolDescriptor, arguments: dict[str, Any]) -> None:
    try:
        Draft202012Validator(descriptor.input_schema).validate(arguments)
    except ValidationError as exc:
        raise ToolInputValidationError(
            f"tool {descriptor.name!r} arguments failed schema: {exc.message}"
        ) from exc


def validate_tool_output(descriptor: ToolDescriptor, output: dict[str, Any]) -> None:
    if descriptor.output_schema is None:
        return
    candidate: object = output
    if descriptor.provider.kind is ToolProviderKind.MCP and "structuredContent" in output:
        # MCP carries structured output inside its transport envelope; the
        # published MCP schema remains the schema pin for that inner value.
        candidate = output["structuredContent"]
    try:
        Draft202012Validator(descriptor.output_schema).validate(candidate)
    except ValidationError as exc:
        raise ToolSchemaError(
            f"tool {descriptor.name!r} output failed schema: {exc.message}"
        ) from exc


def authorize_tool_call(
    descriptor: ToolDescriptor,
    request: ToolInvocationRequest,
    policy: ToolPolicy,
) -> None:
    if descriptor.name not in policy.allowed_tools:
        raise ToolPolicyDenied(f"tool {descriptor.name!r} is not in the provider allowlist")
    if descriptor.impact is not ToolImpact.READ_ONLY and not request.allow_write:
        raise ToolPolicyDenied(f"tool {descriptor.name!r} requires explicit write authority")
    if descriptor.impact is ToolImpact.HIGH_IMPACT and (
        not policy.allow_high_impact or not request.approval_granted
    ):
        raise ToolPolicyDenied(f"tool {descriptor.name!r} requires an approved high-impact call")
    if not set(descriptor.secret_scopes).issubset(policy.secret_scopes):
        raise ToolPolicyDenied(f"tool {descriptor.name!r} requests an undelegated secret scope")
    if not set(descriptor.allowed_egress).issubset(policy.allowed_egress):
        raise ToolPolicyDenied(f"tool {descriptor.name!r} requests undelegated egress")
    if not set(descriptor.filesystem_read_roots).issubset(policy.filesystem_read_roots):
        raise ToolPolicyDenied(f"tool {descriptor.name!r} requests undelegated filesystem reads")
    if not set(descriptor.filesystem_write_roots).issubset(policy.filesystem_write_roots):
        raise ToolPolicyDenied(f"tool {descriptor.name!r} requests undelegated filesystem writes")
