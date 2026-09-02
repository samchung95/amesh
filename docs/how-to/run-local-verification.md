# Run local verification

AMESH has no executable GitHub Actions workflows. The supported merge gate runs locked Python and
Node dependencies in disposable Docker containers and writes release archives locally without
receiving repository credentials, GitHub credentials, OpenRouter credentials or a Docker socket.
Local `.env` and derived environment files are excluded from the verifier image build context.

## Enable the local push gate

Enable the tracked pre-push hook once in each clone on POSIX systems:

```bash
make install-git-hooks
```

Enable the same hook from Windows PowerShell:

```powershell
.\scripts\install-git-hooks.ps1
```

The installer sets only this clone's `core.hooksPath` to `.githooks`. It refuses to replace a
different configured hooks directory. Confirm the active path with:

```bash
git config --local --get core.hooksPath
```

After installation, every ordinary `git push` runs the complete aggregate below and aborts before
the remote update when Docker verification fails. Git hooks are a workstation guard rather than a
remote trust boundary: `git push --no-verify` bypasses `pre-push`, and a clone owner can change local
Git configuration. Enforcing the gate against deliberate bypass requires a server-side receive hook
or a protected-branch status check; AMESH does not add one while hosted CI is intentionally disabled.

Run the complete supported gate on POSIX systems:

```bash
make verify-local-all
```

Run the same gate from Windows PowerShell:

```powershell
.\scripts\verify-local.ps1 -Suite all
```

The aggregate runs Python formatting, frontend lint, the core verifier, the strict documentation
build and browser journeys, validates all checked-in Compose profiles, builds and probes the
production image, and creates repository and SDK archives under `dist/local-release/`. It does not
publish, sign, attest or upload those artifacts.

## Core and focused suites

The core verifier is available directly when `make` or PowerShell is unavailable:

```bash
docker compose -f docker/compose.verify.yaml run --rm --build verify all
```

| Suite | Make | PowerShell | What it runs |
| --- | --- | --- | --- |
| Core aggregate | `make verify-local` | `.\scripts\verify-local.ps1 -Suite core` | Python format, frontend lint, backend, frontend, Pi harness, contracts, review regressions and documentation |
| Backend | `make verify-local-backend` | `.\scripts\verify-local.ps1 -Suite backend` | Ruff lint, strict mypy, the complete pytest suite and the enforced coverage floor |
| Frontend | `make verify-local-frontend` | `.\scripts\verify-local.ps1 -Suite frontend` | Unit tests, production build and the Chromium agent-session lifecycle/accessibility journey |
| Harness | `make verify-local-harness` | `.\scripts\verify-local.ps1 -Suite harness` | Pi tests and two byte-identical conformance reports |
| Contracts | `make verify-local-contracts` | `.\scripts\verify-local.ps1 -Suite contracts` | Planning drift, backlog, clean-room, REUSE, SDK generation-integrity receipt, generated contracts and compilation |
| Review regressions | `make verify-local-review` | `.\scripts\verify-local.ps1 -Suite review` | PostgreSQL-backed retry-identity, execution-deadline and authorization-before-quota tests |
| Documentation | `make verify-local-docs` | `.\scripts\verify-local.ps1 -Suite docs` | Strict MkDocs build plus desktop/tablet Playwright search and axe journeys |
| Compose | `make verify-local-compose` | `.\scripts\verify-local.ps1 -Suite compose` | Default, model-engine overlay, compact, verifier, docs, hardened and session-orchestrator Compose configuration |
| Image | `make verify-local-image` | `.\scripts\verify-local.ps1 -Suite image` | Production/Pi probe plus the secret-free pinned model-engine image, runtime identity and state-directory probe |
| Package | `make verify-local-package` | `.\scripts\verify-local.ps1 -Suite package` | Repository and four SDK archives under `dist/local-release/` |
| Live OpenRouter (opt-in) | `make verify-local-live-openrouter` | `.\scripts\verify-local.ps1 -Suite live-openrouter` | Paid Luna and DeepSeek provider smoke plus Pi multimodal/session qualification |

The backend suite does not deselect tracked tests. Coverage is enforced through
`tool.coverage.report.fail_under` in `pyproject.toml`, currently set to 65% against a measured 65.61%
repository baseline, so future regressions fail the aggregate while coverage can be ratcheted upward
deliberately.

### PostgreSQL test isolation

`AMESH_TEST_DATABASE_URL` is an administrative anchor for tests, not a database that tests may use
as application state. The root pytest fixtures create a uniquely named database, apply the complete
migration plan, and drop that database after each requesting test. Repository and API tests should
request `migrated_test_database_url`, `isolated_postgres_database`, or the event-loop-bound
`postgres_async_engine` fixture instead of opening the configured URL directly. The suite still
collects when the variable is absent; only tests that request PostgreSQL state are skipped.

## Focused gates and specialist qualification

Repository-wide Python formatting and frontend lint run first in the aggregate and remain available
as focused suites:

```bash
make verify-local-format
make verify-local-frontend-lint
```

```powershell
.\scripts\verify-local.ps1 -Suite format
.\scripts\verify-local.ps1 -Suite frontend-lint
```

The contracts suite verifies a SHA-256 receipt over the OpenAPI contract, pinned generator script,
SDK templates, license and complete checked-in SDK output tree. This detects contract, generator,
template and manual output drift without exposing the host Docker socket to the verifier container.
Full regeneration remains the host-only `uv run python scripts/generate_sdks.py --check` specialist
qualification. The PostgreSQL 15–18 matrix, generated Terraform-provider documentation,
every-language live SDK matrix and other specialist toolchain/environment gates also remain separate
qualifications when their required environments are available; they are not represented by a hosted
green check.

## Run the opt-in live OpenRouter suite

The default aggregate does not receive provider credentials or spend provider credits. To run the
separate Docker qualification on POSIX, provide the key explicitly:

```bash
OPENROUTER_API_KEY="..." make verify-local-live-openrouter
```

From Windows PowerShell:

```powershell
$env:OPENROUTER_API_KEY = "..."
.\scripts\verify-local.ps1 -Suite live-openrouter
```

The suite defaults both `OPENROUTER_TEST_MODELS` and `OPENROUTER_QUALIFICATION_MODELS` to
`openai/gpt-5.6-luna,deepseek/deepseek-v4-flash-vision-exp`; set either variable before invoking the
command to override that model set. It runs the direct provider smoke and the Pi multimodal
structured-session qualification, including image input, safe progress chronology, normalized
usage/cost/cache evidence, context receipt v3, and restart/reuse behavior.

The OpenRouter key is available to the AMESH parent test container but is not passed to the isolated
Pi worker. A missing key fails the specialist suite immediately. JUnit results are written to
`.artifacts/live-openrouter/junit.xml`. Because this suite is paid and opt-in, `verify-local-all` does
not invoke it.

## Release artifacts

Create archives without rerunning the rest of the aggregate:

```bash
make verify-local-package
```

```powershell
.\scripts\verify-local.ps1 -Suite package
```

Checksums are written beside the archives under `dist/local-release/repository/` and
`dist/local-release/sdk/`. Publication, signing, provenance attestation and GitHub Release creation
remain deliberate operator actions.
