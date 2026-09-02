from __future__ import annotations

from typing import Any, cast

import pytest

from amesh.application.handlers import (
    HandlerComposition,
    HandlerFactories,
    PluginHandlerRuntime,
    RuntimeCompositionError,
    build_handler_registry,
)
from amesh.executor import TaskHandler
from amesh.workflow.working_directory import WorkingDirectoryManager


async def _handler(*_: object) -> dict[str, bool]:
    return {"ok": True}


def _factories() -> HandlerFactories:
    def registry(*_: object, **__: object) -> dict[str, TaskHandler]:
        return {"core.injected": _handler}

    def mesh(*_: object, **__: object) -> dict[str, TaskHandler]:
        return {"agent.mesh.route": _handler}

    def one(*_: object, **__: object) -> TaskHandler:
        return _handler

    return HandlerFactories(
        model=one,
        mcp=one,
        mesh=mesh,
        session=one,
        approval=one,
        core=registry,
        scripts=registry,
    )


def _composition(**kwargs: Any) -> HandlerComposition:
    return HandlerComposition(
        workspace_manager=WorkingDirectoryManager(None),
        shell_handler=_handler,
        **kwargs,
    )


class PluginDouble:
    def __init__(self, handlers: dict[str, TaskHandler]) -> None:
        self.handlers = handlers

    def task_handlers(self, _: object) -> dict[str, TaskHandler]:
        return self.handlers


def test_handler_registry_composes_core_and_optional_agent_capabilities() -> None:
    handlers = build_handler_registry(
        _composition(
            agent_resources=cast(Any, object()),
            agent_sessions=cast(Any, object()),
            agent_session_harness=cast(Any, object()),
            human_task_repository=object(),
            execution_repository=cast(Any, object()),
            token_pepper="pepper",
        ),
        factories=_factories(),
    )

    assert {"core.shell", "core.injected", "agent.llm", "agent.mcp"} <= handlers.keys()
    assert {"agent.mesh.route", "agent.session", "core.approval"} <= handlers.keys()


def test_handler_registry_rejects_missing_plugin_handler() -> None:
    with pytest.raises(RuntimeCompositionError, match="missing required"):
        build_handler_registry(
            _composition(
                trusted_plugin_runtime=cast(PluginHandlerRuntime, PluginDouble({})),
                plugin_resolution={},
                required_plugin_types=("plugin.task",),
            ),
            factories=_factories(),
        )


def test_handler_registry_rejects_conflicting_plugin_handlers() -> None:
    with pytest.raises(RuntimeCompositionError, match="multiple runtime owners"):
        build_handler_registry(
            _composition(
                trusted_plugin_runtime=cast(
                    PluginHandlerRuntime,
                    PluginDouble({"plugin.task": _handler}),
                ),
                isolated_plugin_runtime=cast(
                    PluginHandlerRuntime,
                    PluginDouble({"plugin.task": _handler}),
                ),
                plugin_resolution={},
            ),
            factories=_factories(),
        )
