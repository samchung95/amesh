# Current progress

- Active request: GitHub epic #74 / Agent Hotel c219, separated research/finalization and
  measured prompt-cache efficiency. The daemon board owns status; ADR-076 owns the design.
- Isolated implementation branch: `feat/session-finalization-cache`, based on `origin/main`
  at `f1895f0`. The original working tree's uncommitted integration/SonarQube work is untouched.
- First slice (#75/c220, still Doing): healing-enabled structured OpenRouter calls now use
  unary HTTP even through the progress interface. Other calls retain streaming behavior.
  No public schema or checkpoint format changed in this slice.
- Verified locally: mismatch reproduced with 2 failing/4 passing HTTP cases before the fix;
  49 adapter/model primitive tests pass after it, including eight new regression cases.
  Successful replay makes no second HTTP call; malformed output fails closed while billing
  and cache counters remain recorded. Ruff passes. Full pre-push gate is pending.
- Next: finish explicit transport policy and useful privacy-safe rejection diagnostics (#75),
  then native research and checkpointed finalization (#76/c221), stable evidence projection
  and measured cache comparison (#77/c222), and recovery/consumer qualification (#78/c223).
  None of these milestones or the epic is complete; the PR is a full-scope draft.
- Consumer evidence: VibeStonks Core Discovery execution
  `01a0723b-9992-7834-9b65-4ae2e83b829d` failed on four specialists' initial/repair JSON responses;
  scout and news succeeded, no slate was accepted. Exact malformed content is unavailable.
  Integration #72 and Vibe c128 remain open. The earlier calendar block applied to the Daily
  workflow, not this research-only Core Discovery path.
- No paid rerun, broker action, merge or deployment in this implementation slice. Prior
  deployment qualification of `f1895f0`/79 migrations does not qualify this new branch.
- Verification: focused commands and boundaries are recorded in
  [`docs/reviews/TESTLOG.md`](docs/reviews/TESTLOG.md). The required pre-push command remains
  `.\scripts\verify-local.ps1 -Suite all` (Docker-local, no live-provider suite).

## Session log

### 2026-09-06

- Created epic #74 and milestones #75-#78; included cache efficiency explicitly as requested.
- Recorded architecture and implemented/tested the first response transport correction.
- Remaining scope is deliberate, not a completion claim. Resume at #75's diagnostics/policy.
- Earlier development history remains in [the progress archive](docs/reviews/progress-archive.md).
