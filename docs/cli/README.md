# CLI and generated clients

Install the cross-platform CLI from the repository with `uv`:

```console
uv tool install .
amesh --version
```

The default output is stable JSON. Use `--output human` for interactive summaries or
`--output quiet` for CI steps that only inspect the exit code. Exit codes are `0` for success,
`1` for a valid comparison or validation difference, `2` for usage/API/runtime errors, and `3`
when a destructive command requires an explicit `--force` acknowledgement.

## Profiles and credentials

Profiles store only the API URL and tenant. Tokens are stored through the operating-system
credential service; the CLI has no plaintext credential fallback.

```console
amesh config set local --api-url http://127.0.0.1:8000 --tenant default
amesh config use local
amesh auth token store --stdin
amesh auth token status
```

For non-interactive service accounts, set `AMESH_SERVICE_ACCOUNT_TOKEN`; it takes precedence over
the OS credential store. `AMESH_API_URL`, `AMESH_TENANT`, `AMESH_CONFIG_PATH`, and
`AMESH_OUTPUT` are also supported. `--token` remains available for compatibility but can be exposed
through process inspection, so CI should prefer the environment variable.

## Declarative and administrative workflows

Flow apply and diff accept a file or `-` for standard input. Export writes YAML by default and JSON
when the destination ends in `.json`.

```console
amesh flow apply flow.yaml
amesh flow diff flow.yaml
amesh flow export examples.cli hello exported.yaml
amesh flow delete examples.cli hello 2        # impact preview, exit 3
amesh flow delete examples.cli hello 2 --force

amesh admin configuration diagnostics
amesh admin tenants list
amesh admin tenants delete tenant-a           # impact preview, exit 3
amesh admin tenants delete tenant-a --force
```

Generate completions or the complete command reference directly from the parser model:

```console
amesh completion powershell
amesh command-docs docs/cli/reference.md
```

The generated reference is checked in at [reference.md](reference.md).

## Typed clients

Published Python, TypeScript, Java and Go source packages, compatibility metadata, and cursor
pagination helpers are under [`sdks/api`](../../sdks/api/README.md). Regenerate them from the
checked-in OpenAPI contract with:

```console
uv run python scripts/generate_sdks.py
uv run python scripts/generate_sdks.py --check
```
