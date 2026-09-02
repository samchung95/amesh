"""Execution control persistence internals.

This module owns the SQL and implementation for execution interventions while
the aggregate compatibility class remains in ``execution_repository``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import (
    ExecutionEventType,
    ExecutionState,
    FailureCategory,
    TaskRunEventType,
    TaskRunLifecyclePhase,
    TaskRunState,
    new_runtime_id,
)
from amesh.ports.execution_repository import (
    ExecutionInterventionAction,
    ExecutionInterventionRecord,
    ExecutionStateConflictError,
    PersistedExecution,
)

from .check_repository import evaluate_execution_terminal_checks
from .tenant_context import tenant_transaction

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
        flow_revisions.revision AS flow_revision,
        executions.inputs,
        executions.outputs,
        executions.labels,
        executions.trigger_context,
        executions.created_by,
        executions.created_at,
        executions.updated_at,
        executions.timeout_at,
        executions.cancel_deadline_at,
        executions.lifecycle_evidence
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    JOIN flow_revisions ON flow_revisions.id = executions.flow_revision_id
    WHERE executions.id = :execution_id
      AND tenants.slug = :tenant_slug
    """
)


class _Unset:
    pass


_UNSET = _Unset()


def _require_control_state(
    action: ExecutionInterventionAction,
    state: ExecutionState,
    allowed: set[ExecutionState],
) -> None:
    if state not in allowed:
        expected = ", ".join(sorted(candidate.value for candidate in allowed))
        raise ExecutionStateConflictError(
            f"{action.value} requires execution state {expected}; found {state.value}"
        )


_LOCK_EXECUTION_CONTROL = text(
    """
    SELECT
        executions.*,
        tenants.slug AS tenant_slug,
        clock_timestamp() AS database_now
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    WHERE executions.id = :execution_id
      AND executions.tenant_id = :tenant_id
    FOR UPDATE OF executions
    """
)

_LOCK_TASK_RUNS_CONTROL = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.lifecycle_phase,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        attempts.id AS attempt_id,
        attempts.state AS attempt_state,
        attempts.queue_id,
        attempts.cancellation_acknowledged
    FROM task_runs
    LEFT JOIN task_attempts AS attempts
      ON attempts.task_run_id = task_runs.id
     AND attempts.attempt = task_runs.current_attempt
    WHERE task_runs.tenant_id = :tenant_id
      AND task_runs.execution_id = :execution_id
    ORDER BY task_runs.created_at, task_runs.task_path
    FOR UPDATE OF task_runs
    """
)

_UPDATE_EXECUTION_CONTROL = text(
    """
    UPDATE executions
    SET state = :state,
        epoch = :epoch,
        version = :version,
        lifecycle_evidence = CASE
            WHEN :state = 'RUNNING' AND state IN ('FAILED', 'CANCELLED', 'WARNING')
                THEN '{}'::jsonb
            ELSE lifecycle_evidence
        END,
        timeout_at = :timeout_at,
        cancel_deadline_at = :cancel_deadline_at,
        terminal_at = :terminal_at,
        updated_by = :actor_id,
        updated_at = clock_timestamp()
    WHERE id = :execution_id
      AND tenant_id = :tenant_id
    RETURNING id
    """
)

_UPDATE_TASK_CONTROL = text(
    """
    UPDATE task_runs
    SET state = :state,
        version = version + 1,
        retry_at = NULL,
        terminal_result = CASE WHEN :state = 'WAITING' THEN NULL ELSE terminal_result END,
        control_evidence = CASE
            WHEN :state = 'WAITING' THEN '{}'::jsonb
            ELSE control_evidence
        END,
        updated_at = clock_timestamp()
    WHERE id = :task_run_id
      AND tenant_id = :tenant_id
      AND state = :expected_state
    RETURNING id, execution_id, task_path, state, current_attempt, version, retry_at
    """
)

_INVALIDATE_ATTEMPT = text(
    """
    UPDATE task_attempts
    SET state = :state,
        fencing_token = fencing_token + 1,
        lease_expires_at = NULL,
        queue_id = NULL,
        finished_at = clock_timestamp(),
        failure_category = :failure_category,
        result = CAST(:result AS jsonb)
    WHERE id = :attempt_id
      AND tenant_id = :tenant_id
      AND state = 'RUNNING'
    RETURNING id
    """
)

_REQUEST_ATTEMPT_CANCELLATION = text(
    """
    UPDATE task_attempts
    SET cancellation_requested_at = clock_timestamp()
    WHERE id = :attempt_id
      AND tenant_id = :tenant_id
      AND state = 'RUNNING'
    RETURNING id
    """
)

_DELETE_TASK_QUEUE = text(
    """
    DELETE FROM durable_work_queue
    WHERE id = :queue_id
      AND tenant_id = :tenant_id
    """
)

_INSERT_EXECUTION_INTERVENTION_EVENT = text(
    """
    INSERT INTO execution_events (
        tenant_id, execution_id, sequence, event_id, event_type, schema_version,
        idempotency_key, correlation_id, causation_id, actor_id, reason, occurred_at, payload
    ) VALUES (
        :tenant_id, :execution_id, :sequence, :event_id, :event_type, 2,
        :idempotency_key, :correlation_id, NULL, :actor_id, :reason,
        clock_timestamp(), CAST(:payload AS jsonb)
    )
    """
)

_LIST_EXECUTION_INTERVENTIONS = text(
    """
    SELECT sequence, event_type, actor_id, reason, occurred_at, payload
    FROM execution_events
    WHERE tenant_id = :tenant_id
      AND execution_id = :execution_id
      AND payload ? 'intervention'
    ORDER BY sequence
    """
)


class _ExecutionControlMixin:
    """Execution control methods mixed into the compatibility repository."""

    _engine: AsyncEngine

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
        raise NotImplementedError

    async def apply_execution_intervention(
        self,
        execution_id: UUID,
        action: ExecutionInterventionAction,
        *,
        tenant_id: str,
        expected_version: int,
        expected_epoch: int,
        actor_id: str,
        reason: str,
        grace_period: timedelta = timedelta(seconds=30),
        reset_task_ids: tuple[str, ...] = (),
        checkpoint_task_id: str | None = None,
        restart_timeout: timedelta | None = None,
    ) -> PersistedExecution:
        if grace_period.total_seconds() < 0:
            raise ValueError("cancellation grace period cannot be negative")
        if restart_timeout is not None and restart_timeout.total_seconds() <= 0:
            raise ValueError("restart timeout must be positive")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            execution = await self._lock_execution_for_control(
                connection,
                tenant_uuid,
                execution_id,
            )
            self._require_intervention_fence(
                execution,
                expected_version=expected_version,
                expected_epoch=expected_epoch,
            )
            tasks = await self._lock_tasks_for_control(connection, tenant_uuid, execution_id)
            state = ExecutionState(execution["state"])
            version = int(execution["version"])
            epoch = int(execution["epoch"])
            now = execution["database_now"]
            if not isinstance(now, datetime):
                raise TypeError("PostgreSQL returned an invalid database timestamp")
            correlation_id = new_runtime_id()

            if action is ExecutionInterventionAction.PAUSE:
                _require_control_state(action, state, {ExecutionState.RUNNING})
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.PAUSED,
                    version=version + 1,
                    epoch=epoch,
                    actor_id=actor_id,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.PAUSED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
            elif action is ExecutionInterventionAction.RESUME:
                _require_control_state(action, state, {ExecutionState.PAUSED})
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.RUNNING,
                    version=version + 1,
                    epoch=epoch,
                    actor_id=actor_id,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.RESUMED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
            elif action is ExecutionInterventionAction.REQUEST_CANCEL:
                _require_control_state(
                    action,
                    state,
                    {ExecutionState.RUNNING, ExecutionState.PAUSED, ExecutionState.QUEUED},
                )
                deadline = now + grace_period
                await self._request_task_cancellation(
                    connection,
                    tenant_uuid,
                    tasks,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.CANCELLING,
                    version=version + 1,
                    epoch=epoch,
                    actor_id=actor_id,
                    cancel_deadline_at=deadline,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.CANCEL_REQUESTED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                    extra_payload={"graceDeadline": deadline.isoformat()},
                )
            elif action in {
                ExecutionInterventionAction.CONFIRM_CANCEL,
                ExecutionInterventionAction.FORCE_CANCEL,
            }:
                _require_control_state(action, state, {ExecutionState.CANCELLING})
                if action is ExecutionInterventionAction.CONFIRM_CANCEL:
                    unacknowledged = [
                        row
                        for row in tasks
                        if row["attempt_state"] == "RUNNING"
                        and not bool(row["cancellation_acknowledged"])
                    ]
                    if unacknowledged:
                        raise ExecutionStateConflictError(
                            "running attempts have not acknowledged cancellation"
                        )
                else:
                    deadline = execution["cancel_deadline_at"]
                    if not isinstance(deadline, datetime) or now < deadline:
                        raise ExecutionStateConflictError(
                            "force cancellation is not available before the grace deadline"
                        )
                await self._terminate_tasks(
                    connection,
                    tenant_uuid,
                    [
                        task
                        for task in tasks
                        if task["lifecycle_phase"] == TaskRunLifecyclePhase.MAIN.value
                        or task["state"] == TaskRunState.RUNNING.value
                    ],
                    task_state=TaskRunState.CANCELLED,
                    attempt_state="CANCELLED",
                    category=FailureCategory.CANCELLED,
                    event_type=TaskRunEventType.CANCELLED,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.CANCELLED,
                    version=version + 1,
                    epoch=epoch,
                    actor_id=actor_id,
                    cancel_deadline_at=None,
                    terminal_at=now,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.CANCELLED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
                await evaluate_execution_terminal_checks(
                    connection,
                    tenant_uuid,
                    flow_revision_id=UUID(str(execution["flow_revision_id"])),
                    execution_id=execution_id,
                    execution_state=ExecutionState.CANCELLED.value,
                    namespace=str(execution["namespace_name"]),
                    flow_id=str(execution["flow_key"]),
                    flow_revision=int(
                        await connection.scalar(
                            text("SELECT revision FROM flow_revisions WHERE id = :id"),
                            {"id": execution["flow_revision_id"]},
                        )
                    ),
                    created_at=execution["created_at"],
                    terminal_at=now,
                    inputs=dict(execution["inputs"]),
                    trigger=dict(execution["trigger_context"]),
                    labels=dict(execution["labels"]),
                )
            elif action is ExecutionInterventionAction.RESTART:
                _require_control_state(
                    action,
                    state,
                    {ExecutionState.FAILED, ExecutionState.CANCELLED, ExecutionState.WARNING},
                )
                if not reset_task_ids:
                    raise ValueError("restart requires at least one reset task")
                known_task_ids = {str(row["task_path"]) for row in tasks}
                unknown = sorted(set(reset_task_ids) - known_task_ids)
                if unknown:
                    raise ValueError("restart reset tasks do not exist: " + ", ".join(unknown))
                effective_reset_task_ids = frozenset(
                    {
                        *reset_task_ids,
                        *(
                            str(row["task_path"])
                            for row in tasks
                            if row["lifecycle_phase"] != TaskRunLifecyclePhase.MAIN.value
                        ),
                    }
                )
                await self._restart_tasks(
                    connection,
                    tenant_uuid,
                    tasks,
                    reset_task_ids=effective_reset_task_ids,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
                timeout_at = now + restart_timeout if restart_timeout is not None else None
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.RUNNING,
                    version=version + 2,
                    epoch=epoch + 1,
                    actor_id=actor_id,
                    timeout_at=timeout_at,
                    cancel_deadline_at=None,
                    terminal_at=None,
                )
                restart_payload: dict[str, object] = {
                    "checkpointTaskId": checkpoint_task_id,
                    "resetTaskIds": sorted(effective_reset_task_ids),
                    "nextEpoch": epoch + 1,
                }
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.RESTART_REQUESTED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                    extra_payload=restart_payload,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 2,
                    event_type=ExecutionEventType.STARTED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                    extra_payload=restart_payload,
                )
            else:
                raise ValueError(f"unsupported execution intervention {action.value}")

            row = (
                (
                    await connection.execute(
                        _GET_EXECUTION,
                        {"execution_id": execution_id, "tenant_slug": tenant_id},
                    )
                )
                .mappings()
                .one()
            )
        return _to_execution(row)

    async def list_execution_interventions(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionInterventionRecord]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            exists = await connection.scalar(
                text("SELECT id FROM executions WHERE id = :execution_id"),
                {"execution_id": execution_id},
            )
            if exists is None:
                raise LookupError(f"execution {execution_id} does not exist")
            rows = (
                (
                    await connection.execute(
                        _LIST_EXECUTION_INTERVENTIONS,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .all()
            )
        return [
            ExecutionInterventionRecord(
                sequence=int(row["sequence"]),
                action=ExecutionInterventionAction(row["payload"]["intervention"]),
                event_type=row["event_type"],
                actor_id=row["actor_id"],
                reason=row["reason"],
                occurred_at=row["occurred_at"],
                payload=row["payload"],
            )
            for row in rows
        ]

    async def timeout_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        actor_id = "system:execution-timeout"
        reason = "execution deadline exceeded"
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            execution = await self._lock_execution_for_control(
                connection,
                tenant_uuid,
                execution_id,
            )
            state = ExecutionState(execution["state"])
            epoch = int(execution["epoch"])
            now = execution["database_now"]
            timeout_at = execution["timeout_at"]
            if epoch != expected_epoch:
                raise ExecutionStateConflictError(
                    f"execution {execution_id} is fenced at epoch {epoch}; received {expected_epoch}"
                )
            if (
                state not in {ExecutionState.RUNNING, ExecutionState.PAUSED}
                or not isinstance(now, datetime)
                or not isinstance(timeout_at, datetime)
                or now < timeout_at
            ):
                raise ExecutionStateConflictError(
                    f"execution {execution_id} is not due for timeout"
                )
            version = int(execution["version"])
            tasks = await self._lock_tasks_for_control(connection, tenant_uuid, execution_id)
            correlation_id = new_runtime_id()
            await self._timeout_tasks(
                connection,
                tenant_uuid,
                tasks,
                actor_id=actor_id,
                reason=reason,
                correlation_id=correlation_id,
            )
            await self._update_execution_control(
                connection,
                execution,
                state=ExecutionState.FAILED,
                version=version + 1,
                epoch=epoch,
                actor_id=actor_id,
                cancel_deadline_at=None,
                terminal_at=now,
            )
            await connection.execute(
                _INSERT_EXECUTION_INTERVENTION_EVENT,
                {
                    "tenant_id": tenant_uuid,
                    "execution_id": execution_id,
                    "sequence": version + 1,
                    "event_id": new_runtime_id(),
                    "event_type": ExecutionEventType.FAILED.value,
                    "idempotency_key": f"timeout:{execution_id}:{epoch}",
                    "correlation_id": correlation_id,
                    "actor_id": actor_id,
                    "reason": reason,
                    "payload": json.dumps({"failureCategory": FailureCategory.TIMED_OUT.value}),
                },
            )
            row = (
                (
                    await connection.execute(
                        _GET_EXECUTION,
                        {"execution_id": execution_id, "tenant_slug": tenant_id},
                    )
                )
                .mappings()
                .one()
            )
        return _to_execution(row)

    async def _lock_execution_for_control(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
    ) -> RowMapping:
        row = (
            (
                await connection.execute(
                    _LOCK_EXECUTION_CONTROL,
                    {"tenant_id": tenant_id, "execution_id": execution_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise LookupError(f"execution {execution_id} does not exist")
        return row

    async def _lock_tasks_for_control(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
    ) -> list[RowMapping]:
        return list(
            (
                await connection.execute(
                    _LOCK_TASK_RUNS_CONTROL,
                    {"tenant_id": tenant_id, "execution_id": execution_id},
                )
            )
            .mappings()
            .all()
        )

    @staticmethod
    def _require_intervention_fence(
        execution: RowMapping,
        *,
        expected_version: int,
        expected_epoch: int,
    ) -> None:
        if int(execution["version"]) != expected_version:
            raise ExecutionStateConflictError(
                f"execution version is {execution['version']}; received {expected_version}"
            )
        if int(execution["epoch"]) != expected_epoch:
            raise ExecutionStateConflictError(
                f"execution epoch is {execution['epoch']}; received {expected_epoch}"
            )

    async def _update_execution_control(
        self,
        connection: AsyncConnection,
        execution: RowMapping,
        *,
        state: ExecutionState,
        version: int,
        epoch: int,
        actor_id: str,
        timeout_at: datetime | _Unset | None = _UNSET,
        cancel_deadline_at: datetime | _Unset | None = _UNSET,
        terminal_at: datetime | _Unset | None = _UNSET,
    ) -> None:
        changed = await connection.scalar(
            _UPDATE_EXECUTION_CONTROL,
            {
                "execution_id": execution["id"],
                "tenant_id": execution["tenant_id"],
                "state": state.value,
                "epoch": epoch,
                "version": version,
                "timeout_at": (execution["timeout_at"] if timeout_at is _UNSET else timeout_at),
                "cancel_deadline_at": (
                    execution["cancel_deadline_at"]
                    if cancel_deadline_at is _UNSET
                    else cancel_deadline_at
                ),
                "terminal_at": (execution["terminal_at"] if terminal_at is _UNSET else terminal_at),
                "actor_id": actor_id,
            },
        )
        if changed is None:
            raise ExecutionStateConflictError(
                f"execution {execution['id']} changed during intervention"
            )

    async def _request_task_cancellation(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        tasks: list[RowMapping],
        *,
        actor_id: str,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        for task in tasks:
            state = TaskRunState(task["state"])
            if (
                state in {TaskRunState.WAITING, TaskRunState.RETRY_DELAY}
                and task["lifecycle_phase"] == TaskRunLifecyclePhase.MAIN.value
            ):
                changed = await self._update_task_control(
                    connection,
                    tenant_id,
                    task,
                    TaskRunState.CANCELLED,
                )
                await self._insert_task_event(
                    connection,
                    tenant_id,
                    changed,
                    new_runtime_id(),
                    TaskRunEventType.CANCELLED,
                    correlation_id,
                    reason=reason,
                    payload={
                        "intervention": ExecutionInterventionAction.REQUEST_CANCEL.value,
                        "failureCategory": FailureCategory.CANCELLED.value,
                    },
                    actor_id=actor_id,
                )
            elif state is TaskRunState.RUNNING and task["attempt_id"] is not None:
                await connection.execute(
                    _REQUEST_ATTEMPT_CANCELLATION,
                    {"tenant_id": tenant_id, "attempt_id": task["attempt_id"]},
                )

    async def _terminate_tasks(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        tasks: list[RowMapping],
        *,
        task_state: TaskRunState,
        attempt_state: str,
        category: FailureCategory,
        event_type: TaskRunEventType,
        actor_id: str,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        for task in tasks:
            state = TaskRunState(task["state"])
            if state in {TaskRunState.SUCCESS, TaskRunState.FAILED, TaskRunState.CANCELLED}:
                continue
            if task["attempt_state"] == "RUNNING" and task["attempt_id"] is not None:
                await self._invalidate_attempt(
                    connection,
                    tenant_id,
                    task,
                    attempt_state=attempt_state,
                    category=category,
                    reason=reason,
                )
            changed = await self._update_task_control(
                connection,
                tenant_id,
                task,
                task_state,
            )
            await self._insert_task_event(
                connection,
                tenant_id,
                changed,
                new_runtime_id(),
                event_type,
                correlation_id,
                reason=reason,
                payload={"failureCategory": category.value},
                actor_id=actor_id,
            )

    async def _restart_tasks(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        tasks: list[RowMapping],
        *,
        reset_task_ids: frozenset[str],
        actor_id: str,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        for task in tasks:
            if str(task["task_path"]) not in reset_task_ids:
                continue
            if task["attempt_state"] == "RUNNING" and task["attempt_id"] is not None:
                await self._invalidate_attempt(
                    connection,
                    tenant_id,
                    task,
                    attempt_state="CANCELLED",
                    category=FailureCategory.CANCELLED,
                    reason="superseded by execution restart",
                )
            changed = await self._update_task_control(
                connection,
                tenant_id,
                task,
                TaskRunState.WAITING,
            )
            await self._insert_task_event(
                connection,
                tenant_id,
                changed,
                new_runtime_id(),
                TaskRunEventType.RESTARTED,
                correlation_id,
                reason=reason,
                payload={"intervention": ExecutionInterventionAction.RESTART.value},
                actor_id=actor_id,
            )

    async def _timeout_tasks(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        tasks: list[RowMapping],
        *,
        actor_id: str,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        for task in tasks:
            state = TaskRunState(task["state"])
            if state in {TaskRunState.SUCCESS, TaskRunState.FAILED, TaskRunState.CANCELLED}:
                continue
            target_state = (
                TaskRunState.FAILED if state is TaskRunState.RUNNING else TaskRunState.CANCELLED
            )
            event_type = (
                TaskRunEventType.FAILED
                if target_state is TaskRunState.FAILED
                else TaskRunEventType.CANCELLED
            )
            category = (
                FailureCategory.TIMED_OUT
                if target_state is TaskRunState.FAILED
                else FailureCategory.CANCELLED
            )
            if task["attempt_state"] == "RUNNING" and task["attempt_id"] is not None:
                await self._invalidate_attempt(
                    connection,
                    tenant_id,
                    task,
                    attempt_state="TIMED_OUT",
                    category=FailureCategory.TIMED_OUT,
                    reason=reason,
                )
            changed = await self._update_task_control(
                connection,
                tenant_id,
                task,
                target_state,
            )
            await self._insert_task_event(
                connection,
                tenant_id,
                changed,
                new_runtime_id(),
                event_type,
                correlation_id,
                reason=reason,
                payload={"failureCategory": category.value},
                actor_id=actor_id,
            )

    async def _invalidate_attempt(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task: RowMapping,
        *,
        attempt_state: str,
        category: FailureCategory,
        reason: str,
    ) -> None:
        changed = await connection.scalar(
            _INVALIDATE_ATTEMPT,
            {
                "tenant_id": tenant_id,
                "attempt_id": task["attempt_id"],
                "state": attempt_state,
                "failure_category": category.value,
                "result": json.dumps({"error": reason, "failureCategory": category.value}),
            },
        )
        if changed is None:
            raise ExecutionStateConflictError(
                f"task attempt for {task['task_path']} changed during intervention"
            )
        if task["queue_id"] is not None:
            await connection.execute(
                _DELETE_TASK_QUEUE,
                {"tenant_id": tenant_id, "queue_id": task["queue_id"]},
            )

    async def _update_task_control(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task: RowMapping,
        state: TaskRunState,
    ) -> RowMapping:
        row = (
            (
                await connection.execute(
                    _UPDATE_TASK_CONTROL,
                    {
                        "tenant_id": tenant_id,
                        "task_run_id": task["id"],
                        "expected_state": task["state"],
                        "state": state.value,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise ExecutionStateConflictError(
                f"task run {task['task_path']} changed during intervention"
            )
        return row

    async def _insert_execution_intervention_event(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
        *,
        sequence: int,
        event_type: ExecutionEventType,
        action: ExecutionInterventionAction,
        actor_id: str,
        reason: str,
        correlation_id: UUID,
        extra_payload: dict[str, object] | None = None,
    ) -> None:
        event_id = new_runtime_id()
        payload: dict[str, object] = {"intervention": action.value}
        payload.update(extra_payload or {})
        await connection.execute(
            _INSERT_EXECUTION_INTERVENTION_EVENT,
            {
                "tenant_id": tenant_id,
                "execution_id": execution_id,
                "sequence": sequence,
                "event_id": event_id,
                "event_type": event_type.value,
                "idempotency_key": str(event_id),
                "correlation_id": correlation_id,
                "actor_id": actor_id,
                "reason": reason,
                "payload": json.dumps(payload),
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
        flow_revision=row["flow_revision"],
        inputs=row["inputs"],
        outputs=row["outputs"],
        labels=row["labels"],
        trigger=row["trigger_context"],
        created_by=row["created_by"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        timeout_at=row["timeout_at"],
        cancel_deadline_at=row["cancel_deadline_at"],
        lifecycle_evidence=row.get("lifecycle_evidence") or {},
    )
