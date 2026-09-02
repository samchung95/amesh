# EPIC-835 — Reliable agent repair, accounting and provider-bounded sessions

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI application developer and agent-session operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Make structured-output repair progress invocation-safe, retain truthful usage and billing evidence for every model attempt, let clients explicitly select provider-bounded sessions without hidden AMESH ceilings, preserve message-bound continuation state across turns, and close terminal progress streams promptly after reconnect.

## In scope

- [x] Pi progress source identity includes the canonical model invocation identity, including the structured-output repair ordinal, so distinct repair attempts cannot reuse one source sequence with different content and PostgreSQL conflict detection remains strict.
- [x] Exact retry and restart semantics are explicit: an identical accepted progress frame is idempotent, a different frame under the same source identity remains a conflict, and a new provider or repair attempt receives a distinct invocation-scoped progress identity.
- [x] A real Pi plus PostgreSQL regression rejects one invalid structured result, accepts the repair, reaches session success and preserves unique chronological progress; exhausted repair retains the original sanitized structured-output diagnostic.
- [x] Every model response normalizes and durably stores safe prompt, completion, reasoning, cache, total-token and cost evidence before assistant-content or structured-output validation, including failed and rejected attempts where the provider supplied those values.
- [x] Timeout and cancellation paths leave each claimed external invocation terminal or explicitly in doubt, and public evidence distinguishes exact billed cost, a known lower bound and unresolved billing without converting unavailable data to zero.
- [x] Session repair and terminal evidence aggregate all known attempt usage and cost without double counting restart replay, and query/repository-recreation tests prove the evidence survives recovery.
- [x] A backwards-compatible explicit provider-bounded mode can disable AMESH token, cost, duration, turn, tool, loop, repair, context-projection and task/model/tool timeout ceilings while retaining provider physical limits, cancellation, usage and immutable policy provenance.
- [x] Existing bounded resources keep their current defaults and validation behavior, bounded and provider-bounded policy intersection is deterministic, no hidden 60-second model or 30-second tool timeout is injected in provider-bounded mode, and focused plus Docker-local verification passes.
- [x] Multi-turn sessions retain an ordered, encrypted continuation binding for every retained assistant message, remap those bindings through context projection or compaction, preserve backwards compatibility with the latest-only checkpoint, and never expose provider continuation bodies through public session state or clean transfer bundles.
- [x] A progress SSE reconnect after the final terminal cursor returns prompt EOF without a heartbeat, while already committed later-attempt events still replay before close and genuinely running idle sessions retain heartbeat behavior.

## Implementation completion evidence

- 2026-09-02 — EPIC-835 is complete. Pi progress identity is invocation- and repair-scoped without weakening PostgreSQL conflict detection; a real Pi/PostgreSQL repair regression reaches success with unique chronological progress. Durable attempt accounting preserves known usage, cost and billing certainty across invalid, rejected, failed, timed-out, cancelled and replayed responses. Explicit provider-bounded policies remove only selected AMESH ceilings while retaining physical limits and cancellation. Encrypted continuation bindings remain attached to exact retained assistant messages, and terminal progress reconnects close promptly while committed retries replay and active retries heartbeat. Focused regressions, independent Fable 5 review and the complete Docker-local gate passed with 1,009 backend tests, 122 frontend tests, two application and eight documentation Playwright journeys, eight Pi worker tests, all 27 Pi conformance cases, production-image probing and repository/four-SDK packaging.

## Explicit non-goals

- Persisting hidden chain-of-thought or raw provider payloads
- Weakening PostgreSQL progress identity conflicts or replay invariants
- Changing existing bounded defaults for resources that do not opt in
- Adding provider-specific workflow nodes or client-domain behavior
- Implementing subscription-backed OpenAI or GitHub Copilot engines in this epic

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-808
- EPIC-812
- EPIC-813
- EPIC-816
- EPIC-824
- EPIC-826
- EPIC-832
- EPIC-834

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Run the real Pi worker against PostgreSQL with a scripted invalid structured response followed by a valid repair and assert session success, unique invocation-scoped progress and durable chronological replay.
- Run exhausted-repair and exact-retry regressions proving sanitized diagnostics, duplicate idempotency and conflict rejection.
- Run model-task and PostgreSQL invocation tests for successful, empty, invalid JSON, schema-invalid, timed-out, cancelled and restart-reused responses with full safe usage/cost projections.
- Run session evidence tests that aggregate known attempt usage once and expose exact, lower-bound or unresolved billing state.
- Run domain, API/OpenAPI and executor tests for legacy bounded defaults, explicit provider-bounded policies, mixed intersections, long-running calls and clean cancellation.
- Run three-turn continuation tests that prove each retained assistant message carries its own provider continuation, context projection remaps exact message indexes, encrypted bindings survive restart, and clean transfer excludes continuation bodies.
- Run progress SSE reconnect tests for query and Last-Event-ID final cursors, committed later attempts, and active idle heartbeat behavior.
- Run Ruff, strict mypy, generated contracts and SDKs, strict documentation, canonical planning validation and the complete Docker-local aggregate.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] GitHub issues #10, #11, #12, #16 and #17 each have executable regressions mapped to the implemented behavior.
- [x] Structured-output repair succeeds through Pi and PostgreSQL without progress-key collisions or weakened journal conflict detection.
- [x] Failed, rejected, timed-out and cancelled model attempts retain all safely known usage and billing evidence with an explicit certainty state.
- [x] Provider-bounded mode removes only explicitly disabled AMESH ceilings and timeouts; existing bounded defaults remain byte-compatible at the public contract boundary.
- [x] Restart, replay, cancellation and repository-recreation verification passes without duplicate accounting or lost progress.
- [x] Three-turn and restart regressions prove provider continuation state remains bound to the correct retained assistant messages without entering public payloads or clean transfers.
- [x] Terminal progress reconnect closes promptly without suppressing committed retry-attempt events or active-session heartbeats.
- [x] Affected user, API, operations and architecture documentation matches the implementation.
- [x] Focused verification and the complete Docker-local gate pass with evidence recorded in docs/reviews/TESTLOG.md.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Weakening progress conflict detection would hide corruption, so uniqueness must be fixed at the producer identity boundary.
- Provider usage may be absent or incomplete after ambiguous outcomes, so certainty must remain explicit rather than inferred.
- Provider-bounded means no selected AMESH application ceiling; it cannot override provider context, output, quota or physical transport limits.
- Removing hidden call timeouts must not remove explicit cancellation, operator stop or invocation fencing.
- Continuation references must be remapped from the canonical history through context projection; treating a single latest continuation as session-wide state would corrupt multi-turn provider context.
- Stream termination must be based on the cursor-referenced attempt state, not merely an empty page, so a reconnect cannot hide a later committed retry attempt.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
