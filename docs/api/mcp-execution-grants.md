# Execution-scoped MCP grants

Use this opt-in contract when independently authorized logical sessions share one MCP connection.
AMESH supplies authenticated execution context; your gateway owns grant issuance, consumer binding,
revocation and external side-effect receipts. See [ADR-077](../adr/077-execution-scoped-mcp-grant-exchange.md).

## Register a connection and a consumer grant

1. Create the usual namespace secret for the gateway's AMESH connection credential. This credential
   authenticates AMESH for discovery and grant exchange; it must not authorize scoped tool calls by
   itself. Never use an AMESH API token as this credential.
2. Discover tools and register an immutable MCP connection revision through
   `POST /api/v1/namespaces/{namespace}/agent/mcp-connections`. In addition to its existing endpoint,
   credential reference and exact tool pins, set
   `"executionGrant": {"exchangeEndpoint": "https://gateway.example/exchange"}`.
   The exchange and MCP endpoint must have the same scheme, host and port. Use HTTPS in production;
   local HTTP requires an explicitly trusted local network/egress policy.
3. Pin that connection revision in the agent. In your gateway, issue an opaque grant identifier such
   as `grant-a` for the approved consumer binding. Grant IDs use 1–128 letters, digits, underscores or
   hyphens, beginning with a letter or digit. An ID is not a credential. The gateway must require the
   trusted AMESH connection credential, permitted tenant/namespace/actor, exact audience and tool
   scope, an unexpired grant and current consumer approval. Bind the grant to one AMESH logical
   session, either during registration or atomically on the first valid exchange; never silently
   transfer an already bound grant to a different session.
4. Create the canonical session with its exact `agentRef`, ordinary `input`, stable idempotency key,
   and `"toolGrants": {"gateway": "grant-a"}`. The map has at most 64 entries and its keys must be
   connection keys pinned by the agent. It is separate from model-visible input. Existing requests
   and MCP connections can omit the feature.

## Exchange and invoke

For a governed tool call, AMESH POSTs JSON to the pinned exchange endpoint with the configured
connection bearer. The body has `schemaVersion: "amesh.mcp-execution-grant/v1"` and these fields:

| Field | Meaning |
|---|---|
| `grantRef`, `audience` | Accepted consumer grant ID and exact MCP endpoint URL |
| `tenantId`, `namespace`, `actorId` | Tenant, namespace and authenticated launching AMESH principal |
| `sessionId`, `executionId`, `taskRunId` | Stable logical session and current execution/task identities |
| `invocationId` | Stable logical tool-call UUID, reused during recovery of that call |
| `attemptId`, `attempt` | Current executor attempt UUID and ordinal |
| `connection`, `connectionRevision`, `connectionDigest`, `tool` | Exact pinned destination and requested tool |

Validate the grant against all of that context and the authenticated AMESH instance. The gateway
must not trust an unauthenticated request claiming those fields. Return HTTP 403 for a denied,
revoked, expired or mismatched grant. Model-supplied `sessionId`, `bindingId` or similar arguments
cannot replace the authenticated context or authorize a different binding.

An accepted response is JSON with exactly `accessToken`, `tokenType: "Bearer"`, `audience`,
`expiresAt` (timezone-aware RFC 3339 timestamp), and `contextDigest`. The token expires within five
minutes. `contextDigest` is the SHA-256 hex digest of the request JSON encoded as UTF-8 with sorted
keys, no insignificant whitespace and unescaped Unicode. Bind the issued token to this exact
context; the digest alone is not an authentication mechanism. Limit the response to 32 KiB and the
token to 16,384 characters.

AMESH verifies the returned audience, digest and expiry, then uses the token as the MCP bearer for
that call. The gateway validates it at invocation time, enforces the bound tool/session and current
revocation/expiry, and correlates its durable receipt with `invocationId` and `attemptId`. Tool
discovery, schema-digest validation, AMESH allowlists, impact policy and approval gates still apply.
AMESH does not fall back to the connection credential if exchange fails, and scoped calls require
HTTP transport. Grant references are omitted from public execution projections; tokens and echoed
grant material are redacted before invocation results or errors enter ordinary evidence.

## Follow-up, retry and recovery

Canonical follow-up messages inherit the exact accepted grant map and original actor. They cannot
replace it through message input. The logical session remains the same; the new execution and its
tool calls receive new identities. A retry retains the logical invocation identity while its
attempt identity changes. Replaying a completed invocation reuses its receipt; an unfinished
external invocation remains ambiguous and is not silently repeated. The gateway must keep these
same rules across its own restarts. Losing a receipt after a possible mutation does not establish
whether the mutation happened.

Revoking a grant blocks future exchanges; the gateway must also reject any outstanding token for a
revoked grant at invocation time. Reauthorization for a different consumer binding requires a new
session/grant, not a model argument or a change to an existing checkpoint.

## Verification and single-user fallback

`python -m pytest tests/tasks/test_mcp_execution_grants.py` runs a provider-free gateway fixture
through the real Streamable HTTP MCP client. It checks two sessions on one endpoint, cross-binding
denial, follow-up/recovery correlation, expiry/revocation/audience rejection and token redaction.
The canonical API tests additionally check admission, immutable follow-up inheritance and public
execution redaction.

For a single-user MVP, use separate connection credentials scoped by the gateway to one approved
consumer binding and omit `executionGrant` and `toolGrants`. The gateway still validates that
credential's scope and current authority. AMESH does not implement browser membership, attachment,
origin checks, UI, recorder storage or external exactly-once execution.
