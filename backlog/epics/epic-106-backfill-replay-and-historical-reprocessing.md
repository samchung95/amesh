# EPIC-106 — Backfill, replay and historical reprocessing

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Run historical workload ranges safely and observably without confusing them with live trigger traffic.

## In scope

- [ ] **URS-F-0132** — The system shall create backfills over explicit time ranges, partitions or selected trigger occurrences.
- [ ] **URS-F-0133** — The system shall preview the number of executions and estimated impact before submitting a backfill.
- [ ] **URS-F-0134** — The system shall apply concurrency, rate, priority, labels, inputs and revision pinning to a backfill.
- [ ] **URS-F-0135** — The system shall pause, resume, cancel and monitor a backfill as a first-class resource.
- [ ] **URS-F-0136** — The system shall replay one or more prior executions while preserving source lineage.
- [ ] **URS-F-0137** — The system shall prevent accidental duplicate external effects through dry-run and idempotency guidance.
- [ ] **URS-F-0138** — The system shall track generated executions and aggregate success, failure, duration and cost.
- [ ] **URS-F-0139** — The system shall resume incomplete backfills after service restart without regenerating completed occurrences.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-102
- EPIC-104
- EPIC-105

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
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

- Functional requirements: URS-F-0132, URS-F-0133, URS-F-0134, URS-F-0135, URS-F-0136, URS-F-0137, URS-F-0138, URS-F-0139
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
