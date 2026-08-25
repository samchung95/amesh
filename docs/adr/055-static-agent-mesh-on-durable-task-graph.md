# ADR-055: Static agent meshes on the durable task graph

- Status: Accepted
- Date: 2026-08-25
- Owners: EPIC-806

## Context

AMESH already has a durable reducer, exact agent capability pins, bounded recoverable sessions,
isolated memory, evaluation gates and human approvals. Multi-agent coordination must compose those
controls without giving a model direct orchestration authority or creating a second state machine.
Routing and hand-offs also need durable evidence that remains useful when model providers change.

## Decision

1. Add `agent.mesh` as a static flowable that compiles supervisor, router, peer-to-peer,
   hierarchical and swarm members into ordinary child task runs in the existing reducer.
2. Require each member to identify one exact `agent.session` child, agent revision, role and declared
   capability set. Every session receives a reservation, and validation rejects reservations whose
   sessions, concurrency, tokens, cost, duration or tools exceed the parent mesh budget.
3. Enforce the minimum of the member reservation and the pinned agent hard limits during model,
   judge and tool operations. The mesh parent fails closed if persisted aggregate usage exceeds its
   budget and records topology, members, usage and model nondeterminism in its result.
4. Make `agent.route` a pure, deterministic task. Capability coverage, policy allow and availability
   are gates; eligible members are ordered by exact evaluation score, projected cost, latency and a
   stable member ID. The full assessment and content-addressed decision are durable task output.
5. Make `agent.handoff` a pure, idempotent boundary task between a completed source session and a
   directly dependent destination. It validates a Draft 2020-12 schema, verifies exact endpoint
   identity, destination delegation and policy, selects explicit context, redacts protected values,
   and records source, destination, rationale and policy/schema/context digests.
6. Keep routing and hand-off evidence provider-neutral. Model and judge text remains explicitly
   nondeterministic, while topology, policy, schemas, budgets and reducer transitions remain
   deterministic configuration and state evidence.

## Consequences

- Restart, cancellation, retry and provider-failure behavior use the existing task-run fencing,
  session checkpoint and primitive invocation journals; no mesh-specific recovery store is needed.
- A route does not dynamically mutate the graph. Router flows declare candidate sessions in advance
  and use ordinary `dependsOn` plus `runIf` expressions against the route decision.
- Hand-off schema validity does not prove semantic truth. Evaluation and human release controls stay
  available on the destination session.
- Changing a provider creates new model-policy and agent revisions but does not change the
  `amesh.agent-mesh/v1`, `amesh.agent-route/v1` or `amesh.agent-handoff/v1` evidence shapes.

## Rejected alternatives

- **Opaque multi-agent loop inside one handler:** hides member progress, budgets and recovery from
  the reducer.
- **Runtime graph mutation:** complicates replay, authorization and restart without being required
  for the declared bounded topologies.
- **Separate mesh service and state store:** duplicates scheduling, cancellation, fencing, evidence
  and tenancy already owned by the execution engine.
