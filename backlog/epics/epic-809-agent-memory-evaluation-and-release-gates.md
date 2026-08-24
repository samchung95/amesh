# EPIC-809 — Agent memory, evaluation and release gates

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH Agent Mesh differentiator; not a Kestra-parity claim

## Outcome

Make bounded agents safe to adopt through isolated memory, versioned evaluations, human-readable traces and evidence-backed promotion gates in the existing workflow experience.

## In scope

- [ ] **URS-F-0812** — The system shall provide isolated private memory and policy-controlled shared memory with retention, redaction, size and tenant boundaries.
- [ ] **URS-F-0816** — The system shall evaluate agent and mesh outcomes against versioned tests, rubrics, judges and business assertions.
- [ ] **URS-F-0819** — The system shall interleave agent sessions, ordinary tasks and human approval tasks in one state machine, timeline and audit trail.

## Explicit non-goals

- Using an LLM judge as the sole authority for high-impact release or tool decisions
- Storing unrestricted conversation history without retention and redaction policy

## Non-functional requirements

- [ ] **URS-NFR-AGENT-002** — Every agent message, routing decision, tool call, hand-off, approval and model response shall be traceable to pinned policy and execution context. Target: All catalogued mesh scenarios produce a complete provenance graph with no orphan tool effects.
- [ ] **URS-NFR-AGENT-003** — Agent memory, tools and credentials shall be isolated by tenant, namespace, execution and delegated capability. Target: Zero cross-boundary disclosure or unauthorised tool invocation in adversarial mesh tests.
- [ ] **URS-NFR-AGENT-004** — Core mesh state and policy shall remain usable when a model provider is disabled or replaced. Target: Reference meshes migrate between two conforming model adapters with documented output nondeterminism and no state-schema change.

## Dependencies

- EPIC-407
- EPIC-508
- EPIC-510
- EPIC-800
- EPIC-808

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Agent memory-isolation, evaluation, trace, approval-interleaving and release-gate end-to-end tests.
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

- Shared memory can disclose information across executions, namespaces or tenants
- LLM judges can be nondeterministic, biased or correlated with the model under test
- A passing format or rubric score can be mistaken for business correctness

## Traceability

- Functional requirements: URS-F-0812, URS-F-0816, URS-F-0819
- Non-functional requirements: URS-NFR-AGENT-002, URS-NFR-AGENT-003, URS-NFR-AGENT-004
- Source scope: AMESH Agent Mesh differentiator; not a Kestra-parity claim
