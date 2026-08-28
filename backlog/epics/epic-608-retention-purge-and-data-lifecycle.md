# EPIC-608 — Retention, purge and data lifecycle

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Control metadata, logs, metrics, artifacts and audit growth safely.

## In scope

- [x] **URS-F-0646** — The system shall define retention by resource type at instance, tenant, namespace and label scopes.
- [x] **URS-F-0647** — The system shall preview affected record and byte counts before purge.
- [x] **URS-F-0648** — The system shall purge in bounded resumable batches that do not block active orchestration.
- [x] **URS-F-0649** — The system shall preserve referential integrity across executions, task runs, events, logs, metrics, artifacts, caches and indexes.
- [x] **URS-F-0650** — The system shall honor legal holds and independent audit-retention requirements.
- [x] **URS-F-0651** — The system shall delete object storage and search projections only after authoritative metadata decisions.
- [x] **URS-F-0652** — The system shall record purge job progress, failures, retries and evidence.
- [x] **URS-F-0653** — The system shall support manual purge and scheduled lifecycle policies.

## Implementation completion evidence

- 2026-08-23 — EPIC-608 functional scope is complete. AMESH defines versioned retention policies for execution, log, metric, artifact and cache resources with instance, tenant, namespace and label precedence; previews exact eligible/protected/active record and byte impact; and requires exact destructive confirmation in the API, CLI and Lifecycle administration view. Terminal data is purged in bounded resumable jobs while execution tombstones preserve referential integrity, legal holds protect matching metadata and provider objects, and object/search deletion follows the authoritative PostgreSQL decision. Durable progress, failures, retries, evidence, manual execution and scheduled maintenance are covered on a fresh PostgreSQL database. Both generated API contracts and the retention/data-inventory runbooks are current. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`retention.md`](../../docs/operations/retention.md), [`test_retention_repository.py`](../../tests/adapters/postgres/test_retention_repository.py), and [`test_retention_api.py`](../../tests/api/test_retention_api.py).

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-005** — Destructive UI and CLI operations shall present impact, scope and recovery consequences before execution. Target: All destructive-action catalog entries have preview or explicit force semantics.
- [ ] **URS-NFR-PRIVACY-002** — The platform shall retain only data required by configured orchestration, audit and operational policy. Target: Data inventory maps every persisted field to purpose, retention and sensitivity.

## Dependencies

- EPIC-008
- EPIC-010
- EPIC-504

## Architecture impact

- Primary bounded area: `operations`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Reference deployment, upgrade and failure-recovery tests.
- Interaction and CLI contract tests.
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

- External object-store lifecycle/provider qualification and long-duration high-volume purge soak remain deferred; local evidence uses the verified object-store contract and bounded PostgreSQL batches.
- Shared destructive-action usability and privacy NFRs remain open until every mapped epic and the full persisted-field inventory are qualified.

## Traceability

- Functional requirements: URS-F-0646, URS-F-0647, URS-F-0648, URS-F-0649, URS-F-0650, URS-F-0651, URS-F-0652, URS-F-0653
- Non-functional requirements: URS-NFR-USABILITY-005, URS-NFR-PRIVACY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
