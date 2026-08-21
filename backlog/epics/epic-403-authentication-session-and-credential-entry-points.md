# EPIC-403 — Authentication session and credential entry points

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `security`
- **Primary persona:** User
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide secure local and federated entry points while keeping authorization separate.

## In scope

- [ ] **URS-F-0422** — The system shall support secure local administrator bootstrap without shipping universal default credentials.
- [ ] **URS-F-0423** — The system shall support browser sessions with secure cookies, CSRF protection, rotation, inactivity and absolute expiry.
- [ ] **URS-F-0424** — The system shall support bearer tokens for API and CLI clients with explicit audience and expiry.
- [ ] **URS-F-0425** — The system shall apply account lockout, rate limiting and anomaly telemetry to authentication attempts.
- [ ] **URS-F-0426** — The system shall support logout, global session revocation and credential rotation.
- [ ] **URS-F-0427** — The system shall record authentication events without logging passwords, assertions or token material.
- [ ] **URS-F-0428** — The system shall expose a provider-neutral authentication interface used by OIDC, SAML, LDAP and local modes.
- [ ] **URS-F-0429** — The system shall disable local password authentication when policy requires federated-only access.

## MVP implementation progress

- 2026-08-21 — W6 verified the explicitly accepted single-admin MVP boundary: protected REST endpoints reject missing bearer credentials and accept the configured static admin token while validation remains public. Evidence: [`TESTLOG.md`](../../TESTLOG.md) and [`test_mvp_api.py`](../../tests/api/test_mvp_api.py). Sessions, users, federation and the broader authentication epic remain open.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-010** — Fresh production-oriented configurations shall fail closed for authentication, plugin trust, network exposure and secrets. Target: Security baseline scanner reports no critical unsafe defaults.

## Dependencies

- EPIC-500
- EPIC-501
- EPIC-502

## Architecture impact

- Primary bounded area: `security`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Security integration tests and threat-model review.
- Configuration conformance and container scan.
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

- Functional requirements: URS-F-0422, URS-F-0423, URS-F-0424, URS-F-0425, URS-F-0426, URS-F-0427, URS-F-0428, URS-F-0429
- Non-functional requirements: URS-NFR-SECURITY-010
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
