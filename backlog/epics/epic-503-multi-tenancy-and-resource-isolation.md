# EPIC-503 — Multi-tenancy and resource isolation

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Platform operator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Host multiple organizations or environments with strong logical isolation and independent administration.

## In scope

- [ ] **URS-F-0518** — The system shall scope every resource, query, message, cache entry, artifact and audit event to an explicit tenant.
- [ ] **URS-F-0519** — The system shall require tenant context at service boundaries and reject implicit fallback outside single-tenant mode.
- [ ] **URS-F-0520** — The system shall support tenant creation, suspension, deletion, export and restoration workflows.
- [ ] **URS-F-0521** — The system shall apply tenant-specific quotas, retention, encryption, identity providers, plugins and feature flags.
- [ ] **URS-F-0522** — The system shall prevent identifiers, timing, search, metrics, logs and error messages from leaking cross-tenant information.
- [ ] **URS-F-0523** — The system shall support tenant-aware worker groups and storage prefixes or buckets.
- [ ] **URS-F-0524** — The system shall let super-administrators operate across tenants with separately audited privileges.
- [ ] **URS-F-0525** — The system shall prove isolation with adversarial automated tests and database policy checks.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-001** — No API, event, cache, log, metric, search, storage or plugin path shall expose one tenant's protected data to another. Target: Zero cross-tenant findings in adversarial isolation test suite and pre-GA penetration test.

## Dependencies

- EPIC-002
- EPIC-500

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
- Automated negative tests, database checks and independent penetration testing.
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

- Functional requirements: URS-F-0518, URS-F-0519, URS-F-0520, URS-F-0521, URS-F-0522, URS-F-0523, URS-F-0524, URS-F-0525
- Non-functional requirements: URS-NFR-SECURITY-001
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
