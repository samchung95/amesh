# EPIC-607 — OpenTelemetry, Prometheus and log shipping

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `observability`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Expose actionable telemetry without coupling the platform to one vendor.

## In scope

- [x] **URS-F-0638** — The system shall instrument API, scheduler, executor, worker, storage, messaging, plugin and runner operations with OpenTelemetry.
- [x] **URS-F-0639** — The system shall propagate trace context through commands, events, messages, tasks, subflows and outbound plugin calls.
- [x] **URS-F-0640** — The system shall publish Prometheus-compatible metrics with bounded cardinality and documented labels.
- [x] **URS-F-0641** — The system shall emit structured application logs with component, tenant-safe correlation and version metadata.
- [x] **URS-F-0642** — The system shall support configurable log shipping to standard external destinations.
- [x] **URS-F-0643** — The system shall provide default dashboards and alerts for availability, latency, saturation, failures, lag and stuck work.
- [x] **URS-F-0644** — The system shall redact sensitive values before telemetry export.
- [x] **URS-F-0645** — The system shall continue core operation when telemetry collectors or exporters are unavailable.

## MVP implementation progress

- 2026-08-21 — W7 verified the accepted Prometheus/logging slice: `/metrics` exposes process, build and normalized HTTP request counters through the Helm Service, which carries scrape annotations, while server and worker stdout is newline-delimited JSON. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`test_observability.py`](../../tests/test_observability.py), and [`observability.py`](../../src/amesh/observability.py). OpenTelemetry, dashboards, alerts, shipping and the broader telemetry epic remain open.

## Implementation completion evidence

- 2026-08-23 — EPIC-607 functional scope is complete. The official OpenTelemetry SDK emits redacted OTLP/HTTP traces for API, scheduler, executor, worker, storage, messaging, plugin and runner operations; W3C context crosses HTTP, durable contracts, PostgreSQL event rows, subflows and plugin/runner calls. Prometheus exposes bounded component, queue, capacity, lag, stuck-work, exporter and log-drop signals. JSON logs ship through bounded non-blocking queues to stdout, rotating file or syslog, and collector/exporter failure cannot fail core work. Helm packages a seven-signal Grafana dashboard and actionable Prometheus alerts. Tenant-scoped redacted diagnostics include component health, versions, recent tenant-matched errors and fixed metric samples. Both Compose deployments are healthy at migration 53. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`observability.md`](../../docs/operations/observability.md), [`test_observability.py`](../../tests/test_observability.py), and [`test_observability_assets.py`](../../tests/test_observability_assets.py).

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-005** — Core orchestration shall continue when optional search, telemetry, outbound webhook or analytics services are unavailable. Target: New and running executions continue within documented latency budgets during optional-service outage tests.
- [ ] **URS-NFR-PERFORMANCE-007** — Log ingestion shall not block task completion and shall apply explicit overload policy. Target: Provisional target: 50,000 log records per second per standard cluster with bounded buffers.
- [ ] **URS-NFR-SECURITY-003** — Secret plaintext shall not appear in persistent metadata, events, logs, metrics, traces, UI payloads or generated support bundles. Target: Zero seeded canary secrets detected across persisted and exported telemetry in the security suite.
- [ ] **URS-NFR-OPERABILITY-002** — Operational metrics shall avoid unbounded tenant, flow, execution and task identifiers by default. Target: Metric cardinality remains within published limits under the standard scale test.
- [ ] **URS-NFR-OPERABILITY-003** — Reference alerts shall include symptom, likely causes, impact and runbook link. Target: All GA SLO alerts pass alert-quality review and simulated firing tests.
- [ ] **URS-NFR-OPERABILITY-004** — Administrators shall be able to generate a redacted diagnostic bundle without exposing secrets or unrelated tenant data. Target: Canary-secret and cross-tenant scans pass for generated bundles.
- [ ] **URS-NFR-OPERABILITY-005** — Operators shall see queue lag, worker capacity, admission pressure, database saturation, storage use and search lag. Target: All capacity signals are present in the reference dashboard and alert catalog.

## Dependencies

- EPIC-111
- EPIC-601

## Architecture impact

- Primary bounded area: `observability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Telemetry contract and outage tests.
- Dependency isolation and outage integration tests.
- Burst and sustained log-load test with exporter outage.
- Canary-secret scanning and redaction tests.
- Telemetry cardinality audit.
- Alert fixture and runbook audit.
- Security test with seeded sensitive data.
- Dashboard and telemetry contract tests.
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

- The provisional 50,000-log-record/second standard-cluster target remains deferred to external profile qualification; local evidence proves bounded non-blocking overload and exporter-outage behavior only.
- Shared reliability, security, alert-review, support-bundle and capacity NFRs remain open until their other mapped epics and pre-GA qualification complete.

## Traceability

- Functional requirements: URS-F-0638, URS-F-0639, URS-F-0640, URS-F-0641, URS-F-0642, URS-F-0643, URS-F-0644, URS-F-0645
- Non-functional requirements: URS-NFR-RELIABILITY-005, URS-NFR-PERFORMANCE-007, URS-NFR-SECURITY-003, URS-NFR-OPERABILITY-002, URS-NFR-OPERABILITY-003, URS-NFR-OPERABILITY-004, URS-NFR-OPERABILITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
