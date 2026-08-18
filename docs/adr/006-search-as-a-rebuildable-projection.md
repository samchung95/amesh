# ADR-006: PostgreSQL search as a rebuildable projection

- **Status:** Accepted
- **Decision questions:** Q-008, Q-009
- **Date:** 2026-08-15

## Context

Search, logs and dashboards need read-optimised structures but must not become execution truth. The reference architecture is PostgreSQL-only for stateful control-plane infrastructure.

## Decision

Build search and analytics projections in PostgreSQL using partitioned projection tables, full-text search, `pg_trgm`, materialized views and rollups where appropriate. Projection state remains disposable and rebuildable from authoritative resources and events.

An external search adapter is not part of the baseline or GA requirement. It requires a later ADR if introduced.

## Consequences

- Search can degrade or rebuild without stopping orchestration.
- One backup system covers metadata, queue and projections.
- Large log and analytics workloads require partitioning, retention, archival and carefully bounded queries.
- The UI must aggregate large executions rather than issuing unbounded searches.

## Revisit triggers

- Published search/query targets cannot be achieved at the selected scale profile.
- Customers require a separately operated search service and accept its operational cost.

## Traceability

See `EPIC-409`, `EPIC-604`, `EPIC-608` and `docs/architecture/data-model.md`.
