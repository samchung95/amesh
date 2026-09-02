# EPIC-813 — Pluggable model-provider capabilities and conformance

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Run bounded agents against replaceable model providers whose capabilities, continuation state, timeouts, usage and cost semantics are negotiated and tested before provider I/O.

## In scope

- [x] A versioned ModelProvider registry declares context, output, structured-output, tool, streaming, opaque-continuation, timeout, cancellation, usage, cache, cost and retry capabilities.
- [x] Capability negotiation rejects incompatible requests before external I/O and pins the exact provider revision used.
- [x] OpenAI-compatible transport remains one implementation and independently trusted adapters can register without changing workflow semantics.
- [x] Opaque reasoning continuation data round-trips for supported providers without exposing hidden rationale to users or logs.
- [x] Usage and cost normalize to billed, unpriced or unavailable states and hard budgets fail closed when required cost data is absent.
- [x] Conformance covers large responses, malformed structured output, tool turns, timeout, retry, cancellation and ambiguous outcomes.
- [x] Environment-gated live checks use OpenRouter with `openai/gpt-5.6-luna`; a DeepSeek-compatible fixture proves large-output and continuation semantics without making DeepSeek a core dependency.

## Implementation completion evidence

- 2026-08-26 — EPIC-813 is complete. A provider-neutral registry pins exact provider revisions and negotiates structured output, tools, reasoning continuation, timeout, retry and cancellation capabilities before network I/O. Usage and billed-cost normalization preserve unavailable and unpriced states; hard budgets fail closed; ambiguous outcomes are not repeated; opaque continuation state is application-encrypted with rotatable Fernet keys and tenant-scoped durable storage. Seventeen model-provider/task tests passed against two independently implemented fixtures, strict mypy passed, and the live OpenRouter smoke returned content, usage and billed cost from exact model `openai/gpt-5.6-luna`. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`add-model-provider.md`](../../docs/how-to/add-model-provider.md), [`057-application-encrypted-model-continuations.md`](../../docs/adr/057-application-encrypted-model-continuations.md), [`test_model_provider_registry.py`](../../tests/model_providers/test_model_provider_registry.py), and [`test_openrouter_smoke.py`](../../tests/llm/test_openrouter_smoke.py).

## Explicit non-goals

- Making DeepSeek or OpenRouter mandatory for AMESH
- Persisting user-visible hidden chain-of-thought

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-312
- EPIC-807
- EPIC-808

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Provider registry, capability negotiation and immutable-revision unit tests.
- Provider conformance fixture suite for structured output, tools, continuation, usage, timeout and ambiguous outcomes.
- Large-response and budget fail-closed tests.
- Environment-gated OpenRouter Luna smoke test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] At least two provider registrations pass the neutral conformance suite.
- [x] Agent resource and session traces expose pinned capabilities and normalized usage without provider secrets.
- [x] Provider authoring and conformance documentation is runnable with uv.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Provider-specific request features can leak into durable workflow contracts.
- Missing or incompatible cost telemetry can silently defeat hard budgets.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
