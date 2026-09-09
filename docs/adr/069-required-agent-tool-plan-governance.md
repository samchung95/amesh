# ADR-069: Govern required agent tool plans in a provider-neutral domain core

Status: accepted

Context: GitHub issue #7 describes a governed research session that can return a schema-valid
final action while required calls remain unexecuted. Prompt instructions cannot make that
requirement a durable runtime invariant, and downstream client validation is too late to prevent
an incomplete execution from being accepted.

Decision: Add an optional `requiredToolPlan` to the canonical agent-session invocation and the
`agent.session` DSL. The versioned `amesh.agent-tool-plan/v1` value is immutable and contains
ordered, uniquely identified tool steps. A step may provide static arguments, bind argument
fields to RFC 6901 JSON Pointers in immutable session input, bind fields from the current
`forEach` item, and expand once over a bounded input collection. Expansion preserves declared
step order and collection order, rejects malformed or missing pointers and non-array sources,
and enforces both per-step and plan-level occurrence limits. The expanded plan records a
canonical SHA-256 plan/expanded digest and each occurrence records its canonical exact-call
digest. Admission also verifies that every expanded tool is present in the pinned capability
envelope before external work begins.

The session checkpoint carries an immutable completion ledger derived from the expanded plan.
At dispatch, AMESH applies ordinary capability bindings, then matches only the next unresolved
occurrence by tool name and canonical arguments before approval or tool I/O. Unknown, changed,
duplicated or out-of-order calls fail closed. Successful results advance the ledger monotonically
and idempotently using the existing invocation identity and optional result digest; failures
remain retryable for that occurrence. Plan and expanded digests are checked when a recoverable
session reloads, so a worker restart cannot lose accepted success or silently change the plan.

Final output is accepted only when the ledger is complete. An early final action enters the
existing invalid-output repair path and, when repair is unavailable or exhausted, fails closed
with a specific required-tool-plan reason. Sessions without `requiredToolPlan` retain their
current behavior. Public and durable evidence exposes only schema version, digests, counts,
occurrence identity, state and bounded attempt metadata; it excludes arguments, prompts,
secrets and hidden reasoning. Provider and harness adapters remain unaware of plan semantics.

Failure paths: malformed plans, invalid pointers, non-array expansion sources, duplicate step
IDs, expansion overflow, unpinned tools, mismatched calls, out-of-order calls, plan drift and
conflicting replays raise typed errors before completion is recorded. A failed attempt leaves
its occurrence unresolved, while an accepted success cannot be regressed to failed or pending.

## Unordered accepted-result extension (#93)

Decision (2026-09-09): extend this same plan/ledger with opt-in `mode: UNORDERED`.
Each uniquely named pinned tool has one requirement and a `successSchema` over its actual
MCP `structuredContent`. Use the installed Draft 2020-12 validator; a custom predicate language
or a second completion engine adds no needed capability. Schemas are self-contained (no
references), must reject an empty result, and never retrieve external resources. See the
[validator contract](https://python-jsonschema.readthedocs.io/en/stable/validate/).
Static/input-bound arguments constrain only their declared fields; remaining arguments may be
generated and corrected under the pinned input schema and normal host bindings. Collection
expansion remains the ordered mode's contract. Other permitted tools remain callable.

The session runner evaluates results at the existing tool-result boundary, persists accepted
invocation keys/result digests atomically with the TOOL_RESULT checkpoint, and supplies explicit
feedback when a result leaves a requirement unmet. The ledger is bound to the executing session
record, not an execution/workflow ID or a model-reported receipt. Recovery keeps that record's
evidence; a new session record, including a new canonical message dispatch, starts unmet.
Both structured completion and native research/finalization consume the same completion gate.
Existing repair, invocation, authorization, fencing and exhaustion policies remain authoritative.

Compatibility: omitted mode means ORDERED; old plan/expanded digests retain their exact encoding.
Public models and DSL reuse RequiredToolPlan, generated SDKs expose its fields, and evidence adds
only the unordered mode's session/invocation/result identities. No migration or new dependency.
