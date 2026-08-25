# EPIC-809 — Agent memory, evaluation and release gates

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH Agent Mesh differentiator; not a Kestra-parity claim

## Outcome

Make bounded agents safe to adopt through isolated memory, versioned evaluations, human-readable traces and evidence-backed promotion gates in the existing workflow experience.

## In scope

- [x] **URS-F-0812** — The system shall provide isolated private memory and policy-controlled shared memory with retention, redaction, size and tenant boundaries.
- [x] **URS-F-0816** — The system shall evaluate agent and mesh outcomes against versioned tests, rubrics, judges and business assertions.
- [x] **URS-F-0819** — The system shall interleave agent sessions, ordinary tasks and human approval tasks in one state machine, timeline and audit trail.

## Implementation completion evidence

- 2026-08-25 — EPIC-809 is complete. Migration 0059 adds a tenant-RLS memory journal with exact execution, private agent-revision and named shared scopes; bounded size and retention; redaction; idempotent provenance; metadata-only discovery; and namespace-scoped soft deletion with audit evidence. Exact immutable evaluation revisions run deterministic JSON-schema assertions and weighted rubrics before an optional judge pinned to ordered model-policy routes. Judge evidence records model, route, usage, cost, score, uncertainty, rationale and nondeterminism, while deterministic failure remains authoritative and high-impact release still requires a direct ordinary `core.approval` predecessor. Side-effect-free definition and fixture previews disclose that model behavior is unknown. Agent checkpoints and the ordinary execution trace interleave memory, evaluation, approval and output events. The deployed OpenRouter Luna cold and recall executions `01a03728-0034-7730-82f9-fce320a344fc` and `01a03728-fc13-70cc-b592-df2fabca6c88` both passed exact evaluation revision 1; the latter proved private-memory recall and replacement. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`agent-primitives.md`](../../docs/api/agent-primitives.md), [`configure-agent-memory-evaluations.md`](../../docs/how-to/configure-agent-memory-evaluations.md), [`054-agent-memory-evaluation-and-release-evidence.md`](../../docs/adr/054-agent-memory-evaluation-and-release-evidence.md), [`test_agent_memory_repository.py`](../../tests/adapters/postgres/test_agent_memory_repository.py), [`test_agent_sessions.py`](../../tests/tasks/test_agent_sessions.py), and [`executionTraceModel.test.ts`](../../frontend/src/components/executionTraceModel.test.ts). Shared mesh-wide NFRs remain In Progress until EPIC-806 qualifies multi-agent routing, hand-offs and provider substitution.

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

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Shared memory can disclose information across executions, namespaces or tenants
- LLM judges can be nondeterministic, biased or correlated with the model under test
- A passing format or rubric score can be mistaken for business correctness

## Traceability

- Functional requirements: URS-F-0812, URS-F-0816, URS-F-0819
- Non-functional requirements: URS-NFR-AGENT-002, URS-NFR-AGENT-003, URS-NFR-AGENT-004
- Source scope: AMESH Agent Mesh differentiator; not a Kestra-parity claim
