# EPIC-101 — Worker protocol, leases and heartbeats

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Safely assign runnable work to workers and recover ownership after failure.

## In scope

- [x] **URS-F-0092** — The system shall register workers with stable identity, version, capabilities, labels, runner types and capacity.
- [x] **URS-F-0093** — The system shall lease task runs atomically to one eligible worker using expiring ownership and fencing tokens.
- [x] **URS-F-0094** — The system shall renew leases through heartbeats that include progress, resource use and cancellation acknowledgement.
- [x] **URS-F-0095** — The system shall reject stale completion or mutation attempts from a worker holding an obsolete fencing token.
- [x] **URS-F-0096** — The system shall requeue or fail task runs according to policy when a worker or lease disappears.
- [x] **URS-F-0097** — The system shall drain workers without assigning new work while allowing in-flight work to finish.
- [x] **URS-F-0098** — The system shall expose worker inventory, liveness, utilization, claimed work and compatibility status.
- [x] **URS-F-0099** — The system shall support pull-based and PostgreSQL-notification-assisted dispatch through one versioned worker protocol.

## Implementation completion evidence

- 2026-08-22 — EPIC-101 is complete. Versioned worker registration is stable by tenant/group/instance and advertises version, task capabilities, runner types, labels and capacity. PostgreSQL atomically binds each eligible `DispatchTaskRun` queue claim to the current task attempt with one database-time lease and monotonic fencing token; heartbeats renew both rows and persist progress, resource use and cancellation acknowledgement. Completion consumes the queue claim atomically, stale owners are rejected after reassignment, expired work follows explicit requeue/fail policy, and draining blocks new claims while live work can finish. Authorized `/api/v1/workers` inventory and fenced drain controls expose liveness, compatibility, claimed work and utilization. Pull and tenant-scoped LISTEN/NOTIFY use the same protocol-v1 repository. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`workers-and-runners.md`](../../docs/architecture/workers-and-runners.md), [`0016_worker_protocol.sql`](../../migrations/0016_worker_protocol.sql), [`worker_repository.py`](../../src/amesh/adapters/postgres/worker_repository.py), [`test_worker_protocol.py`](../../tests/worker/test_worker_protocol.py), [`test_worker_api.py`](../../tests/api/test_worker_api.py) and [`test_authorization_api.py`](../../tests/api/test_authorization_api.py). The shared Profile-M 60-minute dispatch benchmark and live network-partition/failover qualification remain with EPIC-603/601/611.

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

- Functional requirements: URS-F-0092, URS-F-0093, URS-F-0094, URS-F-0095, URS-F-0096, URS-F-0097, URS-F-0098, URS-F-0099
- Non-functional requirements: URS-NFR-RELIABILITY-003, URS-NFR-PERFORMANCE-004
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
