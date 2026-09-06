# Current progress

- Active request: GitHub epic #74 / Agent Hotel c219, separated research/finalization and
  measured prompt-cache efficiency. The daemon board owns status; ADR-076 owns the design.
- Current #77 work: owner approved the stable-envelope finding. Opt-in NATIVE_V3 keeps
  tools/business schema in both phases with required/none tool choice, strict controller
  authority and unchanged V1/V2 behavior. Twelve real-Pi phase/recovery/repair cases and
  191 focused tests pass (one skip). Fable's parallel-call repair blocker is fixed; five
  paired provider measurements passed with 52.00% less uncached input and 12.24% lower
  observed cost. Codex/Fable sign off practical optimization for this pinned workload.
  Fresh Vibe revision 4 passed all eight sessions and normal durable acceptance with zero
  repairs/compaction/broker commands. See PR #79 and the authoritative board for final
  release-gate and publication status.
- Isolated implementation branch: `feat/session-finalization-cache`, based on `origin/main`
  at `f1895f0`. The original working tree's uncommitted integration/SonarQube work is untouched.
- Implementation now includes explicit transport policy and privacy-safe rejection diagnostics,
  opt-in native research with checkpointed business-schema finalization, duplicate-free evidence
  projection, and v2 cache accounting including rejected billed calls, phase cohorts and accepted-result
  denominators. Vibe Core Discovery alone now opts into NATIVE_V3 with unchanged budgets.
- Focused session/model tests pass, including real Pi restart before/after phase transition,
  finalization repair, and replay without duplicate tools. Ten analyzer tests and 14 Vibe bundle/
  provisioning/acceptance tests pass. Fable 5.1's implementation review found no confirmed blockers.
- The expanded implementation requires the full Docker-local pre-push gate; its result is recorded
  on PR #79 and the daemon board after the hook finishes. The earlier gate at 83dedf2 passed for the
  initial transport slice only. Public contracts, frontend types and all four SDKs are refreshed.
- Live qualification now passes on AMESH `1a0a699`, Core Discovery revision 3:
  execution `01a0749e-8812-7a7d-962e-d7b5b3e77f0e` collected fresh candidates and completed
  all eight sessions, with zero repairs/compaction. Vibe acceptance recovery reused that exact
  execution after two consumer fixes (shared news attribution and AMESH history release IDs).
  Durable artifact `da_1ebe046d7c20d7d18e842528` is visible through `/api/discovery` and its
  status endpoint. It is a valid research abstention: six stocks reviewed, zero ranked candidates,
  80 evidence references and zero broker commands. No manufactured candidate or weaker gate.
- AMESH runtime fixes admit the native protocol in the DSL, guide exact-plan repair, project
  unused optional fields and unsupported primitive schema alternatives from the full immutable
  required plan. Original schemas/dispatch authority remain pinned. Session suite: 56 passed,
  1 skipped; Vibe focused consumer suite: 37 passed. Fable found no confirmed fix blockers.
- The earlier V2 optimization review left its gate OPEN. That accepted run used 2,726,314
  input tokens, 1,956,162 cached (71.75%), and USD 0.403499184 billed. Research reused 83.05%;
  finalization reused 0%. A frozen public-request stable-envelope probe reached 98.02% reuse
  at the transition, but its identical repeat missed. This is not a production savings result.
  Codex and Fable agree #77 should next qualify stable tools plus business schema across phases,
  with exact phase/dispatch authority, provider compatibility and real-harness paired evidence.
  This prior review motivated the now-qualified V3 implementation.
- Current V3 fresh execution `01a07540-e6ca-716a-8ac4-69c0a1e3e47c`, snapshot
  `ds_e624b51d08f61a71789cd258`, accepted normally as `da_5560423dcec9f7a16f9fc039`.
  Six names reviewed, valid abstention, 81 evidence references. All 78 calls accounted:
  86.11% overall reuse, 99.505% finalization, USD 0.339512536 billed per accepted result.
  This corroborating fresh run is not substituted for the controlled five-pair comparison.
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
