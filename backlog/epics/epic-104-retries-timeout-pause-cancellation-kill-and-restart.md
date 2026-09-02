# EPIC-104 — Retries, timeout, pause, cancellation, kill and restart

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Give users predictable control over failure recovery and execution interruption.

## In scope

- [x] **URS-F-0116** — The system shall apply configurable retry attempts, delays, exponential backoff, maximum interval and jitter.
- [x] **URS-F-0117** — The system shall classify errors as retryable, non-retryable, cancelled, timed out or infrastructure failures.
- [x] **URS-F-0118** — The system shall enforce task and execution timeouts using monotonic deadlines where possible.
- [x] **URS-F-0119** — The system shall pause and resume workflows without losing completed work or admitting new runnable tasks.
- [x] **URS-F-0120** — The system shall request graceful cancellation before escalating to force termination after a deadline.
- [x] **URS-F-0121** — The system shall restart an execution, task run or subflow from supported checkpoints with explicit state reset rules.
- [x] **URS-F-0122** — The system shall invalidate stale worker results after cancellation, retry or restart through fencing.
- [x] **URS-F-0123** — The system shall surface a complete intervention history and predicted consequences before destructive actions.

## MVP implementation progress

- 2026-08-21 — W3 verified the accepted MVP slice: persisted retry attempts with delay and exponential backoff, local task timeout and cancellation escalation, and attempt fencing that rejects a superseded result. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`test_local_process_execution.py`](../../tests/executor/test_local_process_execution.py), and [`test_process_runner.py`](../../tests/adapters/local/test_process_runner.py). The broader parity requirements remain open.

## Implementation completion evidence

- 2026-08-22 — EPIC-104 is complete. Retry policies now include bounded exponential intervals and deterministic jitter; handler and runner failures persist one of five stable categories. Task deadlines use asyncio's monotonic timeout and execution deadlines use PostgreSQL time. Durable, version-and-epoch-fenced pause, resume, graceful cancel, force cancel and checkpoint restart preserve committed work, reset an explicit downstream task scope, invalidate active claims and retain immutable intervention events. Authorized preview, apply and history endpoints expose consequences and reject stale previews. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`execution-semantics.md`](../../docs/architecture/execution-semantics.md), [`0017_execution_interventions.sql`](../../migrations/0017_execution_interventions.sql), [`test_execution_control.py`](../../tests/executor/test_execution_control.py), and [`test_execution_control_api.py`](../../tests/api/test_execution_control_api.py). Live multi-node clock-skew and failover qualification remains shared with EPIC-601.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-008** — Temporal decisions shall tolerate bounded clock skew and use monotonic time for local deadlines where possible. Target: Correct schedule, lease and timeout behavior with plus or minus 30 seconds node skew.

## Dependencies

- EPIC-100
- EPIC-101

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
- Virtual-clock and multi-node skew tests.
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

- Functional requirements: URS-F-0116, URS-F-0117, URS-F-0118, URS-F-0119, URS-F-0120, URS-F-0121, URS-F-0122, URS-F-0123
- Non-functional requirements: URS-NFR-RELIABILITY-008
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
