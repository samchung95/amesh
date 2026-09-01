# Agent session service API

Use this provider-neutral API to run one bounded agent session without authoring a workflow. The
surface is a facade over the existing execution, task-run, checkpoint and evidence authorities; it
does not create a second executor, queue or transcript store.

## Authentication and request identity

Every operation requires an AMESH bearer credential and `X-Amesh-Tenant`. The session product has a
separate `agent_session` authorization resource: `create` launches a session, `view` reads sessions
owned by the caller, `list` reads the permitted fleet, and `manage` accepts lifecycle controls.
Cross-tenant resources are not returned. Namespace scope still applies, and a fleet reader cannot
control a session unless it also has `manage`.

The built-in `session-client`, `session-operator` and `session-admin` roles map those capabilities to
application clients, operators and administrators. During the compatibility window, data-plane
routes accept equivalent legacy `execution` grants only when no session grant or compatible
credential scope exists. An explicit `agent_session` deny always wins and never falls back. New
integrations should issue session-scoped credentials.

The creating actor is an authenticated AMESH application or platform principal, not an arbitrary
client-supplied end-user identifier. The owner filter applies to this session facade. Existing
namespace execution `VIEW` and `MANAGE` grants remain privileged access to the same canonical records
through execution APIs during that transition; applications must keep those roles away from
untrusted end users or mediate end-user identity in their own client boundary.

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

### Require an ordered tool plan

Set `requiredToolPlan` when final output is valid only after specific pinned tools have succeeded.
AMESH expands the plan from the immutable request `input`, stores the expanded ledger in the session
checkpoint, checks the exact next tool name and arguments before approval or tool I/O, and rejects an
early final action through the configured repair policy.

```json
{
  "requiredToolPlan": {
    "schemaVersion": "amesh.agent-tool-plan/v1",
    "steps": [
      {
        "stepId": "lookup-candidates",
        "toolName": "research.lookup",
        "arguments": {"depth": "brief"},
        "argumentBindings": {"topic": "/topic"},
        "forEach": "/candidates",
        "itemArgumentBindings": {"candidate": "/symbol"},
        "maxOccurrences": 25
      }
    ],
    "maxOccurrences": 100
  }
}
```

`argumentBindings` are RFC 6901 pointers rooted at the full session input.
`itemArgumentBindings` are rooted at the current `forEach` item. Expansion preserves step and input
array order. Every named tool must exist in the pinned agent revision. Missing pointers, non-array
`forEach` values, overflow, changed or out-of-order calls, and plan drift fail closed. Sessions that
omit `requiredToolPlan` keep the ordinary model-directed tool behavior.

Public result and event evidence contains plan and occurrence digests, counts, identities, states and
attempt counts, but not bound arguments or prompts. Read `session.requiredToolPlan.complete` in the
terminal result, or the `requiredToolPlan` projection on `tool.result` and `output.accepted` events.

A model policy may point at an existing provider-side fine-tuned model identifier. AMESH does not
train model weights, upload training datasets or treat MCP as a fine-tuning mechanism.

## Read sessions and events

| Method and path | Purpose |
| --- | --- |
| `GET /api/v1/agent-sessions?limit=N` | List up to 100 recent sessions owned by the caller, plus sessions in namespaces the caller can manage. |
| `GET /api/v1/agent-sessions/{sessionId}` | Read one redacted summary and bounded event page. |
| `GET /api/v1/agent-sessions/{sessionId}/progress` | Read the safe cross-attempt timeline after an opaque `after` cursor. |
| `GET /api/v1/agent-sessions/{sessionId}/progress/stream` | Watch reconnectable NDJSON progress after `after` or `Last-Event-ID`. |
| `GET /api/v1/agent-sessions/{sessionId}/events` | Read events after `afterEventIndex`, up to `limit=100`. |
| `GET /api/v1/agent-sessions/{sessionId}/events/stream` | Read reconnectable NDJSON events and heartbeats after `afterEventIndex`. |
| `GET /api/v1/agent-sessions/{sessionId}/result` | Read the structured terminal result or safe error. |
| `GET /api/v1/agent-sessions/harnesses` | List registered public harness names and exact provenance. |

The progress page returns `{sessionId, events, nextCursor}`. Treat `nextCursor` as opaque and advance
it only after handling the page. Each stream line is either one `amesh.agent-progress-event/v1`
event or a `{type: "heartbeat", sessionId, cursor}` record. Reconnect with the last handled cursor in
`after` or `Last-Event-ID`. The server authorizes before writing response bytes, preserves accepted
journal order across retries and closes after the current attempt reaches its terminal tail. A
bounded non-terminal stream may close; reconnecting from its last cursor is normal.

If progress reports `TRUNCATED`, treat the trace as incomplete and continue reading session state
and result. The marker does not by itself mean that the model invocation or session failed.

The older event surface uses attempt-local `nextEventIndex`. It remains compatible, but it cannot
represent one logical timeline across retries. Both surfaces are redacted lifecycle projections,
not hidden reasoning or model-token transcripts.

The CLI exposes the same canonical progress contract:

```powershell
uv run amesh session progress SESSION_ID --limit 100
uv run amesh session watch SESSION_ID
uv run amesh session watch SESSION_ID --after OPAQUE_CURSOR
```

`GET /messages` returns the same safe journal projection. `POST /messages` accepts one durable
follow-up input after the current turn succeeds:

```json
{
  "input": {
    "prompt": "Now compare the second chart.",
    "image": {
      "artifact": {
        "reference": "namespace-file://agents.demo/images/second.png?v=2&sha256=...",
        "contentAddress": "sha256:..."
      }
    }
  }
}
```

Send a stable `Idempotency-Key` header (or the equivalent `idempotencyKey` body field). A retry with
the same key returns the same execution turn. The server keeps the public `sessionId`, creates an
ordered durable execution turn, resumes the exact successful checkpoint and immutable capability,
envelope and harness pins, then returns the ordinary launch response and structured result. Governed
image references require namespace read authorization and exact artifact/checksum resolution; a
model route without image-input support is rejected before provider I/O. Progress cursors remain
valid across these turns. Only the creating actor may append a follow-up message.

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
| `POST /v1/chat/completions` | `model`, ordered text/inline `image_url` message parts and `stream` |
| `POST /v1/responses` | `model`, ordered `input_text`/inline `input_image` parts, optional `instructions` and `stream` |

`model` is an authorized immutable AMESH agent reference such as
`agents.demo/incident-helper@1`; it is not a provider model identifier. The selected agent input
schema must accept the normalized `messages` object. Send the ordinary AMESH bearer credential and
`X-Amesh-Tenant` header, and use `Idempotency-Key` to make a retried compatibility request resolve to
the same canonical session.

Temperature, top-p, token ceilings, user identity and output schema remain owned by the pinned agent
definition. Supplying those request overrides fails explicitly. Structured output still works: the
agent's immutable output schema validates the result, which Chat Completions returns as JSON text and
Responses returns as `output_text`.

For image input, this compatibility subset accepts only a base64 `data:` URL in a user message.
Chat Completions uses `{"type":"image_url","image_url":{"url":"data:image/png;base64,..."}}`;
Responses uses `{"type":"input_image","image_url":"data:image/png;base64,..."}`. AMESH decodes,
validates and content-addresses the image in the caller's governed namespace before launch, then
persists only an immutable `image_ref`. Transient bytes and placeholders are cleared before the
canonical session request is written. Remote URLs, file IDs, unsupported media, corrupt images,
non-user image placement and over-limit inputs fail explicitly rather than being ignored.

`stream: true` emits documented SSE response shapes after the bounded canonical execution completes.
It is buffered compatibility output, not live provider-token delivery. Canonical reconnectable
progress remains available from `/api/v1/agent-sessions/{sessionId}/progress/stream`. Usage is derived
from durable session events. Errors under `/v1/*` use an OpenAI-style `error` envelope; the canonical
API continues to use AMESH problem details.

Each request is one durable bounded session. For another conversational turn, send the full desired
message history in a new request with a new idempotency key. AMESH does not implement proprietary
ChatGPT accounts, stored thread mutation, history synchronization, UI behavior or hidden protocols.

See [Start and inspect an agent session](../how-to/use-agent-session-service.md) for CLI commands and
[Operate the agent session service](../operations/agent-session-service.md) for deployment and
recovery guidance.
