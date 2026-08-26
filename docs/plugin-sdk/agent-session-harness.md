# Agent-session harness contract

AMESH owns the durable session, provider credentials, model route, tool policy, approvals, budgets,
checkpoints and evidence. A harness is an implementation detail behind the typed
`AgentSessionHarness` port; it is not a second workflow engine or session store.

## Port authority

An adapter implements:

```python
async def next_action(
    request: AgentSessionHarnessRequest,
    *,
    model_gateway: AgentSessionModelGateway,
) -> AgentSessionHarnessResult: ...
```

`request.model_call` is the complete AMESH-authorized call. The adapter must use it unchanged. The
gateway is the only route to a model and receives no provider credential value. The adapter returns
the model output plus its exact adapter name and version; AMESH validates the output and writes the
authoritative session event.

The contract deliberately permits one model call per harness turn. A multi-turn agent session is a
series of durable AMESH turns. Tool proposals, approvals and effects return to AMESH for policy,
dispatch and evidence before the next turn. A harness must not write workflow state, call an MCP
server directly, persist its own authoritative transcript or execute an undeclared tool.

## Pi protocol

The production Pi adapter starts `harnesses/pi/src/worker.mjs` in an isolated process using the
versioned `amesh.pi-worker/v1` JSONL bridge. The parent sends `run.start`; the worker emits
`model.request` and receives `model.event` frames. Parent-mediated tool requests use
`tool.request`/`tool.result`. Completion is `run.result`.

Control frames are bounded and model output may be larger than the control-frame limit. The worker
environment is reduced to non-secret runtime variables, and Pi has no OpenRouter credential. Pi
`0.84.3` and its `pi-ai` companion are pinned in `harnesses/pi/package-lock.json`.

## Registration and fail-closed behavior

Production composition registers Pi explicitly. An unknown or unavailable adapter is a startup or
execution error; AMESH must not silently select a built-in fallback. Adapter choice is fixed for an
execution and cannot change during an active session.

## Conformance and provenance

Run the versioned, provider-free kit locally:

```powershell
uv sync --extra runtime --extra dev --locked
npm ci --prefix harnesses/pi
uv run python scripts/run_agent_harness_conformance.py --adapter pi --output .artifacts/harness-report.json
```

The report records the kit and manifest digest, AMESH source version, adapter and worker protocol
versions, runtime versions, exact package integrity and license metadata, every fixture result and a
canonical report digest. The same inputs must produce byte-identical reports. CI runs the command
twice in one environment, compares the outputs and uploads the report as an artifact.

The production-image probe uses the real Python Pi adapter and a deterministic in-process gateway,
so it never spends provider credits:

```powershell
docker build -t amesh:harness-conformance .
docker run --rm --entrypoint python amesh:harness-conformance -m amesh.harness_probe
```

For a provider-backed local smoke, opt in explicitly with an OpenRouter key. The key remains in the
parent process and is never passed to the worker:

```powershell
$env:OPENROUTER_API_KEY = "..."
uv run pytest -q tests/tasks/test_agent_sessions.py `
  -k test_live_openrouter_luna_session_runs_through_pi
```

The smoke targets `openai/gpt-5.6-luna`, uses the same AMESH gateway and checks the bounded tool,
structured result, cache-evidence and session-event path. Do not make paid-provider credentials a PR
CI requirement.

## Adding another adapter

To evaluate DSH, Goose or another harness:

1. Implement only the `AgentSessionHarness` port in an isolated adapter package.
2. Add an explicit registry entry and adapter/version provenance; unknown names must fail closed.
3. Pass the provider-free conformance kit and authority/failure-injection fixtures unchanged.
4. Add exact dependency, license, runtime and lockfile evidence.
5. Add a local live smoke only when the provider and credentials are intentionally available.

The adapter must not require a change to the public `agent.session` workflow, output, event or
recovery contract.
