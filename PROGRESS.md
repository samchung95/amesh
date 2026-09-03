# Current progress

- Current branch: `fix/epic-838-role-boundaries`.
- Active work: EPIC-838 milestone 4 / GitHub issue #47 is implemented and qualified for publication.
  PostgreSQL administrative work now fails closed without the restricted grants; tenant-bearing paths,
  notification waits and pooled-session cleanup are explicitly role-scoped and tested under a
  `NOINHERIT NOBYPASSRLS` login.
- Completed immediately before this work: EPIC-838 milestone 3 / GitHub issue #46 and pull request
  #57 made the complete Docker-local gate run and report the PostgreSQL suite honestly.
- Next bounded work: EPIC-838 milestone 5 / GitHub issue #48, decomposing API bootstrap,
  dependencies and feature routers without public OpenAPI drift or import-time runtime singletons.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
