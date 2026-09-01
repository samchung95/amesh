# Run a bounded agent session

Use this guide after creating `incident-helper@1` from
[Define and pin an agent](define-agent-capability-envelope.md). The runtime secret binding named
`openrouter-api-key` must resolve to an OpenRouter credential; its value is never stored in the flow,
agent definition, checkpoint or trace.

For agents whose required input is only `request`, open **Workflows → Create workflow → AI / model
task** for the no-YAML path. Select the immutable agent revision, inspect **Preview resolved
envelope**, tune the repair, data-handling and derived-context bounds, then save. The preview is
side-effect-free and shows the exact nested resource pins, routes, tools, schema, permissions and hard
budgets. **Test agent node (isolated)** uses an inline flow-test fixture and never calls the model or
tools. Agents with a different required input contract continue through the YAML path below.

## Create and run the workflow

Save
[bounded-agent-session.yaml](https://github.com/samchung95/amesh/blob/main/examples/bounded-agent-session.yaml),
then create and run it
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

The workflow task succeeds only after the pinned output schema, listed business assertions and every
exact evaluation revision pass. Its output contains `result` plus the immutable pin, final counters,
memory/evaluation/release evidence and nondeterminism disclosure under `session`.

## Require exact tool calls before final output

Add `requiredToolPlan` when prompt guidance is not sufficient and the runtime must prove that every
required call completed. This example expands once per input candidate while binding `topic` from the
full task input and `candidate` from each current item:

```yaml
input:
  topic: payment latency
  candidates:
    - symbol: API
    - symbol: WORKER
requiredToolPlan:
  schemaVersion: amesh.agent-tool-plan/v1
  steps:
    - stepId: inspect-candidates
      toolName: research.lookup
      arguments:
        depth: brief
      argumentBindings:
        topic: /topic
      forEach: /candidates
      itemArgumentBindings:
        candidate: /symbol
      maxOccurrences: 25
  maxOccurrences: 100
```

`research.lookup` must be pinned in the selected agent revision. AMESH freezes the expanded order at
admission, matches the exact next call after ordinary pinned argument bindings, and performs that
check before approval or external tool I/O. A final action with missing occurrences consumes the
configured output-repair budget; with no remaining repair it fails with a
`required_tool_plan` reason. The checkpoint preserves completed occurrences across worker restart,
and safe event/result projections expose completion state and digests without tool arguments.

## Inspect what happened

Open the execution and use **Simple execution trace**. Agent annotations identify the envelope,
model turn and cumulative budget, authorized tool/approval decision, tool result, memory recall/write,
deterministic and judge evaluation, human release, rejected repair or accepted output. The same
persisted redacted summaries are available at:

```text
GET /api/v1/executions/{executionId}/agent-sessions
GET /api/v1/executions/{executionId}/evidence
```

Select a session task in the trace to inspect its ordered event detail:

```text
GET /api/v1/executions/{executionId}/agent-sessions/{taskRunId}?attempt=1&afterEventIndex=0&limit=100
```

The detail response includes a bounded `events` page and `nextEventIndex`; pass that cursor back as
`afterEventIndex` to continue. The summary and detail routes are projections of the canonical,
tenant-authorized session journal, so they remain inspectable after an API or worker restart. They
exclude private checkpoints, prompts/messages, model continuations, hidden reasoning and raw oversized
payloads; sensitive fields are redacted and payloads over 64 KiB are returned only as digest/size
metadata with `truncated: true`.

To replay a run, use the existing replay/backfill control from the execution context. Replay requires
one frozen attestation per source execution: `sourceExecutionId`, `frozenInputDigest`, and exact
`resourcePins` containing each resource `key`, `revision`, and `digest`. AMESH verifies the
attestation against the source execution and its determinism envelope, rejects any replay `inputs`
override, and carries the source input values forward unchanged. The new execution retains its source
linkage and an identical frozen source/pin submission converges on the existing durable replay rather
than creating a duplicate accepted effect.

On worker restart, AMESH loads the last checkpoint. A pending accepted proposal is dispatched with
the same primitive invocation key; an already completed call is reused, while an ambiguous unfinished
external call is not repeated. A failure after a tool effect is non-retryable so a fresh orchestration
attempt cannot silently duplicate that effect.

For high-impact tools, add a direct `core.approval` predecessor, set `approvalTask` to its task ID,
and include that ID in `dependsOn`. The model cannot grant its own approval or call an undeclared tool.
Use [Configure memory, evaluations and release](configure-agent-memory-evaluations.md) for exact
resource and workflow examples.
