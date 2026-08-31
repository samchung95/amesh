# Create and inspect your first workflow

The built-in **Hello, workflow** blueprint creates a validated unsaved draft before anything is
persisted or executed.

## Use the control room

1. Sign in at `http://localhost:8000` with API token `development-token` and tenant `default`.
2. Open **Blueprints** and select **Hello, workflow**.
3. Select **Open unsaved draft**. Review the visual definition or its YAML.
4. Select **Save revision**. AMESH validates the definition and stores an immutable revision.
5. Open the saved flow, select **Execute**, keep the default `name` input, review the request and
   confirm it.
6. Open **Executions**, select the new run and follow the simple trace from `greet` to `done`.

The final task returns the workflow result. The execution page keeps the flow revision, state,
task attempts, logs, inputs, output and evidence together; failures remain attached to the exact task
attempt that produced them.

## Use the CLI instead

Install the locked runtime and development environment once:

```console
uv sync --extra runtime --extra dev
```

Apply and launch the same checked-in example:

```console
uv run --extra runtime python -m amesh --token development-token --tenant default apply examples/hello-world.yaml
uv run --extra runtime python -m amesh --token development-token --tenant default run examples.getting_started hello_world
```

The `run` command prints the execution identity. Open **Executions** in the control room to inspect
the same durable run. For CLI profiles, result lookup and execution controls, continue with the
[CLI guide](../cli/README.md).

## What the workflow contains

The YAML has a stable flow ID and namespace, one typed input, two ordered tasks and one output. Task
IDs become keys in the `outputs` expression context. See [Workflow concepts](../concepts/workflows.md)
for the full node model and [Flow DSL](../architecture/flow-dsl.md) for the validated contract.
