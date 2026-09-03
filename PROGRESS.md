# Current progress

- Current branch: `fix/epic-838-postgres-gate`.
- Active work: EPIC-838 milestone 3 / GitHub issue #46 is implemented and qualified for publication.
  The complete Docker-local backend gate now enables PostgreSQL fixtures, rejects missing-database
  skips, enforces at least 75% coverage and exercises substantive readiness, metrics, transaction
  discovery and non-mutating planning checks.
- Completed immediately before this work: EPIC-838 milestone 2 / GitHub issue #45 and pull request
  #56 made state, progress, trace propagation, redaction and determinism behavior substantive.
- Next bounded work: EPIC-838 milestone 4 / GitHub issue #47, making PostgreSQL administrative-role
  assumptions fail closed and qualifying tenant paths under restricted logins after milestone 3 merges.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
