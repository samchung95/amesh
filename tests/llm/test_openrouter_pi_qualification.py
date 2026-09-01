from __future__ import annotations

import asyncio
import base64
import hashlib
import os
import shutil
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from tests.tasks.test_agent_sessions import (
    MemoryResources,
    MemorySessions,
    ScriptedMcp,
    _context,
    _pin,
    _session_image,
    _task,
)

from amesh.adapters.agent_session_harness import PiAgentSessionHarness
from amesh.domain.agent_progress import AgentProgressFrame
from amesh.domain.image_inputs import ImageArtifactRef
from amesh.ports import AgentProgressContext
from amesh.tasks import agent_llm_handler, agent_session_handler

_DEFAULT_QUALIFICATION_MODELS = (
    "openai/gpt-5.6-luna",
    "deepseek/deepseek-v4-flash-vision-exp",
)


def _qualification_models() -> tuple[str, ...]:
    configured = os.getenv("OPENROUTER_QUALIFICATION_MODELS")
    if configured is None:
        return _DEFAULT_QUALIFICATION_MODELS
    return tuple(model.strip() for model in configured.split(",") if model.strip())


@pytest.fixture
def pi_harness() -> PiAgentSessionHarness:
    node = shutil.which("node")
    if node is None:
        pytest.fail("Pi qualification requires Node 22")
    worker = Path(__file__).resolve().parents[2] / "harnesses" / "pi" / "src" / "worker.mjs"
    return PiAgentSessionHarness((node, str(worker)))


class _TinyImageResolver:
    _PNG = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )

    async def resolve_image(self, image: ImageArtifactRef, *, tenant_id: str) -> bytes:
        assert image.artifact.tenant_id == tenant_id
        return self._PNG


class _ProgressSink:
    def __init__(self) -> None:
        self.frames: list[AgentProgressFrame] = []
        self.contexts: list[AgentProgressContext] = []

    async def append(self, context: AgentProgressContext, frame: AgentProgressFrame) -> object:
        self.contexts.append(context)
        self.frames.append(frame)
        return object()

    async def close_active_segment(
        self, context: AgentProgressContext, *, occurred_at: Any
    ) -> None:
        del context, occurred_at


@pytest.mark.skipif(
    os.getenv("OPENROUTER_API_KEY") is None,
    reason="OPENROUTER_API_KEY is required for the paid Pi multimodal qualification",
)
@pytest.mark.parametrize("model_id", _qualification_models())
def test_live_openrouter_pi_multimodal_qualification(
    model_id: str,
    pi_harness: PiAgentSessionHarness,
    record_testsuite_property: Any,
) -> None:
    """Exercise exact OpenRouter routes while keeping provider evidence explicit and safe."""

    async def scenario() -> None:
        base_pin = _pin(required_features=("image-input",), model=model_id)
        pin = base_pin.model_copy(
            update={
                "envelope": base_pin.envelope.model_copy(
                    update={
                        "input_schema": {"type": "object"},
                        "hard_limits": base_pin.envelope.hard_limits.model_copy(
                            update={"max_total_tokens": 2048}
                        ),
                        "tools": (),
                        "permissions": base_pin.envelope.permissions.model_copy(
                            update={"tool_allowlist": ()}
                        ),
                    }
                )
            }
        )
        sessions = MemorySessions()
        progress = _ProgressSink()
        model = agent_llm_handler(image_resolver=_TinyImageResolver(), progress_sink=progress)
        handler = agent_session_handler(
            resources=MemoryResources(pin),
            sessions=sessions,
            model_handler=model,
            mcp_handler=ScriptedMcp(),
            harness=pi_harness,
            progress_sink=progress,
        )
        context = _context()
        image_payload = _session_image().model_dump(mode="json", by_alias=True)
        checksum = hashlib.sha256(_TinyImageResolver._PNG).hexdigest()
        image_payload["artifact"].update(
            {
                "reference": image_payload["artifact"]["reference"].replace("a" * 64, checksum),
                "contentAddress": f"sha256:{checksum}",
                "sizeBytes": len(_TinyImageResolver._PNG),
                "checksumSha256": checksum,
            }
        )
        image_payload["display"].update({"widthPixels": 1, "heightPixels": 1})
        image = ImageArtifactRef.model_validate(image_payload)
        task = _task(
            repair=True,
            question=(
                "Inspect the supplied image and describe it briefly in the final "
                "output.answer, with no tool call."
            ),
            input_value={
                "question": "Inspect the supplied image and describe it briefly.",
                "image": image.model_dump(mode="json", by_alias=True),
            },
        )
        context = replace(
            context,
            secrets={"openrouter": os.environ["OPENROUTER_API_KEY"], "mcp-token": "unused"},
        )

        completed = await handler(task, context)

        answer = completed.output["result"]["answer"]
        assert isinstance(answer, str) and answer.strip()
        detail = await sessions.get_session(context.tenant_id, context.task_run_id, context.attempt)
        responses = [event for event in detail.events if event.event_type == "model.response"]
        assert len(responses) == 1
        response = responses[0].payload
        assert response["model"] == model_id
        assert response["usageNormalized"]["state"] != "unavailable"
        assert response["costNormalized"]["state"] == "billed"
        assert response["promptCache"]["state"] in {"reported", "unavailable"}
        assert response["contextReceipt"]["schemaVersion"] == "amesh.agent-context/v3"
        assert response["contextReceipt"]["harnessAdapter"] == "pi-agent-core"
        sequences_by_source: dict[str, list[int]] = {}
        for frame in progress.frames:
            sequences_by_source.setdefault(frame.source_id, []).append(frame.source_sequence)
        assert all(
            sequences == list(range(1, len(sequences) + 1))
            for sequences in sequences_by_source.values()
        )
        for frame in progress.frames:
            payload = frame.model_dump(mode="json")
            assert "reasoning" not in payload
            assert "thinking" not in payload
        if model_id == "deepseek/deepseek-v4-flash-vision-exp":
            assert any(frame.activity.value == "THINKING" for frame in progress.frames)
        record_testsuite_property("model", response["model"])
        record_testsuite_property("usage_state", response["usageNormalized"]["state"])
        record_testsuite_property("input_tokens", response["usageNormalized"]["inputTokens"])
        record_testsuite_property("output_tokens", response["usageNormalized"]["outputTokens"])
        record_testsuite_property("total_tokens", response["usageNormalized"]["totalTokens"])
        record_testsuite_property("cost_usd", response["costNormalized"]["amountUsd"])
        record_testsuite_property("prompt_cache_state", response["promptCache"]["state"])
        record_testsuite_property("safe_progress_frames", len(progress.frames))

        # A second call against the same durable session is the restart/reconnect check: the
        # terminal result is reused and the provider is not charged a duplicate model turn.
        resumed = await handler(task, context)
        assert resumed.output == completed.output
        detail_after_restart = await sessions.get_session(
            context.tenant_id, context.task_run_id, context.attempt
        )
        assert (
            len(
                [
                    event
                    for event in detail_after_restart.events
                    if event.event_type == "model.response"
                ]
            )
            == 1
        )

    asyncio.run(scenario())
