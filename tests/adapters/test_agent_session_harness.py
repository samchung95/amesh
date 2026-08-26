from __future__ import annotations

import asyncio
import shutil
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from amesh.adapters.agent_session_harness import (
    PiAgentSessionHarness,
    _pi_usage,
    _pi_worker_environment,
)
from amesh.executor import TaskExecutionFailure
from amesh.ports import (
    AgentSessionHarnessRequest,
    AgentSessionModelCall,
)


def _request(
    *, timeout: float = 1, messages: tuple[dict[str, Any], ...] = ()
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
    )


def _fake_worker_script(*frames: dict[str, Any]) -> str:
    serialized = repr(frames)
    return (
        "import json,sys; command=json.loads(sys.stdin.readline()); "
        f"frames={serialized}; "
        "[print(json.dumps({**frame, 'runId': command.get('runId')}), flush=True) for frame in frames]"
    )


_ROOT = Path(__file__).resolve().parents[2]
_WORKER = _ROOT / "harnesses" / "pi" / "src" / "worker.mjs"
_PI_PACKAGE = _ROOT / "harnesses" / "pi" / "node_modules" / "@earendil-works" / "pi-agent-core"


class RecordingGateway:
    def __init__(self, answer: str = "through Pi") -> None:
        self.calls: list[AgentSessionModelCall] = []
        self.answer = answer

    async def invoke(self, call: AgentSessionModelCall) -> dict[str, Any]:
        self.calls.append(call)
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
            "workerProtocol": "amesh.pi-worker/v1",
        }
        assert gateway.calls == [call]

    asyncio.run(scenario())


def test_pi_worker_environment_excludes_provider_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "must-not-reach-pi")
    monkeypatch.setenv("PATH", "runtime-path")

    environment = _pi_worker_environment()

    assert environment["PATH"] == "runtime-path"
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
            "protocol": "amesh.pi-worker/v1",
            "adapterVersion": "0.84.3",
        }
        for frame, error in (
            ({"type": "tool.request", "protocol": "amesh.pi-worker/v1"}, "native tool"),
            ({"type": "state.commit", "protocol": "amesh.pi-worker/v1"}, "unexpected frame"),
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
