from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.observability import instrument_async_operation
from amesh.ports import (
    WORKER_PROTOCOL_VERSION,
    WorkerClaimHeartbeat,
    WorkerCompatibility,
    WorkerCompatibilityError,
    WorkerFenceError,
    WorkerInventory,
    WorkerLiveness,
    WorkerLossPolicy,
    WorkerRegistration,
    WorkerRepository,
    WorkerStatus,
    WorkerTaskClaim,
)
from amesh.ports.errors import NotFoundError

from .durable_transport import PostgresDurableTransport
from .repository_support import PostgresRepositoryBase

_REGISTER_WORKER = text(
    """
    WITH changed AS (
        INSERT INTO workers (
            id, tenant_id, worker_group, instance_name, version, protocol_version,
            status, capabilities, runner_types, capacity, labels, last_heartbeat_at,
            resource_version, created_by, updated_by, registered_at, updated_at
        ) VALUES (
            :worker_id, :tenant_id, :worker_group, :instance_name, :version,
            :protocol_version, 'READY', CAST(:capabilities AS jsonb),
            CAST(:runner_types AS jsonb), :capacity, CAST(:labels AS jsonb),
            clock_timestamp(), 1, :actor_id, :actor_id, clock_timestamp(), clock_timestamp()
        )
        ON CONFLICT (tenant_id, worker_group, instance_name) DO UPDATE SET
            version = EXCLUDED.version,
            protocol_version = EXCLUDED.protocol_version,
            status = 'READY',
            capabilities = EXCLUDED.capabilities,
            runner_types = EXCLUDED.runner_types,
            capacity = EXCLUDED.capacity,
            labels = EXCLUDED.labels,
            last_heartbeat_at = clock_timestamp(),
            heartbeat_progress = '{}'::jsonb,
            resource_usage = '{}'::jsonb,
            cancellation_acknowledged = false,
            resource_version = workers.resource_version + 1,
            updated_by = EXCLUDED.updated_by,
            updated_at = clock_timestamp()
        RETURNING *
    )
    SELECT changed.*, tenants.slug AS tenant_slug, clock_timestamp() AS database_now,
           (
               SELECT count(*)
               FROM task_attempts
               WHERE task_attempts.tenant_id = changed.tenant_id
                 AND task_attempts.worker_id = changed.id
                 AND task_attempts.state = 'RUNNING'
                 AND task_attempts.lease_expires_at > clock_timestamp()
           ) AS claimed_work
    FROM changed
    JOIN tenants ON tenants.id = changed.tenant_id
    """
)

_LOCK_WORKER = text(
    """
    SELECT workers.*,
           (
               SELECT count(*)
               FROM task_attempts
               WHERE task_attempts.tenant_id = workers.tenant_id
                 AND task_attempts.worker_id = workers.id
                 AND task_attempts.state = 'RUNNING'
                 AND task_attempts.lease_expires_at > clock_timestamp()
           ) AS claimed_work,
           clock_timestamp() AS database_now
    FROM workers
    WHERE workers.id = :worker_id AND workers.tenant_id = :tenant_id
    FOR UPDATE
    """
)

_CLAIM_TASKS = text(
    """
    WITH candidates AS (
        SELECT
            queue.id AS queue_id,
            attempts.id AS attempt_id,
            attempts.task_run_id,
            attempts.attempt,
            runs.execution_id,
            runs.task_path,
            queue.fencing_token + 1 AS next_fencing_token
        FROM durable_work_queue AS queue
        JOIN task_runs AS runs
          ON runs.tenant_id = queue.tenant_id
         AND runs.id::text = COALESCE(
             queue.envelope #>> '{payload,task_run_id}',
             queue.envelope #>> '{payload,taskRunId}'
         )
        JOIN task_attempts AS attempts
          ON attempts.tenant_id = runs.tenant_id
         AND attempts.task_run_id = runs.id
         AND attempts.attempt = runs.current_attempt
        JOIN executions ON executions.id = runs.execution_id
        JOIN flow_revisions ON flow_revisions.id = executions.flow_revision_id
        JOIN LATERAL (
            SELECT item.definition
            FROM jsonb_array_elements(flow_revisions.canonical_definition -> 'tasks')
                AS item(definition)
            WHERE item.definition ->> 'id' = runs.task_path
        ) AS task_definition ON true
        JOIN workers
          ON workers.id = :worker_id
         AND workers.tenant_id = queue.tenant_id
        WHERE queue.tenant_id = :tenant_id
          AND queue.lane = 'task-dispatch'
          AND queue.message_type = 'DispatchTaskRun'
          AND queue.schema_version = 1
          AND queue.delivery_attempt < queue.max_attempts
          AND (
              (queue.state = 'READY' AND queue.available_at <= clock_timestamp())
              OR (queue.state = 'CLAIMED' AND queue.lease_expires_at <= clock_timestamp())
          )
          AND NOT EXISTS (
              SELECT 1
              FROM durable_work_queue AS earlier
              WHERE earlier.tenant_id = queue.tenant_id
                AND earlier.lane = queue.lane
                AND earlier.partition_key = queue.partition_key
                AND earlier.id < queue.id
                AND earlier.state IN ('READY', 'CLAIMED')
          )
          AND attempts.state = 'RUNNING'
          AND (attempts.lease_expires_at IS NULL OR attempts.lease_expires_at <= clock_timestamp())
          AND (
              jsonb_array_length(COALESCE(workers.capabilities -> 'taskTypes', '[]'::jsonb)) = 0
              OR (workers.capabilities -> 'taskTypes') ? (task_definition.definition ->> 'type')
          )
          AND (
              task_definition.definition ->> 'runner' IS NULL
              OR workers.runner_types ? (task_definition.definition ->> 'runner')
          )
          AND (
              task_definition.definition ->> 'workerGroup' IS NULL
              OR workers.worker_group = task_definition.definition ->> 'workerGroup'
          )
        ORDER BY queue.priority DESC, queue.available_at, queue.id
        FOR UPDATE OF queue, attempts SKIP LOCKED
        LIMIT :limit
    ), claimed_queue AS (
        UPDATE durable_work_queue AS queue
        SET state = 'CLAIMED',
            claimed_by = :consumer_id,
            fencing_token = candidates.next_fencing_token,
            lease_expires_at = clock_timestamp() + make_interval(secs => :lease_seconds),
            last_claimed_at = clock_timestamp(),
            delivery_attempt = queue.delivery_attempt + 1,
            updated_at = clock_timestamp()
        FROM candidates
        WHERE queue.id = candidates.queue_id
        RETURNING
            queue.id, queue.message_id, queue.fencing_token, queue.lease_expires_at,
            queue.delivery_attempt, candidates.attempt_id, candidates.task_run_id,
            candidates.attempt, candidates.execution_id, candidates.task_path
    ), claimed_attempt AS (
        UPDATE task_attempts AS attempts
        SET worker_id = :worker_id,
            queue_id = claimed_queue.id,
            fencing_token = claimed_queue.fencing_token,
            lease_expires_at = claimed_queue.lease_expires_at,
            last_heartbeat_at = clock_timestamp(),
            progress = '{}'::jsonb,
            resource_usage = '{}'::jsonb,
            cancellation_acknowledged = false
        FROM claimed_queue
        WHERE attempts.id = claimed_queue.attempt_id
        RETURNING
            claimed_queue.id AS queue_id,
            claimed_queue.message_id,
            attempts.worker_id,
            attempts.task_run_id,
            claimed_queue.execution_id,
            claimed_queue.task_path,
            attempts.attempt,
            attempts.fencing_token,
            attempts.lease_expires_at,
            claimed_queue.delivery_attempt
    )
    SELECT * FROM claimed_attempt ORDER BY queue_id
    """
)

_HEARTBEAT_WORKER = text(
    """
    UPDATE workers
    SET status = :status,
        last_heartbeat_at = clock_timestamp(),
        heartbeat_progress = CAST(:progress AS jsonb),
        resource_usage = CAST(:resource_usage AS jsonb),
        cancellation_acknowledged = :cancellation_acknowledged,
        resource_version = resource_version + 1,
        updated_by = :actor_id,
        updated_at = clock_timestamp()
    WHERE id = :worker_id
      AND tenant_id = :tenant_id
      AND resource_version = :expected_version
      AND status <> 'STOPPED'
    RETURNING id
    """
)

_RENEW_TASK_CLAIM = text(
    """
    WITH renewed_queue AS (
        UPDATE durable_work_queue
        SET lease_expires_at = clock_timestamp() + make_interval(secs => :lease_seconds),
            updated_at = clock_timestamp()
        WHERE id = :queue_id
          AND tenant_id = :tenant_id
          AND state = 'CLAIMED'
          AND claimed_by = :consumer_id
          AND fencing_token = :fencing_token
          AND lease_expires_at > clock_timestamp()
        RETURNING lease_expires_at
    ), renewed_attempt AS (
        UPDATE task_attempts
        SET lease_expires_at = renewed_queue.lease_expires_at,
            last_heartbeat_at = clock_timestamp(),
            progress = CAST(:progress AS jsonb),
            resource_usage = CAST(:resource_usage AS jsonb),
            cancellation_acknowledged = :cancellation_acknowledged
        FROM renewed_queue
        WHERE task_attempts.tenant_id = :tenant_id
          AND task_attempts.task_run_id = :task_run_id
          AND task_attempts.attempt = :attempt
          AND task_attempts.state = 'RUNNING'
          AND task_attempts.worker_id = :worker_id
          AND task_attempts.queue_id = :queue_id
          AND task_attempts.fencing_token = :fencing_token
          AND task_attempts.lease_expires_at > clock_timestamp()
        RETURNING task_attempts.lease_expires_at
    )
    SELECT lease_expires_at FROM renewed_attempt
    """
)

_DRAIN_WORKER = text(
    """
    UPDATE workers
    SET status = 'DRAINING',
        resource_version = resource_version + 1,
        updated_by = :actor_id,
        updated_at = clock_timestamp()
    WHERE id = :worker_id
      AND tenant_id = :tenant_id
      AND resource_version = :expected_version
      AND status IN ('STARTING', 'READY', 'DEGRADED', 'DRAINING')
    RETURNING id
    """
)

_INVENTORY = text(
    """
    SELECT workers.*, tenants.slug AS tenant_slug, clock_timestamp() AS database_now,
           (
               SELECT count(*)
               FROM task_attempts
               WHERE task_attempts.tenant_id = workers.tenant_id
                 AND task_attempts.worker_id = workers.id
                 AND task_attempts.state = 'RUNNING'
                 AND task_attempts.lease_expires_at > clock_timestamp()
           ) AS claimed_work
    FROM workers
    JOIN tenants ON tenants.id = workers.tenant_id
    WHERE workers.tenant_id = :tenant_id
      AND (
          CAST(:worker_id AS uuid) IS NULL
          OR workers.id = CAST(:worker_id AS uuid)
      )
    ORDER BY workers.worker_group, workers.instance_name
    """
)

_REQUEUE_EXPIRED = text(
    """
    WITH candidates AS (
        SELECT queue.id AS queue_id, attempts.id AS attempt_id
        FROM durable_work_queue AS queue
        JOIN task_attempts AS attempts
          ON attempts.tenant_id = queue.tenant_id
         AND attempts.queue_id = queue.id
        WHERE queue.tenant_id = :tenant_id
          AND queue.lane = 'task-dispatch'
          AND queue.state = 'CLAIMED'
          AND queue.lease_expires_at <= clock_timestamp()
          AND queue.delivery_attempt < queue.max_attempts
          AND attempts.state = 'RUNNING'
          AND attempts.lease_expires_at <= clock_timestamp()
        ORDER BY queue.lease_expires_at, queue.id
        FOR UPDATE OF queue, attempts SKIP LOCKED
        LIMIT :limit
    ), released_queue AS (
        UPDATE durable_work_queue AS queue
        SET state = 'READY', claimed_by = NULL, lease_expires_at = NULL,
            available_at = clock_timestamp(), last_error = 'worker lease expired',
            updated_at = clock_timestamp()
        FROM candidates
        WHERE queue.id = candidates.queue_id
        RETURNING candidates.attempt_id
    ), released_attempt AS (
        UPDATE task_attempts AS attempts
        SET worker_id = NULL, queue_id = NULL, lease_expires_at = NULL
        FROM released_queue
        WHERE attempts.id = released_queue.attempt_id
        RETURNING attempts.id
    )
    SELECT count(*) FROM released_attempt
    """
)

_FAIL_EXPIRED = text(
    """
    WITH candidates AS (
        SELECT queue.*, attempts.id AS attempt_id, attempts.task_run_id, attempts.attempt
        FROM durable_work_queue AS queue
        JOIN task_attempts AS attempts
          ON attempts.tenant_id = queue.tenant_id
         AND attempts.queue_id = queue.id
        WHERE queue.tenant_id = :tenant_id
          AND queue.lane = 'task-dispatch'
          AND queue.state = 'CLAIMED'
          AND queue.lease_expires_at <= clock_timestamp()
          AND (:fail_all OR queue.delivery_attempt >= queue.max_attempts)
          AND attempts.state = 'RUNNING'
          AND attempts.lease_expires_at <= clock_timestamp()
        ORDER BY queue.lease_expires_at, queue.id
        FOR UPDATE OF queue, attempts SKIP LOCKED
        LIMIT :limit
    ), failed_queue AS (
        UPDATE durable_work_queue AS queue
        SET state = 'DEAD_LETTER', claimed_by = NULL, lease_expires_at = NULL,
            last_error = 'worker lease expired', dead_lettered_at = clock_timestamp(),
            updated_at = clock_timestamp()
        FROM candidates
        WHERE queue.id = candidates.id
        RETURNING queue.id
    ), quarantined AS (
        INSERT INTO durable_dead_letters (
            tenant_id, source_type, source_id, message_id, lane, partition_key,
            message_type, schema_version, failure_class, payload_checksum,
            attempt_count, last_error, quarantined_at
        )
        SELECT
            candidates.tenant_id, 'QUEUE', candidates.id, candidates.message_id,
            candidates.lane, candidates.partition_key, candidates.message_type,
            candidates.schema_version, 'worker.lease_expired',
            encode(digest(candidates.envelope::text, 'sha256'), 'hex'),
            candidates.delivery_attempt, 'worker lease expired', clock_timestamp()
        FROM candidates
        JOIN failed_queue ON failed_queue.id = candidates.id
        RETURNING source_id
    ), failed_attempt AS (
        UPDATE task_attempts AS attempts
        SET state = 'FAILED', finished_at = clock_timestamp(),
            result = jsonb_build_object('error', 'worker lease expired'),
            lease_expires_at = NULL
        FROM candidates
        WHERE attempts.id = candidates.attempt_id
        RETURNING attempts.task_run_id, attempts.attempt
    ), failed_run AS (
        UPDATE task_runs AS runs
        SET state = 'FAILED', version = version + 1, retry_at = NULL,
            updated_at = clock_timestamp()
        FROM failed_attempt
        WHERE runs.id = failed_attempt.task_run_id
          AND runs.tenant_id = :tenant_id
          AND runs.current_attempt = failed_attempt.attempt
          AND runs.state = 'RUNNING'
        RETURNING runs.id, runs.execution_id, runs.version
    ), event AS (
        INSERT INTO task_run_events (
            tenant_id, task_run_id, execution_id, sequence, event_id, event_type,
            schema_version, idempotency_key, correlation_id, actor_id, reason,
            occurred_at, payload
        )
        SELECT
            :tenant_id, failed_run.id, failed_run.execution_id, failed_run.version,
            gen_random_uuid(), 'TaskRunFailed', 2,
            'worker-loss:' || failed_run.id::text || ':' || failed_run.version::text,
            gen_random_uuid(), 'worker-recovery', 'worker lease expired',
            clock_timestamp(), jsonb_build_object('error', 'worker lease expired')
        FROM failed_run
        RETURNING task_run_id
    )
    SELECT count(*) FROM event
    """
)


class PostgresWorkerRepository(PostgresRepositoryBase, WorkerRepository):
    """PostgreSQL-authoritative worker registration and fenced task dispatch."""

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)
        self._transport = PostgresDurableTransport(engine)

    async def register_worker(
        self,
        registration: WorkerRegistration,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> WorkerInventory:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _REGISTER_WORKER,
                        {
                            "worker_id": registration.worker_id,
                            "tenant_id": tenant_uuid,
                            "worker_group": registration.worker_group,
                            "instance_name": registration.instance_name,
                            "version": registration.version,
                            "protocol_version": registration.protocol_version,
                            "capabilities": self._services.codec.dumps(
                                {"taskTypes": list(registration.capabilities)}
                            ),
                            "runner_types": self._services.codec.dumps(registration.runner_types),
                            "capacity": registration.capacity,
                            "labels": self._services.codec.dumps(registration.labels),
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return _to_inventory(row)

    async def claim_tasks(
        self,
        worker_id: UUID,
        *,
        tenant_id: str,
        limit: int,
        lease_duration: timedelta,
    ) -> list[WorkerTaskClaim]:
        if limit < 1:
            raise ValueError("worker claim limit must be at least 1")
        lease_seconds = _positive_lease_seconds(lease_duration)
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            worker = (
                (
                    await connection.execute(
                        _LOCK_WORKER,
                        {"worker_id": worker_id, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if worker is None:
                raise NotFoundError(
                    "worker",
                    worker_id,
                    message=f"worker {worker_id} does not exist",
                )
            if int(worker["protocol_version"]) != WORKER_PROTOCOL_VERSION:
                raise WorkerCompatibilityError(
                    f"worker {worker_id} protocol {worker['protocol_version']} is incompatible"
                )
            if WorkerStatus(worker["status"]) is not WorkerStatus.READY or not _is_live(worker):
                return []
            available = max(int(worker["capacity"]) - int(worker["claimed_work"]), 0)
            if available == 0:
                return []
            rows = (
                (
                    await connection.execute(
                        _CLAIM_TASKS,
                        {
                            "worker_id": worker_id,
                            "tenant_id": tenant_uuid,
                            "consumer_id": str(worker_id),
                            "lease_seconds": lease_seconds,
                            "limit": min(limit, available),
                        },
                    )
                )
                .mappings()
                .all()
            )
        return [_to_task_claim(row) for row in rows]

    async def heartbeat_worker(
        self,
        worker_id: UUID,
        *,
        tenant_id: str,
        expected_version: int,
        status: WorkerStatus,
        lease_duration: timedelta,
        claims: tuple[WorkerClaimHeartbeat, ...] = (),
        progress: dict[str, object] | None = None,
        resource_usage: dict[str, object] | None = None,
        cancellation_acknowledged: bool = False,
        actor_id: str,
    ) -> WorkerInventory:
        lease_seconds = _positive_lease_seconds(lease_duration)
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            worker_id_result = await connection.scalar(
                _HEARTBEAT_WORKER,
                {
                    "worker_id": worker_id,
                    "tenant_id": tenant_uuid,
                    "expected_version": expected_version,
                    "status": status.value,
                    "progress": self._services.codec.dumps(progress or {}),
                    "resource_usage": self._services.codec.dumps(resource_usage or {}),
                    "cancellation_acknowledged": cancellation_acknowledged,
                    "actor_id": actor_id,
                },
            )
            if worker_id_result is None:
                raise WorkerFenceError(
                    f"worker {worker_id} version {expected_version} is stale or stopped"
                )
            for claim in claims:
                renewed = await connection.scalar(
                    _RENEW_TASK_CLAIM,
                    {
                        "queue_id": claim.queue_id,
                        "tenant_id": tenant_uuid,
                        "consumer_id": str(worker_id),
                        "worker_id": worker_id,
                        "task_run_id": claim.task_run_id,
                        "attempt": claim.attempt,
                        "fencing_token": claim.fencing_token,
                        "lease_seconds": lease_seconds,
                        "progress": self._services.codec.dumps(claim.progress),
                        "resource_usage": self._services.codec.dumps(claim.resource_usage),
                        "cancellation_acknowledged": claim.cancellation_acknowledged,
                    },
                )
                if renewed is None:
                    raise WorkerFenceError(
                        f"task claim {claim.task_run_id}/{claim.fencing_token} is stale"
                    )
            row = await _get_inventory_row(connection, tenant_uuid, worker_id)
        return _to_inventory(row)

    async def drain_worker(
        self,
        worker_id: UUID,
        *,
        tenant_id: str,
        expected_version: int,
        actor_id: str,
    ) -> WorkerInventory:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            changed = await connection.scalar(
                _DRAIN_WORKER,
                {
                    "worker_id": worker_id,
                    "tenant_id": tenant_uuid,
                    "expected_version": expected_version,
                    "actor_id": actor_id,
                },
            )
            if changed is None:
                raise WorkerFenceError(
                    f"worker {worker_id} version {expected_version} is stale or stopped"
                )
            row = await _get_inventory_row(connection, tenant_uuid, worker_id)
        return _to_inventory(row)

    @instrument_async_operation("worker", "recover-claims")
    async def recover_expired_claims(
        self,
        *,
        tenant_id: str,
        policy: WorkerLossPolicy,
        limit: int = 100,
    ) -> int:
        if limit < 1:
            raise ValueError("worker recovery limit must be at least 1")
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            failed = int(
                await connection.scalar(
                    _FAIL_EXPIRED,
                    {
                        "tenant_id": tenant_uuid,
                        "limit": limit,
                        "fail_all": policy is WorkerLossPolicy.FAIL,
                    },
                )
                or 0
            )
            if policy is WorkerLossPolicy.FAIL or failed >= limit:
                return failed
            requeued = int(
                await connection.scalar(
                    _REQUEUE_EXPIRED,
                    {"tenant_id": tenant_uuid, "limit": limit - failed},
                )
                or 0
            )
        return failed + requeued

    async def list_worker_inventory(self, *, tenant_id: str) -> list[WorkerInventory]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _INVENTORY,
                        {"tenant_id": tenant_uuid, "worker_id": None},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_inventory(row) for row in rows]

    async def wait_for_work(
        self,
        *,
        tenant_id: str,
        timeout_seconds: float,
    ) -> bool:
        return await self._transport.wait_for_work(
            "task-dispatch",
            tenant_id=tenant_id,
            timeout_seconds=timeout_seconds,
        )


async def _get_inventory_row(
    connection: AsyncConnection,
    tenant_id: UUID,
    worker_id: UUID,
) -> RowMapping:
    row = (
        (
            await connection.execute(
                _INVENTORY,
                {"tenant_id": tenant_id, "worker_id": worker_id},
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise NotFoundError(
            "worker",
            worker_id,
            message=f"worker {worker_id} does not exist",
        )
    return row


def _positive_lease_seconds(value: timedelta) -> float:
    seconds = value.total_seconds()
    if seconds <= 0:
        raise ValueError("worker lease duration must be positive")
    return seconds


def _is_live(row: RowMapping) -> bool:
    database_now = row["database_now"]
    last_heartbeat_at = row["last_heartbeat_at"]
    if not isinstance(database_now, datetime) or not isinstance(last_heartbeat_at, datetime):
        raise TypeError("PostgreSQL returned invalid worker timestamps")
    return database_now - last_heartbeat_at <= timedelta(seconds=30)


def _to_inventory(row: RowMapping) -> WorkerInventory:
    status = WorkerStatus(row["status"])
    liveness = (
        WorkerLiveness.STOPPED
        if status is WorkerStatus.STOPPED
        else WorkerLiveness.LIVE
        if _is_live(row)
        else WorkerLiveness.STALE
    )
    protocol_version = int(row["protocol_version"])
    claimed_work = int(row["claimed_work"])
    capacity = int(row["capacity"])
    capabilities = row["capabilities"] or {}
    return WorkerInventory(
        worker_id=row["id"],
        tenant_id=row["tenant_slug"],
        worker_group=row["worker_group"],
        instance_name=row["instance_name"],
        version=row["version"],
        protocol_version=protocol_version,
        status=status,
        liveness=liveness,
        compatibility=(
            WorkerCompatibility.COMPATIBLE
            if protocol_version == WORKER_PROTOCOL_VERSION
            else WorkerCompatibility.INCOMPATIBLE
        ),
        capabilities=tuple(capabilities.get("taskTypes", ())),
        runner_types=tuple(row["runner_types"] or ()),
        labels=row["labels"] or {},
        capacity=capacity,
        claimed_work=claimed_work,
        utilization=claimed_work / capacity,
        progress=row["heartbeat_progress"] or {},
        resource_usage=row["resource_usage"] or {},
        cancellation_acknowledged=bool(row["cancellation_acknowledged"]),
        last_heartbeat_at=row["last_heartbeat_at"],
        resource_version=int(row["resource_version"]),
    )


def _to_task_claim(row: RowMapping) -> WorkerTaskClaim:
    return WorkerTaskClaim(
        queue_id=int(row["queue_id"]),
        message_id=row["message_id"],
        worker_id=row["worker_id"],
        task_run_id=row["task_run_id"],
        execution_id=row["execution_id"],
        task_id=row["task_path"],
        attempt=int(row["attempt"]),
        fencing_token=int(row["fencing_token"]),
        lease_expires_at=row["lease_expires_at"],
        delivery_attempt=int(row["delivery_attempt"]),
    )
