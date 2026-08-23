from __future__ import annotations

from collections import Counter
from time import perf_counter
from uuid import UUID

from amesh.domain import (
    ReconciliationDisposition,
    ReconciliationInvariant,
    ReconciliationRequest,
    ReconciliationRun,
)
from amesh.observability import (
    RECONCILIATION_DURATION,
    RECONCILIATION_FINDINGS,
    RECONCILIATION_RUNS,
    RECONCILIATION_UNRESOLVED,
    STUCK_WORK,
)
from amesh.ports import ReconciliationRepository


class ReconciliationService:
    def __init__(self, repository: ReconciliationRepository) -> None:
        self._repository = repository

    async def run(
        self,
        request: ReconciliationRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> ReconciliationRun:
        started = perf_counter()
        try:
            result = await self._repository.run(
                request,
                tenant_id=tenant_id,
                actor_id=actor_id,
            )
        finally:
            RECONCILIATION_DURATION.observe(perf_counter() - started)
        RECONCILIATION_RUNS.labels(request.mode.value).inc()
        unresolved = Counter(
            finding.invariant
            for finding in result.findings
            if finding.disposition is not ReconciliationDisposition.REPAIRED
        )
        for invariant in ReconciliationInvariant:
            RECONCILIATION_UNRESOLVED.labels(invariant.value).set(unresolved[invariant])
        STUCK_WORK.set(sum(unresolved.values()))
        for finding in result.findings:
            RECONCILIATION_FINDINGS.labels(
                finding.invariant.value,
                finding.disposition.value,
            ).inc()
        return result

    async def get(self, run_id: UUID, *, tenant_id: str) -> ReconciliationRun:
        return await self._repository.get(run_id, tenant_id=tenant_id)

    async def list_runs(
        self,
        *,
        tenant_id: str,
        limit: int = 50,
    ) -> list[ReconciliationRun]:
        return await self._repository.list_runs(tenant_id=tenant_id, limit=limit)
