# EPIC-804 — Open enterprise distribution and packaging

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** Operator
- **Parity scope:** AMESH differentiator; not a Kestra-parity claim

## Outcome

Ship every production capability under an OSI-approved license without artificial feature gates.

## In scope

- [ ] **URS-F-0782** — The system shall build one public source tree containing standalone, distributed, governance and administration features.
- [ ] **URS-F-0783** — The system shall avoid license-key checks or closed runtime dependencies for core production operation.
- [ ] **URS-F-0784** — The system shall publish complete source and reproducible build instructions for official artifacts.
- [ ] **URS-F-0785** — The system shall permit commercial support and hosted offerings without restricting self-hosted capability.
- [ ] **URS-F-0786** — The system shall document optional trademark, certification or hosted-service boundaries separately from software rights.
- [ ] **URS-F-0787** — The system shall make telemetry, update checks and external services opt-in or replaceable.
- [ ] **URS-F-0788** — The system shall publish a bill of materials showing the license of every distributed dependency.
- [ ] **URS-F-0789** — The system shall maintain a contributor certificate or developer certificate process appropriate to the selected governance model.

## Non-functional requirements

- [ ] **URS-NFR-PORTABILITY-001** — The self-hosted platform shall not require a proprietary control service or license server for any GA capability. Target: Air-gapped reference deployment passes the full core and governance acceptance suite.
- [ ] **URS-NFR-PRIVACY-001** — Product analytics and update checks shall be disabled by default or require an explicit informed opt-in. Target: No undeclared outbound connection occurs in the offline network test.

## Dependencies

- EPIC-001
- EPIC-612

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Feature-specific end-to-end and policy tests.
- Offline installation and test run.
- Network capture in a clean reference deployment.
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

- Functional requirements: URS-F-0782, URS-F-0783, URS-F-0784, URS-F-0785, URS-F-0786, URS-F-0787, URS-F-0788, URS-F-0789
- Non-functional requirements: URS-NFR-PORTABILITY-001, URS-NFR-PRIVACY-001
- Source scope: AMESH differentiator; not a Kestra-parity claim
