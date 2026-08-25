from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from amesh.evidence_bundle import EvidenceRecord


class EvidenceBundlePageResponse(BaseModel):
    """Bounded canonical bundle projection returned by REST and SDK clients."""

    model_config = ConfigDict(populate_by_name=True)

    schema_version: str = Field(alias="schemaVersion")
    execution_id: str = Field(alias="executionId")
    bundle_digest: str = Field(alias="bundleDigest")
    section: str
    items: tuple[EvidenceRecord, ...]
    next_cursor: str | None = Field(default=None, alias="nextCursor")
    limit: int = Field(ge=1)
    total: int = Field(ge=0)
