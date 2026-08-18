# EPIC-408 — Dashboards, query language and saved views

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Create operational and business views from execution, log, metric, SLA and asset data.

## In scope

- [ ] **URS-F-0462** — The system shall provide built-in instance, tenant, namespace, flow, worker and SLA dashboards.
- [ ] **URS-F-0463** — The system shall support time series, tables, counters, distributions, status breakdowns and ranked lists.
- [ ] **URS-F-0464** — The system shall define dashboard queries through a typed restricted query model rather than arbitrary database SQL.
- [ ] **URS-F-0465** — The system shall filter by time, labels, namespace, flow, state, worker group and custom dimensions.
- [ ] **URS-F-0466** — The system shall save, share, export and permission dashboards independently from underlying data.
- [ ] **URS-F-0467** — The system shall apply query limits, timeouts, sampling and aggregation to protect operational workloads.
- [ ] **URS-F-0468** — The system shall show query freshness, partial-result and permission-redaction indicators.
- [ ] **URS-F-0469** — The system shall allow custom dashboard definitions to be managed through API and GitOps.

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

- Functional requirements: URS-F-0462, URS-F-0463, URS-F-0464, URS-F-0465, URS-F-0466, URS-F-0467, URS-F-0468, URS-F-0469
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
