# EPIC-404 — Web UI shell, navigation and accessibility

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** User
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide a responsive, permission-aware and accessible web application for all platform personas.

## In scope

- [x] **URS-F-0430** — The system shall provide consistent navigation for dashboards, flows, executions, namespaces, assets, apps, plugins and administration.
- [x] **URS-F-0431** — The system shall hide or disable actions based on server-authoritative permissions without relying on UI checks for enforcement.
- [x] **URS-F-0432** — The system shall support deep links, browser history, saved views and tenant or namespace context.
- [x] **URS-F-0433** — The system shall meet WCAG 2.2 AA for keyboard access, focus, semantics, contrast and assistive technology in GA scope.
- [x] **URS-F-0434** — The system shall support responsive desktop and tablet layouts and a documented browser support policy.
- [x] **URS-F-0435** — The system shall provide global search, command palette, notifications and error recovery.
- [x] **URS-F-0436** — The system shall internationalize user-visible strings and locale-sensitive dates, numbers and time zones.
- [x] **URS-F-0437** — The system shall collect opt-in product telemetry only under explicit deployment policy.

## Implementation completion evidence

- 2026-08-22 — EPIC-404 is complete. AMESH now ships a responsive React control room with consistent persona navigation, server-authoritative capability rendering, tenant/namespace context, deep links, browser history, saved execution views, API-backed flow/execution pages, global live-resource search, a keyboard command menu, notifications, retry recovery, English/Simplified Chinese locale and explicit time-zone formatting. The FastAPI image serves the compiled SPA and browser deep links, telemetry remains deployment-controlled and off by default, bundled fonts make the UI self-contained, and the supported shell passed desktop/tablet, same-origin privacy and WCAG 2.2 AA automated acceptance. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`README.md`](../../frontend/README.md), [`DESIGN.md`](../../frontend/DESIGN.md), [`shell.spec.ts`](../../frontend/e2e/shell.spec.ts), [`AppShell.tsx`](../../frontend/src/components/AppShell.tsx), [`test_ui_session_api.py`](../../tests/api/test_ui_session_api.py), and [`test_frontend.py`](../../tests/test_frontend.py). Shared URS-NFR-USABILITY-004 remains In Progress for EPIC-405/407 plus the pre-GA NVDA/VoiceOver matrix; shared URS-NFR-PRIVACY-001 remains In Progress for EPIC-003/804.
- 2026-08-22 — Deployment follow-up: the PostgreSQL flow adapter now normalizes sub-millisecond transaction timestamp skew at deserialization, preventing one valid persisted flow from collapsing the Dashboard and Flows views into their recovery state. The regression test and a fresh Chromium session against the rebuilt Compose service verified `/api/v1/flows` HTTP 200 and the complete flow catalog. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`execution_repository.py`](../../src/amesh/adapters/postgres/execution_repository.py), and [`test_postgres_executor.py`](../../tests/executor/test_postgres_executor.py).

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

- Functional requirements: URS-F-0430, URS-F-0431, URS-F-0432, URS-F-0433, URS-F-0434, URS-F-0435, URS-F-0436, URS-F-0437
- Non-functional requirements: URS-NFR-USABILITY-004, URS-NFR-PRIVACY-001
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
