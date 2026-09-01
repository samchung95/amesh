# Build and run agents

AMESH supports agents as versioned capabilities used inside workflows or as durable sessions exposed
directly to applications.

## Define the capability

1. Create immutable prompt, skill and model-policy revisions.
2. Register only the tools and MCP connections the agent may use.
3. Define input and output JSON Schemas plus hard budgets.
4. Publish an agent revision that pins every dependency.
5. Resolve and preview the effective envelope before executing it.

Follow [Define and pin an agent capability envelope](../how-to/define-agent-capability-envelope.md),
then read the [agent primitive API](../api/agent-primitives.md) for the exact resource shapes.

## Choose an execution surface

| Surface | Use it when… | Start with… |
| --- | --- | --- |
| `agent.llm` workflow task | One bounded structured model call is enough | [Structured-model task](../how-to/run-bounded-model-task.md) |
| `agent.session` workflow task | The node needs a multi-turn tool loop and durable evidence | [Bounded agent session](../how-to/run-bounded-agent-session.md) |
| Agent-session service | A chat or application owns the outer interaction | [First session](../getting-started/first-agent-session.md) |
| Agent mesh | A supervisor coordinates multiple pinned agents | [Agent mesh](../how-to/coordinate-agent-mesh.md) |

An agent model policy may select an isolated [subscription-backed model engine](../how-to/use-subscription-model-engine.md)
by `engineRef` and an explicit `engineScopes` delegation. The same provider-neutral task and
session contracts are used for direct HTTP providers and process engines.

## Inspect and control a session

The session service provides stable logical session IDs, idempotent starts and later turns,
chronological cursor-based progress, structured results, retry/cancel/pause/resume controls and
governed image inputs. Use the [CLI/API journey](../how-to/use-agent-session-service.md), the
[session API reference](../api/agent-session-service.md) and the
[progress and image contract](../reference/chronological-progress-and-image-inputs.md).

Operators manage fleet policy, quotas, retention and migration through the separate
[session administration workbench](../how-to/administer-agent-sessions.md). Application users cannot
acquire those instance-wide authorities merely by creating a session.
