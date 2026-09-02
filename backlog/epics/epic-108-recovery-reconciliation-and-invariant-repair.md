# EPIC-108 — Recovery, reconciliation and invariant repair

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `reliability`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Continuously detect and safely repair drift caused by process, PostgreSQL, worker, runner or object-storage failure.

## In scope

- [x] **URS-F-0148** — The system shall scan for expired leases, orphan task runs, stuck executions, missing dispatches and unprojected events.
- [x] **URS-F-0149** — The system shall rebuild disposable projections from authoritative state and event records.
- [x] **URS-F-0150** — The system shall apply only idempotent, version-checked repairs and record every repair as an auditable event.
- [x] **URS-F-0151** — The system shall quarantine ambiguous cases for operator review instead of guessing.
- [x] **URS-F-0152** — The system shall provide targeted reconciliation by execution, trigger, worker, tenant or time range.
- [x] **URS-F-0153** — The system shall rate-limit repair work so recovery cannot overwhelm the primary workload.
- [x] **URS-F-0154** — The system shall publish repair metrics, unresolved invariant counts and runbook links.
- [x] **URS-F-0155** — The system shall prove recovery scenarios through fault-injection and crash-consistency tests.

## MVP implementation progress

- 2026-08-21 — The MVP recovery slice resumed persisted DAG state and in-flight Kubernetes Jobs, rejected stale task and execution commits through attempt/epoch fencing, and completed 270 unique single-attempt soak executions while deleting every task pod plus 27 server pods and 13 worker pods. Independent API rereads found zero lost or duplicated executions. The product owner deferred the remaining uninterrupted 24-hour qualification to EPIC-611; projection repair, quarantine, targeted/rate-limited reconciliation and the broader epic remain open. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`src/amesh/worker.py`](../../src/amesh/entrypoints/worker.py), and [`scripts/soak_mvp.py`](../../scripts/soak_mvp.py).

## Implementation completion evidence

- 2026-08-22 — EPIC-108 functional scope is complete. Migration 0024 adds tenant-isolated run and finding ledgers; the PostgreSQL reconciler scans all six declared invariant classes, supports dry-run and bounded apply targeting tenant/execution/trigger/worker/time, rebuilds event/outbox and schedule projections with observed versions, requeues fenced expired claims, quarantines ambiguous task/execution state, and audits repairs, deferrals and quarantines. Tenant-management APIs, periodic worker execution, Prometheus metrics and the operator runbook are included. Fault injection verifies idempotency, a one-repair cap and repairable-state convergence in a second pass. A clean 24-migration database ran 207 passing tests with four environment skips, and the live OpenRouter smoke passed with `openai/gpt-5.6-luna`. The shared acknowledged-command failover NFR remains In Progress for HA qualification. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`reconciliation.md`](../../docs/operations/reconciliation.md), [`test_reconciliation_repository.py`](../../tests/adapters/postgres/test_reconciliation_repository.py), and [`test_reconciliation_api.py`](../../tests/api/test_reconciliation_api.py).

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-001** — The platform shall not lose an accepted state-changing command after the API or durable PostgreSQL transport acknowledges it. Target: Zero lost acknowledged commands in crash-consistency and failover tests.
- [ ] **URS-NFR-RELIABILITY-007** — Automated reconciliation shall converge recoverable invariant violations without creating new violations. Target: Reference fault scenarios converge within 10 minutes after dependencies recover.

## Dependencies

- EPIC-007
- EPIC-009
- EPIC-100
- EPIC-101

## Architecture impact

- Primary bounded area: `reliability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Fault-injection, replay and invariant tests.
- Fault-injection tests that terminate services and PostgreSQL connections at every commit, claim and acknowledgement boundary.
- End-to-end recovery suite with invariant counters.
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

- Functional requirements: URS-F-0148, URS-F-0149, URS-F-0150, URS-F-0151, URS-F-0152, URS-F-0153, URS-F-0154, URS-F-0155
- Non-functional requirements: URS-NFR-RELIABILITY-001, URS-NFR-RELIABILITY-007
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
