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

The aggregate runs the core verifier, including the strict documentation build and browser journeys,
validates all checked-in Compose profiles, builds and probes the
production image, and creates repository and SDK archives under `dist/local-release/`. It does not
publish, sign, attest or upload those artifacts.

## Core and focused suites

The core verifier is available directly when `make` or PowerShell is unavailable:

```bash
docker compose -f compose.verify.yaml run --rm --build verify all
```

| Suite | Make | PowerShell | What it runs |
| --- | --- | --- | --- |
| Core aggregate | `make verify-local` | `.\scripts\verify-local.ps1 -Suite core` | Backend, frontend, Pi harness, contracts and current review regressions |
| Backend | `make verify-local-backend` | `.\scripts\verify-local.ps1 -Suite backend` | Ruff lint, strict mypy, pytest and coverage report |
| Frontend | `make verify-local-frontend` | `.\scripts\verify-local.ps1 -Suite frontend` | Unit tests, production build and the Chromium agent-session lifecycle/accessibility journey |
| Harness | `make verify-local-harness` | `.\scripts\verify-local.ps1 -Suite harness` | Pi tests and two byte-identical conformance reports |
| Contracts | `make verify-local-contracts` | `.\scripts\verify-local.ps1 -Suite contracts` | Planning drift, backlog, clean-room, REUSE, generated contracts and compilation |
| Review regressions | `make verify-local-review` | `.\scripts\verify-local.ps1 -Suite review` | PostgreSQL-backed retry-identity and authorization-before-quota tests |
| Documentation | `make verify-local-docs` | `.\scripts\verify-local.ps1 -Suite docs` | Strict MkDocs build plus desktop/tablet Playwright search and axe journeys |
| Compose | `make verify-local-compose` | `.\scripts\verify-local.ps1 -Suite compose` | Default, compact, verifier, docs, hardened and session-orchestrator Compose configuration |
| Image | `make verify-local-image` | `.\scripts\verify-local.ps1 -Suite image` | Production image build and Pi harness probe |
| Package | `make verify-local-package` | `.\scripts\verify-local.ps1 -Suite package` | Repository and four SDK archives under `dist/local-release/` |

The backend suite explicitly deselects four board-tracked baselines: the deadline timing assertion
(`c15`), process-global storage metric registration (`c29`), the load-sensitive 5,000-line validation
threshold (`c89`) and the event-loop-sensitive plugin registry test (`c120`). Each remains visible
instead of being reported as a passing release check.

## Diagnostic gates and specialist qualification

Repository-wide Python formatting and frontend lint are runnable as explicit diagnostics:

```bash
make verify-local-format
make verify-local-frontend-lint
```

```powershell
.\scripts\verify-local.ps1 -Suite format
.\scripts\verify-local.ps1 -Suite frontend-lint
```

Their existing repository-wide baselines are tracked on `c90` and `c88`, so they are not included in
the passing aggregate. The repository-wide branch/function coverage threshold remains tracked on
`c94`.

Deterministic SDK regeneration, the PostgreSQL 15–18 matrix, generated Terraform-provider
documentation, every-language live SDK matrix and other specialist toolchain/environment gates remain
on `c110`. Those qualifications are invoked separately when their required toolchains or environments
are available and are not represented by a hosted green check.

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
