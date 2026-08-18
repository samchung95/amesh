# EPIC-508 — Apps, forms and human approval tasks

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Business user
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Build governed human-in-the-loop experiences on top of durable workflows.

## In scope

- [ ] **URS-F-0558** — The system shall define versioned apps with forms, validation, display, permissions and flow launch behavior.
- [ ] **URS-F-0559** — The system shall generate forms from flow inputs while allowing explicit layout and help text.
- [ ] **URS-F-0560** — The system shall create durable approval tasks with assignees, groups, deadlines, escalation and delegation.
- [ ] **URS-F-0561** — The system shall support approve, reject, request changes, comment and attach artifact actions.
- [ ] **URS-F-0562** — The system shall resume waiting workflows exactly once after an authorized decision.
- [ ] **URS-F-0563** — The system shall record decision identity, time, reason and form values in audit and execution history.
- [ ] **URS-F-0564** — The system shall notify participants without exposing inaccessible execution data.
- [ ] **URS-F-0565** — The system shall provide embeddable or linkable app views protected by the same authorization model.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-205
- EPIC-401
- EPIC-500

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

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0558, URS-F-0559, URS-F-0560, URS-F-0561, URS-F-0562, URS-F-0563, URS-F-0564, URS-F-0565
- Non-functional requirements: none specifically mapped
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
