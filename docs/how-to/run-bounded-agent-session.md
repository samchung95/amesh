# Run a bounded agent session

Use this guide after creating `incident-helper@1` from
[Define and pin an agent](define-agent-capability-envelope.md). The runtime secret binding named
`openrouter-api-key` must resolve to an OpenRouter credential; its value is never stored in the flow,
agent definition, checkpoint or trace.

## Create and run the workflow

Save [bounded-agent-session.yaml](../../examples/bounded-agent-session.yaml), then create and run it
through the Workflows page or the existing flow/execution API. The task input must satisfy the pinned
agent input schema. `REPAIR` allows one additional model turn only when the envelope still has turn,
loop, token, cost and duration capacity.

```yaml
id: bounded_agent_session
namespace: agents.demo
tasks:
  - id: summarize
    type: agent.session
    agent: incident-helper
    agentRevision: 1
    input:
      incident: API latency exceeded the objective for eight minutes.
    invalidOutputPolicy: REPAIR
    maxRepairAttempts: 1
    dataHandling: DENY_SECRETS
    businessAssertions:
      - type: object
        properties:
          nextAction:
            type: string
            minLength: 1
        required: [nextAction]
    contract:
      secretScopes: [openrouter-api-key]
    retry:
      maxAttempts: 2
      delaySeconds: 2
    timeoutSeconds: 120
outputs:
  summary: "{{ outputs.summarize.result }}"
```

The workflow task succeeds only after the pinned output schema and the listed business assertion
pass. Its output contains `result` plus the immutable pin, final counters and nondeterminism
disclosure under `session`.

## Inspect what happened

Open the execution and use **Simple execution trace**. Agent annotations identify the envelope,
model turn and cumulative budget, authorized tool/approval decision, tool result, rejected repair or
accepted output. The same persisted summaries are available at:

```text
GET /api/v1/executions/{executionId}/agent-sessions
GET /api/v1/executions/{executionId}/evidence
```

On worker restart, AMESH loads the last checkpoint. A pending accepted proposal is dispatched with
the same primitive invocation key; an already completed call is reused, while an ambiguous unfinished
external call is not repeated. A failure after a tool effect is non-retryable so a fresh orchestration
attempt cannot silently duplicate that effect.

For high-impact tools, add a direct `core.approval` predecessor, set `approvalTask` to its task ID,
and include that ID in `dependsOn`. The model cannot grant its own approval or call an undeclared tool.
