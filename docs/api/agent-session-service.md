# Agent session service API

Use this provider-neutral API to run one bounded agent session without authoring a workflow. The
surface is a facade over the existing execution, task-run, checkpoint and evidence authorities; it
does not create a second executor, queue or transcript store.

## Authentication and request identity

Every operation requires an AMESH bearer credential and `X-Amesh-Tenant`. Creation requires ordinary
execution permission for the selected namespace. Session reads require namespace view permission and
are limited to the creating principal unless the caller also has namespace execution-management
permission. Control actions retain the ordinary execution-management check. Cross-tenant resources
are not returned; deliberately privileged namespace operators can inspect sessions they do not own.

The creating actor is an authenticated AMESH application or platform principal, not an arbitrary
client-supplied end-user identifier. The owner filter applies to this session facade. Existing
namespace execution `VIEW` and `MANAGE` grants remain privileged access to the same canonical records
through execution APIs; applications must keep those roles away from untrusted end users or mediate
end-user identity in their own client boundary.

For creation, send a stable `Idempotency-Key`. Repeating the same actor, tenant, namespace and key
resolves to the same logical session; the same key used by another actor does not alias it.
`X-Correlation-ID` is optional and is returned when supplied. Send
`Prefer: respond-async` to receive `202 Accepted`, `Preference-Applied: respond-async` and a
`Location` to poll when work remains active.

## Create a session

`POST /api/v1/agent-sessions` accepts a harness-neutral agent reference. The clearest form names the
three immutable parts explicitly:

```json
{
  "namespace": "agents.demo",
  "agent": "incident-helper",
  "agentRevision": 1,
  "input": {
    "incident": "API latency exceeded the objective for eight minutes."
  },
  "invalidOutputPolicy": "FAIL",
  "maxRepairAttempts": 0,
  "dataHandling": "DENY_SECRETS",
  "memoryReadKeys": [],
  "runner": "local"
}
```

`agentRef: "agents.demo/incident-helper@1"` is the equivalent compact representation. If both forms
are present, they must agree. The request may also set `approvalTask`, `businessAssertions`,
`memoryWriteKey`, `timeoutSeconds` and `retry`. Limits, prompts, skills, MCP tools, schemas and model
routes come from the exact agent revision; request input cannot replace those pins.

The response contains `sessionId`, `executionId`, `taskRunId`, `attempt`, `executionState` and the
session summary when it has already started. `Location` identifies the stable public session.

A model policy may point at an existing provider-side fine-tuned model identifier. AMESH does not
train model weights, upload training datasets or treat MCP as a fine-tuning mechanism.

## Read sessions and events

| Method and path | Purpose |
| --- | --- |
| `GET /api/v1/agent-sessions?limit=N` | List up to 100 recent sessions owned by the caller, plus sessions in namespaces the caller can manage. |
| `GET /api/v1/agent-sessions/{sessionId}` | Read one redacted summary and bounded event page. |
| `GET /api/v1/agent-sessions/{sessionId}/events` | Read events after `afterEventIndex`, up to `limit=100`. |
| `GET /api/v1/agent-sessions/{sessionId}/events/stream` | Read reconnectable NDJSON events and heartbeats after `afterEventIndex`. |
| `GET /api/v1/agent-sessions/{sessionId}/result` | Read the structured terminal result or safe error. |
| `GET /api/v1/agent-sessions/harnesses` | List registered public harness names and exact provenance. |

`nextEventIndex` is the next durable cursor. Advance it only after handling the returned page. The
stream uses `application/x-ndjson`; reconnect with the last handled index. It is a redacted event
projection, not a model-token stream.

`GET /messages` currently returns the same safe journal projection. `POST /messages` returns `409`:
arbitrary follow-up turns on a completed session are not part of the current contract. Create a new
session with a new idempotency key for a new bounded request.

## Control a session

Use `POST /api/v1/agent-sessions/{sessionId}/{action}` where `action` is `cancel`, `pause`, `retry` or
`resume`:

```json
{
  "reason": "Hold for operator review.",
  "graceSeconds": 30
}
```

The server resolves the current execution fence when `expectedVersion` and `expectedEpoch` are
omitted. Automation that already read the underlying execution may include either value to reject a
stale control request. A conflict means no control was accepted; read the current session and
execution before deciding whether to retry.

## Harness and privacy boundary

Pi is the current production default, registered as `pi` with exact adapter version and worker
protocol provenance. The public create contract does not require a Pi field. A future harness can
serve new sessions only after it is registered behind the same typed port and passes the conformance
suite. An active session retains its resolved harness pin and cannot be hot-swapped.

The harness receives no model-provider or MCP credential. AMESH remains responsible for model and
tool authorization, approvals, budgets, invocation identity, checkpoints and evidence. Public
responses omit credentials, private checkpoints, provider continuations, prompts and hidden
reasoning. AMESH validates structured results but does not claim deterministic model output.

## OpenAI compatibility boundary

AMESH exposes two authenticated compatibility routes over the same canonical launch path:

| Method and path | Supported request subset |
| --- | --- |
| `POST /v1/chat/completions` | `model`, text `messages` and `stream` |
| `POST /v1/responses` | `model`, text `input`, optional `instructions` and `stream` |

`model` is an authorized immutable AMESH agent reference such as
`agents.demo/incident-helper@1`; it is not a provider model identifier. The selected agent input
schema must accept the normalized `messages` object. Send the ordinary AMESH bearer credential and
`X-Amesh-Tenant` header, and use `Idempotency-Key` to make a retried compatibility request resolve to
the same canonical session.

Temperature, top-p, token ceilings, user identity and output schema remain owned by the pinned agent
definition. Supplying those request overrides fails explicitly. Structured output still works: the
agent's immutable output schema validates the result, which Chat Completions returns as JSON text and
Responses returns as `output_text`. Unknown fields and unsupported media, tool-call, file and image
content also fail rather than being ignored.

`stream: true` emits documented SSE response shapes after the bounded canonical execution completes.
It is buffered compatibility output, not live provider-token delivery. Canonical reconnectable
progress remains available from `/api/v1/agent-sessions/{sessionId}/events/stream`. Usage is derived
from durable session events. Errors under `/v1/*` use an OpenAI-style `error` envelope; the canonical
API continues to use AMESH problem details.

Each request is one durable bounded session. For another conversational turn, send the full desired
message history in a new request with a new idempotency key. AMESH does not implement proprietary
ChatGPT accounts, stored thread mutation, history synchronization, UI behavior or hidden protocols.

See [Start and inspect an agent session](../how-to/use-agent-session-service.md) for CLI commands and
[Operate the agent session service](../operations/agent-session-service.md) for deployment and
recovery guidance.
