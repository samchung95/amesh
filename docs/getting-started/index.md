# Getting started

This path starts the development stack, signs in to the control room and runs the built-in deterministic
workflow. It does not require an LLM key.

## Prerequisites

- Git
- Docker with Compose v2
- 4 GiB of available memory for the development minimum
- [uv](https://docs.astral.sh/uv/) only if you also want to use the CLI or run local checks

## 1. Create the local environment

From the repository root, copy the example environment file:

PowerShell:

```powershell
Copy-Item .env.example .env
```

Shell:

```sh
cp .env.example .env
```

The sample `OPENROUTER_API_KEY` value is not needed for the first workflow. Replace it before a live
model or agent run. Never commit the populated `.env` file.

## 2. Start AMESH

```console
docker compose up -d --build
docker compose ps
```

Wait until readiness succeeds:

```console
curl http://localhost:8000/ready
```

PowerShell users can use `Invoke-RestMethod http://localhost:8000/ready`.

Open [http://localhost:8000](http://localhost:8000). Choose **API token**, enter
`development-token`, and keep tenant `default`. These are development credentials, not a shipped
username and password. The default Compose stack is development-only and should not be exposed as a
production service.

## 3. Run the first workflow

Follow [Create and inspect your first workflow](first-workflow.md). It uses only `core.log` and
`core.return`, so a successful run proves the API, database, executor and control-room path without
calling an external provider.

## 4. Choose your next journey

- [Start your first agent session](first-agent-session.md) when you have an OpenRouter key.
- [Learn the platform model](../concepts/platform.md) before designing a larger system.
- [Build workflows](../workflows/index.md) for branches, loops, subflows, files and images.
- [Integrate an application](../integrations/index.md) through REST, CLI or a generated SDK.
- [Choose a deployment profile](../operations/index.md) before operating beyond local development.

## Stop the stack

```console
docker compose down
```

This stops containers and retains named-volume data. Removing volumes is a separate destructive
operation and is not part of the normal cleanup path.

If startup or readiness fails, use the [first-run readiness guide](../operations/onboarding.md) and
then the runbook named by the failing readiness card.
