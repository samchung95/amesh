# EPIC-815 — Hardened client-driven local deployment profile

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `security`
- **Primary persona:** Operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Provide a fail-closed local deployment profile that external clients can safely call without Docker authority, public exposure or unrelated domain credentials.

## In scope

- [x] The hardened profile binds client-facing services to loopback and keeps internal roles on private networks with explicit enabled-role declarations.
- [x] The Docker runner and Docker socket are absent; the scheduler is enabled or explicitly disabled with truthful health semantics.
- [x] Real authentication and scoped service accounts protect every client operation.
- [x] Secrets are references, outbound egress is allowlisted, and private-host access is denied unless explicitly authorized.
- [x] Preflight rejects public binds, development auth, Docker sockets, default credentials, unexpected secrets and missing required roles.
- [x] Compose, uv-based setup, authentication and run smoke tests pass without domain or broker credentials.

## Implementation completion evidence

- 2026-08-26 — EPIC-815 is complete. The checked-in hardened Compose profile binds AMESH to loopback, removes Docker/socket authority and broker/OpenRouter credentials, requires real authentication, uses a password-free database URL plus a permission-restricted `PGPASSFILE` Docker secret, and fails preflight on unsafe exposure or inline secrets. Eight focused deployment tests and Ruff passed. A fresh isolated qualification on port 18016 applied migrations and preflight, completed a real authenticated workflow and evidence read, exposed no database port, mounted no Docker socket, and carried no broker or model-provider credential. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`compose.hardened.yaml`](../../compose.hardened.yaml), [`run-hardened-local-profile.md`](../../docs/how-to/run-hardened-local-profile.md), [`deployment_profile.py`](../../src/amesh/deployment_profile.py), and [`test_hardened_deployment.py`](../../tests/test_hardened_deployment.py).

## Explicit non-goals

- Storing client broker credentials in AMESH
- Qualifying public internet or multi-region hosting

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-403
- EPIC-510
- EPIC-612
- EPIC-810
- EPIC-811

## Architecture impact

- Primary bounded area: `security`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Hardened-profile configuration and fail-closed preflight tests.
- Compose configuration assertions for loopback binds, private networks and absent Docker socket.
- Authentication, service-account scope and egress policy tests.
- Live local authenticated launch and evidence-retrieval smoke test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] A checked-in hardened Compose profile starts with documented secret injection and no development credentials.
- [x] Negative preflight fixtures fail before any service accepts client traffic.
- [x] The deployment runbook states the exact trust and exposure boundary.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Development defaults can be mistaken for a safe client deployment.
- Container runtime authority or broad egress can turn a workflow tool into host compromise.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
