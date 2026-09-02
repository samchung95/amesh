# EPIC-501 — Service accounts, API tokens and credentials

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Support non-human automation identities with scoped, rotatable and observable credentials.

## In scope

- [x] **URS-F-0502** — The system shall create service accounts with roles, groups, tenant and namespace bindings.
- [x] **URS-F-0503** — The system shall issue hashed or asymmetric API tokens with name, scopes, audience, expiry and last-used metadata.
- [x] **URS-F-0504** — The system shall show token material only once and support rotation with an overlap period.
- [x] **URS-F-0505** — The system shall revoke tokens, sessions and derived credentials immediately across components.
- [x] **URS-F-0506** — The system shall support workload identity and short-lived token exchange for workers and plugins.
- [x] **URS-F-0507** — The system shall apply independent quotas and rate limits to automation identities.
- [x] **URS-F-0508** — The system shall record token creation, use, failure, rotation and revocation without storing token plaintext.
- [x] **URS-F-0509** — The system shall prevent service accounts from interactive login unless explicitly supported by policy.

## Implementation completion evidence

- 2026-08-21 — EPIC-501 is complete. AMESH now issues one-time 256-bit opaque API and derived workload tokens whose keyed digests, scopes, audience, expiry, last-use, independent quota and lifecycle remain PostgreSQL-authoritative; service accounts consume the existing role/group/tenant/namespace policy; rotation supports bounded overlap and current/previous pepper rollout; token, derived-child and principal-epoch revocation take effect on the next request; worker/plugin exchange is scope-narrowing and capped at one hour; and lifecycle success/failure audit evidence contains no token plaintext. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`credentials.py`](../../src/amesh/credentials.py), [`credential_repository.py`](../../src/amesh/adapters/postgres/credential_repository.py), [`test_credential_repository.py`](../../tests/adapters/postgres/test_credential_repository.py), and [`test_credential_api.py`](../../tests/api/test_credential_api.py).

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-002** — Components, workers, plugins and runners shall receive only the identities and capabilities required for their role and current operation. Target: Reference deployments pass privilege review with no shared administrator credentials.
- [ ] **URS-NFR-SECURITY-006** — User, service, component and provider credentials shall be rotatable without rebuilding application images. Target: Reference rotation procedures complete without losing accepted work.

## Dependencies

- EPIC-500

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
- Threat-model review and deployment policy tests.
- Automated token, certificate and external-secret rotation tests.
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

- Functional requirements: URS-F-0502, URS-F-0503, URS-F-0504, URS-F-0505, URS-F-0506, URS-F-0507, URS-F-0508, URS-F-0509
- Non-functional requirements: URS-NFR-SECURITY-002, URS-NFR-SECURITY-006
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
