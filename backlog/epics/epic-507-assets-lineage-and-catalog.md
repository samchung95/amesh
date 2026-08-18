# EPIC-507 — Assets, lineage and catalog

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Data steward
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Represent data and infrastructure assets and their relationship to workflows and executions.

## In scope

- [ ] **URS-F-0550** — The system shall register assets from explicit declarations and plugin-emitted read or write events.
- [ ] **URS-F-0551** — The system shall identify assets by provider, account, location, type and stable external key.
- [ ] **URS-F-0552** — The system shall link assets to producing and consuming flows, task runs, executions and artifacts.
- [ ] **URS-F-0553** — The system shall display upstream, downstream, last materialization, health and ownership metadata.
- [ ] **URS-F-0554** — The system shall support custom metadata, tags, descriptions, contacts and domain grouping.
- [ ] **URS-F-0555** — The system shall record lineage confidence and distinguish declared, observed and inferred edges.
- [ ] **URS-F-0556** — The system shall apply tenant and namespace permissions to asset visibility and lineage traversal.
- [ ] **URS-F-0557** — The system shall export catalog and lineage through API and open interchange formats where practical.

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

- Functional requirements: URS-F-0550, URS-F-0551, URS-F-0552, URS-F-0553, URS-F-0554, URS-F-0555, URS-F-0556, URS-F-0557
- Non-functional requirements: none specifically mapped
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
