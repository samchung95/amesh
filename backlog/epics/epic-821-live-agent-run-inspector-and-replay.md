# EPIC-821 — Live agent run inspector and replay

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let a user understand and safely control an agent run from trigger through structured result.

## In scope

- [x] One agent-focused projection presents current state and turn, model attempts, tool proposals and results, approvals, retries, context usage, token, cost and cache budgets, schema decisions and the final result or failure.
- [x] The projection uses only canonical redacted execution, session and evidence records and preserves stable pagination and realtime refresh across API restart.
- [x] The UI presents a simple chronological trace with drill-down to exact evidence and clear running, waiting, failed, cancelled and successful states.
- [x] Existing authorized pause, cancel, resume, retry and replay operations are exposed contextually without creating a second control path or duplicating accepted effects.
- [x] Replay or fork requires explicit frozen inputs and exact resource pins and links the new execution to its source.
- [x] Responsive Playwright journeys and focused permission, redaction, malformed evidence, large evidence and restart tests pass.

## Implementation completion evidence

- 2026-08-26 — EPIC-821 is complete. Execution detail now projects authorized agent-session summaries and a canonical, redacted, event-index-paginated session detail into one responsive inspector showing state, turn, model, tool, approval, repair, context, token/cost/cache, schema and terminal facts without checkpoints, prompts or hidden reasoning. Existing execution controls remain canonical, while replay now requires frozen source inputs, their SHA-256 digest, exact flow/plugin/envelope/policy pins and an explicit idempotency key; duplicate submissions converge and intentional new keys remain distinct. Focused Python/API/PostgreSQL and frontend unit tests, strict mypy, Ruff, build, responsive Playwright journeys, axe checks and screenshots passed. Deployed execution 01a03de7-fdcd-791f-992c-721e38eb0313 persisted and exposed a deliberate three-turn Luna repair/failure trace with 11 canonical events and no private checkpoint or reasoning fields; API readiness remained full at migration 66. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`agent-primitives.md`](../../docs/api/agent-primitives.md), [`AgentRunInspector.tsx`](../../frontend/src/components/AgentRunInspector.tsx), and [`shell.spec.ts`](../../frontend/e2e/shell.spec.ts).

## Explicit non-goals

- Displaying hidden chain-of-thought
- Adding a second execution-control or replay engine

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-106
- EPIC-407
- EPIC-812
- EPIC-819

## Architecture impact

- Primary bounded area: `ui`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Agent-run projection and redaction contract tests.
- Realtime reconnect, pagination and API-restart integration tests.
- Control and replay idempotency tests with exact source linkage.
- Responsive Playwright inspect, control and replay journeys.
- Live local multi-turn agent inspection smoke test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] A user can identify what an agent is doing, why it is waiting or failed and what result it produced from one screen.
- [x] Every displayed fact and control maps to canonical authorized execution evidence and commands.
- [x] Replay uses frozen inputs and exact pins without duplicating an accepted logical effect.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A UI-derived state can disagree with canonical execution evidence.
- Replay can silently change nondeterministic inputs or duplicate external effects if pins and effect policy are not explicit.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
