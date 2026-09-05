from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest

from amesh.application.handlers import (
    HandlerComposition,
    HandlerFactories,
    PluginHandlerRuntime,
    RuntimeCompositionError,
    build_handler_registry,
)
from amesh.dsl import (
    FLOWABLE_TASK_TYPES,
    HandlerConfigurationContract,
    ResourceKind,
    TaskDefinition,
    TaskRuntimeOwnership,
)
from amesh.dsl.specifications import agent_task_specifications, core_task_specifications
from amesh.executor import (
    TaskConfigurationError,
    TaskExecutionContext,
    TaskHandler,
)
from amesh.executor.contracts import TaskHandlerBinding
from amesh.executor.subflows import SUBFLOW_TASK_TYPE
from amesh.executor.task_handlers import CORE_EXECUTOR_TASK_TYPES
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


def test_every_builtin_task_specification_has_one_runtime_owner() -> None:
    handlers = build_handler_registry(
        _composition(
            agent_resources=cast(Any, object()),
            agent_sessions=cast(Any, object()),
            agent_session_harness=cast(Any, object()),
            human_task_repository=object(),
            execution_repository=cast(Any, object()),
            token_pepper="pepper",
        )
    )
    specifications = (*core_task_specifications(), *agent_task_specifications())
    specification_types = {
        specification.type
        for specification in specifications
        if specification.kind is ResourceKind.TASK
    }
    declared_handler_owned = {
        specification.type
        for specification in specifications
        if specification.runtime_ownership is TaskRuntimeOwnership.HANDLER
    }
    declared_flowables = {
        specification.type
        for specification in specifications
        if specification.runtime_ownership is TaskRuntimeOwnership.FLOWABLE
    }
    declared_executor_owned = {
        specification.type
        for specification in specifications
        if specification.runtime_ownership is TaskRuntimeOwnership.EXECUTOR
    }

    assert len(handlers) == 37
    assert set(handlers) == declared_handler_owned
    assert declared_flowables == FLOWABLE_TASK_TYPES
    assert declared_executor_owned == {*CORE_EXECUTOR_TASK_TYPES, SUBFLOW_TASK_TYPE}
    assert not declared_handler_owned.intersection(declared_flowables, declared_executor_owned)
    assert not declared_flowables.intersection(declared_executor_owned)
    assert (
        declared_handler_owned | declared_flowables | declared_executor_owned == specification_types
    )
    for specification in specifications:
        if specification.runtime_ownership is not TaskRuntimeOwnership.HANDLER:
            continue
        binding = handlers[specification.type]
        assert isinstance(binding, TaskHandlerBinding)
        assert binding.configuration_contract is not specification.configuration_contract
        assert binding.configuration_contract.model_json_schema() == (
            specification.configuration_schema
        )


def test_handler_binding_rejects_configuration_before_calling_handler() -> None:
    called = False

    async def handler(*_: object) -> dict[str, bool]:
        nonlocal called
        called = True
        return {"ok": True}

    binding = TaskHandlerBinding(
        task_type="core.return",
        handler=handler,
        configuration_contract=HandlerConfigurationContract(
            {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
                "additionalProperties": False,
            }
        ),
    )

    with pytest.raises(TaskConfigurationError, match="handler contract"):
        asyncio.run(
            binding(
                TaskDefinition.model_validate(
                    {
                        "id": "invalid",
                        "type": "core.return",
                        "value": None,
                    }
                ),
                cast(TaskExecutionContext, object()),
            )
        )
    assert not called


def test_model_handler_bindings_accept_only_public_runtime_controls() -> None:
    handlers = build_handler_registry(_composition(), factories=_factories())
    invocation_id = "11111111-1111-4111-8111-111111111111"
    common = {
        "provider": {
            "adapter": "openai-compatible",
            "endpoint": "https://models.example.test/v1/chat/completions",
            "credentialRef": "models",
        },
        "model": "example/chat",
        "ceilingMode": "PROVIDER_BOUNDED",
        "dataHandling": {
            "egress": "REDACT_SECRETS",
            "promptRetention": "REDACTED",
        },
        "timeoutMode": "DISABLED",
        "continuationFromInvocationId": invocation_id,
        "continuationSources": [
            {"messageIndex": 0, "invocationId": invocation_id},
        ],
    }
    completion_limited = {**common, "maxCompletionTokens": 16}
    configurations = {
        "agent.llm": {**completion_limited, "prompt": "Reply ready."},
        "agent.chat": {**completion_limited, "prompt": "Reply ready."},
        "agent.embedding": {**common, "input": "Embed this."},
        "agent.structured": {
            **completion_limited,
            "prompt": "Reply ready.",
            "outputSchema": {"type": "object"},
        },
        "agent.toolCall": {
            **completion_limited,
            "prompt": "Reply ready.",
            "tools": [{"name": "echo", "inputSchema": {"type": "object"}}],
        },
    }

    for index, (task_type, configuration) in enumerate(configurations.items(), start=1):
        task = TaskDefinition.model_validate(
            {"id": f"model-{index}", "type": task_type, **configuration}
        )
        assert asyncio.run(handlers[task_type](task, cast(TaskExecutionContext, object()))) == {
            "ok": True
        }

        rejected = TaskDefinition.model_validate(
            {
                "id": f"model-{index}-internal",
                "type": task_type,
                **configuration,
                "progressContext": {"not": "public"},
            }
        )
        with pytest.raises(TaskConfigurationError, match="handler contract"):
            asyncio.run(handlers[task_type](rejected, cast(TaskExecutionContext, object())))

        if task_type == "agent.embedding":
            continue
        conflicting = TaskDefinition.model_validate(
            {
                "id": f"model-{index}-conflicting-limits",
                "type": task_type,
                **configuration,
                "budget": {
                    "maxTotalTokens": 32,
                    "maxCompletionTokens": 16,
                    "maxCostUsd": "0.01",
                },
            }
        )
        with pytest.raises(TaskConfigurationError, match="budget and maxCompletionTokens"):
            asyncio.run(handlers[task_type](conflicting, cast(TaskExecutionContext, object())))


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
