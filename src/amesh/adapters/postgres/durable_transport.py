from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from time import perf_counter
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql.elements import TextClause

from amesh.observability import (
    QUEUE_DEPTH,
    QUEUE_OLDEST_AGE,
    instrument_async_operation,
)
from amesh.ports.durable_transport import (
    DeadLetterRecord,
    DeadLetterReplayError,
    DurableEnvelope,
    DurableTransport,
    MessageIdentityConflict,
    QueueShardDiagnostics,
    StaleWorkClaimError,
    TransportDiagnostics,
    TransportRetentionResult,
    WorkClaim,
)
from amesh.ports.errors import NotFoundError

from .repository_support import PostgresRepositoryBase, PostgresRepositoryServices
from .tenant_context import resolve_active_tenant_id_asyncpg

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
        max_attempts,
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
        :max_attempts,
        COALESCE(CAST(:available_at AS timestamptz), now())
    FROM tenants
    WHERE tenants.slug = :tenant_slug
    ON CONFLICT (tenant_id, message_id)
    DO UPDATE SET message_id = EXCLUDED.message_id
    WHERE durable_work_queue.lane = EXCLUDED.lane
      AND durable_work_queue.partition_key = EXCLUDED.partition_key
      AND durable_work_queue.message_type = EXCLUDED.message_type
      AND durable_work_queue.schema_version = EXCLUDED.schema_version
      AND durable_work_queue.envelope = EXCLUDED.envelope
      AND durable_work_queue.max_attempts = EXCLUDED.max_attempts
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
        max_attempts,
        available_at
    )
    SELECT
        tenants.id,
        :message_id,
        :subject,
        :partition_key,
        CAST(:envelope AS jsonb),
        :max_attempts,
        COALESCE(CAST(:available_at AS timestamptz), now())
    FROM tenants
    WHERE tenants.slug = :tenant_slug
    ON CONFLICT (tenant_id, message_id)
    DO UPDATE SET message_id = EXCLUDED.message_id
    WHERE messages_outbox.subject = EXCLUDED.subject
      AND messages_outbox.partition_key = EXCLUDED.partition_key
      AND messages_outbox.envelope = EXCLUDED.envelope
      AND messages_outbox.max_attempts = EXCLUDED.max_attempts
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
            max_attempts,
            available_at
        FROM messages_outbox AS candidate
        WHERE candidate.published_at IS NULL
          AND candidate.dead_lettered_at IS NULL
          AND candidate.tenant_id = :tenant_id
          AND candidate.available_at <= now()
          AND NOT EXISTS (
              SELECT 1
              FROM messages_outbox AS earlier
              WHERE earlier.tenant_id = candidate.tenant_id
                AND earlier.subject = candidate.subject
                AND earlier.partition_key = candidate.partition_key
                AND earlier.sequence < candidate.sequence
                AND earlier.published_at IS NULL
                AND earlier.dead_lettered_at IS NULL
          )
        ORDER BY candidate.available_at, candidate.sequence
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
            priority,
            max_attempts,
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
            COALESCE(CAST(pending.envelope #>> '{payload,event,priority}' AS integer), 0),
            pending.max_attempts,
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

_RECORD_OUTBOX_FAILURE = text(
    """
    WITH failed AS (
        UPDATE messages_outbox
        SET attempts = attempts + 1,
            available_at = :retry_at,
            last_error = :reason,
            dead_lettered_at = CASE
                WHEN attempts + 1 >= max_attempts THEN now()
                ELSE NULL
            END
        WHERE sequence = :sequence
          AND tenant_id = :tenant_id
          AND published_at IS NULL
          AND dead_lettered_at IS NULL
        RETURNING *
    ), quarantined AS (
        INSERT INTO durable_dead_letters (
            tenant_id, source_type, source_id, message_id, lane, partition_key,
            message_type, schema_version, failure_class, payload_checksum,
            attempt_count, last_error, quarantined_at
        )
        SELECT
            tenant_id, 'OUTBOX', sequence, message_id, subject, partition_key,
            envelope ->> 'message_type',
            CAST(envelope ->> 'schema_version' AS integer),
            :failure_class,
            encode(digest(envelope::text, 'sha256'), 'hex'),
            attempts, last_error, dead_lettered_at
        FROM failed
        WHERE dead_lettered_at IS NOT NULL
        RETURNING id
    )
    SELECT sequence, dead_lettered_at IS NOT NULL AS dead_lettered
    FROM failed
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
        SELECT candidate.id
        FROM durable_work_queue AS candidate
        WHERE candidate.lane = :lane
          AND candidate.tenant_id = :tenant_id
          AND candidate.delivery_attempt < candidate.max_attempts
          AND mod(candidate.shard_key, :shard_count) = :shard_id
          AND (
              :accept_all_schema_versions
              OR candidate.schema_version = ANY(CAST(:supported_schema_versions AS integer[]))
          )
          AND (
              (candidate.state = 'READY' AND candidate.available_at <= now())
              OR (candidate.state = 'CLAIMED' AND candidate.lease_expires_at <= now())
          )
          AND NOT EXISTS (
              SELECT 1
              FROM durable_work_queue AS earlier
              WHERE earlier.tenant_id = candidate.tenant_id
                AND earlier.lane = candidate.lane
                AND earlier.partition_key = candidate.partition_key
                AND earlier.id < candidate.id
                AND earlier.state IN ('READY', 'CLAIMED')
          )
        ORDER BY candidate.priority DESC, candidate.available_at, candidate.id
        FOR UPDATE SKIP LOCKED
        LIMIT :limit
    )
    UPDATE durable_work_queue AS queue
    SET state = 'CLAIMED',
        claimed_by = :consumer_id,
        fencing_token = queue.fencing_token + 1,
        lease_expires_at = now() + make_interval(secs => :lease_seconds),
        last_claimed_at = clock_timestamp(),
        delivery_attempt = queue.delivery_attempt + 1,
        updated_at = now()
    FROM candidates
    WHERE queue.id = candidates.id
    RETURNING
        queue.id,
        queue.shard_key,
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
      AND tenant_id = :tenant_id
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
      AND tenant_id = :tenant_id
      AND state = 'CLAIMED'
      AND claimed_by = :consumer_id
      AND fencing_token = :fencing_token
      AND lease_expires_at > now()
    RETURNING id
    """
)

_RELEASE = text(
    """
    WITH failed AS (
        UPDATE durable_work_queue
        SET state = CASE
                WHEN delivery_attempt >= max_attempts THEN 'DEAD_LETTER'
                ELSE 'READY'
            END,
            claimed_by = NULL,
            lease_expires_at = NULL,
            available_at = :retry_at,
            last_error = :reason,
            dead_lettered_at = CASE
                WHEN delivery_attempt >= max_attempts THEN now()
                ELSE NULL
            END,
            updated_at = now()
        WHERE id = :queue_id
          AND tenant_id = :tenant_id
          AND state = 'CLAIMED'
          AND claimed_by = :consumer_id
          AND fencing_token = :fencing_token
          AND lease_expires_at > now()
        RETURNING *
    ), quarantined AS (
        INSERT INTO durable_dead_letters (
            tenant_id, source_type, source_id, message_id, lane, partition_key,
            message_type, schema_version, failure_class, payload_checksum,
            attempt_count, last_error, quarantined_at
        )
        SELECT
            tenant_id, 'QUEUE', id, message_id, lane, partition_key,
            message_type, schema_version, :failure_class,
            encode(digest(envelope::text, 'sha256'), 'hex'),
            delivery_attempt, last_error, dead_lettered_at
        FROM failed
        WHERE state = 'DEAD_LETTER'
        RETURNING id
    )
    SELECT id FROM failed
    """
)

_LIST_DEAD_LETTERS = text(
    """
    SELECT *
    FROM durable_dead_letters
    WHERE tenant_id = :tenant_id
    ORDER BY quarantined_at, id
    """
)

_SELECT_DEAD_LETTER_FOR_UPDATE = text(
    """
    SELECT *
    FROM durable_dead_letters
    WHERE id = :dead_letter_id
      AND tenant_id = :tenant_id
      AND resolution = 'PENDING'
    FOR UPDATE
    """
)

_REPLAY_QUEUE = text(
    """
    UPDATE durable_work_queue
    SET state = 'READY',
        delivery_attempt = 0,
        claimed_by = NULL,
        lease_expires_at = NULL,
        available_at = now(),
        last_error = NULL,
        dead_lettered_at = NULL,
        updated_at = now()
    WHERE id = :source_id
      AND tenant_id = :tenant_id
      AND state = 'DEAD_LETTER'
    RETURNING id
    """
)

_REPLAY_OUTBOX = text(
    """
    UPDATE messages_outbox
    SET attempts = 0,
        available_at = now(),
        last_error = NULL,
        dead_lettered_at = NULL
    WHERE sequence = :source_id
      AND tenant_id = :tenant_id
      AND published_at IS NULL
      AND dead_lettered_at IS NOT NULL
    RETURNING sequence
    """
)

_RESOLVE_DEAD_LETTER = text(
    """
    UPDATE durable_dead_letters
    SET resolution = 'REPLAYED', resolved_at = now(), resolved_by = :actor_id
    WHERE id = :dead_letter_id
      AND tenant_id = :tenant_id
      AND resolution = 'PENDING'
    RETURNING id
    """
)

_DIAGNOSTICS = text(
    """
    SELECT
        count(*) FILTER (WHERE state IN ('READY', 'CLAIMED')) AS queue_depth,
        EXTRACT(EPOCH FROM now() - min(available_at) FILTER (
            WHERE state = 'READY' AND available_at <= now()
        )) AS oldest_eligible_age_seconds,
        count(*) FILTER (WHERE state = 'CLAIMED') AS claimed_count,
        count(*) FILTER (
            WHERE state = 'CLAIMED' AND lease_expires_at <= now()
        ) AS expired_claim_count,
        COALESCE(sum(GREATEST(delivery_attempt - 1, 0)), 0) AS redelivery_count,
        count(*) FILTER (WHERE state = 'DEAD_LETTER') AS poison_message_count,
        (SELECT count(*) FROM durable_dead_letters
         WHERE resolution = 'PENDING') AS dead_letter_count,
        (SELECT count(*) FROM messages_outbox
         WHERE published_at IS NULL AND dead_lettered_at IS NULL) AS outbox_pending_count,
        (SELECT EXTRACT(EPOCH FROM now() - min(available_at))
         FROM messages_outbox
         WHERE published_at IS NULL
           AND dead_lettered_at IS NULL
           AND available_at <= now()) AS outbox_oldest_age_seconds,
        (SELECT COALESCE(sum(GREATEST(
            attempts - CASE WHEN published_at IS NULL THEN 0 ELSE 1 END,
            0
        )), 0)
         FROM messages_outbox) AS outbox_retry_count,
        (SELECT count(*) FROM messages_outbox
         WHERE dead_lettered_at IS NOT NULL) AS outbox_dead_letter_count,
        count(*) FILTER (
            WHERE state = 'COMPLETED'
              AND completed_at >= clock_timestamp() - interval '1 minute'
        ) AS completed_last_minute,
        percentile_cont(0.95) WITHIN GROUP (
            ORDER BY GREATEST(EXTRACT(EPOCH FROM last_claimed_at - available_at), 0)
        ) FILTER (
            WHERE last_claimed_at >= clock_timestamp() - interval '1 minute'
        ) AS claim_p95_latency_seconds,
        current_setting('server_version') AS postgres_version,
        pg_is_in_recovery() AS postgres_in_recovery
    FROM durable_work_queue
    """
)

_SHARD_DIAGNOSTICS = text(
    """
    WITH configured_shards AS (
        SELECT generate_series(0, :shard_count - 1) AS shard_id
    ), pressure AS (
        SELECT
            mod(shard_key, :shard_count) AS shard_id,
            count(*) AS queue_depth,
            EXTRACT(EPOCH FROM clock_timestamp() - min(available_at) FILTER (
                WHERE state = 'READY' AND available_at <= clock_timestamp()
            )) AS oldest_eligible_age_seconds
        FROM durable_work_queue
        WHERE state IN ('READY', 'CLAIMED')
        GROUP BY mod(shard_key, :shard_count)
    )
    SELECT
        configured_shards.shard_id,
        COALESCE(pressure.queue_depth, 0) AS queue_depth,
        pressure.oldest_eligible_age_seconds
    FROM configured_shards
    LEFT JOIN pressure USING (shard_id)
    ORDER BY configured_shards.shard_id
    """
)

_DELETE_COMPLETED_QUEUE = text(
    """
    DELETE FROM durable_work_queue
    WHERE id IN (
        SELECT id
        FROM durable_work_queue
        WHERE state = 'COMPLETED' AND completed_at < :before
        ORDER BY completed_at, id
        FOR UPDATE SKIP LOCKED
        LIMIT :limit
    )
    RETURNING id
    """
)

_DELETE_PUBLISHED_OUTBOX = text(
    """
    DELETE FROM messages_outbox
    WHERE sequence IN (
        SELECT sequence
        FROM messages_outbox
        WHERE published_at < :before
        ORDER BY published_at, sequence
        FOR UPDATE SKIP LOCKED
        LIMIT :limit
    )
    RETURNING sequence
    """
)

_DELETE_CONSUMED_INBOX = text(
    """
    DELETE FROM consumed_messages
    WHERE (consumer_name, tenant_id, message_id) IN (
        SELECT consumer_name, tenant_id, message_id
        FROM consumed_messages
        WHERE consumed_at < :before
        ORDER BY consumed_at, consumer_name, message_id
        FOR UPDATE SKIP LOCKED
        LIMIT :limit
    )
    RETURNING message_id
    """
)

_DELETE_RESOLVED_DEAD_LETTERS = text(
    """
    DELETE FROM durable_dead_letters
    WHERE id IN (
        SELECT id
        FROM durable_dead_letters
        WHERE resolution <> 'PENDING' AND resolved_at < :before
        ORDER BY resolved_at, id
        FOR UPDATE SKIP LOCKED
        LIMIT :limit
    )
    RETURNING id
    """
)


class PostgresDurableTransport(PostgresRepositoryBase, DurableTransport):
    """SQLAlchemy async adapter for the authoritative PostgreSQL work queue."""

    def __init__(
        self,
        engine: AsyncEngine,
        *,
        services: PostgresRepositoryServices | None = None,
    ) -> None:
        super().__init__(engine, services=services)

    @instrument_async_operation("messaging", "enqueue")
    async def enqueue(
        self,
        lane: str,
        envelope: DurableEnvelope,
        *,
        available_at: datetime | None = None,
        priority: int = 0,
        max_attempts: int = 25,
    ) -> int:
        if max_attempts < 1:
            raise ValueError("maximum delivery attempts must be at least 1")
        parameters = {
            "message_id": envelope.message_id,
            "lane": lane,
            "partition_key": envelope.partition_key,
            "message_type": envelope.message_type,
            "schema_version": envelope.schema_version,
            "envelope": self._services.codec.dumps(envelope.model_dump(mode="json")),
            "priority": priority,
            "max_attempts": max_attempts,
            "available_at": available_at,
            "tenant_slug": envelope.tenant_id,
        }
        async with self._services.transactions.tenant(envelope.tenant_id) as (
            connection,
            _tenant_uuid,
        ):
            result = await connection.execute(_ENQUEUE, parameters)
            queue_id = result.scalar_one_or_none()
        if queue_id is None:
            raise MessageIdentityConflict(
                f"message {envelope.message_id} already has different queue content"
            )
        return int(queue_id)

    @instrument_async_operation("messaging", "enqueue-outbox")
    async def enqueue_outbox(
        self,
        subject: str,
        envelope: DurableEnvelope,
        *,
        available_at: datetime | None = None,
        max_attempts: int = 25,
    ) -> int:
        if max_attempts < 1:
            raise ValueError("maximum delivery attempts must be at least 1")
        async with self._services.transactions.tenant(envelope.tenant_id) as (
            connection,
            _tenant_uuid,
        ):
            result = await connection.execute(
                _ENQUEUE_OUTBOX,
                {
                    "message_id": envelope.message_id,
                    "subject": subject,
                    "partition_key": envelope.partition_key,
                    "envelope": self._services.codec.dumps(envelope.model_dump(mode="json")),
                    "available_at": available_at,
                    "max_attempts": max_attempts,
                    "tenant_slug": envelope.tenant_id,
                },
            )
            sequence = result.scalar_one_or_none()
        if sequence is None:
            raise MessageIdentityConflict(
                f"message {envelope.message_id} already has different outbox content"
            )
        return int(sequence)

    @instrument_async_operation("messaging", "publish-outbox")
    async def publish_outbox(self, *, tenant_id: str, limit: int) -> int:
        if limit < 1:
            raise ValueError("outbox publish limit must be at least 1")
        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            tenant_uuid,
        ):
            result = await connection.execute(
                _PUBLISH_OUTBOX,
                {"tenant_id": tenant_uuid, "limit": limit},
            )
            published = result.scalars().all()
        return len(published)

    @instrument_async_operation("messaging", "outbox-failure")
    async def record_outbox_failure(
        self,
        sequence: int,
        *,
        tenant_id: str,
        retry_at: datetime,
        reason: str,
        failure_class: str,
    ) -> bool:
        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            tenant_uuid,
        ):
            row = (
                (
                    await connection.execute(
                        _RECORD_OUTBOX_FAILURE,
                        {
                            "sequence": sequence,
                            "tenant_id": tenant_uuid,
                            "retry_at": retry_at,
                            "reason": reason,
                            "failure_class": failure_class,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise NotFoundError(
                "pending outbox sequence",
                sequence,
                message=f"pending outbox sequence {sequence} does not exist",
            )
        return bool(row["dead_lettered"])

    @instrument_async_operation("messaging", "record-consumed")
    async def record_consumed(
        self,
        consumer_name: str,
        envelope: DurableEnvelope,
    ) -> bool:
        async with self._services.transactions.tenant(envelope.tenant_id) as (
            connection,
            _tenant_uuid,
        ):
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
            raise NotFoundError(
                "tenant",
                envelope.tenant_id,
                message=f"tenant {envelope.tenant_id!r} does not exist",
            )
        return bool(row["inserted"])

    @instrument_async_operation("messaging", "claim")
    async def claim(
        self,
        lane: str,
        consumer_id: str,
        *,
        tenant_id: str,
        limit: int,
        lease_duration: timedelta,
        shard_id: int = 0,
        shard_count: int = 1,
        supported_schema_versions: tuple[int, ...] | None = None,
    ) -> list[WorkClaim]:
        lease_seconds = _positive_lease_seconds(lease_duration)
        if limit < 1:
            raise ValueError("claim limit must be at least 1")
        _validate_shard(shard_id, shard_count)
        if supported_schema_versions is not None and (
            not supported_schema_versions
            or any(version < 1 for version in supported_schema_versions)
        ):
            raise ValueError("supported schema versions must contain positive integers")

        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            tenant_uuid,
        ):
            result = await connection.execute(
                _CLAIM,
                {
                    "lane": lane,
                    "tenant_id": tenant_uuid,
                    "consumer_id": consumer_id,
                    "limit": limit,
                    "lease_seconds": lease_seconds,
                    "shard_id": shard_id,
                    "shard_count": shard_count,
                    "accept_all_schema_versions": supported_schema_versions is None,
                    "supported_schema_versions": list(supported_schema_versions or ()),
                },
            )
            rows = result.mappings().all()
        return [_to_work_claim(row) for row in rows]

    @instrument_async_operation("messaging", "wait")
    async def wait_for_work(
        self,
        lane: str,
        *,
        tenant_id: str,
        timeout_seconds: float,
    ) -> bool:
        if not lane:
            raise ValueError("work lane must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("work wait timeout must be positive")
        async with self._engine.connect() as pooled_connection:
            raw_connection = await pooled_connection.get_raw_connection()
            connection = raw_connection.driver_connection
            if connection is None:
                raise RuntimeError("PostgreSQL notification driver connection is unavailable")
            listener_installed = False
            channel = ""
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

            try:
                await connection.execute("SET ROLE amesh_runtime")
                tenant_uuid = await resolve_active_tenant_id_asyncpg(connection, tenant_id)
                await connection.execute(
                    "SELECT set_config('amesh.tenant_id', $1, false)",
                    str(tenant_uuid),
                )
                channel = f"amesh_work_{str(tenant_uuid).replace('-', '')}"
                await connection.add_listener(channel, listener)
                listener_installed = True
                ready = await connection.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM durable_work_queue
                        WHERE lane = $1
                          AND tenant_id = $2
                          AND state = 'READY'
                          AND available_at <= now()
                    )
                    """,
                    lane,
                    tenant_uuid,
                )
                if ready:
                    return True
                try:
                    await asyncio.wait_for(wake.wait(), timeout=timeout_seconds)
                except TimeoutError:
                    return False
                return True
            finally:

                async def cleanup_connection() -> None:
                    try:
                        if listener_installed:
                            await connection.remove_listener(channel, listener)
                    finally:
                        try:
                            await connection.execute("RESET amesh.tenant_id")
                        finally:
                            await connection.execute("RESET ROLE")

                cleanup = asyncio.create_task(cleanup_connection())
                cleanup_cancellation: asyncio.CancelledError | None = None
                while not cleanup.done():
                    try:
                        await asyncio.shield(cleanup)
                    except asyncio.CancelledError as error:
                        cleanup_cancellation = error
                await cleanup
                if cleanup_cancellation is not None:
                    raise cleanup_cancellation

    @instrument_async_operation("messaging", "extend")
    async def extend(
        self,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        lease_duration: timedelta,
        *,
        tenant_id: str,
    ) -> datetime:
        lease_seconds = _positive_lease_seconds(lease_duration)
        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            tenant_uuid,
        ):
            result = await connection.execute(
                _EXTEND,
                {
                    "queue_id": queue_id,
                    "tenant_id": tenant_uuid,
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

    @instrument_async_operation("messaging", "acknowledge")
    async def acknowledge(
        self,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        *,
        tenant_id: str,
    ) -> None:
        await self._mutate_claim(
            _ACKNOWLEDGE,
            queue_id=queue_id,
            consumer_id=consumer_id,
            fencing_token=fencing_token,
            tenant_id=tenant_id,
        )

    @instrument_async_operation("messaging", "release")
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
    ) -> None:
        await self._mutate_claim(
            _RELEASE,
            queue_id=queue_id,
            consumer_id=consumer_id,
            fencing_token=fencing_token,
            tenant_id=tenant_id,
            retry_at=retry_at,
            reason=reason,
            failure_class=failure_class,
        )

    @instrument_async_operation("messaging", "list-dead-letters")
    async def list_dead_letters(self, *, tenant_id: str) -> list[DeadLetterRecord]:
        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            tenant_uuid,
        ):
            rows = (
                (
                    await connection.execute(
                        _LIST_DEAD_LETTERS,
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_dead_letter(row) for row in rows]

    @instrument_async_operation("messaging", "replay-dead-letter")
    async def replay_dead_letter(
        self,
        dead_letter_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> None:
        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            tenant_uuid,
        ):
            dead_letter = (
                (
                    await connection.execute(
                        _SELECT_DEAD_LETTER_FOR_UPDATE,
                        {"dead_letter_id": dead_letter_id, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if dead_letter is None:
                raise DeadLetterReplayError(f"pending dead letter {dead_letter_id} does not exist")
            replay_statement = (
                _REPLAY_QUEUE if dead_letter["source_type"] == "QUEUE" else _REPLAY_OUTBOX
            )
            replayed = await connection.scalar(
                replay_statement,
                {"source_id": dead_letter["source_id"], "tenant_id": tenant_uuid},
            )
            if replayed is None:
                raise DeadLetterReplayError(
                    f"dead letter {dead_letter_id} source is not replayable"
                )
            await connection.execute(
                _RESOLVE_DEAD_LETTER,
                {
                    "dead_letter_id": dead_letter_id,
                    "tenant_id": tenant_uuid,
                    "actor_id": actor_id,
                },
            )

    @instrument_async_operation("messaging", "diagnostics")
    async def diagnostics(
        self,
        *,
        tenant_id: str,
        shard_count: int = 16,
    ) -> TransportDiagnostics:
        _validate_shard(0, shard_count)
        started = perf_counter()
        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            _tenant_uuid,
        ):
            row = (await connection.execute(_DIAGNOSTICS)).mappings().one()
            shard_rows = (
                (await connection.execute(_SHARD_DIAGNOSTICS, {"shard_count": shard_count}))
                .mappings()
                .all()
            )
        transaction_latency_ms = (perf_counter() - started) * 1_000
        shards = tuple(
            QueueShardDiagnostics(
                shard_id=item["shard_id"],
                queue_depth=item["queue_depth"],
                oldest_eligible_age_seconds=item["oldest_eligible_age_seconds"],
            )
            for item in shard_rows
        )
        average_depth = sum(item.queue_depth for item in shards) / shard_count
        shard_skew_ratio = (
            max(item.queue_depth for item in shards) / average_depth if average_depth else 0.0
        )
        diagnostics = TransportDiagnostics(
            queue_depth=row["queue_depth"],
            oldest_eligible_age_seconds=row["oldest_eligible_age_seconds"],
            claimed_count=row["claimed_count"],
            expired_claim_count=row["expired_claim_count"],
            redelivery_count=row["redelivery_count"],
            poison_message_count=row["poison_message_count"],
            dead_letter_count=row["dead_letter_count"],
            outbox_pending_count=row["outbox_pending_count"],
            outbox_oldest_age_seconds=row["outbox_oldest_age_seconds"],
            outbox_retry_count=row["outbox_retry_count"],
            outbox_dead_letter_count=row["outbox_dead_letter_count"],
            completed_last_minute=row["completed_last_minute"],
            completion_throughput_per_second=row["completed_last_minute"] / 60,
            claim_p95_latency_seconds=row["claim_p95_latency_seconds"],
            shard_count=shard_count,
            shard_skew_ratio=shard_skew_ratio,
            shards=shards,
            postgres_available=True,
            postgres_version=row["postgres_version"],
            postgres_in_recovery=row["postgres_in_recovery"],
            transaction_latency_ms=transaction_latency_ms,
        )
        QUEUE_DEPTH.set(diagnostics.queue_depth)
        QUEUE_OLDEST_AGE.set(diagnostics.oldest_eligible_age_seconds or 0)
        return diagnostics

    @instrument_async_operation("messaging", "retention")
    async def purge_terminal(
        self,
        *,
        tenant_id: str,
        before: datetime,
        limit: int = 1_000,
    ) -> TransportRetentionResult:
        if limit < 1:
            raise ValueError("retention limit must be at least 1")
        parameters = {"before": before, "limit": limit}
        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            _tenant_uuid,
        ):
            queue_rows = len((await connection.execute(_DELETE_COMPLETED_QUEUE, parameters)).all())
            outbox_rows = len(
                (await connection.execute(_DELETE_PUBLISHED_OUTBOX, parameters)).all()
            )
            inbox_rows = len((await connection.execute(_DELETE_CONSUMED_INBOX, parameters)).all())
            dead_letter_rows = len(
                (await connection.execute(_DELETE_RESOLVED_DEAD_LETTERS, parameters)).all()
            )
        return TransportRetentionResult(
            queue_rows=queue_rows,
            outbox_rows=outbox_rows,
            inbox_rows=inbox_rows,
            dead_letter_rows=dead_letter_rows,
        )

    async def _mutate_claim(
        self,
        statement: TextClause,
        *,
        queue_id: int,
        consumer_id: str,
        fencing_token: int,
        tenant_id: str,
        **parameters: object,
    ) -> None:
        values = {
            "queue_id": queue_id,
            "consumer_id": consumer_id,
            "fencing_token": fencing_token,
            **parameters,
        }
        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            tenant_uuid,
        ):
            values["tenant_id"] = tenant_uuid
            result = await connection.execute(statement, values)
            mutated_id = result.scalar_one_or_none()
        if mutated_id is None:
            raise _stale_claim(queue_id, consumer_id, fencing_token)


def _positive_lease_seconds(lease_duration: timedelta) -> float:
    lease_seconds = lease_duration.total_seconds()
    if lease_seconds <= 0:
        raise ValueError("lease duration must be positive")
    return lease_seconds


def _validate_shard(shard_id: int, shard_count: int) -> None:
    if shard_count < 1 or shard_count > 65_536:
        raise ValueError("shard count must be between 1 and 65536")
    if shard_id < 0 or shard_id >= shard_count:
        raise ValueError("shard id must be within the configured shard count")


def _to_work_claim(row: RowMapping) -> WorkClaim:
    return WorkClaim(
        queue_id=row["id"],
        shard_key=row["shard_key"],
        lane=row["lane"],
        consumer_id=row["claimed_by"],
        fencing_token=row["fencing_token"],
        lease_expires_at=row["lease_expires_at"],
        delivery_attempt=row["delivery_attempt"],
        envelope=DurableEnvelope.model_validate(row["envelope"]),
    )


def _to_dead_letter(row: RowMapping) -> DeadLetterRecord:
    return DeadLetterRecord(
        dead_letter_id=row["id"],
        source_type=row["source_type"],
        source_id=row["source_id"],
        message_id=row["message_id"],
        lane=row["lane"],
        partition_key=row["partition_key"],
        message_type=row["message_type"],
        schema_version=row["schema_version"],
        failure_class=row["failure_class"],
        payload_checksum=row["payload_checksum"],
        attempt_count=row["attempt_count"],
        last_error=row["last_error"],
        quarantined_at=row["quarantined_at"],
        resolution=row["resolution"],
        resolved_at=row["resolved_at"],
        resolved_by=row["resolved_by"],
    )


def _stale_claim(queue_id: int, consumer_id: str, fencing_token: int) -> StaleWorkClaimError:
    return StaleWorkClaimError(
        "queue claim is expired or superseded: "
        f"queue_id={queue_id}, consumer_id={consumer_id!r}, fencing_token={fencing_token}"
    )
