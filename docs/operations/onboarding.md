# First local workflow

The reference path is designed to reach one successful local execution in less than 20 minutes after
container images are available. It sends no onboarding telemetry.

## Start the reference stack

From the repository root:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Wait until `api`, `executor`, `scheduler`, `indexer` and `postgres` report healthy. Open
`http://localhost:8000`, choose **API token**, enter `development-token`, and keep tenant `default`.
The development token is deliberately disabled outside the development profile.

## Create and run the sample

1. Open **Blueprints** and select **Hello, workflow**.
2. Keep namespace `examples.getting_started`, choose a unique Flow ID, and select **Open unsaved
   draft**. This step validates the draft but does not save or run anything.
3. Review the visual or YAML definition and select **Save**.
4. Open the saved flow, select **Execute**, keep the default name, review the request, and confirm.
5. Open the resulting execution and verify `SUCCESS` and the returned greeting.

The equivalent local CLI sample is:

```powershell
uv run --extra runtime python -m amesh --token development-token --tenant default apply examples/hello-world.yaml
uv run --extra runtime python -m amesh --token development-token --tenant default run examples.getting_started hello_world
```

## Use the setup guide

Open **Blueprints → Setup guide**. The live readiness cards report:

- PostgreSQL readiness and applied migrations;
- the configured object-storage backend;
- availability of the local execution runner;
- at least one interactive authentication provider.

The four onboarding checkboxes are scoped to the active tenant and principal and stored only in
browser local storage. Reloading retains them; clearing site data resets them. No analytics or
completion request is emitted.

Use **Blueprints → Playground** for expressions or YAML fragments. Its result explicitly confirms
that the request was not persisted or executed and had no credential or infrastructure access.

If a readiness card is not ready, use the linked subsystem runbook: [PostgreSQL](postgresql.md),
[object storage](object-storage.md), [local runner](local-process-runner.md), or
[authentication](authentication.md).
