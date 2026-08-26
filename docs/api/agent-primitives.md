# Agent primitive API and task reference

This reference defines the bounded model tasks, governed MCP connections, versioned agent resources,
durable governed agent sessions, and AMESH MCP read surface introduced by EPIC-312 and
EPIC-807–809.

## Model task types

| Task type | Required operation input | Validated result field |
|---|---|---|
| `agent.chat` | `prompt` or `messages` | `content` |
| `agent.embedding` | `input` string or string array | `embeddings` |
| `agent.structured` | `prompt`/`messages` plus `outputSchema` | `structuredOutput` |
| `agent.toolCall` | `prompt`/`messages` plus `tools` | `toolCalls` |

Every bounded model task requires:

- `provider.endpoint`, `provider.credentialRef`, and optional `provider.embeddingEndpoint`; the only
  shipped adapter is `openai-compatible`.
- `model`; OpenRouter qualification uses `openai/gpt-5.6-luna`.
- `budget.maxTotalTokens`, optional `budget.maxCompletionTokens`, and `budget.maxCostUsd`.
- `dataHandling.egress`: `DENY_SECRETS`, `REDACT_SECRETS`, or `ALLOW`.
- `dataHandling.promptRetention`: `REDACTED` or `HASH_ONLY`.
- the provider credential in `contract.secretScopes`.

`parameters` supports `temperature`, `topP`, and `seed`. Standard task `timeoutSeconds` and `retry`
fields control the attempt deadline and retry schedule. Responses include the operation, resolved
model, provider usage, `costUsd`, and provenance containing the endpoint, model, policy, request hash,
retry/timeout metadata, and `nondeterministic: true`. Prompt retention never stores a runtime
credential; output and errors replace known secret values before persistence.

`agent.structured` validates the parsed response with `Draft202012Validator` before publishing task
output. `agent.toolCall` validates every proposed function and argument object against its declared
tool schema; it proposes calls but does not execute them.

## Invocation replay boundary

Migration `0056_agent_primitives.sql` adds the tenant-scoped `agent_invocations` journal. One row is
created before each model or governed MCP attempt. A duplicate completed attempt returns the stored
validated result. A duplicate `STARTED` attempt is not repeated because its external outcome is
ambiguous. A later orchestration attempt has a new attempt identity and follows the task retry policy.

Pinned request metadata makes replay evidence comparable, but a replayed provider request is still
nondeterministic. AMESH does not claim byte-identical model output.

## Governed MCP connections

Connection revisions are immutable and tenant/namespace scoped. A revision stores the endpoint,
credential reference, exact tool allowlist, input/output schemas, impact labels, and canonical digest;
it never stores the credential value.

| Method and path | Purpose |
|---|---|
| `POST /api/v1/namespaces/{namespace}/agent/mcp-connections/discover` | Authenticate and discover live schemas. |
| `POST /api/v1/namespaces/{namespace}/agent/mcp-connections` | Verify live schemas and create the next immutable revision. |
| `GET /api/v1/namespaces/{namespace}/agent/mcp-connections` | List the latest revision of each key. |
| `GET /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}?revision=N` | Read one latest or pinned revision. |
| `GET /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools?revision=N` | List the exact tool catalog and schema digests for an approved revision. |
| `POST /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/test` | Discover the live server and compare its pinned tool schema digests without invoking a tool. |

The connection test accepts `revision` and `timeoutSeconds`. It uses the connection's secret binding
reference and ordinary egress policy, then returns `PASSED`, `SCHEMA_DRIFT`, or `UNAVAILABLE`.
The response includes a redacted immutable audit `evidenceId`, the exact connection pin, an observed
digest when available, a checked tool count, and `effectBoundary: DISCOVERY_ONLY`. It never returns
credential values or invokes a tool. Authorization failures are denied before discovery.

### Authorized capability catalog

`GET /api/v1/namespaces/{namespace}/agent/capabilities/catalog` is one authorized projection over the
immutable agent resource, MCP connection/tool, and self-hosted plugin registries. It is not a second
registry and does not copy opaque IDs into a new store. Each catalog item can expose its exact
revision/digest, kind and label, status, schemas, permissions, impact, provider compatibility and
attachment constraints, together with source-level access information in `sourceAccess`.

Supported query parameters are `q`, `kind`, `status`, and `limit`. The projection applies authorization
independently to each source, so denied or unavailable source entries can be reported as actionable
status without leaking their protected metadata. The guided agent authoring UI consumes these exact
references; attaching an item creates a new unsaved guided workflow draft rather than mutating the
catalog or silently selecting a different revision.

`agent.mcp` accepts `connection`, optional `revision`, `tool`, `arguments`, `dataHandling`,
`allowWrite`, and `approvalTask`. It validates arguments against the pin, rediscovers the live server,
rejects schema drift, applies impact approval, validates structured output, and journals the call.
Legacy `endpoint` tasks remain available for compatibility but do not provide governed connection
semantics.

## Versioned agent resources

Prompt, skill, model-policy, evaluation, and agent definitions share one tenant- and namespace-scoped immutable
revision ledger. Creating an existing key adds a revision; references inside an agent definition must
always name an exact revision.

| Method and path | Purpose |
|---|---|
| `POST /api/v1/namespaces/{namespace}/agent/resources` | Create the next immutable resource revision. |
| `GET /api/v1/namespaces/{namespace}/agent/resources?kind=AGENT` | List the latest resources, optionally by kind. |
| `GET /api/v1/namespaces/{namespace}/agent/resources/{kind}/{key}?revision=N` | Inspect an exact resource revision. |
| `POST /api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve` | Resolve exact dependencies and atomically pin the effective capability envelope to a subject. |
| `GET /api/v1/namespaces/{namespace}/agent/definitions/{key}/preview?agentRevision=N` | Resolve the envelope without provider, tool, memory or approval side effects; model behavior is reported unknown. |
| `GET /api/v1/namespaces/{namespace}/agent/evaluations/{key}/fixtures/{fixture}/preview?revision=N` | Run deterministic assertions/rubrics over one recorded fixture without invoking its optional judge. |
| `GET /api/v1/namespaces/{namespace}/agent/definitions/{key}/compare?fromRevision=A&toRevision=B` | Explain agent revision changes. |
| `GET /api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration?fromRevision=A&toRevision=B` | Explain provider-route migration and output nondeterminism. |

The resolved `amesh.agent-envelope/v1` pin contains the exact prompt, skill, model-policy and MCP
tool and evaluation revisions, composed instructions, schemas, memory policy, delegated permissions,
hard limits and evaluation policy. Resolution rejects missing revisions, schema drift, undelegated skill
capabilities, undeclared secret/network access, and unapproved high-impact tools. A `subjectRef` is
content-addressed: retrying the same resolution is idempotent, while trying to attach a different
envelope to the same subject is rejected.

The envelope is deterministic configuration evidence, not a claim that model output is deterministic.
Provider substitution creates a new model-policy revision and the migration endpoint always reports
that output remains nondeterministic. See
[Define and pin an agent](../how-to/define-agent-capability-envelope.md) for an end-to-end example.

## Durable `agent.session` task

`agent.session` accepts `agent`, exact `agentRevision`, typed `input`, `invalidOutputPolicy` (`FAIL` or
`REPAIR`), bounded `maxRepairAttempts`, optional Draft 2020-12 `businessAssertions`, optional
`approvalTask`, `memoryReadKeys`, `memoryWriteKey`, and `dataHandling`. Every envelope secret scope must also appear in the task
`contract.secretScopes`.

The task atomically resolves a capability pin using the task-run and attempt identity, validates the
input schema, and then asks the pinned model for exactly one proposed action at a time. A proposal is
either a pinned MCP tool call or a final object. AMESH—not the model—validates tool identity and
schema, enforces authority and approval, dispatches the governed MCP primitive, and validates the
final output schema and business assertions.

Migration `0058_agent_sessions.sql` stores the current checkpoint, cumulative turn/loop/tool/token/
cost counters, and ordered idempotent events. Those events are projected into the ordinary execution
evidence stream and the simple trace. `GET /api/v1/executions/{executionId}/agent-sessions` returns
authorized, redacted session summaries for inspection. A summary includes the session/task identity,
capability-pin and envelope digests, state and phase, cumulative counters, the bounded context receipt,
final result, error and lifecycle timestamps. It does not include the private checkpoint, transcript,
prompts, model continuation or hidden reasoning.

Use `GET /api/v1/executions/{executionId}/agent-sessions/{taskRunId}` to drill into one authorized
session attempt. The detail projection is paginated over the canonical ordered event journal:

| Query parameter | Meaning |
|---|---|
| `attempt` (default `1`) | Select the task-run attempt. |
| `afterEventIndex` (default `0`) | Return events whose index is greater than this cursor. |
| `limit` (default `100`, maximum `100`) | Bound the returned event page. |

The response returns `events` and `nextEventIndex`; pass that value as `afterEventIndex` for the next
page. Event payloads are redacted for credentials, prompts, messages, continuations, private/model
rationale and hidden reasoning. Payloads larger than 64 KiB are represented by a digest, byte count
and `truncated: true`. These exclusions apply after authorization and are part of the public contract;
the endpoint never exposes chain-of-thought or a raw private checkpoint.

One stable `invocationKey` is derived for each model route and tool action. Recovery therefore reuses
a completed primitive result without repeating its effect. An unfinished external call is reported
as ambiguous and fails closed. At most one external operation is in flight; the task checks
cancellation and the pinned turn, loop, tool-call, token, cost and duration ceilings between calls.
High-impact tools and `ALLOW` sensitive-data egress require an `APPROVED` direct `approvalTask`
dependency. Model output and future model calls remain explicitly nondeterministic.

Replay is a linked execution operation, not a second session engine. A replay submission must attest
each selected source with its `sourceExecutionId`, `frozenInputDigest` and exact `resourcePins`
(`key`, `revision`, `digest`). The server verifies those values against the immutable source
execution's inputs and determinism envelope. Replay submissions cannot provide input overrides;
replayed inputs are copied from the source exactly. Re-submitting the same frozen source and pins
converges on the existing replay backfill and generated execution through the durable idempotency
key, while the source execution linkage remains visible in the new execution trigger/evidence.

Migration `0059_agent_memory.sql` adds tenant-RLS memory entries with `EXECUTION`, revision-private
`PRIVATE`, or explicitly named `SHARED` boundaries. Size and expiry are enforced at write/read time;
known secrets are redacted, every write carries operation/session/envelope provenance, and duplicate
operation keys reuse the stored entry. The authorized catalog returns metadata and digests only:

| Method and path | Purpose |
|---|---|
| `GET /api/v1/namespaces/{namespace}/agent/memory?agentKey=KEY` | List active memory metadata without content. |
| `DELETE /api/v1/namespaces/{namespace}/agent/memory/{entryId}` | Soft-delete one namespace-scoped entry and write audit evidence. |

Exact `EVALUATION` revisions run deterministic JSON-schema assertions and weighted rubrics before
an optional judge pinned to an exact model policy. Judge evidence includes model route, tokens, cost,
score, uncertainty, rationale and a nondeterminism disclosure. A deterministic failure cannot be
overridden by a judge. When `requireHumanRelease` is true, only an `APPROVED` direct
`core.approval` predecessor releases the result; the judge is never release or tool authority.

See [Run a bounded agent session](../how-to/run-bounded-agent-session.md) and
[Configure memory, evaluations and release](../how-to/configure-agent-memory-evaluations.md) for
workflow and trace inspection steps.

## Agent mesh tasks and route preview

`agent.mesh` is a static flowable with `topology`, exact `members`, a parent `budget`, bounded
`maxConcurrency` and ordinary child tasks. Every member names one exact `agent.session` child and a
complete `meshBudget`; validation rejects identity mismatches, unregistered sessions, cycles,
unwired hand-offs and reservation overcommit. The session runtime uses the tighter member or agent
limit, and the parent emits `amesh.agent-mesh/v1` topology, member, aggregate-usage, routing,
hand-off and nondeterminism evidence.

`agent.route` accepts `requiredCapabilities` and exact candidates with policy decision/digest,
availability source/time, projected cost/latency and evaluation key/revision/score. It emits an
`amesh.agent-route/v1` decision after deterministic gates and ranking. The same pure operation is
available without persistence or external calls:

| Method and path | Purpose |
|---|---|
| `POST /api/v1/namespaces/{namespace}/agent/mesh/routes/preview` | Authorize and preview an explainable route without creating a run. |

`agent.handoff` requires exact source/destination task and agent revisions, a rendered object
`payload`, Draft 2020-12 `schema`, non-empty `rationale`, optional `contextKeys`/`redactKeys`, required
delegated capabilities and an exact policy decision. It accepts only a direct completed source and
publishes selected redacted context plus `amesh.agent-handoff/v1` source, destination, rationale,
schema/context/policy and redaction provenance.

See [Coordinate a bounded agent mesh](../how-to/coordinate-agent-mesh.md) for topology and workflow
examples. Mesh policy and state are provider-neutral; all model output remains nondeterministic.

## AMESH MCP server

Streamable HTTP is available at `/mcp`. It accepts only AMESH workload credentials issued with
audience `amesh-mcp`; normal `amesh-api` tokens are rejected. DNS-rebinding protection restricts Host
and Origin to `NETWORK_EXTERNAL_BASE_URL` (or `http://localhost:8000` in local development).

The server exposes only read-only, non-destructive tools:

- `list_workflows(tenant, namespace, limit=100)` returns authorized revision identifiers and hashes.
- `inspect_execution(tenant, execution_id)` returns authorized execution and task-run states without
  inputs or outputs.
- `list_agents(tenant, namespace, limit=100)` returns authorized latest agent-definition revisions.
- `inspect_agent(tenant, namespace, key, revision=None)` returns one authorized exact definition and
  its credential references, never credential values.

Each call uses the same role/binding/credential-scope authorization service as the REST API with
audience `amesh-mcp`. The MCP server cannot create executions or mutate orchestration state.
