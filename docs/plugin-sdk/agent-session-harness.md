# Agent-session harness contract

AMESH owns the durable session, canonical transcript, provider credentials, model route, tool policy,
approvals, budgets, checkpoints and evidence. A harness is an implementation detail behind the typed
`AgentSessionHarness` port; it is not a second workflow engine or authoritative session store.

## Port authority

The conformance manifest identifies this contract as `amesh.agent-session-harness/v2`.

An adapter implements:

```python
async def next_action(
    request: AgentSessionHarnessRequest,
    *,
    model_gateway: AgentSessionModelGateway,
) -> AgentSessionHarnessResult: ...
```

`request.model_call.messages` contains the canonical transcript for the turn, and
`request.context_budget` contains the hard model-input budget calculated by AMESH. The adapter must
not mutate the authorized call. It may select an exact subset of canonical messages for the model,
then pass that projection separately to the only permitted provider route:

```python
await model_gateway.invoke(
    request.model_call,
    context_selection=AgentHarnessContextSelection(
        messages=selected_messages,
        receipt=context_receipt,
    ),
)
```

AMESH verifies the authorized call, selected messages and receipt before provider I/O. The adapter
returns the model output, the verified context receipt, and its exact adapter name and version;
AMESH then writes the authoritative session event.

The contract permits one model call per harness turn. A multi-turn agent session is a series of
durable AMESH turns. Tool proposals, approvals and effects return to AMESH for policy, dispatch and
evidence before the next turn. A harness must not receive provider credentials, write workflow
state, call an MCP server directly, persist its own authoritative transcript or execute an
undeclared tool.

## Context ownership, budget and receipt

The harness owns context projection. AMESH retains the complete canonical transcript and supplies an
`amesh.agent-context-budget/v1` boundary containing:

- the model context window and reserved completion tokens;
- the maximum input and compaction-trigger token estimates;
- request-overhead, message-count and byte limits.

The Pi adapter implements that ownership with Pi's native `transformContext` hook. Its
`pi.transform-context/recent-complete-turns/v1` projection keeps the pinned prefix and newest
complete dialogue group, then removes the oldest complete groups until every supplied limit fits.
Selected messages are an exact subset of the canonical transcript: the harness does not synthesize a
summary or insert a compaction marker.

Every completed turn returns an `amesh.agent-context/v3` receipt. It records the canonical
transcript and selected-context digests, retained and omitted source indexes, message/byte/token
measurements, headroom and compaction state, plus the harness identity and applied budget. AMESH
reconstructs and verifies the receipt against the canonical transcript and calculated budget before
calling the provider. A missing, stale, malformed or over-budget selection fails closed. Older v1
and v2 receipts remain readable as persisted history, but new harness executions must produce v3.

## Pi worker protocol v2

The production Pi adapter starts `harnesses/pi/src/worker.mjs` in an isolated process using the
versioned `amesh.pi-worker/v2` JSONL bridge:

1. For a small transcript, the parent includes canonical `messages` in `run.start`. For a large
   transcript, it first sends ordered `transcript.chunk` frames and puts their count, byte length and
   SHA-256 descriptor in `run.start`.
2. `run.start` includes the AMESH-calculated context budget. The worker loads the canonical
   transcript into Pi and calls `Agent.continue()`; Pi invokes the adapter's native
   `transformContext` projection.
3. The worker sends `model.request` with `contextProjection` and either inline `selectedMessages` or
   a `selectedTranscript` descriptor preceded by ordered `context.chunk` frames.
4. The parent reconstructs the selection, verifies chunk metadata, creates and validates the v3
   receipt, and invokes the AMESH model gateway. The matching provider result returns as
   `model.event`.
5. The worker emits `run.result`; the parent accepts it only when the expected model call and receipt
   have completed successfully.

Control frames are limited to 1 MiB. Chunk descriptors bind the count, decoded byte length and
SHA-256 digest, so missing, duplicate, reordered or altered transcript data is rejected. Pi `0.84.3`
and its `pi-ai` companion are pinned in `harnesses/pi/package-lock.json`.

## Registration and fail-closed behavior

Production composition registers Pi explicitly. An unknown or unavailable adapter is a startup or
execution error; AMESH must not silently select a built-in fallback. Adapter choice is fixed for an
execution and cannot change during an active session.

The parent also rejects an incorrect protocol or run identifier, an incomplete or mismatched chunk
stream, an invalid context projection or receipt, more than one model request, unexpected native
tool/state frames, and a missing final result. The current Pi worker is started with no native tools;
tool effects remain AMESH-mediated session turns. Its environment is reduced to non-secret runtime
variables, so it never receives the OpenRouter key.

## Conformance and provenance

Run the versioned, provider-free kit locally:

```powershell
uv sync --extra runtime --extra dev --locked
npm ci --prefix harnesses/pi
uv run python scripts/run_agent_harness_conformance.py --adapter pi --output .artifacts/harness-report.json
```

The report records the kit and manifest digest, AMESH source version, adapter and worker protocol
versions, runtime versions, exact package integrity and license metadata, every fixture result and a
canonical report digest. The same inputs must produce byte-identical reports. `make
verify-local-harness` runs the command twice in one Docker environment and compares the outputs.

The production-image probe uses the real Python Pi adapter and a deterministic in-process gateway,
so it never spends provider credits:

```powershell
docker build -t amesh:harness-conformance .
docker run --rm --entrypoint python amesh:harness-conformance -m amesh.harness_probe
```

For provider-backed local qualification, opt in explicitly with an OpenRouter key. PowerShell:

```powershell
$env:OPENROUTER_API_KEY = "..."
.\scripts\verify-local.ps1 -Suite live-openrouter
```

POSIX:

```bash
OPENROUTER_API_KEY="..." make verify-local-live-openrouter
```

The Docker suite defaults to `openai/gpt-5.6-luna` and
`deepseek/deepseek-v4-flash-vision-exp`. Override `OPENROUTER_TEST_MODELS` or
`OPENROUTER_QUALIFICATION_MODELS` to change the smoke and qualification sets. It verifies direct
provider behavior plus Pi multimodal structured sessions, safe progress chronology, normalized
usage/cost/cache evidence, context receipt v3, and restart/reuse behavior. Results are written to
`.artifacts/live-openrouter/junit.xml`.

This is a paid, opt-in suite and is not part of `verify-local-all`. The key remains in the AMESH
parent container and is never passed to the Pi worker.

## Adding another adapter

To evaluate DSH, Goose or another harness:

1. Implement only the `AgentSessionHarness` port in an isolated adapter package.
2. Accept the canonical transcript and AMESH context budget, project context through the harness's
   native mechanism, and return a verifiable v3 receipt.
3. Add an explicit registry entry and adapter/version provenance; unknown names must fail closed.
4. Pass the provider-free conformance kit and authority/failure-injection fixtures unchanged.
5. Add exact dependency, license, runtime and lockfile evidence.
6. Add a local live smoke only when the provider and credentials are intentionally available.

The adapter must not require a change to the public `agent.session` workflow, output, event or
recovery contract.
