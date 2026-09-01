# Extensions: tools, MCP, plugins, and providers

AMESH is intentionally extensible at the capability boundary. The core platform owns orchestration,
policy, evidence, and recovery. A connector or provider supplies a capability through a versioned
contract so the same controls work for different domains.

## Which extension should you use?

| You need to… | Use | What AMESH governs |
|---|---|---|
| Call a server that already speaks MCP | Governed MCP connection | Discovery, pinned schemas, allowlist, impact, credentials, arguments, journal, and evidence |
| Package reusable task/trigger/notification/condition logic | Isolated plugin | Manifest, version, capabilities, transport, schemas, runtime limits, and supervision |
| Add a model vendor or gateway | Model provider adapter | Capability negotiation, route pin, usage/cost, continuation, timeout, retry, and cancellation |
| Change the session implementation | Agent-session harness adapter | The harness port, AMESH model gateway, protocol/version evidence, and conformance |
| Provide a one-off workflow action | Existing built-in task or a plugin task | The task schema, runner boundary, timeout, output, and retry behavior |

Pick the smallest contract that fits. Do not put provider-specific fields into durable workflow
state, and do not make connector code a second orchestration engine.

## MCP tools

Discover an MCP server, review its tool schemas and impact labels, then save an immutable connection
revision with only the tools the agent may use. A live schema mismatch returns `SCHEMA_DRIFT` and
prevents invocation. `READ_ONLY` calls need no write flag; writes require explicit policy, and a
`HIGH_IMPACT` tool additionally requires a direct approved predecessor.

The [MCP connection guide](../how-to/register-mcp-connection.md) includes the discovery, registration,
test, and call sequence. For a browser extension, keep the exact automation command implementation
and sensitive browser state in the extension. Expose a high-level MCP operation with a narrow schema;
AMESH then supplies authorization, bounded calls, and trace evidence without becoming the browser's
secret store.

## Plugins

A plugin manifest declares its name, SemVer version, compatibility, entry points, configuration and
output schemas, transport target, dependencies, required capabilities, egress, filesystem access,
and secret scopes. Capability declarations are deny-first: installation or execution policy may grant
only a subset, and missing capabilities fail before connector code runs.

The SDK supports task, trigger, condition, runner, storage, secret, expression, and notification
entry points. Runtime code crosses an isolated RPC/OCI boundary by default. It receives scoped
capability tokens and typed requests, not unrestricted platform state. Start with the
[plugin manifest contract](../plugin-sdk/manifest.md), then use the
[extension contracts](../plugin-sdk/extension-contracts.md) and [isolated runtime guide](../plugin-sdk/isolated-runtime.md).

## Model providers

Providers implement the transport-neutral `ModelProvider` port. AMESH negotiates required features
before adapter I/O and pins the provider ID, revision, and digest. Responses are normalized into
usage, cost, structured output, tool proposals, timeout, retry, cancellation, and optional opaque
continuation fields. Private continuation data is encrypted behind secret references and is never a
public transcript.

The OpenAI-compatible adapter is suitable for OpenRouter and the current Luna qualification path.
Isolated Codex App Server and Copilot CLI runtimes use `engineRef` plus an explicit
`engineScopes` delegation; neither subscription is an API key. The workflow contract remains
provider-neutral. Follow [add and qualify a model provider](../how-to/add-model-provider.md) for
adapter/conformance expectations and the [model-engine operations runbook](../operations/model-engines.md)
for deployment isolation.

## Harnesses

The session harness is swappable. It receives an AMESH-authorized model call and returns a bounded
result. It may not call an MCP server directly, persist its own authoritative transcript, execute an
undeclared tool, or bypass the workflow state. The current Pi adapter runs in an isolated worker
with a versioned JSONL bridge and no provider credential; future DSH, Goose, or other adapters should
pass the same provider-free conformance kit. See the [agent-session harness contract](../plugin-sdk/agent-session-harness.md).

## Extension lifecycle

```text
declare schema and capability needs
        -> discover/validate locally
        -> review permissions and impact
        -> register an immutable revision
        -> resolve/pin it into a workflow or agent
        -> invoke through the governed runtime
        -> inspect evidence and version provenance
```

When an extension changes, publish a new revision and resolve a new subject. Existing executions keep
their old pin. The platform records the call or provider outcome before exposing it to downstream
orchestration, and restart/retry behavior follows the same idempotency and ambiguity rules as built-in
tasks.
