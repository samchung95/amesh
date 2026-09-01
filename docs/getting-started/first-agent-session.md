# Start your first agent session

An agent session runs an immutable agent revision inside a durable, bounded harness. The agent revision
owns its system prompt, skills, model route, tools, budgets and structured-output schema; a workflow
or client supplies only the permitted input.

## Before the live run

1. Put a real `OPENROUTER_API_KEY` in `.env` before starting the Compose stack.
2. Run `uv sync --extra runtime` in the repository checkout so the `amesh` CLI is available.
3. Create and pin the sample model policy, prompt, skill and `incident-helper` agent by following
   [Define an agent capability envelope](../how-to/define-agent-capability-envelope.md).
4. Use **Workflows → Create workflow → AI / model task** to preview the resolved envelope and run
   **Test agent node (isolated)**. That test validates the node with fixtures and calls neither the
   model nor tools, so it is the provider-free preflight.

## Run through a workflow

Apply the checked-in `examples/bounded-agent-session.yaml` flow and launch it as described in
[Run a bounded agent session](../how-to/run-bounded-agent-session.md). Its `agent.session` task pins
`incident-helper@1`, applies a 120-second timeout, limits repair attempts and accepts only output that
passes the configured schema and assertions.

Open the execution and select the agent task. The chronological trace separates model activity, tool
activity, validation and terminal status. It deliberately exposes safe summaries—not hidden reasoning,
raw prompts, credentials or private checkpoint state.

## Run as a session service

Applications that do not need a workflow wrapper can create the same exact agent revision through the
session service:

```console
uv run amesh session create agents.demo incident-helper --agent-revision 1 --input-json '{"incident":"API latency exceeded the objective for eight minutes."}' --idempotency-key incident-demo-001 --prefer-async
```

Save the returned `sessionId`, then inspect it:

```console
uv run amesh session watch <session-id>
uv run amesh session result <session-id>
```

Use a new idempotency key with the canonical message endpoint for a later turn under the same logical
session. See [Start and inspect an agent session](../how-to/use-agent-session-service.md) for the exact
request, image-input and reconnect examples.

## Tune the boundary, not each request

Reasoning effort, model sampling, token/cost/time/turn/tool-call ceilings, allowed tools, context
compaction and the final output schema belong to versioned resources and policies. That keeps clients
from silently changing execution authority. See [Agent concepts](../concepts/agents.md) for where each
setting lives.
