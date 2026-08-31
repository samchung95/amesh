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

- **Successful model calls:** the denominator for cache-evidence coverage and the separate all-success positive-read rate.
- **Cache-reported calls:** successful calls whose normalized `promptCache.state` is `reported`; this is the denominator for the report's primary request hit rate.
- **Positive reads:** successful calls whose provider usage contains `cached_tokens > 0`.
- **Positive writes:** successful calls whose provider usage contains `cache_write_tokens > 0`.
- **Request-level read rate:** positive reads divided by cache-reported calls. The report also emits positive reads divided by all successful calls as a coverage-inclusive rate.
- **Prompt tokens:** the sum of provider-reported input/prompt tokens.
- **Cached tokens:** the sum of provider-reported cached input tokens.
- **Token-weighted read rate:** cached tokens divided by normalized input tokens in the cache-reported cohort.
- **Unavailable/absent evidence:** calls with no provider usage or no normalized prompt-cache object. Do not convert this count to zero cache tokens.
- **Cost:** report legacy `result.costUsd` and normalized billed cost separately when both are available; neither is a promise of current provider pricing.
- **Cache-attributable savings:** the sum of `promptCache.costEffectUsd` only when the provider reports it. A missing value means savings are unavailable, not zero savings.

Always report the request-level and token-weighted rates together. A high request rate can coexist with a low token-weighted rate when only a small stable prefix is reused.

## Compare useful cohorts

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
