# EPIC-111 — Logs, metrics, outputs and artifact events

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `observability`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Capture task-produced evidence as structured, searchable and streamable execution data.

## In scope

- [ ] **URS-F-0172** — The system shall ingest structured and unstructured logs with execution, task-run, worker, tenant and trace context.
- [ ] **URS-F-0173** — The system shall preserve event time, ingest time, severity, logger, attempt and source stream.
- [ ] **URS-F-0174** — The system shall accept typed counters, gauges, timers and custom metrics from tasks and plugins.
- [ ] **URS-F-0175** — The system shall persist task and flow outputs separately from logs with size and sensitivity controls.
- [ ] **URS-F-0176** — The system shall link artifact metadata to internal storage without embedding large payloads in metadata records.
- [ ] **URS-F-0177** — The system shall stream new logs and state updates to authorized clients with reconnect cursors.
- [ ] **URS-F-0178** — The system shall apply redaction, retention, sampling and export policies before external shipment.
- [ ] **URS-F-0179** — The system shall continue execution when optional telemetry sinks are temporarily unavailable.

## MVP implementation progress

- 2026-08-21 — W6–W7 verified the accepted MVP evidence slice: task results are persisted and queryable through execution/log APIs, while server and worker processes emit structured JSON records carrying HTTP, execution or worker context. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`test_mvp_api.py`](../../tests/api/test_mvp_api.py), and [`test_observability.py`](../../tests/test_observability.py). Streaming, artifacts and the broader observability epic remain open.

## Non-functional requirements

- [ ] **URS-NFR-PERFORMANCE-007** — Log ingestion shall not block task completion and shall apply explicit overload policy. Target: Provisional target: 50,000 log records per second per standard cluster with bounded buffers.
- [ ] **URS-NFR-SECURITY-003** — Secret plaintext shall not appear in persistent metadata, events, logs, metrics, traces, UI payloads or generated support bundles. Target: Zero seeded canary secrets detected across persisted and exported telemetry in the security suite.

## Dependencies

- EPIC-010
- EPIC-100

## Architecture impact

- Primary bounded area: `observability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Telemetry contract and outage tests.
- Burst and sustained log-load test with exporter outage.
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

- Functional requirements: URS-F-0172, URS-F-0173, URS-F-0174, URS-F-0175, URS-F-0176, URS-F-0177, URS-F-0178, URS-F-0179
- Non-functional requirements: URS-NFR-PERFORMANCE-007, URS-NFR-SECURITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
