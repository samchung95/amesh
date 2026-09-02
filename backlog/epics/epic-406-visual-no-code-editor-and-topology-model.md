# EPIC-406 — Visual no-code editor and topology model

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Author and understand workflows visually without creating a second incompatible representation.

## In scope

- [x] **URS-F-0446** — The system shall render the canonical flow model as an interactive task and dependency graph.
- [x] **URS-F-0447** — The system shall add, configure, connect, reorder, group and remove supported tasks through schema-generated forms.
- [x] **URS-F-0448** — The system shall round-trip supported visual edits to YAML without changing unrelated semantic content.
- [x] **URS-F-0449** — The system shall fall back to code editing for constructs the visual editor cannot represent.
- [x] **URS-F-0450** — The system shall show conditions, retries, timeouts, concurrency, handlers and subflows in topology.
- [x] **URS-F-0451** — The system shall validate graph cycles, missing references and incompatible connections before save.
- [x] **URS-F-0452** — The system shall support zoom, pan, keyboard navigation, minimap and large-graph performance.
- [x] **URS-F-0453** — The system shall mark generated or lossy transformations before the user accepts them.

## Implementation completion evidence

- 2026-08-23 — EPIC-406 is complete. React Flow now renders the canonical task/dependency model as an interactive canvas in authoring, flow detail and execution detail views, with zoom, pan, keyboard operation, controls and a labelled mini map. The authoring canvas derives from the current YAML draft; its installed-resource palette and inspector add and configure tasks, while connections and structure controls connect, disconnect, reorder, group and remove them. Conditions, retries, timeouts, concurrency, lifecycle handlers and subflow targets are visible as topology metadata. The YAML AST transformer preserves comments, order and unrelated fields, rejects missing/cross-group/cyclic links, labels unsupported fields for code fallback and requires review of generated or lossy changes before acceptance. Five focused model tests include all transformations and a 500-task sub-second gate; the production build, full browser matrix and editor WCAG 2.2 AA scan passed. Public API, DSL and durable state contracts are unchanged; accepted YAML still uses EPIC-405's authorized, audited server save. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`VisualFlowEditor.tsx`](../../frontend/src/components/VisualFlowEditor.tsx), [`visualFlowModel.ts`](../../frontend/src/components/visualFlowModel.ts), [`visualFlowModel.test.ts`](../../frontend/src/components/visualFlowModel.test.ts), [`FlowGraphView.tsx`](../../frontend/src/components/FlowGraphView.tsx) and [`shell.spec.ts`](../../frontend/e2e/shell.spec.ts).

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

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0446, URS-F-0447, URS-F-0448, URS-F-0449, URS-F-0450, URS-F-0451, URS-F-0452, URS-F-0453
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
