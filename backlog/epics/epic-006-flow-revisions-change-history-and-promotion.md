# EPIC-006 — Flow revisions, change history and promotion

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `domain`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Make workflow definitions immutable by revision and safely promotable across environments.

## In scope

- [ ] **URS-F-0045** — The system shall create a new immutable revision for each semantic flow change.
- [ ] **URS-F-0046** — The system shall show human-readable and machine-readable diffs between revisions.
- [ ] **URS-F-0047** — The system shall pin every execution to the exact flow revision and plugin resolution set used at launch.
- [ ] **URS-F-0048** — The system shall restore or clone an earlier revision without rewriting history.
- [ ] **URS-F-0049** — The system shall support draft, active, disabled and archived lifecycle states.
- [ ] **URS-F-0050** — The system shall attach actor, source, commit, environment and deployment metadata to revisions.
- [ ] **URS-F-0051** — The system shall prevent incompatible revision deletion while executions or audit records reference it.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-004

## Architecture impact

- Primary bounded area: `domain`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Domain model unit and serialization compatibility tests.
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

- Functional requirements: URS-F-0045, URS-F-0046, URS-F-0047, URS-F-0048, URS-F-0049, URS-F-0050, URS-F-0051
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
