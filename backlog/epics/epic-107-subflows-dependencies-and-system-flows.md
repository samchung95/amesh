# EPIC-107 — Subflows, dependencies and system flows

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Compose workflows while preserving parent-child state, outputs, cancellation and authorization.

## In scope

- [ ] **URS-F-0140** — The system shall invoke another flow by tenant, namespace, identifier and selected or current revision.
- [ ] **URS-F-0141** — The system shall pass typed inputs, labels, correlation and trace context from parent to child.
- [ ] **URS-F-0142** — The system shall choose synchronous wait, asynchronous launch or detached invocation semantics.
- [ ] **URS-F-0143** — The system shall propagate success, failure, cancellation, pause and restart according to explicit policy.
- [ ] **URS-F-0144** — The system shall map child outputs and artifacts back to the parent with schema validation.
- [ ] **URS-F-0145** — The system shall prevent recursive invocation beyond configured depth and detect dependency cycles.
- [ ] **URS-F-0146** — The system shall support privileged system flows for notifications, governance and operational automation.
- [ ] **URS-F-0147** — The system shall authorize parent and child resources independently and record cross-namespace access.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-100

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

- Functional requirements: URS-F-0140, URS-F-0141, URS-F-0142, URS-F-0143, URS-F-0144, URS-F-0145, URS-F-0146, URS-F-0147
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
