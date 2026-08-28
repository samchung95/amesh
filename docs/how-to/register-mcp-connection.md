# Register and call a governed MCP connection

Use this guide to discover an authenticated MCP server, pin its schemas, and call an allowed tool from
a workflow.

## Find attachable capabilities

The capability catalog is the user-facing projection of the resources that can be attached to an agent.
It includes prompts, skills, model policies, agents, plugins, MCP connections and MCP tools that the
caller is authorized to see. It reports exact revisions and digests, schemas, permissions, impact,
provider compatibility and attachment constraints; it does not copy or create a second registry.

```http
GET /api/v1/namespaces/agents.demo/agent/capabilities/catalog?q=research&kind=mcp-tool&status=available&limit=50
Authorization: Bearer <amesh-token>
X-Amesh-Tenant: default
```

Use the returned exact capability reference when attaching an item in the Agents capability catalog
or when creating a guided workflow draft. The response also reports `sourceAccess`, so denied,
unavailable or incompatible items can be explained without exposing an opaque identifier or secret.

## Discover the server

1. Put the remote bearer token in an environment variable available to the API and workers, then bind
   that variable to a namespace secret key as described in the
   [bounded-model guide](run-bounded-model-task.md#register-the-runtime-credential).

2. Discover the live catalog. AMESH resolves the credential at runtime and does not return it.

   ```http
   POST /api/v1/namespaces/agents.demo/agent/mcp-connections/discover
   Authorization: Bearer <amesh-token>
   X-Amesh-Tenant: default
   Content-Type: application/json

   {
     "endpoint": "https://mcp.example.test/mcp",
     "credentialRef": "mcp-token",
     "timeoutSeconds": 30
   }
   ```

3. Review every returned input/output schema and impact. Keep only approved tools, set each impact to
   `READ_ONLY`, `IDEMPOTENT_WRITE`, or `HIGH_IMPACT`, and submit the exact allowlist and pins.

   ```http
   POST /api/v1/namespaces/agents.demo/agent/mcp-connections
   Authorization: Bearer <amesh-token>
   X-Amesh-Tenant: default
   Content-Type: application/json

   {
     "key": "catalog",
     "namespace": "agents.demo",
     "endpoint": "https://mcp.example.test/mcp",
     "credentialRef": "mcp-token",
     "toolAllowlist": ["lookup"],
     "tools": [{
       "name": "lookup",
       "description": "Look up one record",
       "inputSchema": {"type":"object","properties":{"key":{"type":"string"}},"required":["key"]},
       "outputSchema": {"type":"object","properties":{"value":{"type":"string"}},"required":["value"]},
       "impact": "READ_ONLY"
     }]
   }
   ```

   AMESH rediscovers the server before saving. If the live schemas differ, the request returns `409`
   and no revision is stored.

## Test a pinned connection

After registering a revision, test that its approved tool schemas still match the live server. This
operation performs discovery only: it lists the server's tools, does not invoke a tool, and resolves
the configured secret binding only inside the server boundary.

```http
POST /api/v1/namespaces/agents.demo/agent/mcp-connections/catalog/test
Authorization: Bearer <amesh-token>
X-Amesh-Tenant: default
Content-Type: application/json

{"revision": 1, "timeoutSeconds": 30}
```

The result is `PASSED` when every pinned tool schema digest matches, `SCHEMA_DRIFT` when a pinned
schema is missing or changed, and `UNAVAILABLE` when discovery cannot reach the server. Each result
includes a redacted immutable audit `evidenceId`, the observed digest when available, and a checked
tool count. No endpoint credential or tool arguments are returned, and the evidence boundary is
`DISCOVERY_ONLY`.

4. Use the pinned tool catalog when composing an agent definition. It returns the `schemaDigest`
   required by an exact agent tool reference.

   ```http
   GET /api/v1/namespaces/agents.demo/agent/mcp-connections/catalog/tools?revision=1
   Authorization: Bearer <amesh-token>
   X-Amesh-Tenant: default
   ```

## Call a pinned tool

Reference the connection key from `agent.mcp`; declare its credential in `contract.secretScopes`.

```yaml
- id: lookup
  type: agent.mcp
  connection: catalog
  revision: 1
  tool: lookup
  arguments:
    key: customer-42
  dataHandling: DENY_SECRETS
  contract:
    secretScopes: [mcp-token]
  timeoutSeconds: 30
```

`READ_ONLY` tools need no additional flag. Other writes require `allowWrite: true`; a `HIGH_IMPACT`
tool also requires `approvalTask` naming a direct dependency whose output decision is `APPROVED`.
Before every call, AMESH verifies the live schema digest and validates the arguments. A completed
attempt is reused; an unfinished journal entry fails as an ambiguous external outcome instead of
repeating a possibly side-effecting call.

See the [agent primitive contract](../api/agent-primitives.md) for connection endpoints and failure
semantics. To attach the pinned tool to a reusable agent, continue with
[Define and pin an agent](define-agent-capability-envelope.md).
