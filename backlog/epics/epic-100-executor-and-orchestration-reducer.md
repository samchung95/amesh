# EPIC-100 — Executor and orchestration reducer

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Drive executions from committed state and events without executing untrusted task code in the control plane.

## In scope

- [ ] **URS-F-0084** — The system shall create executions from manual, API, scheduled, event and subflow launches.
- [ ] **URS-F-0085** — The system shall expand runnable tasks only when dependencies and conditions are satisfied.
- [ ] **URS-F-0086** — The system shall apply task-run results to the workflow state through the deterministic reducer.
- [ ] **URS-F-0087** — The system shall coordinate sequential, parallel and dependency-driven branches without race-dependent outcomes.
- [ ] **URS-F-0088** — The system shall emit dispatch commands, downstream trigger events and terminal execution events transactionally.
- [ ] **URS-F-0089** — The system shall resume orchestration after executor restart without losing or duplicating logical progress.
- [ ] **URS-F-0090** — The system shall detect deadlocked or unsatisfiable execution graphs and terminate them with actionable diagnostics.
- [ ] **URS-F-0091** — The system shall support horizontally scaled executor instances through partitioning, leases or optimistic coordination.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-002** — The platform shall tolerate duplicate commands, events, trigger occurrences and task results without duplicate logical state transitions. Target: All conformance duplicate-injection scenarios produce one logical effect.
- [ ] **URS-NFR-RELIABILITY-004** — The execution reducer shall produce the same canonical state from the same ordered event stream and reducer version. Target: Byte-equivalent canonical snapshots across 100 repeated replays and supported platforms.
- [ ] **URS-NFR-PERFORMANCE-002** — Accepted execution launches shall become visible and eligible for orchestration promptly. Target: Provisional target: p95 below 2 seconds and p99 below 5 seconds in the standard profile.
- [ ] **URS-NFR-PERFORMANCE-004** — The distributed reference profile shall sustain task dispatch and completion processing without unbounded lag. Target: Profile M target: 50 task starts per second sustained for 60 minutes with p95 dispatch latency below 3 seconds and no unbounded queue lag.

## Dependencies

- EPIC-007
- EPIC-008
- EPIC-009

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
- Property-based and integration tests with duplicate and reordered delivery.
- Golden event-stream and property-based reducer tests.
- End-to-end launch benchmark under mixed workload.
- Published benchmark on a fixed reference topology.
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

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0084, URS-F-0085, URS-F-0086, URS-F-0087, URS-F-0088, URS-F-0089, URS-F-0090, URS-F-0091
- Non-functional requirements: URS-NFR-RELIABILITY-002, URS-NFR-RELIABILITY-004, URS-NFR-PERFORMANCE-002, URS-NFR-PERFORMANCE-004
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
