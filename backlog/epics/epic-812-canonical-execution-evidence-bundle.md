# EPIC-812 — Canonical execution evidence bundle

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `observability`
- **Primary persona:** Operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Export one versioned, bounded and integrity-checkable record of everything a client needs to explain an execution without exposing secrets or hidden model rationale.

## In scope

- [x] The bundle includes exact pins, inputs, outputs, task attempts, agent sessions, external invocations, state transitions, logs, metrics, files, errors, approvals and interventions.
- [x] Records have stable ordering, correlation identifiers, schema digests, token usage and explicit priced, unpriced or unavailable cost states.
- [x] Secrets and hidden chain-of-thought are excluded while provider-supplied opaque continuation data remains protected and resumable.
- [x] Large fields externalize to integrity-checked object storage and every API response remains bounded and paginated.
- [x] REST, CLI and SDK retrieval enforce authorization, tenant isolation and redaction.
- [x] The same completed or recovered execution produces a stable bundle digest; conflicting evidence is detected rather than overwritten.

## Implementation completion evidence

- 2026-08-26 — EPIC-812 is complete. The canonical evidence bundle captures workflow, agent, model, tool, decision, error, approval, intervention and control records with exact lineage, normalized usage/cost states, deterministic ordering, bounded pagination, object-store externalization, redaction and a stable SHA-256 digest; secrets and hidden reasoning are excluded. Migration 0066 preserves every evidence kind. Fourteen focused unit/API/PostgreSQL tests passed. Live execution `01a039c5-4225-735e-b4f7-e7af5d4a5dbc` exported 13 trace records with digest `sha256:eced2443a98deae4cc15c372a09e72553cafa907b2e924f570919cbb0f347576`, and the uv CLI independently returned `verified: true`. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`evidence-bundles.md`](../../docs/operations/evidence-bundles.md), [`evidence-bundle-v1.json`](../../schemas/evidence-bundle-v1.json), [`test_evidence_bundle.py`](../../tests/test_evidence_bundle.py), and [`test_evidence_bundle_repository.py`](../../tests/adapters/postgres/test_evidence_bundle_repository.py).

## Explicit non-goals

- Persisting or displaying private chain-of-thought
- Defining a domain-specific decision or citation schema

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-407
- EPIC-602
- EPIC-808
- EPIC-811

## Architecture impact

- Primary bounded area: `observability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Canonical ordering, digest and schema contract tests.
- Large-record externalization and integrity-corruption integration tests.
- Authorization, tenant-isolation and secret-redaction tests.
- Restart-stability tests plus REST, CLI and SDK retrieval smoke tests.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] The evidence schema is versioned and its compatibility policy is documented.
- [x] A reference execution with agents and tools exports and verifies end to end.
- [x] TESTLOG records bundle size limits, digest evidence and negative cases.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Unbounded evidence responses can make successful large runs impossible to inspect.
- Raw provider or tool records can disclose credentials or sensitive reasoning.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
