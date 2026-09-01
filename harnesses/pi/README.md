# Pi agent-session worker

This required Node 22 worker embeds Pi `0.84.3`'s direct `Agent` API behind an AMESH-owned JSONL
bridge. It receives no provider credential, persists no authoritative transcript and performs no
native tool effect. Its only model request is completed by the AMESH parent gateway.

Install and verify the exact lock:

```powershell
cd harnesses/pi
npm ci
npm test
```

Run the worker with `node src/worker.mjs`. The bridge uses
`amesh.pi-worker/v2` and one worker process per harness turn:

1. The parent sends the full canonical transcript inline in `run.start`, or sends ordered
   `transcript.chunk` frames followed by a `run.start` transcript descriptor for larger payloads.
2. `run.start` supplies `amesh.agent-context-budget/v1`. The worker loads the transcript into Pi and
   calls `Agent.continue()`.
3. Pi calls the worker's native `transformContext` hook. The worker emits `model.request` with the
   resulting `contextProjection` and inline `selectedMessages`, or ordered `context.chunk` frames
   plus a `selectedTranscript` descriptor.
4. The parent validates the projection, constructs the context receipt, calls the provider, and
   answers with a matching `model.event`.
5. The worker completes with `run.result`.

Chunk descriptors bind their count, decoded byte length and SHA-256 digest. The bridge fails closed
on invalid protocol/run identifiers, missing, duplicate or mismatched chunks, multiple model
requests, and incomplete results; the parent also rejects native tool/state frames. Control frames
are limited to 1 MiB. The focused worker and Python adapter tests are executable protocol examples.

## Context projection ownership

AMESH keeps the durable canonical transcript and calculates the hard context boundary. Pi owns the
model-visible projection through `transformContext`. The
`pi.transform-context/recent-complete-turns/v1` algorithm preserves the pinned prefix and newest
complete dialogue group, then drops the oldest complete groups until the message, byte and estimated
input-token limits fit. It returns only exact source messages; it does not create a summary or a
compaction marker.

AMESH turns that selection into an `amesh.agent-context/v3` receipt and verifies the receipt,
source indexes, digests, measurements, harness provenance and applied budget before provider I/O.
The model call also reserves completion and request-overhead capacity inside the context window. If
the minimum safe context cannot fit, or the selection or receipt does not verify, the turn fails
closed while the canonical transcript remains intact.

Provider prompt-cache read/write tokens, hit ratio and signed cost effect are normalized as explicit
evidence; missing provider telemetry is recorded as unavailable rather than inferred.

## Build and qualification

`make dev` installs both the uv-managed Python environment and this exact npm lock. The product image
also contains Node 22, this worker and its production dependencies. API and recovery-executor paths
inject Pi explicitly; missing worker/runtime configuration fails closed and never selects a built-in
harness.

Run the provider-free conformance kit from the repository root:

```powershell
uv run python scripts/run_agent_harness_conformance.py --adapter pi --output .artifacts/harness-report.json
```

The report includes the exact adapter/package versions, worker protocol, package integrity and
license metadata, kit digest and fixture evidence. `npm ci` must be used so `package-lock.json`
remains authoritative.

To qualify the installed worker in the production image, run:

```powershell
docker run --rm --entrypoint python amesh:harness-conformance -m amesh.harness_probe
```

For the opt-in paid OpenRouter suite, set the key only in the AMESH parent environment. PowerShell:

```powershell
$env:OPENROUTER_API_KEY = "..."
.\scripts\verify-local.ps1 -Suite live-openrouter
```

POSIX:

```bash
OPENROUTER_API_KEY="..." make verify-local-live-openrouter
```

The Docker suite defaults to `openai/gpt-5.6-luna` and
`deepseek/deepseek-v4-flash-vision-exp`, writes
`.artifacts/live-openrouter/junit.xml`, and is not part of `verify-local-all`. The worker never
receives the key. See the full contract and override settings in
[`docs/plugin-sdk/agent-session-harness.md`](../../docs/plugin-sdk/agent-session-harness.md).
