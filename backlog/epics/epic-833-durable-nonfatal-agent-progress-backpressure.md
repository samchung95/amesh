# EPIC-833 — Durable nonfatal agent-progress backpressure

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `observability`
- **Primary persona:** AI application developer and agent-session operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Keep chronological agent progress bounded and durable without allowing telemetry overflow to fail an otherwise valid model invocation, agent session or workflow execution, while preserving a clear server-versus-client responsibility boundary.

## In scope

- [x] Progress validation, redaction, ordering, idempotency and hard storage/rate ceilings remain authoritative AMESH responsibilities; connected clients may filter, collapse or sample their own presentation but cannot disable server safety limits.
- [x] When a progress hard limit is first exceeded, the PostgreSQL sink persists exactly one deterministic TRUNCATED telemetry marker for the attempt and returns a receipt with truncated=true without failing the model invocation or agent session.
- [x] After a durable TRUNCATED marker exists, later novel progress frames are safe no-ops that return the same marker identity with truncated=true and duplicate=false; they neither append more telemetry nor raise a terminal-stream error into the producer.
- [x] Regular persisted frames return duplicate=false and truncated=false, while exact idempotent retries return duplicate=true; the existing conflict rejection for reused source identities with different payloads remains unchanged before terminal-state handling.
- [x] The append-only progress reducer remains strict and terminal after TRUNCATED; nonfatal producer behavior is implemented at the durable sink boundary rather than weakening domain replay invariants or adding provider-specific handling.
- [x] A session can persist its schema-valid final result, terminal state, token usage, cost and tool evidence after its progress journal truncates, and callers can retrieve that final evidence independently of telemetry completeness.
- [x] Focused PostgreSQL tests cover first overflow, later frames, exact retry/conflict behavior, repository recreation, one-marker durability and successful final session evidence after overflow.
- [x] Architecture and user reference documentation explain the nonfatal truncation contract and AMESH-versus-client ownership; focused checks and the complete Docker-local quality gate pass.

## Implementation completion evidence

- 2026-09-01 — EPIC-833 is complete. The PostgreSQL progress sink now returns additive duplicate/truncated receipt evidence, commits one deterministic TRUNCATED marker at the first hard-limit overflow and treats later or concurrent novel frames as restart-safe truncated no-ops while retaining strict reducer replay and conflicting-key rejection. A Docker/PostgreSQL regression proves one-marker durability across repository recreation and successful final result, 321-token, USD 0.045 and one-tool-call evidence after overflow. Focused tests, Ruff, strict mypy, strict documentation, planning validation and the complete Docker-local gate passed with 907 backend tests, 122 frontend tests, two application and eight documentation Playwright journeys, all 27 Pi conformance cases, production-image probing and repository/four-SDK packaging.

## Explicit non-goals

- Removing AMESH hard progress bounds or delegating storage protection to connected clients
- Changing the default progress limits or provider streaming cadence
- Adding provider-, model- or client-specific progress behavior
- Changing client UI rendering controls or retaining hidden reasoning content
- Refactoring unrelated session, workflow or observability paths

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-808
- EPIC-812
- EPIC-816
- EPIC-826
- EPIC-828

## Architecture impact

- Primary bounded area: `observability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Add a PostgreSQL integration regression that reproduces issue #14 by exceeding the same-window progress rate and then appending another novel frame.
- Assert one durable TRUNCATED marker, truthful duplicate/truncated receipt flags, unchanged conflicting-reuse rejection and safe behavior through a recreated repository.
- Complete the affected session after overflow and verify its final result, terminal state, token usage, cost and tool evidence remain durable.
- Run focused domain, port, PostgreSQL repository, task and harness tests plus Ruff and strict mypy for the affected modules.
- Run planning/documentation drift validation and the complete Docker-local quality gate.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] GitHub issue #14 has an executable regression and no progress overflow exception can fail the affected model/session path.
- [x] The PostgreSQL journal contains no more than one deterministic truncation marker per attempt and remains bounded across later frames, retries and repository recreation.
- [x] Receipts distinguish persisted, exact-duplicate and truncated/no-op outcomes without misreporting a novel dropped frame as an exact duplicate.
- [x] Session final result and accounting evidence remain durable after telemetry truncation.
- [x] The server/client responsibility boundary is documented and provider-neutral.
- [x] Focused verification and the complete Docker-local gate pass with evidence recorded in TESTLOG.md.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Returning a generic duplicate receipt for a novel dropped frame would hide data loss from internal callers, so the receipt must expose truncation explicitly.
- Weakening the pure reducer could make corrupt post-terminal journals replayable, so terminal-state tolerance belongs only at the sink boundary.
- An in-memory truncation flag would be lost on restart, so the persisted marker and locked session row must remain authoritative.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
