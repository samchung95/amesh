# EPIC-200 — Runnable task contract

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Plugin developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Define the lifecycle contract for units of executable work.

## In scope

- [x] **URS-F-0180** — The system shall validate task configuration against plugin-provided schemas before an execution starts.
- [x] **URS-F-0181** — The system shall create one task-run identity per logical attempt and preserve attempt history.
- [x] **URS-F-0182** — The system shall supply a typed execution context, scoped secrets, files, variables and cancellation channel.
- [x] **URS-F-0183** — The system shall capture structured outputs, metrics, logs, artifacts and exit metadata.
- [x] **URS-F-0184** — The system shall distinguish user-code failure, configuration failure, infrastructure failure and platform failure.
- [x] **URS-F-0185** — The system shall support synchronous completion and asynchronous deferral with a durable resume token.
- [x] **URS-F-0186** — The system shall bound task resource use and enforce output, log and artifact limits.
- [x] **URS-F-0187** — The system shall make task completion idempotent and reject stale attempt results.

## Implementation completion evidence

- 2026-08-22 — EPIC-200 is complete. Registered task schemas are validated before execution creation; every attempt retains its durable identity and history. Handlers receive typed inputs, outputs, variables, declared secret scopes/files and a durable cancellation channel, and can return structured output, logs, metrics, artifacts and exit evidence under configured size limits. Failure categories distinguish configuration, user-code, infrastructure and platform causes. Asynchronous handlers persist hashed, expiring resume tokens and survive executor restart; the authorized resume API converges duplicate callbacks while stale attempts fail closed. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`execution-semantics.md`](../../docs/architecture/execution-semantics.md), [`0021_runnable_task_contract.sql`](../../migrations/0021_runnable_task_contract.sql), [`test_runnable_task_contract.py`](../../tests/executor/test_runnable_task_contract.py), [`test_task_deferral.py`](../../tests/executor/test_task_deferral.py) and [`test_task_resume_api.py`](../../tests/api/test_task_resume_api.py).

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

- Functional requirements: URS-F-0180, URS-F-0181, URS-F-0182, URS-F-0183, URS-F-0184, URS-F-0185, URS-F-0186, URS-F-0187
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
