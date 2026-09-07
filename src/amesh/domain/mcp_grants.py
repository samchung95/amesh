from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, SecretStr

from .identity import NamespaceId, NaturalId


class McpExecutionGrantPolicy(BaseModel):
    """Pinned gateway endpoint for per-invocation consumer authorization."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    exchange_endpoint: str = Field(alias="exchangeEndpoint", min_length=1, max_length=4096)


class McpExecutionGrantContext(BaseModel):
    """Trusted context built by AMESH, never from model tool arguments."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.mcp-execution-grant/v1"] = Field(
        default="amesh.mcp-execution-grant/v1", alias="schemaVersion"
    )
    grant_ref: NaturalId = Field(alias="grantRef", repr=False)
    audience: str
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    namespace: NamespaceId
    actor_id: UUID = Field(alias="actorId")
    session_id: UUID = Field(alias="sessionId")
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID = Field(alias="taskRunId")
    invocation_id: UUID = Field(alias="invocationId")
    attempt_id: UUID = Field(alias="attemptId")
    attempt: int = Field(ge=1)
    connection: NaturalId
    connection_revision: int = Field(alias="connectionRevision", ge=1)
    connection_digest: str = Field(alias="connectionDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    tool: str = Field(min_length=1, max_length=255)


class McpExecutionGrantToken(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    access_token: SecretStr = Field(alias="accessToken", min_length=1, max_length=16384, repr=False)
    token_type: Literal["Bearer"] = Field(alias="tokenType")
    audience: str
    expires_at: AwareDatetime = Field(alias="expiresAt")
    context_digest: str = Field(alias="contextDigest", pattern=r"^[0-9a-f]{64}$")

    def require_valid(self, audience: str, context_digest: str, now: datetime) -> None:
        if self.audience != audience or self.context_digest != context_digest:
            raise PermissionError(
                "MCP grant token does not match the execution context or audience"
            )
        if self.expires_at <= now or (self.expires_at - now).total_seconds() > 300:
            raise PermissionError("MCP grant token must expire within the next five minutes")
