# EPIC-205 — Inputs, outputs and variables

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide typed data contracts at flow and task boundaries.

## In scope

- [ ] **URS-F-0219** — The system shall declare string, number, boolean, datetime, duration, enum, array, object, file and secret input types.
- [ ] **URS-F-0220** — The system shall apply required, default, validation, display, prefill and sensitivity metadata.
- [ ] **URS-F-0221** — The system shall validate manual, API, trigger and subflow inputs before creating runnable work.
- [ ] **URS-F-0222** — The system shall declare flow outputs rendered from completed execution context.
- [ ] **URS-F-0223** — The system shall keep static variables separate from execution inputs and mutable key-value data.
- [ ] **URS-F-0224** — The system shall enforce payload size limits and move large file values into internal storage.
- [ ] **URS-F-0225** — The system shall generate UI forms and API schemas from the same input definitions.
- [ ] **URS-F-0226** — The system shall redact sensitive inputs and outputs according to schema metadata and policy.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-003** — Secret plaintext shall not appear in persistent metadata, events, logs, metrics, traces, UI payloads or generated support bundles. Target: Zero seeded canary secrets detected across persisted and exported telemetry in the security suite.

## Dependencies

- EPIC-004
- EPIC-005
- EPIC-010

## Architecture impact

- Primary bounded area: `workflow`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- DSL validation plus end-to-end workflow conformance tests.
- Canary-secret scanning and redaction tests.
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

- Functional requirements: URS-F-0219, URS-F-0220, URS-F-0221, URS-F-0222, URS-F-0223, URS-F-0224, URS-F-0225, URS-F-0226
- Non-functional requirements: URS-NFR-SECURITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
