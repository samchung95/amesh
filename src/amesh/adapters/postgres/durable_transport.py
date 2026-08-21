from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta

import asyncpg  # type: ignore[import-untyped]
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql.elements import TextClause

from amesh.ports.durable_transport import (
    DurableEnvelope,
    DurableTransport,
    StaleWorkClaimError,
    WorkClaim,
)

_ENQUEUE = text(
    """
    INSERT INTO durable_work_queue (
        tenant_id,
        message_id,
        lane,
        partition_key,
        message_type,
        schema_version,
        envelope,
        priority,
        available_at
    )
    SELECT
        tenants.id,
        :message_id,
        :lane,
        :partition_key,
        :message_type,
        :schema_version,
        CAST(:envelope AS jsonb),
        :priority,
        COALESCE(CAST(:available_at AS timestamptz), now())
    FROM tenants
    WHERE tenants.slug = :tenant_slug
    ON CONFLICT (tenant_id, message_id)
    DO UPDATE SET message_id = EXCLUDED.message_id
    RETURNING id
    """
)

_ENQUEUE_OUTBOX = text(
    """
    INSERT INTO messages_outbox (
        tenant_id,
        message_id,
        subject,
        partition_key,
        envelope,
        available_at
    )
    SELECT
        tenants.id,
        :message_id,
        :subject,
        :partition_key,
        CAST(:envelope AS jsonb),
        COALESCE(CAST(:available_at AS timestamptz), now())
    FROM tenants
    WHERE tenants.slug = :tenant_slug
    ON CONFLICT (tenant_id, message_id)
    DO UPDATE SET message_id = EXCLUDED.message_id
    RETURNING sequence
    """
)

_PUBLISH_OUTBOX = text(
    """
    WITH pending AS (
        SELECT
            sequence,
            tenant_id,
            message_id,
            subject,
            partition_key,
            envelope,
            available_at
        FROM messages_outbox
        WHERE published_at IS NULL
          AND available_at <= now()
        ORDER BY available_at, sequence
        FOR UPDATE SKIP LOCKED
        LIMIT :limit
    ), queued AS (
        INSERT INTO durable_work_queue (
            tenant_id,
            message_id,
            lane,
            partition_key,
            message_type,
            schema_version,
            envelope,
            available_at
        )
        SELECT
            pending.tenant_id,
            pending.message_id,
            pending.subject,
            pending.partition_key,
            pending.envelope ->> 'message_type',
            CAST(pending.envelope ->> 'schema_version' AS integer),
            pending.envelope,
            pending.available_at
        FROM pending
        ON CONFLICT (tenant_id, message_id) DO NOTHING
        RETURNING message_id
    )
    UPDATE messages_outbox AS outbox
    SET published_at = now(),
        attempts = outbox.attempts + 1,
        last_error = NULL
    FROM pending
    WHERE outbox.sequence = pending.sequence
    RETURNING outbox.sequence
    """
)

_RECORD_CONSUMED = text(
    """
    WITH tenant AS (
        SELECT id
        FROM tenants
        WHERE slug = :tenant_slug
    ), inserted AS (
        INSERT INTO consumed_messages (consumer_name, tenant_id, message_id)
        SELECT :consumer_name, tenant.id, :message_id
        FROM tenant
        ON CONFLICT (consumer_name, tenant_id, message_id) DO NOTHING
        RETURNING message_id
    )
    SELECT
        EXISTS (SELECT 1 FROM tenant) AS tenant_exists,
        EXISTS (SELECT 1 FROM inserted) AS inserted
    """
)

_CLAIM = text(
    """
    WITH candidates AS (
        SELECT id
        FROM durable_work_queue
        WHERE lane = :lane
          AND delivery_attempt < max_attempts
          AND (
              (state = 'READY' AND available_at <= now())
              OR (state = 'CLAIMED' AND lease_expires_at <= now())
          )
        ORDER BY priority DESC, available_at, id
        FOR UPDATE SKIP LOCKED
        LIMIT :limit
    )
    UPDATE durable_work_queue AS queue
    SET state = 'CLAIMED',
        claimed_by = :consumer_id,
        fencing_token = queue.fencing_token + 1,
        lease_expires_at = now() + make_interval(secs => :lease_seconds),
        delivery_attempt = queue.delivery_attempt + 1,
        updated_at = now()
    FROM candidates
    WHERE queue.id = candidates.id
    RETURNING
        queue.id,
        queue.lane,
        queue.claimed_by,
        queue.fencing_token,
        queue.lease_expires_at,
        queue.delivery_attempt,
        queue.envelope
    """
)

_EXTEND = text(
    """
    UPDATE durable_work_queue
    SET lease_expires_at = now() + make_interval(secs => :lease_seconds),
        updated_at = now()
    WHERE id = :queue_id
      AND state = 'CLAIMED'
      AND claimed_by = :consumer_id
      AND fencing_token = :fencing_token
      AND lease_expires_at > now()
    RETURNING lease_expires_at
    """
)

_ACKNOWLEDGE = text(
    """
    UPDATE durable_work_queue
    SET state = 'COMPLETED',
        claimed_by = NULL,
        lease_expires_at = NULL,
        completed_at = now(),
        updated_at = now()
    WHERE id = :queue_id
      AND state = 'CLAIMED'
      AND claimed_by = :consumer_id
      AND fencing_token = :fencing_token
      AND lease_expires_at > now()
    RETURNING id
    """
)

_RELEASE = text(
    """
    UPDATE durable_work_queue
    SET state = 'READY',
        claimed_by = NULL,
        lease_expires_at = NULL,
        available_at = :retry_at,
        last_error = :reason,
        updated_at = now()
    WHERE id = :queue_id
      AND state = 'CLAIMED'
      AND claimed_by = :consumer_id
      AND fencing_token = :fencing_token
      AND lease_expires_at > now()
    RETURNING id
    """
)


class PostgresDurableTransport(DurableTransport):
    """SQLAlchemy async adapter for the authoritative PostgreSQL work queue."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def enqueue(
        self,
        lane: str,
        envelope: DurableEnvelope,
        *,
        available_at: datetime | None = None,
        priority: int = 0,
    ) -> int:
        parameters = {
            "message_id": envelope.message_id,
            "lane": lane,
            "partition_key": envelope.partition_key,
            "message_type": envelope.message_type,
            "schema_version": envelope.schema_version,
            "envelope": json.dumps(envelope.model_dump(mode="json")),
            "priority": priority,
            "available_at": available_at,
            "tenant_slug": envelope.tenant_id,
        }
        async with self._engine.begin() as connection:
            result = await connection.execute(_ENQUEUE, parameters)
            queue_id = result.scalar_one_or_none()
        if queue_id is None:
            raise LookupError(f"tenant {envelope.tenant_id!r} does not exist")
        return int(queue_id)

    async def enqueue_outbox(
        self,
        subject: str,
        envelope: DurableEnvelope,
        *,
        available_at: datetime | None = None,
    ) -> int:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _ENQUEUE_OUTBOX,
                {
                    "message_id": envelope.message_id,
                    "subject": subject,
                    "partition_key": envelope.partition_key,
                    "envelope": json.dumps(envelope.model_dump(mode="json")),
                    "available_at": available_at,
                    "tenant_slug": envelope.tenant_id,
                },
            )
            sequence = result.scalar_one_or_none()
        if sequence is None:
            raise LookupError(f"tenant {envelope.tenant_id!r} does not exist")
        return int(sequence)

    async def publish_outbox(self, *, limit: int) -> int:
        if limit < 1:
            raise ValueError("outbox publish limit must be at least 1")
        async with self._engine.begin() as connection:
            result = await connection.execute(_PUBLISH_OUTBOX, {"limit": limit})
            published = result.scalars().all()
        return len(published)

    async def record_consumed(
        self,
        consumer_name: str,
        envelope: DurableEnvelope,
    ) -> bool:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _RECORD_CONSUMED,
                {
                    "consumer_name": consumer_name,
                    "tenant_slug": envelope.tenant_id,
                    "message_id": envelope.message_id,
                },
            )
            row = result.mappings().one()
        if not row["tenant_exists"]:
            raise LookupError(f"tenant {envelope.tenant_id!r} does not exist")
        return bool(row["inserted"])

    async def claim(
        self,
        lane: str,
        consumer_id: str,
        *,
        limit: int,
        lease_duration: timedelta,
    ) -> list[WorkClaim]:
        lease_seconds = _positive_lease_seconds(lease_duration)
        if limit < 1:
            raise ValueError("claim limit must be at least 1")

        async with self._engine.begin() as connection:
            result = await connection.execute(
                _CLAIM,
                {
                    "lane": lane,
                    "consumer_id": consumer_id,
                    "limit": limit,
                    "lease_seconds": lease_seconds,
                },
            )
            rows = result.mappings().all()
        return [_to_work_claim(row) for row in rows]

    async def wait_for_work(self, lane: str, *, timeout_seconds: float) -> bool:
        if not lane:
            raise ValueError("work lane must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("work wait timeout must be positive")
        connection = await asyncpg.connect(
            self._engine.url.render_as_string(hide_password=False).replace(
                "postgresql+asyncpg://",
                "postgresql://",
                1,
            )
        )
        wake = asyncio.Event()

        def listener(
            connection: object,
            process_id: int,
            channel: str,
            payload: str,
        ) -> None:
            del connection, process_id, channel
            if payload == lane:
                wake.set()

        await connection.add_listener("amesh_work", listener)
        try:
            ready = await connection.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM durable_work_queue
                    WHERE lane = $1
                      AND state = 'READY'
                      AND available_at <= now()
                )
                """,
                lane,
            )
            if ready:
                return True
            try:
                await asyncio.wait_for(wake.wait(), timeout=timeout_seconds)
            except TimeoutError:
                return False
            return True
        finally:
            await connection.remove_listener("amesh_work", listener)
            await connection.close()

    async def extend(
        self,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        lease_duration: timedelta,
    ) -> datetime:
        lease_seconds = _positive_lease_seconds(lease_duration)
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _EXTEND,
                {
                    "queue_id": queue_id,
                    "consumer_id": consumer_id,
                    "fencing_token": fencing_token,
                    "lease_seconds": lease_seconds,
                },
            )
            lease_expires_at = result.scalar_one_or_none()
        if lease_expires_at is None:
            raise _stale_claim(queue_id, consumer_id, fencing_token)
        if not isinstance(lease_expires_at, datetime):
            raise TypeError("PostgreSQL returned a non-datetime lease expiry")
        return lease_expires_at

    async def acknowledge(
        self,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
    ) -> None:
        await self._mutate_claim(
            _ACKNOWLEDGE,
            queue_id=queue_id,
            consumer_id=consumer_id,
            fencing_token=fencing_token,
        )

    async def release(
        self,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        *,
        retry_at: datetime,
        reason: str,
    ) -> None:
        await self._mutate_claim(
            _RELEASE,
            queue_id=queue_id,
            consumer_id=consumer_id,
            fencing_token=fencing_token,
            retry_at=retry_at,
            reason=reason,
        )

    async def _mutate_claim(
        self,
        statement: TextClause,
        *,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        **parameters: object,
    ) -> None:
        values = {
            "queue_id": queue_id,
            "consumer_id": consumer_id,
            "fencing_token": fencing_token,
            **parameters,
        }
        async with self._engine.begin() as connection:
            result = await connection.execute(statement, values)
            mutated_id = result.scalar_one_or_none()
        if mutated_id is None:
            raise _stale_claim(queue_id, consumer_id, fencing_token)


def _positive_lease_seconds(lease_duration: timedelta) -> float:
    lease_seconds = lease_duration.total_seconds()
    if lease_seconds <= 0:
        raise ValueError("lease duration must be positive")
    return lease_seconds


def _to_work_claim(row: RowMapping) -> WorkClaim:
    return WorkClaim(
        queue_id=row["id"],
        lane=row["lane"],
        consumer_id=row["claimed_by"],
        fencing_token=row["fencing_token"],
        lease_expires_at=row["lease_expires_at"],
        delivery_attempt=row["delivery_attempt"],
        envelope=DurableEnvelope.model_validate(row["envelope"]),
    )


def _stale_claim(queue_id: int, consumer_id: str, fencing_token: int) -> StaleWorkClaimError:
    return StaleWorkClaimError(
        "queue claim is expired or superseded: "
        f"queue_id={queue_id}, consumer_id={consumer_id!r}, fencing_token={fencing_token}"
    )
