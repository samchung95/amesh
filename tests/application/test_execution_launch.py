from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

import pytest

from amesh.application import ExecutionLaunchService
from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.ports import ExecutionLaunchSource, PersistedExecution


def _execution(state: ExecutionState) -> PersistedExecution:
    now = datetime.now(UTC)
    return PersistedExecution(
        execution_id=uuid4(),
        tenant_id="tenant-a",
        state=state,
        epoch=1,
        version=0,
        namespace="tests",
        flow_id="launch",
        created_at=now,
        updated_at=now,
    )


class _Repository:
    def __init__(self) -> None:
        self.current = _execution(ExecutionState.RUNNING)
        self.created: dict[str, object] | None = None

    async def create_execution(self, flow: FlowDefinition, **kwargs: object) -> PersistedExecution:
        self.created = {"flow": flow, **kwargs}
        return self.current

    @asynccontextmanager
    async def execution_guard(self, tenant_id: str, execution_id: UUID) -> AsyncIterator[bool]:
        assert tenant_id == "tenant-a"
        assert execution_id == self.current.execution_id
        yield True

    async def get_execution(self, execution_id: UUID, *, tenant_id: str) -> PersistedExecution:
        assert execution_id == self.current.execution_id
        assert tenant_id == "tenant-a"
        return self.current

    async def list_task_runs(self, *_: object, **__: object) -> list[object]:
        return []

    async def list_subflows(self, *_: object, **__: object) -> list[object]:
        return []


class _Executor:
    def __init__(self, repository: _Repository) -> None:
        self.repository = repository
        self.calls = 0

    async def run_to_completion(self, *_: object, **__: object) -> object:
        self.calls += 1
        self.repository.current = self.repository.current.model_copy(
            update={"state": ExecutionState.SUCCESS}
        )
        return object()


@pytest.mark.parametrize("respond_async", [False, True])
def test_launch_service_owns_sync_and_detached_lifecycle(respond_async: bool) -> None:
    async def scenario() -> None:
        repository = _Repository()
        executor = _Executor(repository)
        scheduled: list[tuple[Callable[..., Any], tuple[object, ...]]] = []
        close_calls = 0

        def schedule(callback: Callable[..., Any], *args: object, **_: object) -> None:
            scheduled.append((callback, args))

        async def close() -> None:
            nonlocal close_calls
            close_calls += 1

        service = ExecutionLaunchService(
            cast(Any, repository),
            lambda: executor,
            schedule_background=schedule,
            close_runtime=close,
        )
        result = await service.launch(
            FlowDefinition(
                id="launch",
                namespace="tests",
                tasks=[TaskDefinition(id="task", type="core.log")],
            ),
            tenant_id="tenant-a",
            actor_id="user:test",
            inputs={"value": 1},
            trigger={"source": "test"},
            launch_source=ExecutionLaunchSource.API,
            idempotency_key="stable-key",
            respond_async=respond_async,
        )

        assert repository.created is not None
        assert repository.created["inputs"] == {"value": 1}
        assert close_calls == 0
        assert len(scheduled) == 1
        if respond_async:
            assert result.execution.state is ExecutionState.RUNNING
        else:
            assert result.execution.state is ExecutionState.SUCCESS

        callback, args = scheduled.pop()
        await callback(*args)
        assert executor.calls == 1
        assert close_calls == 1

    asyncio.run(scenario())
