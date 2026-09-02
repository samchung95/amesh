# EPIC-408 — Dashboards, query language and saved views

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Create operational and business views from execution, log, metric, SLA and asset data.

## In scope

- [x] **URS-F-0462** — The system shall provide built-in instance, tenant, namespace, flow, worker and SLA dashboards.
- [x] **URS-F-0463** — The system shall support time series, tables, counters, distributions, status breakdowns and ranked lists.
- [x] **URS-F-0464** — The system shall define dashboard queries through a typed restricted query model rather than arbitrary database SQL.
- [x] **URS-F-0465** — The system shall filter by time, labels, namespace, flow, state, worker group and custom dimensions.
- [x] **URS-F-0466** — The system shall save, share, export and permission dashboards independently from underlying data.
- [x] **URS-F-0467** — The system shall apply query limits, timeouts, sampling and aggregation to protect operational workloads.
- [x] **URS-F-0468** — The system shall show query freshness, partial-result and permission-redaction indicators.
- [x] **URS-F-0469** — The system shall allow custom dashboard definitions to be managed through API and GitOps.

## Implementation completion evidence

- 2026-08-23 — EPIC-408 is complete. Six built-in dashboards and custom API/GitOps definitions use a restricted typed query model over execution, log, metric, SLA, worker and asset projections. The React workbench provides runtime filters, every required visualization, deep-link sharing, YAML/JSON export and independent viewer/editor ACLs. Query range, scan, result, timeout and deterministic sampling bounds protect PostgreSQL; result metadata exposes freshness, partial and sampled state. Source authorization is evaluated separately and denied widgets are explicitly redacted. Custom definition changes are versioned, tenant-isolated and transactionally published through immutable events and the outbox. Fresh 43-migration PostgreSQL, repository, API, frontend unit, Chromium, automated WCAG, generated-contract, SDK, deployment and live readiness checks passed. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`dashboards.md`](../../docs/api/dashboards.md), [`DashboardPage.tsx`](../../frontend/src/pages/DashboardPage.tsx), [`test_dashboard_repository.py`](../../tests/adapters/postgres/test_dashboard_repository.py), and [`0043_dashboards.sql`](../../migrations/0043_dashboards.sql).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-409
- EPIC-404

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

- Functional requirements: URS-F-0462, URS-F-0463, URS-F-0464, URS-F-0465, URS-F-0466, URS-F-0467, URS-F-0468, URS-F-0469
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
