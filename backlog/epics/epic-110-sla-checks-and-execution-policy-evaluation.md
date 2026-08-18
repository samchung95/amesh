# EPIC-110 — SLA, checks and execution policy evaluation

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Evaluate operational expectations during and after executions and make violations actionable.

## In scope

- [ ] **URS-F-0164** — The system shall define duration, start-delay, freshness, completion-window, output and custom expression checks.
- [ ] **URS-F-0165** — The system shall evaluate checks at deterministic lifecycle points and on periodic deadlines.
- [ ] **URS-F-0166** — The system shall record pass, warn, fail and error outcomes separately from task execution state.
- [ ] **URS-F-0167** — The system shall trigger notifications, system flows or policy actions from check and SLA outcomes.
- [ ] **URS-F-0168** — The system shall aggregate compliance by tenant, namespace, flow, label and time period.
- [ ] **URS-F-0169** — The system shall allow check definitions to be reused through namespace policy or plugin defaults.
- [ ] **URS-F-0170** — The system shall prevent policy loops and bound the work caused by violation handlers.
- [ ] **URS-F-0171** — The system shall expose evidence used for each evaluation.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-100
- EPIC-103

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

- Functional requirements: URS-F-0164, URS-F-0165, URS-F-0166, URS-F-0167, URS-F-0168, URS-F-0169, URS-F-0170, URS-F-0171
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
