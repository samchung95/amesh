"""Shared runner selection and lifecycle composition."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable, Iterable, Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Protocol

from amesh.adapters.docker import DockerContainerRunner
from amesh.adapters.kubernetes import ProfiledKubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.domain.runner import RunnerId, RunnerPolicy, RunnerPolicySet
from amesh.dsl.models import TaskDefinition
from amesh.executor import (
    TaskHandler,
    docker_container_handler,
    kubernetes_job_handler,
    local_process_handler,
    required_runner_ids,
    selecting_runner_handler,
)
from amesh.ports import DockerImagePolicy, KubernetesRunnerProfile, TaskRunner
from amesh.workflow.working_directory import WorkingDirectoryManager


class RunnerSettings(Protocol):
    """Settings subset used to select and construct task runners."""

    @property
    def runner_policies(self) -> tuple[RunnerPolicy, ...]: ...

    @property
    def execution_runner_mode(self) -> str: ...

    @property
    def is_local_process_runner_enabled(self) -> bool: ...

    @property
    def docker_runner_enabled(self) -> bool: ...

    @property
    def docker_runner_endpoint(self) -> str | None: ...

    @property
    def docker_image_policy(self) -> DockerImagePolicy: ...

    @property
    def docker_signature_verification_command(self) -> tuple[str, ...]: ...

    @property
    def docker_vulnerability_verification_command(self) -> tuple[str, ...]: ...

    @property
    def effective_kubernetes_runner_profiles(self) -> tuple[KubernetesRunnerProfile, ...]: ...

    @property
    def kubernetes_api_retry_attempts(self) -> int: ...

    @property
    def kubernetes_api_retry_max_seconds(self) -> float: ...


RunnerConstructor = Callable[[RunnerSettings], TaskRunner]
HandlerConstructor = Callable[[TaskRunner, WorkingDirectoryManager, str], TaskHandler]
SelectorConstructor = Callable[
    [Mapping[RunnerId, TaskHandler], RunnerPolicySet, str, RunnerId], TaskHandler
]
RunnerSelector = Callable[..., frozenset[RunnerId]]


def _default_docker_runner(settings: RunnerSettings) -> TaskRunner:
    return DockerContainerRunner(
        endpoint=settings.docker_runner_endpoint,
        image_policy=settings.docker_image_policy,
        signature_command=settings.docker_signature_verification_command,
        vulnerability_command=settings.docker_vulnerability_verification_command,
    )


def _default_kubernetes_runner(settings: RunnerSettings) -> TaskRunner:
    return ProfiledKubernetesJobRunner(
        settings.effective_kubernetes_runner_profiles,
        transient_retry_attempts=settings.kubernetes_api_retry_attempts,
        transient_retry_max_seconds=settings.kubernetes_api_retry_max_seconds,
    )


def _default_local_handler(
    runner: TaskRunner,
    workspace_manager: WorkingDirectoryManager,
    namespace: str,
) -> TaskHandler:
    return local_process_handler(runner, workspace_manager, namespace=namespace)


def _default_docker_handler(
    runner: TaskRunner,
    workspace_manager: WorkingDirectoryManager,
    namespace: str,
) -> TaskHandler:
    return docker_container_handler(runner, workspace_manager, namespace=namespace)


def _default_kubernetes_handler(
    runner: TaskRunner,
    workspace_manager: WorkingDirectoryManager,
    namespace: str,
) -> TaskHandler:
    return kubernetes_job_handler(runner, workspace_manager, namespace=namespace)


def _default_selector(
    handlers: Mapping[RunnerId, TaskHandler],
    policy: RunnerPolicySet,
    namespace: str,
    fallback: RunnerId,
) -> TaskHandler:
    return selecting_runner_handler(
        handlers,
        policy,
        namespace=namespace,
        fallback=fallback,
    )


@dataclass(frozen=True)
class RunnerFactories:
    """Injectable runner constructors for production roots and focused tests."""

    local_runner: Callable[[], TaskRunner] = LocalProcessRunner
    docker_runner: RunnerConstructor = _default_docker_runner
    kubernetes_runner: RunnerConstructor = _default_kubernetes_runner
    local_handler: HandlerConstructor = _default_local_handler
    docker_handler: HandlerConstructor = _default_docker_handler
    kubernetes_handler: HandlerConstructor = _default_kubernetes_handler
    selector: SelectorConstructor = _default_selector


@dataclass(frozen=True)
class RunnerSelection:
    """Pure runner-selection result shared by admission and runtime wiring."""

    selected: frozenset[RunnerId]
    policy: RunnerPolicySet
    fallback: RunnerId


@dataclass
class RunnerBundle:
    """Selected runner handlers and the external clients that need closing."""

    handlers: dict[RunnerId, TaskHandler]
    policy: RunnerPolicySet
    fallback: RunnerId
    shell_handler: TaskHandler
    docker_runner: TaskRunner | None = None
    kubernetes_runner: TaskRunner | None = None
    _closed: bool = field(default=False, init=False, repr=False)

    async def close(self) -> None:
        """Close owned external clients once, awaiting async doubles when supplied."""

        if self._closed:
            return
        self._closed = True
        failures: list[Exception] = []
        if self.docker_runner is not None:
            try:
                await _close_runner(self.docker_runner, in_thread=True)
            except Exception as exc:
                failures.append(exc)
        if self.kubernetes_runner is not None:
            try:
                await _close_runner(self.kubernetes_runner, in_thread=False)
            except Exception as exc:
                failures.append(exc)
        if len(failures) == 1:
            raise failures[0]
        if failures:
            raise ExceptionGroup("runner bundle close failed", failures)

    async def __aenter__(self) -> RunnerBundle:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()


async def _close_runner(runner: TaskRunner, *, in_thread: bool) -> None:
    close = getattr(runner, "close", None)
    if close is None:
        return
    result = await asyncio.to_thread(close) if in_thread else close()
    if inspect.isawaitable(result):
        await result


async def build_runner_bundle(
    settings: RunnerSettings,
    tasks: Iterable[TaskDefinition],
    workspace_manager: WorkingDirectoryManager,
    *,
    namespace: str,
    fallback: RunnerId | None = None,
    selection: RunnerSelection | None = None,
    factories: RunnerFactories | None = None,
) -> RunnerBundle:
    """Select required runners and build their handlers from injected factories."""

    active_factories = factories or RunnerFactories()
    active_selection = selection or select_runner_ids(
        settings,
        tasks,
        namespace=namespace,
        fallback=fallback,
    )
    policy = active_selection.policy
    fallback_runner = active_selection.fallback
    selected = active_selection.selected
    handlers: dict[RunnerId, TaskHandler] = {}
    docker_runner: TaskRunner | None = None
    kubernetes_runner: TaskRunner | None = None
    try:
        if RunnerId.LOCAL in selected:
            handlers[RunnerId.LOCAL] = active_factories.local_handler(
                active_factories.local_runner(), workspace_manager, namespace
            )
        if RunnerId.DOCKER in selected:
            docker_runner = active_factories.docker_runner(settings)
            handlers[RunnerId.DOCKER] = active_factories.docker_handler(
                docker_runner, workspace_manager, namespace
            )
        if RunnerId.KUBERNETES in selected:
            kubernetes_runner = active_factories.kubernetes_runner(settings)
            handlers[RunnerId.KUBERNETES] = active_factories.kubernetes_handler(
                kubernetes_runner, workspace_manager, namespace
            )
        shell_handler = active_factories.selector(handlers, policy, namespace, fallback_runner)
    except BaseException:
        if docker_runner is not None:
            with suppress(Exception):
                await _close_runner(docker_runner, in_thread=True)
        if kubernetes_runner is not None:
            with suppress(Exception):
                await _close_runner(kubernetes_runner, in_thread=False)
        raise
    return RunnerBundle(
        handlers=handlers,
        policy=policy,
        fallback=fallback_runner,
        shell_handler=shell_handler,
        docker_runner=docker_runner,
        kubernetes_runner=kubernetes_runner,
    )


def select_runner_ids(
    settings: RunnerSettings,
    tasks: Iterable[TaskDefinition],
    *,
    namespace: str,
    fallback: RunnerId | None = None,
    runner_selector: RunnerSelector = required_runner_ids,
) -> RunnerSelection:
    """Resolve runner policy without constructing external runner clients."""

    policy = RunnerPolicySet(settings.runner_policies)
    fallback_runner = fallback or RunnerId(settings.execution_runner_mode)
    available = {RunnerId.KUBERNETES}
    if settings.is_local_process_runner_enabled:
        available.add(RunnerId.LOCAL)
    if settings.docker_runner_enabled:
        available.add(RunnerId.DOCKER)
    selected = runner_selector(
        tuple(tasks),
        policy,
        namespace=namespace,
        fallback=fallback_runner,
        available=frozenset(available),
    )
    return RunnerSelection(
        selected=selected,
        policy=policy,
        fallback=fallback_runner,
    )


__all__ = [
    "RunnerBundle",
    "RunnerFactories",
    "RunnerSelection",
    "RunnerSettings",
    "build_runner_bundle",
    "select_runner_ids",
]
