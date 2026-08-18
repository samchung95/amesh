# EPIC-610 — Upgrades, migrations and LTS policy

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Upgrade the platform predictably without silently changing workflow behavior.

## In scope

- [ ] **URS-F-0662** — The system shall publish supported upgrade paths, LTS windows and minimum compatible component versions.
- [ ] **URS-F-0663** — The system shall run pre-upgrade checks for schema, configuration, plugins, flow syntax, storage and capacity.
- [ ] **URS-F-0664** — The system shall support rolling upgrades where message and database compatibility permits.
- [ ] **URS-F-0665** — The system shall block unsafe version skew and explain the required remediation.
- [ ] **URS-F-0666** — The system shall upcast persisted events and migrate flow or plugin configuration through explicit tools.
- [ ] **URS-F-0667** — The system shall retain a rollback window or provide restoration guidance for irreversible migrations.
- [ ] **URS-F-0668** — The system shall test upgrades from every supported LTS release with representative workloads.
- [ ] **URS-F-0669** — The system shall produce a post-upgrade verification report and unresolved compatibility warnings.

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

- Functional requirements: URS-F-0662, URS-F-0663, URS-F-0664, URS-F-0665, URS-F-0666, URS-F-0667, URS-F-0668, URS-F-0669
- Non-functional requirements: URS-NFR-AVAILABILITY-004, URS-NFR-MAINTAINABILITY-002, URS-NFR-MAINTAINABILITY-003, URS-NFR-OPERABILITY-006
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
