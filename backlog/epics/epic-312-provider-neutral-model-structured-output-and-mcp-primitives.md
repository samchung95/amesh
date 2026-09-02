# EPIC-312 — Provider-neutral model, structured-output and MCP primitives

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide bounded provider-neutral model and MCP task primitives with structured results, explicit policy, complete provenance and no autonomous session state.

## In scope

- [x] **URS-F-0383** — The system shall provide provider-neutral chat, embedding, structured-output and tool-call tasks.
- [x] **URS-F-0384** — The system shall support model endpoint, credential, budget, timeout, retry and data-handling policy.
- [x] **URS-F-0385** — The system shall expose workflows and approved operations through an authenticated MCP server.
- [x] **URS-F-0386** — The system shall invoke external MCP tools through scoped allowlists and auditable tool calls.
- [x] **URS-F-0387** — The system shall store prompts, model parameters, usage, cost and response provenance subject to redaction policy.
- [x] **URS-F-0388** — The system shall validate structured outputs against JSON Schema before downstream use.
- [x] **URS-F-0389** — The system shall require approval or policy checks for high-impact tools and sensitive data movement.
- [x] **URS-F-0390** — The system shall support replay with pinned model and prompt metadata while acknowledging provider nondeterminism.

## Implementation completion evidence

- 2026-08-21 — W6 verified OpenAI-compatible `agent.llm` with OpenRouter `openai/gpt-5.6-luna` as the default live-test model and `agent.mcp` tool invocation through the official MCP v2 client. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`test_handlers.py`](../../tests/tasks/test_handlers.py), [`test_openrouter_smoke.py`](../../tests/llm/test_openrouter_smoke.py), and [`test_agent_shell_http.py`](../../tests/e2e/test_agent_shell_http.py). Provider breadth, agent loops and the broader plugin epic remain open.
- 2026-08-25 — EPIC-312 is complete. AMESH now exposes provider-neutral chat, embedding, structured-output and proposed tool-call tasks through an OpenAI-compatible adapter; enforces explicit endpoint, secret scope, token/cost budget, timeout, retry and data-egress policy; validates Draft 2020-12 structured results; journals redacted model/MCP provenance and ambiguous external outcomes; stores immutable tenant-scoped MCP connection revisions with schema pins and allowlists; gates writes and high-impact calls; and serves authorization-checked read-only workflow/execution MCP tools. The distributed Compose deployment is healthy at migration 56 and a live `openai/gpt-5.6-luna` structured flow completed with schema, usage and cost evidence. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`agent-primitives.md`](../../docs/api/agent-primitives.md), [`test_bounded_agent_tasks.py`](../../tests/tasks/test_bounded_agent_tasks.py), [`test_agent_connections_api.py`](../../tests/api/test_agent_connections_api.py), [`test_agent_primitive_repository.py`](../../tests/adapters/postgres/test_agent_primitive_repository.py), [`test_mcp_server.py`](../../tests/test_mcp_server.py), and [`test_openrouter_smoke.py`](../../tests/llm/test_openrouter_smoke.py).

## Explicit non-goals

- Owning long-running autonomous agent-session state or multi-agent routing
- Allowing a model or MCP server to mutate orchestration state directly

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-303
- EPIC-508

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
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

- Provider output remains nondeterministic even when model, prompt and parameters are pinned
- MCP tools can create external side effects that require explicit authorization and idempotency evidence

## Traceability

- Functional requirements: URS-F-0383, URS-F-0384, URS-F-0385, URS-F-0386, URS-F-0387, URS-F-0388, URS-F-0389, URS-F-0390
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
