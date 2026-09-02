from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from amesh.evidence_bundle import EvidenceBundle, EvidencePage, EvidenceRecord


class EvidenceBundleRepository(Protocol):
    max_page_size: int

    async def put(self, bundle: EvidenceBundle) -> EvidenceBundle: ...

    async def build_and_put(
        self,
        execution_id: UUID | str,
        tenant_id: str,
        events: tuple[Any, ...] | list[Any],
        *,
        created_at: datetime,
        correlation_id: UUID | str | None = None,
        inputs: Mapping[str, Any] | None = None,
        outputs: Mapping[str, Any] | None = None,
    ) -> EvidenceBundle: ...

    async def get(self, execution_id: UUID | str, *, tenant_id: str) -> EvidenceBundle: ...

    async def page(
        self,
        execution_id: UUID | str,
        *,
        tenant_id: str,
        section: str = "trace",
        cursor: str | None = None,
        limit: int = 100,
    ) -> EvidencePage[EvidenceRecord]: ...


__all__ = ["EvidenceBundleRepository"]
