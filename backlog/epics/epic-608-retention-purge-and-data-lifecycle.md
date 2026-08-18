# EPIC-608 — Retention, purge and data lifecycle

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Control metadata, logs, metrics, artifacts and audit growth safely.

## In scope

- [ ] **URS-F-0646** — The system shall define retention by resource type at instance, tenant, namespace and label scopes.
- [ ] **URS-F-0647** — The system shall preview affected record and byte counts before purge.
- [ ] **URS-F-0648** — The system shall purge in bounded resumable batches that do not block active orchestration.
- [ ] **URS-F-0649** — The system shall preserve referential integrity across executions, task runs, events, logs, metrics, artifacts, caches and indexes.
- [ ] **URS-F-0650** — The system shall honor legal holds and independent audit-retention requirements.
- [ ] **URS-F-0651** — The system shall delete object storage and search projections only after authoritative metadata decisions.
- [ ] **URS-F-0652** — The system shall record purge job progress, failures, retries and evidence.
- [ ] **URS-F-0653** — The system shall support manual purge and scheduled lifecycle policies.

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

- Functional requirements: URS-F-0646, URS-F-0647, URS-F-0648, URS-F-0649, URS-F-0650, URS-F-0651, URS-F-0652, URS-F-0653
- Non-functional requirements: URS-NFR-USABILITY-005, URS-NFR-PRIVACY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
