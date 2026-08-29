# ADR-066: Productize the existing agent session and translate compatibility at the edge

Status: accepted

Context: EPIC-826 needs a client-neutral, horizontally scalable session product that can be used by
ordinary application clients and by clients expecting common OpenAI request and stream shapes.
AMESH already owns authenticated execution admission, immutable agent capability pins, the durable
session journal, Pi behind a typed harness port, model and MCP gateways, budgets, recovery and
evidence. Introducing another proxy, executor or transcript authority would duplicate those controls
and make retry and side-effect ownership ambiguous.

Decision: expose one canonical AMESH session API as a thin facade over the existing execution and
`agent.session` authorities. Every admitted bounded request receives a stable operation identity and
advances through the ordinary PostgreSQL command, execution, task, checkpoint, invocation and event
paths. Execution trigger metadata indexes the stable public session identity, but it cannot execute
model or tool work or replace the canonical agent transcript and evidence journal.

Keep client compatibility at the transport edge. A narrow AMESH-owned adapter accepts the documented
Chat Completions and Responses subset, translates it to the canonical session application service,
and emits documented response, usage, error and SSE shapes. Unsupported fields fail explicitly.
Compatibility does not extend to proprietary ChatGPT accounts, history synchronization or hidden
protocols.

Keep the public API harness-neutral. Pi remains the exact production default, selected through the
existing registry and conformance-tested port. Public profiles and evidence identify a harness by
adapter, version and protocol rather than by Pi-specific configuration. A future registered adapter
can serve new sessions after passing the same conformance kit; an active session keeps its resolved
harness pin and cannot be hot-swapped.

Build the compatibility translation with the repository's pinned FastAPI and Pydantic stack. Do not
add LiteLLM: its proxy repeats provider routing, authentication, budgets, fallbacks, cost tracking and
operational state that AMESH already owns. Do not add `fastapi-openai-compat` yet: it is a useful
router factory but has a small adoption base, deliberately passes inner message objects as loose
dictionaries, and would still require AMESH-specific fail-closed capability and session mapping.
The official OpenAI Python package is a client rather than a server framework and is suitable as an
optional compatibility test client, not a runtime authority.

Alternatives: running LiteLLM as the public gateway would create two policy and accounting planes;
using a generic OpenAI router would reduce response boilerplate but not the domain translation; and
exposing only workflow execution APIs would force every session client to understand AMESH flow
construction and prevent the requested product boundary.

Consequences: the new surface inherits AMESH tenant isolation, quotas, durable recovery, evidence and
harness portability. One request maps to one bounded durable session; clients provide full history in
a later request instead of mutating a stored ChatGPT-style thread. Compatibility SSE is buffered from
the terminal canonical result rather than exposing live provider tokens. The compatibility claim is
intentionally narrower than the full and evolving OpenAI API, so supported fields and deviations
require contract fixtures and versioned documentation. Revisit the router-library choice if AMESH
commits to files, audio, images, batches or another broad provider compatibility surface whose schema
maintenance exceeds the narrow session adapter.

References:

- OpenAI Chat Completions API: https://developers.openai.com/api/reference/resources/chat/subresources/completions
- Official OpenAI Python client: https://github.com/openai/openai-python
- FastAPI OpenAI compatibility router considered: https://github.com/deepset-ai/fastapi-openai-compat
- LiteLLM proxy considered: https://docs.litellm.ai/
