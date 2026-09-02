# ADR-072: Make agent attempts accountable and limits explicitly selectable

Status: accepted

Context: one logical agent turn may make several model invocations because provider fallback and
structured-output repair are separate attempts. Pi previously derived progress identity from only
the session, turn and route, so a repair could restart the same source sequence with different
content. Model usage was normalized only into a successful task result, which also meant that an
invalid or empty response could lose already returned usage and a timed-out invocation could remain
`STARTED`. Separately, every agent envelope and context projection required finite AMESH limits, and
an omitted session timeout silently became a 60-second model or 30-second tool timeout. A client
therefore could not explicitly ask AMESH to retain orchestration authority while relying only on
the model provider's physical limits.

Decision: the canonical model `invocationKey` owns one Pi progress source. The key already includes
the route and structured-output repair ordinal. Exact replay of that invocation reproduces the same
source and sequence. `occurredAt` is producer metadata rather than event identity: the first
accepted journal timestamp remains authoritative, while activity, status, segment and safe detail
still participate in the progress fingerprint and conflicting semantic reuse remains an error.

Persist a typed, safe accounting checkpoint on every model invocation immediately after a provider
response and before assistant-content or structured-output validation. The checkpoint contains only
normalized prompt, completion, reasoning, cache and total-token counts plus normalized cost state;
it never stores provider payloads or hidden reasoning. It is first-write idempotent under the
invocation identity so restart replay cannot double count it. Invocation outcomes add `IN_DOUBT`
for cancellation or timeout after external work may have started. Aggregate evidence reports one of
three billing certainties: `EXACT` when every attempted invocation is terminal with known billing,
`LOWER_BOUND` when known amounts coexist with an in-doubt or unavailable amount, and `UNRESOLVED`
when no amount is known. Missing cost is never converted to zero.

Add the explicit `ceilingMode` values `BOUNDED` and `PROVIDER_BOUNDED` to agent hard limits, context
policy and session policy. Absence means `BOUNDED` and preserves all existing required values,
defaults, validation and digests. In `PROVIDER_BOUNDED`, application token, cost, duration, turn,
tool, loop, repair and context-projection ceilings may be null; a supplied finite value remains a
deliberate lower cap. Concurrency, recursion, retention, cancellation, fencing and authorization
remain finite operational controls. Intersections take the smallest non-null value, where null is
the identity; a provider-bounded envelope therefore cannot loosen a finite mesh or governing policy.
The effective values and exact policy revisions are server-authored immutable provenance.

Add an explicit task `timeoutMode`. Its default keeps legacy bounded handler behavior. `DISABLED`
requires `timeoutSeconds` to be absent and is propagated by an opted-in provider-bounded session to
its internal model and MCP calls, so no hidden 60/30-second timeout is injected. An explicit finite
timeout always wins. Provider-bounded context does not mean an infinite model request: before each
turn AMESH resolves the exact route's declared context-window and output-token limits, fails
preflight when either is unknown, and gives the harness a finite physical token budget. Optional
AMESH message, byte and estimated-token caps may lower that budget; disabled caps do not. Provider
usage, quota and transport errors remain authoritative at the external edge.

Consequences: structured repair no longer collides with its original progress stream, rejected
responses retain safe accounting, and ambiguous external calls remain visibly unsettled. Existing
bounded resources and workflows behave as before. Provider-bounded runs can be longer and more
expensive because AMESH will not stop them at disabled application ceilings; operators must use a
finite policy when they require one. Providers without declared physical context and output limits
cannot be selected for provider-bounded context. The schema gains nullable fields and explicit mode
tags, and the invocation table requires a backward-compatible nullable accounting migration.

Alternatives: weakening PostgreSQL progress conflicts would hide genuine corruption; using large
sentinel limits would create fake infinity and unstable policy comparisons; storing accounting only
in task results would repeat the current loss on validation failures; and treating timeout omission
as unbounded would silently change every existing workflow.
