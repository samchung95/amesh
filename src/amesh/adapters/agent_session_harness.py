from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import json
import os
from contextlib import suppress
from time import time
from typing import Any

from amesh.domain import (
    AgentContextReceipt,
    FailureCategory,
    InputModality,
    canonical_json,
    create_harness_context_receipt,
)
from amesh.domain.agent_progress import AgentProgressFrame, AgentPublicSummaryDetail
from amesh.executor import TaskExecutionFailure
from amesh.ports.agent_progress import AgentProgressContext, AgentProgressSink
from amesh.ports.agent_session_harness import (
    AgentHarnessContextSelection,
    AgentSessionHarnessRequest,
    AgentSessionHarnessResult,
    AgentSessionModelGateway,
)

PI_WORKER_PROTOCOL = "amesh.pi-worker/v2"
PI_ADAPTER = "pi-agent-core"
PI_ADAPTER_VERSION = "0.84.3"
_PI_WORKER_PROTOCOL = PI_WORKER_PROTOCOL
_PI_ADAPTER_VERSION = PI_ADAPTER_VERSION
_PI_COMPLETION_ACK = "AMESH model completion acknowledged by parent"


class PiAgentSessionHarness:
    """Runs one authorized AMESH turn through the isolated Pi Agent worker."""

    def __init__(
        self,
        worker_command: tuple[str, ...],
        *,
        max_frame_bytes: int = 1_048_576,
    ) -> None:
        if not worker_command:
            raise ValueError("Pi worker command cannot be empty")
        if max_frame_bytes < 1:
            raise ValueError("Pi worker frame limit must be positive")
        self._worker_command = worker_command
        self._max_frame_bytes = max_frame_bytes

    @property
    def adapter_id(self) -> str:
        return PI_ADAPTER

    @property
    def adapter_version(self) -> str:
        return PI_ADAPTER_VERSION

    @property
    def protocol(self) -> str:
        return PI_WORKER_PROTOCOL

    @property
    def input_modalities(self) -> frozenset[InputModality]:
        return frozenset({InputModality.TEXT, InputModality.IMAGE})

    async def next_action(
        self,
        request: AgentSessionHarnessRequest,
        *,
        model_gateway: AgentSessionModelGateway,
        progress_sink: AgentProgressSink | None = None,
        progress_context: AgentProgressContext | None = None,
    ) -> AgentSessionHarnessResult:
        if (progress_sink is None) != (progress_context is None):
            raise ValueError("Pi progress sink and context must be supplied together")
        try:
            process = await asyncio.create_subprocess_exec(
                *self._worker_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=self._max_frame_bytes,
                env=_pi_worker_environment(),
            )
        except OSError as exc:
            raise TaskExecutionFailure(
                "Pi agent-session worker could not be started",
                FailureCategory.INFRASTRUCTURE,
            ) from exc

        stderr_task = asyncio.create_task(_drain_stream(process.stderr, self._max_frame_bytes))
        model_output: dict[str, Any] | None = None
        context_receipt: AgentContextReceipt | None = None
        context_chunks: dict[int, bytes] = {}
        context_chunk_count: int | None = None
        run_id = f"{request.session_id}:{request.turn}:{request.model_call.route_id}"
        handshake_complete = False
        try:
            async with asyncio.timeout(request.model_call.timeout_seconds):
                transcript = canonical_json(list(request.model_call.messages))
                run_start: dict[str, Any] = {
                    "type": "run.start",
                    "protocol": _PI_WORKER_PROTOCOL,
                    "runId": run_id,
                    "sessionId": str(request.session_id),
                    "turn": request.turn,
                    "model": {
                        "id": request.model_call.model,
                        "name": request.model_call.model,
                        "maxTokens": request.model_call.max_completion_tokens,
                        "contextWindow": request.context_budget.context_window_tokens,
                        "input": sorted(
                            modality.value for modality in request.model_call.input_modalities
                        ),
                    },
                    "contextBudget": request.context_budget.model_dump(
                        mode="json",
                        by_alias=True,
                    ),
                    "tools": [],
                    **(
                        {"progressContext": progress_context.model_dump(mode="json", by_alias=True)}
                        if progress_context is not None
                        else {}
                    ),
                }
                if len(transcript) <= self._max_frame_bytes // 2:
                    run_start["messages"] = list(request.model_call.messages)
                else:
                    chunk_size = max(1, self._max_frame_bytes // 2)
                    chunks = tuple(
                        transcript[offset : offset + chunk_size]
                        for offset in range(0, len(transcript), chunk_size)
                    )
                    transcript_digest = hashlib.sha256(transcript).hexdigest()
                    for index, chunk in enumerate(chunks):
                        await _write_frame(
                            process,
                            {
                                "type": "transcript.chunk",
                                "protocol": _PI_WORKER_PROTOCOL,
                                "runId": run_id,
                                "index": index,
                                "count": len(chunks),
                                "data": base64.b64encode(chunk).decode("ascii"),
                            },
                            maximum_bytes=self._max_frame_bytes,
                        )
                    run_start["transcript"] = {
                        "encoding": "base64-json-chunks",
                        "count": len(chunks),
                        "bytes": len(transcript),
                        "sha256": transcript_digest,
                    }
                await _write_frame(
                    process,
                    run_start,
                    maximum_bytes=self._max_frame_bytes,
                )
                while True:
                    frame = await _read_frame(process, self._max_frame_bytes)
                    frame_type = frame.get("type")
                    if frame_type == "run.started":
                        if handshake_complete:
                            raise RuntimeError("Pi worker emitted duplicate run.started")
                        if (
                            frame.get("protocol") != _PI_WORKER_PROTOCOL
                            or frame.get("adapterVersion") != _PI_ADAPTER_VERSION
                            or frame.get("runId") != run_id
                        ):
                            raise RuntimeError("Pi worker handshake protocol or version mismatch")
                        handshake_complete = True
                        continue
                    if frame_type == "agent.event":
                        if not handshake_complete or frame.get("runId") != run_id:
                            raise RuntimeError("Pi worker emitted agent event before handshake")
                        continue
                    if frame_type == "progress":
                        if not handshake_complete or frame.get("runId") != run_id:
                            raise RuntimeError("Pi worker emitted progress before handshake")
                        if progress_sink is None or progress_context is None:
                            raise RuntimeError(
                                "Pi worker emitted progress without an injected sink"
                            )
                        if frame.get("protocol") != _PI_WORKER_PROTOCOL:
                            raise RuntimeError("Pi worker progress protocol mismatch")
                        raw_progress = frame.get("frame")
                        if not isinstance(raw_progress, dict):
                            raise RuntimeError("Pi worker progress frame must be an object")
                        progress = AgentProgressFrame.model_validate(raw_progress)
                        if (
                            progress.attempt_session_id != progress_context.attempt_session_id
                            or progress.attempt != progress_context.attempt
                            or progress.turn != request.turn
                        ):
                            raise RuntimeError("Pi worker progress context mismatch")
                        if isinstance(progress.detail, AgentPublicSummaryDetail):
                            raise PermissionError("Pi worker cannot emit provider public summaries")
                        await progress_sink.append(progress_context, progress)
                        continue
                    if frame_type == "context.chunk":
                        if not handshake_complete or frame.get("runId") != run_id:
                            raise RuntimeError("Pi worker emitted context chunk before handshake")
                        if frame.get("protocol") != _PI_WORKER_PROTOCOL:
                            raise RuntimeError("Pi worker context chunk protocol mismatch")
                        chunk_index = frame.get("index")
                        chunk_count = frame.get("count")
                        data = frame.get("data")
                        if (
                            not isinstance(chunk_index, int)
                            or isinstance(chunk_index, bool)
                            or not isinstance(chunk_count, int)
                            or isinstance(chunk_count, bool)
                            or chunk_index < 0
                            or chunk_count < 1
                            or chunk_index >= chunk_count
                            or not isinstance(data, str)
                        ):
                            raise RuntimeError("Pi worker context chunk metadata is invalid")
                        if (
                            context_chunk_count not in {None, chunk_count}
                            or chunk_index in context_chunks
                        ):
                            raise RuntimeError(
                                "Pi worker context chunks are inconsistent or duplicated"
                            )
                        try:
                            context_chunks[chunk_index] = base64.b64decode(data, validate=True)
                        except (ValueError, binascii.Error) as exc:
                            raise RuntimeError(
                                "Pi worker context chunk is not valid base64"
                            ) from exc
                        context_chunk_count = chunk_count
                        continue
                    if frame_type == "tool.request":
                        if not handshake_complete or frame.get("runId") != run_id:
                            raise RuntimeError("Pi worker emitted tool request before handshake")
                        raise PermissionError(
                            "Pi turn adapter requested a native tool outside AMESH dispatch"
                        )
                    if frame_type == "model.request":
                        if not handshake_complete or frame.get("runId") != run_id:
                            raise RuntimeError("Pi worker emitted model request before handshake")
                        if frame.get("protocol") != _PI_WORKER_PROTOCOL:
                            raise RuntimeError("Pi worker model request protocol mismatch")
                        if model_output is not None:
                            raise RuntimeError("Pi turn adapter requested more than one model call")
                        request_id = frame.get("requestId")
                        if not isinstance(request_id, str) or not request_id:
                            raise RuntimeError("Pi worker model request omitted requestId")
                        selected_messages = _selected_messages(
                            frame,
                            chunks=context_chunks,
                            chunk_count=context_chunk_count,
                        )
                        projection = frame.get("contextProjection")
                        if not isinstance(projection, dict):
                            raise RuntimeError("Pi worker model request omitted contextProjection")
                        retained_indexes = _source_indexes(
                            projection.get("retainedSourceIndexes"),
                            name="retainedSourceIndexes",
                        )
                        omitted_indexes = _source_indexes(
                            projection.get("omittedSourceIndexes"),
                            name="omittedSourceIndexes",
                        )
                        algorithm = projection.get("algorithm")
                        if not isinstance(algorithm, str) or not algorithm:
                            raise RuntimeError("Pi worker context projection omitted algorithm")
                        context_receipt = create_harness_context_receipt(
                            request.model_call.messages,
                            selected_messages,
                            request.context_budget,
                            turn=request.turn,
                            algorithm=algorithm,
                            harness_adapter=PI_ADAPTER,
                            harness_version=PI_ADAPTER_VERSION,
                            retained_source_indexes=retained_indexes,
                            omitted_source_indexes=omitted_indexes,
                        )
                        model_output = await model_gateway.invoke(
                            request.model_call,
                            context_selection=AgentHarnessContextSelection(
                                messages=selected_messages,
                                receipt=context_receipt,
                            ),
                        )
                        await _write_pi_model_result(
                            process,
                            request_id=request_id,
                            model=request.model_call.model,
                            output=model_output,
                            maximum_bytes=self._max_frame_bytes,
                        )
                        continue
                    if frame_type == "run.result":
                        if not handshake_complete or frame.get("runId") != run_id:
                            raise RuntimeError("Pi worker completed before a valid handshake")
                        if model_output is None:
                            raise RuntimeError("Pi worker completed without an AMESH model call")
                        if context_receipt is None:
                            raise RuntimeError("Pi worker completed without a context receipt")
                        return AgentSessionHarnessResult(
                            adapter=PI_ADAPTER,
                            adapterVersion=_PI_ADAPTER_VERSION,
                            modelOutput=model_output,
                            contextReceipt=context_receipt,
                            metadata={
                                "modelGateway": "amesh",
                                "routeId": request.model_call.route_id,
                                "workerProtocol": _PI_WORKER_PROTOCOL,
                            },
                        )
                    raise RuntimeError(f"Pi worker emitted unexpected frame {frame_type!r}")
        except TimeoutError as exc:
            raise TaskExecutionFailure(
                "Pi agent-session worker timed out",
                FailureCategory.TIMED_OUT,
            ) from exc
        finally:
            await _stop_process(process)
            with suppress(asyncio.CancelledError, ValueError):
                await stderr_task


def _selected_messages(
    frame: dict[str, Any],
    *,
    chunks: dict[int, bytes],
    chunk_count: int | None,
) -> tuple[dict[str, Any], ...]:
    raw_messages = frame.get("selectedMessages")
    if raw_messages is None:
        descriptor = frame.get("selectedTranscript")
        if (
            not isinstance(descriptor, dict)
            or descriptor.get("encoding") != "base64-json-chunks"
            or not isinstance(chunk_count, int)
            or descriptor.get("count") != chunk_count
            or len(chunks) != chunk_count
        ):
            raise RuntimeError("Pi worker selected context chunks are incomplete")
        payload = b"".join(chunks[index] for index in range(chunk_count))
        digest = hashlib.sha256(payload).hexdigest()
        if descriptor.get("bytes") != len(payload) or descriptor.get("sha256") != digest:
            raise RuntimeError("Pi worker selected context chunk digest mismatch")
        try:
            raw_messages = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Pi worker selected context is invalid JSON") from exc
    if not isinstance(raw_messages, list) or not raw_messages:
        raise RuntimeError("Pi worker model request omitted selectedMessages")
    if not all(isinstance(message, dict) for message in raw_messages):
        raise RuntimeError("Pi worker selectedMessages must contain objects")
    return tuple(raw_messages)


def _source_indexes(value: Any, *, name: str) -> tuple[int, ...]:
    if not isinstance(value, list) or not all(
        isinstance(index, int) and not isinstance(index, bool) and index >= 0 for index in value
    ):
        raise RuntimeError(f"Pi worker {name} must be a list of non-negative integers")
    return tuple(value)


async def _write_pi_model_result(
    process: asyncio.subprocess.Process,
    *,
    request_id: str,
    model: str,
    output: dict[str, Any],
    maximum_bytes: int,
) -> None:
    usage = _pi_usage(output)
    message = {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": _PI_COMPLETION_ACK,
            }
        ],
        "api": "amesh",
        "provider": "amesh",
        "model": model,
        "usage": usage,
        "stopReason": "stop",
        "timestamp": int(time() * 1000),
    }
    partial = {**message, "content": []}
    await _write_frame(
        process,
        {
            "type": "model.event",
            "requestId": request_id,
            "event": {"type": "start", "partial": partial},
        },
        maximum_bytes=maximum_bytes,
    )
    await _write_frame(
        process,
        {
            "type": "model.event",
            "requestId": request_id,
            "event": {"type": "done", "reason": "stop", "message": message},
        },
        maximum_bytes=maximum_bytes,
    )


def _pi_usage(output: dict[str, Any]) -> dict[str, int]:
    normalized = output.get("usageNormalized")
    raw = output.get("usage")
    normalized_usage = normalized if isinstance(normalized, dict) else {}
    raw_usage = raw if isinstance(raw, dict) else {}
    raw_prompt_details = raw_usage.get("prompt_tokens_details")
    prompt_details = raw_prompt_details if isinstance(raw_prompt_details, dict) else {}
    normalized_prompt_cache = normalized_usage.get("promptCache")
    prompt_cache = normalized_prompt_cache if isinstance(normalized_prompt_cache, dict) else {}
    input_tokens = _usage_int(normalized_usage, raw_usage, "inputTokens", "prompt_tokens")
    output_tokens = _usage_int(
        normalized_usage,
        raw_usage,
        "outputTokens",
        "completion_tokens",
    )
    total_tokens = _usage_int(normalized_usage, raw_usage, "totalTokens", "total_tokens")
    if total_tokens == 0:
        total_tokens = input_tokens + output_tokens
    cache_read_tokens = _usage_int(
        prompt_cache,
        prompt_details,
        "readTokens",
        "cached_tokens",
    )
    cache_write_tokens = _usage_int(
        prompt_cache,
        prompt_details,
        "writeTokens",
        "cache_write_tokens",
    )
    return {
        "input": input_tokens,
        "output": output_tokens,
        "cacheRead": cache_read_tokens,
        "cacheWrite": cache_write_tokens,
        "totalTokens": total_tokens,
    }


def _usage_int(
    normalized: dict[str, Any],
    raw: dict[str, Any],
    normalized_key: str,
    raw_key: str,
) -> int:
    value = normalized.get(normalized_key, raw.get(raw_key, 0))
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


async def _write_frame(
    process: asyncio.subprocess.Process,
    frame: dict[str, Any],
    *,
    maximum_bytes: int,
) -> None:
    if process.stdin is None:
        raise RuntimeError("Pi worker stdin is unavailable")
    encoded = json.dumps(frame, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(encoded) + 1 > maximum_bytes:
        raise RuntimeError("Pi worker control frame exceeded the configured limit")
    process.stdin.write(encoded + b"\n")
    try:
        await process.stdin.drain()
    except (BrokenPipeError, ConnectionResetError) as exc:
        raise TaskExecutionFailure(
            "Pi agent-session worker exited while receiving a frame",
            FailureCategory.INFRASTRUCTURE,
        ) from exc


async def _read_frame(
    process: asyncio.subprocess.Process,
    maximum_bytes: int,
) -> dict[str, Any]:
    if process.stdout is None:
        raise RuntimeError("Pi worker stdout is unavailable")
    try:
        line = await process.stdout.readline()
    except ValueError as exc:
        raise RuntimeError("Pi worker frame exceeded the configured limit") from exc
    if not line:
        raise TaskExecutionFailure(
            "Pi agent-session worker exited unexpectedly",
            FailureCategory.INFRASTRUCTURE,
        )
    if len(line) > maximum_bytes:
        raise RuntimeError("Pi worker frame exceeded the configured limit")
    try:
        frame = json.loads(line)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Pi worker emitted invalid JSON") from exc
    if not isinstance(frame, dict):
        raise RuntimeError("Pi worker emitted a non-object frame")
    return frame


async def _drain_stream(
    stream: asyncio.StreamReader | None,
    maximum_bytes: int,
) -> None:
    if stream is None:
        return
    consumed = 0
    while chunk := await stream.read(4096):
        consumed += len(chunk)
        if consumed > maximum_bytes:
            raise ValueError("Pi worker stderr exceeded the configured limit")


async def _stop_process(process: asyncio.subprocess.Process) -> None:
    if process.stdin is not None:
        process.stdin.close()
        with suppress(BrokenPipeError, ConnectionResetError):
            await process.stdin.wait_closed()
    if process.returncode is not None:
        return
    with suppress(ProcessLookupError):
        process.terminate()
    try:
        async with asyncio.timeout(2):
            await process.wait()
    except TimeoutError:
        process.kill()
        await process.wait()


def _pi_worker_environment() -> dict[str, str]:
    allowed = {
        "COMSPEC",
        "LANG",
        "LC_ALL",
        "PATH",
        "PATHEXT",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "TMPDIR",
        "TZ",
        "WINDIR",
    }
    return {key: value for key, value in os.environ.items() if key.upper() in allowed}
