from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .agent_resources import AgentMemoryScope
from .identity import NaturalId


class AgentMemoryContext(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    namespace: str
    agent_key: NaturalId = Field(alias="agentKey")
    agent_revision: int = Field(alias="agentRevision", ge=1)
    execution_id: UUID = Field(alias="executionId")
    scope: AgentMemoryScope
    shared_scope: NaturalId | None = Field(default=None, alias="sharedScope")
    max_bytes: int = Field(alias="maxBytes", gt=0)
    retention_seconds: int = Field(alias="retentionSeconds", gt=0)


class AgentMemoryWrite(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: NaturalId
    value: dict[str, Any]
    provenance: dict[str, Any]
    redacted: bool = True


class AgentMemoryEntry(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    entry_id: UUID = Field(alias="entryId")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    agent_key: str = Field(alias="agentKey")
    agent_revision: int = Field(alias="agentRevision")
    execution_id: UUID | None = Field(alias="executionId")
    scope: AgentMemoryScope
    shared_scope: str | None = Field(alias="sharedScope")
    key: str
    value: dict[str, Any]
    content_digest: str = Field(alias="contentDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    byte_size: int = Field(alias="byteSize", ge=0)
    provenance: dict[str, Any]
    redacted: bool
    version: int = Field(ge=1)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    expires_at: datetime = Field(alias="expiresAt")

    def metadata(self) -> AgentMemoryMetadata:
        return AgentMemoryMetadata.model_validate(
            self.model_dump(mode="json", by_alias=True, exclude={"value"})
        )


class AgentMemoryMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    entry_id: UUID = Field(alias="entryId")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    agent_key: str = Field(alias="agentKey")
    agent_revision: int = Field(alias="agentRevision")
    execution_id: UUID | None = Field(alias="executionId")
    scope: AgentMemoryScope
    shared_scope: str | None = Field(alias="sharedScope")
    key: str
    content_digest: str = Field(alias="contentDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    byte_size: int = Field(alias="byteSize", ge=0)
    provenance: dict[str, Any]
    redacted: bool
    version: int = Field(ge=1)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    expires_at: datetime = Field(alias="expiresAt")
