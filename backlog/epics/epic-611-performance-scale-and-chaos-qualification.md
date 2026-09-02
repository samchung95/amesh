# EPIC-611 — Performance, scale and chaos qualification

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `reliability`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Qualify correctness, performance and recovery under profile M load and adversarial failures on the on-premises Kubernetes reference topology.

## In scope

- [ ] **URS-F-0670** — The system shall maintain reproducible benchmarks for flow creation, execution launch, task dispatch, scheduling, logs, search and UI queries.
- [ ] **URS-F-0671** — The system shall measure throughput and latency at small, medium and large reference scales.
- [ ] **URS-F-0672** — The system shall publish hardware, topology, dataset and configuration with every benchmark result.
- [ ] **URS-F-0673** — The system shall load-test multi-tenant fairness, backfills, large DAGs, high log volume and plugin-heavy workloads.
- [ ] **URS-F-0674** — The system shall inject process, node, PostgreSQL, object-storage, network, runner and plugin failures.
- [ ] **URS-F-0675** — The system shall assert no accepted command is lost and no stale owner can commit after fencing.
- [ ] **URS-F-0676** — The system shall track performance regressions and require explicit approval beyond defined budgets.
- [ ] **URS-F-0677** — The system shall provide capacity-planning guidance from benchmark and telemetry evidence.

## MVP implementation progress

- 2026-08-21 — MVP fault injection completed 270 unique single-attempt executions with 270 task-pod, 27 server-pod and 13 worker-pod deletions and zero lost or duplicated persisted executions. The product owner explicitly deferred the remainder of the planned uninterrupted 24-hour run. Deferred acceptance criterion: run the checked-in soak for at least 86,400 elapsed seconds on a documented release-candidate topology, produce a passing final report with no failures, and independently verify every execution ID, task-run cardinality, attempt number and output before making broader availability, scale or production-readiness claims. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md) and [`scripts/soak_mvp.py`](../../scripts/soak_mvp.py). Profile-M load, scale-out and the broader epic remain open.

## Non-functional requirements

- [ ] **URS-NFR-PERFORMANCE-005** — The distributed reference profile shall support large numbers of active executions and task runs. Target: Profile M target: 1,000 active task runs while accepting at least 100,000 executions over a 24-hour mixed-workload qualification run.
- [ ] **URS-NFR-PERFORMANCE-009** — Adding eligible service replicas shall increase throughput until a documented shared dependency becomes limiting. Target: At least 70% scaling efficiency from two to four replicas on the reference distributed workload.
- [ ] **URS-NFR-PERFORMANCE-010** — The v1 distributed reference deployment shall qualify against the accepted profile M workload on the documented on-premises Kubernetes topology. Target: 100,000 executions per day, 1,000 active task runs, 50 sustained task starts per second and 10 million retained execution records.

## Dependencies

- EPIC-601
- EPIC-607

## Architecture impact

- Primary bounded area: `reliability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Fault-injection, replay and invariant tests.
- Soak test with mixed short and long tasks.
- Comparative scale-out benchmark.
- Published 24-hour mixed-workload, retention-query and failure-recovery benchmark on a fixed bill of materials.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- PostgreSQL queue, index and retention performance may require partitioning and carefully bounded projections.
- A benchmark is valid only when topology, dataset, configuration and failure conditions are reproducible.

## Traceability

- Functional requirements: URS-F-0670, URS-F-0671, URS-F-0672, URS-F-0673, URS-F-0674, URS-F-0675, URS-F-0676, URS-F-0677
- Non-functional requirements: URS-NFR-PERFORMANCE-005, URS-NFR-PERFORMANCE-009, URS-NFR-PERFORMANCE-010
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
