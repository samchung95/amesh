# Pi agent-session worker

This required Node 22 worker embeds Pi's direct `Agent` API behind an AMESH-owned JSONL bridge. It
contains no provider credential and performs no native tool effect. Every model and tool request is
sent to the parent process and must be completed by an AMESH gateway.

Install and verify the exact lock:

```powershell
cd harnesses/pi
npm ci
npm test
```

Run the worker with `node src/worker.mjs`. The parent starts one session with `run.start`; the worker
answers with `run.started`, `agent.event` and `run.result`. During the run it emits `model.request` and
`tool.request` frames containing a `requestId`. The parent completes those frames with matching
`model.event` and `tool.result` messages. The focused test is the executable protocol example.

`make dev` installs both the uv-managed Python environment and this exact npm lock. The product image
also contains Node 22, this worker and its production dependencies. API and recovery-executor paths
inject Pi explicitly; missing worker/runtime configuration fails closed and never selects a built-in
harness.

AMESH derives a bounded model context before every Pi turn without modifying the durable transcript.
The `amesh.recent-complete-turns/v1` projection retains pinned instructions and the newest complete
assistant/tool-result groups, fails closed if the minimum safe context cannot fit, and journals a
receipt containing stable transcript/context digests, retained and omitted source indexes, measured
message/byte/token headroom and whether compaction occurred. Provider prompt-cache read/write tokens,
hit ratio and signed cost effect are normalized as explicit evidence; missing provider telemetry is
recorded as unavailable rather than inferred.

Run the provider-free conformance kit from the repository root:

```powershell
uv run python scripts/run_agent_harness_conformance.py --adapter pi --output .artifacts/harness-report.json
```

The report includes the exact adapter/package versions, package integrity and license metadata, kit
digest and fixture evidence. `npm ci` must be used so `package-lock.json` remains authoritative.

To qualify the installed worker in the production image, run:

```powershell
docker run --rm --entrypoint python amesh:harness-conformance -m amesh.harness_probe
```

For an optional paid-provider smoke, set `OPENROUTER_API_KEY` only in the AMESH parent environment
and run the live test documented in
[`docs/plugin-sdk/agent-session-harness.md`](../../docs/plugin-sdk/agent-session-harness.md). The
worker never receives the key.
