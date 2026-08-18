# EPIC-803 — Multi-region and edge worker topology

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** Platform operator
- **Parity scope:** AMESH differentiator; not a Kestra-parity claim

## Outcome

Place execution near private infrastructure while maintaining centralized governance and durable control.

## In scope

- [ ] **URS-F-0774** — The system shall register regional or edge worker pools with capabilities, trust domain, connectivity and data-residency labels.
- [ ] **URS-F-0775** — The system shall route task runs by policy without exposing private service credentials to the central control plane.
- [ ] **URS-F-0776** — The system shall tolerate intermittent worker connectivity through durable local queues and bounded offline leases.
- [ ] **URS-F-0777** — The system shall prevent stale disconnected workers from committing after ownership has moved.
- [ ] **URS-F-0778** — The system shall keep large task data on regional object storage with explicit transfer policy.
- [ ] **URS-F-0779** — The system shall replicate only required metadata and redact location-sensitive information.
- [ ] **URS-F-0780** — The system shall report regional health, lag, capacity, data transfer and failover state.
- [ ] **URS-F-0781** — The system shall document unsupported active-active metadata semantics and consistency tradeoffs.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-101
- EPIC-503
- EPIC-601

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Feature-specific end-to-end and policy tests.
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

- Functional requirements: URS-F-0774, URS-F-0775, URS-F-0776, URS-F-0777, URS-F-0778, URS-F-0779, URS-F-0780, URS-F-0781
- Non-functional requirements: none specifically mapped
- Source scope: AMESH differentiator; not a Kestra-parity claim
