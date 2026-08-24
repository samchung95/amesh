# EPIC-807 — Versioned agent definitions and capability envelopes

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH Agent Mesh differentiator; not a Kestra-parity claim

## Outcome

Define reusable, versioned agent resources whose model, prompt, skill, tool, permission, environment, budget and output-contract revisions resolve and pin before execution.

## In scope

- [ ] **URS-F-0806** — The system shall define versioned agent resources containing model routing, instructions, tools, skills, memory policy, permissions, budgets and evaluation policy.
- [ ] **URS-F-0807** — The system shall pin resolved agent, model-policy, tool and prompt revisions to every agent session and workflow execution.
- [ ] **URS-F-0815** — The system shall provide provider-neutral model adapters, fallback policies and migration diagnostics without changing workflow semantics silently.
- [ ] **URS-F-0818** — The system shall expose approved workflows, agents and tools through authenticated MCP and other versioned agent-protocol adapters.

## Explicit non-goals

- Executing an autonomous reasoning loop
- Letting skills bypass plugin, tool, secret or network policy
- Persisting plaintext credentials in agent definitions

## Non-functional requirements

- [ ] **URS-NFR-AGENT-003** — Agent memory, tools and credentials shall be isolated by tenant, namespace, execution and delegated capability. Target: Zero cross-boundary disclosure or unauthorised tool invocation in adversarial mesh tests.
- [ ] **URS-NFR-AGENT-004** — Core mesh state and policy shall remain usable when a model provider is disabled or replaced. Target: Reference meshes migrate between two conforming model adapters with documented output nondeterminism and no state-schema change.

## Dependencies

- EPIC-207
- EPIC-303
- EPIC-312
- EPIC-505
- EPIC-802

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Agent resource schema, resolution, authorization, pinning and provider-adapter contract tests.
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

- Mutable prompt, skill or tool references can make an execution impossible to explain or replay
- A skill abstraction can become an ungoverned code or secret-delivery path
- Provider-specific model features can leak into the durable agent contract

## Traceability

- Functional requirements: URS-F-0806, URS-F-0807, URS-F-0815, URS-F-0818
- Non-functional requirements: URS-NFR-AGENT-003, URS-NFR-AGENT-004
- Source scope: AMESH Agent Mesh differentiator; not a Kestra-parity claim
