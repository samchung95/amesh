# EPIC-602 — PostgreSQL transactional backend

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `storage`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide a production-grade PostgreSQL backend for compact and horizontally scaled deployments.

## In scope

- [x] **URS-F-0598** — The system shall support current supported PostgreSQL major versions under an explicit compatibility matrix.
- [x] **URS-F-0599** — The system shall use connection pools, prepared statements, indexes and partitioning appropriate to execution workloads.
- [x] **URS-F-0600** — The system shall implement queue claims, locks and scheduler ownership without long blocking transactions.
- [x] **URS-F-0601** — The system shall support read replicas only for explicitly stale-tolerant queries.
- [ ] **URS-F-0602** — The system shall provide maintenance for table bloat, partitions, statistics and high-volume event retention.
- [ ] **URS-F-0603** — The system shall test managed PostgreSQL services and TLS configurations across major cloud providers.
- [x] **URS-F-0604** — The system shall publish query plans and benchmark thresholds for critical operations.
- [x] **URS-F-0605** — The system shall support backup-consistent object-storage metadata and point-in-time recovery procedures.

## Implementation completion evidence

- 2026-08-22 — The accepted EPIC-602 self-managed profile is complete. AMESH now centralizes bounded async pools, prepared-statement caching, pre-ping/recycle recovery and TLS verification; optional replica routing is limited to flow/execution list reads. PostgreSQL 15, 16, 17 and 18 each applied all 22 migrations and passed operations qualification. Critical plan/index and latency reports are reproducible, and a durable WAL-LSN/object-manifest checkpoint supports coordinated PITR procedures. Per product-owner direction, high-volume retention/partition rollout remains In Progress under EPIC-608 and credentialed AWS/Azure/GCP qualification is deferred to EPIC-706; no managed-cloud support claim is made. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`postgresql.md`](../../docs/operations/postgresql.md), [`qualify_postgres.py`](../../scripts/qualify_postgres.py), and [`test_operations_repository.py`](../../tests/adapters/postgres/test_operations_repository.py).

## Non-functional requirements

- [ ] **URS-NFR-AVAILABILITY-001** — A production compact deployment shall support a documented high-availability topology. Target: At least 99.9% monthly control-plane availability excluding declared maintenance.
- [ ] **URS-NFR-SECURITY-005** — The platform shall support encrypted metadata, object storage and secret-provider configurations. Target: Documented reference configurations use provider-managed or customer-managed encryption keys.

## Dependencies

- EPIC-008

## Architecture impact

- Primary bounded area: `storage`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Repository or storage adapter contract and fault-injection tests.
- Reference topology soak test and SLO calculation.
- Configuration audit and restore test.
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

- Functional requirements: URS-F-0598, URS-F-0599, URS-F-0600, URS-F-0601, URS-F-0602, URS-F-0603, URS-F-0604, URS-F-0605
- Non-functional requirements: URS-NFR-AVAILABILITY-001, URS-NFR-SECURITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
