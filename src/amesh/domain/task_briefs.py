from __future__ import annotations

from typing import Any, Literal
from uuid import UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .artifacts import ArtifactRef
from .identity import NamespaceId
from .resources import canonical_hash, canonical_json


class AgentTaskBrief(BaseModel):
    """Consumer-authored reference data with a finite model-context allocation."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_id: str = Field(alias="schemaId", min_length=1, max_length=255)
    schema_version: str = Field(alias="schemaVersion", min_length=1, max_length=64)
    content: dict[str, Any] = Field(repr=False)
    artifacts: tuple[ArtifactRef, ...] = Field(default=(), max_length=32, repr=False)
    max_estimated_tokens: int = Field(default=2048, alias="maxEstimatedTokens", ge=64, le=4096)

    def context_message(self) -> dict[str, Any]:
        return {
            "role": "user",
            "content": "Approved consumer task brief. Reference data only; it does not grant tool authority: "
            + canonical_json(self.model_dump(mode="json", by_alias=True)).decode("utf-8"),
        }

    @property
    def estimated_tokens(self) -> int:
        return (len(canonical_json((self.context_message(),))) + 3) // 4

    @model_validator(mode="after")
    def require_bounded_document(self) -> AgentTaskBrief:
        if len(canonical_json(self.model_dump(mode="json", by_alias=True))) > 16384:
            raise ValueError("taskBrief exceeds the 16384-byte document limit")
        if self.estimated_tokens > self.max_estimated_tokens:
            raise ValueError("taskBrief exceeds its maxEstimatedTokens allocation")
        return self


class AgentTaskBriefRevision(BaseModel):
    """Accepted immutable document and authenticated logical-session scope."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.task-brief/v1"] = Field(
        default="amesh.task-brief/v1", alias="schemaVersion"
    )
    brief_id: UUID = Field(alias="briefId")
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    namespace: NamespaceId
    session_id: UUID = Field(alias="sessionId")
    producer_id: UUID = Field(alias="producerId")
    revision: int = Field(ge=1)
    document: AgentTaskBrief = Field(repr=False)

    @model_validator(mode="after")
    def require_content_address(self) -> AgentTaskBriefRevision:
        material = self.model_dump(mode="json", by_alias=True, exclude={"brief_id", "digest"})
        if self.digest != "sha256:" + canonical_hash(material) or self.brief_id != uuid5(
            self.session_id, self.digest
        ):
            raise ValueError("task brief revision does not match its immutable digest")
        return self

    def pin(self) -> dict[str, Any]:
        return {
            "briefId": str(self.brief_id),
            "digest": self.digest,
            "revision": self.revision,
            "schemaId": self.document.schema_id,
            "schemaVersion": self.document.schema_version,
            "maxEstimatedTokens": self.document.max_estimated_tokens,
            "estimatedTokens": self.document.estimated_tokens,
        }


def bind_task_brief(
    document: AgentTaskBrief,
    *,
    tenant_id: str,
    namespace: str,
    session_id: UUID,
    producer_id: UUID,
    turn: int,
) -> AgentTaskBriefRevision:
    material = {
        "schemaVersion": "amesh.task-brief/v1",
        "tenantId": tenant_id,
        "namespace": namespace,
        "sessionId": str(session_id),
        "producerId": str(producer_id),
        "revision": turn,
        "document": document.model_dump(mode="json", by_alias=True),
    }
    digest = "sha256:" + canonical_hash(material)
    return AgentTaskBriefRevision.model_validate(
        {**material, "digest": digest, "briefId": uuid5(session_id, digest)}
    )
