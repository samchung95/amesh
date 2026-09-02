# EPIC-819 — Pluggable agent-session harness, bounded context and cache evidence

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Run long-lived bounded agents through a replaceable session harness while AMESH remains the sole authority for tools, policy, durability, budgets and evidence.

## In scope

- [x] DSH, Pi and Goose are compared from current primary evidence for embedding cost, provider neutrality, external tool mediation, context handling, cache visibility, resumability, maintenance and license, and one choice is recorded in an ADR.
- [x] A typed agent-session harness port preserves the public agent.session contract, runs the selected third-party adapter in every production composition root and has no silent built-in fallback.
- [x] AMESH remains the only authority that resolves capability pins, approves and invokes tools, enforces budgets, journals external effects, checkpoints progress and accepts final structured output.
- [x] The canonical transcript remains immutable while bounded derived model context preserves pinned instructions and tool-call/result pairing and records a verifiable compaction receipt.
- [x] Provider prompt-cache reads, writes, hit ratio and cost effects become normalized evidence distinct from taskCache and invocation replay.
- [x] A multi-turn OpenRouter openai/gpt-5.6-luna session uses an AMESH-mediated tool and returns schema-valid output through the selected harness adapter.

## Implementation completion evidence

- 2026-08-26 — EPIC-819 is complete. Pi 0.84.3 is the required production harness behind the typed AMESH port with no built-in fallback; AMESH remains authoritative for model routing, tools, policy, budgets, journals, checkpoints and output validation. A deterministic recent-complete-turns projection bounds model context by messages, canonical bytes and estimated tokens while the PostgreSQL checkpoint retains the append-only transcript; every turn records stable transcript/context digests, retained and omitted indexes and remaining headroom. OpenRouter cache reads, writes, hit ratio and signed cost effect are normalized as explicit reported/unavailable evidence separate from task cache and invocation replay. Focused unit, adapter, API, evidence and PostgreSQL tests passed with strict mypy and Ruff, the exact Pi Node test passed, a live openai/gpt-5.6-luna session completed a mediated tool round-trip with schema-valid output, and rebuilt API/executor services returned full readiness at migration 66. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`ADR-058`](../../docs/adr/058-pi-behind-amesh-agent-session-harness-port.md), [`agent_context.py`](../../src/amesh/domain/agent_context.py), and [`test_agent_sessions.py`](../../tests/tasks/test_agent_sessions.py).

## Explicit non-goals

- Replacing the AMESH workflow executor or PostgreSQL session journal
- Permitting harness-native tools, credentials or side effects to bypass AMESH
- Adding domain-specific tools or client-specific workflows
- Claiming production readiness beyond measured local evidence

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-808
- EPIC-812
- EPIC-813
- EPIC-814
- EPIC-816

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Candidate scorecard and adapter contract tests.
- Compatibility, policy denial, malformed action and hard-limit tests.
- Context compaction, tool-pair preservation and cache-normalization tests.
- Restart and accepted-invocation reuse integration tests.
- Live bounded OpenRouter Luna tool-session smoke test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] The selected harness is exactly locked with its native package manager, Python dependencies remain uv-managed, and the adapter can be removed or replaced behind one internal port.
- [x] No harness path can execute a model or tool outside AMESH provider, policy and invocation journals.
- [x] Long sessions have measured context headroom, compaction provenance and provider cache evidence.
- [x] Existing agent.session behavior and focused restart guarantees remain verified.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A third-party harness can become a second workflow engine or bypass AMESH authority if the adapter boundary is too broad.
- Lossy compaction can remove constraints or break tool-call/result pairing.
- Provider cache counters and cache-control semantics vary across models and routes.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
