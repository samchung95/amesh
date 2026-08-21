# EPIC-009 — PostgreSQL transport, inbox and transactional outbox

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `messaging`
- **Primary persona:** Engine developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide durable PostgreSQL-backed work delivery while preserving transactional correctness, idempotency and replayability.

## In scope

- [x] **URS-F-0068** — The system shall define versioned message envelopes with identity, type, tenant, correlation, causation, timestamp and trace context.
- [x] **URS-F-0069** — The system shall write outbound messages to a transactional outbox in the same transaction as state changes.
- [x] **URS-F-0070** — The system shall deduplicate inbound messages through a durable inbox before applying side effects.
- [x] **URS-F-0071** — The system shall support ordered processing by execution or trigger partition key.
- [x] **URS-F-0072** — The system shall retry transient publication and consumption failures with bounded backoff and dead-letter handling.
- [x] **URS-F-0073** — The system shall expose lag, redelivery, poison-message and dead-letter diagnostics.
- [x] **URS-F-0074** — The system shall provide a PostgreSQL-backed durable queue adapter with transactional outbox, inbox, claim, retry and dead-letter semantics.
- [x] **URS-F-0075** — The system shall document at-least-once delivery and external side-effect idempotency responsibilities.

## MVP implementation progress

- 2026-08-21 — W1 verified the accepted PostgreSQL transport slice: idempotent enqueue, `SKIP LOCKED` claims, expiring leases, monotonic fencing, transactional outbox publication, consumer-inbox deduplication, process-crash recovery and lane-specific `LISTEN/NOTIFY` wake-ups without polling. Evidence: [`TESTLOG.md`](../../TESTLOG.md) and [`test_durable_transport.py`](../../tests/adapters/postgres/test_durable_transport.py). Dead-letter policy and the broader parity epic remain open.

## Implementation completion evidence

- 2026-08-22 — EPIC-009 is complete. The versioned public envelope includes identity, tenant, correlation, causation, timestamp and trace context with a checked-in schema; PostgreSQL provides transactional event outbox publication, consumer inbox deduplication, tenant/lane/partition head-of-line ordering, `SKIP LOCKED` claims, expiring leases and fencing; immutable message IDs reject changed content; configurable queue/outbox retry bounds atomically create tenant-isolated payload-safe dead-letter evidence; authorized replay retains resolution history; and diagnostics expose lag, claims, redelivery, poison and outbox/dead-letter totals. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`messaging.md`](../../docs/architecture/messaging.md), [`postgresql-transport.md`](../../docs/architecture/postgresql-transport.md), [`message-envelope.schema.json`](../../schemas/message-envelope.schema.json), [`durable_transport.py`](../../src/amesh/adapters/postgres/durable_transport.py), [`0013_transport_dead_letters.sql`](../../migrations/0013_transport_dead_letters.sql), and [`test_durable_transport.py`](../../tests/adapters/postgres/test_durable_transport.py). Shared reliability, modularity and backend-portability NFRs remain In Progress for their other owning epics and distributed failover qualification.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-001** — The platform shall not lose an accepted state-changing command after the API or durable PostgreSQL transport acknowledges it. Target: Zero lost acknowledged commands in crash-consistency and failover tests.
- [ ] **URS-NFR-RELIABILITY-002** — The platform shall tolerate duplicate commands, events, trigger occurrences and task results without duplicate logical state transitions. Target: All conformance duplicate-injection scenarios produce one logical effect.
- [ ] **URS-NFR-MAINTAINABILITY-001** — Core domain and reducer logic shall not depend directly on web frameworks, PostgreSQL claim mechanics, search projections or object-storage SDKs. Target: Architecture dependency tests enforce allowed module directions.
- [ ] **URS-NFR-PORTABILITY-003** — Core transport semantics shall be isolated from PostgreSQL claim mechanics, while object storage, secret providers, model providers and task runners shall use documented capability interfaces. Target: PostgreSQL remains the sole supported internal durable transport and metadata database; every backend category explicitly marked extensible passes its conformance suite.

## Dependencies

- EPIC-007
- EPIC-008

## Architecture impact

- Primary bounded area: `messaging`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Delivery, ordering, duplicate and outage conformance tests.
- Fault-injection tests that terminate services and PostgreSQL connections at every commit, claim and acknowledgement boundary.
- Property-based and integration tests with duplicate and reordered delivery.
- Static architecture test in CI.
- Static architecture checks plus adapter contract tests for each extensible backend category.
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

- Functional requirements: URS-F-0068, URS-F-0069, URS-F-0070, URS-F-0071, URS-F-0072, URS-F-0073, URS-F-0074, URS-F-0075
- Non-functional requirements: URS-NFR-RELIABILITY-001, URS-NFR-RELIABILITY-002, URS-NFR-MAINTAINABILITY-001, URS-NFR-PORTABILITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
