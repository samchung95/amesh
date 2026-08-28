# EPIC-817 — Generic differential and shadow execution

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `quality`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Compare two exact workflow or agent configurations on frozen inputs without permitting uncontrolled side effects or pretending nondeterministic outputs must be byte-identical.

## In scope

- [x] A differential specification pins two exact configurations, frozen inputs, safe fixtures and comparison policy.
- [x] Shadow runs deny external side effects unless a certified safe fixture or recording is selected.
- [x] Each side retains independent lineage while comparison covers schema, deterministic assertions, task/tool chronology, evidence, usage, cost, latency and configured tolerances.
- [x] Comparator extensions are provider- and domain-neutral; a deterministic structural comparator ships in core.
- [x] REST, CLI and SDK operations are authorized, tenant-isolated and idempotent.
- [x] Tests distinguish expected model nondeterminism from contract, policy and evidence regressions.

## Implementation completion evidence

- 2026-08-26 — EPIC-817 is complete. The durable differential service pins two exact configurations, frozen inputs, certified fixtures and comparison policy; independently claims and records each side; denies uncontrolled effects; and reports deterministic failures, tolerated differences and nondeterministic observations across schema, chronology, evidence, usage, cost and latency. REST, CLI and SDK operations are authorized, tenant-scoped and idempotent. Focused unit/API/CLI/PostgreSQL tests passed. Live Compose spec `561a6327-631e-4c1e-8341-8e61cebad3bc` produced independent runs `01a039cb-1c7a-7d12-9f46-5902b9e468f1` and `01a039cb-1c8f-7681-abf1-cd2240845e23` with zero deterministic failures and returned the identical durable report after an API restart. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`run-differential-shadow.md`](../../docs/how-to/run-differential-shadow.md), [`differential.py`](../../src/amesh/quality/differential.py), [`durable.py`](../../src/amesh/quality/durable.py), and [`test_differential_repository.py`](../../tests/quality/test_differential_repository.py).

## Explicit non-goals

- Encoding VibeStonks parity rules in AMESH
- Automatically promoting the shadow candidate

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-704
- EPIC-812
- EPIC-813
- EPIC-814
- EPIC-816

## Architecture impact

- Primary bounded area: `quality`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Differential specification and structural comparator unit tests.
- Side-effect-denial and certified-fixture policy tests.
- Independent-lineage, tolerance, usage, cost and evidence comparison integration tests.
- REST, CLI and SDK idempotency smoke tests.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] A neutral two-configuration shadow scenario runs end to end with zero uncontrolled effects.
- [x] The report separates deterministic failures, tolerated differences and nondeterministic observations.
- [x] Extension and operator documentation explains frozen-input and safety requirements.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A shadow run can accidentally duplicate real external effects.
- Byte-level comparison can misclassify valid nondeterministic model variation as failure.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
