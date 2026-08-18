# EPIC-406 — Visual no-code editor and topology model

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Author and understand workflows visually without creating a second incompatible representation.

## In scope

- [ ] **URS-F-0446** — The system shall render the canonical flow model as an interactive task and dependency graph.
- [ ] **URS-F-0447** — The system shall add, configure, connect, reorder, group and remove supported tasks through schema-generated forms.
- [ ] **URS-F-0448** — The system shall round-trip supported visual edits to YAML without changing unrelated semantic content.
- [ ] **URS-F-0449** — The system shall fall back to code editing for constructs the visual editor cannot represent.
- [ ] **URS-F-0450** — The system shall show conditions, retries, timeouts, concurrency, handlers and subflows in topology.
- [ ] **URS-F-0451** — The system shall validate graph cycles, missing references and incompatible connections before save.
- [ ] **URS-F-0452** — The system shall support zoom, pan, keyboard navigation, minimap and large-graph performance.
- [ ] **URS-F-0453** — The system shall mark generated or lossy transformations before the user accepts them.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-201
- EPIC-405

## Architecture impact

- Primary bounded area: `ui`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated browser, accessibility and manual usability tests.
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

- Functional requirements: URS-F-0446, URS-F-0447, URS-F-0448, URS-F-0449, URS-F-0450, URS-F-0451, URS-F-0452, URS-F-0453
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
