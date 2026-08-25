from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .identity import NamespaceId, NaturalId, new_runtime_id
from .resources import canonical_hash


class ModelOperation(StrEnum):
    CHAT = "CHAT"
    EMBEDDING = "EMBEDDING"
    STRUCTURED = "STRUCTURED"
    TOOL_CALL = "TOOL_CALL"


class ModelDataEgress(StrEnum):
    DENY_SECRETS = "DENY_SECRETS"
    REDACT_SECRETS = "REDACT_SECRETS"
    ALLOW = "ALLOW"


class PromptRetention(StrEnum):
    REDACTED = "REDACTED"
    HASH_ONLY = "HASH_ONLY"


class ModelProviderSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    adapter: str = Field(default="openai-compatible", pattern=r"^[a-z][a-z0-9.-]*$")
    revision: str | None = Field(default=None, min_length=1, max_length=255)
    endpoint: str = Field(min_length=1, max_length=4096)
    embedding_endpoint: str | None = Field(
        default=None,
        alias="embeddingEndpoint",
        min_length=1,
        max_length=4096,
    )
    credential_ref: NaturalId = Field(alias="credentialRef")

    @field_validator("endpoint", "embedding_endpoint")
    @classmethod
    def validate_endpoint(cls, value: str | None) -> str | None:
        if value is None:
            return None
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("model provider endpoint must be an absolute HTTP(S) URL")
        if parsed.username is not None or parsed.password is not None or parsed.fragment:
            raise ValueError("model provider endpoint cannot contain credentials or a fragment")
        return value


class ModelBudget(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    max_total_tokens: int = Field(alias="maxTotalTokens", ge=1)
    max_completion_tokens: int | None = Field(
        default=None,
        alias="maxCompletionTokens",
        ge=1,
    )
    max_cost_usd: Decimal = Field(alias="maxCostUsd", ge=0)

    @model_validator(mode="after")
    def validate_completion_budget(self) -> ModelBudget:
        if (
            self.max_completion_tokens is not None
            and self.max_completion_tokens > self.max_total_tokens
        ):
            raise ValueError("maxCompletionTokens cannot exceed maxTotalTokens")
        return self


class ModelDataHandling(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    egress: ModelDataEgress
    prompt_retention: PromptRetention = Field(alias="promptRetention")


class ModelToolDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: NaturalId
    description: str = Field(default="", max_length=4096)
    input_schema: dict[str, Any] = Field(alias="inputSchema")

    @field_validator("input_schema")
    @classmethod
    def validate_schema(cls, value: dict[str, Any]) -> dict[str, Any]:
        try:
            Draft202012Validator.check_schema(value)
        except SchemaError as exc:
            raise ValueError(f"invalid tool input schema: {exc.message}") from exc
        return value


class McpToolImpact(StrEnum):
    READ_ONLY = "READ_ONLY"
    IDEMPOTENT_WRITE = "IDEMPOTENT_WRITE"
    HIGH_IMPACT = "HIGH_IMPACT"


class McpToolPin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: NaturalId
    description: str = Field(default="", max_length=4096)
    input_schema: dict[str, Any] = Field(alias="inputSchema")
    output_schema: dict[str, Any] | None = Field(default=None, alias="outputSchema")
    impact: McpToolImpact = McpToolImpact.HIGH_IMPACT

    @field_validator("input_schema", "output_schema")
    @classmethod
    def validate_schema(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        try:
            Draft202012Validator.check_schema(value)
        except SchemaError as exc:
            raise ValueError(f"invalid MCP tool schema: {exc.message}") from exc
        return value

    @property
    def schema_digest(self) -> str:
        return "sha256:" + canonical_hash(
            {
                "name": self.name,
                "inputSchema": self.input_schema,
                "outputSchema": self.output_schema,
            }
        )


class McpConnectionSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: NaturalId
    namespace: NamespaceId
    endpoint: str = Field(min_length=1, max_length=4096)
    credential_ref: NaturalId = Field(alias="credentialRef")
    tool_allowlist: tuple[NaturalId, ...] = Field(alias="toolAllowlist", min_length=1)
    tools: tuple[McpToolPin, ...] = Field(min_length=1)

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("MCP endpoint must be an absolute HTTP(S) URL")
        if parsed.username is not None or parsed.password is not None or parsed.fragment:
            raise ValueError("MCP endpoint cannot contain credentials or a fragment")
        return value

    @model_validator(mode="after")
    def validate_tool_pins(self) -> McpConnectionSpec:
        allowlist = tuple(self.tool_allowlist)
        tool_names = tuple(tool.name for tool in self.tools)
        if len(set(allowlist)) != len(allowlist):
            raise ValueError("MCP toolAllowlist entries must be unique")
        if len(set(tool_names)) != len(tool_names):
            raise ValueError("MCP tool pins must be unique")
        if set(allowlist) != set(tool_names):
            raise ValueError("MCP toolAllowlist must exactly match the pinned tool names")
        return self

    @property
    def digest(self) -> str:
        return "sha256:" + canonical_hash(self)

    def pinned_tool(self, name: str) -> McpToolPin:
        selected = next((tool for tool in self.tools if tool.name == name), None)
        if selected is None:
            raise PermissionError(f"MCP tool {name!r} is not allowed by connection {self.key!r}")
        return selected


class McpConnectionRevision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    connection_id: UUID = Field(alias="connectionId")
    tenant_id: str = Field(alias="tenantId")
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    spec: McpConnectionSpec
    created_by: str = Field(alias="createdBy", min_length=1, max_length=255)
    created_at: datetime = Field(alias="createdAt")


class McpDiscoveryResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    server_name: str = Field(alias="serverName", min_length=1, max_length=512)
    server_version: str = Field(default="", alias="serverVersion", max_length=128)
    tools: tuple[McpToolPin, ...]
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class AgentInvocationKind(StrEnum):
    MODEL = "MODEL"
    MCP = "MCP"


class AgentInvocationState(StrEnum):
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class AgentInvocationStart(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    invocation_id: UUID = Field(default_factory=new_runtime_id, alias="invocationId")
    tenant_id: str = Field(alias="tenantId")
    namespace: NamespaceId
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID = Field(alias="taskRunId")
    attempt: int = Field(ge=1)
    kind: AgentInvocationKind
    operation: str = Field(min_length=1, max_length=128)
    request_hash: str = Field(alias="requestHash", pattern=r"^[0-9a-f]{64}$")
    request_metadata: dict[str, Any] = Field(default_factory=dict, alias="requestMetadata")


class AgentInvocationRecord(AgentInvocationStart):
    state: AgentInvocationState
    result: dict[str, Any] | None = None
    error: str | None = Field(default=None, max_length=4096)
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="startedAt",
    )
    completed_at: datetime | None = Field(default=None, alias="completedAt")


class AgentInvocationClaim(BaseModel):
    model_config = ConfigDict(frozen=True)

    record: AgentInvocationRecord
    created: bool


class AmbiguousAgentInvocation(RuntimeError):
    """Raised when an unfinished external call cannot be repeated safely."""
