# Run local verification

AMESH has no executable GitHub Actions workflows. The supported merge gate runs locked Python and
Node dependencies in disposable Docker containers and writes release archives locally without
receiving repository credentials, GitHub credentials, OpenRouter credentials or a Docker socket.
Local `.env` and derived environment files are excluded from the verifier image build context.
Tests, builds and packaging run as the unprivileged `verifier` user (UID 10001); only image
construction installs system packages as root. Chromium is installed in a shared read-only browser
directory. PostgreSQL database creation and migration use the separate administrative test anchor;
restricted-role tests verify application RLS with a non-superuser database login. Compose runs the
single supplementary-group drop qualification in `root-runner-check` before the ordinary verifier;
that test is skipped only in the unprivileged main process.

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
`tool.coverage.report.fail_under` in `pyproject.toml`; the supported gate enforces `>=75%` and reports
the measured database-enabled result when it runs.

Strict mypy also checks every domain test, shared fixture and the root PostgreSQL fixture.
Wire-input validation tests use `model_validate` so intentionally invalid payloads remain
runtime checks without bypassing static checking of the surrounding test logic.

### PostgreSQL test isolation

`AMESH_TEST_DATABASE_URL` is an administrative anchor for tests, not a database that tests may use
as application state. The root pytest fixtures create a uniquely named database, apply the complete
migration plan, and drop that database after each requesting test. Repository and API tests should
request `migrated_test_database_url`, `isolated_postgres_database`, or the event-loop-bound
`postgres_async_engine` fixture instead of opening the configured URL directly. The suite still
collects when the variable is absent; only tests that request PostgreSQL state are skipped.

## Default backend skip inventory

The Linux verifier without external credentials or optional toolchains has these 22 skipped
cases (reconciled on 2026-09-08). Fourteen collection conditions and seven runtime tool/credential
checks identify the complete set. The gate prints skip reasons; PostgreSQL unavailability is a
failure, not an allowed skip. Supplying an opt-in prerequisite changes this list and requires its
separate qualification evidence. Compose rendering also runs in the host aggregate stage.

| Collected test case | Missing prerequisite or qualification |
| --- | --- |
| `tests/adapters/docker/test_container_runner.py::test_real_engine_enforces_output_limit_and_removes_container` | set AMESH_TEST_DOCKER=1 for the disposable Docker Engine profile |
| `tests/adapters/docker/test_container_runner.py::test_epic221_real_engine_archive_security_logs_cancellation_and_reconciliation` | set AMESH_TEST_DOCKER=1 for the disposable Docker Engine profile |
| `tests/adapters/kubernetes/test_job_runner.py::test_executor_job_survives_pod_deletion_on_kind` | AMESH_KIND_CONTEXT is required |
| `tests/adapters/kubernetes/test_job_runner.py::test_fresh_executor_reconciles_running_job_after_control_plane_loss` | AMESH_KIND_CONTEXT is required |
| `tests/adapters/kubernetes/test_job_runner.py::test_profiled_job_transfers_workspace_and_applies_network_policy_on_kind` | AMESH_KIND_CONTEXT is required |
| `tests/adapters/local/test_process_runner_contract.py::test_urs_f_0259_0262_windows_rejects_posix_only_controls` | Windows constraint qualification |
| `tests/adapters/local/test_process_runner_contract.py::test_local_runner_sets_primary_group_and_drops_supplementary_groups` | Requires root to exercise privilege dropping; covered by the separate `root-runner-check` Compose prerequisite. |
| `tests/adapters/postgres/test_disaster_recovery.py::test_backup_is_restored_reconciled_and_version_verified` | AMESH_TEST_DATABASE_URL and PostgreSQL client tools are required |
| `tests/e2e/test_agent_shell_http.py::test_api_runs_openrouter_shell_http_demo_on_kind` | kind and OpenRouter settings are required |
| `tests/llm/test_openrouter_pi_qualification.py::test_live_openrouter_pi_multimodal_qualification[openai/gpt-5.6-luna]` | OPENROUTER_API_KEY is required for the paid Pi multimodal qualification |
| `tests/llm/test_openrouter_pi_qualification.py::test_live_openrouter_pi_multimodal_qualification[deepseek/deepseek-v4-flash-vision-exp]` | OPENROUTER_API_KEY is required for the paid Pi multimodal qualification |
| `tests/llm/test_openrouter_pi_qualification.py::test_live_native_envelope_cache_pairs` | Paid frozen-scout comparison requires explicit session and provider credentials |
| `tests/sdk/test_python_execution_client.py::test_live_execution_conformance` | live endpoint not configured |
| `tests/storage/test_minio_integration.py::test_minio_stream_integrity_lifecycle_inventory_and_versioned_delete` | AMESH_TEST_S3_ENDPOINT is required for MinIO integration tests |
| `tests/tasks/test_agent_sessions.py::test_live_openrouter_luna_session_runs_through_pi` | OPENROUTER_API_KEY is required for live Pi session tests |
| `tests/llm/test_openrouter_smoke.py::test_openrouter_chat_completion_contract[openai/gpt-5.6-luna]` | No provider credentials in the default gate; explicit paid qualification is separate. |
| `tests/deployment/test_compose_structure.py::test_compose_manifests_render_after_shared_merges[compose.yaml-environment0]` | No Docker CLI in the verifier; the aggregate Compose stage covers rendering on the host. |
| `tests/deployment/test_compose_structure.py::test_compose_manifests_render_after_shared_merges[docker/compose.hardened.yaml-environment1]` | No Docker CLI in the verifier; the aggregate Compose stage covers rendering on the host. |
| `tests/deployment/test_compose_structure.py::test_compose_manifests_render_after_shared_merges[docker/compose.session-orchestrator.yaml-environment2]` | No Docker CLI in the verifier; the aggregate Compose stage covers rendering on the host. |
| `tests/deployment/test_compose_structure.py::test_compose_manifests_render_after_shared_merges[docker/compose.verify.yaml-environment3]` | No Docker CLI in the verifier; the aggregate Compose stage covers rendering on the host. |
| `tests/deployment/test_session_orchestrator_deployment.py::test_docker_compose_profile_renders_with_reference_only_inputs` | No Docker CLI in the verifier; the aggregate Compose stage covers rendering on the host. |
| `tests/deployment/test_session_orchestrator_deployment.py::test_helm_session_orchestrator_profile_renders_when_helm_is_available` | No Helm executable; use the separate Helm qualification. |

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

The following register is the authoritative list of specialist qualifications deliberately excluded
from `verify-local-all`. A missing result is a deferral, not a pass. On the review date, the accountable
repository role must either attach current evidence and close the deferral or record why it remains
deferred and set a new ISO `YYYY-MM-DD` review date.

| Deferred specialist gate | Why it is separate | Accountable repository role | Review date |
| --- | --- | --- | --- |
| Deterministic SDK regeneration with `uv run python scripts/generate_sdks.py --check` | The pinned generator and formatter images require host Docker access that the verifier container does not receive. | SDK maintainer | 2026-10-01 |
| Python, TypeScript, Java and Go SDK compilation plus live API conformance | The complete language toolchain matrix and a live AMESH endpoint are intentionally outside the common verifier image. | SDK maintainer | 2026-10-01 |
| PostgreSQL 15–18 qualification at the current migration head | The ordinary merge gate uses one PostgreSQL major; the four-major matrix requires separate disposable servers and retained reports. | PostgreSQL maintainer | 2026-10-01 |
| AWS RDS, Azure Flexible Server and Google Cloud SQL qualification | Credentialed provider reference environments are tracked under EPIC-706 and cannot run in the secret-free aggregate. | PostgreSQL maintainer | 2026-10-01 |
| Terraform/OpenTofu build, generated documentation and compatibility matrix | The Go, `tfplugindocs`, Terraform and OpenTofu toolchains remain outside the common verifier image. | Terraform provider maintainer | 2026-10-01 |
| Kubernetes runtime and cluster-compatibility qualification | A disposable cluster and Kubernetes toolchain are not part of the Docker-local aggregate. | Deployment maintainer | 2026-10-01 |
| Helm chart render, install and upgrade qualification | The Helm toolchain and disposable target cluster are not part of the Docker-local aggregate. | Deployment maintainer | 2026-10-01 |
| Paid OpenRouter provider and Pi session qualification | Provider credentials and billable calls are deliberately excluded from the default aggregate. | Model-provider maintainer | 2026-10-01 |
| Agent-session capacity reference qualification with `scripts/qualify_agent_session_service.py` | The 10,000-session, 1,000-reader reference profile is an opt-in local capacity measurement rather than a fast merge-gate workload. | Agent-session service maintainer | 2026-10-01 |
| Disposable Docker Engine container-runner profile with `AMESH_TEST_DOCKER=1` | The verifier container deliberately receives no Docker socket, so real image, archive, log, cancellation and cleanup tests require a separately controlled Engine. | Docker runner maintainer | 2026-10-01 |
| MinIO multipart, lifecycle, inventory and versioned-delete integration with `AMESH_TEST_S3_ENDPOINT` | The portable aggregate does not start or receive credentials for a MinIO service. | Object-storage maintainer | 2026-10-01 |
| Live S3, Azure Blob Storage and Google Cloud Storage provider certification | Credentialed managed-provider environments, private-network policy and outage drills remain EPIC-706 release qualifications. | Object-storage maintainer | 2026-10-01 |
| PostgreSQL logical backup/restore and reconciliation integration | The verifier image does not contain the required `pg_dump` and `pg_restore` client tools. | Disaster-recovery maintainer | 2026-10-01 |
| Kind + OpenRouter agent-shell HTTP end-to-end qualification | The journey requires both a live kind context and billable provider credentials, which the default aggregate does not receive. | Deployment maintainer | 2026-10-01 |

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
