# EPIC-806 — Multi-agent topology, typed hand-offs and routing

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH Agent Mesh differentiator; not a Kestra-parity claim

## Outcome

Coordinate multiple already-bounded agent sessions through typed hand-offs and explainable routing without creating a second execution engine.

## In scope

- [x] **URS-F-0808** — The system shall support supervisor, router, peer-to-peer, hierarchical and swarm mesh topologies without creating a second execution engine.
- [x] **URS-F-0810** — The system shall validate agent-to-agent hand-offs against typed schemas and preserve source, destination, rationale and context provenance.
- [x] **URS-F-0811** — The system shall route work by declared capability, policy, cost, latency, availability and evaluation score with an explainable decision record.

## Explicit non-goals

- Giving models direct access to orchestration state or plaintext secrets
- Claiming deterministic model output
- Maintaining agent or mesh state outside the existing execution reducer

## Non-functional requirements

- [ ] **URS-NFR-AGENT-001** — Agent and mesh budgets shall be enforced by the platform independently of model compliance. Target: No test mesh exceeds its configured hard cost, token, duration or tool-call limit beyond one explicitly bounded in-flight operation.
- [ ] **URS-NFR-AGENT-002** — Every agent message, routing decision, tool call, hand-off, approval and model response shall be traceable to pinned policy and execution context. Target: All catalogued mesh scenarios produce a complete provenance graph with no orphan tool effects.
- [ ] **URS-NFR-AGENT-003** — Agent memory, tools and credentials shall be isolated by tenant, namespace, execution and delegated capability. Target: Zero cross-boundary disclosure or unauthorised tool invocation in adversarial mesh tests.
- [ ] **URS-NFR-AGENT-004** — Core mesh state and policy shall remain usable when a model provider is disabled or replaced. Target: Reference meshes migrate between two conforming model adapters with documented output nondeterminism and no state-schema change.

## Dependencies

- EPIC-503
- EPIC-802
- EPIC-808
- EPIC-809

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Multi-agent topology, typed hand-off, routing, budget, provenance and failover end-to-end tests.
- Adversarial runaway-loop and concurrent tool-call tests.
- Provenance graph completeness tests.
- Cross-tenant, prompt-injection and capability-confusion tests.
- Provider substitution and outage tests.
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

- Concurrent routing can amplify cost and side effects across otherwise bounded sessions
- A schema-valid hand-off can still be semantically wrong or malicious
- Shared-memory and capability confusion can cross agent or tenant boundaries
- Model nondeterminism can be mistaken for deterministic workflow replay

## Traceability

- Functional requirements: URS-F-0808, URS-F-0810, URS-F-0811
- Non-functional requirements: URS-NFR-AGENT-001, URS-NFR-AGENT-002, URS-NFR-AGENT-003, URS-NFR-AGENT-004
- Source scope: AMESH Agent Mesh differentiator; not a Kestra-parity claim
