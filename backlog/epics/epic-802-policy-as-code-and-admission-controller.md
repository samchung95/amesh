# EPIC-802 — Policy as code and admission controller

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** Security engineer
- **Parity scope:** AMESH differentiator; not a Kestra-parity claim

## Outcome

Evaluate authoring, deployment and execution policy through open, testable rules.

## In scope

- [x] **URS-F-0766** — The system shall evaluate policies when validating, saving, promoting, launching and dispatching workflows.
- [x] **URS-F-0767** — The system shall provide structured policy input for actor, tenant, namespace, flow, plugin, runner, image, secret, network and resource context.
- [x] **URS-F-0768** — The system shall support deny, warn, mutate-default and require-approval outcomes.
- [x] **URS-F-0769** — The system shall use an open policy engine or documented declarative rule format.
- [x] **URS-F-0770** — The system shall version policies and pin decisions to policy revisions.
- [x] **URS-F-0771** — The system shall test policies with fixtures and explain matched rules and evidence.
- [x] **URS-F-0772** — The system shall bound evaluation time and fail safely according to policy criticality.
- [x] **URS-F-0773** — The system shall record every enforcement decision in audit history and execution metadata.

## Implementation completion evidence

- 2026-08-23 — EPIC-802 is complete. The documented `amesh.policy/v1` engine evaluates immutable instance, tenant and namespace rules at validation, save, promotion, launch and task dispatch; exposes typed actor, tenant, namespace, flow, plugin, runner, image, secret-scope, network and resource input; supports deny, warn, default mutation and explicit approval; bounds evaluation by enforcing/advisory criticality; and pins every decision to revision digests with human-readable evidence. PostgreSQL tenant isolation, immutable revision and decision history, audit linkage, execution/task metadata, fixture testing, generated API clients, Flow Editor validation and the Plugins governance UI passed focused verification. Sensitive inputs are redacted and internal mutation context is excluded from stored decisions. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`admission-policies.md`](../../docs/api/admission-policies.md), [`047-versioned-declarative-admission-policy.md`](../../docs/adr/047-versioned-declarative-admission-policy.md), and [`test_admission_policy.py`](../../tests/policy/test_admission_policy.py).

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

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0766, URS-F-0767, URS-F-0768, URS-F-0769, URS-F-0770, URS-F-0771, URS-F-0772, URS-F-0773
- Non-functional requirements: URS-NFR-USABILITY-002
- Source scope: AMESH differentiator; not a Kestra-parity claim
