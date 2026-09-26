# ADR-080: Mirror the Docker-local gate in minimal hosted CI

Status: accepted. Supersedes the hosted-automation exclusion in
[ADR-062](062-docker-local-verification-without-github-actions.md) and the "no protected-branch
status check" boundary in [ADR-065](065-native-pre-push-docker-gate.md). The Docker-local gate and
the tracked pre-push hook remain the developer workflow.

Context: the 2026-09-26 repository audit (GitHub #102) found that the only merge gate is a
workstation hook that `git push --no-verify` bypasses, that `main` has no remote evidence of passing,
and that the deployed image was built from a branch that was never pushed (#99). ADR-062 deferred
hosted automation until the product owner explicitly authorized it together with a decision on
credentials, protected branches and release provenance. On 2026-09-26 the product owner authorized
minimal CI and branch protection.

Decision:

- Add one workflow, `.github/workflows/ci.yml`, triggered by pull requests, pushes to `main` and
  manual dispatch. It calls only the existing Make entry points, so the Docker verification
  sequence keeps one owner: `make verify-local` and `make verify-local-compose` in the `verify` job,
  and `make verify-local-image` in the `image` job.
- Credentials: the workflow token is `contents: read`, checkout does not persist credentials, no
  repository secret is referenced, `pull_request_target` is not used and actions are pinned by
  commit SHA. Live OpenRouter and subscription-engine qualifications stay operator-invoked.
- Publication: CI never creates releases, uploads packages or images, signs, attests or deploys.
  `verify-local-package` stays local because it produces release-shaped archives. Publication and
  provenance remain separate manual operator actions as ADR-062 requires.
- Protected branch: `main` requires a pull request and the `verify` and `image` checks, and rejects
  force pushes and deletion. Zero approvals are required because GitHub does not let an author
  approve their own pull request; the independent-review evidence rules in `CONTRIBUTING.md` still
  apply. Administrator enforcement stays off so the sole maintainer can recover a broken `main`.

Alternatives: keeping verification local-only leaves the gate bypassable and unobservable; running
the full `verify-local-all` aggregate in CI would add release-shaped packaging with no merge value;
a self-hosted runner would execute untrusted public pull-request code on a workstation that has a
Docker Engine.

Consequences: every pull request and every commit on `main` has a remote pass/fail record from
GitHub-hosted runners at no cost for this public repository. Contributors should still run the
pre-push hook, which additionally builds local archives. Specialist matrices (Kubernetes, multiple
PostgreSQL versions, Terraform/OpenTofu, Helm and every SDK compiler) remain separately invoked
qualifications and are not implied by a green check.
