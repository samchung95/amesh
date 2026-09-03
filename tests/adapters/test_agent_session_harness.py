from __future__ import annotations

import asyncio
import shutil
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

import amesh.adapters.agent_session_harness as agent_session_harness
from amesh.adapters._managed_process import ManagedProcess
from amesh.adapters.agent_session_harness import (
    PiAgentSessionHarness,
    _pi_usage,
    _pi_worker_environment,
)
from amesh.adapters.agent_session_registry import create_agent_session_harness
from amesh.config import Settings
from amesh.domain import AgentHarnessContextBudget, create_harness_context_receipt
from amesh.domain.agent_progress import AgentProgressFrame
from amesh.domain.image_inputs import InputModality
from amesh.executor import TaskExecutionFailure
from amesh.ports import (
    AgentHarnessContextSelection,
    AgentProgressContext,
    AgentSessionHarnessRequest,
    AgentSessionHarnessResult,
    AgentSessionModelCall,
)


def test_harness_request_preserves_ordered_image_content_parts() -> None:
    request = _request(
        messages=(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe"},
                    {
                        "type": "image_ref",
                        "image": {"schemaVersion": "amesh.image-ref/v1"},
                    },
                ],
            },
        )
    )
    request = request.model_copy(
        update={
            "model_call": request.model_call.model_copy(
                update={"input_modalities": frozenset({InputModality.TEXT, InputModality.IMAGE})}
            )
        }
    )

    assert request.model_call.input_modalities == frozenset(
        {InputModality.TEXT, InputModality.IMAGE}
    )
    assert request.model_call.messages[0]["content"][1]["type"] == "image_ref"


def test_pi_keeps_governed_images_ordered_at_amesh_gateway_boundary() -> None:
    """Pi receives an acknowledgement only; AMESH retains the governed input and authority."""

    async def scenario() -> None:
        image = {
            "schemaVersion": "amesh.image-ref/v1",
            "artifact": {
                "reference": "nsfile:///images/tiny.png?version=1&sha256=" + "a" * 64,
                "contentAddress": "sha256:" + "a" * 64,
                "tenantId": "default",
                "namespace": "agents.demo",
                "path": "images/tiny.png",
                "version": 1,
                "mediaType": "image/png",
                "sizeBytes": 68,
                "checksumSha256": "a" * 64,
                "provenance": {
                    "source": "namespace-file",
                    "originNamespace": "agents.demo",
                    "createdBy": "fixture",
                    "createdAt": "2026-01-01T00:00:00Z",
                },
                "retention": {},
            },
            "display": {"filename": "tiny.png", "altText": "fixture image"},
        }
        request = _request(
            messages=(
                {
                    "role": "user",
                    "content": (
                        {"type": "text", "text": "Read this image."},
                        {"type": "image_ref", "image": image},
                        {"type": "text", "text": "Return the pinned JSON."},
                    ),
                },
            )
        ).model_copy(
            update={
                "model_call": _request(messages=()).model_call.model_copy(
                    update={
                        "messages": (
                            {
                                "role": "user",
                                "content": (
                                    {"type": "text", "text": "Read this image."},
                                    {"type": "image_ref", "image": image},
                                    {"type": "text", "text": "Return the pinned JSON."},
                                ),
                            },
                        ),
                        "input_modalities": frozenset({InputModality.TEXT, InputModality.IMAGE}),
                    }
                )
            }
        )
        gateway = RecordingGateway()
        command = (
            sys.executable,
            "-c",
            _fake_worker_script(
                {
                    "type": "run.started",
                    "protocol": "amesh.pi-worker/v2",
                    "adapterVersion": "0.84.3",
                },
                {"type": "model.request", "protocol": "amesh.pi-worker/v2", "requestId": "model-1"},
                {"type": "run.result", "protocol": "amesh.pi-worker/v2"},
            ),
        )

        result = await PiAgentSessionHarness(command).next_action(
            request,
            model_gateway=gateway,
        )

        assert result.adapter == "pi-agent-core"
        assert gateway.calls[0] == request.model_call
        assert [part["type"] for part in gateway.calls[0].messages[0]["content"]] == [
            "text",
            "image_ref",
            "text",
        ]
        assert "image" not in result.metadata

    asyncio.run(scenario())


def test_pi_harness_declares_text_and_image_input() -> None:
    harness = PiAgentSessionHarness((sys.executable, "-c", ""))

    assert harness.input_modalities == frozenset({InputModality.TEXT, InputModality.IMAGE})


def _request(
    *, timeout: float | None = 1, messages: tuple[dict[str, Any], ...] = ()
) -> AgentSessionHarnessRequest:
    call = AgentSessionModelCall(
        routeId="luna",
        provider={"adapter": "openai-compatible"},
        model="openai/gpt-5.6-luna",
        messages=messages or ({"role": "user", "content": "Answer."},),
        outputSchema={"type": "object"},
        maxTotalTokens=100,
        maxCompletionTokens=50,
        maxCostUsd=Decimal("1"),
        timeoutSeconds=timeout,
        invocationKey="session:test:turn:1:route:luna",
    )
    return AgentSessionHarnessRequest(
        sessionId=uuid4(),
        turn=1,
        envelopeDigest="sha256:" + "1" * 64,
        modelCall=call,
        contextBudget=_budget(call),
    )


def _budget(call: AgentSessionModelCall) -> AgentHarnessContextBudget:
    return AgentHarnessContextBudget(
        contextWindowTokens=10_000 + call.max_completion_tokens,
        maxInputTokens=10_000,
        reservedCompletionTokens=call.max_completion_tokens,
        compactionTriggerTokens=10_000,
        maxMessages=10_000,
        maxBytes=100_000_000,
    )


def _receipt(
    request: AgentSessionHarnessRequest,
    *,
    adapter: str,
    version: str,
):
    indexes = tuple(range(len(request.model_call.messages)))
    return create_harness_context_receipt(
        request.model_call.messages,
        request.model_call.messages,
        request.context_budget,
        turn=request.turn,
        algorithm="fixture.passthrough/v1",
        harness_adapter=adapter,
        harness_version=version,
        retained_source_indexes=indexes,
        omitted_source_indexes=(),
    )


def test_harness_evidence_allows_only_safe_provenance_metadata() -> None:
    request = _request()
    evidence = AgentSessionHarnessResult(
        adapter="fixture",
        adapterVersion="1.0",
        modelOutput={"structuredOutput": {}},
        contextReceipt=_receipt(request, adapter="fixture", version="1.0"),
        metadata={
            "modelGateway": "amesh",
            "routeId": {"prompt": "must not escape"},
            "workerProtocol": "fixture/v1",
            "prompt": "hidden prompt",
            "reasoning": "private reasoning",
            "debug": {"secret": "value"},
        },
    ).evidence()

    assert evidence == {
        "adapter": "fixture",
        "adapterVersion": "1.0",
        "metadata": {
            "modelGateway": "amesh",
            "workerProtocol": "fixture/v1",
        },
    }


def _fake_worker_script(
    *frames: dict[str, Any],
    expected_turn: int | None = None,
    expected_run_id: str | None = None,
) -> str:
    serialized = repr(frames)
    turn_assertion = (
        f"assert command.get('turn') == {expected_turn}; " if expected_turn is not None else ""
    )
    run_id_assertion = (
        f"assert command.get('runId') == {expected_run_id!r}; "
        if expected_run_id is not None
        else ""
    )
    return (
        "import json,sys; command=json.loads(sys.stdin.readline()); "
        f"{turn_assertion}"
        f"{run_id_assertion}"
        f"frames={serialized}; "
        "selected=command.get('messages', []); indexes=list(range(len(selected))); "
        "projection={'algorithm':'fixture.passthrough/v1','retainedSourceIndexes':indexes,'omittedSourceIndexes':[]}; "
        "[print(json.dumps({**frame, 'runId': command.get('runId'), **({'selectedMessages':selected,'contextProjection':projection} if frame.get('type')=='model.request' else {})}), flush=True) for frame in frames]"
    )


_ROOT = Path(__file__).resolve().parents[2]
_WORKER = _ROOT / "harnesses" / "pi" / "src" / "worker.mjs"
_PI_PACKAGE = _ROOT / "harnesses" / "pi" / "node_modules" / "@earendil-works" / "pi-agent-core"


class RecordingGateway:
    def __init__(self, answer: str = "through Pi") -> None:
        self.calls: list[AgentSessionModelCall] = []
        self.selections: list[AgentHarnessContextSelection] = []
        self.answer = answer

    async def invoke(
        self,
        call: AgentSessionModelCall,
        *,
        context_selection: AgentHarnessContextSelection,
    ) -> dict[str, Any]:
        self.calls.append(call)
        self.selections.append(context_selection)
        return {
            "structuredOutput": {
                "action": "final",
                "tool": "none",
                "arguments": None,
                "output": {"answer": self.answer},
                "rationale": "Done",
            },
            "model": call.model,
            "usage": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5},
            "usageNormalized": {
                "state": "unpriced",
                "inputTokens": 2,
                "outputTokens": 3,
                "totalTokens": 5,
            },
            "costUsd": "0.001",
        }


class RecordingProgressSink:
    def __init__(self) -> None:
        self.frames: list[AgentProgressFrame] = []
        self.contexts: list[AgentProgressContext] = []
        self.closed: list[AgentProgressContext] = []

    async def append(
        self,
        context: AgentProgressContext,
        frame: AgentProgressFrame,
    ) -> object:
        self.contexts.append(context)
        self.frames.append(frame)
        return object()

    async def close_active_segment(
        self, context: AgentProgressContext, *, occurred_at: object
    ) -> None:
        del occurred_at
        self.closed.append(context)


def test_pi_default_worker_starts_after_managed_process_changes_cwd() -> None:
    async def scenario() -> None:
        settings = Settings(_env_file=None)
        assert settings.agent_session_pi_worker_command == (
            "node",
            "harnesses/pi/src/worker.mjs",
        )
        assert shutil.which("node") is not None
        assert _PI_PACKAGE.exists()
        adapter = create_agent_session_harness(
            "pi",
            settings.agent_session_pi_worker_command,
        )

        result = await adapter.next_action(
            _request(timeout=10),
            model_gateway=RecordingGateway(),
        )

        assert result.adapter == "pi-agent-core"

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "worker_command",
    (
        ("node", str(_WORKER)),
        ("custom-node", "custom/worker.mjs", "--flag"),
    ),
)
def test_pi_registry_preserves_absolute_and_custom_worker_commands(
    worker_command: tuple[str, ...],
) -> None:
    adapter = create_agent_session_harness("pi", worker_command)

    assert adapter._worker_command == worker_command


def test_pi_adapter_uses_stable_invocation_specific_run_ids() -> None:
    async def scenario() -> None:
        session_id = uuid4()
        initial = _request().model_copy(update={"session_id": session_id})
        repair = initial.model_copy(
            update={
                "model_call": initial.model_call.model_copy(
                    update={
                        "invocation_key": "session:test:turn:1:repair:1:route:luna",
                    }
                )
            }
        )
        initial_run_id = f"{session_id}:{initial.model_call.invocation_key}"
        repair_run_id = f"{session_id}:{repair.model_call.invocation_key}"
        frames = (
            {
                "type": "run.started",
                "protocol": "amesh.pi-worker/v2",
                "adapterVersion": "0.84.3",
            },
            {
                "type": "model.request",
                "protocol": "amesh.pi-worker/v2",
                "requestId": "model-1",
            },
            {"type": "run.result", "protocol": "amesh.pi-worker/v2"},
        )

        assert initial_run_id != repair_run_id
        for request, expected_run_id in (
            (initial, initial_run_id),
            (initial, initial_run_id),
            (repair, repair_run_id),
        ):
            command = (
                sys.executable,
                "-c",
                _fake_worker_script(*frames, expected_run_id=expected_run_id),
            )
            result = await PiAgentSessionHarness(command).next_action(
                request,
                model_gateway=RecordingGateway(),
            )
            assert result.adapter == "pi-agent-core"

    asyncio.run(scenario())


def test_pi_adapter_routes_one_turn_through_amesh_model_gateway() -> None:
    async def scenario() -> None:
        call = AgentSessionModelCall(
            routeId="luna",
            provider={
                "adapter": "openai-compatible",
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "credentialRef": "openrouter",
            },
            model="openai/gpt-5.6-luna",
            messages=(
                {"role": "system", "content": "Return one action."},
                {"role": "user", "content": "Answer."},
            ),
            outputSchema={"type": "object"},
            maxTotalTokens=100,
            maxCompletionTokens=50,
            maxCostUsd=Decimal("1"),
            timeoutSeconds=10,
            invocationKey="session:test:turn:1:route:luna",
            secretScopes=("openrouter",),
        )
        request = AgentSessionHarnessRequest(
            sessionId=uuid4(),
            turn=1,
            envelopeDigest="sha256:" + "1" * 64,
            modelCall=call,
            contextBudget=_budget(call),
        )
        gateway = RecordingGateway()
        node = shutil.which("node")
        assert node is not None
        assert _PI_PACKAGE.exists()
        adapter = PiAgentSessionHarness((node, str(_WORKER)))

        result = await adapter.next_action(request, model_gateway=gateway)

        assert result.adapter == "pi-agent-core"
        assert result.adapter_version == "0.84.3"
        assert result.model_output["structuredOutput"]["output"] == {"answer": "through Pi"}
        assert result.metadata == {
            "modelGateway": "amesh",
            "routeId": "luna",
            "workerProtocol": "amesh.pi-worker/v2",
        }
        assert gateway.calls == [call]

    asyncio.run(scenario())


def test_pi_adapter_transports_disabled_message_and_byte_context_caps() -> None:
    async def scenario() -> None:
        request = _request(timeout=10)
        request = request.model_copy(
            update={
                "context_budget": request.context_budget.model_copy(
                    update={"max_messages": None, "max_bytes": None}
                )
            }
        )
        gateway = RecordingGateway()
        node = shutil.which("node")
        assert node is not None
        assert _PI_PACKAGE.exists()

        result = await PiAgentSessionHarness((node, str(_WORKER))).next_action(
            request,
            model_gateway=gateway,
        )

        assert gateway.selections[0].messages == request.model_call.messages
        assert result.context_receipt.message_headroom is None
        assert result.context_receipt.byte_headroom is None

    asyncio.run(scenario())


def test_pi_adapter_chunks_large_canonical_and_selected_context() -> None:
    async def scenario() -> None:
        large_content = "x" * 700_000
        request = _request(
            timeout=10,
            messages=({"role": "user", "content": large_content},),
        ).model_copy(
            update={
                "context_budget": AgentHarnessContextBudget(
                    contextWindowTokens=300_050,
                    maxInputTokens=300_000,
                    reservedCompletionTokens=50,
                    compactionTriggerTokens=300_000,
                    maxMessages=64,
                    maxBytes=2_000_000,
                )
            }
        )
        gateway = RecordingGateway()
        node = shutil.which("node")
        assert node is not None

        result = await PiAgentSessionHarness((node, str(_WORKER))).next_action(
            request,
            model_gateway=gateway,
        )

        assert result.model_output["structuredOutput"]["output"] == {"answer": "through Pi"}
        assert gateway.selections[0].messages[0]["content"] == large_content
        assert result.context_receipt.context_bytes > 524_288

    asyncio.run(scenario())


def test_pi_adapter_sends_requested_turn_to_worker() -> None:
    async def scenario() -> None:
        request = _request().model_copy(update={"turn": 2})
        command = (
            sys.executable,
            "-c",
            _fake_worker_script(
                {
                    "type": "run.started",
                    "protocol": "amesh.pi-worker/v2",
                    "adapterVersion": "0.84.3",
                },
                {
                    "type": "model.request",
                    "protocol": "amesh.pi-worker/v2",
                    "requestId": "model-1",
                },
                {"type": "run.result", "protocol": "amesh.pi-worker/v2"},
                expected_turn=2,
            ),
        )

        result = await PiAgentSessionHarness(command).next_action(
            request,
            model_gateway=RecordingGateway(),
        )

        assert result.model_output["structuredOutput"]["output"] == {"answer": "through Pi"}

    asyncio.run(scenario())


def test_pi_adapter_appends_versioned_progress_in_worker_order() -> None:
    async def scenario() -> None:
        request = _request()
        context = AgentProgressContext(
            tenantId="default",
            serviceSessionId=uuid4(),
            executionId=uuid4(),
            taskRunId=uuid4(),
            attemptSessionId=uuid4(),
            attempt=1,
        )
        segment = uuid4()
        occurred_at = "2026-01-01T00:00:00+00:00"
        frames = (
            {
                "type": "run.started",
                "protocol": "amesh.pi-worker/v2",
                "adapterVersion": "0.84.3",
            },
            {
                "type": "progress",
                "protocol": "amesh.pi-worker/v2",
                "frame": {
                    "schemaVersion": "amesh.agent-progress/v1",
                    "attemptSessionId": str(context.attempt_session_id),
                    "attempt": 1,
                    "turn": 1,
                    "activity": "THINKING",
                    "status": "STARTED",
                    "activityId": "thinking:1",
                    "segmentId": str(segment),
                    "sourceId": "pi",
                    "sourceSequence": 1,
                    "occurredAt": occurred_at,
                },
            },
            {
                "type": "model.request",
                "protocol": "amesh.pi-worker/v2",
                "requestId": "model-1",
            },
            {
                "type": "progress",
                "protocol": "amesh.pi-worker/v2",
                "frame": {
                    "schemaVersion": "amesh.agent-progress/v1",
                    "attemptSessionId": str(context.attempt_session_id),
                    "attempt": 1,
                    "turn": 1,
                    "activity": "TOOL",
                    "status": "STARTED",
                    "activityId": "tool:hash",
                    "segmentId": str(segment),
                    "sourceId": "pi",
                    "sourceSequence": 2,
                    "occurredAt": occurred_at,
                },
            },
            {
                "type": "progress",
                "protocol": "amesh.pi-worker/v2",
                "frame": {
                    "schemaVersion": "amesh.agent-progress/v1",
                    "attemptSessionId": str(context.attempt_session_id),
                    "attempt": 1,
                    "turn": 1,
                    "activity": "TOOL",
                    "status": "COMPLETED",
                    "activityId": "tool:hash",
                    "segmentId": str(segment),
                    "sourceId": "pi",
                    "sourceSequence": 3,
                    "occurredAt": occurred_at,
                },
            },
            {"type": "run.result", "protocol": "amesh.pi-worker/v2"},
        )
        command = (sys.executable, "-c", _fake_worker_script(*frames))
        sink = RecordingProgressSink()

        result = await PiAgentSessionHarness(command).next_action(
            request,
            model_gateway=RecordingGateway(),
            progress_sink=sink,
            progress_context=context,
        )

        assert result.adapter == "pi-agent-core"
        assert [(frame.activity.value, frame.status.value) for frame in sink.frames] == [
            ("THINKING", "STARTED"),
            ("TOOL", "STARTED"),
            ("TOOL", "COMPLETED"),
        ]
        assert sink.contexts == [context, context, context]

    asyncio.run(scenario())


def test_pi_adapter_rejects_progress_without_both_sink_and_context() -> None:
    async def scenario() -> None:
        with pytest.raises(ValueError, match="sink and context"):
            await PiAgentSessionHarness((sys.executable, "-c", "")).next_action(
                _request(),
                model_gateway=RecordingGateway(),
                progress_sink=RecordingProgressSink(),
            )

    asyncio.run(scenario())


def test_pi_adapter_closes_progress_when_worker_fails() -> None:
    async def scenario() -> None:
        request = _request()
        context = AgentProgressContext(
            tenantId="default",
            serviceSessionId=uuid4(),
            executionId=uuid4(),
            taskRunId=uuid4(),
            attemptSessionId=uuid4(),
            attempt=1,
        )
        command = (
            sys.executable,
            "-c",
            _fake_worker_script(
                {
                    "type": "run.started",
                    "protocol": "amesh.pi-worker/v2",
                    "adapterVersion": "0.84.3",
                },
                {
                    "type": "progress",
                    "protocol": "amesh.pi-worker/v2",
                    "frame": {
                        "schemaVersion": "amesh.agent-progress/v1",
                        "attemptSessionId": str(context.attempt_session_id),
                        "attempt": 1,
                        "turn": 1,
                        "activity": "THINKING",
                        "status": "STARTED",
                        "activityId": "thinking:failure",
                        "segmentId": str(uuid4()),
                        "sourceId": "pi",
                        "sourceSequence": 1,
                        "occurredAt": "2026-01-01T00:00:00+00:00",
                    },
                },
                {"type": "unexpected", "protocol": "amesh.pi-worker/v2"},
            ),
        )
        sink = RecordingProgressSink()

        with pytest.raises(RuntimeError, match="unexpected frame"):
            await PiAgentSessionHarness(command).next_action(
                request,
                model_gateway=RecordingGateway(),
                progress_sink=sink,
                progress_context=context,
            )

        assert len(sink.frames) == 1
        assert sink.closed == [context]

    asyncio.run(scenario())


def test_pi_worker_environment_excludes_provider_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "must-not-reach-pi")
    monkeypatch.setenv("PATH", "runtime-path")

    environment = _pi_worker_environment(
        {"LANG": "configured-locale"},
        max_frame_bytes=2_097_152,
    )

    assert environment["PATH"] == "runtime-path"
    assert environment["LANG"] == "configured-locale"
    assert environment["AMESH_PI_MAX_FRAME_BYTES"] == "2097152"
    assert "OPENROUTER_API_KEY" not in environment


def test_pi_usage_preserves_normalized_prompt_cache_counters() -> None:
    usage = _pi_usage(
        {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 5,
                "total_tokens": 105,
                "prompt_tokens_details": {
                    "cached_tokens": 70,
                    "cache_write_tokens": 20,
                },
            },
            "usageNormalized": {
                "inputTokens": 100,
                "outputTokens": 5,
                "totalTokens": 105,
                "promptCache": {"readTokens": 70, "writeTokens": 20},
            },
        }
    )

    assert usage == {
        "input": 100,
        "output": 5,
        "cacheRead": 70,
        "cacheWrite": 20,
        "totalTokens": 105,
    }


def test_pi_adapter_preserves_model_outputs_larger_than_its_control_frame_limit() -> None:
    async def scenario() -> None:
        answer = "x" * 1_100_000
        call = AgentSessionModelCall(
            routeId="luna",
            provider={"adapter": "openai-compatible"},
            model="openai/gpt-5.6-luna",
            messages=({"role": "user", "content": "Return the payload."},),
            outputSchema={"type": "object"},
            maxTotalTokens=1_000_000,
            maxCompletionTokens=500_000,
            maxCostUsd=Decimal("100"),
            timeoutSeconds=10,
            invocationKey="session:test:large:turn:1:route:luna",
        )
        request = AgentSessionHarnessRequest(
            sessionId=uuid4(),
            turn=1,
            envelopeDigest="sha256:" + "2" * 64,
            modelCall=call,
            contextBudget=_budget(call),
        )
        node = shutil.which("node")
        assert node is not None
        assert _PI_PACKAGE.exists()

        result = await PiAgentSessionHarness((node, str(_WORKER))).next_action(
            request,
            model_gateway=RecordingGateway(answer),
        )

        assert result.model_output["structuredOutput"]["output"]["answer"] == answer

    asyncio.run(scenario())


def test_pi_adapter_rejects_wrong_versioned_handshake() -> None:
    async def scenario() -> None:
        request = _request()
        command = (
            sys.executable,
            "-c",
            _fake_worker_script(
                {
                    "type": "run.started",
                    "protocol": "amesh.pi-worker/v0",
                    "adapterVersion": "0.84.3",
                }
            ),
        )
        with pytest.raises(RuntimeError, match="handshake protocol or version mismatch"):
            await PiAgentSessionHarness(command).next_action(
                request,
                model_gateway=RecordingGateway(),
            )

    asyncio.run(scenario())


def test_pi_adapter_rejects_native_tool_and_state_commit_frames() -> None:
    async def scenario() -> None:
        request = _request()
        started = {
            "type": "run.started",
            "protocol": "amesh.pi-worker/v2",
            "adapterVersion": "0.84.3",
        }
        for frame, error in (
            ({"type": "tool.request", "protocol": "amesh.pi-worker/v2"}, "native tool"),
            ({"type": "state.commit", "protocol": "amesh.pi-worker/v2"}, "unexpected frame"),
        ):
            command = (
                sys.executable,
                "-c",
                _fake_worker_script(started, frame),
            )
            harness = PiAgentSessionHarness(command)
            if error == "native tool":
                with pytest.raises(PermissionError, match="native tool"):
                    await harness.next_action(request, model_gateway=RecordingGateway())
            else:
                with pytest.raises(RuntimeError, match="unexpected frame"):
                    await harness.next_action(request, model_gateway=RecordingGateway())

    asyncio.run(scenario())


def test_pi_adapter_timeout_is_reported_as_timed_out() -> None:
    async def scenario() -> None:
        request = _request(timeout=0.01)
        command = (sys.executable, "-c", "import time; time.sleep(10)")
        with pytest.raises(TaskExecutionFailure) as caught:
            await PiAgentSessionHarness(command).next_action(
                request,
                model_gateway=RecordingGateway(),
            )
        assert caught.value.category.value == "TIMED_OUT"

    asyncio.run(scenario())


def test_pi_adapter_uses_configured_timeout_when_request_omits_one() -> None:
    async def scenario() -> None:
        request = _request(timeout=None)
        command = (sys.executable, "-c", "import time; time.sleep(10)")
        with pytest.raises(TaskExecutionFailure) as caught:
            await PiAgentSessionHarness(
                command,
                operation_timeout_seconds=0.01,
                cancel_grace_seconds=0.05,
            ).next_action(
                request,
                model_gateway=RecordingGateway(),
            )
        assert caught.value.category.value == "TIMED_OUT"

    asyncio.run(scenario())


def test_pi_missing_request_timeout_has_no_total_deadline() -> None:
    async def scenario() -> None:
        request = _request(timeout=None)
        frames = (
            {
                "type": "run.started",
                "protocol": "amesh.pi-worker/v2",
                "adapterVersion": "0.84.3",
            },
            {"type": "model.request", "protocol": "amesh.pi-worker/v2", "requestId": "model-1"},
            {"type": "run.result", "protocol": "amesh.pi-worker/v2"},
        )
        script = (
            "import json,sys,time; command=json.loads(sys.stdin.readline()); "
            f"frames={frames!r}; selected=command.get('messages', []); "
            "indexes=list(range(len(selected))); "
            "projection={'algorithm':'fixture.passthrough/v1','retainedSourceIndexes':indexes,'omittedSourceIndexes':[]}; "
            "[(time.sleep(0.25), print(json.dumps({**frame, 'runId': command.get('runId'), "
            "**({'selectedMessages':selected,'contextProjection':projection} if frame.get('type')=='model.request' else {})}), flush=True)) for frame in frames]"
        )

        result = await PiAgentSessionHarness(
            (sys.executable, "-c", script),
            operation_timeout_seconds=0.4,
        ).next_action(request, model_gateway=RecordingGateway())

        assert result.adapter == "pi-agent-core"

    asyncio.run(scenario())


def test_pi_cancellation_closes_child_and_owned_cwd(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[tuple[asyncio.subprocess.Process, Path]] = []

    class RecordingManagedProcess(ManagedProcess):
        async def start(self) -> asyncio.subprocess.Process:
            child = await super().start()
            assert self._cwd is not None
            observed.append((child, self._cwd))
            return child

    monkeypatch.setattr(agent_session_harness, "ManagedProcess", RecordingManagedProcess)

    async def scenario() -> None:
        harness = PiAgentSessionHarness(
            (sys.executable, "-c", "import sys, time; sys.stdin.readline(); time.sleep(10)"),
            cancel_grace_seconds=0.05,
        )
        task = asyncio.create_task(
            harness.next_action(_request(timeout=None), model_gateway=RecordingGateway())
        )
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        child, cwd = observed[0]
        assert child.returncode is not None
        assert not cwd.exists()

    asyncio.run(scenario())


def test_parent_to_pi_control_frames_are_bounded() -> None:
    class Stdin:
        def write(self, value: bytes) -> None:
            del value

        async def drain(self) -> None:
            return None

    class Process:
        stdin = Stdin()

    async def scenario() -> None:
        from amesh.adapters.agent_session_harness import _write_frame

        with pytest.raises(RuntimeError, match="control frame exceeded"):
            await _write_frame(Process(), {"payload": "x" * 100}, maximum_bytes=32)

    asyncio.run(scenario())
