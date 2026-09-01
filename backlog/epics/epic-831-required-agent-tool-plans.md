# EPIC-831 — Required agent tool-plan governance

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI application developer requiring complete governed research runs
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let an agent/session invocation pin a required ordered tool-call plan, expand bounded runtime candidates deterministically, and gate final acceptance until every exact required occurrence succeeds in a restart-safe ledger.

## In scope

- [x] The canonical agent-session API and agent.session DSL accept an optional requiredToolPlan using the versioned amesh.agent-tool-plan/v1 contract, while invocations without a plan preserve existing behavior.
- [x] A plan contains ordered, uniquely identified steps with static arguments, RFC 6901 argumentBindings, itemArgumentBindings, optional forEach expansion, per-step limits and a plan-level occurrence limit; malformed pointers, duplicate step IDs and invalid bounds fail closed.
- [x] Admission expands the plan from immutable session input in declared-step and collection order, applies deterministic bindings, emits stable occurrence identities and canonical SHA-256 plan, expanded-plan and exact-call digests, and rejects missing/non-array sources, overflow and unpinned tools before external work.
- [x] The expanded plan and completion ledger are persisted in the session checkpoint and safe session/evidence projections with the existing durable execution and invocation identity.
- [x] Tool dispatch applies ordinary capability bindings and then matches only the next unresolved occurrence by exact tool name and canonical arguments before approval or tool I/O; unknown, altered, duplicate or out-of-order calls cannot create a side effect.
- [x] Ledger success is monotonic and idempotent, records attempt and optional result digests, leaves failed occurrences retryable, and validates plan/expanded identity on checkpoint reload so restart recovery cannot lose success or accept plan drift.
- [x] Final output is accepted only when the ledger is complete; an early final action is rejected through the existing repair path and fails closed with a specific required-tool-plan reason when repair is unavailable or exhausted.
- [x] Public and durable evidence exposes only schema version, digests, counts, occurrence identity, state and bounded attempt metadata; arguments, prompts, secrets and hidden reasoning are excluded.
- [x] Focused domain, API/DSL and session tests cover deterministic expansion and bindings, bounds and digest stability, duplicate and exact ordering, failed-call retry, restart replay, early-final repair, changed arguments before side effects, complete execution and no-plan compatibility; the ADR and canonical API/DSL documentation describe the contract and limits.

## Implementation completion evidence

- 2026-08-31 — EPIC complete: the canonical session API and agent.session DSL accept the versioned provider-neutral requiredToolPlan contract. Admission performs bounded deterministic RFC 6901 expansion against immutable input and rejects malformed, overflowing or unpinned plans before external work. The durable checkpoint ledger enforces the exact next tool and canonical arguments before approval or tool I/O, survives pending-tool restart replay, and gates early final output through bounded repair. Safe events and results expose only digests, identities, counts, states and attempts. OpenAPI plus Python, TypeScript, Java and Go SDKs are current. Focused provider-free regression passed 158 tests with two expected environment skips; Ruff, formatting, strict mypy, contract/backlog and strict documentation checks passed. The complete Docker-local gate passed 892 backend tests, 120 frontend tests, two application and eight documentation Playwright journeys, all 25 Pi conformance cases, production-image probing and repository/four-SDK packaging. The opt-in openai/gpt-5.6-luna Pi qualification also passed with governed PNG pixels, structured output, chronological safe progress, normalized usage/cost/cache evidence and terminal-result restart reuse.

## Explicit non-goals

- Provider-specific planning, prompt wording or harness-specific plan semantics
- Client-side post-validation or client-domain research/business logic
- Changing existing tool authorization, approval, invocation or external side-effect contracts
- Allowing models or tools to mutate the admitted plan or its bound values

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-807
- EPIC-812
- EPIC-814
- EPIC-819
- EPIC-825
- EPIC-826

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Run `tests/domain/test_agent_tool_plan.py` for RFC 6901 expansion/bindings, bounds, deterministic identities and digests, exact matching, duplicate calls, failed retry and serialized ledger reload.
- Run the focused agent-session tests in `tests/tasks/test_agent_sessions.py` for API admission, exact dispatch gating, early-final repair/failure, changed arguments before tool I/O, complete execution, crash replay and no-plan compatibility.
- Run API and DSL contract validation for `requiredToolPlan` in `src/amesh/api/models.py` and `src/amesh/dsl/registry.py`, including pinned-tool and malformed-plan rejection.
- Inspect session evidence projections for redaction of arguments, prompts, secrets and hidden reasoning while retaining bounded plan state and digest metadata.
- Run Ruff, strict mypy, generated-contract drift and `python scripts/validate_backlog.py` after canonical planning regeneration.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] `requiredToolPlan` is accepted at the canonical API and DSL boundary as a versioned provider-neutral contract, and legacy sessions without it remain behaviorally unchanged.
- [x] Expansion and binding are deterministic, bounded and immutable; every occurrence has stable identity and canonical plan/expanded/call digests.
- [x] The exact next-occurrence gate runs before approval or external tool I/O and rejects unknown, changed, duplicate and out-of-order calls fail closed.
- [x] The restart-safe ledger preserves accepted successes, makes failures retryable, is idempotent for replays and rejects altered recoverable plans.
- [x] Early final output cannot succeed while required occurrences are unresolved; repair and terminal failure expose a specific safe reason.
- [x] Safe evidence proves plan state and completion without exposing protected arguments, prompts, secrets or hidden reasoning.
- [x] Focused domain, API/DSL and session integration tests pass for partial expansion, duplicate calls, failed calls, complete execution, repair, restart replay and side-effect ordering.
- [x] ADR-069 and canonical API/DSL documentation accurately describe the integrated contract, boundaries and explicit non-claims.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- If runtime input, capability pins or expansion limits are not immutable, a retry could execute a different required call than the one originally admitted.
- A dispatch check after tool I/O would allow an unplanned or altered call to create a side effect; exact matching must remain before approval and invocation.
- Prompt or argument fields in plan evidence could expose protected application data, so projections must remain digest- and count-based.
- Repair loops can consume session budgets without satisfying the plan; existing repair ceilings and a specific terminal failure must remain authoritative.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
