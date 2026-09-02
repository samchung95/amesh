"""Shared executor-factory wiring for API and recovery composition roots."""

from __future__ import annotations

from collections.abc import Callable, MutableMapping

from amesh.domain.scripts import SCRIPT_TASK_TYPES
from amesh.executor import InProcessExecutor, TaskHandler
from amesh.executor.contracts import TaskContextProvider
from amesh.executor.service import DispatchPolicyEnforcer
from amesh.ports import ExecutionRepository, ObjectStore, TaskCacheRepository
from amesh.workflow.working_directory import WorkingDirectoryManager

RECOVER_RUNNING_TYPES = frozenset(
    {"core.shell", "agent.session", "core.subflow", *SCRIPT_TASK_TYPES}
)
LAUNCH_RECOVER_RUNNING_TYPES = frozenset({"core.subflow", "agent.session"})


ContextProviderFactory = Callable[[ObjectStore | None], TaskContextProvider | None]
ExecutorFactory = Callable[[], InProcessExecutor]
ExecutorConstructor = Callable[..., InProcessExecutor]


def build_executor_factory(
    repository: ExecutionRepository,
    handlers: MutableMapping[str, TaskHandler],
    *,
    context_provider: TaskContextProvider | None = None,
    context_provider_factory: ContextProviderFactory | None = None,
    object_store: ObjectStore | None = None,
    task_cache: TaskCacheRepository | None = None,
    workspace_manager: WorkingDirectoryManager | None = None,
    dispatch_policy_enforcer: DispatchPolicyEnforcer | None = None,
    recover_running_types: frozenset[str] = RECOVER_RUNNING_TYPES,
    admission_poll_initial_seconds: float = 0.05,
    admission_poll_max_seconds: float = 1.0,
    executor_constructor: ExecutorConstructor = InProcessExecutor,
) -> ExecutorFactory:
    """Return a factory that creates executors over the supplied mutable registry.

    ``context_provider_factory`` is useful for recovery, where the object store is
    composed per execution.  All other collaborators are intentionally captured as
    explicit values so tests can provide lightweight doubles.
    """

    if context_provider is not None and context_provider_factory is not None:
        raise ValueError("provide context_provider or context_provider_factory, not both")

    def create_executor() -> InProcessExecutor:
        active_context_provider = (
            context_provider_factory(object_store)
            if context_provider_factory is not None
            else context_provider
        )
        return executor_constructor(
            repository,
            handlers=handlers,
            recover_running_types=recover_running_types,
            context_provider=active_context_provider,
            object_store=object_store,
            task_cache=task_cache,
            workspace_manager=workspace_manager,
            dispatch_policy_enforcer=dispatch_policy_enforcer,
            admission_poll_initial_seconds=admission_poll_initial_seconds,
            admission_poll_max_seconds=admission_poll_max_seconds,
        )

    return create_executor


__all__ = [
    "LAUNCH_RECOVER_RUNNING_TYPES",
    "RECOVER_RUNNING_TYPES",
    "build_executor_factory",
]
