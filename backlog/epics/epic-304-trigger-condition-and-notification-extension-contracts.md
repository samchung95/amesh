# EPIC-304 — Trigger, condition and notification extension contracts

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Plugin developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Make non-task workflow extensions first-class and durable.

## In scope

- [ ] **URS-F-0321** — The system shall support polling triggers with durable checkpoints and normalized occurrence identities.
- [ ] **URS-F-0322** — The system shall support realtime triggers with connection lifecycle, backpressure and acknowledgement hooks.
- [ ] **URS-F-0323** — The system shall support conditions that return boolean results and explainable evaluation evidence.
- [ ] **URS-F-0324** — The system shall support notification plugins that receive typed lifecycle events and delivery policy.
- [ ] **URS-F-0325** — The system shall apply retry, timeout, cancellation and secret-scope behavior consistently across extension types.
- [ ] **URS-F-0326** — The system shall validate trigger and condition configuration without opening external connections.
- [ ] **URS-F-0327** — The system shall provide emulator and fault-injection fixtures for connector developers.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-103
- EPIC-300

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
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

- Functional requirements: URS-F-0321, URS-F-0322, URS-F-0323, URS-F-0324, URS-F-0325, URS-F-0326, URS-F-0327
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
