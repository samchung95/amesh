# EPIC-407 — Execution details, Gantt, logs and debugging UI

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Help users diagnose execution behavior from one coherent timeline.

## In scope

- [x] **URS-F-0454** — The system shall show execution identity, revision, inputs, labels, state history, duration, trigger and parent-child relationships.
- [x] **URS-F-0455** — The system shall render task runs as topology and Gantt views with attempts, queues, waits and runner duration.
- [x] **URS-F-0456** — The system shall stream and filter logs by task, attempt, level, worker, time and text.
- [x] **URS-F-0457** — The system shall show rendered inputs, outputs, metrics, artifacts, errors and cache decisions subject to authorization.
- [x] **URS-F-0458** — The system shall offer pause, resume, cancel, kill, restart, replay and backfill actions with impact confirmation.
- [x] **URS-F-0459** — The system shall link each state transition to its causative event and actor where available.
- [x] **URS-F-0460** — The system shall retain the user's filters and selected task in shareable deep links.
- [x] **URS-F-0461** — The system shall remain usable for executions with tens of thousands of task runs through virtualization and aggregation.

## Implementation completion evidence

- 2026-08-23 — EPIC-407 is complete. The execution debugger unifies identity, revision, trigger, relationships, topology, Gantt, reconnectable logs, authorized data and actor-linked state history in one deep-linkable workbench. Operators receive impact previews before pause, resume, cancel, kill, restart, replay or backfill commands. Server-side task-run summaries and 100-row paging avoid full execution materialization; topology aggregates above 1,000 nodes and browser evidence is capped at 5,000 events. A fresh PostgreSQL run proved 100,000 task-run summary and paging below five seconds and 16 MiB traced Python memory. Focused backend, generated-contract, unit, Chromium, automated WCAG, deployment and live API checks passed. The shared manual NVDA/VoiceOver and cross-browser release matrix remains deferred and does not block this functional slice. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`ExecutionDebugger.tsx`](../../frontend/src/components/ExecutionDebugger.tsx), [`executionDebugModel.test.ts`](../../frontend/src/components/executionDebugModel.test.ts), [`test_execution_debug_paging.py`](../../tests/adapters/postgres/test_execution_debug_paging.py), and [`0042_execution_debug_evidence.sql`](../../migrations/0042_execution_debug_evidence.sql).

## Non-functional requirements

- [ ] **URS-NFR-PERFORMANCE-006** — The engine and UI shall handle executions with very large expanded task graphs. Target: Provisional target: 100,000 task runs per execution with aggregated UI views and bounded memory.
- [ ] **URS-NFR-USABILITY-004** — The GA web interface shall conform to WCAG 2.2 AA for supported workflows. Target: No critical or serious automated findings and manual keyboard and screen-reader acceptance.

## Dependencies

- EPIC-111
- EPIC-401
- EPIC-404

## Architecture impact

- Primary bounded area: `ui`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated browser, accessibility and manual usability tests.
- Synthetic large-DAG and loop benchmark.
- Automated accessibility scan plus manual audit.
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

- Functional requirements: URS-F-0454, URS-F-0455, URS-F-0456, URS-F-0457, URS-F-0458, URS-F-0459, URS-F-0460, URS-F-0461
- Non-functional requirements: URS-NFR-PERFORMANCE-006, URS-NFR-USABILITY-004
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
