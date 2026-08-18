# EPIC-604 — Search and analytics projection backend

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `search`
- **Primary persona:** Operator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Scale read-heavy UI, log and analytics queries through rebuildable PostgreSQL projections, partitions and rollups.

## In scope

- [ ] **URS-F-0614** — The system shall project committed flow, execution, task-run, log, metric, asset and audit events into tenant-scoped PostgreSQL projection tables.
- [ ] **URS-F-0615** — The system shall version projection schemas, indexes, materialized views and rollups to support low-downtime rebuilds.
- [ ] **URS-F-0616** — The system shall resume projection from durable event positions after projector failure.
- [ ] **URS-F-0617** — The system shall rebuild selected tenants, resource types or time ranges without stopping orchestration.
- [ ] **URS-F-0618** — The system shall verify projected row counts, checksums and checkpoints against authoritative repositories.
- [ ] **URS-F-0619** — The system shall enforce tenant isolation during projection construction and every search or analytics query.
- [ ] **URS-F-0620** — The system shall partition, archive and expire projected data consistently with source retention policy.
- [ ] **URS-F-0621** — The system shall support disabling or rebuilding projections and falling back to bounded authoritative queries where feasible.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-005** — Core orchestration shall continue when optional search, telemetry, outbound webhook or analytics services are unavailable. Target: New and running executions continue within documented latency budgets during optional-service outage tests.
- [ ] **URS-NFR-SECURITY-001** — No API, event, cache, log, metric, search, storage or plugin path shall expose one tenant's protected data to another. Target: Zero cross-tenant findings in adversarial isolation test suite and pre-GA penetration test.

## Dependencies

- EPIC-409
- EPIC-601

## Architecture impact

- Primary bounded area: `search`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- PostgreSQL projection rebuild, isolation, retention and query-load tests.
- Dependency isolation and outage integration tests.
- Automated negative tests, database checks and independent penetration testing.
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

- Large log and analytics workloads may compete with orchestration writes
- Unbounded queries can exhaust database resources
- Projection drift can mislead operators if checkpoints are not verified

## Traceability

- Functional requirements: URS-F-0614, URS-F-0615, URS-F-0616, URS-F-0617, URS-F-0618, URS-F-0619, URS-F-0620, URS-F-0621
- Non-functional requirements: URS-NFR-RELIABILITY-005, URS-NFR-SECURITY-001
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
