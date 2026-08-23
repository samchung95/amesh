# EPIC-613 — TLS, networking, proxy and private connectivity

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Operate across enterprise networks without weakening transport or destination controls.

## In scope

- [x] **URS-F-0686** — The system shall support inbound TLS termination directly or through a trusted reverse proxy.
- [x] **URS-F-0687** — The system shall support mutual TLS between selected internal components and workers.
- [x] **URS-F-0688** — The system shall support custom certificate authorities and certificate rotation without full service outage.
- [x] **URS-F-0689** — The system shall support HTTP or HTTPS proxies and explicit no-proxy destinations.
- [x] **URS-F-0690** — The system shall validate forwarded headers and trusted proxy ranges before constructing external URLs.
- [x] **URS-F-0691** — The system shall provide egress allowlists and DNS or IP protections for plugins and HTTP tasks.
- [x] **URS-F-0692** — The system shall support private endpoints and split control-plane or worker network topologies.
- [x] **URS-F-0693** — The system shall expose connection, certificate, proxy and DNS diagnostics without leaking credentials.

## Implementation completion evidence

- 2026-08-23 — EPIC-613 is complete for the locally reproducible enterprise-network profile. AMESH now runs direct modern TLS with optional/required client-certificate authentication or behind a CIDR-trusted TLS proxy; untrusted forwarded origins are rejected before routing. HTTP, download, webhook and OpenRouter task traffic shares explicit HTTP/HTTPS proxy, no-proxy, custom CA/client certificate, hostname/CIDR allowlist, DNS and private-IP controls. Helm provides split component roles, optional Ingress and NetworkPolicy, private-service annotations, mounted certificate Secrets and zero-unavailable rolling rotation. An authorized Administration Operations view and versioned API report redacted connection, certificate fingerprint, proxy and DNS posture. Focused unit/API/frontend checks, TLS context/rotation tests, strict mypy, Ruff, two Helm 4 renders, OpenAPI and four generated SDKs passed. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`networking.md`](../../docs/operations/networking.md), [`041-trusted-network-boundary.md`](../../docs/adr/041-trusted-network-boundary.md), [`networking.py`](../../src/amesh/networking.py), [`test_networking.py`](../../tests/test_networking.py), and [`test_configuration_api.py`](../../tests/api/test_configuration_api.py).

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

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Direct required mTLS covers the complete listener; deployments that require mTLS only for internal workers must expose a dedicated private listener or release boundary.
- Cloud-provider private load balancers and live multi-node certificate-controller rotation remain environment qualification work; the Helm contracts, mounted-secret rotation path and zero-unavailable rollout are locally rendered and tested.

## Traceability

- Functional requirements: URS-F-0686, URS-F-0687, URS-F-0688, URS-F-0689, URS-F-0690, URS-F-0691, URS-F-0692, URS-F-0693
- Non-functional requirements: URS-NFR-SECURITY-004, URS-NFR-SECURITY-006
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
