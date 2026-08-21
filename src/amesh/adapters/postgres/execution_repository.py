from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4, uuid5

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import ExecutionEventType, ExecutionState
from amesh.dsl import FlowDefinition
from amesh.ports.execution_repository import (
    ExecutionRepository,
    ExecutionStateConflictError,
    PersistedExecution,
    PersistedFlow,
    PersistedTaskRun,
    TaskRunState,
    TaskStateConflictError,
)

_UPSERT_NAMESPACE = text(
    """
    INSERT INTO namespaces (tenant_id, name)
    SELECT tenants.id, :namespace
    FROM tenants
    WHERE tenants.slug = :tenant_slug
    ON CONFLICT (tenant_id, name) DO UPDATE SET name = EXCLUDED.name
    RETURNING id, tenant_id
    """
)

_UPSERT_FLOW = text(
    """
    INSERT INTO flows (tenant_id, namespace_id, flow_key)
    VALUES (:tenant_id, :namespace_id, :flow_key)
    ON CONFLICT (tenant_id, namespace_id, flow_key)
    DO UPDATE SET flow_key = EXCLUDED.flow_key
    RETURNING id
    """
)

_INSERT_FLOW_REVISION = text(
    """
    INSERT INTO flow_revisions (
        id,
        tenant_id,
        flow_id,
        revision,
        semantic_hash,
        canonical_definition,
        created_by
    )
    VALUES (
        :revision_id,
        :tenant_id,
        :flow_id,
        :revision,
        :semantic_hash,
        CAST(:canonical_definition AS jsonb),
        'mvp-executor'
    )
    ON CONFLICT (tenant_id, flow_id, revision) DO NOTHING
    """
)

_SELECT_FLOW_REVISION = text(
    """
    SELECT id, semantic_hash
    FROM flow_revisions
    WHERE tenant_id = :tenant_id
      AND flow_id = :flow_id
      AND revision = :revision
    """
)

_ACTIVATE_FLOW_REVISION = text(
    """
    UPDATE flows
    SET active_revision = :revision,
        status = 'ACTIVE',
        version = version + 1,
        updated_at = now()
    WHERE tenant_id = :tenant_id
      AND id = :flow_id
    """
)

_INSERT_EXECUTION = text(
    """
    INSERT INTO executions (
        id,
        tenant_id,
        flow_id,
        flow_revision_id,
        namespace_name,
        flow_key,
        state,
        epoch,
        version,
        idempotency_key,
        inputs,
        labels,
        created_at,
        updated_at
    )
    VALUES (
        :execution_id,
        :tenant_id,
        :flow_id,
        :flow_revision_id,
        :namespace_name,
        :flow_key,
        'RUNNING',
        1,
        3,
        :idempotency_key,
        CAST(:inputs AS jsonb),
        CAST(:labels AS jsonb),
        :created_at,
        :created_at
    )
    ON CONFLICT (tenant_id, idempotency_key) DO NOTHING
    RETURNING id
    """
)

_SELECT_EXECUTION_BY_IDEMPOTENCY = text(
    """
    SELECT id
    FROM executions
    WHERE tenant_id = :tenant_id
      AND idempotency_key = :idempotency_key
    """
)

_INSERT_EXECUTION_EVENT = text(
    """
    INSERT INTO execution_events (
        tenant_id,
        execution_id,
        sequence,
        event_id,
        event_type,
        schema_version,
        correlation_id,
        causation_id,
        actor_id,
        occurred_at,
        payload
    )
    VALUES (
        :tenant_id,
        :execution_id,
        :sequence,
        :event_id,
        :event_type,
        1,
        :correlation_id,
        NULL,
        'mvp-executor',
        :occurred_at,
        '{}'::jsonb
    )
    """
)

_INSERT_TASK_RUN = text(
    """
    INSERT INTO task_runs (
        id,
        tenant_id,
        execution_id,
        task_path,
        state,
        current_attempt,
        version
    )
    VALUES (
        :task_run_id,
        :tenant_id,
        :execution_id,
        :task_id,
        'WAITING',
        0,
        0
    )
    ON CONFLICT (id) DO NOTHING
    """
)

_GET_EXECUTION = text(
    """
    SELECT
        executions.id,
        tenants.slug AS tenant_slug,
        executions.state,
        executions.epoch,
        executions.version,
        executions.namespace_name,
        executions.flow_key,
        executions.inputs,
        executions.created_at,
        executions.updated_at
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    WHERE executions.id = :execution_id
    """
)

_LIST_EXECUTIONS = text(
    """
    SELECT
        executions.id,
        tenants.slug AS tenant_slug,
        executions.state,
        executions.epoch,
        executions.version,
        executions.namespace_name,
        executions.flow_key,
        executions.inputs,
        executions.created_at,
        executions.updated_at
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    WHERE tenants.slug = :tenant_slug
    ORDER BY executions.created_at DESC, executions.id
    LIMIT :limit
    """
)

_GET_FLOW_DEFINITION = text(
    """
    SELECT flow_revisions.canonical_definition
    FROM flows
    JOIN tenants ON tenants.id = flows.tenant_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    JOIN flow_revisions
      ON flow_revisions.flow_id = flows.id
     AND flow_revisions.revision = flows.active_revision
    WHERE tenants.slug = :tenant_slug
      AND namespaces.name = :namespace
      AND flows.flow_key = :flow_key
    """
)

_LIST_FLOWS = text(
    """
    SELECT
        namespaces.name AS namespace,
        flows.flow_key,
        flow_revisions.revision,
        flow_revisions.semantic_hash
    FROM flows
    JOIN tenants ON tenants.id = flows.tenant_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    JOIN flow_revisions
      ON flow_revisions.flow_id = flows.id
     AND flow_revisions.revision = flows.active_revision
    WHERE tenants.slug = :tenant_slug
    ORDER BY namespaces.name, flows.flow_key
    """
)

_LIST_TASK_RUNS = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        task_runs.retry_at,
        task_attempts.result
    FROM task_runs
    LEFT JOIN task_attempts
      ON task_attempts.task_run_id = task_runs.id
     AND task_attempts.attempt = task_runs.current_attempt
    WHERE task_runs.execution_id = :execution_id
    ORDER BY task_runs.created_at, task_runs.task_path
    """
)

_START_TASK = text(
    """
    WITH updated AS (
        UPDATE task_runs
        SET state = 'RUNNING',
            current_attempt = current_attempt + 1,
            version = version + 1,
            retry_at = NULL,
            updated_at = now()
        WHERE id = :task_run_id
          AND (
              state = 'WAITING'
              OR (state = 'RETRY_DELAY' AND retry_at <= now())
          )
        RETURNING
            id,
            tenant_id,
            execution_id,
            task_path,
            state,
            current_attempt,
            version,
            retry_at
    ), inserted AS (
        INSERT INTO task_attempts (
            id,
            tenant_id,
            task_run_id,
            attempt,
            state,
            fencing_token,
            started_at
        )
        SELECT
            :attempt_id,
            updated.tenant_id,
            updated.id,
            updated.current_attempt,
            'RUNNING',
            updated.current_attempt,
            now()
        FROM updated
        RETURNING task_run_id
    )
    SELECT
        updated.id,
        updated.execution_id,
        updated.task_path,
        updated.state,
        updated.current_attempt,
        updated.version,
        updated.retry_at,
        NULL::jsonb AS result
    FROM updated
    JOIN inserted ON inserted.task_run_id = updated.id
    """
)

_FINISH_TASK = text(
    """
    WITH finished_attempt AS (
        UPDATE task_attempts
        SET state = :state,
            result = CAST(:result AS jsonb),
            finished_at = now()
        WHERE task_run_id = :task_run_id
          AND attempt = :attempt
          AND state = 'RUNNING'
        RETURNING task_run_id, result
    ), finished_run AS (
        UPDATE task_runs
        SET state = :state,
            version = version + 1,
            retry_at = NULL,
            updated_at = now()
        FROM finished_attempt
        WHERE task_runs.id = finished_attempt.task_run_id
          AND task_runs.current_attempt = :attempt
          AND task_runs.state = 'RUNNING'
        RETURNING
            task_runs.id,
            task_runs.execution_id,
            task_runs.task_path,
            task_runs.state,
            task_runs.current_attempt,
            task_runs.version,
            task_runs.retry_at,
            finished_attempt.result
    )
    SELECT * FROM finished_run
    """
)

_RETRY_TASK = text(
    """
    WITH failed_attempt AS (
        UPDATE task_attempts
        SET state = 'FAILED',
            result = CAST(:result AS jsonb),
            finished_at = now()
        WHERE task_run_id = :task_run_id
          AND attempt = :attempt
          AND state = 'RUNNING'
        RETURNING task_run_id, result
    ), retrying_run AS (
        UPDATE task_runs
        SET state = 'RETRY_DELAY',
            version = version + 1,
            retry_at = :retry_at,
            updated_at = now()
        FROM failed_attempt
        WHERE task_runs.id = failed_attempt.task_run_id
          AND task_runs.current_attempt = :attempt
          AND task_runs.state = 'RUNNING'
        RETURNING
            task_runs.id,
            task_runs.execution_id,
            task_runs.task_path,
            task_runs.state,
            task_runs.current_attempt,
            task_runs.version,
            task_runs.retry_at,
            failed_attempt.result
    )
    SELECT * FROM retrying_run
    """
)

_FINISH_EXECUTION = text(
    """
    WITH finished AS (
        UPDATE executions
        SET state = :state,
            version = version + 1,
            updated_at = now(),
            terminal_at = now()
        WHERE id = :execution_id
          AND state = 'RUNNING'
          AND epoch = :expected_epoch
        RETURNING
            id,
            tenant_id,
            state,
            epoch,
            version,
            namespace_name,
            flow_key,
            inputs,
            created_at,
            updated_at
    ), event AS (
        INSERT INTO execution_events (
            tenant_id,
            execution_id,
            sequence,
            event_id,
            event_type,
            schema_version,
            correlation_id,
            causation_id,
            actor_id,
            occurred_at,
            payload
        )
        SELECT
            finished.tenant_id,
            finished.id,
            finished.version,
            :event_id,
            :event_type,
            1,
            :correlation_id,
            NULL,
            'mvp-executor',
            now(),
            CAST(:payload AS jsonb)
        FROM finished
        RETURNING execution_id
    )
    SELECT
        finished.id,
        tenants.slug AS tenant_slug,
        finished.state,
        finished.epoch,
        finished.version,
        finished.namespace_name,
        finished.flow_key,
        finished.inputs,
        finished.created_at,
        finished.updated_at
    FROM finished
    JOIN event ON event.execution_id = finished.id
    JOIN tenants ON tenants.id = finished.tenant_id
    """
)


class PostgresExecutionRepository(ExecutionRepository):
    """Persists MVP executions, task runs, attempts and terminal events."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def apply_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
    ) -> PersistedFlow:
        encoded, semantic_hash = _canonical_flow(flow)
        async with self._engine.begin() as connection:
            tenant_uuid, namespace_id = await self._ensure_namespace(
                connection,
                tenant_id,
                flow.namespace,
            )
            flow_uuid = await self._ensure_flow(
                connection,
                tenant_uuid,
                namespace_id,
                flow.id,
            )
            await self._ensure_flow_revision(
                connection,
                tenant_uuid,
                flow_uuid,
                flow,
                semantic_hash,
                encoded,
            )
            await connection.execute(
                _ACTIVATE_FLOW_REVISION,
                {
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_uuid,
                    "revision": flow.revision,
                },
            )
        return PersistedFlow(
            namespace=flow.namespace,
            flow_id=flow.id,
            revision=flow.revision,
            semantic_hash=semantic_hash,
        )

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> FlowDefinition:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _GET_FLOW_DEFINITION,
                {
                    "tenant_slug": tenant_id,
                    "namespace": namespace,
                    "flow_key": flow_id,
                },
            )
            definition = result.scalar_one_or_none()
        if definition is None:
            raise LookupError(f"flow {namespace}.{flow_id} does not exist")
        return FlowDefinition.model_validate(definition)

    async def list_flows(self, *, tenant_id: str) -> list[PersistedFlow]:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _LIST_FLOWS,
                {"tenant_slug": tenant_id},
            )
            rows = result.mappings().all()
        return [
            PersistedFlow(
                namespace=row["namespace"],
                flow_id=row["flow_key"],
                revision=row["revision"],
                semantic_hash=row["semantic_hash"],
            )
            for row in rows
        ]

    async def create_execution(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        inputs: dict[str, object],
        idempotency_key: str | None = None,
    ) -> PersistedExecution:
        execution_id = uuid4()
        created_at = datetime.now(UTC)
        encoded, semantic_hash = _canonical_flow(flow)

        async with self._engine.begin() as connection:
            tenant_uuid, namespace_id = await self._ensure_namespace(
                connection,
                tenant_id,
                flow.namespace,
            )
            flow_id = await self._ensure_flow(connection, tenant_uuid, namespace_id, flow.id)
            flow_revision_id = await self._ensure_flow_revision(
                connection,
                tenant_uuid,
                flow_id,
                flow,
                semantic_hash,
                encoded,
            )
            await connection.execute(
                _ACTIVATE_FLOW_REVISION,
                {"tenant_id": tenant_uuid, "flow_id": flow_id, "revision": flow.revision},
            )
            insert_result = await connection.execute(
                _INSERT_EXECUTION,
                {
                    "execution_id": execution_id,
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_id,
                    "flow_revision_id": flow_revision_id,
                    "namespace_name": flow.namespace,
                    "flow_key": flow.id,
                    "idempotency_key": idempotency_key,
                    "inputs": json.dumps(inputs),
                    "labels": json.dumps(flow.labels),
                    "created_at": created_at,
                },
            )
            inserted_execution_id = insert_result.scalar_one_or_none()
            if inserted_execution_id is None:
                if idempotency_key is None:
                    raise RuntimeError("execution insert did not return an identity")
                existing_result = await connection.execute(
                    _SELECT_EXECUTION_BY_IDEMPOTENCY,
                    {"tenant_id": tenant_uuid, "idempotency_key": idempotency_key},
                )
                execution_id = UUID(str(existing_result.scalar_one()))
            else:
                execution_id = UUID(str(inserted_execution_id))
                await self._insert_initial_events(
                    connection,
                    tenant_uuid,
                    execution_id,
                    created_at,
                )
                await connection.execute(
                    _INSERT_TASK_RUN,
                    [
                        {
                            "task_run_id": uuid5(execution_id, f"task:{task.id}"),
                            "tenant_id": tenant_uuid,
                            "execution_id": execution_id,
                            "task_id": task.id,
                        }
                        for task in flow.tasks
                    ],
                )

        return await self.get_execution(execution_id)

    async def get_execution(self, execution_id: UUID) -> PersistedExecution:
        async with self._engine.connect() as connection:
            result = await connection.execute(_GET_EXECUTION, {"execution_id": execution_id})
            row = result.mappings().one_or_none()
        if row is None:
            raise LookupError(f"execution {execution_id} does not exist")
        return _to_execution(row)

    async def list_executions(
        self,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> list[PersistedExecution]:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _LIST_EXECUTIONS,
                {"tenant_slug": tenant_id, "limit": limit},
            )
            rows = result.mappings().all()
        return [_to_execution(row) for row in rows]

    async def list_task_runs(self, execution_id: UUID) -> list[PersistedTaskRun]:
        async with self._engine.connect() as connection:
            result = await connection.execute(_LIST_TASK_RUNS, {"execution_id": execution_id})
            rows = result.mappings().all()
        return [_to_task_run(row) for row in rows]

    async def start_task(self, task_run_id: UUID) -> PersistedTaskRun:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _START_TASK,
                {"task_run_id": task_run_id, "attempt_id": uuid4()},
            )
            row = result.mappings().one_or_none()
        if row is None:
            raise TaskStateConflictError(f"task run {task_run_id} is not waiting")
        return _to_task_run(row)

    async def complete_task(
        self,
        task_run_id: UUID,
        attempt: int,
        result: dict[str, object],
    ) -> PersistedTaskRun:
        return await self._finish_task(task_run_id, attempt, TaskRunState.SUCCESS, result)

    async def retry_task(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        retry_at: datetime,
        reason: str,
    ) -> PersistedTaskRun:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _RETRY_TASK,
                {
                    "task_run_id": task_run_id,
                    "attempt": attempt,
                    "retry_at": retry_at,
                    "result": json.dumps({"error": reason}),
                },
            )
            row = result.mappings().one_or_none()
        if row is None:
            raise TaskStateConflictError(f"task run {task_run_id} attempt {attempt} is not running")
        return _to_task_run(row)

    async def fail_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
    ) -> PersistedTaskRun:
        return await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.FAILED,
            {"error": reason},
        )

    async def complete_execution(
        self,
        execution_id: UUID,
        *,
        expected_epoch: int,
    ) -> PersistedExecution:
        return await self._finish_execution(
            execution_id,
            ExecutionState.SUCCESS,
            ExecutionEventType.SUCCEEDED,
            {},
            expected_epoch=expected_epoch,
        )

    async def fail_execution(
        self,
        execution_id: UUID,
        reason: str,
        *,
        expected_epoch: int,
    ) -> PersistedExecution:
        return await self._finish_execution(
            execution_id,
            ExecutionState.FAILED,
            ExecutionEventType.FAILED,
            {"reason": reason},
            expected_epoch=expected_epoch,
        )

    async def _ensure_namespace(
        self,
        connection: AsyncConnection,
        tenant_slug: str,
        namespace: str,
    ) -> tuple[UUID, UUID]:
        result = await connection.execute(
            _UPSERT_NAMESPACE,
            {"tenant_slug": tenant_slug, "namespace": namespace},
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise LookupError(f"tenant {tenant_slug!r} does not exist")
        return UUID(str(row["tenant_id"])), UUID(str(row["id"]))

    async def _ensure_flow(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        namespace_id: UUID,
        flow_key: str,
    ) -> UUID:
        result = await connection.execute(
            _UPSERT_FLOW,
            {"tenant_id": tenant_id, "namespace_id": namespace_id, "flow_key": flow_key},
        )
        return UUID(str(result.scalar_one()))

    async def _ensure_flow_revision(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        flow_id: UUID,
        flow: FlowDefinition,
        semantic_hash: str,
        canonical_definition: str,
    ) -> UUID:
        await connection.execute(
            _INSERT_FLOW_REVISION,
            {
                "revision_id": uuid4(),
                "tenant_id": tenant_id,
                "flow_id": flow_id,
                "revision": flow.revision,
                "semantic_hash": semantic_hash,
                "canonical_definition": canonical_definition,
            },
        )
        result = await connection.execute(
            _SELECT_FLOW_REVISION,
            {"tenant_id": tenant_id, "flow_id": flow_id, "revision": flow.revision},
        )
        row = result.mappings().one()
        if row["semantic_hash"] != semantic_hash:
            raise ValueError(
                f"flow {flow.namespace}.{flow.id} revision {flow.revision} already has different content"
            )
        return UUID(str(row["id"]))

    async def _insert_initial_events(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
        occurred_at: datetime,
    ) -> None:
        correlation_id = uuid4()
        event_types = (
            ExecutionEventType.CREATED,
            ExecutionEventType.QUEUED,
            ExecutionEventType.STARTED,
        )
        await connection.execute(
            _INSERT_EXECUTION_EVENT,
            [
                {
                    "tenant_id": tenant_id,
                    "execution_id": execution_id,
                    "sequence": sequence,
                    "event_id": uuid4(),
                    "event_type": event_type.value,
                    "correlation_id": correlation_id,
                    "occurred_at": occurred_at,
                }
                for sequence, event_type in enumerate(event_types, start=1)
            ],
        )

    async def _finish_task(
        self,
        task_run_id: UUID,
        attempt: int,
        state: TaskRunState,
        result_payload: dict[str, object],
    ) -> PersistedTaskRun:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _FINISH_TASK,
                {
                    "task_run_id": task_run_id,
                    "attempt": attempt,
                    "state": state.value,
                    "result": json.dumps(result_payload),
                },
            )
            row = result.mappings().one_or_none()
        if row is None:
            raise TaskStateConflictError(f"task run {task_run_id} attempt {attempt} is not running")
        return _to_task_run(row)

    async def _finish_execution(
        self,
        execution_id: UUID,
        state: ExecutionState,
        event_type: ExecutionEventType,
        payload: dict[str, object],
        *,
        expected_epoch: int,
    ) -> PersistedExecution:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _FINISH_EXECUTION,
                {
                    "execution_id": execution_id,
                    "expected_epoch": expected_epoch,
                    "state": state.value,
                    "event_id": uuid4(),
                    "event_type": event_type.value,
                    "correlation_id": uuid4(),
                    "payload": json.dumps(payload),
                },
            )
            row = result.mappings().one_or_none()
        if row is None:
            existing = await self.get_execution(execution_id)
            if existing.epoch != expected_epoch:
                raise ExecutionStateConflictError(
                    f"execution {execution_id} is fenced at epoch {existing.epoch}; "
                    f"received {expected_epoch}"
                )
            if existing.state is state:
                return existing
            raise ExecutionStateConflictError(
                f"execution {execution_id} cannot transition from {existing.state.value} to {state.value}"
            )
        return _to_execution(row)


def _to_execution(row: RowMapping) -> PersistedExecution:
    return PersistedExecution(
        execution_id=row["id"],
        tenant_id=row["tenant_slug"],
        state=row["state"],
        epoch=row["epoch"],
        version=row["version"],
        namespace=row["namespace_name"],
        flow_id=row["flow_key"],
        inputs=row["inputs"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _to_task_run(row: RowMapping) -> PersistedTaskRun:
    return PersistedTaskRun(
        task_run_id=row["id"],
        execution_id=row["execution_id"],
        task_id=row["task_path"],
        state=row["state"],
        current_attempt=row["current_attempt"],
        version=row["version"],
        retry_at=row["retry_at"],
        result=row["result"],
    )


def _canonical_flow(flow: FlowDefinition) -> tuple[str, str]:
    canonical = flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return encoded, hashlib.sha256(encoded.encode("utf-8")).hexdigest()
