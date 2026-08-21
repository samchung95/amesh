from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import (
    ExecutionEventType,
    ExecutionState,
    ResourceMetadata,
    ResourceVersionConflict,
    TaskRunEventType,
    TaskRunState,
    TenantPolicy,
    TransitionRejectionCode,
    new_runtime_id,
    resource_etag,
)
from amesh.dsl import FlowDefinition
from amesh.ports.execution_repository import (
    ExecutionLaunchSource,
    ExecutionRepository,
    ExecutionStateConflictError,
    PersistedExecution,
    PersistedFlow,
    PersistedTaskRun,
    TaskStateConflictError,
)
from amesh.ports.tenant_repository import TenantQuotaExceeded, TenantUnavailableError

from .metadata_repository import store_flow_triggers
from .tenant_context import tenant_transaction

_UPSERT_NAMESPACE = text(
    """
    INSERT INTO namespaces (id, tenant_id, name, created_by, updated_by)
    SELECT :namespace_id, tenants.id, :namespace, :actor_id, :actor_id
    FROM tenants
    WHERE tenants.slug = :tenant_slug
    ON CONFLICT (tenant_id, name) DO UPDATE
    SET name = EXCLUDED.name,
        updated_by = EXCLUDED.updated_by,
        updated_at = now()
    RETURNING id, tenant_id
    """
)

_UPSERT_FLOW = text(
    """
    INSERT INTO flows (
        id, tenant_id, namespace_id, flow_key, created_by, updated_by
    )
    VALUES (
        :resource_id, :tenant_id, :namespace_id, :flow_key, :actor_id, :actor_id
    )
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
        :actor_id
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
        labels = CAST(:labels AS jsonb),
        annotations = CAST(:annotations AS jsonb),
        updated_by = :actor_id,
        version = version + 1,
        updated_at = now()
    WHERE tenant_id = :tenant_id
      AND id = :flow_id
      AND (
          CAST(:expected_version AS bigint) IS NULL
          OR version = CAST(:expected_version AS bigint)
      )
    RETURNING version
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
        trigger_context,
        labels,
        created_by,
        updated_by,
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
        CAST(:trigger_context AS jsonb),
        CAST(:labels AS jsonb),
        :actor_id,
        :actor_id,
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
        idempotency_key,
        correlation_id,
        causation_id,
        actor_id,
        reason,
        occurred_at,
        payload
    )
    VALUES (
        :tenant_id,
        :execution_id,
        :sequence,
        :event_id,
        :event_type,
        2,
        :idempotency_key,
        :correlation_id,
        NULL,
        :actor_id,
        :reason,
        :occurred_at,
        '{}'::jsonb
    )
    """
)

_INSERT_TASK_RUN = text(
    """
    WITH inserted AS (
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
            1
        )
        ON CONFLICT (id) DO NOTHING
        RETURNING id, tenant_id, execution_id, task_path, version
    )
    INSERT INTO task_run_events (
        tenant_id,
        task_run_id,
        execution_id,
        sequence,
        event_id,
        event_type,
        schema_version,
        idempotency_key,
        correlation_id,
        causation_id,
        actor_id,
        reason,
        occurred_at,
        payload
    )
    SELECT
        inserted.tenant_id,
        inserted.id,
        inserted.execution_id,
        inserted.version,
        :event_id,
        'TaskRunCreated',
        1,
        :idempotency_key,
        :correlation_id,
        NULL,
        :actor_id,
        NULL,
        :occurred_at,
        jsonb_build_object('task_id', inserted.task_path)
    FROM inserted
    """
)

_INSERT_TASK_RUN_EVENT = text(
    """
    INSERT INTO task_run_events (
        tenant_id,
        task_run_id,
        execution_id,
        sequence,
        event_id,
        event_type,
        schema_version,
        idempotency_key,
        correlation_id,
        causation_id,
        actor_id,
        reason,
        occurred_at,
        payload
    ) VALUES (
        :tenant_id,
        :task_run_id,
        :execution_id,
        :sequence,
        :event_id,
        :event_type,
        1,
        :idempotency_key,
        :correlation_id,
        NULL,
        :actor_id,
        :reason,
        now(),
        CAST(:payload AS jsonb)
    )
    """
)

_INSERT_TRANSITION_REJECTION = text(
    """
    INSERT INTO transition_rejections (
        tenant_id,
        rejection_id,
        command_id,
        idempotency_key,
        schema_version,
        aggregate_type,
        aggregate_id,
        code,
        current_state,
        current_version,
        current_epoch,
        actor_id,
        reason,
        correlation_id,
        causation_id,
        occurred_at
    ) VALUES (
        :tenant_id,
        :rejection_id,
        :command_id,
        :idempotency_key,
        1,
        :aggregate_type,
        :aggregate_id,
        :code,
        :current_state,
        :current_version,
        :current_epoch,
        :actor_id,
        :reason,
        :correlation_id,
        NULL,
        now()
    )
    ON CONFLICT (tenant_id, aggregate_type, aggregate_id, idempotency_key) DO NOTHING
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
        executions.trigger_context,
        executions.created_at,
        executions.updated_at
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    WHERE executions.id = :execution_id
      AND tenants.slug = :tenant_slug
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
        executions.trigger_context,
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
        flows.id,
        tenants.slug AS tenant_slug,
        namespaces.name AS namespace,
        flows.flow_key,
        flow_revisions.revision,
        flow_revisions.semantic_hash,
        flows.labels,
        flows.annotations,
        flows.created_by,
        flows.updated_by,
        flows.version,
        flows.lifecycle,
        flows.archived_at,
        flows.deleted_at,
        flows.created_at,
        flows.updated_at
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

_GET_PERSISTED_FLOW = text(
    """
    SELECT
        flows.id,
        tenants.slug AS tenant_slug,
        namespaces.name AS namespace,
        flows.flow_key,
        flow_revisions.revision,
        flow_revisions.semantic_hash,
        flows.labels,
        flows.annotations,
        flows.created_by,
        flows.updated_by,
        flows.version,
        flows.lifecycle,
        flows.archived_at,
        flows.deleted_at,
        flows.created_at,
        flows.updated_at
    FROM flows
    JOIN tenants ON tenants.id = flows.tenant_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    JOIN flow_revisions
      ON flow_revisions.flow_id = flows.id
     AND flow_revisions.revision = flows.active_revision
    WHERE flows.tenant_id = :tenant_id
      AND flows.id = :flow_id
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
    JOIN tenants ON tenants.id = task_runs.tenant_id
    LEFT JOIN task_attempts
      ON task_attempts.task_run_id = task_runs.id
     AND task_attempts.attempt = task_runs.current_attempt
    WHERE task_runs.execution_id = :execution_id
      AND tenants.slug = :tenant_slug
    ORDER BY task_runs.created_at, task_runs.task_path
    """
)

_GET_TASK_RUN = text(
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
    WHERE task_runs.id = :task_run_id
      AND task_runs.tenant_id = :tenant_id
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
          AND tenant_id = :tenant_id
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
    WITH eligible_attempt AS (
        SELECT attempts.id, attempts.queue_id
        FROM task_attempts AS attempts
        WHERE attempts.task_run_id = :task_run_id
          AND attempts.tenant_id = :tenant_id
          AND attempts.attempt = :attempt
          AND attempts.state = 'RUNNING'
          AND (
              (
                  CAST(:worker_id AS uuid) IS NULL
                  AND CAST(:fencing_token AS bigint) IS NULL
                  AND attempts.worker_id IS NULL
                  AND attempts.queue_id IS NULL
              )
              OR (
                  attempts.worker_id = CAST(:worker_id AS uuid)
                  AND attempts.fencing_token = CAST(:fencing_token AS bigint)
                  AND attempts.lease_expires_at > clock_timestamp()
                  AND EXISTS (
                      SELECT 1
                      FROM durable_work_queue AS queue
                      WHERE queue.id = attempts.queue_id
                        AND queue.tenant_id = attempts.tenant_id
                        AND queue.state = 'CLAIMED'
                        AND queue.claimed_by = :worker_consumer_id
                        AND queue.fencing_token = CAST(:fencing_token AS bigint)
                        AND queue.lease_expires_at > clock_timestamp()
                  )
              )
          )
        FOR UPDATE
    ), finished_attempt AS (
        UPDATE task_attempts AS attempts
        SET state = :state,
            result = CAST(:result AS jsonb),
            finished_at = clock_timestamp(),
            lease_expires_at = NULL,
            queue_id = NULL
        FROM eligible_attempt
        WHERE attempts.id = eligible_attempt.id
        RETURNING attempts.task_run_id, attempts.result, eligible_attempt.queue_id
    ), acknowledged_queue AS (
        DELETE FROM durable_work_queue AS queue
        USING finished_attempt
        WHERE finished_attempt.queue_id IS NOT NULL
          AND queue.id = finished_attempt.queue_id
          AND queue.tenant_id = :tenant_id
          AND queue.state = 'CLAIMED'
          AND queue.claimed_by = :worker_consumer_id
          AND queue.fencing_token = CAST(:fencing_token AS bigint)
        RETURNING queue.id
    ), finished_run AS (
        UPDATE task_runs
        SET state = :state,
            version = version + 1,
            retry_at = NULL,
            updated_at = now()
        FROM finished_attempt
        LEFT JOIN acknowledged_queue ON acknowledged_queue.id = finished_attempt.queue_id
        WHERE task_runs.id = finished_attempt.task_run_id
          AND task_runs.tenant_id = :tenant_id
          AND task_runs.current_attempt = :attempt
          AND task_runs.state = 'RUNNING'
          AND (
              finished_attempt.queue_id IS NULL
              OR acknowledged_queue.id IS NOT NULL
          )
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
    WITH eligible_attempt AS (
        SELECT attempts.id, attempts.queue_id
        FROM task_attempts AS attempts
        WHERE attempts.task_run_id = :task_run_id
          AND attempts.tenant_id = :tenant_id
          AND attempts.attempt = :attempt
          AND attempts.state = 'RUNNING'
          AND (
              (
                  CAST(:worker_id AS uuid) IS NULL
                  AND CAST(:fencing_token AS bigint) IS NULL
                  AND attempts.worker_id IS NULL
                  AND attempts.queue_id IS NULL
              )
              OR (
                  attempts.worker_id = CAST(:worker_id AS uuid)
                  AND attempts.fencing_token = CAST(:fencing_token AS bigint)
                  AND attempts.lease_expires_at > clock_timestamp()
                  AND EXISTS (
                      SELECT 1
                      FROM durable_work_queue AS queue
                      WHERE queue.id = attempts.queue_id
                        AND queue.tenant_id = attempts.tenant_id
                        AND queue.state = 'CLAIMED'
                        AND queue.claimed_by = :worker_consumer_id
                        AND queue.fencing_token = CAST(:fencing_token AS bigint)
                        AND queue.lease_expires_at > clock_timestamp()
                  )
              )
          )
        FOR UPDATE
    ), failed_attempt AS (
        UPDATE task_attempts AS attempts
        SET state = 'FAILED',
            result = CAST(:result AS jsonb),
            finished_at = clock_timestamp(),
            lease_expires_at = NULL,
            queue_id = NULL
        FROM eligible_attempt
        WHERE attempts.id = eligible_attempt.id
        RETURNING attempts.task_run_id, attempts.result, eligible_attempt.queue_id
    ), acknowledged_queue AS (
        DELETE FROM durable_work_queue AS queue
        USING failed_attempt
        WHERE failed_attempt.queue_id IS NOT NULL
          AND queue.id = failed_attempt.queue_id
          AND queue.tenant_id = :tenant_id
          AND queue.state = 'CLAIMED'
          AND queue.claimed_by = :worker_consumer_id
          AND queue.fencing_token = CAST(:fencing_token AS bigint)
        RETURNING queue.id
    ), retrying_run AS (
        UPDATE task_runs
        SET state = 'RETRY_DELAY',
            version = version + 1,
            retry_at = :retry_at,
            updated_at = now()
        FROM failed_attempt
        LEFT JOIN acknowledged_queue ON acknowledged_queue.id = failed_attempt.queue_id
        WHERE task_runs.id = failed_attempt.task_run_id
          AND task_runs.tenant_id = :tenant_id
          AND task_runs.current_attempt = :attempt
          AND task_runs.state = 'RUNNING'
          AND (
              failed_attempt.queue_id IS NULL
              OR acknowledged_queue.id IS NOT NULL
          )
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
          AND tenant_id = :tenant_id
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
            trigger_context,
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
            idempotency_key,
            correlation_id,
            causation_id,
            actor_id,
            reason,
            occurred_at,
            payload
        )
        SELECT
            finished.tenant_id,
            finished.id,
            finished.version,
            :event_id,
            :event_type,
            2,
            :idempotency_key,
            :correlation_id,
            NULL,
            'mvp-executor',
            :reason,
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
        finished.trigger_context,
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
        expected_etag: str | None = None,
        actor_id: str = "system:flow-manager",
    ) -> PersistedFlow:
        encoded, semantic_hash = _canonical_flow(flow)
        async with tenant_transaction(self._engine, tenant_id) as (connection, scoped_tenant_id):
            policy = await _load_tenant_policy(connection)
            _require_allowed_plugins(policy, flow)
            tenant_uuid, namespace_id = await self._ensure_namespace(
                connection,
                tenant_id,
                flow.namespace,
                actor_id,
            )
            if tenant_uuid != scoped_tenant_id:
                raise TenantUnavailableError("tenant context changed during flow application")
            flow_uuid = await self._ensure_flow(
                connection,
                tenant_uuid,
                namespace_id,
                flow.id,
                actor_id,
            )
            await self._ensure_flow_revision(
                connection,
                tenant_uuid,
                flow_uuid,
                flow,
                semantic_hash,
                encoded,
                actor_id,
            )
            expected_version: int | None = None
            if expected_etag is not None:
                current_result = await connection.execute(
                    _GET_PERSISTED_FLOW,
                    {"tenant_id": tenant_uuid, "flow_id": flow_uuid},
                )
                current_row = current_result.mappings().one_or_none()
                if current_row is None or _to_flow(current_row).etag != expected_etag:
                    raise ResourceVersionConflict(
                        f"flow {flow.namespace}.{flow.id} does not match If-Match"
                    )
                expected_version = int(current_row["version"])
            activation = await connection.execute(
                _ACTIVATE_FLOW_REVISION,
                {
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_uuid,
                    "revision": flow.revision,
                    "labels": json.dumps(flow.labels),
                    "annotations": json.dumps(flow.annotations),
                    "actor_id": actor_id,
                    "expected_version": expected_version,
                },
            )
            if activation.scalar_one_or_none() is None:
                raise ResourceVersionConflict(
                    f"flow {flow.namespace}.{flow.id} changed during conditional update"
                )
            result = await connection.execute(
                _GET_PERSISTED_FLOW,
                {"tenant_id": tenant_uuid, "flow_id": flow_uuid},
            )
            row = result.mappings().one()
        return _to_flow(row)

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> FlowDefinition:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
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
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_FLOWS,
                {"tenant_slug": tenant_id},
            )
            rows = result.mappings().all()
        return [_to_flow(row) for row in rows]

    async def create_execution(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        inputs: dict[str, object],
        trigger: dict[str, object] | None = None,
        launch_source: ExecutionLaunchSource = ExecutionLaunchSource.MANUAL,
        idempotency_key: str | None = None,
        actor_id: str = "system:executor",
    ) -> PersistedExecution:
        execution_id = new_runtime_id()
        created_at = datetime.now(UTC)
        encoded, semantic_hash = _canonical_flow(flow)

        async with tenant_transaction(self._engine, tenant_id) as (connection, scoped_tenant_id):
            policy = await _load_tenant_policy(connection)
            _require_allowed_plugins(policy, flow)
            if not policy.feature_enabled("executions"):
                raise TenantQuotaExceeded("tenant execution feature is disabled")
            running_count = int(
                await connection.scalar(
                    text("SELECT count(*) FROM executions WHERE state = 'RUNNING'")
                )
                or 0
            )
            if running_count >= policy.max_concurrent_executions:
                raise TenantQuotaExceeded("tenant concurrent execution quota exceeded")
            tenant_uuid, namespace_id = await self._ensure_namespace(
                connection,
                tenant_id,
                flow.namespace,
                actor_id,
            )
            if tenant_uuid != scoped_tenant_id:
                raise TenantUnavailableError("tenant context changed during execution creation")
            flow_id = await self._ensure_flow(
                connection,
                tenant_uuid,
                namespace_id,
                flow.id,
                actor_id,
            )
            flow_revision_id = await self._ensure_flow_revision(
                connection,
                tenant_uuid,
                flow_id,
                flow,
                semantic_hash,
                encoded,
                actor_id,
            )
            await connection.execute(
                _ACTIVATE_FLOW_REVISION,
                {
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_id,
                    "revision": flow.revision,
                    "labels": json.dumps(flow.labels),
                    "annotations": json.dumps(flow.annotations),
                    "actor_id": actor_id,
                    "expected_version": None,
                },
            )
            launch_context = dict(trigger or {})
            launch_context["source"] = launch_source.value
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
                    "trigger_context": json.dumps(launch_context),
                    "labels": json.dumps(flow.labels),
                    "actor_id": actor_id,
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
                    actor_id,
                )
                task_rows: list[dict[str, object]] = []
                for task in flow.tasks:
                    task_event_id = new_runtime_id()
                    task_rows.append(
                        {
                            "task_run_id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "execution_id": execution_id,
                            "task_id": task.id,
                            "event_id": task_event_id,
                            "idempotency_key": str(task_event_id),
                            "correlation_id": new_runtime_id(),
                            "actor_id": actor_id,
                            "occurred_at": created_at,
                        }
                    )
                await connection.execute(
                    _INSERT_TASK_RUN,
                    task_rows,
                )

        return await self.get_execution(execution_id, tenant_id=tenant_id)

    async def get_execution(self, execution_id: UUID, *, tenant_id: str) -> PersistedExecution:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _GET_EXECUTION,
                {"execution_id": execution_id, "tenant_slug": tenant_id},
            )
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
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_EXECUTIONS,
                {"tenant_slug": tenant_id, "limit": limit},
            )
            rows = result.mappings().all()
        return [_to_execution(row) for row in rows]

    async def list_task_runs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedTaskRun]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_TASK_RUNS,
                {"execution_id": execution_id, "tenant_slug": tenant_id},
            )
            rows = result.mappings().all()
        return [_to_task_run(row) for row in rows]

    async def start_task(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
        dispatch: bool = True,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _START_TASK,
                {
                    "task_run_id": task_run_id,
                    "attempt_id": new_runtime_id(),
                    "tenant_id": tenant_uuid,
                },
            )
            row = result.mappings().one_or_none()
            if row is not None:
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    TaskRunEventType.STARTED,
                    correlation_id,
                    payload={"dispatch": dispatch},
                )
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                conflict_message = f"task run {task_run_id} is not waiting"
                if row is not None:
                    await self._record_rejection(
                        connection,
                        tenant_uuid,
                        command_id,
                        "task_run",
                        task_run_id,
                        TransitionRejectionCode.ILLEGAL_TRANSITION,
                        str(row["state"]),
                        int(row["version"]),
                        None,
                        conflict_message,
                        correlation_id,
                    )
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def complete_task(
        self,
        task_run_id: UUID,
        attempt: int,
        result: dict[str, object],
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        return await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.SUCCESS,
            result,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
        )

    async def retry_task(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
        retry_at: datetime,
        reason: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _RETRY_TASK,
                {
                    "task_run_id": task_run_id,
                    "tenant_id": tenant_uuid,
                    "attempt": attempt,
                    "retry_at": retry_at,
                    "result": json.dumps({"error": reason}),
                    "worker_id": worker_id,
                    "worker_consumer_id": str(worker_id) if worker_id is not None else None,
                    "fencing_token": fencing_token,
                },
            )
            row = result.mappings().one_or_none()
            if row is not None:
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    TaskRunEventType.RETRY_SCHEDULED,
                    correlation_id,
                    reason=reason,
                    payload={"retry_at": retry_at.isoformat(), "error": reason},
                )
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                is_duplicate = (
                    worker_id is None
                    and fencing_token is None
                    and row is not None
                    and TaskRunState(row["state"]) is TaskRunState.RETRY_DELAY
                    and int(row["current_attempt"]) == attempt
                )
                if not is_duplicate:
                    conflict_message = f"task run {task_run_id} attempt {attempt} is not running"
                    if row is not None:
                        await self._record_rejection(
                            connection,
                            tenant_uuid,
                            command_id,
                            "task_run",
                            task_run_id,
                            TransitionRejectionCode.ILLEGAL_TRANSITION,
                            str(row["state"]),
                            int(row["version"]),
                            None,
                            conflict_message,
                            correlation_id,
                        )
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def fail_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        return await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.FAILED,
            {"error": reason},
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
        )

    async def complete_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        return await self._finish_execution(
            execution_id,
            ExecutionState.SUCCESS,
            ExecutionEventType.SUCCEEDED,
            {},
            tenant_id=tenant_id,
            expected_epoch=expected_epoch,
        )

    async def fail_execution(
        self,
        execution_id: UUID,
        reason: str,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        return await self._finish_execution(
            execution_id,
            ExecutionState.FAILED,
            ExecutionEventType.FAILED,
            {"reason": reason},
            tenant_id=tenant_id,
            expected_epoch=expected_epoch,
        )

    async def _ensure_namespace(
        self,
        connection: AsyncConnection,
        tenant_slug: str,
        namespace: str,
        actor_id: str,
    ) -> tuple[UUID, UUID]:
        result = await connection.execute(
            _UPSERT_NAMESPACE,
            {
                "namespace_id": new_runtime_id(),
                "tenant_slug": tenant_slug,
                "namespace": namespace,
                "actor_id": actor_id,
            },
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
        actor_id: str,
    ) -> UUID:
        result = await connection.execute(
            _UPSERT_FLOW,
            {
                "resource_id": new_runtime_id(),
                "tenant_id": tenant_id,
                "namespace_id": namespace_id,
                "flow_key": flow_key,
                "actor_id": actor_id,
            },
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
        actor_id: str,
    ) -> UUID:
        await connection.execute(
            _INSERT_FLOW_REVISION,
            {
                "revision_id": new_runtime_id(),
                "tenant_id": tenant_id,
                "flow_id": flow_id,
                "revision": flow.revision,
                "semantic_hash": semantic_hash,
                "canonical_definition": canonical_definition,
                "actor_id": actor_id,
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
        revision_id = UUID(str(row["id"]))
        await store_flow_triggers(
            connection,
            tenant_id,
            revision_id,
            tuple(
                trigger.model_dump(mode="json", by_alias=True, exclude_none=True)
                for trigger in flow.triggers
            ),
            actor_id,
        )
        return revision_id

    async def _insert_initial_events(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
        occurred_at: datetime,
        actor_id: str,
    ) -> None:
        correlation_id = new_runtime_id()
        event_types = (
            ExecutionEventType.CREATED,
            ExecutionEventType.QUEUED,
            ExecutionEventType.STARTED,
        )
        parameters: list[dict[str, object]] = []
        for sequence, event_type in enumerate(event_types, start=1):
            event_id = new_runtime_id()
            parameters.append(
                {
                    "tenant_id": tenant_id,
                    "execution_id": execution_id,
                    "sequence": sequence,
                    "event_id": event_id,
                    "event_type": event_type.value,
                    "idempotency_key": str(event_id),
                    "correlation_id": correlation_id,
                    "actor_id": actor_id,
                    "reason": None,
                    "occurred_at": occurred_at,
                }
            )
        await connection.execute(_INSERT_EXECUTION_EVENT, parameters)

    async def _finish_task(
        self,
        task_run_id: UUID,
        attempt: int,
        state: TaskRunState,
        result_payload: dict[str, object],
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _FINISH_TASK,
                {
                    "task_run_id": task_run_id,
                    "tenant_id": tenant_uuid,
                    "attempt": attempt,
                    "state": state.value,
                    "result": json.dumps(result_payload),
                    "worker_id": worker_id,
                    "worker_consumer_id": str(worker_id) if worker_id is not None else None,
                    "fencing_token": fencing_token,
                },
            )
            row = result.mappings().one_or_none()
            if row is not None:
                event_type = (
                    TaskRunEventType.SUCCEEDED
                    if state is TaskRunState.SUCCESS
                    else TaskRunEventType.FAILED
                )
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    event_type,
                    correlation_id,
                    reason=str(result_payload.get("error"))
                    if result_payload.get("error") is not None
                    else None,
                    payload=result_payload,
                )
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                is_duplicate = (
                    worker_id is None
                    and fencing_token is None
                    and row is not None
                    and TaskRunState(row["state"]) is state
                    and int(row["current_attempt"]) == attempt
                )
                if not is_duplicate:
                    conflict_message = f"task run {task_run_id} attempt {attempt} is not running"
                    if row is not None:
                        await self._record_rejection(
                            connection,
                            tenant_uuid,
                            command_id,
                            "task_run",
                            task_run_id,
                            TransitionRejectionCode.ILLEGAL_TRANSITION,
                            str(row["state"]),
                            int(row["version"]),
                            None,
                            conflict_message,
                            correlation_id,
                        )
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def _finish_execution(
        self,
        execution_id: UUID,
        state: ExecutionState,
        event_type: ExecutionEventType,
        payload: dict[str, object],
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        event_id = new_runtime_id()
        correlation_id = new_runtime_id()
        reason = str(payload.get("reason")) if payload.get("reason") is not None else None
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _FINISH_EXECUTION,
                {
                    "execution_id": execution_id,
                    "tenant_id": tenant_uuid,
                    "expected_epoch": expected_epoch,
                    "state": state.value,
                    "event_id": event_id,
                    "event_type": event_type.value,
                    "idempotency_key": str(event_id),
                    "correlation_id": correlation_id,
                    "reason": reason,
                    "payload": json.dumps(payload),
                },
            )
            row = result.mappings().one_or_none()
            if row is None:
                existing_result = await connection.execute(
                    _GET_EXECUTION,
                    {"execution_id": execution_id, "tenant_slug": tenant_id},
                )
                row = existing_result.mappings().one_or_none()
                if row is None:
                    conflict_message = f"execution {execution_id} does not exist"
                elif int(row["epoch"]) != expected_epoch:
                    conflict_message = (
                        f"execution {execution_id} is fenced at epoch {row['epoch']}; "
                        f"received {expected_epoch}"
                    )
                    await self._record_rejection(
                        connection,
                        tenant_uuid,
                        event_id,
                        "execution",
                        execution_id,
                        TransitionRejectionCode.EPOCH_CONFLICT,
                        str(row["state"]),
                        int(row["version"]),
                        int(row["epoch"]),
                        conflict_message,
                        correlation_id,
                    )
                elif ExecutionState(row["state"]) is not state:
                    conflict_message = (
                        f"execution {execution_id} cannot transition from "
                        f"{row['state']} to {state.value}"
                    )
                    await self._record_rejection(
                        connection,
                        tenant_uuid,
                        event_id,
                        "execution",
                        execution_id,
                        TransitionRejectionCode.ILLEGAL_TRANSITION,
                        str(row["state"]),
                        int(row["version"]),
                        int(row["epoch"]),
                        conflict_message,
                        correlation_id,
                    )
        if conflict_message is not None or row is None:
            raise ExecutionStateConflictError(
                conflict_message or f"execution {execution_id} does not exist"
            )
        return _to_execution(row)

    async def _get_task_run_row(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task_run_id: UUID,
    ) -> RowMapping | None:
        result = await connection.execute(
            _GET_TASK_RUN,
            {"task_run_id": task_run_id, "tenant_id": tenant_id},
        )
        return result.mappings().one_or_none()

    async def _insert_task_event(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        row: RowMapping,
        event_id: UUID,
        event_type: TaskRunEventType,
        correlation_id: UUID,
        *,
        reason: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> None:
        await connection.execute(
            _INSERT_TASK_RUN_EVENT,
            {
                "tenant_id": tenant_id,
                "task_run_id": row["id"],
                "execution_id": row["execution_id"],
                "sequence": row["version"],
                "event_id": event_id,
                "event_type": event_type.value,
                "idempotency_key": str(event_id),
                "correlation_id": correlation_id,
                "actor_id": "mvp-executor",
                "reason": reason,
                "payload": json.dumps(payload or {}),
            },
        )

    async def _record_rejection(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        command_id: UUID,
        aggregate_type: str,
        aggregate_id: UUID,
        code: TransitionRejectionCode,
        current_state: str,
        current_version: int,
        current_epoch: int | None,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        await connection.execute(
            _INSERT_TRANSITION_REJECTION,
            {
                "tenant_id": tenant_id,
                "rejection_id": command_id,
                "command_id": command_id,
                "idempotency_key": str(command_id),
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
                "code": code.value,
                "current_state": current_state,
                "current_version": current_version,
                "current_epoch": current_epoch,
                "actor_id": "mvp-executor",
                "reason": reason,
                "correlation_id": correlation_id,
            },
        )


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
        trigger=row["trigger_context"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _to_flow(row: RowMapping) -> PersistedFlow:
    metadata = ResourceMetadata(
        labels=row["labels"],
        annotations=row["annotations"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        created_by=row["created_by"],
        updated_by=row["updated_by"],
        resource_version=row["version"],
        lifecycle=row["lifecycle"],
        archived_at=row["archived_at"],
        deleted_at=row["deleted_at"],
    )
    representation = {
        "resourceId": str(row["id"]),
        "tenantId": row["tenant_slug"],
        "namespace": row["namespace"],
        "flowId": row["flow_key"],
        "revision": row["revision"],
        "semanticHash": row["semantic_hash"],
        "metadata": metadata.model_dump(mode="json", exclude_none=True),
    }
    return PersistedFlow(
        resource_id=row["id"],
        tenant_id=row["tenant_slug"],
        namespace=row["namespace"],
        flow_id=row["flow_key"],
        revision=row["revision"],
        semantic_hash=row["semantic_hash"],
        metadata=metadata,
        etag=resource_etag(representation),
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


def _require_complete_claim(worker_id: UUID | None, fencing_token: int | None) -> None:
    if (worker_id is None) != (fencing_token is None):
        raise ValueError("worker_id and fencing_token must be supplied together")
    if fencing_token is not None and fencing_token < 1:
        raise ValueError("worker fencing token must be positive")


def _canonical_flow(flow: FlowDefinition) -> tuple[str, str]:
    canonical = flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return encoded, hashlib.sha256(encoded.encode("utf-8")).hexdigest()


async def _load_tenant_policy(connection: AsyncConnection) -> TenantPolicy:
    settings = await connection.scalar(text("SELECT settings FROM tenants"))
    if settings is None:
        raise TenantUnavailableError("tenant is unavailable")
    return TenantPolicy.model_validate(settings)


def _require_allowed_plugins(policy: TenantPolicy, flow: FlowDefinition) -> None:
    denied = sorted({task.type for task in flow.tasks if not policy.allows_plugin(task.type)})
    if denied:
        raise ValueError("tenant plugin policy does not allow: " + ", ".join(denied))
