from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TriggerOccurrenceState(StrEnum):
    ACCEPTED = "ACCEPTED"
    DEFERRED = "DEFERRED"
    PROCESSING = "PROCESSING"
    RETRY_WAIT = "RETRY_WAIT"
    SUCCEEDED = "SUCCEEDED"
    DEAD_LETTERED = "DEAD_LETTERED"


class TriggerRuntimeState(BaseModel):
    """Queryable lifecycle and health projection for one immutable trigger revision."""

    model_config = ConfigDict(frozen=True)

    trigger_definition_id: UUID
    tenant_id: str
    namespace: str
    flow_id: str
    flow_revision: int = Field(ge=1)
    trigger_id: str
    trigger_type: str
    active: bool
    paused: bool
    checkpoint: dict[str, Any] = Field(default_factory=dict)
    cursor: str | None = None
    last_evaluated_at: datetime | None = None
    next_evaluation_at: datetime | None = None
    last_occurrence_at: datetime | None = None
    last_success_at: datetime | None = None
    lag_seconds: float = Field(default=0, ge=0)
    pending_count: int = Field(default=0, ge=0)
    dead_letter_count: int = Field(default=0, ge=0)
    consecutive_failures: int = Field(default=0, ge=0)
    last_error: str | None = None
    last_decision: str
    updated_at: datetime


class TriggerOccurrence(BaseModel):
    """One durable, tenant-isolated source occurrence and its processing evidence."""

    model_config = ConfigDict(frozen=True)

    occurrence_id: UUID
    tenant_id: str
    trigger_definition_id: UUID
    namespace: str
    flow_id: str
    flow_revision: int = Field(ge=1)
    trigger_id: str
    trigger_type: str
    occurrence_key: str
    state: TriggerOccurrenceState
    attempt: int = Field(ge=0)
    max_attempts: int = Field(ge=1)
    available_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, Any] = Field(default_factory=dict)
    execution_id: UUID | None = None
    replay_of: UUID | None = None
    owner_id: UUID | None = None
    fencing_token: int = Field(default=0, ge=0)
    lease_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class TriggerOccurrenceAcceptance(BaseModel):
    model_config = ConfigDict(frozen=True)

    occurrence: TriggerOccurrence
    duplicate: bool = False
    accepted: bool = True
    reason: str


class TriggerAdapterOccurrence(BaseModel):
    model_config = ConfigDict(frozen=True)

    occurrence_key: str = Field(min_length=1, max_length=1024)
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime


class TriggerPollResult(BaseModel):
    """Stable polling-adapter result: new candidates plus the committed checkpoint."""

    model_config = ConfigDict(frozen=True)

    occurrences: tuple[TriggerAdapterOccurrence, ...] = ()
    checkpoint: dict[str, Any] = Field(default_factory=dict)
    cursor: str | None = None
    next_evaluation_at: datetime | None = None


class PollingTriggerAdapter(Protocol):
    """Language-neutral contract implemented by polling trigger plugins."""

    trigger_types: frozenset[str]

    async def poll(
        self,
        definition: dict[str, Any],
        *,
        checkpoint: dict[str, Any],
        cursor: str | None,
        limit: int,
    ) -> TriggerPollResult: ...

    async def acknowledge(
        self,
        *,
        checkpoint: dict[str, Any],
        cursor: str | None,
    ) -> None: ...


class RealtimeTriggerAdapter(Protocol):
    """Language-neutral contract implemented by realtime trigger plugins."""

    trigger_types: frozenset[str]

    def subscribe(
        self,
        definition: dict[str, Any],
        *,
        checkpoint: dict[str, Any],
        cursor: str | None,
    ) -> AsyncIterator[TriggerAdapterOccurrence]: ...

    async def acknowledge(self, occurrence_key: str) -> None: ...


class TriggerRuntimeRepository(Protocol):
    async def accept_occurrence(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        flow_revision: int,
        trigger_id: str,
        occurrence_key: str,
        payload: dict[str, Any],
        metadata: dict[str, Any],
        max_pending: int,
        max_attempts: int,
        retry_delay: timedelta,
    ) -> TriggerOccurrenceAcceptance: ...

    async def claim_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        lease_duration: timedelta,
    ) -> TriggerOccurrence: ...

    async def claim_due_occurrences(
        self,
        *,
        tenant_id: str,
        owner_id: UUID,
        lease_duration: timedelta,
        limit: int = 100,
    ) -> list[TriggerOccurrence]: ...

    async def complete_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        execution_id: UUID,
        evidence: dict[str, Any],
    ) -> TriggerOccurrence: ...

    async def fail_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        error: str,
        retry_delay: timedelta,
    ) -> TriggerOccurrence: ...

    async def get_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
    ) -> TriggerOccurrence: ...

    async def list_occurrences(
        self,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        trigger_id: str | None = None,
        state: TriggerOccurrenceState | None = None,
        limit: int = 100,
    ) -> list[TriggerOccurrence]: ...

    async def replay_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
    ) -> TriggerOccurrence: ...

    async def list_runtime_states(
        self,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        trigger_id: str | None = None,
        active: bool | None = None,
        limit: int = 100,
    ) -> list[TriggerRuntimeState]: ...

    async def set_paused(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        trigger_id: str,
        paused: bool,
        actor_id: str,
        reason: str,
    ) -> TriggerRuntimeState: ...

    async def update_checkpoint(
        self,
        *,
        tenant_id: str,
        trigger_definition_id: UUID,
        checkpoint: dict[str, Any],
        cursor: str | None,
        evaluated_at: datetime,
        next_evaluation_at: datetime | None,
        decision: str,
    ) -> TriggerRuntimeState: ...
