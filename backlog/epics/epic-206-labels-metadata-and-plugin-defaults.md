# EPIC-206 — Labels, metadata and plugin defaults

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Apply searchable metadata and inherited defaults without hidden ambiguity.

## In scope

- [ ] **URS-F-0227** — The system shall attach user and system labels to flows, executions, task runs, assets and backfills.
- [ ] **URS-F-0228** — The system shall reserve protected system label prefixes and prevent user spoofing.
- [ ] **URS-F-0229** — The system shall support namespace-scoped plugin defaults with exact type and property matching.
- [ ] **URS-F-0230** — The system shall define deterministic inheritance, merge and override precedence.
- [ ] **URS-F-0231** — The system shall show the effective configuration and origin of every inherited value.
- [ ] **URS-F-0232** — The system shall allow policy to require, deny or normalize selected labels and defaults.
- [ ] **URS-F-0233** — The system shall index labels for filtering, dashboards, quotas, routing and retention.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-002
- EPIC-004

## Architecture impact

- Primary bounded area: `workflow`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- DSL validation plus end-to-end workflow conformance tests.
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

- Functional requirements: URS-F-0227, URS-F-0228, URS-F-0229, URS-F-0230, URS-F-0231, URS-F-0232, URS-F-0233
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
