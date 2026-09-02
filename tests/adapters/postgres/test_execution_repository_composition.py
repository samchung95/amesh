from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import cast, get_type_hints
from uuid import UUID, uuid4

from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.adapters.postgres import PostgresExecutionRepository as BarrelRepository
from amesh.adapters.postgres.execution_control_repository import _ExecutionControlMixin
from amesh.adapters.postgres.execution_repository import PostgresExecutionRepository
from amesh.domain import TaskRunEventType, TaskRunLifecyclePhase, TaskRunState
from amesh.ports.execution_repository import ExecutionRepository, split_execution_repository


def test_execution_repository_import_and_control_composition() -> None:
    assert BarrelRepository is PostgresExecutionRepository
    assert PostgresExecutionRepository.__module__ == (
        "amesh.adapters.postgres.execution_repository"
    )
    assert issubclass(PostgresExecutionRepository, _ExecutionControlMixin)
    assert get_type_hints(PostgresExecutionRepository.__init__)["engine"] is AsyncEngine
    assert all(
        hasattr(PostgresExecutionRepository, name)
        for name in (
            "apply_flow",
            "create_execution",
            "request_admission",
            "complete_execution",
            "start_task",
            "apply_execution_intervention",
            "list_subflows",
        )
    )
    ports = split_execution_repository(
        cast(ExecutionRepository, object.__new__(PostgresExecutionRepository))
    )
    assert ports.flow_registry is ports.admission
    assert ports.admission is ports.lifecycle
    assert ports.lifecycle is ports.task_runs
    assert ports.task_runs is ports.control


def test_execution_control_mixin_keeps_self_dispatch_for_task_events() -> None:
    class ProbeRepository(PostgresExecutionRepository):
        def __init__(self) -> None:
            super().__init__(cast(AsyncEngine, object()))
            self.events: list[TaskRunEventType] = []

        async def _update_task_control(
            self,
            connection: AsyncConnection,
            tenant_id: UUID,
            task: RowMapping,
            state: TaskRunState,
        ) -> RowMapping:
            return cast(
                RowMapping,
                {
                    "id": task["id"],
                    "execution_id": task["execution_id"],
                    "version": 2,
                },
            )

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
            self.events.append(event_type)

    async def scenario() -> None:
        repository = ProbeRepository()
        task_id = uuid4()
        await repository._request_task_cancellation(
            cast(AsyncConnection, object()),
            uuid4(),
            [
                cast(
                    RowMapping,
                    {
                        "id": task_id,
                        "execution_id": uuid4(),
                        "state": TaskRunState.WAITING.value,
                        "lifecycle_phase": TaskRunLifecyclePhase.MAIN.value,
                    },
                )
            ],
            actor_id="test",
            reason="test cancellation",
            correlation_id=uuid4(),
        )
        assert repository.events == [TaskRunEventType.CANCELLED]

    asyncio.run(scenario())
