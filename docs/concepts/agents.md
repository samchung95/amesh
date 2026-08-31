# Agents, sessions, and model work

AMESH supports both bounded model tasks and durable agent sessions. A model task is a single
workflow node that calls a provider and validates its response. An agent session adds a durable
checkpoint and a governed sequence of model proposals, tool calls, and final structured output.

The agent is allowed to decide *within* its envelope. AMESH remains responsible for the envelope,
the workflow graph, the tool calls, the budgets, and the durable result.

## The capability envelope

An agent definition is an immutable revision that references exact revisions of:

- a model policy and provider route;
- ordered prompts and skills;
- approved MCP or plugin tools;
- input and output JSON Schemas;
- memory and evaluation policies; and
- permissions, secret scopes, egress, filesystem roots, approvals, and hard limits.

Create and inspect these resources from the guided Agents UI or with the API/CLI. The end-to-end
[capability envelope guide](../how-to/define-agent-capability-envelope.md) shows the JSON shape. A
resolution produces a digest and pin; changing a dependency requires a new revision rather than
silently changing an existing run.

## Prompts, skills, and tools

A prompt is versioned instruction content with optional variables. A skill is reusable procedural
guidance and a declared capability request. A tool is an explicitly described operation with an
input/output schema and impact classification.

MCP tools are discovered from a pinned connection. AMESH checks the live schema before calling,
validates arguments, enforces `READ_ONLY`/write/approval policy, journals the invocation, and
redacts protected values. Plugins provide the same governed capability through the plugin contract.
The model cannot invent a new tool, grant its own approval, or call an undeclared endpoint. Read
[register an MCP connection](../how-to/register-mcp-connection.md) and [the ToolProvider guide](../how-to/implement-tool-provider.md).

## Model tuning and budgets

The model policy chooses the provider adapter, endpoint, model, required features, and parameters
such as temperature, top-p, and seed. The agent envelope sets hard ceilings for total tokens, turns,
loop iterations, tool calls, duration, cost, concurrency, and recursion. A node can further set its
timeout, retry, invalid-output policy, and data handling; the tightest applicable boundary wins.

The current shipped OpenAI-compatible route can target OpenRouter, including the qualified
`openai/gpt-5.6-luna` baseline. Provider credentials are referenced by secret scope and remain out
of flows, prompts, checkpoints, traces, and model representations. Usage and cost are normalized;
an unpriced or unavailable cost does not get guessed into a hard budget. See [add and qualify a model
provider](../how-to/add-model-provider.md).

## The session loop

One session turn asks the harness for one proposed action. The proposal is either a final structured
object or one authorized tool call. AMESH validates the proposal, dispatches the tool through its
durable journal, records the result, and then permits the next bounded turn. This can repeat up to
the envelope's limits; it is not an unrestricted autonomous process.

```text
input -> resolve exact envelope -> model proposal
                              |
              +---------------+----------------+
              |                                |
       authorized tool                  structured final result
              |                                |
       policy + schema + journal          output schema + assertions
              |                                |
              +---------- next bounded turn
```

The harness is replaceable infrastructure behind the `AgentSessionHarness` port. Pi is the current
explicit adapter, but a conformant future adapter must use the AMESH model gateway and must not own
workflow state, credentials, authoritative transcripts, or undeclared tool execution. See the
[harness contract](../plugin-sdk/agent-session-harness.md).

## Context, continuation, and compaction

Large or private session state is kept in a bounded checkpoint and provider continuation boundary,
not copied into the public trace. The provider adapter may preserve opaque encrypted continuation
state; public evidence exposes only an invocation handle, provider pin, and token digest. When the
session continues, AMESH loads the stored checkpoint and exact pins, then starts the next durable
turn.

Compaction is therefore a governed context-boundary concern: the session has bounded context,
turn, token, cost, tool, and duration limits, and the public projection is intentionally smaller
than private model state. Hidden reasoning, raw prompts/messages, credentials, and oversized payloads
are not public result data. This preserves inspectability without claiming that hidden reasoning is a
replayable artifact.

## Cache and structured results

Task-result caching is opt-in and belongs to the runnable task boundary. A cache key includes the
tenant/security context, pinned revision, configuration, selected context, and code/plugin version.
Each execution still records a task attempt and whether it was a hit, miss, expiry, invalidation,
bypass, or refresh. Read [task cache operations](../operations/task-cache.md) for administration and
evidence.

Agent output is accepted only after parsing and validating the pinned Draft 2020-12 output schema,
plus any business assertions or deterministic evaluation policy. A judge may add evaluation evidence
but cannot override a deterministic failure or grant tool/release authority. A valid structured
result is reliable at the boundary; it is not proof that the model text or reasoning was identical
across calls.

## Progress and images

Session progress is a chronological, cursor-based projection of safe model, tool, approval,
validation, artifact, and terminal observations. It deliberately omits hidden reasoning and private
checkpoints. Use the [session service guide](../how-to/use-agent-session-service.md) to create a
session, watch progress, continue a session, and retrieve the terminal result.

Images use the same governed artifact boundary as workflows. A caller can attach an image at
ingestion or at a later session turn when the pinned route and input schema allow it. AMESH stores a
reference, checksum, and metadata—not an unbounded inline data URL—and authorizes access before the
provider call. The workflow-wide image journey is documented in [route a governed image](../how-to/route-governed-images-through-workflows.md).

## What an agent cannot do

An agent cannot change its own envelope, exceed its hard limits, read undeclared secrets or files,
call an undeclared tool, approve a high-impact operation, write authoritative workflow state, or
silently repeat an ambiguous external effect after restart. If a tool can trade, publish, delete, or
otherwise cause a consequential side effect, put the approval and destination idempotency boundary
in the workflow and tool contract—not in a hopeful prompt.
