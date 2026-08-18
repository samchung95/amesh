# EPIC-105 — Concurrency, admission control and fairness

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Protect shared capacity while offering predictable fairness across tenants, namespaces, flows and task types.

## In scope

- [ ] **URS-F-0124** — The system shall enforce execution and task concurrency limits at global, tenant, namespace, flow, worker-group and key scopes.
- [ ] **URS-F-0125** — The system shall support queue, cancel, fail, replace and skip behaviors when a limit is reached.
- [ ] **URS-F-0126** — The system shall evaluate dynamic concurrency keys from safe expressions.
- [ ] **URS-F-0127** — The system shall reserve scarce resources atomically before dispatch and release them idempotently.
- [ ] **URS-F-0128** — The system shall prioritize admitted work without starving lower-priority tenants or queues.
- [ ] **URS-F-0129** — The system shall apply per-tenant quotas for active executions, queued work, storage, logs and API usage.
- [ ] **URS-F-0130** — The system shall explain admission decisions and expose queued position, age and limiting policy.
- [ ] **URS-F-0131** — The system shall recover leaked reservations after crashes through lease expiry and reconciliation.

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

- Functional requirements: URS-F-0124, URS-F-0125, URS-F-0126, URS-F-0127, URS-F-0128, URS-F-0129, URS-F-0130, URS-F-0131
- Non-functional requirements: URS-NFR-PERFORMANCE-005, URS-NFR-USABILITY-002, URS-NFR-OPERABILITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
