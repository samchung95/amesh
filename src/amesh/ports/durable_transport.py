from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StaleWorkClaimError(RuntimeError):
    """Raised when a queue mutation uses an expired or superseded fencing token."""


class MessageIdentityConflict(RuntimeError):
    """Raised when one message identity is reused with different immutable content."""


class DeadLetterReplayError(RuntimeError):
    """Raised when a dead-letter record cannot be replayed from its current state."""


class DurableEnvelope(BaseModel):
    """Versioned payload stored in the PostgreSQL durable work queue."""

    model_config = ConfigDict(frozen=True)

    message_id: UUID
    message_type: str = Field(min_length=1, max_length=256)
    schema_version: int = Field(ge=1)
    tenant_id: str = Field(min_length=1, max_length=128)
    partition_key: str = Field(min_length=1, max_length=512)
    correlation_id: UUID
    causation_id: UUID | None = None
    produced_at: datetime
    trace_context: dict[str, str] = Field(default_factory=dict)
    payload: dict[str, Any]


class WorkClaim(BaseModel):
    """A fenced, expiring claim over one durable queue record."""

    model_config = ConfigDict(frozen=True)

    queue_id: int = Field(ge=1)
    lane: str
    consumer_id: str
    fencing_token: int = Field(ge=1)
    lease_expires_at: datetime
    delivery_attempt: int = Field(ge=1)
    envelope: DurableEnvelope


class DeadLetterRecord(BaseModel):
    """Payload-safe quarantine evidence for one exhausted delivery cycle."""

    model_config = ConfigDict(frozen=True)

    dead_letter_id: UUID
    source_type: str
    source_id: int = Field(ge=1)
    message_id: UUID
    lane: str
    partition_key: str
    message_type: str
    schema_version: int = Field(ge=1)
    failure_class: str
    payload_checksum: str
    attempt_count: int = Field(ge=1)
    last_error: str
    quarantined_at: datetime
    resolution: str
    resolved_at: datetime | None = None
    resolved_by: str | None = None


class TransportDiagnostics(BaseModel):
    """Bounded tenant transport health without message payloads or high-cardinality labels."""

    model_config = ConfigDict(frozen=True)

    queue_depth: int = Field(ge=0)
    oldest_eligible_age_seconds: float | None = Field(default=None, ge=0)
    claimed_count: int = Field(ge=0)
    expired_claim_count: int = Field(ge=0)
    redelivery_count: int = Field(ge=0)
    poison_message_count: int = Field(ge=0)
    dead_letter_count: int = Field(ge=0)
    outbox_pending_count: int = Field(ge=0)
    outbox_oldest_age_seconds: float | None = Field(default=None, ge=0)
    outbox_retry_count: int = Field(ge=0)
    outbox_dead_letter_count: int = Field(ge=0)


class DurableTransport(Protocol):
    """PostgreSQL-backed queue contract.

    The interface isolates domain services from SQL claim mechanics; it is not a promise that
    AMESH will support an alternate internal broker.
    """

    async def enqueue(
        self,
        lane: str,
        envelope: DurableEnvelope,
        *,
        available_at: datetime | None = None,
        priority: int = 0,
        max_attempts: int = 25,
    ) -> int: ...

    async def enqueue_outbox(
        self,
        subject: str,
        envelope: DurableEnvelope,
        *,
        available_at: datetime | None = None,
        max_attempts: int = 25,
    ) -> int: ...

    async def publish_outbox(self, *, tenant_id: str, limit: int) -> int: ...

    async def record_outbox_failure(
        self,
        sequence: int,
        *,
        tenant_id: str,
        retry_at: datetime,
        reason: str,
        failure_class: str,
    ) -> bool: ...

    async def record_consumed(
        self,
        consumer_name: str,
        envelope: DurableEnvelope,
    ) -> bool: ...

    async def claim(
        self,
        lane: str,
        consumer_id: str,
        *,
        tenant_id: str,
        limit: int,
        lease_duration: timedelta,
    ) -> list[WorkClaim]: ...

    async def wait_for_work(
        self,
        lane: str,
        *,
        tenant_id: str,
        timeout_seconds: float,
    ) -> bool: ...

    async def extend(
        self,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        lease_duration: timedelta,
        *,
        tenant_id: str,
    ) -> datetime: ...

    async def acknowledge(
        self,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        *,
        tenant_id: str,
    ) -> None: ...

    async def release(
        self,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        *,
        tenant_id: str,
        retry_at: datetime,
        reason: str,
        failure_class: str = "transient",
    ) -> None: ...

    async def list_dead_letters(self, *, tenant_id: str) -> list[DeadLetterRecord]: ...

    async def replay_dead_letter(
        self,
        dead_letter_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> None: ...

    async def diagnostics(self, *, tenant_id: str) -> TransportDiagnostics: ...
