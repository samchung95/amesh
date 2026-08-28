# EPIC-502 — SSO, OIDC, SAML, LDAP and SCIM

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Integrate enterprise identity providers using open standards and auditable mapping.

## In scope

- [x] **URS-F-0510** — The system shall support OpenID Connect authorization-code flow with PKCE and configurable claims.
- [x] **URS-F-0511** — The system shall support SAML 2.0 service-provider flows with signed assertions and metadata rotation.
- [x] **URS-F-0512** — The system shall support LDAP or Active Directory authentication and group lookup over TLS.
- [x] **URS-F-0513** — The system shall support SCIM 2.0 user and group provisioning, update, disable and deprovision operations.
- [x] **URS-F-0514** — The system shall map identity-provider claims or groups to platform groups and tenant access through explicit rules.
- [x] **URS-F-0515** — The system shall prevent account takeover through ambiguous email, subject or provider linking.
- [x] **URS-F-0516** — The system shall test signing-key rotation, clock skew, replay, logout and provider outage behavior.
- [x] **URS-F-0517** — The system shall allow multiple identity providers with domain or tenant routing policy.

## Implementation completion evidence

- 2026-08-23 — EPIC-502 is complete. AMESH now provides configurable multi-provider OIDC authorization-code/PKCE, strict SAML service-provider metadata and certificate rollover, TLS-only LDAP/AD authentication and group lookup, explicit claim/group-to-platform and tenant mapping, immutable provider-subject links that reject ambiguous identity ownership, and tenant/provider-isolated SCIM user/group lifecycle APIs. One-time state and assertion fences reject replay; signed token validation covers issuer, audience, nonce, asymmetric algorithms, clock skew and live JWKS rotation; mounted client secrets, certificates, trust anchors and SCIM tokens rotate without rebuilding the image. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`identity-federation.md`](../../docs/operations/identity-federation.md), [`identity-and-scim.md`](../../docs/api/identity-and-scim.md), [`federation.py`](../../src/amesh/federation.py), [`federation_repository.py`](../../src/amesh/adapters/postgres/federation_repository.py), [`test_federation.py`](../../tests/domain/test_federation.py), [`test_federation_repository.py`](../../tests/adapters/postgres/test_federation_repository.py), and [`test_federation_api.py`](../../tests/api/test_federation_api.py). The provider-credential contribution to shared URS-NFR-SECURITY-006 is verified; the shared NFR remains In Progress with EPIC-506 and EPIC-613.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-006** — User, service, component and provider credentials shall be rotatable without rebuilding application images. Target: Reference rotation procedures complete without losing accepted work.

## Dependencies

- EPIC-500
- EPIC-403

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
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

- Functional requirements: URS-F-0510, URS-F-0511, URS-F-0512, URS-F-0513, URS-F-0514, URS-F-0515, URS-F-0516, URS-F-0517
- Non-functional requirements: URS-NFR-SECURITY-006
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
