# EPIC-202 — Conditional branching and switch semantics

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Choose workflow branches from safe expressions with explainable decisions.

## In scope

- [x] **URS-F-0196** — The system shall execute if, else-if and else branches from boolean conditions.
- [x] **URS-F-0197** — The system shall select switch cases by exact value, ordered predicate or default branch.
- [x] **URS-F-0198** — The system shall record rendered condition inputs, redacted evaluation result and selected branch.
- [x] **URS-F-0199** — The system shall treat expression errors according to explicit fail, false or fallback policy.
- [x] **URS-F-0200** — The system shall skip non-selected branches without creating misleading runnable attempts.
- [x] **URS-F-0201** — The system shall support conditions on tasks, triggers, retries, errors and outputs.
- [x] **URS-F-0202** — The system shall validate unreachable or duplicate cases where static analysis permits.

## Implementation completion evidence

- 2026-08-22 — EPIC-202 is complete. Durable `core.if` and `core.switch` decisions select ordered boolean, exact-value, predicate and fallback branches; persist redacted evaluation evidence and explicit expression-error policy; skip every non-selected descendant at attempt zero; and reuse the committed decision after restart. Task, trigger, retry, error and output conditions share the typed expression contract, while static validation rejects duplicate and unreachable cases. A fresh 35-migration PostgreSQL run, the complete backend suite, Ruff, strict mypy, generated contracts/planning, live Compose acceptance and deployed branch execution passed. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`test_conditionals.py`](../../tests/executor/test_conditionals.py), [`conditional-flowables.yaml`](../../examples/conditional-flowables.yaml) and [`ADR-033`](../../docs/adr/033-durable-conditional-branch-decisions.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-005
- EPIC-201

## Architecture impact

- Primary bounded area: `workflow`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- DSL validation plus end-to-end workflow conformance tests.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0196, URS-F-0197, URS-F-0198, URS-F-0199, URS-F-0200, URS-F-0201, URS-F-0202
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
