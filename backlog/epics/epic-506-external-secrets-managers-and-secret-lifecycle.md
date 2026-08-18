# EPIC-506 — External secrets managers and secret lifecycle

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `security`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Resolve secrets from approved stores without making the orchestration database a plaintext vault.

## In scope

- [ ] **URS-F-0542** — The system shall define a provider-neutral secret reference and lookup interface.
- [ ] **URS-F-0543** — The system shall support environment or file development secrets and at least three production secret-manager adapters before GA.
- [ ] **URS-F-0544** — The system shall resolve secrets just in time for an authorized task, trigger, runner or plugin call.
- [ ] **URS-F-0545** — The system shall cache secret values only in protected memory for a bounded duration and support forced invalidation.
- [ ] **URS-F-0546** — The system shall support version pinning, rotation, missing-secret behavior and provider failover policy.
- [ ] **URS-F-0547** — The system shall prevent secret values from entering events, logs, errors, metrics, outputs, caches or UI previews.
- [ ] **URS-F-0548** — The system shall audit secret metadata access and use without recording the value.
- [ ] **URS-F-0549** — The system shall apply namespace and tenant permissions independently from provider-side permissions.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-003** — Secret plaintext shall not appear in persistent metadata, events, logs, metrics, traces, UI payloads or generated support bundles. Target: Zero seeded canary secrets detected across persisted and exported telemetry in the security suite.
- [ ] **URS-NFR-SECURITY-005** — The platform shall support encrypted metadata, object storage and secret-provider configurations. Target: Documented reference configurations use provider-managed or customer-managed encryption keys.
- [ ] **URS-NFR-SECURITY-006** — User, service, component and provider credentials shall be rotatable without rebuilding application images. Target: Reference rotation procedures complete without losing accepted work.
- [ ] **URS-NFR-PORTABILITY-003** — Core transport semantics shall be isolated from PostgreSQL claim mechanics, while object storage, secret providers, model providers and task runners shall use documented capability interfaces. Target: PostgreSQL remains the sole supported internal durable transport and metadata database; every backend category explicitly marked extensible passes its conformance suite.

## Dependencies

- EPIC-500
- EPIC-303

## Architecture impact

- Primary bounded area: `security`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Security integration tests and threat-model review.
- Canary-secret scanning and redaction tests.
- Configuration audit and restore test.
- Automated token, certificate and external-secret rotation tests.
- Static architecture checks plus adapter contract tests for each extensible backend category.
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

- Functional requirements: URS-F-0542, URS-F-0543, URS-F-0544, URS-F-0545, URS-F-0546, URS-F-0547, URS-F-0548, URS-F-0549
- Non-functional requirements: URS-NFR-SECURITY-003, URS-NFR-SECURITY-005, URS-NFR-SECURITY-006, URS-NFR-PORTABILITY-003
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
