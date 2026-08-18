# EPIC-609 — Backup, restore and disaster recovery

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `reliability`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Restore a consistent platform state after data loss or regional failure.

## In scope

- [ ] **URS-F-0654** — The system shall document coordinated backup points for PostgreSQL metadata, queues and projections, object storage and configuration.
- [ ] **URS-F-0655** — The system shall automate backup verification through isolated restore tests.
- [ ] **URS-F-0656** — The system shall support PostgreSQL point-in-time recovery and object-version-aware restoration.
- [ ] **URS-F-0657** — The system shall rebuild disposable search and analytics projections from authoritative sources.
- [ ] **URS-F-0658** — The system shall detect and reconcile messages, leases and worker state after restoration.
- [ ] **URS-F-0659** — The system shall provide tenant-scoped export and import where isolation permits.
- [ ] **URS-F-0660** — The system shall publish reference recovery time and recovery point procedures with measured evidence.
- [ ] **URS-F-0661** — The system shall run scheduled disaster-recovery exercises and record unresolved gaps.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-006** — All stored artifacts and imported bundles shall be protected by cryptographic checksums and corruption detection. Target: Every stored object has a verified checksum; corruption drills are detected before consumption.
- [ ] **URS-NFR-AVAILABILITY-003** — The first stable release and later hardened profiles shall have documented and tested recovery point and recovery time objectives. Target: First stable release gate: RPO <= 48 hours and RTO <= 8 hours. Post-GA hardened reference target: RPO <= 4 hours and RTO <= 4 hours; the tighter target is not a v1 release blocker.

## Dependencies

- EPIC-602
- EPIC-603
- EPIC-605

## Architecture impact

- Primary bounded area: `reliability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Fault-injection, replay and invariant tests.
- Storage adapter conformance and corruption-injection tests.
- Isolated restore exercise on the on-premises Kubernetes reference topology, with measured data-loss window and service-restoration time.
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

- The v1 RPO <= 48 hours and RTO <= 8 hours are deliberately minimal and unsuitable for every production workload.
- PostgreSQL and object-storage recovery points must be coordinated to avoid inconsistent restored state.

## Traceability

- Functional requirements: URS-F-0654, URS-F-0655, URS-F-0656, URS-F-0657, URS-F-0658, URS-F-0659, URS-F-0660, URS-F-0661
- Non-functional requirements: URS-NFR-RELIABILITY-006, URS-NFR-AVAILABILITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
