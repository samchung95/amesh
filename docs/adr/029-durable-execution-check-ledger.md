# ADR-029: Durable execution check ledger

- Status: Accepted
- Date: 2026-08-22
- Epic: EPIC-110

## Context

Execution expectations must be evaluated at lifecycle transitions and database-time deadlines without
changing task or execution state. Definitions also need reusable namespace and plugin defaults, while
violation actions must survive restart and cannot create unbounded policy loops.

## Decision

Materialize enabled checks with each immutable flow revision. Store deadlines, evaluations and actions
in tenant-RLS-protected PostgreSQL tables. Execution start and terminal transitions write evaluations
inside their existing state transaction; the scheduler role evaluates due database-time deadlines and
claims actions with expiring leases and fencing tokens.

The ledger records `PASS`, `WARN`, `FAIL` or `ERROR` independently from orchestration state. Output and
custom checks reuse the bounded native expression engine. A failed evaluation may enqueue `NOTIFY` or
`RUN_FLOW`; action identity is unique per evaluation/index, retries are bounded, and `checkPolicyDepth`
causes actions at their configured maximum depth to be persisted as `SKIPPED`.

Namespace policies apply only when named by `checkPolicies`. Enabled `PLUGIN_DEFAULT` policies apply
when the flow contains their task type. Explicit flow checks take precedence by check ID. Compliance is
aggregated from immutable evaluations by tenant, namespace, flow, label, day, week or month.

## Consequences

- PostgreSQL remains the only correctness dependency and preserves evidence through process restart.
- A flow revision pins the effective policy definition; policy changes require a new flow revision.
- Notification delivery uses the existing transactional outbox and system-flow actions use ordinary
  idempotent execution creation.
- The scheduler must be running for deadline checks and action processing; lifecycle evaluations still
  commit synchronously with execution changes.
