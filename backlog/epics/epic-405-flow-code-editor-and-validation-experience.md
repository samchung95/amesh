# EPIC-405 — Flow code editor and validation experience

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Offer a productive schema-aware editor for the declarative flow language.

## In scope

- [ ] **URS-F-0438** — The system shall edit YAML with syntax highlighting, folding, formatting, search and multi-cursor support.
- [ ] **URS-F-0439** — The system shall provide schema-driven completion for core and installed plugin properties.
- [ ] **URS-F-0440** — The system shall show validation errors, warnings and documentation at exact source ranges.
- [ ] **URS-F-0441** — The system shall preview expression evaluation using a safe redacted sample context.
- [ ] **URS-F-0442** — The system shall diff current edits against active and historical revisions.
- [ ] **URS-F-0443** — The system shall preserve drafts locally and warn before navigating away from unsaved changes.
- [ ] **URS-F-0444** — The system shall validate and save through server APIs so client and server rules cannot diverge.
- [ ] **URS-F-0445** — The system shall support import, export, clone, disable and revision restore operations.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-001** — Flow validation shall return actionable errors tied to source locations. Target: p95 validation response below 1 second for a 5,000-line flow; every error includes code and location.
- [ ] **URS-NFR-USABILITY-004** — The GA web interface shall conform to WCAG 2.2 AA for supported workflows. Target: No critical or serious automated findings and manual keyboard and screen-reader acceptance.

## Dependencies

- EPIC-004
- EPIC-301
- EPIC-404

## Architecture impact

- Primary bounded area: `ui`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated browser, accessibility and manual usability tests.
- Editor benchmark and validation contract tests.
- Automated accessibility scan plus manual audit.
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

- Functional requirements: URS-F-0438, URS-F-0439, URS-F-0440, URS-F-0441, URS-F-0442, URS-F-0443, URS-F-0444, URS-F-0445
- Non-functional requirements: URS-NFR-USABILITY-001, URS-NFR-USABILITY-004
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
