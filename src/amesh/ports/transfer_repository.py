from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from amesh.profile_transfer import ProfileBundle
    from amesh.session_transfer import (
        SessionTransferBundle,
        SessionTransferCompatibilityReport,
        SessionTransferImportResult,
        SessionTransferMode,
    )


class ProfileImportReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    import_id: str = Field(alias="importId", min_length=1)
    bundle_digest: str = Field(alias="bundleDigest", pattern=r"^[0-9a-f]{64}$")
    target_tenant_id: str = Field(alias="targetTenantId", min_length=1, max_length=255)
    agent_key: str = Field(alias="agentKey", min_length=1, max_length=255)
    agent_revision: int = Field(alias="agentRevision", ge=1)
    created_at: datetime = Field(alias="createdAt")


class ProfileTransferImportRepository(Protocol):
    async def get_profile_import(
        self, target_tenant_id: str, import_id: str
    ) -> ProfileImportReceipt | None: ...

    async def record_profile_import(
        self,
        target_tenant_id: str,
        bundle: ProfileBundle,
        *,
        actor_id: str,
        import_id: str,
    ) -> ProfileImportReceipt: ...


class SessionTransferImportRepository(Protocol):
    async def get_import(
        self, target_tenant_id: str, import_id: str
    ) -> SessionTransferImportResult | None: ...

    async def import_records(
        self,
        target_tenant_id: str,
        bundle: SessionTransferBundle,
        *,
        actor_id: str,
        import_id: str,
        credential_rebindings: dict[str, str] | None = None,
    ) -> SessionTransferImportResult: ...

    async def plan_import(
        self,
        target_tenant_id: str,
        bundle: SessionTransferBundle,
        *,
        credential_rebindings: dict[str, str] | None = None,
    ) -> SessionTransferCompatibilityReport: ...


class TransferRepository(
    ProfileTransferImportRepository, SessionTransferImportRepository, Protocol
):
    """Combined profile/session persistence port."""

    async def export_session_bundle(
        self,
        source_tenant_id: str,
        session_id: UUID,
        *,
        mode: SessionTransferMode,
        artifact_destination_refs: dict[str, str] | None = None,
    ) -> SessionTransferBundle: ...


__all__ = [
    "ProfileImportReceipt",
    "ProfileTransferImportRepository",
    "SessionTransferImportRepository",
    "TransferRepository",
]
