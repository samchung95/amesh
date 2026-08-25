# Register and call a governed MCP connection

Use this guide to discover an authenticated MCP server, pin its schemas, and call an allowed tool from
a workflow.

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
