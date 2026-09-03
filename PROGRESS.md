# Current progress

- Current branch: `fix/epic-838-structure-docs-authority`.
- Active work: EPIC-838 milestone 9 / GitHub issue #52 is implemented, qualified and ready to
  publish.
  Canonical feature packages preserve legacy symbol identity, supported PostgreSQL tests use one
  shared isolated-database lifecycle with three explicit migration-history exceptions,
  `.env.example` is checked against every `Settings` field, repeated Compose service mappings use
  local templates, and ADR plus screenshot evidence navigation is complete and checked.
- Completed immediately before this work: EPIC-838 milestone 8 / GitHub issue #51 was merged through
  pull request #62 as `0e80689`.
- Current verification: focused structure, configuration, deployment, worker, documentation and
  renamed runner/CLI suites pass; the 64-file affected PostgreSQL set passed 148 tests with one
  explicit PostgreSQL-client-tools skip. An independent Sol/high review returned PASS. The complete
  Docker-local aggregate passed 1,516 backend tests with 20 documented skips and 81.62% coverage,
  124 frontend tests and build, all 10 Playwright journeys, 11 Pi worker tests, all 27 deterministic
  harness conformance cases, generated-contract and SDK integrity checks, strict documentation,
  production and model-engine image probes, and repository plus four-SDK packaging.
- Next bounded work: publish and merge issue #52, then begin EPIC-838 milestone 10 / GitHub issue
  #53 for authoritative generated frontend paths.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
