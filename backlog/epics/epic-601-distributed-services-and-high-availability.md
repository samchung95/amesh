# EPIC-601 — Distributed services and high availability

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Scale platform roles independently and survive ordinary node or zone failures.

## In scope

- [x] **URS-F-0590** — The system shall run webserver, executor, scheduler, worker, indexer and maintenance roles as independent scalable services.
- [x] **URS-F-0591** — The system shall assign partitioned work through durable messages, leases and fencing rather than node affinity.
- [x] **URS-F-0592** — The system shall continue orchestration through the loss and replacement of any stateless service instance.
- [x] **URS-F-0593** — The system shall support multiple replicas across failure zones with documented quorum dependencies.
- [x] **URS-F-0594** — The system shall drain, upgrade and replace instances without losing accepted work.
- [x] **URS-F-0595** — The system shall expose service registry, version skew, ownership, partition and failover status.
- [x] **URS-F-0596** — The system shall detect split-brain or stale ownership and reject unfenced mutations.
- [x] **URS-F-0597** — The system shall publish tested reference topologies for small, medium and large deployments.

## Implementation completion evidence

- 2026-08-22 — EPIC-601 functional scope is complete. Migration 0025 adds a global service registry with incarnation generations that fence replaced processes. Webserver, executor, scheduler, worker, indexer and maintenance now run as independently scalable roles; scheduler/worker/queue work retains PostgreSQL leases and fences. Instance-admin APIs expose liveness, readiness, version skew, failure domains, ownership, partition strategy and failover status, and perform version-checked audited drains. Helm defaults and tested small/medium/large profiles add rolling updates, PDBs, zone spread, pre-stop drain and distinct readiness/liveness behavior. A real role-process test registered, accepted a drain, stopped before another cycle and persisted STOPPED; stale incarnation and drain versions were rejected. Helm 4.0.0 lint passed for all profiles, and a clean 25-migration database ran 213 passing tests with four environment skips. Per product-owner direction, the 24-hour 100,000-execution workload, measured two-to-four replica efficiency, and credentialed dependency failover certification remain In Progress under EPIC-611/606/607; no such capacity or external quorum claim is made. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`high-availability.md`](../../docs/operations/high-availability.md), [`test_service_registry.py`](../../tests/adapters/postgres/test_service_registry.py), and [`test_helm_ha.py`](../../tests/test_helm_ha.py).

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-003** — The platform shall prevent an expired scheduler, worker or service owner from committing after ownership transfers. Target: Zero accepted stale mutations in lease-expiry and partition tests.
- [ ] **URS-NFR-RELIABILITY-007** — Automated reconciliation shall converge recoverable invariant violations without creating new violations. Target: Reference fault scenarios converge within 10 minutes after dependencies recover.
- [ ] **URS-NFR-RELIABILITY-008** — Temporal decisions shall tolerate bounded clock skew and use monotonic time for local deadlines where possible. Target: Correct schedule, lease and timeout behavior with plus or minus 30 seconds node skew.
- [ ] **URS-NFR-AVAILABILITY-002** — The distributed topology shall tolerate loss of any one stateless service instance without operator intervention. Target: No accepted work lost; service recovers within 60 seconds of instance loss.
- [ ] **URS-NFR-AVAILABILITY-004** — Planned maintenance and rolling upgrades shall drain or transfer owned work without silent loss. Target: Zero lost accepted work and no more than one configured scheduling-delay window.
- [ ] **URS-NFR-PERFORMANCE-005** — The distributed reference profile shall support large numbers of active executions and task runs. Target: Profile M target: 1,000 active task runs while accepting at least 100,000 executions over a 24-hour mixed-workload qualification run.
- [ ] **URS-NFR-PERFORMANCE-009** — Adding eligible service replicas shall increase throughput until a documented shared dependency becomes limiting. Target: At least 70% scaling efficiency from two to four replicas on the reference distributed workload.
- [ ] **URS-NFR-OPERABILITY-001** — Each service shall expose distinct liveness, readiness and detailed dependency health. Target: Reference orchestrator removes unready instances without restarting healthy but degraded processes unnecessarily.
- [ ] **URS-NFR-OPERABILITY-005** — Operators shall see queue lag, worker capacity, admission pressure, database saturation, storage use and search lag. Target: All capacity signals are present in the reference dashboard and alert catalog.

## Dependencies

- EPIC-101
- EPIC-108
- EPIC-603

## Architecture impact

- Primary bounded area: `operations`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Reference deployment, upgrade and failure-recovery tests.
- Chaos tests with paused processes, network partitions and delayed completions.
- End-to-end recovery suite with invariant counters.
- Virtual-clock and multi-node skew tests.
- Multi-replica chaos and zone-spread tests.
- Upgrade and drain conformance suite.
- Soak test with mixed short and long tasks.
- Comparative scale-out benchmark.
- Kubernetes and Compose health tests.
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

- Functional requirements: URS-F-0590, URS-F-0591, URS-F-0592, URS-F-0593, URS-F-0594, URS-F-0595, URS-F-0596, URS-F-0597
- Non-functional requirements: URS-NFR-RELIABILITY-003, URS-NFR-RELIABILITY-007, URS-NFR-RELIABILITY-008, URS-NFR-AVAILABILITY-002, URS-NFR-AVAILABILITY-004, URS-NFR-PERFORMANCE-005, URS-NFR-PERFORMANCE-009, URS-NFR-OPERABILITY-001, URS-NFR-OPERABILITY-005
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
