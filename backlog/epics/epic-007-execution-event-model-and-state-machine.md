# EPIC-007 — Execution event model and state machine

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Engine developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Define the authoritative deterministic state transitions for workflows, tasks, triggers and service components.

## In scope

- [x] **URS-F-0052** — The system shall represent all commands, decisions and state changes as typed versioned events.
- [x] **URS-F-0053** — The system shall enforce legal execution and task-run state transitions through a pure deterministic reducer.
- [x] **URS-F-0054** — The system shall retain immutable transition history with actor, reason, correlation and causation identifiers.
- [x] **URS-F-0055** — The system shall make duplicate commands and events idempotent by stable idempotency keys.
- [x] **URS-F-0056** — The system shall support replay from event history to rebuild current execution state.
- [x] **URS-F-0057** — The system shall record rejected transitions and invariant violations without corrupting state.
- [x] **URS-F-0058** — The system shall version the event schema and provide upcasters for supported historical versions.
- [x] **URS-F-0059** — The system shall publish committed events only after the corresponding state transaction succeeds.

## Implementation completion evidence

- 2026-08-22 — EPIC-007 is complete. AMESH now defines immutable, typed and versioned execution/task-run commands, events, snapshots, accepted decisions and rejected decisions; enforces both lifecycles through pure transition tables; deduplicates stable command/event identities; replays canonical history; upcasts execution event schema v1 to v2; persists actor, reason, correlation and causation metadata plus task history and rejection evidence; and creates each event outbox record transactionally through PostgreSQL triggers. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`execution-semantics.md`](../../docs/architecture/execution-semantics.md), [`execution.py`](../../src/amesh/domain/execution.py), [`reducer.py`](../../src/amesh/domain/reducer.py), [`0011_execution_event_model.sql`](../../migrations/0011_execution_event_model.sql), [`test_reducer.py`](../../tests/test_reducer.py), and [`test_postgres_executor.py`](../../tests/executor/test_postgres_executor.py). Shared reliability and maintainability NFRs remain In Progress for their other owning epics and distributed failover qualification.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-001** — The platform shall not lose an accepted state-changing command after the API or durable PostgreSQL transport acknowledges it. Target: Zero lost acknowledged commands in crash-consistency and failover tests.
- [ ] **URS-NFR-RELIABILITY-002** — The platform shall tolerate duplicate commands, events, trigger occurrences and task results without duplicate logical state transitions. Target: All conformance duplicate-injection scenarios produce one logical effect.
- [ ] **URS-NFR-RELIABILITY-004** — The execution reducer shall produce the same canonical state from the same ordered event stream and reducer version. Target: Byte-equivalent canonical snapshots across 100 repeated replays and supported platforms.
- [ ] **URS-NFR-MAINTAINABILITY-001** — Core domain and reducer logic shall not depend directly on web frameworks, PostgreSQL claim mechanics, search projections or object-storage SDKs. Target: Architecture dependency tests enforce allowed module directions.

## Dependencies

- EPIC-002

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
- Fault-injection tests that terminate services and PostgreSQL connections at every commit, claim and acknowledgement boundary.
- Property-based and integration tests with duplicate and reordered delivery.
- Golden event-stream and property-based reducer tests.
- Static architecture test in CI.
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

- Functional requirements: URS-F-0052, URS-F-0053, URS-F-0054, URS-F-0055, URS-F-0056, URS-F-0057, URS-F-0058, URS-F-0059
- Non-functional requirements: URS-NFR-RELIABILITY-001, URS-NFR-RELIABILITY-002, URS-NFR-RELIABILITY-004, URS-NFR-MAINTAINABILITY-001
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
