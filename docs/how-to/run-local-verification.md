# Run local verification

AMESH does not run GitHub Actions. The release-quality core gate runs in a disposable local Docker
image with locked Python and Node dependencies:

```bash
make verify-local
```

The same command works without `make`:

```bash
docker compose -f compose.verify.yaml run --rm verify all
```

The image runs Ruff lint, strict mypy, the backend suite with a coverage report, frontend unit tests and production
build, Pi tests, the agent-harness conformance report twice with byte comparison, planning and
backlog validation, clean-room and license checks, generated-contract tests and Python compilation.
It does not receive GitHub credentials, repository credentials,
OpenRouter credentials or a Docker socket.

Use a narrower suite while developing:

```bash
make verify-local-backend
make verify-local-frontend
make verify-local-harness
make verify-local-contracts
```

Validate deployment files and the exact production image separately, or run all three gates:

```bash
make verify-local-compose
make verify-local-image
make verify-local-all
```

The backend suite explicitly deselects four board-tracked baselines: the 50 ms deadline timing
assertion (`c15`), process-global storage metric registration (`c29`), the load-sensitive 5,000-line
performance threshold (`c89`) and the Windows event-loop-sensitive plugin registry test (`c120`).
Each remains visible rather than being reported as a passing release check. Repository-wide Python
formatting drift remains tracked separately on `c90`; the repository-wide branch/function coverage
threshold remains tracked on `c94`. Neither baseline is represented as a passing gate. Deterministic SDK
regeneration (which uses the pinned generator container), the full database-version
matrix, generated provider documentation and every-language live SDK matrix remain on the deferred
local-specialist card (`c110`); they are not represented by a hosted green check.

Release archive creation remains an explicit local operator action:

```bash
make package
uv run python scripts/package_sdks.py --output-dir dist/sdk
```

There is intentionally no automatic publication, signing, provenance attestation or GitHub Release
creation.
