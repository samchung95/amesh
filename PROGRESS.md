# Current progress

- Release baseline: `main` at `b450e7d` after the documentation-only EPIC-838 parent closeout.
- Release dependency: issue #66 is implemented at `9bf3c26` on
  `fix/issue-66-must-have-regressions`; PR #68 is open, not merged.
- Active work: integration-readiness epic #69 (Agent Hotel c215). Documentation correction #70
  (c216) is implemented and locally verified; GitHub and the board track publication/review status.
  Deployment #71 (c217) and consumer qualification #72 (c218) await their target/change confirmations.
  The board owns task status.
- Completed in this follow-up: explicit-null/default and YAML-date flow validation, imported
  RUNNING-session progress reconstruction, supported and pre-0075 upgrade preflight evidence,
  transient worker pool-timeout handling, and the three requested contributor rules.
- Review verification on 2026-09-05: the Docker core aggregate passed 1,561 backend tests with
  20 skips and 81.67% coverage, 136 frontend tests, two application and eight documentation
  Playwright journeys, 11 Pi worker tests, all 27 harness conformance cases, generated-contract/SDK
  integrity checks, static checks and strict documentation. Compose validation also passed.
  This review did not rerun production-image probes, packaging or live providers. Earlier full
  release-gate evidence remains recorded in
  [`docs/reviews/TESTLOG.md`](docs/reviews/TESTLOG.md).
- Deployment evidence on 2026-09-05: port 8000 reports healthy/ready with 74 expected/applied
  migrations, while this checkout's manifest contains 79. Do not interpret old-binary readiness as
  qualification of current source; follow the current-head boundary in
  [`docs/operations/upgrades.md`](docs/operations/upgrades.md#current-head-deployment-boundary).
- Next bounded work: review the focused #70 changes, then confirm #66/PR #68 disposition and the target/change window
  for #71. Identify the consuming repository and approved agent/provider budget for #72. Preserve
  unrelated local SonarQube changes and `probe_pkg/`; deferred debt remains out of scope.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
