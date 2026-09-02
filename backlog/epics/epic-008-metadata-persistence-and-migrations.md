# EPIC-008 — Metadata persistence and migrations

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `storage`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Persist platform metadata transactionally with clear repository boundaries and safe schema evolution.

## In scope

- [x] **URS-F-0060** — The system shall provide repository interfaces for flows, revisions, executions, task runs, triggers, workers, logs, metrics, assets and governance resources.
- [x] **URS-F-0061** — The system shall implement PostgreSQL as the reference transactional backend.
- [x] **URS-F-0062** — The system shall use explicit transactions and isolation levels for scheduling, claiming, state transitions and outbox publication.
- [x] **URS-F-0063** — The system shall apply ordered forward migrations with preflight checks and rollback guidance.
- [x] **URS-F-0064** — The system shall support online-compatible migrations for rolling upgrades whenever feasible.
- [x] **URS-F-0065** — The system shall protect invariants with database constraints in addition to application validation.
- [x] **URS-F-0066** — The system shall expose health, pool saturation, slow query and migration status metrics.
- [x] **URS-F-0067** — The system shall provide deterministic seed data and ephemeral test database support.

## Implementation completion evidence

- 2026-08-22 — EPIC-008 is complete. AMESH now exposes cohesive PostgreSQL repositories for flows/revisions/executions/task runs, triggers/workers/logs/metrics/assets, tenants, authorization governance and credentials; materializes immutable trigger metadata in the flow transaction; uses explicit READ COMMITTED tenant transactions and SERIALIZABLE locked migrations; validates an ordered migration manifest with preflight, online-compatibility and rollback guidance; protects metadata and state invariants with constraints and forced tenant RLS; reports database readiness, pool, query and migration signals; and creates guarded ephemeral databases with canonical schema/seed fingerprints. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`metadata-storage.md`](../../docs/operations/metadata-storage.md), [`metadata_repository.py`](../../src/amesh/adapters/postgres/metadata_repository.py), [`migrations.py`](../../src/amesh/entrypoints/migrations.py), [`0012_metadata_repository.sql`](../../migrations/0012_metadata_repository.sql), [`test_metadata_repository.py`](../../tests/adapters/postgres/test_metadata_repository.py), and [`test_migration_contract.py`](../../tests/adapters/postgres/test_migration_contract.py). Shared reliability, migration-LTS and privacy-retention NFRs remain In Progress for their other owning epics.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-001** — The platform shall not lose an accepted state-changing command after the API or durable PostgreSQL transport acknowledges it. Target: Zero lost acknowledged commands in crash-consistency and failover tests.
- [ ] **URS-NFR-MAINTAINABILITY-003** — Schema, event and resource migrations shall be repeatable and produce the same canonical result. Target: Repeated migration fixtures produce identical checksums.
- [ ] **URS-NFR-PRIVACY-002** — The platform shall retain only data required by configured orchestration, audit and operational policy. Target: Data inventory maps every persisted field to purpose, retention and sensitivity.

## Dependencies

- EPIC-002
- EPIC-007

## Architecture impact

- Primary bounded area: `storage`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Repository or storage adapter contract and fault-injection tests.
- Fault-injection tests that terminate services and PostgreSQL connections at every commit, claim and acknowledgement boundary.
- Migration golden tests.
- Privacy and schema review.
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

- Functional requirements: URS-F-0060, URS-F-0061, URS-F-0062, URS-F-0063, URS-F-0064, URS-F-0065, URS-F-0066, URS-F-0067
- Non-functional requirements: URS-NFR-RELIABILITY-001, URS-NFR-MAINTAINABILITY-003, URS-NFR-PRIVACY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
