"""Provider-free load and soak qualification for the agent-session runtime.

``stub`` serves an OpenAI-compatible chat-completions endpoint that finishes every session turn
with the output ``{"answer": "<nonce>"}``, where the nonce is the first ``nonce-<hex>`` token in
the prompt.
``run`` launches sessions through the public API against a deployment whose model policy points
at the stub, waits for each to finish and verifies that every session returned its own nonce.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import re
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4

NONCE = re.compile(r"nonce-[0-9a-f]{32}")
TERMINAL = {"SUCCEEDED", "FAILED"}
AGENT_KEY = "echo"
MODEL_SECRET = "qualification-model-key"


def stub_reply(body: dict[str, object]) -> tuple[str, dict[str, int]]:
    text = json.dumps(body.get("messages", []))
    match = NONCE.search(text)
    # The session harness asks for this action envelope (amesh.tasks.session._action_schema).
    content = json.dumps(
        {
            "action": "final",
            "tool": "none",
            "arguments": None,
            "output": {"answer": match.group(0) if match else "no-nonce"},
            "rationale": "qualification stub",
        }
    )
    prompt_tokens = max(1, len(text) // 4)
    return content, {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": 12,
        "total_tokens": prompt_tokens + 12,
        # Session budgets require a reported cost; the stub is free.
        "cost": 0,
    }


class StubHandler(BaseHTTPRequestHandler):
    delay_seconds = 0.0
    log_requests = 0
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        length = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")
        if StubHandler.log_requests > 0:
            StubHandler.log_requests -= 1
            print(json.dumps(body)[:4000], file=sys.stderr, flush=True)
        if self.delay_seconds:
            time.sleep(self.delay_seconds)
        content, usage = stub_reply(body)
        model = str(body.get("model", "stub"))
        base = {"id": "stub", "created": int(time.time()), "model": model}
        if not body.get("stream"):
            payload = {
                **base,
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": usage,
            }
            self._send(200, "application/json", json.dumps(payload).encode())
            return
        chunks: list[dict[str, Any]] = [
            {"choices": [{"index": 0, "delta": {"role": "assistant", "content": content}}]},
            {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
            {"choices": [], "usage": usage},
        ]
        stream = "".join(
            f"data: {json.dumps({**base, 'object': 'chat.completion.chunk', **chunk})}\n\n"
            for chunk in chunks
        )
        self._send(200, "text/event-stream", (stream + "data: [DONE]\n\n").encode())

    def _send(self, status: int, content_type: str, data: bytes) -> None:
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        return


def run_stub(args: argparse.Namespace) -> int:
    StubHandler.delay_seconds = args.delay_ms / 1000
    StubHandler.log_requests = args.log_requests
    server = ThreadingHTTPServer(("0.0.0.0", args.port), StubHandler)
    print(f"model stub listening on :{args.port}", flush=True)
    server.serve_forever()
    return 0


@dataclass
class Launched:
    session_id: str
    nonce: str
    submitted: float
    state: str = "PENDING"
    finished: float | None = None
    server_seconds: float | None = None
    error: str | None = None
    execution_id: str | None = None
    task_run_id: str | None = None


def percentiles(values: list[float]) -> dict[str, float | None]:
    ordered = sorted(values)

    def at(fraction: float) -> float | None:
        if not ordered:
            return None
        return round(ordered[min(len(ordered) - 1, int(fraction * len(ordered)))], 4)

    return {"p50": at(0.50), "p95": at(0.95), "p99": at(0.99), "max": at(1.0)}


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


async def ensure_agent(client: Any, namespace: str, model_endpoint: str) -> None:
    """Create the secret binding, stub model policy and echo agent once per namespace."""

    resources = f"/api/v1/namespaces/{namespace}/agent/resources"
    existing = await client.get(f"{resources}/AGENT/{AGENT_KEY}")
    if existing.status_code == 200:
        return
    for response in (
        await client.put(
            f"/api/v1/namespaces/{namespace}/secret-bindings/{MODEL_SECRET}",
            json={"providerReference": "QUALIFICATION_MODEL_KEY"},
        ),
        await client.post(
            resources,
            json={
                "kind": "MODEL_POLICY",
                "key": "stub",
                "namespace": namespace,
                "title": "Qualification model stub",
                "routes": [
                    {
                        "routeId": "primary",
                        "provider": {
                            "adapter": "openai-compatible",
                            "endpoint": model_endpoint,
                            "credentialRef": MODEL_SECRET,
                        },
                        # A catalogued model name so context limits resolve; the stub ignores it.
                        "model": "openai/gpt-5.6-luna",
                    }
                ],
                "fallbackMode": "DISABLED",
                "outputNondeterminismDisclosure": "The stub is deterministic.",
            },
        ),
        await client.post(
            resources,
            json={
                "kind": "AGENT",
                "key": AGENT_KEY,
                "namespace": namespace,
                "title": "Nonce echo",
                "instructions": "Return the nonce from the input as the answer.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"nonce": {"type": "string"}},
                    "required": ["nonce"],
                },
                "outputSchema": {
                    "type": "object",
                    "properties": {"answer": {"type": "string"}},
                    "required": ["answer"],
                },
                "modelPolicy": {"key": "stub", "revision": 1},
                "memoryPolicy": {"scope": "NONE"},
                "permissions": {
                    "secretScopes": [MODEL_SECRET],
                    "networkHosts": [model_endpoint.split("/")[2].split(":")[0]],
                },
                "hardLimits": {
                    "maxTotalTokens": 8000,
                    "maxCostUsd": "0.10",
                    "maxDurationSeconds": 120,
                    "maxToolCalls": 0,
                    "maxTurns": 3,
                    "maxLoopIterations": 0,
                    "maxRecursionDepth": 0,
                    # Also the admission ceiling per agent, actor and provider: above --concurrency
                    # so the driver measures the runtime, not a one-at-a-time session queue.
                    "maxConcurrency": 64,
                },
                "evaluationPolicy": {"requiredEvaluations": ["schema"], "evaluations": []},
            },
        ),
    ):
        if response.status_code >= 300:
            raise RuntimeError(f"setup failed: {response.status_code} {response.text[:500]}")


def server_seconds(session: dict[str, Any]) -> float | None:
    created, completed = session.get("createdAt"), session.get("completedAt")
    if not created or not completed:
        return None
    return (datetime.fromisoformat(completed) - datetime.fromisoformat(created)).total_seconds()


def judge(item: Launched, session: dict[str, Any]) -> None:
    item.state = str(session.get("state"))
    item.server_seconds = server_seconds(session)
    item.execution_id, item.task_run_id = session.get("executionId"), session.get("taskRunId")
    result = session.get("result") or {}
    runs = (session.get("attempt", 1), session.get("executionEpoch", 1))
    if item.state == "SUCCEEDED" and result.get("answer") != item.nonce:
        item.state = "MISMATCHED"
        item.error = f"answer {result.get('answer')!r} != {item.nonce!r}"
    elif item.state == "SUCCEEDED" and runs != (1, 1):
        # Nothing is injected, so a retried or recovered run means the runtime lost an owner.
        item.state = "RETRIED"
        item.error = f"attempt {runs[0]}, execution epoch {runs[1]}"
    elif item.state == "FAILED":
        item.error = str(session.get("error"))[:300]


def mark_shared_runs(items: list[Launched]) -> None:
    """Each session must own exactly one execution and one task run."""
    owners: dict[str, list[Launched]] = {}
    for item in items:
        for run in (item.execution_id, item.task_run_id):
            if run:
                owners.setdefault(run, []).append(item)
    for run, sharing in owners.items():
        if len(sharing) > 1:
            for item in sharing:
                item.state, item.error = "DUPLICATED", f"{run} is shared by {len(sharing)} sessions"


async def run_load(args: argparse.Namespace) -> int:
    import httpx

    headers = {"Authorization": f"Bearer {args.token}", "X-Amesh-Tenant": args.tenant}
    limits = httpx.Limits(max_connections=args.concurrency + 20)
    started_at = datetime.now(UTC)
    began = time.monotonic()
    launched: list[Launched] = []
    create_seconds: list[float] = []
    create_errors: dict[str, int] = {}
    read_errors: dict[str, int] = {}
    stop_launching = asyncio.Event()
    launch_seconds: list[float] = []

    async with httpx.AsyncClient(
        base_url=args.api_url, headers=headers, timeout=60, limits=limits
    ) as client:
        await ensure_agent(client, args.namespace, args.model_endpoint)
        ready = (await client.get("/ready")).json()

        def snapshot(final: bool) -> dict[str, Any]:
            elapsed = time.monotonic() - began
            window = launch_seconds[0] if launch_seconds else elapsed
            states: dict[str, int] = {}
            for item in launched:
                states[item.state] = states.get(item.state, 0) + 1
            done = [item for item in launched if item.finished is not None]
            failures = [
                {"sessionId": item.session_id, "state": item.state, "error": item.error}
                for item in launched
                if item.state in {"FAILED", "MISMATCHED", "RETRIED", "DUPLICATED", "LOST"}
            ]
            passed = (
                final
                and not failures
                and not create_errors
                and not read_errors
                and elapsed >= args.duration_seconds
                and states.get("SUCCEEDED", 0) == len(launched) > 0
            )
            return {
                "profile": "session-runtime-provider-free-v1",
                "status": "PASSED" if passed else ("FAILED" if final else "RUNNING"),
                "startedAt": started_at.isoformat(),
                "updatedAt": datetime.now(UTC).isoformat(),
                "elapsedSeconds": round(elapsed, 1),
                "configuration": {
                    "apiUrl": args.api_url,
                    "targetRatePerSecond": args.rate,
                    "durationSeconds": args.duration_seconds,
                    "maxInFlight": args.concurrency,
                    "stubDelayMs": args.stub_delay_ms,
                    "revision": args.revision,
                },
                "environment": {
                    "client": platform.platform(),
                    "clientCpus": os.cpu_count(),
                    "serverVersion": ready.get("version"),
                    "serverRoles": ready.get("roles"),
                    "migration": ready.get("latest_migration"),
                },
                "sessions": {
                    "launched": len(launched),
                    "states": states,
                    "achievedStartsPerSecond": round(len(launched) / window, 3) if window else 0,
                    "createErrors": create_errors,
                    "readErrors": read_errors,
                    "verifiedOnFinalPass": sum(1 for item in launched if item.state == "SUCCEEDED")
                    if final
                    else None,
                },
                "latencySeconds": {
                    "create": percentiles(create_seconds),
                    "clientCompletion": percentiles(
                        [item.finished - item.submitted for item in done if item.finished]
                    ),
                    "serverCompletion": percentiles(
                        [item.server_seconds for item in done if item.server_seconds is not None]
                    ),
                },
                "failures": failures[:50],
            }

        async def launch_one() -> None:
            nonce = f"nonce-{uuid4().hex}"
            sent = time.monotonic()
            try:
                response = await client.post(
                    "/api/v1/agent-sessions",
                    headers={"Idempotency-Key": nonce, "Prefer": "respond-async"},
                    json={
                        "namespace": args.namespace,
                        "agent": AGENT_KEY,
                        "agentRevision": 1,
                        "input": {"nonce": nonce},
                        "invalidOutputPolicy": "FAIL",
                        "maxRepairAttempts": 0,
                        "dataHandling": "DENY_SECRETS",
                        "memoryReadKeys": [],
                        "runner": "local",
                    },
                )
            except httpx.HTTPError as exc:
                key = type(exc).__name__
                create_errors[key] = create_errors.get(key, 0) + 1
                return
            create_seconds.append(time.monotonic() - sent)
            if response.status_code not in (200, 201, 202):
                key = str(response.status_code)
                create_errors[key] = create_errors.get(key, 0) + 1
                return
            launched.append(Launched(response.json()["sessionId"], nonce, sent))

        async def launcher() -> None:
            pending: set[asyncio.Task[None]] = set()
            interval = 1 / args.rate
            next_at = time.monotonic()
            while time.monotonic() - began < args.duration_seconds:
                if args.sessions and len(launched) + len(pending) >= args.sessions:
                    break
                in_flight = sum(1 for item in launched if item.finished is None) + len(pending)
                if in_flight < args.concurrency:
                    task = asyncio.create_task(launch_one())
                    pending.add(task)
                    task.add_done_callback(pending.discard)
                next_at += interval
                await asyncio.sleep(max(0.0, next_at - time.monotonic()))
            await asyncio.gather(*pending)
            launch_seconds.append(time.monotonic() - began)
            stop_launching.set()

        async def check(item: Launched) -> None:
            response = await client.get(f"/api/v1/agent-sessions/{item.session_id}")
            if response.status_code != 200:
                key = str(response.status_code)
                read_errors[key] = read_errors.get(key, 0) + 1
                return
            session = response.json().get("session")
            if session and session.get("state") in TERMINAL:
                judge(item, session)
                item.finished = time.monotonic()

        async def poller() -> None:
            gate = asyncio.Semaphore(32)

            async def bounded(item: Launched) -> None:
                async with gate:
                    try:
                        await check(item)
                    except httpx.HTTPError as exc:
                        key = type(exc).__name__
                        read_errors[key] = read_errors.get(key, 0) + 1

            drain_deadline: float | None = None
            last_report = 0.0
            while True:
                active = [item for item in launched if item.finished is None]
                await asyncio.gather(*(bounded(item) for item in active))
                if time.monotonic() - last_report >= args.report_every:
                    write_report(args.report, snapshot(final=False))
                    last_report = time.monotonic()
                if stop_launching.is_set():
                    if not any(item.finished is None for item in launched):
                        return
                    drain_deadline = drain_deadline or time.monotonic() + args.drain_seconds
                    if time.monotonic() > drain_deadline:
                        for item in launched:
                            if item.finished is None:
                                item.state, item.error = "LOST", "not terminal after drain"
                        return
                await asyncio.sleep(args.poll_interval)

        await asyncio.gather(launcher(), poller())

        # Independent final pass: re-read every session and re-check its state and output.
        gate = asyncio.Semaphore(32)

        async def verify(item: Launched) -> None:
            if item.state == "LOST":
                return
            try:
                async with gate:
                    response = await client.get(f"/api/v1/agent-sessions/{item.session_id}")
            except httpx.HTTPError as exc:
                item.state, item.error = "LOST", f"final read failed: {type(exc).__name__}"
                return
            session = response.json().get("session") if response.status_code == 200 else None
            if session is None:
                item.state, item.error = "LOST", f"final read returned {response.status_code}"
                return
            judge(item, session)

        await asyncio.gather(*(verify(item) for item in launched))
        mark_shared_runs(launched)
        report = snapshot(final=True)
        write_report(args.report, report)
    print(json.dumps({key: report[key] for key in ("status", "sessions", "latencySeconds")}))
    return 0 if report["status"] == "PASSED" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    stub = commands.add_parser("stub", help="Serve the OpenAI-compatible model stub")
    stub.add_argument("--port", type=int, default=8090)
    stub.add_argument("--delay-ms", type=float, default=0)
    stub.add_argument("--log-requests", type=int, default=0)
    run = commands.add_parser("run", help="Launch sessions and verify every result")
    run.add_argument("--api-url", default="http://127.0.0.1:18611")
    run.add_argument(
        "--token", default=os.environ.get("AMESH_QUALIFICATION_TOKEN", "development-token")
    )
    run.add_argument("--tenant", default="default")
    run.add_argument("--namespace", default="qualification.sessions")
    run.add_argument("--model-endpoint", default="http://model-stub:8090/v1/chat/completions")
    run.add_argument("--rate", type=float, default=1.0, help="target session starts per second")
    run.add_argument("--duration-seconds", type=float, default=60)
    run.add_argument("--sessions", type=int, default=0, help="stop after this many (0: no cap)")
    run.add_argument("--concurrency", type=int, default=50, help="maximum unfinished sessions")
    run.add_argument("--poll-interval", type=float, default=0.5)
    run.add_argument("--drain-seconds", type=float, default=300)
    run.add_argument("--report-every", type=float, default=60)
    run.add_argument("--stub-delay-ms", type=float, default=0, help="recorded in the report")
    run.add_argument("--revision", default="", help="deployed revision, recorded in the report")
    run.add_argument("--report", type=Path, default=Path("data/session-load-report.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "stub":
        return run_stub(args)
    return asyncio.run(run_load(args))


if __name__ == "__main__":
    raise SystemExit(main())
