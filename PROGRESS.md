# Current progress

- Current branch: `fix/epic-838-runtime-regressions`.
- Active work: EPIC-838 milestone 1 / GitHub issue #44 is implemented and qualified for publication.
  The release-blocking Pi startup, recovery, deferral, Kubernetes result, lifecycle conflict,
  indexing and cancellation regressions now have focused coverage.
- Completed immediately before this work: EPIC-838 milestone 0 / GitHub issue #43 and pull request
  #54 partitioned the canonical catalog into 20 active and 115 completed records without changing
  its deterministic aggregate view.
- Next bounded work: EPIC-838 milestone 2 / GitHub issue #45, correcting the confirmed reducer,
  trace-context, progress, redaction and determinism defects after milestone 1 merges.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
