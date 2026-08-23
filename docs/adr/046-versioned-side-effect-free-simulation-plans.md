# ADR-046: Versioned side-effect-free simulation plans

- Status: Accepted
- Date: 2026-08-23
- Scope: EPIC-800

## Decision

AMESH compiles simulation plans from the same canonical flow graph, bounded expression engine and
retry/condition semantics used by flow tests and the production reducer. A plan is pinned to the
flow semantic hash, resolved plugin-set hash, sample-input hash, `amesh.simulator/v1` and
`amesh.reducer/v1`. Conformance tests compare simulator graph readiness with the real reducer.

Simulation never dispatches a runner, reads a secret, writes an artifact or creates an execution.
Runnable external tasks require a declared mock, recorded fixture or schema-only placeholder.
Missing outputs, dynamic iteration counts and estimate models are reported as typed unknowns; the
simulator does not invent successful external results.

Task count, critical path, runner demand, storage, API calls and cost are estimates only where a
model exists. Revision comparison includes task, plugin-set, estimate and unknown changes. Server
plans carry domain-separated HMAC-SHA256 evidence over their complete canonical payload so a
promotion gate can reject unsigned, stale or modified evidence.

## Consequences

- Workflow authors can preview a stored revision from the flow UI, public API or CLI without
  producing runtime side effects.
- A plan with unknowns remains useful evidence but is not represented as complete or exact.
- Simulator, reducer and expression versions are explicit compatibility boundaries; changing their
  semantics requires a new version and updated conformance evidence.
- Cost and capacity numbers are model outputs, not billing or scheduling guarantees.
