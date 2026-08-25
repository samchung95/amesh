# Agent primitive API and task reference

This reference defines the bounded model tasks, governed MCP connections, and AMESH MCP read surface
introduced by EPIC-312.

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

`agent.mcp` accepts `connection`, optional `revision`, `tool`, `arguments`, `dataHandling`,
`allowWrite`, and `approvalTask`. It validates arguments against the pin, rediscovers the live server,
rejects schema drift, applies impact approval, validates structured output, and journals the call.
Legacy `endpoint` tasks remain available for compatibility but do not provide governed connection
semantics.

## AMESH MCP server

Streamable HTTP is available at `/mcp`. It accepts only AMESH workload credentials issued with
audience `amesh-mcp`; normal `amesh-api` tokens are rejected. DNS-rebinding protection restricts Host
and Origin to `NETWORK_EXTERNAL_BASE_URL` (or `http://localhost:8000` in local development).

The server exposes only read-only, non-destructive tools:

- `list_workflows(tenant, namespace, limit=100)` returns authorized revision identifiers and hashes.
- `inspect_execution(tenant, execution_id)` returns authorized execution and task-run states without
  inputs or outputs.

Each call uses the same role/binding/credential-scope authorization service as the REST API with
audience `amesh-mcp`. The MCP server cannot create executions or mutate orchestration state.
