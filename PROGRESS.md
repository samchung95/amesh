# Current progress

- Current branch: `refactor/epic-837-feature-package-boundaries`.
- Active work: EPIC-837 milestone 10 / GitHub issue #30. Kestra compatibility and executable process
  entry points now have explicit feature packages with legacy identity aliases, verified import cycles
  are removed, and non-default Docker and Compose assets live under `docker/` with their command
  contracts updated atomically.
- Completed immediately before this work: EPIC-837 milestones 1–9 through pull request #39.
- Next bounded work: EPIC-837 milestone 11 / GitHub issue #31, followed by final reconciliation and
  closure of parent issue #19.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
