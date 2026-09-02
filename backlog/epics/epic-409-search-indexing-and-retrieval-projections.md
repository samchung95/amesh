# EPIC-409 — Search, indexing and retrieval projections

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `search`
- **Primary persona:** User
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Find flows, executions, logs, assets and governance records quickly without making the search index authoritative.

## In scope

- [x] **URS-F-0470** — The system shall index authorized metadata and selected log fields into a replaceable search projection.
- [x] **URS-F-0471** — The system shall support full-text, field, range, state, label, namespace and time filters.
- [x] **URS-F-0472** — The system shall return stable pagination and relevance or field sorting.
- [x] **URS-F-0473** — The system shall rebuild indexes from authoritative repositories and event history.
- [x] **URS-F-0474** — The system shall continue writes and orchestration during search backend degradation.
- [x] **URS-F-0475** — The system shall prevent cross-tenant leakage in both indexed documents and query execution.
- [x] **URS-F-0476** — The system shall expose index lag, failures, version and rebuild progress.
- [x] **URS-F-0477** — The system shall provide PostgreSQL full-text, trigram and structured search over rebuildable tenant-scoped projections.

## Implementation completion evidence

- 2026-08-23 — EPIC-409 is complete. The indexer now builds a disposable tenant-hash-partitioned PostgreSQL projection for authorized flow, execution, selected non-sensitive log, asset and audit metadata. The typed API and React workbench support full-text, trigram, structured field/range/state/label/namespace/time filters, deterministic opaque-cursor paging, independent source authorization, projection health and tenant rebuild. Fresh 44-migration PostgreSQL tests verified rebuild, cross-tenant isolation and degradation recovery while orchestration and other indexer work continued. A local 50,000-document workload passed the provisional p95 search budget; the dedicated 10-million-retained-execution qualification is explicitly deferred to a scale environment. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`search.md`](../../docs/api/search.md), [`SearchPage.tsx`](../../frontend/src/pages/SearchPage.tsx), [`test_search_repository.py`](../../tests/adapters/postgres/test_search_repository.py), and [`0044_search_projection.sql`](../../migrations/0044_search_projection.sql).

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-005** — Core orchestration shall continue when optional search, telemetry, outbound webhook or analytics services are unavailable. Target: New and running executions continue within documented latency budgets during optional-service outage tests.
- [ ] **URS-NFR-PERFORMANCE-001** — Common authenticated read and write APIs shall remain responsive at the standard reference scale. Target: Provisional target: p95 below 500 ms and p99 below 1.5 s excluding bulk exports and external dependencies.
- [ ] **URS-NFR-PORTABILITY-003** — Core transport semantics shall be isolated from PostgreSQL claim mechanics, while object storage, secret providers, model providers and task runners shall use documented capability interfaces. Target: PostgreSQL remains the sole supported internal durable transport and metadata database; every backend category explicitly marked extensible passes its conformance suite.

## Dependencies

- EPIC-008
- EPIC-009

## Architecture impact

- Primary bounded area: `search`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Projection rebuild, isolation and query contract tests.
- Dependency isolation and outage integration tests.
- Repeatable load test with 10 million retained execution records and realistic filters.
- Static architecture checks plus adapter contract tests for each extensible backend category.
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

- Functional requirements: URS-F-0470, URS-F-0471, URS-F-0472, URS-F-0473, URS-F-0474, URS-F-0475, URS-F-0476, URS-F-0477
- Non-functional requirements: URS-NFR-RELIABILITY-005, URS-NFR-PERFORMANCE-001, URS-NFR-PORTABILITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
