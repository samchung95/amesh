# Configure agent memory, evaluations and release

Use these controls when a bounded `agent.session` needs retained context or must pass more than its
output schema. Memory, evaluations and approvals remain ordinary pinned resources and execution
evidence; they do not give the model authority over the workflow.

## Create an exact evaluation revision

Create this through **Agents → New resource → Evaluation** or
`POST /api/v1/namespaces/agents.demo/agent/resources`. The recorded fixture is evaluated without a
provider call. The optional judge uses the exact `luna-default@1` model policy, but it runs only after
the deterministic assertion and rubric pass.

```json
{
  "kind": "EVALUATION",
  "key": "incident-quality",
  "namespace": "agents.demo",
  "title": "Incident response quality",
  "description": "Require a concrete next action before release.",
  "assertions": [{
    "type": "object",
    "properties": {"nextAction": {"type": "string", "minLength": 1}},
    "required": ["nextAction"]
  }],
  "rubric": [{
    "key": "has-summary",
    "description": "The response contains a non-empty summary.",
    "assertion": {
      "type": "object",
      "properties": {"summary": {"type": "string", "minLength": 1}},
      "required": ["summary"]
    },
    "weight": 1
  }],
  "minimumRubricScore": 1,
  "fixtures": [{
    "key": "passing",
    "description": "Known deterministic pass.",
    "input": {"incident": "API latency exceeded the objective."},
    "recordedOutput": {
      "summary": "The API latency objective was exceeded.",
      "nextAction": "Inspect the slowest endpoint."
    }
  }],
  "judge": {
    "modelPolicy": {"key": "luna-default", "revision": 1},
    "prompt": "Score operational usefulness. Report uncertainty honestly.",
    "minimumScore": 0.8,
    "maximumUncertainty": 0.2,
    "maxCompletionTokens": 500
  }
}
```

Preview the recorded fixture without invoking Luna or any tool:

```text
GET /api/v1/namespaces/agents.demo/agent/evaluations/incident-quality/fixtures/passing/preview?revision=1
```

## Pin memory and evaluation boundaries

Create a new agent revision with these fields. `PRIVATE` memory is isolated by tenant, namespace,
agent key and agent revision. `EXECUTION` adds the execution identity. `SHARED` requires a stable
`sharedScope`; only agents explicitly pinned to that same scope can recall its keys.

```json
{
  "memoryPolicy": {
    "scope": "PRIVATE",
    "maxBytes": 1000000,
    "retentionSeconds": 86400,
    "redact": true,
    "sharedScope": null
  },
  "evaluationPolicy": {
    "requiredEvaluations": ["schema", "business", "incident-quality"],
    "evaluations": [{"key": "incident-quality", "revision": 1}],
    "requireHumanRelease": true
  }
}
```

The agent permission boundary must include the credential reference and network host of every judge
model route. Preview the complete effective envelope before execution:

```text
GET /api/v1/namespaces/agents.demo/agent/definitions/incident-helper/preview?agentRevision=2
```

The response includes every exact resource and tool schema, reports
`externalCallsSuppressed: true`, and reports `modelBehaviorUnknown: true`.

## Declare memory keys and human authority in the flow

Tasks recall only the listed keys and can write at most one final-output key. Recalled values are
appended as untrusted user reference data, never system instructions. A required human release uses
an `APPROVED` direct `core.approval` predecessor; a passing judge cannot replace it.

```yaml
id: governed_incident_agent
namespace: agents.demo
tasks:
  - id: approve
    type: core.approval
    title: Authorize governed agent release
    description: Confirm this run may release a result after its pinned gates pass.
    assigneeIds: [00000000-0000-7000-8000-000000000001]
    groupIds: []
    form:
      fields: []
      layout: []

  - id: summarize
    type: agent.session
    dependsOn: [approve]
    approvalTask: approve
    agent: incident-helper
    agentRevision: 2
    input:
      incident: API latency exceeded the objective for eight minutes.
    memoryReadKeys: [last-incident-summary]
    memoryWriteKey: last-incident-summary
    businessAssertions:
      - type: object
        required: [nextAction]
    contract:
      secretScopes: [openrouter-api-key]
    timeoutSeconds: 120
```

The execution trace orders session start and memory recall, model turns, deterministic evaluation,
judge evidence, human release, memory write and final acceptance. Judge score, uncertainty, route,
usage and cost remain evidence, not deterministic truth or approval authority.

## Inspect or delete retained memory

The memory API deliberately omits content:

```text
GET /api/v1/namespaces/agents.demo/agent/memory?agentKey=incident-helper
DELETE /api/v1/namespaces/agents.demo/agent/memory/{entryId}
```

Deletion is namespace-scoped, soft-deletes the entry and writes an audit event. Expired entries are
not returned to sessions or the catalog. Changing an evaluation, judge model, memory boundary or
release policy requires a new immutable resource/agent revision.
