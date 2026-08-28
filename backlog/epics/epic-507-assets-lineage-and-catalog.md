# EPIC-507 — Assets, lineage and catalog

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Data steward
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Represent data and infrastructure assets and their relationship to workflows and executions.

## In scope

- [x] **URS-F-0550** — The system shall register assets from explicit declarations and plugin-emitted read or write events.
- [x] **URS-F-0551** — The system shall identify assets by provider, account, location, type and stable external key.
- [x] **URS-F-0552** — The system shall link assets to producing and consuming flows, task runs, executions and artifacts.
- [x] **URS-F-0553** — The system shall display upstream, downstream, last materialization, health and ownership metadata.
- [x] **URS-F-0554** — The system shall support custom metadata, tags, descriptions, contacts and domain grouping.
- [x] **URS-F-0555** — The system shall record lineage confidence and distinguish declared, observed and inferred edges.
- [x] **URS-F-0556** — The system shall apply tenant and namespace permissions to asset visibility and lineage traversal.
- [x] **URS-F-0557** — The system shall export catalog and lineage through API and open interchange formats where practical.

## Implementation completion evidence

- 2026-08-23 — EPIC-507 is complete. Migration 0048 extends the tenant-scoped asset catalog with provider/account/location/type/external-key identity, ownership and governance metadata, durable read/write observations, execution/task/artifact links, confidence-bearing declared and inferred lineage, and row-level tenant isolation. Explicit API declarations and authenticated isolated-plugin `amesh.asset` notifications feed the same persistence path. The authorized API and Assets UI list, declare, filter and traverse only visible namespace resources, while OpenLineage RunEvent export maps the stable provider identity without requiring an external catalog. Evidence: [`asset-catalog-and-lineage.md`](../../docs/api/asset-catalog-and-lineage.md), [`0048_asset_catalog_lineage.sql`](../../migrations/0048_asset_catalog_lineage.sql), [`test_asset_catalog_repository.py`](../../tests/adapters/postgres/test_asset_catalog_repository.py), [`test_asset_catalog_api.py`](../../tests/api/test_asset_catalog_api.py), [`test_isolated_runtime.py`](../../tests/plugins/test_isolated_runtime.py), and [`shell.spec.ts`](../../frontend/e2e/shell.spec.ts).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-111
- EPIC-308
- EPIC-500

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
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

- Functional requirements: URS-F-0550, URS-F-0551, URS-F-0552, URS-F-0553, URS-F-0554, URS-F-0555, URS-F-0556, URS-F-0557
- Non-functional requirements: none specifically mapped
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
