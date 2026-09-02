# Use a subscription-backed model engine

This guide is for a user or application developer who wants a workflow or durable agent session to
run through an authorized OpenAI Codex App Server or GitHub Copilot CLI account. The platform still
owns the workflow/session, policy, tools, schema validation, budgets, progress and evidence. The
subscription runtime supplies model execution only.

## 1. Check the catalog and log in

Deploy the optional pinned CLI image and shared state volume first by following the
[model-engine operations runbook](../operations/model-engines.md). A normal AMESH image can expose
the catalog but cannot start either local CLI. The checked-in local overlay explicitly permits the
headless Copilot CLI to store its OAuth token under the protected, binding-specific
`COPILOT_HOME`; this fallback is disabled in the normal configuration.

An administrator first grants the caller `agent_connection` view/manage access in the target tenant
and namespace. Discover the exact adapter revision:

```powershell
$headers = @{
  Authorization = "Bearer <amesh-token>"
  "X-Amesh-Tenant" = "default"
}
Invoke-RestMethod `
  http://localhost:8000/api/v1/namespaces/agents.demo/model-engines/catalog `
  -Headers $headers
```

Start login through the [account lifecycle API](../api/model-engines.md). For Codex, AMESH uses the
official Codex App Server ChatGPT browser or device-code flow. For Copilot, AMESH uses the official
Copilot CLI browser or device-code flow. Open the returned URL or enter the returned code yourself,
then poll status until the runtime reports `authenticated: true`. No cookie, browser storage or
undocumented token is accepted, and no credential is returned by AMESH.

## 2. Attach the engine to an agent

Create a model-policy revision whose route uses `engineRef`, then give the agent permission for that
exact reference:

```json
{
  "kind": "MODEL_POLICY",
  "key": "research-codex",
  "namespace": "agents.demo",
  "routes": [{
    "routeId": "primary",
    "provider": {
      "adapter": "openai-codex-app-server",
      "engineRef": "team-codex"
    },
    "model": "gpt-5.6-luna",
    "requiredFeatures": ["structured-output", "image-input", "streaming"],
    "parameters": {"reasoningEffort": "medium"}
  }],
  "fallbackMode": "DISABLED"
}
```

For an `agent.session` workflow node, the task contract must delegate the same engine reference:

```yaml
tasks:
  - id: analyze
    type: agent.session
    agent: research-agent
    agentRevision: 1
    input:
      question: "Summarize the supplied report."
    contract:
      engineScopes: [team-codex]
```

The agent revision's `permissions.engineScopes` must contain `team-codex` too. For a one-shot
`agent.structured` or `agent.chat` task, put the same `engineScopes` in its task contract. AMESH
rejects a route whose engine scope is not explicitly delegated, before starting Codex or Copilot.

## 3. Run with the normal AMESH controls

Use the existing workflow/session launch APIs or the web control room. The current Codex and Copilot
revisions include an exact physical profile for `gpt-5.6-luna`, so that model can run with a
`PROVIDER_BOUNDED` agent and context policy. Other engine model names fail before process I/O until
an exact profile is published; AMESH does not invent a generic context window or output ceiling.
Structured results still pass the pinned JSON Schema, and images still enter through governed image
references at any workflow stage. AMESH emits chronological progress and normalized usage evidence
where available.

The engine process has no AMESH credential, MCP client or native tool authority. If the agent needs a
tool, declare and authorize an AMESH plugin/MCP tool; the ordinary AMESH tool journal and approval
policy remain in charge. A subscription does not make an agent unrestricted.

## What to expect

Provider quota and API token pricing are different. Codex and Copilot may report token activity,
rate limits or plan labels, but they do not promise an API-style dollar amount. AMESH therefore marks
cost unavailable or quota-backed when no billable value is supplied. Cache hits are likewise only
reported when the runtime supplies cache evidence.

Subscription runtimes do not currently provide AMESH-compatible opaque continuation handles,
embeddings, native engine tools, cache guarantees or an exact downstream output-token ceiling. A
request that requires one of those capabilities fails during capability negotiation. The model's
wording remains nondeterministic even when the route and inputs are pinned.
