# EPIC-825 — Generic deterministic agent tool argument bindings

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let an orchestrator deterministically bind selected agent-tool arguments from immutable session input while the model continues to choose the tool and all unbound arguments.

## In scope

- [x] A versioned provider-neutral binding contract maps declared tool arguments to absolute JSON Pointer sources rooted at immutable node session input.
- [x] Resolved values override model proposals before invocation while unbound arguments retain ordinary schema, authorization and provider mediation behavior.
- [x] Missing or invalid source pointers fail closed before the tool call with typed redacted evidence.
- [x] Binding declarations propagate through resolved capability pins for MCP and non-MCP tools and remain deterministic across retries.
- [x] Policy evidence identifies binding declarations and resolution outcomes without exposing protected values.
- [x] At least two provider-neutral fixtures prove model override and fail-closed missing-input behavior.
- [x] A live frozen-input workflow proves client-owned domain semantics can use the generic contract without entering AMESH core.

## Implementation completion evidence

- 2026-08-27 — EPIC-825 is complete. Added provider-, harness- and use-case-neutral `argumentBindings` to agent tool references and resolved capability pins. Absolute RFC 6901 JSON Pointers resolve from immutable session input, override model-proposed values before invocation, propagate through MCP and non-MCP tools, fail closed before side effects when a source is missing, and appear in policy evidence. Focused domain and session tests passed. Live qualification used VibeStonks flow revision 9 and execution `01a03f8c-0042-7dfe-9520-c418632ce1e3`: all 12 Luna agent sessions succeeded after checkpoint replay, every cutoff-capable tool received the frozen `2026-08-26T19:08:40Z` value, and the client accepted one idempotent `DO_NOTHING` decision artifact with zero broker commands. Evidence: [`agent-primitives.md`](../../docs/api/agent-primitives.md), [`test_agent_resources.py`](../../tests/domain/test_agent_resources.py), and [`test_agent_sessions.py`](../../tests/tasks/test_agent_sessions.py).

## Explicit non-goals

- Adding provider-specific or client-domain binding types
- Allowing models or tools to mutate orchestrator-bound values
- Reading bound values from ambient mutable state

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-807
- EPIC-812
- EPIC-814
- EPIC-819

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Agent-resource contract, JSON Pointer and capability-pin tests.
- Session tests for immutable override and missing-source fail-closed behavior.
- MCP and non-MCP propagation tests.
- Retry and checkpoint-replay qualification.
- Live client-neutral frozen-input workflow with evidence inspection.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] The generic binding contract is implemented and documented at agent-resource and session boundaries.
- [x] Selected arguments are immutably overlaid before tool execution while unbound arguments continue through normal validation.
- [x] Invalid bindings fail before external side effects and produce redacted trace evidence.
- [x] Provider-neutral focused tests and one live client qualification pass.
- [x] No client-domain integration or business rule is embedded in AMESH core.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Ambiguous source semantics can create authority gaps if pointers are not pinned and validated.
- Trace metadata can expose protected structure if binding evidence is not redacted.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
