"""Application service for durable execution launch and request detachment."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import Any, Protocol, cast
from uuid import UUID

from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition
from amesh.executor import InProcessExecutor, SubflowCoordinator
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionRepository,
    PersistedExecution,
    PersistedTaskRun,
    TenantQuotaExceeded,
)

LOGGER = logging.getLogger("amesh.application.execution_launch")


class ExecutionLaunchRepository(ExecutionRepository, Protocol):
    """Execution port extension required to fence in-process launch work."""

    def execution_guard(
        self,
        tenant_id: str,
        execution_id: UUID,
    ) -> AbstractAsyncContextManager[bool]: ...


class ExecutionDriver(Protocol):
    async def run_to_completion(
        self,
        flow: FlowDefinition,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> object: ...


class ExecutionLaunchConflict(RuntimeError):
    """The durable execution record could not be created as requested."""


@dataclass(frozen=True)
class ExecutionLaunchResult:
    """Durable records produced by one launch request."""

    execution: PersistedExecution
    task_runs: tuple[PersistedTaskRun, ...]


ExecutorFactory = Callable[[], ExecutionDriver]
BackgroundScheduler = Callable[..., Any]
RuntimeCloser = Callable[[], Awaitable[None]]


class ExecutionLaunchService:
    """Create and drive executions without depending on an HTTP framework."""

    def __init__(
        self,
        repository: ExecutionLaunchRepository,
        executor_factory: ExecutorFactory,
        *,
        schedule_background: BackgroundScheduler,
        close_runtime: RuntimeCloser,
    ) -> None:
        self._repository = repository
        self._executor_factory = executor_factory
        self._schedule_background = schedule_background
        self._close_runtime = close_runtime

    async def launch(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        actor_id: str,
        inputs: dict[str, Any],
        trigger: dict[str, Any] | None,
        launch_source: ExecutionLaunchSource,
        idempotency_key: str | None = None,
        respond_async: bool = False,
    ) -> ExecutionLaunchResult:
        """Persist, execute or detach, and return the latest durable records."""

        executor = self._executor_factory()
        background_scheduled = False
        try:
            try:
                execution = await self._repository.create_execution(
                    flow,
                    tenant_id=tenant_id,
                    inputs=inputs,
                    trigger=trigger,
                    launch_source=launch_source,
                    idempotency_key=idempotency_key,
                    actor_id=actor_id,
                )
            except (TenantQuotaExceeded, ValueError) as exc:
                raise ExecutionLaunchConflict(str(exc)) from exc
            if execution.state is ExecutionState.RUNNING and respond_async:
                self._schedule_background(
                    self._run_async_execution,
                    executor,
                    flow,
                    execution.execution_id,
                    tenant_id,
                )
                background_scheduled = True
            elif execution.state is ExecutionState.RUNNING:
                async with self._repository.execution_guard(
                    tenant_id,
                    execution.execution_id,
                ) as acquired:
                    if acquired:
                        await executor.run_to_completion(
                            flow,
                            execution.execution_id,
                            tenant_id=tenant_id,
                        )
            current = await self._repository.get_execution(
                execution.execution_id,
                tenant_id=tenant_id,
            )
            task_runs = tuple(
                await self._repository.list_task_runs(
                    execution.execution_id,
                    tenant_id=tenant_id,
                )
            )
            if current.state is ExecutionState.SUCCESS:
                self._schedule_background(
                    self._run_pending_subflows,
                    execution.execution_id,
                    tenant_id,
                )
                background_scheduled = True
            return ExecutionLaunchResult(execution=current, task_runs=task_runs)
        finally:
            if not background_scheduled:
                await self._close_runtime()

    async def _run_pending_subflows(self, execution_id: UUID, tenant_id: str) -> None:
        try:
            await SubflowCoordinator(
                self._repository,
                cast(Callable[[], InProcessExecutor], self._executor_factory),
            ).run_pending(execution_id, tenant_id=tenant_id)
        finally:
            await self._close_runtime()

    async def _run_async_execution(
        self,
        executor: ExecutionDriver,
        flow: FlowDefinition,
        execution_id: UUID,
        tenant_id: str,
    ) -> None:
        try:
            async with self._repository.execution_guard(tenant_id, execution_id) as acquired:
                if not acquired:
                    return
                await executor.run_to_completion(flow, execution_id, tenant_id=tenant_id)
            completed = await self._repository.get_execution(execution_id, tenant_id=tenant_id)
            if completed.state is ExecutionState.SUCCESS:
                await SubflowCoordinator(
                    self._repository,
                    cast(Callable[[], InProcessExecutor], self._executor_factory),
                ).run_pending(execution_id, tenant_id=tenant_id)
        except Exception:
            LOGGER.exception(
                "asynchronous execution failed",
                extra={"execution_id": str(execution_id), "tenant_id": tenant_id},
            )
        finally:
            await self._close_runtime()


__all__ = [
    "ExecutionDriver",
    "ExecutionLaunchConflict",
    "ExecutionLaunchRepository",
    "ExecutionLaunchResult",
    "ExecutionLaunchService",
]
