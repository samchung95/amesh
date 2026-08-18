# EPIC-502 — SSO, OIDC, SAML, LDAP and SCIM

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Integrate enterprise identity providers using open standards and auditable mapping.

## In scope

- [ ] **URS-F-0510** — The system shall support OpenID Connect authorization-code flow with PKCE and configurable claims.
- [ ] **URS-F-0511** — The system shall support SAML 2.0 service-provider flows with signed assertions and metadata rotation.
- [ ] **URS-F-0512** — The system shall support LDAP or Active Directory authentication and group lookup over TLS.
- [ ] **URS-F-0513** — The system shall support SCIM 2.0 user and group provisioning, update, disable and deprovision operations.
- [ ] **URS-F-0514** — The system shall map identity-provider claims or groups to platform groups and tenant access through explicit rules.
- [ ] **URS-F-0515** — The system shall prevent account takeover through ambiguous email, subject or provider linking.
- [ ] **URS-F-0516** — The system shall test signing-key rotation, clock skew, replay, logout and provider outage behavior.
- [ ] **URS-F-0517** — The system shall allow multiple identity providers with domain or tenant routing policy.

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

- Functional requirements: URS-F-0510, URS-F-0511, URS-F-0512, URS-F-0513, URS-F-0514, URS-F-0515, URS-F-0516, URS-F-0517
- Non-functional requirements: URS-NFR-SECURITY-006
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
