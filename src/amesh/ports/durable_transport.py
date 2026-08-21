from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StaleWorkClaimError(RuntimeError):
    """Raised when a queue mutation uses an expired or superseded fencing token."""


class DurableEnvelope(BaseModel):
    """Versioned payload stored in the PostgreSQL durable work queue."""

    model_config = ConfigDict(frozen=True)

    message_id: UUID
    message_type: str
    schema_version: int = Field(ge=1)
    tenant_id: str
    partition_key: str
    correlation_id: UUID
    causation_id: UUID | None = None
    produced_at: datetime
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
    ) -> int: ...

    async def enqueue_outbox(
        self,
        subject: str,
        envelope: DurableEnvelope,
        *,
        available_at: datetime | None = None,
    ) -> int: ...

    async def publish_outbox(self, *, tenant_id: str, limit: int) -> int: ...

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
    ) -> None: ...
