# Current progress

- Current branch: `fix/epic-838-executor-decomposition`.
- Active work: EPIC-838 milestone 6 / GitHub issue #49 is implemented and qualified for
  publication. The executor compatibility facade delegates to bounded orchestration, attempt,
  condition, flowable, loop and lifecycle components without changing durable identities or public
  signatures.
- Completed immediately before this work: EPIC-838 milestone 5 / GitHub issue #48 and pull request
  #59 split API composition behind application-owned providers without OpenAPI drift.
- Next bounded work: EPIC-838 milestone 7 / GitHub issue #50, decomposing PostgreSQL persistence
  responsibilities behind the existing repository ports.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
