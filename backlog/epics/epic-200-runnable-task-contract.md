# EPIC-200 — Runnable task contract

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Plugin developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Define the lifecycle contract for units of executable work.

## In scope

- [ ] **URS-F-0180** — The system shall validate task configuration against plugin-provided schemas before an execution starts.
- [ ] **URS-F-0181** — The system shall create one task-run identity per logical attempt and preserve attempt history.
- [ ] **URS-F-0182** — The system shall supply a typed execution context, scoped secrets, files, variables and cancellation channel.
- [ ] **URS-F-0183** — The system shall capture structured outputs, metrics, logs, artifacts and exit metadata.
- [ ] **URS-F-0184** — The system shall distinguish user-code failure, configuration failure, infrastructure failure and platform failure.
- [ ] **URS-F-0185** — The system shall support synchronous completion and asynchronous deferral with a durable resume token.
- [ ] **URS-F-0186** — The system shall bound task resource use and enforce output, log and artifact limits.
- [ ] **URS-F-0187** — The system shall make task completion idempotent and reject stale attempt results.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-101
- EPIC-300

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

- Functional requirements: URS-F-0180, URS-F-0181, URS-F-0182, URS-F-0183, URS-F-0184, URS-F-0185, URS-F-0186, URS-F-0187
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
