# EPIC-808 — Durable bounded single-agent sessions

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH Agent Mesh differentiator; not a Kestra-parity claim

## Outcome

Run one supervised agent as a durable workflow task whose model turns and tool proposals are mediated by AMESH and cannot succeed until structured-output and policy gates pass.

## In scope

- [x] **URS-F-0809** — The system shall persist agent sessions, messages, tool calls, checkpoints and approvals as durable execution evidence.
- [x] **URS-F-0813** — The system shall enforce loop, recursion, concurrency, token, cost, duration and tool-call limits with circuit breakers.
- [x] **URS-F-0814** — The system shall require policy or human approval before agents invoke high-impact tools, move sensitive data or exceed delegated authority.
- [x] **URS-F-0817** — The system shall resume an interrupted agent session from a durable checkpoint while disclosing which model outputs cannot be reproduced deterministically.

## Implementation completion evidence

- 2026-08-25 — EPIC-808 is complete. `agent.session` now runs one exact capability-envelope revision as a recoverable task inside the existing execution engine. Migration 0058 adds a tenant-isolated session checkpoint and idempotent event journal projected into ordinary execution evidence. AMESH mediates one model proposal or fenced MCP call at a time, persists stable per-operation identities, reuses accepted results after restart, fails closed on ambiguous external outcomes, and discloses model nondeterminism. The platform enforces cumulative turns, loops, tool calls, tokens, cost and duration; rejects unpinned authority; requires direct human approval for high-impact tools or sensitive egress; and accepts completion only after the pinned output schema plus deterministic business assertions pass. The authorized session API and simple trace expose phase, budget, tool, approval, validation and final-result evidence. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`agent-primitives.md`](../../docs/api/agent-primitives.md), [`run-bounded-agent-session.md`](../../docs/how-to/run-bounded-agent-session.md), [`053-durable-agent-session-journal.md`](../../docs/adr/053-durable-agent-session-journal.md), [`test_agent_sessions.py`](../../tests/tasks/test_agent_sessions.py), [`test_agent_session_repository.py`](../../tests/adapters/postgres/test_agent_session_repository.py), and [`executionTraceModel.test.ts`](../../frontend/src/components/executionTraceModel.test.ts). Shared mesh-wide NFRs remain In Progress for EPIC-809/806 memory, evaluation and multi-agent scenarios.

## Explicit non-goals

- Giving models direct access to execution state, plaintext secrets or tool transports
- Claiming deterministic model output
- Allowing unbounded graph, recursion or tool expansion

## Non-functional requirements

- [ ] **URS-NFR-AGENT-001** — Agent and mesh budgets shall be enforced by the platform independently of model compliance. Target: No test mesh exceeds its configured hard cost, token, duration or tool-call limit beyond one explicitly bounded in-flight operation.
- [ ] **URS-NFR-AGENT-002** — Every agent message, routing decision, tool call, hand-off, approval and model response shall be traceable to pinned policy and execution context. Target: All catalogued mesh scenarios produce a complete provenance graph with no orphan tool effects.
- [ ] **URS-NFR-AGENT-003** — Agent memory, tools and credentials shall be isolated by tenant, namespace, execution and delegated capability. Target: Zero cross-boundary disclosure or unauthorised tool invocation in adversarial mesh tests.

## Dependencies

- EPIC-104
- EPIC-108
- EPIC-312
- EPIC-508
- EPIC-802
- EPIC-807

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Single-agent session state, budget, tool mediation, approval, checkpoint and recovery end-to-end tests.
- Adversarial runaway-loop and concurrent tool-call tests.
- Provenance graph completeness tests.
- Cross-tenant, prompt-injection and capability-confusion tests.
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

- A runaway loop can exhaust token, cost, duration or tool-call budgets
- Restarted sessions can duplicate non-idempotent tool effects
- Schema-valid output can still fail business or safety expectations

## Traceability

- Functional requirements: URS-F-0809, URS-F-0813, URS-F-0814, URS-F-0817
- Non-functional requirements: URS-NFR-AGENT-001, URS-NFR-AGENT-002, URS-NFR-AGENT-003
- Source scope: AMESH Agent Mesh differentiator; not a Kestra-parity claim
