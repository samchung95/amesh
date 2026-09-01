from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from typing import Any, cast
from uuid import UUID, uuid4

import httpx
from cryptography.fernet import Fernet
from tests.model_providers.test_handler_integration import MemoryInvocationRepository
from tests.tasks.test_agent_sessions import (
    MemoryResources,
    MemorySessions,
    RecordingHarness,
    ScriptedMcp,
    _context,
    _pin,
    _task,
)
from tests.test_session_transfer import _bundle

from amesh.domain import (
    AgentHarnessContextBudget,
    AgentModelContinuationBinding,
    AgentModelContinuationRef,
    AgentSessionCheckpoint,
    InputModality,
    create_harness_context_receipt,
)
from amesh.executor import TaskCompletion, TaskExecutionContext
from amesh.model_continuations import ModelContinuationProtector
from amesh.ports import AgentHarnessContextSelection, AgentSessionModelCall
from amesh.session_transfer import SessionTransferMode, SessionTransferService, seal_bundle
from amesh.tasks import agent_llm_handler
from amesh.tasks.session import (
    _continuation_bindings_for_route,
    _TaskHandlerModelGateway,
    agent_session_handler,
)


def _ref(invocation_id: UUID) -> AgentModelContinuationRef:
    return AgentModelContinuationRef(
        invocationId=invocation_id,
        providerId="fixture",
        providerRevision="1.0.0",
        tokenDigest="sha256:" + "a" * 64,
    )


def test_checkpoint_continuation_history_is_ordered_and_backwards_compatible() -> None:
    first = _ref(uuid4())
    second = _ref(uuid4())
    checkpoint = AgentSessionCheckpoint(
        messages=(
            {"role": "system", "content": "s"},
            {"role": "assistant", "content": "a"},
            {"role": "assistant", "content": "b"},
        ),
        modelContinuations=(
            AgentModelContinuationBinding(sourceMessageIndex=1, continuation=first),
            AgentModelContinuationBinding(sourceMessageIndex=2, continuation=second),
        ),
    )

    restored = AgentSessionCheckpoint.model_validate(
        checkpoint.model_dump(mode="json", by_alias=True)
    )
    assert [item.source_message_index for item in restored.model_continuations] == [1, 2]
    legacy = AgentSessionCheckpoint(
        messages=(
            {"role": "system", "content": "s"},
            {"role": "assistant", "content": "a"},
        ),
        modelContinuation=first,
    )
    assert legacy.model_continuations == ()
    inferred = _continuation_bindings_for_route(legacy, "fixture")
    assert [(item.source_message_index, item.invocation_id) for item in inferred] == [
        (1, first.invocation_id)
    ]


def test_gateway_remaps_only_retained_continuation_sources() -> None:
    async def scenario() -> None:
        first_id = uuid4()
        second_id = uuid4()
        messages = tuple(
            {"role": role, "content": str(index)}
            for index, role in enumerate(
                ("system", "user", "assistant", "tool", "assistant", "user")
            )
        )
        bindings = (
            AgentModelContinuationBinding(sourceMessageIndex=2, continuation=_ref(first_id)),
            AgentModelContinuationBinding(sourceMessageIndex=4, continuation=_ref(second_id)),
        )
        call = AgentSessionModelCall(
            routeId="fixture",
            provider={"adapter": "fixture"},
            model="fixture/model",
            messages=messages,
            inputModalities=frozenset({InputModality.TEXT}),
            outputSchema={"type": "object"},
            maxTotalTokens=100,
            maxCompletionTokens=10,
            maxCostUsd=Decimal("1"),
            timeoutSeconds=5,
            invocationKey="continuation-test",
            continuationBindings=bindings,
        )
        budget = AgentHarnessContextBudget(
            contextWindowTokens=100,
            maxInputTokens=80,
            reservedCompletionTokens=10,
            compactionTriggerTokens=80,
            maxMessages=10,
            maxBytes=10_000,
        )
        selected = (messages[0], messages[1], messages[4], messages[5])
        receipt = create_harness_context_receipt(
            messages,
            selected,
            budget,
            turn=1,
            algorithm="fixture/v1",
            harness_adapter="fixture",
            harness_version="1",
            retained_source_indexes=(0, 1, 4, 5),
            omitted_source_indexes=(2, 3),
        )
        captured: list[dict[str, Any]] = []

        async def model_handler(task: Any, context: Any) -> TaskCompletion:
            del context
            assert task.model_extra is not None
            captured.append(task.model_extra)
            return TaskCompletion(output={"ok": True})

        gateway = _TaskHandlerModelGateway(
            model_handler=model_handler,
            context=cast(TaskExecutionContext, object()),
            allowed_call=call,
            context_budget=budget,
            turn=1,
            progress_context=None,
        )
        await gateway.invoke(
            call,
            context_selection=AgentHarnessContextSelection(messages=selected, receipt=receipt),
        )
        assert captured[0]["continuationSources"] == [
            {"messageIndex": 2, "invocationId": str(second_id)}
        ]
        assert str(first_id) not in str(captured[0]["continuationSources"])

    asyncio.run(scenario())


def test_clean_checkpoint_transfer_rejects_continuation_binding_history() -> None:
    bundle = _bundle(SessionTransferMode.CLEAN_CHECKPOINT)
    checkpoint = bundle.session.checkpoint.model_copy(
        update={
            "model_continuations": (
                AgentModelContinuationBinding(
                    sourceMessageIndex=1,
                    continuation=_ref(uuid4()),
                ),
            )
        }
    )
    blocked = seal_bundle(
        bundle.model_copy(
            update={
                "session": bundle.session.model_copy(update={"checkpoint": checkpoint}),
                "checksum_sha256": "0" * 64,
            }
        )
    )
    result = SessionTransferService(_NoopImportRepository()).eligibility(blocked)
    assert not result.eligible
    assert "checkpoint has provider continuation bindings" in result.reasons


class _NoopImportRepository:
    async def get_import(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError


def test_three_accepted_continuations_remain_bound_to_retained_turns() -> None:
    class ThreeTurnModel:
        def __init__(self) -> None:
            self.calls: list[Any] = []
            self.ids = [uuid4(), uuid4(), uuid4()]

        async def __call__(self, task: Any, context: Any) -> TaskCompletion:
            del context
            self.calls.append(task)
            turn = len(self.calls)
            action = (
                {
                    "action": "tool",
                    "tool": "lookup",
                    "arguments": {"key": str(turn)},
                    "output": None,
                    "rationale": "Need evidence",
                }
                if turn < 3
                else {
                    "action": "final",
                    "tool": "lookup",
                    "arguments": None,
                    "output": {"answer": "done"},
                    "rationale": "Done",
                }
            )
            return TaskCompletion(
                output={
                    "structuredOutput": action,
                    "model": "fixture/model",
                    "usage": {"total_tokens": 1},
                    "costUsd": "0.001",
                    "continuation": {
                        "invocationId": str(self.ids[turn - 1]),
                        "providerId": "openai-compatible",
                        "providerRevision": "1.0.0",
                        "tokenDigest": "sha256:" + "a" * 64,
                    },
                }
            )

    async def scenario() -> None:
        model = ThreeTurnModel()
        sessions = MemorySessions()
        handler = agent_session_handler(
            resources=MemoryResources(_pin()),
            sessions=sessions,
            model_handler=model,
            mcp_handler=ScriptedMcp(),
            harness=RecordingHarness(),
        )
        context = _context()
        result = await handler(_task(), context)
        assert result.output["result"] == {"answer": "done"}
        detail = await sessions.get_session("default", context.task_run_id, 1)
        bindings = detail.session.checkpoint.model_continuations
        assert [item.source_message_index for item in bindings] == [2, 4, 6]
        assert model.calls[1].model_extra is not None
        assert model.calls[2].model_extra is not None
        assert model.calls[1].model_extra["continuationSources"] == [
            {"messageIndex": 2, "invocationId": str(model.ids[0])}
        ]
        assert model.calls[2].model_extra["continuationSources"] == [
            {"messageIndex": 2, "invocationId": str(model.ids[0])},
            {"messageIndex": 4, "invocationId": str(model.ids[1])},
        ]

    asyncio.run(scenario())


def test_three_turn_session_inserts_continuations_on_adjacent_assistant_messages() -> None:
    async def scenario() -> None:
        from amesh.adapters.openai_compatible import OpenAICompatibleModelProvider

        actions = (
            {
                "action": "tool",
                "tool": "lookup",
                "arguments": '{"key": "1"}',
                "output": None,
                "rationale": "Need evidence",
            },
            {
                "action": "tool",
                "tool": "lookup",
                "arguments": '{"key": "2"}',
                "output": None,
                "rationale": "Need more evidence",
            },
            {
                "action": "final",
                "tool": "lookup",
                "arguments": None,
                "output": {"answer": "done"},
                "rationale": "Done",
            },
        )
        posted: list[dict[str, Any]] = []

        async def respond(request: httpx.Request) -> httpx.Response:
            posted.append(json.loads(request.content))
            turn = len(posted)
            action = actions[turn - 1]
            return httpx.Response(
                200,
                json={
                    "model": "openai/gpt-5.6-luna",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(action),
                                "reasoning_content": f"continuation-{turn}",
                            }
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 2,
                        "completion_tokens": 1,
                        "total_tokens": 3,
                        "cost": "0.001",
                    },
                },
            )

        repository = MemoryInvocationRepository()
        protector = ModelContinuationProtector(
            primary_key_id="current",
            keys={"current": Fernet.generate_key().decode("ascii")},
        )
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            model_handler = agent_llm_handler(
                provider=OpenAICompatibleModelProvider(client),
                repository=repository,
                continuation_protector=protector,
            )
            handler = agent_session_handler(
                resources=MemoryResources(_pin()),
                sessions=MemorySessions(),
                model_handler=model_handler,
                mcp_handler=ScriptedMcp(),
                harness=RecordingHarness(),
            )
            result = await handler(_task(), _context())

        assert result.output["result"] == {"answer": "done"}
        assert len(posted) == 3
        assert [message["role"] for message in posted[1]["messages"]] == [
            "system",
            "user",
            "assistant",
            "user",
        ]
        assert [message["role"] for message in posted[2]["messages"]] == [
            "system",
            "user",
            "assistant",
            "user",
            "assistant",
            "user",
        ]

        assert all("reasoning_content" not in message for message in posted[0]["messages"])
        assert posted[1]["messages"][2]["reasoning_content"] == "continuation-1"
        assert all(
            message.get("reasoning_content") is None
            for message in posted[1]["messages"][:2] + posted[1]["messages"][3:]
        )
        assert posted[2]["messages"][2]["reasoning_content"] == "continuation-1"
        assert posted[2]["messages"][4]["reasoning_content"] == "continuation-2"
        assert posted[2]["messages"][2]["reasoning_content"] != "continuation-2"
        assert posted[2]["messages"][4]["reasoning_content"] != "continuation-1"
        assert all(
            message.get("reasoning_content") is None
            for message in posted[2]["messages"][:2]
            + posted[2]["messages"][3:4]
            + posted[2]["messages"][5:]
        )

    asyncio.run(scenario())
