# EPIC-802 — Policy as code and admission controller

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** Security engineer
- **Parity scope:** AMESH differentiator; not a Kestra-parity claim

## Outcome

Evaluate authoring, deployment and execution policy through open, testable rules.

## In scope

- [ ] **URS-F-0766** — The system shall evaluate policies when validating, saving, promoting, launching and dispatching workflows.
- [ ] **URS-F-0767** — The system shall provide structured policy input for actor, tenant, namespace, flow, plugin, runner, image, secret, network and resource context.
- [ ] **URS-F-0768** — The system shall support deny, warn, mutate-default and require-approval outcomes.
- [ ] **URS-F-0769** — The system shall use an open policy engine or documented declarative rule format.
- [ ] **URS-F-0770** — The system shall version policies and pin decisions to policy revisions.
- [ ] **URS-F-0771** — The system shall test policies with fixtures and explain matched rules and evidence.
- [ ] **URS-F-0772** — The system shall bound evaluation time and fail safely according to policy criticality.
- [ ] **URS-F-0773** — The system shall record every enforcement decision in audit history and execution metadata.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-002** — State, admission, retry, cache, policy and authorization decisions shall expose human-readable evidence to authorized users. Target: Decision evidence is present in all catalogued decision scenarios.

## Dependencies

- EPIC-500
- EPIC-504
- EPIC-505

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Feature-specific end-to-end and policy tests.
- Scenario-based UI and API acceptance tests.
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

- Functional requirements: URS-F-0766, URS-F-0767, URS-F-0768, URS-F-0769, URS-F-0770, URS-F-0771, URS-F-0772, URS-F-0773
- Non-functional requirements: URS-NFR-USABILITY-002
- Source scope: AMESH differentiator; not a Kestra-parity claim
