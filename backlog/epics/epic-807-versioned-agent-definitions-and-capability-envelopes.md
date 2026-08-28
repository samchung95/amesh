# EPIC-807 — Versioned agent definitions and capability envelopes

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH Agent Mesh differentiator; not a Kestra-parity claim

## Outcome

Define reusable, versioned agent resources whose model, prompt, skill, tool, permission, environment, budget and output-contract revisions resolve and pin before execution.

## In scope

- [x] **URS-F-0806** — The system shall define versioned agent resources containing model routing, instructions, tools, skills, memory policy, permissions, budgets and evaluation policy.
- [x] **URS-F-0807** — The system shall pin resolved agent, model-policy, tool and prompt revisions to every agent session and workflow execution.
- [x] **URS-F-0815** — The system shall provide provider-neutral model adapters, fallback policies and migration diagnostics without changing workflow semantics silently.
- [x] **URS-F-0818** — The system shall expose approved workflows, agents and tools through authenticated MCP and other versioned agent-protocol adapters.

## Implementation completion evidence

- 2026-08-25 — EPIC-807 is complete. One tenant- and namespace-isolated immutable ledger now versions prompt, declarative skill, model-policy and agent resources. Exact resolution verifies every resource and governed MCP tool revision, schema digest, credential reference, network host, delegated capability, high-impact permission, schema and hard boundary before atomically attaching a content-addressed `amesh.agent-envelope/v1` pin to a session or workflow-execution subject. The guided Agents page, REST API and CLI create, inspect, compare, resolve and explain revisions without raw configuration being mandatory. Provider migrations require a new reviewed revision and always disclose model-output nondeterminism. Authenticated MCP adds read-only agent discovery and exact inspection without returning credential values. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`agent-primitives.md`](../../docs/api/agent-primitives.md), [`define-agent-capability-envelope.md`](../../docs/how-to/define-agent-capability-envelope.md), [`052-typed-agent-resource-ledger-and-atomic-capability-pins.md`](../../docs/adr/052-typed-agent-resource-ledger-and-atomic-capability-pins.md), [`test_agent_resources.py`](../../tests/domain/test_agent_resources.py), and [`test_agent_resource_repository.py`](../../tests/adapters/postgres/test_agent_resource_repository.py).

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

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Mutable prompt, skill or tool references can make an execution impossible to explain or replay
- A skill abstraction can become an ungoverned code or secret-delivery path
- Provider-specific model features can leak into the durable agent contract

## Traceability

- Functional requirements: URS-F-0806, URS-F-0807, URS-F-0815, URS-F-0818
- Non-functional requirements: URS-NFR-AGENT-003, URS-NFR-AGENT-004
- Source scope: AMESH Agent Mesh differentiator; not a Kestra-parity claim
