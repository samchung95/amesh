# Coordinate a bounded agent mesh

Use an `agent.mesh` when work needs more than one exact agent definition. Each member is still an
ordinary recoverable `agent.session`; the mesh adds static topology, deterministic routing, typed
context transfer and a parent budget.

## Choose a topology

| Topology | Declared roles | Typical wiring |
|---|---|---|
| `SUPERVISOR` | One `SUPERVISOR`, one or more workers | Worker → typed hand-off → supervisor |
| `ROUTER` | One `ROUTER`, one or more candidates | Route → candidate `runIf` branches |
| `PEER_TO_PEER` | Two or more `PEER` members | Explicit typed hand-offs between peers |
| `HIERARCHICAL` | One root and parent-linked descendants | Child results move upward through hand-offs |
| `SWARM` | Two or more `PEER` members | Bounded parallel peers with an explicit join/reviewer |

The topology is descriptive and validated; `dependsOn`, `runIf`, hand-offs and the ordinary reducer
remain the execution semantics. A model cannot add a member, mutate a dependency or expand its own
budget.

## Run the supervisor example

Create the exact `incident-analyst@2` and `incident-supervisor@4` definitions referenced by
[agent-mesh-supervisor.yaml](../../examples/agent-mesh-supervisor.yaml). The supervisor must declare
the delegated capability `incident-supervision`; both agents must use the runtime-only
`openrouter-api-key` secret binding. Then save and run the example through Workflows.

Validation checks all of these before a run exists:

- member IDs, session task IDs and exact agent revisions match;
- parent links are known and acyclic;
- every member session has `meshId`, `memberId` and a complete `meshBudget` reservation;
- reservation sums and `maxConcurrency` fit the parent budget;
- each hand-off directly depends on its exact source, and its destination directly depends on it;
- route candidates exactly match declared member task, agent, revision and capabilities.

At runtime the hand-off additionally checks the rendered payload schema, exact source-session
identity, destination delegated capability, policy outcome and secret redaction before publishing
`payload` for the destination.

## Build a deterministic router

Add an `agent.route` child with exact signals for every candidate. Capability, policy and
availability are fail-closed gates. Evaluation score descending, projected cost ascending, projected
latency ascending and stable member ID form the documented tie-break order. Candidate sessions can
then use ordinary conditions such as:

```yaml
dependsOn: [choose_agent]
runIf: "{{ outputs.choose_agent.agentRoute.selectedMemberId == 'analyst' }}"
```

Preview the same routing contract without creating an execution or calling a provider:

```text
POST /api/v1/namespaces/{namespace}/agent/mesh/routes/preview
```

## Inspect and recover

Open **Simple execution trace**. It renders the selected route and exact revision, each typed
hand-off and policy outcome, member session phases, and the parent session/token/cost/tool totals.
Raw task results retain the complete decision assessments and hand-off provenance digests.

Restart, cancellation and provider failure follow the existing task-run and `agent.session`
boundaries. Completed member and hand-off task results are reused; an unfinished external provider
operation remains an explicitly ambiguous failure and is not silently repeated. Provider migration
changes exact model-policy/agent revisions, not the mesh state schema. Topology and policy evidence
is deterministic; model output is not.
