# Build workflows

A workflow is a versioned graph of typed tasks. Start visually for common nodes, switch to YAML when
you need the complete DSL, and inspect every run through the same execution trace.

## Author and validate

- [Create the first workflow](../getting-started/first-workflow.md)
- [Flow DSL and validation](../architecture/flow-dsl.md)
- [Expressions and available context](../architecture/expressions.md)
- [Discover installed node types and schemas](../reference/resource-catalog.md)
- [Typed inputs and outputs](../how-to/typed-flow-data.md)
- [Workflow metadata](../how-to/workflow-metadata.md)

## Compose work

- Sequential tasks use list order and dependencies; parallel DAG branches use explicit dependencies.
- Conditions, loops and nested flowables use the validated core control nodes.
- Subflows launch a pinned child flow and preserve parent/child trace links.
- Retries repeat a failed task under its declared policy; replay and backfill create governed new
  executions with source linkage rather than mutating history.

The checked-in runnable examples include
[`conditional-flowables.yaml`](https://github.com/samchung95/amesh/blob/main/examples/conditional-flowables.yaml),
[`loops.yaml`](https://github.com/samchung95/amesh/blob/main/examples/loops.yaml),
[`parallel-dag.yaml`](https://github.com/samchung95/amesh/blob/main/examples/parallel-dag.yaml) and
[`nested-flowables.yaml`](https://github.com/samchung95/amesh/blob/main/examples/nested-flowables.yaml).

## Data, files and model nodes

- [Run scripts](../how-to/run-scripts.md)
- [Extract a PDF artifact](../how-to/extract-pdf-artifact.md)
- [Route governed images](../how-to/route-governed-images-through-workflows.md)
- [Run a bounded structured-model task](../how-to/run-bounded-model-task.md)
- [Run a bounded agent session](../how-to/run-bounded-agent-session.md)

Files and images move through governed artifact references, not arbitrary local paths or durable base64
payloads. A node can call code, a provider or an approved tool only through its registered task and
runner boundary; YAML itself does not grant network, credential or host authority.

## Test and inspect

- [Deterministic simulations](../api/simulations.md)
- [Revision-pinned flow tests](../api/flow-tests.md)
- [Execution semantics](../architecture/execution-semantics.md)
- [Trigger operations](../operations/triggers.md)

The execution detail view is the primary place to answer what is running, which node is active, what
was retried, what result was produced and which child execution or artifact belongs to the run.
