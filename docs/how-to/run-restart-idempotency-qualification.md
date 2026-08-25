# Run the restart and idempotency qualification

Use this guide to run the EPIC-816 qualification against a disposable PostgreSQL database and a
local content-addressed blob directory.

## Requirements

- Python 3.12 or newer with `uv` installed.
- A reachable PostgreSQL 15+ server where the configured user can create and drop databases.
- The repository's runtime dependencies installed with `uv sync --extra runtime --extra dev`.

The database URL is an administrative anchor only. The harness creates a uniquely named
`amesh_test_<random>` database, applies the repository migrations there, and drops that database
in a `finally` block. It never writes qualification rows to the database named in the URL.

## Run the qualification

Start the isolated PostgreSQL service from the local Compose profile, then run:

```powershell
$env:AMESH_TEST_DATABASE_URL = "postgresql+asyncpg://amesh:amesh@localhost:5432/amesh"
uv run python scripts/qualify_restart_idempotency.py `
  --output build/epic-816-qualification.json
```

The command prints the same machine-readable report that it writes to
`build/epic-816-qualification.json`. It exits `0` only when every supported matrix scenario and
the large-payload checks pass. Use `--payload-bytes` and `--max-inline-bytes` to qualify another
bounded payload size; the payload must be larger than the inline limit. Use `--object-store-root`
to retain local blobs for operator inspection; without it, the temporary blob directory is removed
after the report is produced.

For a fast rerun with an explicit 128 KiB payload:

```powershell
$env:AMESH_TEST_DATABASE_URL = "postgresql+asyncpg://amesh:amesh@localhost:5432/amesh"
uv run python scripts/qualify_restart_idempotency.py `
  --payload-bytes 131072 `
  --output build/epic-816-qualification.json
```

## Report interpretation

The report schema is `amesh.restart-qualification/v1`. `matrix.scenarios` contains the supported
before/after restart cases for API, scheduler, executor, worker, model, tool and evidence
boundaries. Each case records its stable operation identity, accepted-record count, external-call
count, result-reuse outcome and stale-fence assertion. Model/tool calls that are interrupted after
external I/O end as `AMBIGUOUS_EXTERNAL_OUTCOME` and are not repeated.

`largePayload` records the payload size, inline limit, content digest, external blob digest and
corruption-detection result. `assertions` is the operator-facing summary: a passing report requires
zero lost accepted records, zero duplicate logical decisions, stale completion rejection, no
repeated ambiguous external calls and equal repeated evidence digests.

If the worktree contains a concurrent EPIC-812 migration 0061 that has not yet been added to the
canonical migration manifest, the harness stages that existing SQL file in a temporary migration
directory for this run. It does not edit `migrations/`, the manifest or any production schema file.
