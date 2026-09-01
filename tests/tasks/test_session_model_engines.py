from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest
from tests.tasks.test_agent_sessions import (
    MemoryResources,
    MemorySessions,
    RecordingHarness,
    ScriptedMcp,
    ScriptedModel,
    _context,
    _pin,
    _task,
)

from amesh.config import Settings
from amesh.domain import AgentCeilingMode, AgentPermissions, ModelProviderSpec
from amesh.dsl import TaskDefinition, TaskTimeoutMode
from amesh.executor import TaskCompletion
from amesh.model_engine_runtime import (
    MODEL_ENGINE_DEFAULT_MODEL,
    configured_model_capability_resolver,
    configured_model_engine_registry,
)
from amesh.tasks import agent_llm_handler, agent_session_handler

CODEX_FIXTURE = Path(__file__).parent.parent / "fixtures" / "codex_app_server_fixture.py"


def _engine_session_fixture() -> tuple[MemoryResources, ScriptedModel, TaskDefinition]:
    pin = _pin(model=MODEL_ENGINE_DEFAULT_MODEL)
    route = pin.envelope.model_routes[0]
    engine_route = route.model_copy(
        update={
            "provider": ModelProviderSpec(
                adapter="openai-codex-app-server",
                engineRef="personal-codex",
            )
        }
    )
    permissions = AgentPermissions(
        toolAllowlist=pin.envelope.permissions.tool_allowlist,
        secretScopes=("mcp-token",),
        engineScopes=("personal-codex",),
        networkHosts=("mcp.example.test",),
    )
    envelope = pin.envelope.model_copy(
        update={
            "model_routes": (engine_route,),
            "permissions": permissions,
        }
    )
    pin = pin.model_copy(update={"envelope": envelope, "envelope_digest": envelope.digest})
    model = ScriptedModel(
        [
            {
                "action": "final",
                "tool": "lookup",
                "arguments": None,
                "output": {"answer": "subscription engine"},
                "rationale": "Done",
            }
        ]
    )
    task = TaskDefinition.model_validate(
        {
            **_task().model_dump(mode="json", by_alias=True),
            "contract": {
                "secretScopes": ["mcp-token"],
                "engineScopes": ["personal-codex"],
            },
        }
    )
    return MemoryResources(pin), model, task


def test_session_delegates_engine_scope_without_fabricating_http_access() -> None:
    async def scenario() -> None:
        resources, model, task = _engine_session_fixture()
        handler = agent_session_handler(
            resources=resources,
            sessions=MemorySessions(),
            model_handler=model,
            mcp_handler=ScriptedMcp(),
            harness=RecordingHarness(),
        )

        completed = await handler(task, _context())

        assert isinstance(completed, TaskCompletion)
        generated = model.calls[0]
        assert generated.model_extra is not None
        assert generated.model_extra["provider"] == {
            "adapter": "openai-codex-app-server",
            "engineRef": "personal-codex",
        }
        assert generated.contract.engine_scopes == ("personal-codex",)
        assert generated.contract.secret_scopes == ()

    asyncio.run(scenario())


def test_provider_bounded_session_dispatches_through_configured_codex_engine(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        resources, _, task = _engine_session_fixture()
        pin = resources.pin
        limits = pin.envelope.hard_limits.model_copy(
            update={
                "ceiling_mode": AgentCeilingMode.PROVIDER_BOUNDED,
                "max_total_tokens": None,
                "max_cost_usd": None,
                "max_duration_seconds": None,
                "max_tool_calls": None,
                "max_turns": None,
                "max_loop_iterations": None,
            }
        )
        envelope = pin.envelope.model_copy(update={"hard_limits": limits})
        resources = MemoryResources(
            pin.model_copy(update={"envelope": envelope, "envelope_digest": envelope.digest})
        )
        task_payload = task.model_dump(mode="json", by_alias=True)
        task_payload.pop("timeoutSeconds", None)
        task_payload.update(
            {
                "timeoutMode": TaskTimeoutMode.DISABLED.value,
                "contextPolicy": {
                    "ceilingMode": AgentCeilingMode.PROVIDER_BOUNDED.value,
                },
            }
        )
        task = TaskDefinition.model_validate(task_payload)
        registry = configured_model_engine_registry(
            Settings(
                _env_file=None,
                model_engine_state_root=str(tmp_path),
                model_engine_codex_command=(sys.executable, str(CODEX_FIXTURE)),
                model_engine_timeout_seconds=2,
                model_engine_cancel_grace_seconds=0.2,
            )
        )
        model_handler = agent_llm_handler(provider_registry=registry)
        completed = await agent_session_handler(
            resources=resources,
            sessions=MemorySessions(),
            model_handler=model_handler,
            mcp_handler=ScriptedMcp(),
            harness=RecordingHarness(),
            model_capability_resolver=configured_model_capability_resolver(registry),
        )(task, _context())

        assert isinstance(completed, TaskCompletion)
        assert completed.output["result"] == {"answer": "ok"}

    asyncio.run(scenario())


def test_session_rejects_undelegated_engine_before_model_invocation() -> None:
    async def scenario() -> None:
        resources, model, task = _engine_session_fixture()
        task = TaskDefinition.model_validate(
            {
                **task.model_dump(mode="json", by_alias=True),
                "contract": {"secretScopes": ["mcp-token"]},
            }
        )
        handler = agent_session_handler(
            resources=resources,
            sessions=MemorySessions(),
            model_handler=model,
            mcp_handler=ScriptedMcp(),
            harness=RecordingHarness(),
        )

        with pytest.raises(PermissionError, match="engineScopes"):
            await handler(task, _context())
        assert model.calls == []

    asyncio.run(scenario())
