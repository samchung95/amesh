# EPIC-830 — Prompt-cache hit-rate forensics and optimization

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Should
- **Domain:** `observability`
- **Primary persona:** AI application operator and platform engineer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Give operators a reproducible, privacy-safe account of provider prompt-cache behavior, locate the first evidence-backed reuse break, and improve reusable context identity without confusing prompt caching with task-result cache or invocation replay.

## In scope

- [x] A read-only historical report derives prompt-cache evidence from durable model invocations and correlated model-response events, supports bounded time and tenant/namespace filters, and emits aggregates without prompts, secrets, raw payloads or resource identifiers.
- [x] The report distinguishes successful, failed, evidence-reported and evidence-unavailable calls; positive reads, reported-zero misses and positive writes; and request-level hit rate from token-weighted reuse rather than presenting one ambiguous cache-hit percentage.
- [x] Aggregates cover date, namespace, provider, model, harness, route, turn, attempt, continuation, compaction and envelope cohorts together with input, output, read and write tokens, cost and explicit unavailable fields.
- [x] Task-result cache, provider response caching and AMESH invocation replay remain explicitly excluded from prompt-cache denominators and are described only as separate mechanisms.
- [x] The checked historical audit identifies the sample window and limitations, preserves unavailable evidence instead of treating it as a miss, and ranks suspected reuse breaks by measured impact without provider-specific savings claims.
- [x] A versioned provider-neutral context projection removes changing transcript identity from the model-visible compaction marker while retaining full transcript, context, retained/omitted index and receipt evidence outside the prompt; existing v1 receipts remain readable.
- [x] A frozen provider-free before/after workload proves the new compaction marker and unchanged pinned prefix remain byte-stable across transcript growth while all context bounds, complete-turn preservation, event ordering and receipt integrity remain enforced.
- [x] Focused tests, strict typing/linting, documentation build and the complete Docker-local aggregate pass; no paid provider call is required and any live provider qualification remains an explicit opt-in follow-up.

## Implementation completion evidence

- 2026-08-31 — EPIC-830 is complete. AMESH now provides a privacy-safe read-only prompt-cache analyzer with explicit evidence coverage, request-level, token-weighted, write, cost and unavailable measures across safe cohorts. The checked historical window contained 732 model calls; 673 successful calls reported cache evidence, with 531 positive reads (78.9004%) and 14.2439% token-weighted reuse. Context projection v2 removes changing transcript identity from the model-visible compaction marker while preserving complete durable receipt provenance and v1 readability. Provider-free fixtures prove the new marker remains byte-stable across transcript growth; focused and complete Docker-local gates pass. Evidence: [`docs/reviews/prompt-cache-hit-rate-audit-2026-08-31.md`](../../docs/reviews/prompt-cache-hit-rate-audit-2026-08-31.md), [`docs/how-to/audit-prompt-cache.md`](../../docs/how-to/audit-prompt-cache.md), [`tests/test_prompt_cache_report.py`](../../tests/test_prompt_cache_report.py), [`tests/domain/test_agent_context.py`](../../tests/domain/test_agent_context.py) and [`TESTLOG.md`](../../docs/reviews/TESTLOG.md). No paid provider request or provider-savings claim was made.

## Explicit non-goals

- Changing or measuring the PostgreSQL task-result cache
- Changing AMESH invocation replay or provider response-cache semantics
- Adding provider-specific prompts, tools, workflows or client-domain behavior
- Claiming provider cache savings without provider-reported cost evidence
- Making paid live-provider calls as part of the default local gate

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-607
- EPIC-812
- EPIC-813
- EPIC-819
- EPIC-828

## Architecture impact

- Primary bounded area: `observability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Run the read-only audit tool against the current local PostgreSQL history and compare its totals with independent SELECT-only queries over agent_invocations and agent_session_events.
- Run unit fixtures for hit/miss/write/unavailable classification, denominator math, grouping, filters, privacy-safe rendering and empty or partial evidence.
- Run context projection compatibility and frozen before/after tests covering legacy v1 receipt loading, v2 marker stability, compaction bounds and complete-turn preservation.
- Run focused session/provider/evidence regressions, Ruff, strict mypy, generated-contract and planning drift checks.
- Run the documentation suite and complete Docker-local verification aggregate.
- Historical audit and operator reproduction evidence: [`docs/reviews/prompt-cache-hit-rate-audit-2026-08-31.md`](../../docs/reviews/prompt-cache-hit-rate-audit-2026-08-31.md), [`docs/how-to/audit-prompt-cache.md`](../../docs/how-to/audit-prompt-cache.md), [`scripts/analyze_prompt_cache.py`](../../scripts/analyze_prompt_cache.py) and [`tests/test_prompt_cache_report.py`](../../tests/test_prompt_cache_report.py).
- Controlled context-identity evidence: [`src/amesh/domain/agent_context.py`](../../src/amesh/domain/agent_context.py), [`tests/domain/test_agent_context.py`](../../tests/domain/test_agent_context.py) and [`docs/adr/058-pi-behind-amesh-agent-session-harness-port.md`](../../docs/adr/058-pi-behind-amesh-agent-session-harness-port.md).
- Release evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md) records the historical denominators, provider-free v1/v2 comparison, focused regressions, strict docs suite and complete Docker-local aggregate.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] An operator can reproduce the historical request-level and token-weighted prompt-cache rates without direct ad hoc payload inspection or exposure of protected content.
- [x] The report answers where evidence became available, where reusable tokens are lost and which conclusions remain unsupported by the retained data.
- [x] The first controlled reuse break has a provider-neutral fix with a frozen before/after comparison and no weakening of deterministic context or durability contracts.
- [x] The audit, command usage, metric definitions, mechanism boundaries and remaining provider qualification limits are documented and linked to executable evidence.
- [x] All focused and complete Docker-local gates pass with evidence recorded in TESTLOG.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Request-level hit rate and token-weighted reuse answer different questions and can be misleading if presented without their denominators.
- Historical provider fields and normalization changed over time, so missing evidence cannot be reclassified as a cache miss.
- Cache read and write semantics, minimum prompt size, routing and cost effects vary by provider and model and cannot be inferred from AMESH alone.
- Changing context compaction can improve prefix stability while reducing useful history unless existing bounds and complete-turn guarantees remain unchanged.
- Historical request metadata may contain protected application content, so the audit must calculate only safe aggregates and never render prompt values or identifiers.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
