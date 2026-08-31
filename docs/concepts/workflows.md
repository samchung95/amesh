# Workflows and nodes

A workflow is a versioned graph of tasks. In the UI, each task is a node; in YAML or JSON, each node
is an item in `tasks`. A node has a type, an ID, configuration, dependencies, and—when relevant—an
input and output contract. AMESH validates that graph before a run is accepted.

## What belongs in a workflow

The canonical flow shape supports:

- inputs and defaults, static variables, labels, and annotations;
- tasks and their dependency edges;
- manual, webhook, interval, and cron triggers;
- terminal outputs rendered from the completed context;
- conditional, sequential, parallel, DAG, loop, subflow, error, finally, and after-execution
  control flow;
- file and artifact declarations, including governed images and document extraction; and
- retries, timeouts, concurrency, cache policy, approvals, and data-handling boundaries.

The [flow DSL guide](../architecture/flow-dsl.md) is the source for the document shape and validation
rules. The [typed flow data guide](../how-to/typed-flow-data.md) explains how declarations become the
same UI form and API schema.

## What a node can do today

The built-in catalog includes data parsing and serialization, file operations, HTTP, shell/process
work, logging, return/fail, notifications, approvals, PDF/document extraction, working directories,
control-flow nodes, subflows, and agent/model primitives. The effective
[resource catalog](../reference/resource-catalog.md) is the definitive list of registered types and
can also be extended by plugins.

An agent or model node can call a configured model, validate a structured response, propose or
invoke an approved tool, or run a bounded durable session. It does not receive unrestricted access
just because the prompt asks for it. See the [agent primitive reference](../api/agent-primitives.md).

## Code, APIs, and plugins

You do not have to write code for every node:

- Use a built-in task when its contract matches the job.
- Use `core.http` for an ordinary HTTP request, with explicit timeout, input, and output handling.
- Use process or shell tasks only within the configured runner and filesystem boundary.
- Use an MCP connection or a plugin ToolProvider when a capability should be discovered, versioned,
  schema-checked, and governed as an external tool.
- Implement an isolated plugin when the behavior belongs to a reusable connector, task, trigger,
  storage, runner, condition, notification, or expression extension.

The plugin runtime does not let connector code mutate orchestration state directly. Start with
[implement an isolated ToolProvider](../how-to/implement-tool-provider.md) or the
[plugin manifest contract](../plugin-sdk/manifest.md).

## How data moves between nodes

Inputs live under `inputs`, static flow variables under `vars`, task results under `outputs`, and
mutable key-value data in its own context. AMESH does not merge these namespaces. A downstream node
reads only the outputs of its declared dependencies and the values allowed by its contract.

Small JSON-safe values can be passed directly. Files and large payloads become governed artifact
references containing a tenant, version, media type, size, and checksum; task code receives a
materialized bounded workspace rather than object-storage credentials. For PDFs, use the
[document extraction guide](../how-to/extract-pdf-artifact.md).

Images are a base workflow capability, not an agent-only special case. Inline image bytes are
accepted only at ingestion, replaced with an immutable `amesh.image-ref/v1` artifact, and then
passed through branches, loops, subflows, or model tasks by reference. A governed image can be
provided at any node that declares an image-capable input. See [route a governed image](../how-to/route-governed-images-through-workflows.md).

## Control flow and execution

Dependencies and conditions determine when a node is ready. Sequential, parallel, and DAG nodes
preserve declared order while admitting independent work within their concurrency limits. `if` and
`switch` decisions are persisted before their selected descendants run; unselected descendants are
recorded as skipped. Loops and subflows are bounded by their declared limits and pinned revisions.

Retries create a new attempt while retaining previous evidence. Pause prevents new work; cancel
records an intervention and lets the configured lifecycle work finish; restart advances the
execution epoch so a stale worker cannot commit. Backfills and replay are durable, idempotent
controllers over ordinary executions, not a separate hidden execution engine. See
[execution semantics](../architecture/execution-semantics.md) for the exact lifecycle and
[execution controls](../operations/execution-checks.md) for operational checks.

## Making a workflow predictable

Validation catches unknown fields, bad types, duplicate IDs, missing dependencies, cycles, and
invalid resource configuration before execution. Pin the flow revision and dependencies, declare
schemas and budgets, and choose an external side-effect strategy for anything that can be repeated.
Task caching is opt-in: when enabled, the key includes the pinned revision, configuration, declared
inputs/context, code or plugin version, and security context. A cache hit still creates an ordinary
task attempt and evidence; it does not hide the run. See [task cache operations](../operations/task-cache.md).

The workflow graph is deterministic platform state. A model or external API remains an
explicitly nondeterministic boundary, so inspect its provenance and structured validation rather
than treating generated text as a replay guarantee.
