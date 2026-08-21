from __future__ import annotations

from typing import Protocol
from uuid import UUID

from amesh.domain import ReconciliationRequest, ReconciliationRun


class ReconciliationAlreadyRunningError(RuntimeError):
    """Raised when another tenant reconciliation owns the bounded repair slot."""


class ReconciliationRepository(Protocol):
    async def run(
        self,
        request: ReconciliationRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> ReconciliationRun: ...

    async def get(self, run_id: UUID, *, tenant_id: str) -> ReconciliationRun: ...

    async def list_runs(
        self,
        *,
        tenant_id: str,
        limit: int = 50,
    ) -> list[ReconciliationRun]: ...
