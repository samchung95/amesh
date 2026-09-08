# Current progress

- Follow-up batch (2026-09-08): #88 canonical continuation, #89 governed approvals,
  #90 streamed validation/repair, #72/#69 consumer qualification and the full #67 A–H
  audit. Agent Hotel cards c231, c233–c244 and c218/c215 are authoritative.
- Implementation is on `fix/session-integration-followups`, isolated from unrelated
  work in the original checkout. The baseline is merged/deployed main `ab5039e`.
- Session changes preserve exact retained pins and continuation across messages,
  construct real authenticated approval predecessors, recover confirmed pre-generation
  streamed 429s and settle interrupted/cancelled invocation accounting without replay.
- #67 changes cover tenant RLS/grants (migration 0080), five SQL-owning repositories,
  handler-derived schemas, runtime tracing and cleanup, API provider lifetimes and
  authorization, strict unprivileged verification, frontend contracts and documentation
  reachability. Dynamic plugin kinds and compatibility imports remain supported.
- Validation checkpoint: 1,699 backend tests passed in the first complete run, with
  eight failures corrected and 75 focused regression checks passing under coverage.
  Strict mypy passes 426 modules. Frontend: 143 unit tests, production build and three
  browser journeys pass; strict docs build and eight docs browser journeys pass.
- The complete pre-push gate is mandatory. Final gate, PR/merge, deployed revision and
  live consumer evidence are recorded on release card c236 and its PR. AURA browser
  qualification is c235; VibeStonks canonical qualification is c218.
- Deployment waits for active executions to finish. Preserve existing environment and
  volumes; the AURA extension's manual reload remains the user's step.

## Previous release handoff (superseded by the baseline above)

- Release in progress: Agent Hotel c232 packages the existing c229/c230 provider
  429 recovery and repair-cache diagnostics on `fix/openrouter-429-turn-retry`,
  based on merged `main` at `794d9e8`. The user authorized local deployment,
  pushing a PR and merging it, followed by issue #90 ticket preparation and an
  evaluation of the remaining open GitHub issues.
- Implemented: confirmed unary OpenRouter 429 rejections retry the identical
  request within its original deadline; stable tenant/session routing and safe
  prefix/provider fingerprints survive repair and rejected-response accounting.
  Other providers and ambiguous or billed outcomes retain their existing behavior.
- Prior focused validation: 119 tests passed, one existing skip; targeted Ruff and
  mypy passed. Fable 5.1 approved c230. Full Docker-local release verification is
  pending for this commit; its final result will be recorded on the PR and c232.
- Running before release: API/executor use `amesh:794d9e8-repair-cache`; the other
  four roles use `amesh:main-794d9e8-runtime`. All six report READY, all 79 migrations
  are applied, and no execution is active. The release will align all six roles.
- Prior accepted Vibe execution `01a07e7f-6f83-709d-9ec3-f86ff1d5d31d` completed
  five turns and four read-only tools with stable routing/envelope hashes and
  matching continuation prefixes. Reported cache reads were 80.3837% overall and
  86.6973% after the first turn. This run had no schema repair; it does not qualify
  live repair-cache reuse or establish a controlled before/after improvement.
- The daemon board is authoritative. c231 already tracks GitHub #90; inspect and
  reconcile it after the release rather than creating a duplicate. The remaining
  issue review is evaluation only, without unrelated fixes or automatic closure.
- Verify with `.\scripts\verify-local.ps1 -Suite all`; the native pre-push hook
  runs this same gate. Historical evidence lives in `docs/reviews/TESTLOG.md`.
- Preserve the original checkout's unrelated SonarQube, onboarding and probe_pkg
  changes. Integration-readiness epic #69 remains separate from this release.
