# Current progress

- Active request: GitHub epic #74 / Agent Hotel c219, separated research/finalization and
  measured prompt-cache efficiency. The daemon board owns status; ADR-076 owns the design.
- Isolated implementation branch: `feat/session-finalization-cache`, based on `origin/main`
  at `f1895f0`. The original working tree's uncommitted integration/SonarQube work is untouched.
- Implementation now includes explicit transport policy and privacy-safe rejection diagnostics,
  opt-in native research with checkpointed business-schema finalization, duplicate-free evidence
  projection, and v2 cache accounting including rejected billed calls, phase cohorts and accepted-result
  denominators. Vibe Core Discovery alone opts into NATIVE_V2 with a finish/finalization/repair budget.
- Focused session/model tests pass, including real Pi restart before/after phase transition,
  finalization repair, and replay without duplicate tools. Ten analyzer tests and 14 Vibe bundle/
  provisioning/acceptance tests pass. Fable 5.1's implementation review found no confirmed blockers.
- The expanded implementation requires the full Docker-local pre-push gate; its result is recorded
  on PR #79 and the daemon board after the hook finishes. The earlier gate at 83dedf2 passed for the
  initial transport slice only. Public contracts, frontend types and all four SDKs are refreshed.
- Current live qualification: locally deployed PR #79, fixed the missing flow-authoring protocol
  field (da0153d), and provisioned Vibe Core Discovery revision 3. The first fresh native run
  failed before tool dispatch on extra optional arguments. Native exact-call repair feedback
  is regression-tested (730965b), but a second live run still added null optional fields.
  Native tool schemas now project fields from the full immutable required plan, preserving
  prefix stability and strict dispatch. Full session suite: 56 passed, 1 skipped. Next rerun
  and Fable schema review are pending; live finalization/cache measurements are still required.
- Next: complete controlled provider comparison and fresh eight-session Core Discovery acceptance.
  Both Codex and Fable must review measured cache evidence
  and find no remaining worthwhile in-scope optimization. No epic completion or live sign-off yet.
- Consumer evidence: VibeStonks Core Discovery execution
  `01a0723b-9992-7834-9b65-4ae2e83b829d` failed on four specialists' initial/repair JSON responses;
  scout and news succeeded, no slate was accepted. Exact malformed content is unavailable.
  Integration #72 and Vibe c128 remain open. The earlier calendar block applied to the Daily
  workflow, not this research-only Core Discovery path.
- Local deployment and paid research-only reruns are now authorized. No broker action or merge.
  Prior deployment qualification of `f1895f0` does not qualify this new branch.
- Verification: focused commands and boundaries are recorded in
  [`docs/reviews/TESTLOG.md`](docs/reviews/TESTLOG.md). The required pre-push command remains
  `.\scripts\verify-local.ps1 -Suite all` (Docker-local, no live-provider suite).

## Session log

### 2026-09-06

- Created epic #74 and milestones #75-#78; included cache efficiency explicitly as requested.
- Recorded architecture and implemented/tested the first response transport correction.
- Implemented the remaining runtime/reporting scope; live cache and consumer gates remain open.
- Earlier development history remains in [the progress archive](docs/reviews/progress-archive.md).
