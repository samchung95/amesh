# EPIC-824 — Agent harness conformance and portability

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `quality`
- **Primary persona:** Platform engineer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Make the agent-session harness boundary continuously replaceable without weakening AMESH authority or behavior.

## In scope

- [x] A versioned harness conformance kit exercises structured final output, multi-turn tools, approval denial, budgets, timeouts, malformed actions, continuation, restart reuse, context compaction and provider-cache evidence.
- [x] Pi runs the complete kit in the local Docker verification gate and produces a machine-readable compatibility report tied to exact adapter and package versions.
- [x] Failure-injection fixtures prove a harness cannot change the authorized provider call, receive provider credentials, execute undeclared tools or commit workflow state.
- [x] Adapter registration is explicit and fail-closed, Pi remains the production default and there is no silent built-in fallback.
- [x] A documented adapter contract and template let a future DSH, Goose or other adapter be evaluated without changing agent.session public behavior.
- [x] Large responses and bounded control frames are qualified and dependency and license provenance is recorded.

## Implementation completion evidence

- 2026-08-26 — EPIC-824 is complete. Added a versioned 23-case harness-neutral conformance manifest, JSON Schema contracts and deterministic machine report; Pi 0.84.3 passes every case with zero failures or skips and report digest `sha256:b1b26b67b6b6793738f5f612320de8873beb719acb65ea62f22dced644e29022`. The Pi bridge uses a versioned bounded-frame handshake, accepts model output only through the one-shot AMESH gateway, strips provider credentials, rejects native tool/state frames, preserves large provider responses and maps timeouts explicitly. Session failure fixtures cover authorized-call mutation, fabricated or changed results, repeat gateway calls, malformed actions, undeclared tools, approval denial, token/cost/tool/turn budgets, continuation, restart reuse, bounded context and provider-cache evidence. The explicit Pi-only registry fails closed with no built-in fallback. The local Docker gate runs the kit twice, byte-compares reports, records exact Node/Python/worker/lock/package integrity and license provenance, and probes the production image. The rebuilt image passed its real Pi probe; Compose reported 66/66 migrations ready; live execution `01a03e4e-6ffc-74a8-b044-980bdc87dae9` completed `SUCCESS` with two Luna sessions through `pi-agent-core` 0.84.3 and persisted token, cost and prompt-cache evidence. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`agent-session-harness.md`](../../docs/plugin-sdk/agent-session-harness.md), [`ADR-061`](../../docs/adr/061-agent-harness-conformance-and-portability.md), and [`agent-harness-conformance-manifest-v1.json`](../../schemas/agent-harness-conformance-manifest-v1.json).

## Explicit non-goals

- Shipping DSH or Goose as an additional production harness in this epic
- Letting operators switch harnesses during an active session

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-816
- EPIC-819

## Architecture impact

- Primary bounded area: `quality`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Versioned conformance manifest and report-schema tests.
- Pi adapter behavior and failure-injection matrix.
- Credential, provider-call and tool-authority isolation tests.
- Local Docker deterministic-report and production-image probes.
- Live local Pi session smoke test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] Pi passes the complete versioned conformance kit with a machine-readable report.
- [x] A future adapter can implement one documented port and run the same kit without changing public session behavior.
- [x] The production composition fails closed when its explicitly configured harness cannot start or violates the protocol.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A conformance suite can validate only happy paths and miss authority bypasses.
- Harness-specific fixtures can make the nominally portable contract depend on Pi internals.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
