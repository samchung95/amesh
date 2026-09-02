from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from amesh.domain.human_tasks import (
    AppForm,
    HumanTask,
    HumanTaskActionRequest,
    HumanTaskCreate,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskDeferral, TaskExecutionContext, TaskHandler
from amesh.ports import ExecutionRepository, HumanTaskRepository


def approval_resume_token(
    token_pepper: str,
    tenant_id: str,
    task_run_id: UUID,
    attempt: int,
) -> str:
    payload = f"human-task:{tenant_id}:{task_run_id}:{attempt}".encode()
    digest = hmac.new(token_pepper.encode(), payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def approval_task_handler(
    repository: HumanTaskRepository,
    execution_repository: ExecutionRepository,
    *,
    token_pepper: str,
) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskDeferral:
        execution = await execution_repository.get_execution(
            context.execution_id,
            tenant_id=context.tenant_id,
        )
        extra = task.model_extra or {}
        deadline_at = extra.get("deadlineAt")
        deadline_seconds = extra.get("deadlineSeconds")
        if deadline_at is not None and deadline_seconds is not None:
            raise ValueError("human approval accepts deadlineAt or deadlineSeconds, not both")
        if deadline_seconds is not None:
            if (
                not isinstance(deadline_seconds, (int, float))
                or isinstance(deadline_seconds, bool)
                or deadline_seconds <= 0
                or deadline_seconds > 31_536_000
            ):
                raise ValueError("human approval deadlineSeconds must be between 0 and 31536000")
            deadline_at = datetime.now(UTC) + timedelta(seconds=float(deadline_seconds))
        form_payload = extra.get("form", {})
        human_task = await repository.ensure_task(
            HumanTaskCreate(
                namespace=execution.namespace,
                executionId=context.execution_id,
                taskRunId=context.task_run_id,
                attempt=context.attempt,
                title=extra.get("title", task.id),
                description=extra.get("description", ""),
                form=AppForm.model_validate(form_payload),
                assigneeIds=tuple(extra.get("assigneeIds", ())),
                groupIds=tuple(extra.get("groupIds", ())),
                deadlineAt=deadline_at,
                escalationAssigneeIds=tuple(extra.get("escalationAssigneeIds", ())),
                escalationGroupIds=tuple(extra.get("escalationGroupIds", ())),
            ),
            tenant_id=context.tenant_id,
        )
        return TaskDeferral(
            resumeToken=approval_resume_token(
                token_pepper,
                context.tenant_id,
                context.task_run_id,
                context.attempt,
            ),
            metadata={
                "type": "human-approval",
                "humanTaskId": str(human_task.human_task_id),
                "deadlineAt": (
                    human_task.deadline_at.isoformat()
                    if human_task.deadline_at is not None
                    else None
                ),
            },
        )

    return run


class HumanTaskService:
    def __init__(
        self,
        repository: HumanTaskRepository,
        execution_repository: ExecutionRepository,
        *,
        token_pepper: str,
    ) -> None:
        self._repository = repository
        self._execution_repository = execution_repository
        self._token_pepper = token_pepper

    async def apply_action(
        self,
        human_task_id: UUID,
        request: HumanTaskActionRequest,
        *,
        tenant_id: str,
        actor_id: UUID,
    ) -> HumanTask:
        task = await self._repository.apply_action(
            human_task_id,
            request,
            tenant_id=tenant_id,
            actor_id=actor_id,
        )
        if request.action.terminal:
            await self._resume(task, tenant_id=tenant_id)
            task = await self._repository.get_task(
                task.human_task_id,
                actor_id,
                tenant_id=tenant_id,
                include_all=True,
            )
        return task

    async def reconcile(self, *, tenant_id: str, limit: int = 100) -> int:
        await self._repository.escalate_due(tenant_id=tenant_id)
        resumed = 0
        for task in await self._repository.list_pending_resume(
            tenant_id=tenant_id,
            limit=limit,
        ):
            await self._resume(task, tenant_id=tenant_id)
            resumed += 1
        return resumed

    async def _resume(self, task: HumanTask, *, tenant_id: str) -> None:
        if task.state.value in {"OPEN", "ESCALATED"}:
            return
        result: dict[str, Any] = {
            "taskType": "core.approval",
            "executionId": str(task.execution_id),
            "taskRunId": str(task.task_run_id),
            "attempt": task.attempt,
            "humanTaskId": str(task.human_task_id),
            "decision": task.state.value,
            "reason": task.reason,
            "formValues": task.form_values,
            "decidedBy": str(task.decided_by) if task.decided_by is not None else None,
            "decidedAt": task.decided_at.isoformat() if task.decided_at is not None else None,
        }
        await self._execution_repository.resume_deferred_task(
            task.task_run_id,
            approval_resume_token(
                self._token_pepper,
                tenant_id,
                task.task_run_id,
                task.attempt,
            ),
            result,
            tenant_id=tenant_id,
            evidence={
                "humanTask": {
                    "humanTaskId": str(task.human_task_id),
                    "decision": task.state.value,
                    "actorId": str(task.decided_by) if task.decided_by is not None else None,
                    "decidedAt": task.decided_at.isoformat()
                    if task.decided_at is not None
                    else None,
                    "reason": task.reason,
                    "formValues": task.form_values,
                }
            },
        )
        await self._repository.mark_resumed(task.human_task_id, tenant_id=tenant_id)
