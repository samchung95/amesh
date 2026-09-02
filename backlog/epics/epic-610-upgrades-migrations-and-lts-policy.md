# EPIC-610 — Upgrades, migrations and LTS policy

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Upgrade the platform predictably without silently changing workflow behavior.

## In scope

- [x] **URS-F-0662** — The system shall publish supported upgrade paths, LTS windows and minimum compatible component versions.
- [x] **URS-F-0663** — The system shall run pre-upgrade checks for schema, configuration, plugins, flow syntax, storage and capacity.
- [x] **URS-F-0664** — The system shall support rolling upgrades where message and database compatibility permits.
- [x] **URS-F-0665** — The system shall block unsafe version skew and explain the required remediation.
- [x] **URS-F-0666** — The system shall upcast persisted events and migrate flow or plugin configuration through explicit tools.
- [x] **URS-F-0667** — The system shall retain a rollback window or provide restoration guidance for irreversible migrations.
- [x] **URS-F-0668** — The system shall test upgrades from every supported LTS release with representative workloads.
- [x] **URS-F-0669** — The system shall produce a post-upgrade verification report and unresolved compatibility warnings.

## Implementation completion evidence

- 2026-08-23 — EPIC-610 is complete for the locally reproducible upgrade profile. A versioned checked-in release catalog publishes the 0.1.0 and 0.2.0 LTS windows, component/protocol minimums, schema boundaries, directed rolling path, capacity limits, 168-hour rollback window and restoration guidance. Authorized API, CLI and Administration UI preflight/postflight reports gate schema checksums, expand-only migrations, runtime configuration, plugins, every stored flow revision, object storage, capacity, service skew and event schemas; unsafe service registration is rejected with remediation. The migration runner targets exact release boundaries, bounded resumable event upcasts require exact confirmation and write audit evidence, and explicit flow/plugin configuration migration never publishes silently. A fresh PostgreSQL fixture upgraded a representative persisted flow, execution and schema-1 event from migration 0032 through 0054, produced pre/post reports and completed the event upcast. Domain, repository, API, CLI, OpenAPI, four SDK, frontend and production-build checks passed. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`upgrades.md`](../../docs/operations/upgrades.md), [`040-declarative-upgrade-compatibility-gates.md`](../../docs/adr/040-declarative-upgrade-compatibility-gates.md), [`upgrade-policy.json`](../../src/amesh/resources/upgrade-policy.json), [`test_upgrade_repository.py`](../../tests/adapters/postgres/test_upgrade_repository.py), and [`test_upgrade_api.py`](../../tests/api/test_upgrade_api.py).

## Non-functional requirements

- [ ] **URS-NFR-AVAILABILITY-004** — Planned maintenance and rolling upgrades shall drain or transfer owned work without silent loss. Target: Zero lost accepted work and no more than one configured scheduling-delay window.
- [ ] **URS-NFR-MAINTAINABILITY-002** — Public DSL, API, event and plugin contracts shall follow documented semantic-versioning and deprecation rules. Target: No breaking contract change enters a minor or patch release without an approved exception.
- [ ] **URS-NFR-MAINTAINABILITY-003** — Schema, event and resource migrations shall be repeatable and produce the same canonical result. Target: Repeated migration fixtures produce identical checksums.
- [ ] **URS-NFR-OPERABILITY-006** — Every release containing irreversible migration or behavior change shall publish recovery and rollback guidance. Target: Release is blocked when migration classification lacks an operator procedure.

## Dependencies

- EPIC-001
- EPIC-008
- EPIC-301

## Architecture impact

- Primary bounded area: `operations`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Reference deployment, upgrade and failure-recovery tests.
- Upgrade and drain conformance suite.
- Automated schema and API compatibility checks.
- Migration golden tests.
- Release metadata validation.
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

- External multi-node work-transfer and dependency failover qualification remains deferred under URS-NFR-AVAILABILITY-004; EPIC-610 verifies the locally reproducible release, schema, skew and migration path without making that broader availability claim.
- Only catalog-declared directed LTS paths are supported; operators must publish and test a new path before upgrading from another release.

## Traceability

- Functional requirements: URS-F-0662, URS-F-0663, URS-F-0664, URS-F-0665, URS-F-0666, URS-F-0667, URS-F-0668, URS-F-0669
- Non-functional requirements: URS-NFR-AVAILABILITY-004, URS-NFR-MAINTAINABILITY-002, URS-NFR-MAINTAINABILITY-003, URS-NFR-OPERABILITY-006
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
