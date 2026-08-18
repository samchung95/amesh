# EPIC-101 — Worker protocol, leases and heartbeats

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Safely assign runnable work to workers and recover ownership after failure.

## In scope

- [ ] **URS-F-0092** — The system shall register workers with stable identity, version, capabilities, labels, runner types and capacity.
- [ ] **URS-F-0093** — The system shall lease task runs atomically to one eligible worker using expiring ownership and fencing tokens.
- [ ] **URS-F-0094** — The system shall renew leases through heartbeats that include progress, resource use and cancellation acknowledgement.
- [ ] **URS-F-0095** — The system shall reject stale completion or mutation attempts from a worker holding an obsolete fencing token.
- [ ] **URS-F-0096** — The system shall requeue or fail task runs according to policy when a worker or lease disappears.
- [ ] **URS-F-0097** — The system shall drain workers without assigning new work while allowing in-flight work to finish.
- [ ] **URS-F-0098** — The system shall expose worker inventory, liveness, utilization, claimed work and compatibility status.
- [ ] **URS-F-0099** — The system shall support pull-based and PostgreSQL-notification-assisted dispatch through one versioned worker protocol.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-003** — The platform shall prevent an expired scheduler, worker or service owner from committing after ownership transfers. Target: Zero accepted stale mutations in lease-expiry and partition tests.
- [ ] **URS-NFR-PERFORMANCE-004** — The distributed reference profile shall sustain task dispatch and completion processing without unbounded lag. Target: Profile M target: 50 task starts per second sustained for 60 minutes with p95 dispatch latency below 3 seconds and no unbounded queue lag.

## Dependencies

- EPIC-100

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
- Chaos tests with paused processes, network partitions and delayed completions.
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

- Functional requirements: URS-F-0092, URS-F-0093, URS-F-0094, URS-F-0095, URS-F-0096, URS-F-0097, URS-F-0098, URS-F-0099
- Non-functional requirements: URS-NFR-RELIABILITY-003, URS-NFR-PERFORMANCE-004
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
