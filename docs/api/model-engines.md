# Subscription-backed model-engine API

AMESH exposes subscription-backed runtimes through the same provider-neutral model route used by
workflows and sessions. An engine route is identified by `provider.adapter` and `provider.engineRef`;
it does not contain an endpoint or a credential reference. `engineScopes` is the explicit permission
boundary that authorizes the route. Direct HTTP routes remain unchanged.

## Select an engine in a model policy

Use an immutable model-policy revision. The engine reference is an AMESH binding name, not a path,
token, account ID or provider credential:

```json
{
  "kind": "MODEL_POLICY",
  "key": "codex-subscription",
  "namespace": "agents.demo",
  "title": "Codex subscription",
  "routes": [{
    "routeId": "codex",
    "provider": {
      "adapter": "openai-codex-app-server",
      "engineRef": "team-codex"
    },
    "model": "gpt-5.6-luna",
    "requiredFeatures": ["structured-output", "streaming"],
    "parameters": {"reasoningEffort": "high"}
  }],
  "fallbackMode": "DISABLED"
}
```

The equivalent Copilot route uses `"adapter": "github-copilot-cli"`. Add the exact same binding
name to the agent's `permissions.engineScopes` and to the workflow task's `contract.engineScopes`:

```json
{
  "permissions": {"engineScopes": ["team-codex"]}
}
```

The engine route and a direct route are mutually exclusive. A missing or undelegated scope, unknown
adapter, unsupported capability or incompatible model limit fails before the external process starts.
Do not put provider-specific login fields, home directories or command arguments in a flow or agent
resource.

## Account lifecycle endpoints

All paths are namespace-scoped and require the caller's normal AMESH bearer credential plus
`X-Amesh-Tenant`. The catalog requires `agent_connection` view authority. Login and logout require
`agent_connection` manage authority. The response never contains a refresh token, keyring value,
filesystem path or raw process output.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/namespaces/{namespace}/model-engines/catalog` | List supported adapters, revisions and login modes. |
| `GET` | `/api/v1/namespaces/{namespace}/model-engines/{adapter}/{engineRef}/status` | Read safe authentication/readiness, plan and provider-reported usage/rate-limit metadata. |
| `POST` | `/api/v1/namespaces/{namespace}/model-engines/{adapter}/{engineRef}/login` | Start the official browser or device authorization flow. |
| `POST` | `/api/v1/namespaces/{namespace}/model-engines/{adapter}/{engineRef}/logout` | Log out the isolated local runtime account. |

Start a browser login:

```bash
curl -sS -X POST \
  http://localhost:8000/api/v1/namespaces/agents.demo/model-engines/openai-codex-app-server/team-codex/login \
  -H 'Authorization: Bearer <amesh-token>' \
  -H 'X-Amesh-Tenant: default' \
  -H 'Content-Type: application/json' \
  --data '{"mode":"browser"}'
```

The result contains a safe `authUrl` or device `verificationUrl`/`userCode`, a `loginId`, an
expiry when supplied by the runtime, and `actionRequired: true`. The operator must open the URL or
complete the device approval in a browser. AMESH does not automate or bypass that human approval.
Poll `status` until `authenticated: true`; `authenticated: null` means the runtime cannot yet
prove readiness (not that login succeeded). A failed or expired flow must be started again.

Use `{"mode":"device"}` for a device-code flow when the adapter supports it. To remove the local
account binding:

```bash
curl -sS -X POST \
  http://localhost:8000/api/v1/namespaces/agents.demo/model-engines/github-copilot-cli/team-copilot/logout \
  -H 'Authorization: Bearer <amesh-admin-token>' \
  -H 'X-Amesh-Tenant: default'
```

Logout clears the adapter's local account state. Provider-side OAuth grants are governed by the
provider and may require separate provider account settings to revoke completely.

## Capability semantics

The first process-engine revision advertises text/image input, structured final output, streaming
progress, cancellation and normalized usage when the runtime supplies it. `reasoningEffort` accepts
`low`, `medium`, `high`, `xhigh` or `max`; the engine translates it to the selected runtime. Images
must already be governed AMESH image references. AMESH resolves them to invocation-scoped temporary
files and removes those files after the process exits.

These subscription routes do not claim:

- embeddings;
- AMESH-native engine tools or MCP tools (engine tools are disabled; use AMESH-governed tools);
- provider-native opaque continuation handles;
- prompt-cache hit/write guarantees;
- exact API-style dollar cost or an exact downstream output-token ceiling.

The current process-engine revisions pin `gpt-5.6-luna` to its 1,050,000-token context window and
128,000-token physical output limit, so that model can run in `PROVIDER_BOUNDED` sessions without a
fabricated AMESH application ceiling. Any other engine model without an exact physical profile is
rejected before process I/O. Bounded engine requests that demand exact downstream token or dollar
enforcement are also rejected because these subscription runtimes do not expose those controls.
AMESH still validates structured output locally, records usage when known and reports monetary cost
as unavailable or quota-backed unless the runtime supplies a billable amount. Never treat missing
cost or cache evidence as zero.
