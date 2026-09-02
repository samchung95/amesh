from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from amesh.domain.human_tasks import (
    HumanTask,
    HumanTaskActionRequest,
    HumanTaskCreate,
    HumanTaskNotification,
    WorkflowApp,
    WorkflowAppSpec,
)


class HumanTaskRepository(Protocol):
    async def list_apps(
        self, *, tenant_id: str, namespace: str | None = None
    ) -> Sequence[WorkflowApp]: ...

    async def get_app(
        self,
        namespace: str,
        app_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> WorkflowApp: ...

    async def upsert_app(
        self,
        namespace: str,
        app_id: str,
        spec: WorkflowAppSpec,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None,
    ) -> WorkflowApp: ...

    async def ensure_task(
        self,
        task: HumanTaskCreate,
        *,
        tenant_id: str,
        actor_id: str = "system:executor",
    ) -> HumanTask: ...

    async def list_tasks(
        self,
        actor_id: UUID,
        *,
        tenant_id: str,
        namespace: str | None = None,
        include_closed: bool = False,
        include_all: bool = False,
    ) -> Sequence[HumanTask]: ...

    async def get_task(
        self,
        human_task_id: UUID,
        actor_id: UUID,
        *,
        tenant_id: str,
        include_all: bool = False,
    ) -> HumanTask: ...

    async def apply_action(
        self,
        human_task_id: UUID,
        request: HumanTaskActionRequest,
        *,
        tenant_id: str,
        actor_id: UUID,
    ) -> HumanTask: ...

    async def escalate_due(self, *, tenant_id: str) -> int: ...

    async def list_pending_resume(
        self, *, tenant_id: str, limit: int = 100
    ) -> Sequence[HumanTask]: ...

    async def mark_resumed(self, human_task_id: UUID, *, tenant_id: str) -> None: ...

    async def list_notifications(
        self, actor_id: UUID, *, tenant_id: str, limit: int = 100
    ) -> Sequence[HumanTaskNotification]: ...


__all__ = ["HumanTaskRepository"]
