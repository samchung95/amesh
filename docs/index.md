# AMESH documentation

AMESH is a self-hosted orchestration platform for durable workflows and bounded agent sessions. Use
the control room for visual authoring and inspection, or use the REST API, CLI and generated SDKs
from another application.

## Start here

| I want to… | Go to… |
| --- | --- |
| Run AMESH locally and complete a first workflow | [Getting started](getting-started/index.md) |
| Understand flows, nodes, executions and artifacts | [Workflow concepts](concepts/workflows.md) |
| Configure agents, tools, budgets and structured output | [Agent concepts](concepts/agents.md) |
| Create, run and debug workflows | [Workflow guide](workflows/index.md) |
| Start and continue durable agent sessions | [Agent-session guide](agents/index.md) |
| Call AMESH from an application | [Integrations](integrations/index.md) |
| Add plugins, tools, MCP servers, models or harnesses | [Extensions](extensions/index.md) |
| Deploy, secure, observe or recover AMESH | [Operations](operations/index.md) |

## What AMESH owns

AMESH validates versioned definitions, persists execution state in PostgreSQL, stores governed files
and images through its object-storage boundary, dispatches work to configured runners, records safe
evidence, applies authorization and resumes durable work after interruption. Agent runs additionally
pin their prompt, skills, model policy, tools, output contract and session-harness protocol.

The platform does not make an LLM's wording deterministic. It makes the **boundary around the call**
repeatable and inspectable: exact inputs and revisions, hard budgets, permitted tools, output-schema
validation, idempotency, checkpoints and chronological evidence. External APIs and tools still own
their effects and failure behavior.

Read [How the platform fits together](concepts/platform.md) for the state and authority model, and
[Execution semantics](architecture/execution-semantics.md) for the deeper contract.

## Current qualification boundary

The checked-in development stack is for local evaluation. Production claims depend on the selected
deployment profile and its recorded qualification evidence. AMESH does not claim complete Kestra
compatibility, managed-cloud operation or deterministic model text. The operations guides keep those
limits next to the procedures they qualify.

The OpenAPI document, schemas, requirements, backlog and test evidence remain canonical generated or
repository artifacts; this site links to them instead of replacing them with prose.
