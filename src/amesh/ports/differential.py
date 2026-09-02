from __future__ import annotations

from typing import TYPE_CHECKING, Protocol
from uuid import UUID

if TYPE_CHECKING:
    from amesh.quality.differential import ComparisonReport, DifferentialSpec, RunObservation
    from amesh.quality.repository import (
        DifferentialEventRecord,
        DifferentialRecord,
        DifferentialRunRecord,
    )


class DifferentialShadowRepository(Protocol):
    async def create_or_get(
        self, spec: DifferentialSpec, *, actor_id: str
    ) -> DifferentialRecord: ...

    async def get(
        self, tenant_id: str, namespace: str, idempotency_key: str
    ) -> DifferentialRecord: ...

    async def get_by_id(self, tenant_id: str, spec_id: UUID) -> DifferentialRecord: ...

    async def claim_side(
        self, tenant_id: str, spec_id: UUID, side: str
    ) -> DifferentialRunRecord: ...

    async def record_observation(
        self, tenant_id: str, run_id: UUID, observation: RunObservation
    ) -> DifferentialRunRecord: ...

    async def get_run(self, tenant_id: str, run_id: UUID) -> DifferentialRunRecord: ...

    async def record_failure(
        self, tenant_id: str, run_id: UUID, error: str
    ) -> DifferentialRunRecord: ...

    async def complete(
        self, tenant_id: str, spec_id: UUID, report: ComparisonReport
    ) -> DifferentialRecord: ...

    async def list_resumable(
        self, tenant_id: str, *, limit: int = 100
    ) -> tuple[DifferentialRunRecord, ...]: ...

    async def events(
        self, tenant_id: str, spec_id: UUID
    ) -> tuple[DifferentialEventRecord, ...]: ...


__all__ = ["DifferentialShadowRepository"]
