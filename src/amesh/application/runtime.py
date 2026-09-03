"""Transactional construction of the shared execution runtime."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import Protocol

from amesh.application.executor import (
    RECOVER_RUNNING_TYPES,
    ExecutorConstructor,
    ExecutorFactory,
    build_executor_factory,
)
from amesh.application.handlers import (
    HandlerComposition,
    HandlerFactories,
    build_handler_registry,
)
from amesh.application.http_policy import HttpPolicySettings, build_http_task_policy
from amesh.application.runners import (
    RunnerBundle,
    RunnerFactories,
    RunnerSelection,
    RunnerSettings,
    build_runner_bundle,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import InProcessExecutor, TaskHandler, subflow_task_handler
from amesh.executor.contracts import DispatchPolicyEnforcer, TaskContextProvider
from amesh.ports import ExecutionRepository, ObjectStore, TaskCacheRepository
from amesh.tasks import HttpTaskPolicy
from amesh.workflow.working_directory import WorkingDirectoryManager

LOGGER = logging.getLogger("amesh.application.runtime")


class ExecutionRuntimeSettings(RunnerSettings, HttpPolicySettings, Protocol):
    @property
    def execution_admission_poll_initial_seconds(self) -> float: ...

    @property
    def execution_admission_poll_max_seconds(self) -> float: ...


HandlerCompositionFactory = Callable[
    [TaskHandler, HttpTaskPolicy],
    HandlerComposition,
]
SubflowAuthorizer = Callable[[FlowDefinition], Awaitable[None]]


@dataclass(frozen=True)
class ExecutionRuntime:
    """One fully composed executor and its owned external runner clients."""

    handlers: dict[str, TaskHandler]
    executor_factory: ExecutorFactory
    executor: InProcessExecutor
    runners: RunnerBundle

    async def close(self) -> None:
        await self.runners.close()


async def build_execution_runtime(
    settings: ExecutionRuntimeSettings,
    tasks: Iterable[TaskDefinition],
    workspace_manager: WorkingDirectoryManager,
    repository: ExecutionRepository,
    handler_composition_factory: HandlerCompositionFactory,
    authorize_subflow: SubflowAuthorizer,
    *,
    namespace: str,
    runner_selection: RunnerSelection,
    context_provider: TaskContextProvider | None = None,
    object_store: ObjectStore | None = None,
    task_cache: TaskCacheRepository | None = None,
    dispatch_policy_enforcer: DispatchPolicyEnforcer | None = None,
    recover_running_types: frozenset[str] = RECOVER_RUNNING_TYPES,
    runner_factories: RunnerFactories | None = None,
    handler_factories: HandlerFactories | None = None,
    executor_constructor: ExecutorConstructor = InProcessExecutor,
) -> ExecutionRuntime:
    """Compose a complete runtime and close every partial runner on failure."""

    runners = await build_runner_bundle(
        settings,
        tasks,
        workspace_manager,
        namespace=namespace,
        selection=runner_selection,
        factories=runner_factories,
    )
    try:
        handlers = build_handler_registry(
            handler_composition_factory(
                runners.shell_handler,
                build_http_task_policy(settings),
            ),
            factories=handler_factories,
        )
        executor_factory = build_executor_factory(
            repository,
            handlers,
            context_provider=context_provider,
            object_store=object_store,
            task_cache=task_cache,
            workspace_manager=workspace_manager,
            dispatch_policy_enforcer=dispatch_policy_enforcer,
            recover_running_types=recover_running_types,
            admission_poll_initial_seconds=settings.execution_admission_poll_initial_seconds,
            admission_poll_max_seconds=settings.execution_admission_poll_max_seconds,
            executor_constructor=executor_constructor,
        )
        handlers["core.subflow"] = subflow_task_handler(
            repository,
            executor_factory,
            authorize_subflow,
        )
        executor = executor_factory()
    except BaseException:
        try:
            await runners.close()
        except Exception:
            LOGGER.exception("runner cleanup failed after runtime composition error")
        raise
    return ExecutionRuntime(
        handlers=handlers,
        executor_factory=executor_factory,
        executor=executor,
        runners=runners,
    )


__all__ = [
    "ExecutionRuntime",
    "ExecutionRuntimeSettings",
    "HandlerCompositionFactory",
    "build_execution_runtime",
]
