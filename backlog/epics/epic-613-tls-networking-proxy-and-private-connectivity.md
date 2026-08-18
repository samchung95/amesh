# EPIC-613 — TLS, networking, proxy and private connectivity

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Operate across enterprise networks without weakening transport or destination controls.

## In scope

- [ ] **URS-F-0686** — The system shall support inbound TLS termination directly or through a trusted reverse proxy.
- [ ] **URS-F-0687** — The system shall support mutual TLS between selected internal components and workers.
- [ ] **URS-F-0688** — The system shall support custom certificate authorities and certificate rotation without full service outage.
- [ ] **URS-F-0689** — The system shall support HTTP or HTTPS proxies and explicit no-proxy destinations.
- [ ] **URS-F-0690** — The system shall validate forwarded headers and trusted proxy ranges before constructing external URLs.
- [ ] **URS-F-0691** — The system shall provide egress allowlists and DNS or IP protections for plugins and HTTP tasks.
- [ ] **URS-F-0692** — The system shall support private endpoints and split control-plane or worker network topologies.
- [ ] **URS-F-0693** — The system shall expose connection, certificate, proxy and DNS diagnostics without leaking credentials.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-004** — Production interfaces shall support modern TLS and authenticated internal transport where configured. Target: TLS 1.2 or newer; weak ciphers disabled in reference configurations.
- [ ] **URS-NFR-SECURITY-006** — User, service, component and provider credentials shall be rotatable without rebuilding application images. Target: Reference rotation procedures complete without losing accepted work.

## Dependencies

- EPIC-601
- EPIC-612

## Architecture impact

- Primary bounded area: `operations`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Reference deployment, upgrade and failure-recovery tests.
- Automated protocol scan and reference deployment test.
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

- Functional requirements: URS-F-0686, URS-F-0687, URS-F-0688, URS-F-0689, URS-F-0690, URS-F-0691, URS-F-0692, URS-F-0693
- Non-functional requirements: URS-NFR-SECURITY-004, URS-NFR-SECURITY-006
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
