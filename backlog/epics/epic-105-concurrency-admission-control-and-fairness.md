# EPIC-105 — Concurrency, admission control and fairness

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Protect shared capacity while offering predictable fairness across tenants, namespaces, flows and task types.

## In scope

- [x] **URS-F-0124** — The system shall enforce execution and task concurrency limits at global, tenant, namespace, flow, worker-group and key scopes.
- [x] **URS-F-0125** — The system shall support queue, cancel, fail, replace and skip behaviors when a limit is reached.
- [x] **URS-F-0126** — The system shall evaluate dynamic concurrency keys from safe expressions.
- [x] **URS-F-0127** — The system shall reserve scarce resources atomically before dispatch and release them idempotently.
- [x] **URS-F-0128** — The system shall prioritize admitted work without starving lower-priority tenants or queues.
- [x] **URS-F-0129** — The system shall apply per-tenant quotas for active executions, queued work, storage, logs and API usage.
- [x] **URS-F-0130** — The system shall explain admission decisions and expose queued position, age and limiting policy.
- [x] **URS-F-0131** — The system shall recover leaked reservations after crashes through lease expiry and reconciliation.

## Implementation completion evidence

- 2026-08-22 — EPIC-105 is complete. Flow and task DSL policies enforce global, tenant, namespace, flow, worker-group and safe-expression key limits through transaction-locked PostgreSQL reservations. Queue, cancel, fail, replace and skip decisions persist human-readable evidence; priority aging prevents starvation; completion releases reservations idempotently; lease reconciliation recovers lost owners. Tenant policy now bounds active and queued executions, storage, logs and API usage. Authorized admission detail, diagnostics and reconciliation APIs expose position, age and pressure. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`execution-semantics.md`](../../docs/architecture/execution-semantics.md), [`0019_admission_control.sql`](../../migrations/0019_admission_control.sql), [`test_admission_contract.py`](../../tests/test_admission_contract.py), and [`test_admission_control.py`](../../tests/adapters/postgres/test_admission_control.py).
- 2026-08-22 — Per the product owner's “defer and move forward” direction, the uninterrupted profile-M soak remains under EPIC-611 and the complete cross-subsystem reference dashboard/alert catalog remains under EPIC-607. EPIC-105 supplies admission diagnostics, queue age/pressure, worker-group routing and quota counters without claiming those later distributed qualifications.

## Non-functional requirements

- [ ] **URS-NFR-PERFORMANCE-005** — The distributed reference profile shall support large numbers of active executions and task runs. Target: Profile M target: 1,000 active task runs while accepting at least 100,000 executions over a 24-hour mixed-workload qualification run.
- [ ] **URS-NFR-USABILITY-002** — State, admission, retry, cache, policy and authorization decisions shall expose human-readable evidence to authorized users. Target: Decision evidence is present in all catalogued decision scenarios.
- [ ] **URS-NFR-OPERABILITY-005** — Operators shall see queue lag, worker capacity, admission pressure, database saturation, storage use and search lag. Target: All capacity signals are present in the reference dashboard and alert catalog.

## Dependencies

- EPIC-100
- EPIC-101

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
- Soak test with mixed short and long tasks.
- Scenario-based UI and API acceptance tests.
- Dashboard and telemetry contract tests.
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

- Functional requirements: URS-F-0124, URS-F-0125, URS-F-0126, URS-F-0127, URS-F-0128, URS-F-0129, URS-F-0130, URS-F-0131
- Non-functional requirements: URS-NFR-PERFORMANCE-005, URS-NFR-USABILITY-002, URS-NFR-OPERABILITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
