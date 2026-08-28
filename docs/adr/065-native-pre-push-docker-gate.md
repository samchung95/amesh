# ADR-065: Gate ordinary pushes with the native Docker pre-push hook

Status: accepted

Context: AMESH already has one supported Docker-local merge gate, with equivalent Make and Windows
PowerShell entry points. Running it manually does not prevent a contributor from accidentally
pushing an unverified change. The product owner still does not authorize GitHub Actions or another
hosted CI service.

Decision: track a native Git `pre-push` hook under `.githooks/` and provide explicit POSIX and
PowerShell installers that set the clone-local `core.hooksPath` to that directory. On POSIX the hook
runs `make verify-local-all`; under Git for Windows, MSYS or Cygwin it runs
`scripts/verify-local.ps1 -Suite all`. The existing commands remain the only owners of the Docker
verification sequence, and any non-zero result is returned to Git so the push is aborted.

Use Git's built-in hook mechanism instead of adding pre-commit or Lefthook. Those frameworks support
pre-push stages, but AMESH needs one repository-local command rather than dependency installation,
file filtering or multi-hook orchestration. Native Git already supports a configurable hooks path
and defines a non-zero `pre-push` result as a push rejection.

Alternatives: copying a hook into `.git/hooks/` would leave clones with stale untracked copies;
duplicating every Docker command in the hook would create a second verification definition; adding a
hook-manager package or binary would increase bootstrap and upgrade surface without changing the
local enforcement boundary.

Consequences: after the one-time clone-local installer runs, every ordinary `git push` executes the
complete Docker gate before any remote ref is updated. Docker must be available, and POSIX
contributors also need Make while Git for Windows contributors need PowerShell. The gate can take
several minutes because it intentionally includes the production-image probe and local package
build.

This is a developer guard, not a remote trust boundary. Git explicitly permits `git push
--no-verify`, and a user who controls a clone can change its hook configuration. An unbypassable
repository rule therefore still requires a server-side receive hook or protected-branch status check;
neither is introduced while hosted CI remains out of scope.

References:

- Git hooks and `pre-push`: https://git-scm.com/docs/githooks
- Git `core.hooksPath`: https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath
- Git push verification bypass: https://git-scm.com/docs/git-push#Documentation/git-push.txt---no-verify
- pre-commit installation and pre-push stages: https://pre-commit.com/
- Lefthook installation and pre-push jobs: https://github.com/evilmartians/lefthook
