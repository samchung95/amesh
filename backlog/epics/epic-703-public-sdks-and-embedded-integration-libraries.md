# EPIC-703 — Public SDKs and embedded integration libraries

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `api`
- **Primary persona:** Application developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Integrate the orchestrator into applications using supported language libraries.

## In scope

- [ ] **URS-F-0718** — The system shall publish supported SDKs for Python, JavaScript or TypeScript, Java and Go.
- [ ] **URS-F-0719** — The system shall provide typed models, authentication, retries, idempotency, pagination, streaming and error helpers.
- [ ] **URS-F-0720** — The system shall support execution launch, monitoring, cancellation, logs, artifacts and webhook verification.
- [ ] **URS-F-0721** — The system shall maintain semantic-version compatibility aligned with API support policy.
- [ ] **URS-F-0722** — The system shall generate most models from OpenAPI while hand-crafting ergonomic high-level operations.
- [ ] **URS-F-0723** — The system shall publish examples for web applications, CLIs, CI systems and event consumers.
- [ ] **URS-F-0724** — The system shall test SDKs against live conformance environments in release CI.
- [ ] **URS-F-0725** — The system shall document thread safety, async support and transport customization.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-400
- EPIC-401

## Architecture impact

- Primary bounded area: `api`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- OpenAPI contract and authenticated end-to-end API tests.
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

- Functional requirements: URS-F-0718, URS-F-0719, URS-F-0720, URS-F-0721, URS-F-0722, URS-F-0723, URS-F-0724, URS-F-0725
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
