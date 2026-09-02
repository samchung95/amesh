# EPIC-405 — Flow code editor and validation experience

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Offer a productive schema-aware editor for the declarative flow language.

## In scope

- [x] **URS-F-0438** — The system shall edit YAML with syntax highlighting, folding, formatting, search and multi-cursor support.
- [x] **URS-F-0439** — The system shall provide schema-driven completion for core and installed plugin properties.
- [x] **URS-F-0440** — The system shall show validation errors, warnings and documentation at exact source ranges.
- [x] **URS-F-0441** — The system shall preview expression evaluation using a safe redacted sample context.
- [x] **URS-F-0442** — The system shall diff current edits against active and historical revisions.
- [x] **URS-F-0443** — The system shall preserve drafts locally and warn before navigating away from unsaved changes.
- [x] **URS-F-0444** — The system shall validate and save through server APIs so client and server rules cannot diverge.
- [x] **URS-F-0445** — The system shall support import, export, clone, disable and revision restore operations.

## Implementation completion evidence

- 2026-08-23 — EPIC-405 is complete. The control room now provides a CodeMirror 6 YAML workbench with syntax highlighting, folding, search, multi-selection, server formatting, core and installed-plugin completion, exact-range diagnostics, bounded redacted expression preview, local draft recovery and unsaved-change warnings. Authors can validate/save through the same plugin-aware server contract, import/export/clone flows, compare drafts with any stored revision, disable the active revision and restore history. The versioned editor schema and preview APIs are published in OpenAPI and all four generated SDKs. Focused API, unit, PostgreSQL revision, 5,000-line validation, Chromium interaction and WCAG 2.2 AA checks passed; shared URS-NFR-USABILITY-001 and URS-NFR-USABILITY-004 remain Proposed until all owner epics and the pre-GA assistive-technology matrix complete. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`FlowEditorPage.tsx`](../../frontend/src/pages/FlowEditorPage.tsx), [`FlowCodeEditor.tsx`](../../frontend/src/components/FlowCodeEditor.tsx), [`test_flow_editor_api.py`](../../tests/api/test_flow_editor_api.py), [`test_flow_revision_api.py`](../../tests/api/test_flow_revision_api.py), and [`shell.spec.ts`](../../frontend/e2e/shell.spec.ts).

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

- Functional requirements: URS-F-0438, URS-F-0439, URS-F-0440, URS-F-0441, URS-F-0442, URS-F-0443, URS-F-0444, URS-F-0445
- Non-functional requirements: URS-NFR-USABILITY-001, URS-NFR-USABILITY-004
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
