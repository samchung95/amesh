# EPIC-400 — Versioned REST API and OpenAPI contract

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `api`
- **Primary persona:** API consumer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Expose the complete supported control plane through a stable, documented and automatable API.

## In scope

- [x] **URS-F-0398** — The system shall provide CRUD and lifecycle endpoints for flows, revisions, executions, task runs, triggers, backfills, namespaces, files, key-values, plugins and governance resources.
- [x] **URS-F-0399** — The system shall use consistent pagination, filtering, sorting, field selection, error envelopes and idempotency headers.
- [x] **URS-F-0400** — The system shall generate an OpenAPI document from implementation types and validate backward compatibility in CI.
- [x] **URS-F-0401** — The system shall support optimistic concurrency and conditional requests for mutable resources.
- [x] **URS-F-0402** — The system shall accept bulk operations with per-item results and bounded transactional scope.
- [x] **URS-F-0403** — The system shall stream large imports, exports, logs and artifacts rather than buffering them.
- [x] **URS-F-0404** — The system shall version incompatible contracts and publish a deprecation schedule.
- [x] **URS-F-0405** — The system shall enforce authorization and tenant scope before resource existence is disclosed.

## MVP implementation progress

- 2026-08-21 — W6 verified the accepted `/api/v1` slice for flow validation/apply/list, execution create/get/list, task logs and webhooks, and regenerated the OpenAPI contract. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`test_mvp_api.py`](../../tests/api/test_mvp_api.py), and [`openapi.json`](../../docs/api/openapi.json). Pagination, asynchronous commands and the broader API remain open.
- 2026-08-22 — ADR-025 completed the authoritative v0.2 API profile: shared opt-in collection controls and problem details; synchronous-compatible and asynchronous idempotent launch; bounded bulk results; streaming logs; Docker-local generated OpenAPI compatibility checks; and a Compose recovery executor. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`test_mvp_api.py`](../../tests/api/test_mvp_api.py), [`test_contracts.py`](../../tests/api/test_contracts.py), and [`openapi.json`](../../docs/api/openapi.json).

## Explicit non-goals

- Namespace files, key-values, secret providers and installable plugin lifecycles remain owned by EPIC-207, EPIC-506 and EPIC-300/301; EPIC-400 does not create placeholder persistence.
- The 10-million-record filter and index qualification remains EPIC-409; EPIC-400 qualifies the launch critical path.

## Non-functional requirements

- [ ] **URS-NFR-PERFORMANCE-001** — Common authenticated read and write APIs shall remain responsive at the standard reference scale. Target: Provisional target: p95 below 500 ms and p99 below 1.5 s excluding bulk exports and external dependencies.
- [ ] **URS-NFR-PERFORMANCE-002** — Accepted execution launches shall become visible and eligible for orchestration promptly. Target: Provisional target: p95 below 2 seconds and p99 below 5 seconds in the standard profile.
- [ ] **URS-NFR-MAINTAINABILITY-002** — Public DSL, API, event and plugin contracts shall follow documented semantic-versioning and deprecation rules. Target: No breaking contract change enters a minor or patch release without an approved exception.

## Dependencies

- EPIC-002
- EPIC-500

## Architecture impact

- Primary bounded area: `api`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- OpenAPI contract and authenticated end-to-end API tests.
- Repeatable load test with 10 million retained execution records and realistic filters.
- End-to-end launch benchmark under mixed workload.
- Automated schema and API compatibility checks.
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

- Functional requirements: URS-F-0398, URS-F-0399, URS-F-0400, URS-F-0401, URS-F-0402, URS-F-0403, URS-F-0404, URS-F-0405
- Non-functional requirements: URS-NFR-PERFORMANCE-001, URS-NFR-PERFORMANCE-002, URS-NFR-MAINTAINABILITY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
