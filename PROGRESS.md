# Current progress

- Current branch: `fix/epic-838-handler-authoritative-dsl`.
- Active work: EPIC-838 milestone 8 / GitHub issue #51 is implemented and Docker-qualified. Built-in
  task schemas now come from independently checked handler contracts,
  task kinds have explicit runtime ownership, validators and plugin runtimes share one structural
  field authority, persisted revision hashes remain repository-row data, and flow tests use the
  executor's switch and inline-loop value semantics.
- Completed immediately before this work: EPIC-838 milestone 7 / GitHub issue #50 and pull request
  #61 split the five execution repository ports over one transaction-owned PostgreSQL aggregate.
- Next bounded work: publish and merge issue #51, then begin EPIC-838 milestone 9 / GitHub issue #52,
  reconciling repository settings, Compose and documentation structure.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
