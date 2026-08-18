# EPIC-404 — Web UI shell, navigation and accessibility

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** User
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide a responsive, permission-aware and accessible web application for all platform personas.

## In scope

- [ ] **URS-F-0430** — The system shall provide consistent navigation for dashboards, flows, executions, namespaces, assets, apps, plugins and administration.
- [ ] **URS-F-0431** — The system shall hide or disable actions based on server-authoritative permissions without relying on UI checks for enforcement.
- [ ] **URS-F-0432** — The system shall support deep links, browser history, saved views and tenant or namespace context.
- [ ] **URS-F-0433** — The system shall meet WCAG 2.2 AA for keyboard access, focus, semantics, contrast and assistive technology in GA scope.
- [ ] **URS-F-0434** — The system shall support responsive desktop and tablet layouts and a documented browser support policy.
- [ ] **URS-F-0435** — The system shall provide global search, command palette, notifications and error recovery.
- [ ] **URS-F-0436** — The system shall internationalize user-visible strings and locale-sensitive dates, numbers and time zones.
- [ ] **URS-F-0437** — The system shall collect opt-in product telemetry only under explicit deployment policy.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-004** — The GA web interface shall conform to WCAG 2.2 AA for supported workflows. Target: No critical or serious automated findings and manual keyboard and screen-reader acceptance.
- [ ] **URS-NFR-PRIVACY-001** — Product analytics and update checks shall be disabled by default or require an explicit informed opt-in. Target: No undeclared outbound connection occurs in the offline network test.

## Dependencies

- EPIC-400
- EPIC-500

## Architecture impact

- Primary bounded area: `ui`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated browser, accessibility and manual usability tests.
- Automated accessibility scan plus manual audit.
- Network capture in a clean reference deployment.
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

- Functional requirements: URS-F-0430, URS-F-0431, URS-F-0432, URS-F-0433, URS-F-0434, URS-F-0435, URS-F-0436, URS-F-0437
- Non-functional requirements: URS-NFR-USABILITY-004, URS-NFR-PRIVACY-001
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
