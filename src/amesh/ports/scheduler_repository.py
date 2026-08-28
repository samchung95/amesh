from __future__ import annotations

from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SchedulerFenceError(RuntimeError):
    """Raised when a scheduler mutation uses an expired or superseded ownership token."""


class ScheduleState(BaseModel):
    """Persisted schedule cursor, ownership and latest decision evidence."""

    model_config = ConfigDict(frozen=True)

    trigger_definition_id: UUID
    tenant_id: str
    namespace: str
    flow_id: str
    flow_revision: int = Field(ge=1)
    trigger_id: str
    next_fire_at: datetime | None = None
    last_evaluated_at: datetime | None = None
    last_occurrence_at: datetime | None = None
    owner_id: UUID | None = None
    fencing_token: int = Field(ge=0)
    lease_expires_at: datetime | None = None
    last_decision: str
    missed_count: int = Field(ge=0)
    claimed: bool = False


class SchedulerRepository(Protocol):
    async def database_time(self) -> datetime: ...

    async def claim_schedule(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        flow_revision: int,
        trigger_id: str,
        initial_next_fire_at: datetime | None,
        due_before: datetime,
        owner_id: UUID,
        lease_duration: timedelta,
    ) -> ScheduleState: ...

    async def complete_schedule(
        self,
        *,
        tenant_id: str,
        trigger_definition_id: UUID,
        owner_id: UUID,
        fencing_token: int,
        evaluated_at: datetime,
        next_fire_at: datetime | None,
        last_occurrence_at: datetime | None,
        decision: str,
        missed_count: int,
    ) -> ScheduleState: ...

    async def get_schedule_state(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        flow_revision: int,
        trigger_id: str,
    ) -> ScheduleState: ...
