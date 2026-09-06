from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import shutil
import subprocess
import time
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from cryptography.fernet import Fernet
from scripts.analyze_prompt_cache import aggregate_observations, observation_from_row
from tests.model_providers.test_handler_integration import MemoryInvocationRepository
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
from amesh.domain.agent_resources import AgentCapabilityPin
from amesh.domain.image_inputs import ImageArtifactRef
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskExecutionFailure
from amesh.model_continuations import ModelContinuationProtector
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


@pytest.mark.skipif(
    not os.getenv("AMESH_CACHE_QUALIFICATION_SESSION") or not os.getenv("OPENROUTER_API_KEY"),
    reason="Paid frozen-scout comparison requires explicit session and provider credentials",
)
def test_live_native_envelope_cache_pairs(
    pi_harness: PiAgentSessionHarness, record_testsuite_property: Any
) -> None:
    """Five matched real-Pi pairs; frozen read-only evidence, encrypted continuation, lab storage.

    Only the first, independent scout seat is replayed. No MCP network calls or production
    writes occur. Frozen public evidence is a lab control, never a fresh consumer result.
    The separate live Vibe E2E remains the consumer acceptance gate.
    """
    session_id = UUID(os.environ["AMESH_CACHE_QUALIFICATION_SESSION"])
    query = f"""
        SELECT jsonb_build_object(
          'pin', jsonb_build_object('pinId', p.pin_id, 'tenantId', 'default',
            'namespace', p.namespace_name, 'subjectRef', p.subject_ref,
            'envelopeDigest', p.envelope_digest, 'envelope', p.envelope,
            'createdBy', p.created_by, 'createdAt', p.created_at),
          'task', f.canonical_definition->'tasks'->0,
          'inputMessage', s.checkpoint->'messages'->1,
          'messages', s.checkpoint->'messages',
          'plan', s.checkpoint->'toolPlan')
        FROM agent_sessions s JOIN agent_capability_pins p ON p.pin_id=s.capability_pin_id
        JOIN executions e ON e.id=s.execution_id
        JOIN flow_revisions f ON f.id=e.flow_revision_id
        WHERE s.session_id='{session_id}' AND s.state='SUCCEEDED'
    """
    source = json.loads(
        subprocess.run(
            [
                "docker",
                "exec",
                "amesh-postgres-1",
                "psql",
                "-U",
                "amesh",
                "-d",
                "amesh",
                "-At",
                "-c",
                query,
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
    )
    pin = AgentCapabilityPin.model_validate(source["pin"])
    assert pin.envelope.agent.key == source["task"]["id"] == "universe-scout"
    assert not source["task"]["dependsOn"]
    assert all(tool.impact.value == "READ_ONLY" for tool in pin.envelope.tools)
    frozen_results = [
        json.loads(message["content"])["result"]
        for message in source["messages"]
        if message["role"] == "tool" and "result" in json.loads(message["content"])
    ]
    occurrences = source["plan"]["occurrences"]
    assert len(frozen_results) == len(occurrences) == 12
    fixture_digest = hashlib.sha256(
        json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    observations: dict[str, list[Any]] = {"NATIVE_V2": [], "NATIVE_V3": []}
    accepted = {"NATIVE_V2": 0, "NATIVE_V3": 0}

    class FrozenMcp:
        calls = 0

        async def __call__(
            self, task: TaskDefinition, context: TaskExecutionContext
        ) -> TaskCompletion:
            del context
            document = task.configuration.handler_view()
            expected = occurrences[self.calls]
            assert document["tool"] == expected["toolName"]
            assert document["arguments"] == expected["arguments"]
            output = frozen_results[self.calls]
            self.calls += 1
            return TaskCompletion(output=output)

    async def run_session(protocol: str, pair: int) -> None:
        repository = MemoryInvocationRepository()
        model = agent_llm_handler(
            repository=repository,
            continuation_protector=ModelContinuationProtector(
                primary_key_id="qualification",
                keys={"qualification": Fernet.generate_key().decode("ascii")},
            ),
        )

        async def measured_model(
            task: TaskDefinition, context: TaskExecutionContext
        ) -> TaskCompletion:
            started = datetime.now(UTC)
            clock_start = time.monotonic()
            output: dict[str, Any] = {}
            state = "FAILED"
            try:
                completed = await model(task, context)
                output = completed.output
                state = "SUCCEEDED"
                return completed
            except TaskExecutionFailure as exc:
                output = exc.result if isinstance(exc.result, dict) else {}
                raise
            finally:
                usage = output.get("usageNormalized") or {}
                cache = usage.get("promptCache") or {}
                cost = output.get("costNormalized") or {}
                document = task.configuration.handler_view()
                key = document["invocationKey"]
                observation = observation_from_row(
                    {
                        "started_at": started,
                        "invocation_state": state,
                        "namespace": pin.namespace,
                        "model": document["model"],
                        "adapter": "openai-compatible",
                        "harness_adapter": "pi-agent-core",
                        "turn": key,
                        "attempt": 1,
                        "phase": "finalization" if ":phase:finalization:" in key else "research",
                        "continuation_present": bool(document.get("continuationSources")),
                        "cache_state": cache.get("state"),
                        "input_tokens": usage.get("inputTokens"),
                        "read_tokens": cache.get("readTokens"),
                        "write_tokens": cache.get("writeTokens"),
                        "output_tokens": usage.get("outputTokens"),
                        "normalized_cost_usd": cost.get("amountUsd"),
                        "normalized_cost_state": cost.get("state"),
                        "latency_seconds": time.monotonic() - clock_start,
                    }
                )
                observations[protocol].append(observation)
                print(
                    json.dumps(
                        {
                            "pair": pair,
                            "protocol": protocol,
                            "turn": observation.turn,
                            "phase": observation.phase,
                            "state": state,
                            "input": observation.input_tokens,
                            "read": observation.read_tokens,
                            "output": observation.output_tokens,
                            "cost": observation.normalized_cost_usd,
                        }
                    ),
                    flush=True,
                )

        sessions = MemorySessions()
        mcp = FrozenMcp()
        document = {
            **source["task"],
            "agent": "helper",
            "interactionProtocol": protocol,
            "input": json.JSONDecoder().raw_decode(source["inputMessage"]["content"])[0]["input"],
        }
        task = TaskDefinition.model_validate(document)
        context = replace(
            _context(),
            namespace=pin.namespace,
            secrets={
                "openrouter-api-key": os.environ["OPENROUTER_API_KEY"],
                "stock-data-mcp-token": "unused",
            },
            secret_scopes=("openrouter-api-key", "stock-data-mcp-token"),
        )
        handler = agent_session_handler(
            resources=MemoryResources(pin),
            sessions=sessions,
            model_handler=measured_model,
            mcp_handler=mcp,
            harness=pi_harness,
        )
        completed = await handler(task, context)
        assert mcp.calls == len(occurrences)
        detail = await sessions.get_session(context.tenant_id, context.task_run_id, context.attempt)
        assert detail.session.state.value == "SUCCEEDED"
        assert len(repository.continuations) > 0
        call_count = len(observations[protocol])
        assert (await handler(task, context)).output == completed.output
        assert len(observations[protocol]) == call_count
        accepted[protocol] += 1

    async def scenario() -> None:
        try:
            for pair in range(1, 6):
                order = ("NATIVE_V2", "NATIVE_V3") if pair % 2 else ("NATIVE_V3", "NATIVE_V2")
                for protocol in order:
                    await run_session(protocol, pair)
        finally:
            report = {
                "fixtureSha256": fixture_digest,
                "sourceSession": str(session_id),
                "storage": "in-memory reducer and encrypted invocation repository",
                "acceptance": "lab business-schema result; not Vibe consumer acceptance",
                "protocols": {
                    protocol: aggregate_observations(rows, accepted_results=accepted[protocol])
                    for protocol, rows in observations.items()
                },
            }
            record_testsuite_property("native_envelope_cache_pairs", json.dumps(report))
            print(json.dumps(report), flush=True)

    asyncio.run(scenario())
