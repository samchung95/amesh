"""Shared task-handler registry composition for API and recovery roots."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol

from amesh.executor import TaskHandler
from amesh.human_tasks import approval_task_handler
from amesh.model_continuations import ModelContinuationProtector
from amesh.model_providers import ModelProviderCapabilities, ModelProviderRegistry
from amesh.plugin_sdk import PluginResolution
from amesh.ports import (
    AgentMemoryRepository,
    AgentPrimitiveRepository,
    AgentProgressSink,
    AgentResourceRepository,
    AgentSessionHarness,
    AgentSessionRepository,
    ExecutionRepository,
    ImageArtifactResolver,
)
from amesh.tasks import (
    HttpTaskPolicy,
    OpenAICompatibleConfig,
    ScriptTaskPolicy,
    agent_llm_handler,
    agent_mcp_handler,
    agent_mesh_handlers,
    agent_session_handler,
    core_utility_handlers,
    script_task_handlers,
)
from amesh.workflow.working_directory import WorkingDirectoryManager


class RuntimeCompositionError(RuntimeError):
    """Raised when composition cannot produce an unambiguous handler registry."""


class PluginHandlerRuntime(Protocol):
    """The synchronous handler surface shared by trusted and isolated runtimes."""

    def task_handlers(
        self,
        resolution: PluginResolution | Mapping[str, object],
    ) -> Mapping[str, TaskHandler]: ...


HandlerFactory = Callable[..., TaskHandler]
HandlerRegistryFactory = Callable[..., Mapping[str, TaskHandler]]


@dataclass(frozen=True)
class HandlerFactories:
    """Injectable handler constructors for production roots and unit tests."""

    model: HandlerFactory = agent_llm_handler
    mcp: HandlerFactory = agent_mcp_handler
    mesh: Callable[[AgentResourceRepository], Mapping[str, TaskHandler]] = agent_mesh_handlers
    session: HandlerFactory = agent_session_handler
    approval: HandlerFactory = approval_task_handler
    core: HandlerRegistryFactory = core_utility_handlers
    scripts: HandlerRegistryFactory = script_task_handlers


HandlerFactoryBundle = HandlerFactories


@dataclass(frozen=True)
class HandlerComposition:
    """Explicit collaborators used to build one core task-handler registry."""

    workspace_manager: WorkingDirectoryManager
    shell_handler: TaskHandler
    execution_repository: ExecutionRepository | None = None
    http_policy: HttpTaskPolicy | None = None
    model_configuration: OpenAICompatibleConfig | None = None
    agent_repository: AgentPrimitiveRepository | None = None
    agent_resources: AgentResourceRepository | None = None
    agent_sessions: AgentSessionRepository | None = None
    agent_memory: AgentMemoryRepository | None = None
    agent_progress_sink: AgentProgressSink | None = None
    image_resolver: ImageArtifactResolver | None = None
    model_engine_registry: ModelProviderRegistry | None = None
    model_capability_resolver: Callable[[str, str], ModelProviderCapabilities] | None = None
    continuation_protector: ModelContinuationProtector | None = None
    agent_session_harness: AgentSessionHarness | None = None
    human_task_repository: object | None = None
    token_pepper: str | None = None
    script_policy: ScriptTaskPolicy | None = None
    trusted_plugin_runtime: PluginHandlerRuntime | None = None
    isolated_plugin_runtime: PluginHandlerRuntime | None = None
    plugin_resolution: PluginResolution | Mapping[str, object] | None = None
    required_plugin_types: tuple[str, ...] = ()


def build_handler_registry(
    composition: HandlerComposition,
    *,
    factories: HandlerFactories | None = None,
) -> dict[str, TaskHandler]:
    """Build the common registry while preserving optional capability boundaries.

    Plugin runtimes must already be started/configured by the caller.  The runtime
    task-handler surface is deliberately synchronous so API and recovery roots can
    share this builder without sharing their lifecycle policies.
    """

    active = factories or HandlerFactories()
    model_handler = active.model(
        configuration=composition.model_configuration,
        http_policy=composition.http_policy,
        repository=composition.agent_repository,
        progress_sink=composition.agent_progress_sink,
        image_resolver=composition.image_resolver,
        provider_registry=composition.model_engine_registry,
        continuation_protector=composition.continuation_protector,
    )
    mcp_handler = active.mcp(
        repository=composition.agent_repository,
        http_policy=composition.http_policy,
    )
    handlers: dict[str, TaskHandler] = {
        "core.shell": composition.shell_handler,
        **{
            task_type: model_handler
            for task_type in (
                "agent.llm",
                "agent.chat",
                "agent.embedding",
                "agent.structured",
                "agent.toolCall",
            )
        },
        "agent.mcp": mcp_handler,
        **active.core(composition.workspace_manager, http_policy=composition.http_policy),
        **active.scripts(
            composition.shell_handler,
            composition.script_policy or ScriptTaskPolicy(),
        ),
    }
    if composition.agent_resources is not None:
        handlers.update(active.mesh(composition.agent_resources))
    if any(
        dependency is not None
        for dependency in (
            composition.agent_sessions,
            composition.agent_session_harness,
        )
    ):
        if (
            composition.agent_resources is None
            or composition.agent_sessions is None
            or composition.agent_session_harness is None
        ):
            raise RuntimeCompositionError(
                "agent.session composition requires resources, sessions and harness"
            )
        handlers["agent.session"] = active.session(
            resources=composition.agent_resources,
            sessions=composition.agent_sessions,
            model_handler=model_handler,
            mcp_handler=mcp_handler,
            harness=composition.agent_session_harness,
            memory=composition.agent_memory,
            progress_sink=composition.agent_progress_sink,
            **(
                {"model_capability_resolver": composition.model_capability_resolver}
                if composition.model_capability_resolver is not None
                else {}
            ),
        )
    if composition.human_task_repository is not None or composition.token_pepper is not None:
        if composition.human_task_repository is None or composition.execution_repository is None:
            raise RuntimeCompositionError(
                "core.approval composition requires human and execution repositories"
            )
        if composition.token_pepper is None:
            raise RuntimeCompositionError("core.approval composition requires token pepper")
        handlers["core.approval"] = active.approval(
            composition.human_task_repository,
            composition.execution_repository,
            token_pepper=composition.token_pepper,
        )
    handlers.update(_plugin_handlers(composition, handlers))
    return handlers


def _plugin_handlers(
    composition: HandlerComposition,
    core_handlers: Mapping[str, TaskHandler],
) -> dict[str, TaskHandler]:
    runtimes = (
        ("trusted", composition.trusted_plugin_runtime),
        ("isolated", composition.isolated_plugin_runtime),
    )
    if (
        not any(runtime is not None for _, runtime in runtimes)
        and not composition.required_plugin_types
    ):
        return {}
    if composition.plugin_resolution is None:
        raise RuntimeCompositionError("plugin handlers require a plugin resolution")
    combined: dict[str, TaskHandler] = {}
    for _label, runtime in runtimes:
        if runtime is None:
            continue
        for task_type, handler in runtime.task_handlers(composition.plugin_resolution).items():
            if task_type in combined:
                raise RuntimeCompositionError(
                    f"plugin task identity {task_type!r} has multiple runtime owners"
                )
            if task_type in core_handlers:
                raise RuntimeCompositionError(
                    f"plugin task identity {task_type!r} conflicts with a core task"
                )
            combined[task_type] = handler
    missing = sorted(set(composition.required_plugin_types).difference(combined))
    if missing:
        raise RuntimeCompositionError(
            "plugin handlers are missing required task identities: " + ", ".join(missing)
        )
    return combined


__all__ = [
    "HandlerComposition",
    "HandlerFactories",
    "HandlerFactoryBundle",
    "PluginHandlerRuntime",
    "RuntimeCompositionError",
    "build_handler_registry",
]
