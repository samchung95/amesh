# Audit prompt-cache evidence

Use the local analyzer to measure provider prompt-cache evidence without making a provider call. The analyzer reads persisted AMESH invocation and session records, prints aggregate metrics, and can restrict the sample by time, namespace, model, or session-turn cohort.

## Run the analyzer

Set a read-only database URL in your shell. Do not commit it or print the value. The example uses a placeholder rather than a real credential:

```powershell
$env:AMESH_DATABASE_URL = "postgresql+asyncpg://<readonly-user>:<password>@localhost:5432/amesh"
uv run --extra runtime python scripts/analyze_prompt_cache.py `
  --from "2026-08-24T23:57:00Z" `
  --to "2026-08-31T00:52:10Z"
```

The equivalent POSIX shell command is:

```bash
export AMESH_DATABASE_URL='postgresql+asyncpg://<readonly-user>:<password>@localhost:5432/amesh'
uv run --extra runtime python scripts/analyze_prompt_cache.py \
  --from '2026-08-24T23:57:00Z' \
  --to '2026-08-31T00:52:10Z'
```

Run `uv run --extra runtime python scripts/analyze_prompt_cache.py --help` to see the available filters. Time, tenant, namespace, provider, model, harness, route and turn filters are supported; the tenant filter is never rendered. Use the JSON output option when another local tool needs machine-readable results; do not send the output to a third-party service.

## Read the output

The analyzer reports these separate values:

- **Model calls:** all invocation outcomes, including rejected billed responses. This is the v2 cache-coverage denominator; successful-call rate remains a separate metric.
- **Cache-reported calls:** calls whose normalized `promptCache.state` is `reported`.
- **Positive reads/writes:** calls with positive provider-reported cache read/write tokens, regardless of acceptance.
- **Request-level read rate:** positive reads divided by calls with an explicit read-token count (`cache_read_reported`). Missing read evidence is not a miss.
- **Prompt tokens:** the sum of provider-reported input/prompt tokens.
- **Cached tokens:** the sum of provider-reported cached input tokens.
- **Token-weighted read rate:** cached tokens divided by input tokens, using only calls with both counts reported.
- **Unavailable/absent evidence:** calls with no provider usage or no normalized prompt-cache object. Do not convert this count to zero cache tokens.
- **Cost:** report legacy `result.costUsd` and normalized billed cost separately when both are available; neither is a promise of current provider pricing.
- **Cache-attributable savings:** the sum of `promptCache.costEffectUsd` only when the provider reports it. A missing value means savings are unavailable, not zero savings.

Always report the request-level and token-weighted rates together. A high request rate can coexist with a low token-weighted rate when only a small stable prefix is reused.

Report schema v2 adds uncached input, mean recorded invocation latency, phase and first/continuation
cohorts. First/continuation is not proof of a cold/warm provider cache: use observed read/write counts
to interpret it. Historical reports retain their original denominators.
Pass `--accepted-results N` only after verifying that many accepted consumer results in the exact
report window. Zero is valid; omission means unknown. Known billed cost per accepted result includes
rejected calls and is a lower bound when `cost_evidence_complete` is false. Uncached input per accepted
result is unavailable if any call lacks the required token evidence. The report does not infer
consumer acceptance from successful model calls.

## Compare useful cohorts

### Opt into reusable text boundaries

Use a release containing c253 and GitHub #97; deployed baseline `154edb9` does not contain
these controls. Drain active agent-session attempts and checkpoint writes before upgrading:
the older OpenRouter invocation hash includes the routing field, so an interrupted old claim
cannot be reclaimed under the new hash. Keep workers quiesced during deployment. Completed
checkpoints remain usable, and new-version replay/recovery is idempotent.

On a canonical session-create request or an `agent.session` task, add:

```json
{
  "contextPolicy": {
    "cacheBreakpoints": [
      {"messageIndex": 0, "partIndex": 0},
      {"messageIndex": 1, "partIndex": 0}
    ]
  }
}
```

Indexes refer to the original session transcript: message 0 is the pinned system instructions,
and message 1 is the initial input. A string becomes one text part; for multipart messages,
`partIndex` selects a text part (omission selects the last part). References must exist at
session creation. Invalid positions or image boundaries fail validation. The selection stays
in the canonical session configuration; checkpoints, follow-ups and compaction preserve the
selected text and marker. This does not remove context or alter tool requirements.

Direct model-task text parts also accept `prompt_cache_breakpoint: {"mode": "explicit"}`.
Use the pinned model policy's existing `parameters.requestOptions` for mode and TTL:

```json
{"prompt_cache_options": {"mode": "implicit", "ttl": "30m"}}
```

The built-in HTTP integration enables explicit controls for declared GPT-5.6 models on
OpenAI/OpenRouter; [custom model profiles](add-model-provider.md) can declare equivalent support.
Unsupported routes fail before I/O. Defaults send no markers or mode/TTL overrides. `implicit`
keeps automatic caching alongside markers. Choose `explicit` deliberately: without markers,
explicit-only mode disables cache use/writes. Writes are billable on GPT-5.6, and a marker does
not guarantee a hit. See [OpenAI's caching guidance](https://developers.openai.com/api/docs/guides/prompt-caching).

For Vibe's frozen Allocator comparison, keep inputs, model, effort, schema, tools and acceptance
criteria unchanged. Start with these two boundaries and implicit/30m on a new pinned configuration.
A separately authorized live comparison must report first-turn and continuation cohorts,
positive-read request rate, weighted reads, uncached input, writes, rejected billed calls,
latency and cost per accepted report. Matching hashes or successful output alone do not close
optimization qualification.

### Compare repairs on newly instrumented runs

OpenRouter agent sessions send a tenant-scoped stable `session_id` and supported
`prompt_cache_key` across turns, repairs, canonical follow-ups and worker recovery.
Other compatible routes receive supported upstream keys through the HTTP adapter.
OpenRouter models outside the inferred OpenAI set retain session stickiness; an upstream
cache key requires an explicit supporting model profile. Embeddings receive no automatic keys.
Explicit `requestOptions.prompt_cache_key` values are tenant-scoped; the automatic
identity uses the canonical session when present. Provider fallback remains available.
Keys improve routing affinity but do not guarantee a cache hit.

Inspect `providerPin.cacheDiagnostics` on successful `model.response` events. On
`output.rejected` events, the evidence sits in a different place depending on why the output was
rejected:

- When the provider response fails schema validation, the diagnostics are under
  `failureEvidence.cacheDiagnostics`.
- When the structured action is missing or its JSON is malformed, the diagnostics are under
  `providerPin.cacheDiagnostics`, and the priced usage is in top-level
  `usageNormalized.promptCache`. No tool call is dispatched.

Invocation results retain the same fields under `provenance.cacheDiagnostics`,
including rejected responses. Older records have no diagnostics.

- Compare `envelopeSha256` for changes to tools, output schema and other request
  settings. Completion ceilings and transport-only fields are excluded.
- Compare the earlier `messagePrefixSha256` list with the same leading entries
  in the later request. A matching list proves those outbound message objects
  are unchanged, including restored private continuation; it does not reveal
  provider-internal instructions or guarantee a token-level cache match.
- Compare `sessionKeySha256` and `responseProvider`. A missing provider identifier
  is unknown routing evidence, not proof of an unchanged upstream.
- Version 2 `sessionKeySha256` covers both OpenRouter session and upstream cache keys.
  Compare fingerprints within the same diagnostic version.
- Use bounded `responseId`, `requestId`, `responseModel` and `systemFingerprint` for
  provider correlation. Missing, oversized or unsafe values remain null. A matching
  provider label or fingerprint does not establish an identical cache machine.

The adapter records hashes, not prompt/continuation text. Use these alongside
reported read/write tokens and cost. Schema rejection alone is not a cache-miss
diagnosis; matching prefixes can still miss because of provider cache availability.

Start with these comparisons:

1. First-turn/two-message calls versus turn 2+ calls.
2. Compacted sessions versus sessions without a compaction event.
3. Namespace and model route.
4. Prompt-cache evidence versus task-result-cache events.

For the 2026-08-31 audit, the important values are in [Prompt-cache hit-rate audit](../reviews/prompt-cache-hit-rate-audit-2026-08-31.md): 531/673 reported-cohort positive reads, 1,860,152 cached of 13,059,275 normalized input tokens, 680 session model events with 670 reported cache objects, and a 503/507 read-positive rate for turn 2+ calls. The audit also records the 695-call raw coverage denominator separately.

## Safe handling

- Use a read-only database principal and run the analyzer locally.
- Keep database URLs, passwords, API keys, prompt contents, and raw provider responses out of logs and screenshots.
- The analyzer must not instantiate a model provider or call OpenRouter. It only reads persisted AMESH evidence.
- Treat `promptCache.state=unavailable` and a missing `promptCache` field as unavailable evidence, not as a provider miss.
- Do not mix prompt-cache results with task-result cache hits, invocation replay, continuation reuse, or response caching.
