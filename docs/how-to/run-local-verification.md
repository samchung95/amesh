# Run local verification

AMESH has no executable GitHub Actions workflows. The supported merge gate runs locked Python and
Node dependencies in disposable Docker containers and writes release archives locally without
receiving repository credentials, GitHub credentials, OpenRouter credentials or a Docker socket.
Local `.env` and derived environment files are excluded from the verifier image build context.

Run the complete supported gate on POSIX systems:

```bash
make verify-local-all
```

Run the same gate from Windows PowerShell:

```powershell
.\scripts\verify-local.ps1 -Suite all
```

The aggregate runs the core verifier, validates all four Compose profiles, builds and probes the
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
| Frontend | `make verify-local-frontend` | `.\scripts\verify-local.ps1 -Suite frontend` | Unit tests and production build |
| Harness | `make verify-local-harness` | `.\scripts\verify-local.ps1 -Suite harness` | Pi tests and two byte-identical conformance reports |
| Contracts | `make verify-local-contracts` | `.\scripts\verify-local.ps1 -Suite contracts` | Planning drift, backlog, clean-room, REUSE, generated contracts and compilation |
| Review regressions | `make verify-local-review` | `.\scripts\verify-local.ps1 -Suite review` | PostgreSQL-backed retry-identity and authorization-before-quota tests |
| Compose | `make verify-local-compose` | `.\scripts\verify-local.ps1 -Suite compose` | Default, compact, verifier and hardened Compose configuration |
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
