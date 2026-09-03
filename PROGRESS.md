# Current progress

- Current branch: `fix/epic-838-postgres-decomposition`.
- Active work: EPIC-838 milestone 7 / GitHub issue #50 is implemented and qualified for
  publication. Five distinct execution repository ports now share one transaction-owned aggregate,
  and every engine-owning PostgreSQL repository adopts the common transaction, audit, JSON and clock
  services without changing public persistence behavior.
- Completed immediately before this work: EPIC-838 milestone 6 / GitHub issue #49 and pull request
  #60 decomposed executor responsibilities behind the compatibility facade.
- Next bounded work: EPIC-838 milestone 8 / GitHub issue #51, making built-in task specifications
  authoritative for handler schemas and simulator/executor configuration semantics.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
