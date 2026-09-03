# Current progress

- Current branch: `fix/epic-838-state-determinism`.
- Active work: EPIC-838 milestone 2 / GitHub issue #45 is implemented and qualified for publication.
  Typed reducer-owned transitions, incremental progress state, semantic redaction fields,
  application-level trace propagation, linear determinism analysis and simulator/executor handler
  parity now have focused unit and PostgreSQL coverage.
- Completed immediately before this work: EPIC-838 milestone 1 / GitHub issue #44 and pull request
  #55 repaired the confirmed runtime regressions and passed the complete Docker-local aggregate.
- Next bounded work: EPIC-838 milestone 3 / GitHub issue #46, making the Docker-local backend gate
  run, enforce and report the complete PostgreSQL-dependent suite after milestone 2 merges.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
