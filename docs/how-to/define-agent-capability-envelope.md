# Define and pin an agent capability envelope

Open the web app and select **Agents** for the guided path. It presents resource kinds, exact
revision selectors, approved MCP tools, schema presets, memory choices, and bounded limits without
requiring raw YAML or JSON. The API and CLI expose the same immutable contracts for automation.

This example defines a bounded OpenRouter agent using `openai/gpt-5.6-luna`. It stores only the
credential reference `openrouter-api-key`; register that runtime secret separately before execution.

## Create exact dependencies

Save each JSON object as a separate file and apply it in dependency order:

```json
{
  "kind": "MODEL_POLICY",
  "key": "luna-default",
  "namespace": "agents.demo",
  "title": "OpenRouter Luna",
  "routes": [{
    "routeId": "primary",
    "provider": {
      "adapter": "openai-compatible",
      "endpoint": "https://openrouter.ai/api/v1/chat/completions",
      "credentialRef": "openrouter-api-key"
    },
    "model": "openai/gpt-5.6-luna",
    "requiredFeatures": ["structured-output"],
    "parameters": {"temperature": 0}
  }],
  "fallbackMode": "DISABLED",
  "outputNondeterminismDisclosure": "Model output can vary across calls and provider revisions."
}
```

```json
{
  "kind": "PROMPT",
  "key": "support-tone",
  "namespace": "agents.demo",
  "title": "Support tone",
  "content": "Answer for {{audience}} with concise, evidence-backed steps.",
  "variables": {"audience": "an operations user"}
}
```

```json
{
  "kind": "SKILL",
  "key": "incident-summary",
  "namespace": "agents.demo",
  "title": "Incident summary",
  "description": "Produce an operational incident summary.",
  "instructions": "Separate observed facts, inference, impact, and next action.",
  "requestedCapabilities": ["summarize-incidents"]
}
```

Apply the files; every successful call prints the assigned revision and SHA-256 digest.

```powershell
amesh agent apply agents.demo model-policy.json
amesh agent apply agents.demo prompt.json
amesh agent apply agents.demo skill.json
```

## Create the agent definition

References are exact. If a dependency changes, create and review a new agent revision instead of
silently following a mutable latest value.

```json
{
  "kind": "AGENT",
  "key": "incident-helper",
  "namespace": "agents.demo",
  "title": "Incident helper",
  "description": "Turns bounded incident input into a structured summary.",
  "instructions": "Use only supplied input and approved capabilities.",
  "inputSchema": {
    "type": "object",
    "properties": {"incident": {"type": "string"}},
    "required": ["incident"],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "summary": {"type": "string"},
      "nextAction": {"type": "string"}
    },
    "required": ["summary", "nextAction"],
    "additionalProperties": false
  },
  "modelPolicy": {"key": "luna-default", "revision": 1},
  "prompts": [{"key": "support-tone", "revision": 1, "order": 10}],
  "skills": [{"key": "incident-summary", "revision": 1}],
  "tools": [],
  "memoryPolicy": {"scope": "NONE", "maxBytes": 0, "retentionSeconds": 0, "redact": true},
  "permissions": {
    "delegatedCapabilities": ["summarize-incidents"],
    "toolAllowlist": [],
    "secretScopes": ["openrouter-api-key"],
    "networkHosts": ["openrouter.ai"],
    "filesystemReadRoots": [],
    "filesystemWriteRoots": [],
    "allowHighImpactTools": false
  },
  "hardLimits": {
    "maxTotalTokens": 4096,
    "maxCostUsd": 0.25,
    "maxDurationSeconds": 120,
    "maxToolCalls": 0,
    "maxTurns": 4,
    "maxLoopIterations": 3,
    "maxRecursionDepth": 0,
    "maxConcurrency": 1
  },
  "evaluationPolicy": {"requiredEvaluations": [], "evaluations": [], "requireHumanRelease": false}
}
```

```powershell
amesh agent apply agents.demo agent.json
```

## Resolve and inspect the pin

Resolve before execution and use a stable, unique subject identity. The same subject can be retried
with the same envelope, but cannot be rebound to a different envelope.

```powershell
amesh agent resolve agents.demo incident-helper --revision 1 --subject-ref workflow-execution:demo-001
amesh agent get agents.demo AGENT incident-helper --revision 1
amesh agent compare agents.demo incident-helper --from-revision 1 --to-revision 2
amesh agent model-migration agents.demo luna-default --from-revision 1 --to-revision 2
```

Resolution composes instructions in declared order and validates every capability, credential,
network host, schema, tool digest and hard boundary. A `409` means no new pin was accepted; inspect
the error, create a new immutable dependency or definition revision, and resolve a new subject.

EPIC-807 establishes this deterministic configuration boundary. The `agent.session` task consumes
the pin through the durable EPIC-808 journal; neither layer promises reproducible model text. Continue
with [Run a bounded agent session](run-bounded-agent-session.md), then optionally add
[memory, evaluations and human release](configure-agent-memory-evaluations.md).
