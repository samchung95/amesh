# EPIC-000 — Clean-room governance and parity baseline

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Maintainer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Establish a defensible, repeatable method for reproducing observable capabilities without copying protected expression.

## In scope

- [ ] **URS-F-0001** — The system shall maintain a version-pinned parity inventory against Kestra v1.3.30 and its documented public behavior.
- [ ] **URS-F-0002** — The system shall record source provenance for every compatibility requirement and prohibit copying source code, UI assets, trademarks, or documentation prose.
- [ ] **URS-F-0003** — The system shall separate reference researchers from implementers when a strict clean-room mode is selected.
- [ ] **URS-F-0004** — The system shall run automated similarity and license scans before every release.
- [ ] **URS-F-0005** — The system shall document trademark-safe naming, attribution, notices, and contribution provenance.
- [ ] **URS-F-0006** — The system shall track parity gaps, intentional differences, deferred features, and evidence in a machine-readable matrix.
- [ ] **URS-F-0007** — The system shall provide a repeatable procedure for rebasing the parity target to a later upstream release.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- None

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
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

- Accidental source or UI copying
- Ambiguous compatibility claims
- Trademark confusion

## Traceability

- Functional requirements: URS-F-0001, URS-F-0002, URS-F-0003, URS-F-0004, URS-F-0005, URS-F-0006, URS-F-0007
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
