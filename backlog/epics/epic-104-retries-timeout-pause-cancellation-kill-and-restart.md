# EPIC-104 — Retries, timeout, pause, cancellation, kill and restart

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Give users predictable control over failure recovery and execution interruption.

## In scope

- [ ] **URS-F-0116** — The system shall apply configurable retry attempts, delays, exponential backoff, maximum interval and jitter.
- [ ] **URS-F-0117** — The system shall classify errors as retryable, non-retryable, cancelled, timed out or infrastructure failures.
- [ ] **URS-F-0118** — The system shall enforce task and execution timeouts using monotonic deadlines where possible.
- [ ] **URS-F-0119** — The system shall pause and resume workflows without losing completed work or admitting new runnable tasks.
- [ ] **URS-F-0120** — The system shall request graceful cancellation before escalating to force termination after a deadline.
- [ ] **URS-F-0121** — The system shall restart an execution, task run or subflow from supported checkpoints with explicit state reset rules.
- [ ] **URS-F-0122** — The system shall invalidate stale worker results after cancellation, retry or restart through fencing.
- [ ] **URS-F-0123** — The system shall surface a complete intervention history and predicted consequences before destructive actions.

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

- Functional requirements: URS-F-0116, URS-F-0117, URS-F-0118, URS-F-0119, URS-F-0120, URS-F-0121, URS-F-0122, URS-F-0123
- Non-functional requirements: URS-NFR-RELIABILITY-008
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
