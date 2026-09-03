# EPIC-201 — Sequential, parallel and DAG flowables

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Express common dependency and parallelism patterns as first-class flowable tasks.

## In scope

- [x] **URS-F-0188** — The system shall execute child tasks sequentially in declared order.
- [x] **URS-F-0189** — The system shall execute independent child tasks in parallel up to declared and platform concurrency limits.
- [x] **URS-F-0190** — The system shall execute directed acyclic graphs from explicit dependency edges.
- [x] **URS-F-0191** — The system shall validate DAG references and cycles at flow revision creation time.
- [x] **URS-F-0192** — The system shall aggregate child states, outputs and errors using documented deterministic rules.
- [x] **URS-F-0193** — The system shall support fail-fast, continue-on-error and collect-all policies.
- [x] **URS-F-0194** — The system shall render child task contexts without leaking sibling-private values.
- [x] **URS-F-0195** — The system shall visualize expanded dependency graphs before and during execution.

## Implementation completion evidence

- 2026-08-21 — W2 verified the accepted top-level DAG slice: independent ready tasks run concurrently, dependants wait for successful predecessors and persisted progress resumes after executor restart. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md) and [`test_postgres_executor.py`](../../tests/executor/test_postgres_executor.py). Nested flowables, joins and the broader epic remain open.
- 2026-08-22 — EPIC-201 is complete. Nested sequential, bounded-parallel and explicit-DAG children compile into durable parent/child task runs; persisted child state resumes after executor restart. Parent aggregates preserve declared child order, states, outputs and errors under fail-fast, continue-on-error and collect-all policies. Contexts expose transitive dependency output without independent sibling leakage. Authorized flow and execution graph APIs drive graphical pre-execution and live-state views in the control room. A 1,000-child DAG compiled in a 1.329 ms local mean over 100 iterations. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`execution-semantics.md`](../../docs/architecture/execution-semantics.md), [`nested-flowables.yaml`](../../examples/nested-flowables.yaml), [`test_flow_validation.py`](../../tests/test_flow_validation.py), [`test_postgres_executor.py`](../../tests/executor/test_postgres_executor.py), [`test_mvp_api.py`](../../tests/api/test_mvp_api.py) and [`FlowGraphView.tsx`](../../frontend/src/features/workflows/FlowGraphView.tsx).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-100
- EPIC-200

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

- Functional requirements: URS-F-0188, URS-F-0189, URS-F-0190, URS-F-0191, URS-F-0192, URS-F-0193, URS-F-0194, URS-F-0195
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
