# EPIC-503 — Multi-tenancy and resource isolation

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Platform operator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Host multiple organizations or environments with strong logical isolation and independent administration.

## In scope

- [x] **URS-F-0518** — The system shall scope every resource, query, message, cache entry, artifact and audit event to an explicit tenant.
- [x] **URS-F-0519** — The system shall require tenant context at service boundaries and reject implicit fallback outside single-tenant mode.
- [x] **URS-F-0520** — The system shall support tenant creation, suspension, deletion, export and restoration workflows.
- [x] **URS-F-0521** — The system shall apply tenant-specific quotas, retention, encryption, identity providers, plugins and feature flags.
- [x] **URS-F-0522** — The system shall prevent identifiers, timing, search, metrics, logs and error messages from leaking cross-tenant information.
- [x] **URS-F-0523** — The system shall support tenant-aware worker groups and storage prefixes or buckets.
- [x] **URS-F-0524** — The system shall let super-administrators operate across tenants with separately audited privileges.
- [x] **URS-F-0525** — The system shall prove isolation with adversarial automated tests and database policy checks.

## Implementation completion evidence

- 2026-08-21 — EPIC-503 is complete. AMESH now requires explicit tenant context in multi-tenant mode; manages tenant creation, suspension, export, tombstone and restore; enforces tenant execution quotas, feature flags and plugin allowlists; routes schedulers and workers by active tenant and worker group; derives immutable tenant storage prefixes; scopes execution and durable-transport operations through transaction-local forced PostgreSQL RLS; supports a non-superuser tenant-repository login through restricted security-definer selectors and a narrow administration role; uses tenant-specific queue notification channels; and separately audits cross-tenant super-administration. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`multi-tenancy.md`](../../docs/operations/multi-tenancy.md), [`0006_multi_tenancy.sql`](../../migrations/0006_multi_tenancy.sql), [`0008_restricted_tenant_resolution.sql`](../../migrations/0008_restricted_tenant_resolution.sql), [`0009_tenant_administration_role.sql`](../../migrations/0009_tenant_administration_role.sql), [`test_tenant_repository.py`](../../tests/adapters/postgres/test_tenant_repository.py), [`test_durable_transport.py`](../../tests/adapters/postgres/test_durable_transport.py), and [`test_tenant_api.py`](../../tests/api/test_tenant_api.py). Shared URS-NFR-SECURITY-001 remains In Progress until EPIC-604/605 and pre-GA penetration testing complete.

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

- Functional requirements: URS-F-0518, URS-F-0519, URS-F-0520, URS-F-0521, URS-F-0522, URS-F-0523, URS-F-0524, URS-F-0525
- Non-functional requirements: URS-NFR-SECURITY-001
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
