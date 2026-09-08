"""SQL authority for the task_run_repository execution port."""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection

from amesh.domain import (
    AdmissionResourceType,
    FailureCategory,
    TaskRunEventType,
    TaskRunLifecyclePhase,
    TaskRunState,
    TransitionRejectionCode,
    new_runtime_id,
)
from amesh.ports.errors import NotFoundError
from amesh.ports.execution_repository import (
    PersistedIterationSummary,
    PersistedTaskDeferral,
    PersistedTaskRun,
    PersistedTaskRunSummary,
    TaskRunRepository,
    TaskStateConflictError,
)
from amesh.workflow.metadata import (
    task_system_labels,
)

from .execution_port_base import PostgresExecutionPort
from .execution_rows import (
    task_deferral_from_row as _to_task_deferral,
)
from .execution_rows import (
    task_run_from_row as _to_task_run,
)
from .execution_shared import _DATABASE_TIME, _INSERT_TASK_RUN
from .metadata_repository import store_task_evidence

_FINISH_TASK_UPDATE_TASK_DEFERRALS = text(
    """
                        UPDATE task_deferrals
                        SET state = CASE WHEN :state = 'SUCCESS' THEN 'COMPLETED' ELSE 'EXPIRED' END,
                            resumed_at = CASE
                                WHEN :state = 'SUCCESS' THEN clock_timestamp()
                                ELSE resumed_at
                            END
                        WHERE tenant_id = :tenant_id AND task_run_id = :task_run_id
                          AND attempt = :attempt AND state = 'WAITING'
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

_LIST_TASK_RUNS = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.iteration_key,
        task_runs.lifecycle_phase,
        task_runs.labels,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        task_runs.retry_at,
        COALESCE(task_attempts.result, task_runs.terminal_result) AS result
        ,task_attempts.failure_category
        ,COALESCE(task_attempts.evidence, task_runs.control_evidence, '{}'::jsonb) AS evidence
    FROM task_runs
    JOIN tenants ON tenants.id = task_runs.tenant_id
    LEFT JOIN task_attempts
      ON task_attempts.task_run_id = task_runs.id
     AND task_attempts.attempt = task_runs.current_attempt
    WHERE task_runs.execution_id = :execution_id
      AND tenants.slug = :tenant_slug
      AND (:include_iterations OR task_runs.iteration_key IS NULL)
    ORDER BY task_runs.created_at, task_runs.task_path, task_runs.iteration_key
    LIMIT :limit OFFSET :offset
    """
)

_SUMMARIZE_TASK_RUNS = text(
    """
    SELECT
        count(*) AS total,
        count(*) FILTER (WHERE task_runs.state = 'WAITING') AS waiting,
        count(*) FILTER (WHERE task_runs.state = 'RUNNING') AS running,
        count(*) FILTER (WHERE task_runs.state = 'RETRY_DELAY') AS retry_delay,
        count(*) FILTER (WHERE task_runs.state = 'SUCCESS') AS succeeded,
        count(*) FILTER (WHERE task_runs.state = 'FAILED') AS failed,
        count(*) FILTER (WHERE task_runs.state = 'CANCELLED') AS cancelled
    FROM task_runs
    JOIN tenants ON tenants.id = task_runs.tenant_id
    WHERE task_runs.execution_id = :execution_id
      AND tenants.slug = :tenant_slug
      AND (:include_iterations OR task_runs.iteration_key IS NULL)
    """
)

_LIST_ITERATION_SUMMARIES = text(
    """
    SELECT
        split_part(iteration_key, ':', 1) AS loop_id,
        task_path AS task_id,
        count(DISTINCT iteration_key) AS iteration_count,
        count(*) FILTER (WHERE state = 'WAITING') AS waiting,
        count(*) FILTER (WHERE state IN ('RUNNING', 'RETRY_DELAY')) AS running,
        count(*) FILTER (WHERE state = 'SUCCESS') AS succeeded,
        count(*) FILTER (WHERE state = 'FAILED') AS failed,
        count(*) FILTER (WHERE state = 'CANCELLED') AS cancelled
    FROM task_runs
    JOIN tenants ON tenants.id = task_runs.tenant_id
    WHERE task_runs.execution_id = :execution_id
      AND tenants.slug = :tenant_slug
      AND iteration_key IS NOT NULL
    GROUP BY split_part(iteration_key, ':', 1), task_path
    ORDER BY loop_id, task_id
    """
)

_TASK_ATTEMPT_STARTED_AT = text(
    """
    SELECT task_attempts.started_at
    FROM task_attempts
    JOIN task_runs ON task_runs.id = task_attempts.task_run_id
    WHERE task_attempts.task_run_id = :task_run_id
      AND task_attempts.attempt = :attempt
      AND task_attempts.tenant_id = :tenant_id
    """
)

_LIST_ITERATION_TASK_RUNS = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.iteration_key,
        task_runs.lifecycle_phase,
        task_runs.labels,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        task_runs.retry_at,
        COALESCE(task_attempts.result, task_runs.terminal_result) AS result,
        task_attempts.failure_category,
        COALESCE(task_attempts.evidence, task_runs.control_evidence, '{}'::jsonb) AS evidence
    FROM task_runs
    LEFT JOIN task_attempts
      ON task_attempts.task_run_id = task_runs.id
     AND task_attempts.attempt = task_runs.current_attempt
    WHERE task_runs.execution_id = :execution_id
      AND task_runs.tenant_id = :tenant_id
      AND task_runs.iteration_key = :iteration_key
    ORDER BY task_runs.created_at, task_runs.task_path
    """
)

_GET_TASK_RUN = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.lifecycle_phase,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        task_runs.retry_at,
        COALESCE(task_attempts.result, task_runs.terminal_result) AS result
        ,task_attempts.failure_category
        ,COALESCE(task_attempts.evidence, task_runs.control_evidence, '{}'::jsonb) AS evidence
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
        NULL::jsonb AS result,
        NULL::text AS failure_category
    FROM updated
    JOIN inserted ON inserted.task_run_id = updated.id
    """
)

_RECORD_TASK_CONTROL = text(
    """
    WITH updated_attempt AS (
        UPDATE task_attempts AS attempts
        SET evidence = CAST(:evidence AS jsonb)
        FROM task_runs
        WHERE attempts.task_run_id = task_runs.id
          AND attempts.tenant_id = task_runs.tenant_id
          AND attempts.task_run_id = :task_run_id
          AND attempts.tenant_id = :tenant_id
          AND attempts.attempt = :attempt
          AND attempts.state = 'RUNNING'
          AND task_runs.current_attempt = :attempt
          AND task_runs.state = 'RUNNING'
        RETURNING attempts.task_run_id, attempts.evidence
    ), updated_run AS (
        UPDATE task_runs
        SET version = version + 1,
            control_evidence = updated_attempt.evidence,
            updated_at = clock_timestamp()
        FROM updated_attempt
        WHERE task_runs.id = updated_attempt.task_run_id
          AND task_runs.tenant_id = :tenant_id
        RETURNING
            task_runs.id,
            task_runs.execution_id,
            task_runs.task_path,
            task_runs.state,
            task_runs.current_attempt,
            task_runs.version,
            task_runs.retry_at,
            NULL::jsonb AS result,
            NULL::text AS failure_category,
            updated_attempt.evidence
    )
    SELECT * FROM updated_run
    """
)

_SKIP_TASK = text(
    """
    UPDATE task_runs
    SET state = 'SUCCESS',
        version = version + 1,
        terminal_result = CAST(:result AS jsonb),
        control_evidence = CAST(:evidence AS jsonb),
        retry_at = NULL,
        updated_at = clock_timestamp()
    WHERE id = :task_run_id
      AND tenant_id = :tenant_id
      AND state = 'WAITING'
    RETURNING
        id,
        execution_id,
        task_path,
        iteration_key,
        state,
        current_attempt,
        version,
        retry_at,
        terminal_result AS result,
        NULL::text AS failure_category,
        control_evidence AS evidence
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
            evidence = CAST(:evidence AS jsonb),
            failure_category = CAST(:failure_category AS text),
            finished_at = clock_timestamp(),
            lease_expires_at = NULL,
            queue_id = NULL
        FROM eligible_attempt
        WHERE attempts.id = eligible_attempt.id
        RETURNING
            attempts.task_run_id,
            attempts.result,
            attempts.failure_category,
            attempts.evidence,
            eligible_attempt.queue_id
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
            finished_attempt.result,
            finished_attempt.failure_category
            ,finished_attempt.evidence
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
            failure_category = CAST(:failure_category AS text),
            finished_at = clock_timestamp(),
            lease_expires_at = NULL,
            queue_id = NULL
        FROM eligible_attempt
        WHERE attempts.id = eligible_attempt.id
        RETURNING
            attempts.task_run_id,
            attempts.result,
            attempts.failure_category,
            eligible_attempt.queue_id
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
            failed_attempt.result,
            failed_attempt.failure_category
    )
    SELECT * FROM retrying_run
    """
)


def _resume_token_digest(resume_token: str) -> str:
    if not resume_token:
        raise ValueError("resume token must not be empty")
    return hashlib.sha256(resume_token.encode("utf-8")).hexdigest()


def _require_complete_claim(worker_id: UUID | None, fencing_token: int | None) -> None:
    if (worker_id is None) != (fencing_token is None):
        raise ValueError("worker_id and fencing_token must be supplied together")
    if fencing_token is not None and fencing_token < 1:
        raise ValueError("worker fencing token must be positive")


class PostgresTaskRunRepository(PostgresExecutionPort, TaskRunRepository):
    async def list_task_runs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        include_iterations: bool = True,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[PersistedTaskRun]:
        if limit is not None and limit < 1:
            raise ValueError("task run limit must be positive")
        if offset < 0:
            raise ValueError("task run offset cannot be negative")
        async with self._services.transactions.tenant(tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_TASK_RUNS,
                {
                    "execution_id": execution_id,
                    "tenant_slug": tenant_id,
                    "include_iterations": include_iterations,
                    "limit": limit,
                    "offset": offset,
                },
            )
            rows = result.mappings().all()
        return [_to_task_run(row) for row in rows]

    async def summarize_task_runs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        include_iterations: bool = True,
    ) -> PersistedTaskRunSummary:
        async with self._services.transactions.tenant(tenant_id) as (connection, _tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _SUMMARIZE_TASK_RUNS,
                        {
                            "execution_id": execution_id,
                            "tenant_slug": tenant_id,
                            "include_iterations": include_iterations,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return PersistedTaskRunSummary.model_validate(row)

    async def list_iteration_summaries(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedIterationSummary]:
        async with self._services.transactions.tenant(tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_ITERATION_SUMMARIES,
                {"execution_id": execution_id, "tenant_slug": tenant_id},
            )
            rows = result.mappings().all()
        return [PersistedIterationSummary.model_validate(row) for row in rows]

    async def ensure_iteration_task_runs(
        self,
        execution_id: UUID,
        iteration_key: str,
        task_ids: tuple[str, ...],
        *,
        tenant_id: str,
        trace_context: dict[str, str] | None = None,
    ) -> list[PersistedTaskRun]:
        if not iteration_key or len(iteration_key) > 512:
            raise ValueError("iteration key must contain between 1 and 512 characters")
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            occurred_at = await connection.scalar(_DATABASE_TIME)
            if not isinstance(occurred_at, datetime):
                raise TypeError("PostgreSQL returned an invalid database timestamp")
            execution_row = (
                (
                    await connection.execute(
                        text(
                            "SELECT labels FROM executions "
                            "WHERE tenant_id = :tenant_id AND id = :execution_id"
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if execution_row is None or not isinstance(execution_row["labels"], dict):
                raise NotFoundError(
                    "execution",
                    execution_id,
                    message=f"execution {execution_id} does not exist",
                )
            execution_labels = execution_row["labels"]
            execution_trace_context = self._services.codec.dumps(trace_context or {})
            rows: list[dict[str, object]] = []
            for task_id in task_ids:
                event_id = new_runtime_id()
                rows.append(
                    {
                        "task_run_id": new_runtime_id(),
                        "tenant_id": tenant_uuid,
                        "execution_id": execution_id,
                        "task_id": task_id,
                        "iteration_key": iteration_key,
                        "lifecycle_phase": TaskRunLifecyclePhase.MAIN.value,
                        "labels": self._services.codec.dumps(
                            task_system_labels(
                                execution_labels,
                                task_id=task_id,
                                lifecycle_phase=TaskRunLifecyclePhase.MAIN.value,
                            )
                        ),
                        "event_id": event_id,
                        "idempotency_key": str(event_id),
                        "correlation_id": new_runtime_id(),
                        "actor_id": "system:loop",
                        "occurred_at": occurred_at,
                        "trace_context": execution_trace_context,
                    }
                )
            if rows:
                await connection.execute(_INSERT_TASK_RUN, rows)
            result = await connection.execute(
                _LIST_ITERATION_TASK_RUNS,
                {
                    "tenant_id": tenant_uuid,
                    "execution_id": execution_id,
                    "iteration_key": iteration_key,
                },
            )
            task_runs = result.mappings().all()
        return [_to_task_run(task_run) for task_run in task_runs]

    async def task_attempt_started_at(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
    ) -> datetime:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            started_at = await connection.scalar(
                _TASK_ATTEMPT_STARTED_AT,
                {
                    "task_run_id": task_run_id,
                    "attempt": attempt,
                    "tenant_id": tenant_uuid,
                },
            )
        if not isinstance(started_at, datetime):
            raise NotFoundError(
                "task run attempt",
                f"{task_run_id}:{attempt}",
                message=f"task run {task_run_id} attempt {attempt} does not exist",
            )
        return started_at

    async def start_task(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
        dispatch: bool = True,
        priority: int = 0,
        worker_group: str | None = None,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
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
                    payload={
                        "dispatch": dispatch,
                        "priority": priority,
                        "workerGroup": worker_group,
                    },
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

    async def record_task_control(
        self,
        task_run_id: UUID,
        attempt: int,
        evidence: dict[str, object],
        *,
        tenant_id: str,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _RECORD_TASK_CONTROL,
                        {
                            "task_run_id": task_run_id,
                            "tenant_id": tenant_uuid,
                            "attempt": attempt,
                            "evidence": self._services.codec.dumps(evidence),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is not None:
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    TaskRunEventType.CONTROL_RECORDED,
                    correlation_id,
                    payload={"attempt": attempt, "evidence": evidence},
                    actor_id="system:flow-control",
                )
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                is_duplicate = (
                    row is not None
                    and TaskRunState(row["state"]) is TaskRunState.RUNNING
                    and int(row["current_attempt"]) == attempt
                    and dict(row.get("evidence") or {}) == evidence
                )
                if not is_duplicate:
                    conflict_message = (
                        f"task run {task_run_id} attempt {attempt} cannot record control evidence"
                    )
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def skip_task(
        self,
        task_run_id: UUID,
        result: dict[str, object],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        control_evidence = evidence or {}
        conflict_message: str | None = None
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _SKIP_TASK,
                        {
                            "task_run_id": task_run_id,
                            "tenant_id": tenant_uuid,
                            "result": self._services.codec.dumps(result),
                            "evidence": self._services.codec.dumps(control_evidence),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is not None:
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    TaskRunEventType.SKIPPED,
                    correlation_id,
                    reason=str(result.get("reason") or "condition evaluated false"),
                    payload={**result, "attempt": 0, "evidence": control_evidence},
                    actor_id="system:flow-control",
                )
                await self._repository._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.TASK,
                    task_run_id,
                    "task skipped before dispatch",
                )
                await self._repository._reconcile_admission_tx(connection, tenant_uuid, limit=100)
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                is_duplicate = (
                    row is not None
                    and TaskRunState(row["state"]) is TaskRunState.SUCCESS
                    and int(row["current_attempt"]) == 0
                    and dict(row.get("result") or {}) == result
                    and dict(row.get("evidence") or {}) == control_evidence
                )
                if not is_duplicate:
                    conflict_message = f"task run {task_run_id} is not waiting"
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
        evidence: dict[str, object] | None = None,
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
            evidence=evidence,
        )

    async def defer_task(
        self,
        task_run_id: UUID,
        attempt: int,
        resume_token: str,
        *,
        tenant_id: str,
        metadata: dict[str, object],
        expires_at: datetime | None = None,
    ) -> PersistedTaskDeferral:
        digest = _resume_token_digest(resume_token)
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            inserted = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO task_deferrals (
                                tenant_id, task_run_id, attempt, resume_token_digest,
                                metadata, expires_at
                            )
                            SELECT
                                :tenant_id, task_runs.id, :attempt, :digest,
                                CAST(:metadata AS jsonb), :expires_at
                            FROM task_runs
                            JOIN task_attempts
                              ON task_attempts.tenant_id = task_runs.tenant_id
                             AND task_attempts.task_run_id = task_runs.id
                             AND task_attempts.attempt = :attempt
                            WHERE task_runs.tenant_id = :tenant_id
                              AND task_runs.id = :task_run_id
                              AND task_runs.current_attempt = :attempt
                              AND task_runs.state = 'RUNNING'
                              AND task_attempts.state = 'RUNNING'
                            ON CONFLICT (tenant_id, task_run_id, attempt) DO NOTHING
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "task_run_id": task_run_id,
                            "attempt": attempt,
                            "digest": digest,
                            "metadata": self._services.codec.dumps(metadata),
                            "expires_at": expires_at,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if inserted is None:
                existing = await self._get_deferral_row(connection, tenant_uuid, task_run_id)
                if (
                    existing is None
                    or int(existing["attempt"]) != attempt
                    or not hmac.compare_digest(str(existing["resume_token_digest"]), digest)
                ):
                    raise TaskStateConflictError(
                        f"task run {task_run_id} attempt {attempt} cannot be deferred"
                    )
                return _to_task_deferral(existing)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE task_runs
                            SET version = version + 1, updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND id = :task_run_id
                            RETURNING id, execution_id, task_path, state,
                                      current_attempt, version, retry_at
                            """
                        ),
                        {"tenant_id": tenant_uuid, "task_run_id": task_run_id},
                    )
                )
                .mappings()
                .one()
            )
            await self._insert_task_event(
                connection,
                tenant_uuid,
                row,
                command_id,
                TaskRunEventType.DEFERRED,
                correlation_id,
                reason="task deferred for asynchronous completion",
                payload={
                    "attempt": attempt,
                    "expiresAt": expires_at.isoformat() if expires_at is not None else None,
                    "metadata": metadata,
                },
            )
        return _to_task_deferral(inserted)

    async def get_task_deferral(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedTaskDeferral | None:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = await self._get_deferral_row(connection, tenant_uuid, task_run_id)
        return _to_task_deferral(row) if row is not None else None

    async def resume_deferred_task(
        self,
        task_run_id: UUID,
        resume_token: str,
        result: dict[str, object],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        digest = _resume_token_digest(resume_token)
        expired = False
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            deferral = await self._get_deferral_row(connection, tenant_uuid, task_run_id)
            if deferral is None or not hmac.compare_digest(
                str(deferral["resume_token_digest"]), digest
            ):
                raise TaskStateConflictError("invalid or unavailable task resume token")
            state = str(deferral["state"])
            if state == "EXPIRED":
                raise TaskStateConflictError("task resume token has expired")
            expires_at = deferral["expires_at"]
            now = await connection.scalar(_DATABASE_TIME)
            if (
                state == "WAITING"
                and expires_at is not None
                and isinstance(now, datetime)
                and now >= expires_at
            ):
                await connection.execute(
                    text(
                        """
                        UPDATE task_deferrals SET state = 'EXPIRED'
                        WHERE tenant_id = :tenant_id AND task_run_id = :task_run_id
                          AND attempt = :attempt AND state = 'WAITING'
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "task_run_id": task_run_id,
                        "attempt": deferral["attempt"],
                    },
                )
                expired = True
            attempt = int(deferral["attempt"])
        if expired:
            raise TaskStateConflictError("task resume token has expired")
        completed = await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.SUCCESS,
            result,
            tenant_id=tenant_id,
            evidence=evidence,
        )
        return completed

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
        failure_category: FailureCategory = FailureCategory.RETRYABLE,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _RETRY_TASK,
                {
                    "task_run_id": task_run_id,
                    "tenant_id": tenant_uuid,
                    "attempt": attempt,
                    "retry_at": retry_at,
                    "result": self._services.codec.dumps({"error": reason}),
                    "worker_id": worker_id,
                    "worker_consumer_id": str(worker_id) if worker_id is not None else None,
                    "fencing_token": fencing_token,
                    "failure_category": failure_category.value,
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
                await self._repository._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.TASK,
                    task_run_id,
                    "task attempt entered retry delay",
                )
                await self._repository._reconcile_admission_tx(connection, tenant_uuid, limit=100)
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
        result: dict[str, object] | None = None,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.NON_RETRYABLE,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        return await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.FAILED,
            result or {"error": reason},
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            failure_category=failure_category,
            evidence=evidence,
        )

    async def cancel_task(
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
            TaskRunState.CANCELLED,
            {"error": reason, "failureCategory": FailureCategory.CANCELLED.value},
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            failure_category=FailureCategory.CANCELLED,
        )

    async def _get_deferral_row(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task_run_id: UUID,
    ) -> RowMapping | None:
        return (
            (
                await connection.execute(
                    text(
                        """
                        SELECT task_run_id, attempt, resume_token_digest, state,
                               metadata, expires_at, deferred_at, resumed_at
                        FROM task_deferrals
                        WHERE tenant_id = :tenant_id AND task_run_id = :task_run_id
                        ORDER BY attempt DESC
                        LIMIT 1
                        """
                    ),
                    {"tenant_id": tenant_id, "task_run_id": task_run_id},
                )
            )
            .mappings()
            .one_or_none()
        )

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
        failure_category: FailureCategory | None = None,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _FINISH_TASK,
                {
                    "task_run_id": task_run_id,
                    "tenant_id": tenant_uuid,
                    "attempt": attempt,
                    "state": state.value,
                    "result": self._services.codec.dumps(result_payload),
                    "evidence": self._services.codec.dumps(evidence or {}),
                    "worker_id": worker_id,
                    "worker_consumer_id": str(worker_id) if worker_id is not None else None,
                    "fencing_token": fencing_token,
                    "failure_category": (
                        failure_category.value if failure_category is not None else None
                    ),
                },
            )
            row = result.mappings().one_or_none()
            if row is not None:
                await store_task_evidence(
                    connection,
                    tenant_uuid,
                    execution_id=row["execution_id"],
                    task_run_id=task_run_id,
                    attempt=attempt,
                    worker_id=worker_id,
                    output=result_payload,
                    evidence=evidence or {},
                )
                await connection.execute(
                    _FINISH_TASK_UPDATE_TASK_DEFERRALS,
                    {
                        "tenant_id": tenant_uuid,
                        "task_run_id": task_run_id,
                        "attempt": attempt,
                        "state": state.value,
                    },
                )
                event_type = {
                    TaskRunState.SUCCESS: TaskRunEventType.SUCCEEDED,
                    TaskRunState.FAILED: TaskRunEventType.FAILED,
                    TaskRunState.CANCELLED: TaskRunEventType.CANCELLED,
                }[state]
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
                await self._repository._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.TASK,
                    task_run_id,
                    f"task reached {state.value}",
                )
                await self._repository._reconcile_admission_tx(connection, tenant_uuid, limit=100)
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
        row: RowMapping | Mapping[str, object],
        event_id: UUID,
        event_type: TaskRunEventType,
        correlation_id: UUID,
        *,
        reason: str | None = None,
        payload: dict[str, object] | None = None,
        actor_id: str = "mvp-executor",
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
                "actor_id": actor_id,
                "reason": reason,
                "payload": self._services.codec.dumps(payload or {}),
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
