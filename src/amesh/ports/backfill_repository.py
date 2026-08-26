from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from amesh.domain.backfill import BackfillItem, BackfillRecord, BackfillSpec, BackfillState


class BackfillItemDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    occurrence_key: str
    scheduled_for: datetime | None = None
    partition_key: str | None = None
    source_execution_id: UUID | None = None


class BackfillRepository(Protocol):
    async def create_backfill(
        self,
        spec: BackfillSpec,
        items: tuple[BackfillItemDefinition, ...],
        *,
        backfill_id: UUID | None = None,
        tenant_id: str,
        actor_id: str,
        task_count: int,
    ) -> BackfillRecord: ...

    async def get_backfill(self, backfill_id: UUID, *, tenant_id: str) -> BackfillRecord: ...

    async def list_backfills(self, *, tenant_id: str, limit: int = 100) -> list[BackfillRecord]: ...

    async def list_pending_items(
        self, backfill_id: UUID, *, tenant_id: str, limit: int
    ) -> list[BackfillItem]: ...

    async def link_execution(
        self,
        backfill_id: UUID,
        item_id: UUID,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> None: ...

    async def transition_backfill(
        self,
        backfill_id: UUID,
        state: BackfillState,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
    ) -> BackfillRecord: ...

    async def launch_capacity(self, backfill_id: UUID, *, tenant_id: str) -> int: ...

    async def refresh_backfill(self, backfill_id: UUID, *, tenant_id: str) -> BackfillRecord: ...
