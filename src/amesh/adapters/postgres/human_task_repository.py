from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.human_tasks import (
    AppForm,
    HumanTask,
    HumanTaskAction,
    HumanTaskActionKind,
    HumanTaskActionRequest,
    HumanTaskCreate,
    HumanTaskNotification,
    HumanTaskState,
    WorkflowApp,
    WorkflowAppSpec,
    terminal_state,
)

from .tenant_context import tenant_transaction


class WorkflowAppVersionConflict(RuntimeError):
    """Raised when an app write does not match its current resource version."""


class HumanTaskConflict(RuntimeError):
    """Raised when an action is invalid for the current durable task state."""


_LIST_APPS = text(
    """
    SELECT apps.namespace_name, apps.app_id, apps.resource_version,
           revisions.revision, revisions.flow_id, revisions.flow_revision,
           revisions.definition, revisions.created_by, revisions.created_at
    FROM workflow_apps AS apps
    JOIN workflow_app_revisions AS revisions
      ON revisions.tenant_id = apps.tenant_id
     AND revisions.namespace_name = apps.namespace_name
     AND revisions.app_id = apps.app_id
     AND revisions.revision = apps.current_revision
    WHERE apps.tenant_id = :tenant_uuid
      AND (CAST(:namespace AS text) IS NULL OR apps.namespace_name = :namespace)
    ORDER BY apps.namespace_name, (revisions.definition ->> 'title'), apps.app_id
    """
)

_GET_APP = text(
    """
    SELECT apps.namespace_name, apps.app_id, apps.resource_version,
           revisions.revision, revisions.flow_id, revisions.flow_revision,
           revisions.definition, revisions.created_by, revisions.created_at
    FROM workflow_apps AS apps
    JOIN workflow_app_revisions AS revisions
      ON revisions.tenant_id = apps.tenant_id
     AND revisions.namespace_name = apps.namespace_name
     AND revisions.app_id = apps.app_id
     AND revisions.revision = COALESCE(:revision, apps.current_revision)
    WHERE apps.tenant_id = :tenant_uuid
      AND apps.namespace_name = :namespace
      AND apps.app_id = :app_id
    """
)

_LOCK_APP = text(
    """
    SELECT current_revision, resource_version
    FROM workflow_apps
    WHERE tenant_id = :tenant_uuid AND namespace_name = :namespace AND app_id = :app_id
    FOR UPDATE
    """
)

_INSERT_APP = text(
    """
    INSERT INTO workflow_apps (
        tenant_id, namespace_name, app_id, current_revision, resource_version,
        created_by, updated_by
    ) VALUES (
        :tenant_uuid, :namespace, :app_id, 1, 1, :actor_id, :actor_id
    )
    """
)

_UPDATE_APP = text(
    """
    UPDATE workflow_apps
    SET current_revision = :revision,
        resource_version = resource_version + 1,
        updated_by = :actor_id,
        updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_uuid AND namespace_name = :namespace AND app_id = :app_id
      AND resource_version = :expected_version
    RETURNING resource_version
    """
)

_INSERT_APP_REVISION = text(
    """
    INSERT INTO workflow_app_revisions (
        tenant_id, namespace_name, app_id, revision, flow_id, flow_revision,
        definition, created_by
    ) VALUES (
        :tenant_uuid, :namespace, :app_id, :revision, :flow_id, :flow_revision,
        CAST(:definition AS jsonb), :actor_id
    )
    """
)

_INSERT_HUMAN_TASK = text(
    """
    INSERT INTO human_tasks (
        human_task_id, tenant_id, namespace_name, execution_id, task_run_id, attempt,
        title, description, form, assignee_ids, group_ids, deadline_at,
        escalation_assignee_ids, escalation_group_ids, created_by
    ) VALUES (
        :human_task_id, :tenant_uuid, :namespace, :execution_id, :task_run_id, :attempt,
        :title, :description, CAST(:form AS jsonb), CAST(:assignee_ids AS uuid[]),
        CAST(:group_ids AS uuid[]), :deadline_at, CAST(:escalation_assignee_ids AS uuid[]),
        CAST(:escalation_group_ids AS uuid[]), :actor_id
    )
    ON CONFLICT (tenant_id, task_run_id, attempt) DO NOTHING
    RETURNING human_task_id
    """
)

_GET_TASK_BY_RUN = text(
    """
    SELECT * FROM human_tasks
    WHERE tenant_id = :tenant_uuid AND task_run_id = :task_run_id AND attempt = :attempt
    """
)

_TASK_VISIBILITY = """
    (:include_all OR :actor_id = ANY(tasks.assignee_ids) OR EXISTS (
        SELECT 1 FROM auth_group_memberships AS memberships
        WHERE memberships.member_id = :actor_id
          AND memberships.group_id = ANY(tasks.group_ids)
    ))
"""

_LIST_TASKS = text(
    f"""
    SELECT tasks.* FROM human_tasks AS tasks
    WHERE tasks.tenant_id = :tenant_uuid
      AND (CAST(:namespace AS text) IS NULL OR tasks.namespace_name = :namespace)
      AND (:include_closed OR tasks.state IN ('OPEN', 'ESCALATED'))
      AND {_TASK_VISIBILITY}
    ORDER BY
      CASE WHEN tasks.state IN ('OPEN', 'ESCALATED') THEN 0 ELSE 1 END,
      tasks.deadline_at NULLS LAST, tasks.created_at DESC
    """
)

_GET_TASK = text(
    f"""
    SELECT tasks.* FROM human_tasks AS tasks
    WHERE tasks.tenant_id = :tenant_uuid AND tasks.human_task_id = :human_task_id
      AND {_TASK_VISIBILITY}
    """
)

_LOCK_TASK = text(
    """
    SELECT * FROM human_tasks
    WHERE tenant_id = :tenant_uuid AND human_task_id = :human_task_id
    FOR UPDATE
    """
)

_LIST_ACTIONS = text(
    """
    SELECT * FROM human_task_actions
    WHERE tenant_id = :tenant_uuid AND human_task_id = :human_task_id
    ORDER BY occurred_at, action_id
    """
)

_GET_ACTION_BY_KEY = text(
    """
    SELECT action FROM human_task_actions
    WHERE tenant_id = :tenant_uuid AND human_task_id = :human_task_id
      AND idempotency_key = :idempotency_key
    """
)

_INSERT_ACTION = text(
    """
    INSERT INTO human_task_actions (
        action_id, tenant_id, human_task_id, idempotency_key, action, actor_id,
        reason, form_values, comment, artifact_uri, assignee_ids, group_ids
    ) VALUES (
        :action_id, :tenant_uuid, :human_task_id, :idempotency_key, :action,
        :actor_id, :reason, CAST(:form_values AS jsonb), :comment, :artifact_uri,
        CAST(:assignee_ids AS uuid[]), CAST(:group_ids AS uuid[])
    )
    """
)

_TERMINAL_DECISION = text(
    """
    UPDATE human_tasks
    SET state = :state, resume_state = 'PENDING', version = version + 1,
        decided_by = :actor_id, decided_at = clock_timestamp(), reason = :reason,
        form_values = CAST(:form_values AS jsonb), updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_uuid AND human_task_id = :human_task_id
      AND state IN ('OPEN', 'ESCALATED')
    RETURNING *
    """
)

_DELEGATE_TASK = text(
    """
    UPDATE human_tasks
    SET assignee_ids = CAST(:assignee_ids AS uuid[]),
        group_ids = CAST(:group_ids AS uuid[]), version = version + 1,
        updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_uuid AND human_task_id = :human_task_id
      AND state IN ('OPEN', 'ESCALATED')
    RETURNING *
    """
)

_INSERT_NOTIFICATION = text(
    """
    INSERT INTO human_task_notifications (
        notification_id, tenant_id, human_task_id, recipient_id, recipient_type,
        kind, title, message, deadline_at
    ) VALUES (
        :notification_id, :tenant_uuid, :human_task_id, :recipient_id, :recipient_type,
        :kind, :title, :message, :deadline_at
    ) ON CONFLICT (tenant_id, human_task_id, recipient_id, recipient_type, kind)
      DO NOTHING
    """
)

_LIST_NOTIFICATIONS = text(
    """
    SELECT notifications.*
    FROM human_task_notifications AS notifications
    WHERE notifications.tenant_id = :tenant_uuid
      AND (notifications.recipient_id = :actor_id OR (
          notifications.recipient_type = 'GROUP' AND EXISTS (
              SELECT 1 FROM auth_group_memberships AS memberships
              WHERE memberships.member_id = :actor_id
                AND memberships.group_id = notifications.recipient_id
          )
      ))
    ORDER BY notifications.created_at DESC, notifications.notification_id
    LIMIT :limit
    """
)

_DUE_TASKS = text(
    """
    SELECT * FROM human_tasks
    WHERE tenant_id = :tenant_uuid AND state = 'OPEN'
      AND deadline_at IS NOT NULL AND deadline_at <= clock_timestamp()
    ORDER BY deadline_at, human_task_id
    FOR UPDATE SKIP LOCKED
    """
)

_ESCALATE_TASK = text(
    """
    UPDATE human_tasks
    SET state = 'ESCALATED',
        assignee_ids = CASE WHEN cardinality(escalation_assignee_ids) > 0
                            THEN escalation_assignee_ids ELSE assignee_ids END,
        group_ids = CASE WHEN cardinality(escalation_group_ids) > 0
                         THEN escalation_group_ids ELSE group_ids END,
        version = version + 1, updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_uuid AND human_task_id = :human_task_id AND state = 'OPEN'
    RETURNING *
    """
)

_LIST_PENDING_RESUME = text(
    """
    SELECT * FROM human_tasks
    WHERE tenant_id = :tenant_uuid AND resume_state = 'PENDING'
    ORDER BY updated_at, human_task_id
    LIMIT :limit
    """
)

_MARK_RESUMED = text(
    """
    UPDATE human_tasks
    SET resume_state = 'COMPLETED', updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_uuid AND human_task_id = :human_task_id
      AND resume_state = 'PENDING'
    """
)

_INSERT_AUDIT = text(
    """
    INSERT INTO audit_events (
        event_id, tenant_id, actor_id, action, resource_type, resource_id,
        outcome, reason, source, evidence, occurred_at
    ) VALUES (
        :event_id, :tenant_uuid, :actor_id, :action, :resource_type, :resource_id,
        'SUCCESS', :reason, CAST(:source AS jsonb), CAST(:evidence AS jsonb),
        clock_timestamp()
    )
    """
)


def _app_from_row(row: RowMapping) -> WorkflowApp:
    definition = dict(row["definition"])
    definition.update(
        {
            "namespace": row["namespace_name"],
            "appId": row["app_id"],
            "revision": row["revision"],
            "resourceVersion": row["resource_version"],
            "flowId": row["flow_id"],
            "flowRevision": row["flow_revision"],
            "createdBy": row["created_by"],
            "createdAt": row["created_at"],
        }
    )
    return WorkflowApp.model_validate(definition)


def _action_from_row(row: RowMapping) -> HumanTaskAction:
    return HumanTaskAction(
        actionId=row["action_id"],
        action=row["action"],
        actorId=row["actor_id"],
        reason=row["reason"],
        formValues=dict(row["form_values"]),
        comment=row["comment"],
        artifactUri=row["artifact_uri"],
        occurredAt=row["occurred_at"],
    )


async def _task_from_row(
    connection: AsyncConnection,
    row: RowMapping,
    tenant_uuid: UUID,
) -> HumanTask:
    actions = (
        await connection.execute(
            _LIST_ACTIONS,
            {"tenant_uuid": tenant_uuid, "human_task_id": row["human_task_id"]},
        )
    ).mappings()
    return HumanTask(
        humanTaskId=row["human_task_id"],
        namespace=row["namespace_name"],
        executionId=row["execution_id"],
        taskRunId=row["task_run_id"],
        attempt=row["attempt"],
        title=row["title"],
        description=row["description"],
        form=AppForm.model_validate(row["form"]),
        assigneeIds=tuple(row["assignee_ids"]),
        groupIds=tuple(row["group_ids"]),
        deadlineAt=row["deadline_at"],
        state=row["state"],
        version=row["version"],
        createdAt=row["created_at"],
        decidedBy=row["decided_by"],
        decidedAt=row["decided_at"],
        reason=row["reason"],
        formValues=dict(row["form_values"]),
        actions=tuple(_action_from_row(action) for action in actions),
    )


class PostgresHumanTaskRepository:
    """Versioned workflow apps and participant-scoped durable human tasks."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def list_apps(
        self, *, tenant_id: str, namespace: str | None = None
    ) -> Sequence[WorkflowApp]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                await connection.execute(
                    _LIST_APPS, {"tenant_uuid": tenant_uuid, "namespace": namespace}
                )
            ).mappings()
            return tuple(_app_from_row(row) for row in rows)

    async def get_app(
        self,
        namespace: str,
        app_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> WorkflowApp:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_APP,
                        {
                            "tenant_uuid": tenant_uuid,
                            "namespace": namespace,
                            "app_id": app_id,
                            "revision": revision,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError(f"app {namespace}/{app_id} does not exist")
            return _app_from_row(row)

    async def upsert_app(
        self,
        namespace: str,
        app_id: str,
        spec: WorkflowAppSpec,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None,
    ) -> WorkflowApp:
        if spec.flow_revision is None or spec.form is None:
            raise ValueError("app flow revision and form must be resolved before persistence")
        definition = json.dumps(spec.model_dump(mode="json", by_alias=True), separators=(",", ":"))
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            values: dict[str, Any] = {
                "tenant_uuid": tenant_uuid,
                "namespace": namespace,
                "app_id": app_id,
                "flow_id": spec.flow_id,
                "flow_revision": spec.flow_revision,
                "definition": definition,
                "actor_id": actor_id,
            }
            current = (await connection.execute(_LOCK_APP, values)).mappings().one_or_none()
            try:
                if current is None:
                    if expected_version is not None:
                        raise WorkflowAppVersionConflict("app does not exist at expected version")
                    revision = 1
                    await connection.execute(_INSERT_APP, values)
                else:
                    if (
                        expected_version is None
                        or int(current["resource_version"]) != expected_version
                    ):
                        raise WorkflowAppVersionConflict("app resource version is stale")
                    revision = int(current["current_revision"]) + 1
                    updated = await connection.scalar(
                        _UPDATE_APP,
                        {**values, "revision": revision, "expected_version": expected_version},
                    )
                    if updated is None:
                        raise WorkflowAppVersionConflict("app resource version is stale")
                await connection.execute(_INSERT_APP_REVISION, {**values, "revision": revision})
            except IntegrityError as exc:
                raise WorkflowAppVersionConflict("app write conflicts with current state") from exc
            await connection.execute(
                _INSERT_AUDIT,
                {
                    "event_id": new_runtime_id(),
                    "tenant_uuid": tenant_uuid,
                    "actor_id": actor_id,
                    "action": "APP_REVISION_CREATED",
                    "resource_type": "app",
                    "resource_id": f"{namespace}/{app_id}",
                    "reason": "",
                    "source": json.dumps({"namespace": namespace, "flowId": spec.flow_id}),
                    "evidence": json.dumps(
                        {"revision": revision, "flowRevision": spec.flow_revision}
                    ),
                },
            )
            row = (
                (
                    await connection.execute(
                        _GET_APP,
                        {
                            "tenant_uuid": tenant_uuid,
                            "namespace": namespace,
                            "app_id": app_id,
                            "revision": revision,
                        },
                    )
                )
                .mappings()
                .one()
            )
            return _app_from_row(row)

    async def ensure_task(
        self,
        task: HumanTaskCreate,
        *,
        tenant_id: str,
        actor_id: str = "system:executor",
    ) -> HumanTask:
        task_id = new_runtime_id()
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            values = {
                "human_task_id": task_id,
                "tenant_uuid": tenant_uuid,
                "namespace": task.namespace,
                "execution_id": task.execution_id,
                "task_run_id": task.task_run_id,
                "attempt": task.attempt,
                "title": task.title,
                "description": task.description,
                "form": task.form.model_dump_json(by_alias=True),
                "assignee_ids": list(task.assignee_ids),
                "group_ids": list(task.group_ids),
                "deadline_at": task.deadline_at,
                "escalation_assignee_ids": list(task.escalation_assignee_ids),
                "escalation_group_ids": list(task.escalation_group_ids),
                "actor_id": actor_id,
            }
            inserted = await connection.scalar(_INSERT_HUMAN_TASK, values)
            row = (
                (
                    await connection.execute(
                        _GET_TASK_BY_RUN,
                        {
                            "tenant_uuid": tenant_uuid,
                            "task_run_id": task.task_run_id,
                            "attempt": task.attempt,
                        },
                    )
                )
                .mappings()
                .one()
            )
            if inserted is not None:
                await self._notify(
                    connection,
                    tenant_uuid,
                    row,
                    kind="ASSIGNED",
                    message="A human approval is waiting for your response.",
                )
                await connection.execute(
                    _INSERT_AUDIT,
                    {
                        "event_id": new_runtime_id(),
                        "tenant_uuid": tenant_uuid,
                        "actor_id": actor_id,
                        "action": "HUMAN_TASK_CREATED",
                        "resource_type": "human_task",
                        "resource_id": str(row["human_task_id"]),
                        "reason": "",
                        "source": json.dumps({"namespace": task.namespace}),
                        "evidence": json.dumps(
                            {
                                "executionId": str(task.execution_id),
                                "taskRunId": str(task.task_run_id),
                                "deadlineAt": (
                                    task.deadline_at.isoformat()
                                    if task.deadline_at is not None
                                    else None
                                ),
                            }
                        ),
                    },
                )
            return await _task_from_row(connection, row, tenant_uuid)

    async def list_tasks(
        self,
        actor_id: UUID,
        *,
        tenant_id: str,
        namespace: str | None = None,
        include_closed: bool = False,
        include_all: bool = False,
    ) -> Sequence[HumanTask]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                await connection.execute(
                    _LIST_TASKS,
                    {
                        "tenant_uuid": tenant_uuid,
                        "actor_id": actor_id,
                        "namespace": namespace,
                        "include_closed": include_closed,
                        "include_all": include_all,
                    },
                )
            ).mappings()
            return tuple([await _task_from_row(connection, row, tenant_uuid) for row in rows])

    async def get_task(
        self,
        human_task_id: UUID,
        actor_id: UUID,
        *,
        tenant_id: str,
        include_all: bool = False,
    ) -> HumanTask:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_TASK,
                        {
                            "tenant_uuid": tenant_uuid,
                            "human_task_id": human_task_id,
                            "actor_id": actor_id,
                            "include_all": include_all,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("human task does not exist or is not assigned to this actor")
            return await _task_from_row(connection, row, tenant_uuid)

    async def apply_action(
        self,
        human_task_id: UUID,
        request: HumanTaskActionRequest,
        *,
        tenant_id: str,
        actor_id: UUID,
    ) -> HumanTask:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _LOCK_TASK,
                        {"tenant_uuid": tenant_uuid, "human_task_id": human_task_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("human task does not exist")
            prior = await connection.scalar(
                _GET_ACTION_BY_KEY,
                {
                    "tenant_uuid": tenant_uuid,
                    "human_task_id": human_task_id,
                    "idempotency_key": request.idempotency_key,
                },
            )
            if prior is not None:
                if str(prior) != request.action.value:
                    raise HumanTaskConflict("idempotency key was used for a different action")
                return await _task_from_row(connection, row, tenant_uuid)
            is_open = row["state"] in {HumanTaskState.OPEN.value, HumanTaskState.ESCALATED.value}
            if not is_open and request.action not in {
                HumanTaskActionKind.COMMENT,
                HumanTaskActionKind.ATTACH,
            }:
                raise HumanTaskConflict("human task already has a terminal decision")
            action_values = {
                "action_id": new_runtime_id(),
                "tenant_uuid": tenant_uuid,
                "human_task_id": human_task_id,
                "idempotency_key": request.idempotency_key,
                "action": request.action.value,
                "actor_id": actor_id,
                "reason": request.reason,
                "form_values": json.dumps(request.form_values, separators=(",", ":")),
                "comment": request.comment,
                "artifact_uri": request.artifact_uri,
                "assignee_ids": list(request.assignee_ids),
                "group_ids": list(request.group_ids),
            }
            await connection.execute(_INSERT_ACTION, action_values)
            if request.action.terminal:
                updated = (
                    (
                        await connection.execute(
                            _TERMINAL_DECISION,
                            {
                                **action_values,
                                "state": terminal_state(request.action).value,
                            },
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if updated is None:
                    raise HumanTaskConflict("human task already has a terminal decision")
                row = updated
                await self._notify(
                    connection,
                    tenant_uuid,
                    row,
                    kind="DECIDED",
                    message=f"Approval completed with decision {request.action.value}.",
                )
            elif request.action is HumanTaskActionKind.DELEGATE:
                updated = (
                    (
                        await connection.execute(
                            _DELEGATE_TASK,
                            {
                                **action_values,
                                "assignee_ids": list(request.assignee_ids),
                                "group_ids": list(request.group_ids),
                            },
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if updated is None:
                    raise HumanTaskConflict("only an open human task can be delegated")
                row = updated
                await self._notify(
                    connection,
                    tenant_uuid,
                    row,
                    kind="DELEGATED",
                    message="A human approval was delegated to you.",
                )
            await connection.execute(
                _INSERT_AUDIT,
                {
                    "event_id": new_runtime_id(),
                    "tenant_uuid": tenant_uuid,
                    "actor_id": str(actor_id),
                    "action": f"HUMAN_TASK_{request.action.value}",
                    "resource_type": "human_task",
                    "resource_id": str(human_task_id),
                    "reason": request.reason,
                    "source": json.dumps({"namespace": row["namespace_name"]}),
                    "evidence": json.dumps(
                        {
                            "decision": request.action.value,
                            "formValues": request.form_values,
                            "comment": request.comment,
                            "artifactUri": request.artifact_uri,
                        },
                        separators=(",", ":"),
                    ),
                },
            )
            return await _task_from_row(connection, row, tenant_uuid)

    async def escalate_due(self, *, tenant_id: str) -> int:
        escalated = 0
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (await connection.execute(_DUE_TASKS, {"tenant_uuid": tenant_uuid})).mappings()
            for due in rows:
                row = (
                    (
                        await connection.execute(
                            _ESCALATE_TASK,
                            {"tenant_uuid": tenant_uuid, "human_task_id": due["human_task_id"]},
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    continue
                await connection.execute(
                    _INSERT_ACTION,
                    {
                        "action_id": new_runtime_id(),
                        "tenant_uuid": tenant_uuid,
                        "human_task_id": row["human_task_id"],
                        "idempotency_key": f"deadline:{row['deadline_at'].isoformat()}",
                        "action": HumanTaskActionKind.ESCALATE.value,
                        "actor_id": None,
                        "reason": "approval deadline reached",
                        "form_values": "{}",
                        "comment": "",
                        "artifact_uri": None,
                        "assignee_ids": list(row["assignee_ids"]),
                        "group_ids": list(row["group_ids"]),
                    },
                )
                await self._notify(
                    connection,
                    tenant_uuid,
                    row,
                    kind="ESCALATED",
                    message="A human approval reached its deadline and was escalated.",
                )
                escalated += 1
        return escalated

    async def list_pending_resume(self, *, tenant_id: str, limit: int = 100) -> Sequence[HumanTask]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                await connection.execute(
                    _LIST_PENDING_RESUME,
                    {"tenant_uuid": tenant_uuid, "limit": limit},
                )
            ).mappings()
            return tuple([await _task_from_row(connection, row, tenant_uuid) for row in rows])

    async def mark_resumed(self, human_task_id: UUID, *, tenant_id: str) -> None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                _MARK_RESUMED,
                {"tenant_uuid": tenant_uuid, "human_task_id": human_task_id},
            )

    async def list_notifications(
        self,
        actor_id: UUID,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> Sequence[HumanTaskNotification]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                await connection.execute(
                    _LIST_NOTIFICATIONS,
                    {"tenant_uuid": tenant_uuid, "actor_id": actor_id, "limit": limit},
                )
            ).mappings()
            return tuple(
                HumanTaskNotification(
                    notificationId=row["notification_id"],
                    humanTaskId=row["human_task_id"],
                    kind=row["kind"],
                    title=row["title"],
                    message=row["message"],
                    deadlineAt=row["deadline_at"],
                    createdAt=row["created_at"],
                    readAt=row["read_at"],
                )
                for row in rows
            )

    async def _notify(
        self,
        connection: AsyncConnection,
        tenant_uuid: UUID,
        row: RowMapping,
        *,
        kind: str,
        message: str,
    ) -> None:
        for recipient_type, recipients in (
            ("USER", row["assignee_ids"]),
            ("GROUP", row["group_ids"]),
        ):
            for recipient_id in recipients:
                await connection.execute(
                    _INSERT_NOTIFICATION,
                    {
                        "notification_id": new_runtime_id(),
                        "tenant_uuid": tenant_uuid,
                        "human_task_id": row["human_task_id"],
                        "recipient_id": recipient_id,
                        "recipient_type": recipient_type,
                        "kind": kind,
                        "title": row["title"],
                        "message": message,
                        "deadline_at": row["deadline_at"],
                    },
                )
