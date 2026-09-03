# Current progress

- Current branch: `chore/epic-838-catalog-archive`.
- Active work: EPIC-838 milestone 0 / GitHub issue #43. The canonical epic catalog is being split
  into a small active manifest and a declared completed archive while regeneration, validation and
  GitHub bootstrap retain one deterministic aggregate view.
- Completed immediately before this work: EPIC-837 and its eleven qualified child pull requests;
  GitHub issue #42 then re-verified that work against merged main.
- Next bounded work: EPIC-838 milestone 1 / GitHub issue #44, correcting the confirmed
  release-blocking runtime regressions before any further structural movement.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
