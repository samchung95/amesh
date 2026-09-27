# ADR-082: Run a lightweight sanity check in hosted CI

Status: accepted. Supersedes the check scope, triggers and required checks of
[ADR-080](080-minimal-hosted-ci-mirroring-docker-local-gate.md). ADR-080's credential,
publication and protected-branch rules still apply.

Context: ADR-080's workflow ran the complete Docker-local core verifier, the Compose checks and the
image probes. Each pull request took about 35 minutes of runner time, and each merge ran the same
again on `main`. On 2026-09-27 the product owner asked for a high-level sanity check that uses
little GitHub Actions time. The complete gate already runs before every push through the tracked
pre-push hook (ADR-065). Duplicate runs also blocked stacked pull requests (#133).

Decision:

- `.github/workflows/ci.yml` has one job, `sanity`, triggered by pull requests, pushes to `main` and
  manual dispatch. The `main` run tests the merged result, which a pull request run does not
  guarantee: the protected branch does not require pull requests to be up to date, and an
  administrator can push directly. It also saves the dependency cache that new pull requests
  restore, because GitHub does not share caches between pull requests.
- The job runs `scripts/ci-sanity.sh` natively on the runner, with cached uv and npm dependencies
  and no Docker build. The script runs:
  - Ruff lint, Ruff format check and strict mypy with the same arguments as the local gate
  - a fast pytest subset: domain, DSL, expressions, policy, workflow, scheduler, storage, API,
    application, tasks and model providers, plus the generated SDK contracts, documentation and
    deployment checks. No PostgreSQL service runs, so tests that need one skip.
  - frontend lint, unit tests and production build
- The local gate still owns everything else: PostgreSQL suites, coverage floors, timing-bound and
  process-heavy tests, the 5,000-line p95 budget, Compose and image probes, harness conformance,
  contracts and SDK regeneration, review regressions, strict docs and browser journeys. The
  `AMESH_TEST_PERF_BUDGET_SCALE` passthrough stays for slower local hosts.
- Protected branch: `main` requires the `sanity` check instead of `verify` and `image`. The other
  ADR-080 rules are unchanged.
- Concurrency: a newer push to a pull request cancels its older run. If one push starts two runs
  for the same commit (as happens with stacked pull requests), GitHub can count the cancelled run
  against the required check. Re-run it with `gh run rerun <run-id>`; do not merge with `--admin`.

Alternatives: keeping the ADR-080 mirror spends about 70 runner minutes per pull request, including
the `main` run, to repeat checks the pre-push hook already ran. Requiring pull requests to be up to
date with `main` would also test the merged result, but it forces a re-run and a branch update on
every stacked pull request, and it does not cover direct administrator pushes. Removing hosted CI
again would bring back the bypassable, unobservable gate that #102 fixed. Queueing duplicate runs
instead of cancelling them would stop the stacked-PR block, but would also keep runs for superseded
pushes.

Consequences: a green `sanity` check shows that the change lints, type-checks, passes the fast
tests and builds. It does not show that the complete gate passed. The pre-push hook stays the full
verification, and `--no-verify` still skips it. A failing `main` run blocks nothing; it tells the
owner to fix `main`. Measured in a clean container with a cold cache, the script takes about 2.5
minutes, so a pull request costs about 5 runner minutes including its `main` run. The hosted runner
has Docker and Helm, so the Docker- and Helm-gated deployment tests that skipped in that container
run there.
