# The AMESH mental model

AMESH is a durable orchestration platform. It turns a declared flow into a versioned execution,
coordinates tasks, stores the evidence of what happened, and exposes the result through the web UI,
API, and CLI. An AI model can be one kind of task inside that flow, but AMESH is not just a prompt
runner and it does not treat model text as the source of truth.

## The five things to keep in mind

1. **A flow is the plan.** It describes inputs, variables, tasks, triggers, outputs, and policies.
2. **A revision is the contract.** A run is pinned to one flow revision and the exact resource and
   plugin revisions it resolved.
3. **An execution is the durable record.** It has a lifecycle, task attempts, outputs, artifacts,
   logs, and immutable events. A browser notification is only a view of that record.
4. **A task is the unit of work.** A task may run built-in logic, a process, a container, a plugin,
   a model call, or an agent session. The worker performs the task; the executor decides what is
   runnable next.
5. **Policy is a boundary.** Schemas, permissions, budgets, leases, approvals, and tenant checks
   are evaluated by AMESH. A task or model cannot widen its own authority.

The accepted architecture separates the webserver, compatibility façade, executor, scheduler,
workers, plugin supervisor, agent coordinator, storage, and identity/policy responsibilities. See
the [architecture overview](../architecture/README.md) for the service boundaries and the
[execution semantics](../architecture/execution-semantics.md) for the durable state machine.

## A run from start to finish

```text
author a flow or agent
        |
        v
validate and pin the revision, resources, policies, and schemas
        |
        v
create an execution with an idempotency key
        |
        v
executor admits ready tasks -> worker runs one task -> result is committed
        |                                             |
        +------------------ repeat -------------------+
        |
        v
terminal output, artifacts, logs, trace, and audit evidence
```

The important ordering is that state, immutable events, and outbound work are committed together.
Workers use leases and fencing, so an old worker cannot overwrite a newer attempt after a retry or
restart. Delivery is at-least-once; repeated delivery has one logical effect. External side effects
still need their own idempotency or compensation strategy. These guarantees are explained in
[execution semantics](../architecture/execution-semantics.md#guarantee-vocabulary).

## What the user sees

The web app gives guided resource and workflow authoring, execution and task traces, files and
artifacts, agent-session progress, and operational controls. The API is the automation surface, and
the CLI is useful for repeatable local or scripted work. They use the same contracts; the UI is not a
second execution engine.

For a first run, follow [onboarding](../operations/onboarding.md). For a complete local push gate,
see [local verification](../how-to/run-local-verification.md).

## Determinism: what is and is not fixed

AMESH makes configuration and orchestration decisions reproducible: the flow revision, resource
pins, schemas, conditions, dependency ordering, retries, approvals, and idempotency identities are
recorded. Replaying the same ordered event history gives the same canonical platform state.

Model output and arbitrary external services are not byte-deterministic. A provider may return
different text on two valid calls. AMESH therefore records provider and model provenance, usage,
cost, private continuation handles, validation results, and a nondeterminism disclosure. Structured
schemas make the boundary reliable without pretending that the model's reasoning is reproducible.
Read [flow validation and the DSL](../architecture/flow-dsl.md) and [agent primitive API](../api/agent-primitives.md)
for the exact contracts.

## Responsibility boundaries

| Concern | AMESH owns | The task, plugin, provider, or client owns |
|---|---|---|
| Workflow state | Revision pinning, scheduling, graph decisions, retries, leases, evidence | The implementation of its task result |
| Agent authority | Prompts/skills/tools/model pins, schemas, budgets, approvals, checkpoints | The model's proposed action or generated text |
| External tools | Allowlist, schema validation, impact policy, invocation journal | Connector-specific API behavior and destination idempotency |
| Secrets | References, scopes, redaction, and runtime injection | The external system's credential lifecycle |
| Large data | Governed artifact references, checksums, retention, and access | The producer's content and interpretation |

This is why a browser extension can keep exact browser automation commands in its own trusted
application while exposing only an approved high-level MCP tool to an AMESH session. AMESH governs
the call and records evidence; it is not the browser's command store.
