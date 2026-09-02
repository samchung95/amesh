# EPIC-103 — Trigger runtime and occurrence lifecycle

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Unify schedule, polling, webhook, realtime, flow and programmatic triggers under one occurrence model.

## In scope

- [x] **URS-F-0108** — The system shall define trigger identities, revisions, state, conditions, inputs and occurrence metadata.
- [x] **URS-F-0109** — The system shall activate and deactivate trigger instances when flow revisions change.
- [x] **URS-F-0110** — The system shall persist trigger checkpoints and cursors before acknowledging external events where possible.
- [x] **URS-F-0111** — The system shall deduplicate repeated source events using connector-provided or derived occurrence keys.
- [x] **URS-F-0112** — The system shall support trigger backpressure, pause, retry, dead-letter and manual replay.
- [x] **URS-F-0113** — The system shall expose trigger health, last evaluation, next evaluation, lag and recent occurrences.
- [x] **URS-F-0114** — The system shall route flow-completion events to dependent flows without relying on polling.
- [x] **URS-F-0115** — The system shall allow plugins to implement polling and realtime trigger adapters through stable interfaces.

## MVP implementation progress

- 2026-08-21 — W6 verified the accepted webhook slice: a static-token-protected endpoint resolves a stored flow, derives an idempotency key from the supplied or generated occurrence identity, and returns the completed execution. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md) and [`test_mvp_api.py`](../../tests/api/test_mvp_api.py). The broader trigger occurrence lifecycle remains open.

## Implementation completion evidence

- 2026-08-22 — EPIC-103 is complete. Schedule, webhook, polling, realtime and flow-completion triggers now share tenant-isolated PostgreSQL revision state, checkpoints, stable occurrence identities, backpressure and a fenced occurrence ledger. Flow revisions transactionally activate/deactivate trigger instances; duplicate source events converge, retry exhaustion dead-letters, operator pause/resume and immutable replay are audited, and health/recent occurrences are exposed through authorized APIs and the React control room. Polling and realtime plugin ports enforce durable accept/checkpoint-before-ack ordering. Terminal source executions transactionally route `core.flow` occurrences to dependent executions without source polling, and Compose runs a dedicated scheduler service. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`triggers.md`](../../docs/operations/triggers.md), [`028-durable-trigger-occurrence-runtime.md`](../../docs/adr/028-durable-trigger-occurrence-runtime.md), [`0030_trigger_occurrence_runtime.sql`](../../migrations/0030_trigger_occurrence_runtime.sql), [`test_trigger_runtime_repository.py`](../../tests/adapters/postgres/test_trigger_runtime_repository.py), [`test_trigger_runtime_api.py`](../../tests/api/test_trigger_runtime_api.py), [`test_trigger_runtime.py`](../../tests/test_trigger_runtime.py) and [`shell.spec.ts`](../../frontend/e2e/shell.spec.ts). Shared product-wide duplicate-injection qualification remains In Progress under URS-NFR-RELIABILITY-002.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-002** — The platform shall tolerate duplicate commands, events, trigger occurrences and task results without duplicate logical state transitions. Target: All conformance duplicate-injection scenarios produce one logical effect.

## Dependencies

- EPIC-102
- EPIC-300

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
- Property-based and integration tests with duplicate and reordered delivery.
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

- Functional requirements: URS-F-0108, URS-F-0109, URS-F-0110, URS-F-0111, URS-F-0112, URS-F-0113, URS-F-0114, URS-F-0115
- Non-functional requirements: URS-NFR-RELIABILITY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
