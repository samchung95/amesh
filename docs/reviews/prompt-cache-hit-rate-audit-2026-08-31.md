# Prompt-cache hit-rate audit — 2026-08-31

This review records what the local AMESH history can prove about provider prompt caching and where reuse is lost. It is an audit of persisted evidence, not a provider qualification: it made no new OpenRouter calls and does not expose prompt contents, credentials, or raw provider responses.

## Scope and method

The read-only sample covers these UTC timestamps:

- **Start:** 2026-08-24 23:57 UTC
- **End:** 2026-08-31 00:52 UTC
- **Sources:** `agent_invocations`, `agent_sessions`, `agent_session_events`, `task_cache_entries`, and `task_cache_events`
- **Model route:** `openai/gpt-5.6-luna` through the OpenAI-compatible OpenRouter adapter

The primary sample contains 732 model invocations: 695 succeeded and 37 failed. The session projection contains 203 sessions and 680 `model.response` events. The local database is a development/test history, not a production traffic sample.

The reproducible operator procedure is in [Audit prompt-cache evidence](../how-to/audit-prompt-cache.md).

## Two denominators answer different questions

AMESH reports two useful prompt-cache rates. They must not be collapsed into one number:

| Metric | Calculation | Result | Meaning |
| --- | --- | ---: | --- |
| Request-level positive-read rate (all successful raw responses) | Successful model calls with `cached_tokens > 0` ÷ all successful model calls | **531 ÷ 695 = 76.40%** | How often a successful response had a positive raw counter; the denominator includes 22 calls whose normalized cache evidence is missing |
| Request-level positive-read rate (reported normalized cohort) | Positive reads ÷ successful calls with `promptCache.state=reported` | **531 ÷ 673 = 78.9004%** | How often a response with available normalized evidence reported a reused token |
| Token-weighted read rate (all successful raw responses) | Sum of `cached_tokens` ÷ sum of `prompt_tokens` | **1,860,152 ÷ 13,063,397 = 14.24%** | How much of the submitted prompt volume was reused |
| Token-weighted read rate (reported normalized cohort) | Cached tokens ÷ normalized input tokens | **1,860,152 ÷ 13,059,275 = 14.2439%** | The same reuse volume measured only where normalized input evidence is present |

Writes were positive on 632 of 695 successful raw responses (**90.94%**), or 632 of the 673 reported normalized responses (**93.9079%**), totalling 11,193,253 tokens. In the reported normalized cohort, 14 calls had both read and write equal to zero, 128 were write-only, 27 were read-only, and 504 had both reads and writes. The 22 calls without normalized cache evidence are unavailable, not cache misses. Legacy `result.costUsd` totals **$3.585738667** across successful calls; normalized billed cost is present for 677 calls and totals **$3.581890107**. `promptCache.costEffectUsd` is absent on every call, so cache-attributable savings cannot be calculated. Total prompt and completion volume was 13,063,397 and 353,534 tokens respectively.

The request-level number is high because a call can reuse a small stable prefix while rewriting a much larger dynamic tail. The token-weighted number is the better indicator for cost reduction. The raw all-success denominator is useful for coverage; the normalized-cohort denominator is useful for measuring only calls where AMESH has explicit prompt-cache evidence. Neither denominator should treat missing evidence as a miss.

## Cohorts and reuse boundary

The clearest boundary is session position, represented by the number of messages in the persisted request metadata:

| Cohort | Calls | Positive reads | Request-level read rate |
| --- | ---: | ---: | ---: |
| Two-message / first-turn calls | 185 | 28 | **15.14%** |
| Turn 2+ calls | 507 | 503 | **99.21%** |

The multi-turn cohort is the operational success case: once the conversation continues, the stable prefix is commonly reused. First-turn reuse is weak across new sessions, but the historical contexts are mostly distinct, so this is not evidence of a broken cache. It is consistent with each session beginning with its own input and relying on the provider's implicit cache and routing behavior.

By namespace, the successful model sample was:

| Namespace | Calls | Positive reads | Request rate | Token-weighted rate |
| --- | ---: | ---: | ---: | ---: |
| `vibestonks.daily_agent_book` | 454 | 380 | 83.70% | 13.01% |
| `vibestonks.book_manager` | 201 | 151 | 75.12% | 22.99% |
| `agents.demo` | 30 | 0 | 0% | 0% |
| `aura.local` | 9 | 0 | 0% | 0% |

The sample also shows prompt growth: two-message calls average about 6,110 prompt tokens, while later calls often carry the complete transcript. Cache reads remain bounded around reusable prefixes while writes grow with the dynamic conversation. This is an observation from the persisted counters; it does not prove which individual prompt segment the provider cached.

## Evidence availability and timeline

The evidence became more complete as the current provider/session path rolled out:

| Period | Evidence |
| --- | --- |
| Aug 24–25 | 18 successful model invocations had no normalized cache object; raw cache counters were zero. The first eight session response events had no `promptCache` field. Provider binding was absent on these early records. |
| Aug 26 | Provider-bound records began carrying normalized cache evidence. Four successful calls at 02:35:46–02:36:01 UTC had raw zero read/write counters but no normalized `promptCache` object. |
| Aug 30–31 | All 463 session model responses carried reported prompt-cache evidence. |

Across all 680 session model-response events, 670 reported `promptCache` and 10 lacked the field. Across the 695 successful model invocations, 673 had normalized `promptCache.state=reported` and 22 were missing/unavailable. No session response explicitly recorded `state: unavailable`; failed invocations have no provider result, so their cache availability cannot be inferred. Absence is not a zero and is not evidence of a provider miss.

The provider pin persisted in 672 session response events reports `capabilities.cache=false`, while the same provider responses report cache reads and writes. This is a capability declaration mismatch, not evidence that caching is disabled.

## Context compaction

There were 54 `context.compacted` events across 203 sessions (**26.60% of sessions**). Compaction occurred at turns 4–17, with estimated context sizes from 35,560 to 65,281 tokens; every compaction event included its marker and receipt fields. The non-compacted and compacted session cohorts had prompt-cache read rates of **16.41%** and **6.70%** respectively in this sample.

Compaction therefore coincides with lower prompt-token reuse in this history, but the sample is not a causal experiment. Compaction changes the serialized context and can change the provider-visible prefix; the current evidence does not identify whether compaction itself, session age, prompt size, or workload mix is responsible.

## Source facts versus inference

**Source facts:** OpenRouter returned `cached_tokens` and `cache_write_tokens` for the successful Luna calls; AMESH normalized these into `readTokens`, `writeTokens`, and `hitRatio` when present. The provider pin says `cache=false`. First-turn and later-turn cohorts have the rates above. AMESH has separate task-result-cache tables and events.

**Inference:** First-turn reuse is weak because new sessions do not share enough provider-visible stable context. Later-turn reuse is strong because the same session retains a reusable prefix. The first AMESH-controlled break that can be reproduced offline is the v1 compaction marker: it embeds a changing transcript digest and omitted-message count ahead of the retained dialogue. The observational compaction cohort supports investigating that break, but it does not by itself prove provider causality.

OpenRouter documents automatic prompt caching and provider sticky routing, including a caller-supplied `session_id` for multi-turn affinity, in its [Prompt Caching documentation](https://openrouter.ai/docs/guides/best-practices/prompt-caching). Provider support and pricing vary by model; AMESH must treat those as adapter-level semantics rather than universal guarantees.

## Ranked recommendations

1. **Measure both denominators reproducibly.** Report request-level reads, token-weighted reads, writes, unavailable evidence, first-turn versus later-turn cohorts, namespace, model route, compaction state, continuation, retry and cost. Do not report task-result-cache hits as prompt-cache hits.
2. **Remove AMESH-controlled prefix churn.** Keep the model-visible compaction marker stable while retaining the changing transcript digest, omitted indexes and full provenance in the durable context receipt. Version the algorithm so old receipts remain readable.
3. **Keep reusable context before dynamic context.** Preserve stable system instructions, schemas, and tool definitions at the beginning of the request; append changing user data, retrieved evidence, and transcript tail afterward. This follows the provider guidance and gives the cache a stable prefix to reuse.
4. **Evaluate affinity and capability semantics separately.** A future provider-neutral affinity hint could map to OpenRouter's `session_id`, and the cache capability declaration should become truthful, but neither change is justified as the first fix by this sample: turns 2+ already read cache on 503 of 507 calls. Both need adapter conformance and a controlled live provider comparison.
5. **Defer response caching as a separate decision.** OpenRouter response caching is a request-level feature with different semantics from provider prompt caching. It needs its own authorization, freshness, replay, and privacy contract; it is not a substitute for prompt-cache observability.

### Selected EPIC-830 change

The selected implementation path is recommendations 1 and 2: ship the read-only analyzer as the repeatable measurement gate and move context projection to `amesh.recent-complete-turns/v2`, whose model-visible compaction marker is stable while the changing provenance remains in the receipt. A frozen provider-free comparison proves that the legacy marker changes as the transcript grows and the v2 marker does not. This is a request-identity improvement, not a claim that OpenRouter will deliver a particular hit rate or saving.

## Keep these caches separate

- **Provider prompt cache:** The model provider reuses prompt tokens and reports read/write counters. AMESH stores the evidence returned by the provider. It may reduce provider input cost, but it does not replace execution state.
- **Task-result cache:** AMESH's opt-in `taskCache` stores a completed runnable-task result under a tenant/security/revision-fenced key. It can avoid running a task at all. The local history contains six task-cache events, three lookup decisions (`MISS`, `HIT`, `MISS_INVALIDATED`), and one ready entry with `hit_count=1`; that is an acceptance sample from Aug 22, not a model prompt-cache measurement. See [Task cache operations](../operations/task-cache.md).
- **Invocation replay/continuation:** AMESH persists invocation identity and encrypted provider continuation state so an operation can resume or be replayed under its durable controls. It does not mean a prompt was reused. The sample contains 661 encrypted continuations, including 69 on attempt 2.
- **Response caching:** A provider or gateway may return a previously computed response for an identical request. This is distinct from prompt-token reuse and must not be inferred from `cached_tokens`. See OpenRouter's [Response Caching documentation](https://openrouter.ai/docs/guides/features/response-caching).

## Limitations

- The sample is local development/test history and covers fewer than seven days; it is not representative production traffic.
- No prompt contents were inspected or exported. The database stores request hashes and redacted metadata, not a provider cache trace that identifies the exact reused span.
- OpenRouter/provider behavior, cache TTLs, routing, supported models, and pricing can change; the linked provider documentation is the source for current provider semantics.
- Failed calls have no successful usage payload. They are counted in availability totals but cannot be classified as provider cache hits or misses.
- The compaction comparison is observational and confounded by workload and session age.
