# Current progress

- Current deliverable: approved two-ticket batch c253 (cache portability), then c252 / GitHub #97
  (upstream affinity, explicit boundaries and safe miss diagnostics). Agent Hotel is authoritative.
- Branch: feat/cache-portability-issue-97 in amesh-cache-portability, based on main 154edb9.
- Implemented: generic cache identity on the model port; HTTP cache control mapping and declared
  custom support; canonical-session affinity; optional contextPolicy text boundaries retained in
  checkpoints; safe response/request/backend correlation; missing provider/engine usage aliases.
- No new dependency or migration. Default context/text serialization is preserved. Existing
  requestOptions owns cache mode/TTL and model profiles own custom capability declarations.
- Verified: 201 focused provider/context checks; 102 Pi/session checks (one skip);
  77 final Linux adapter/runtime/API compatibility checks; five process-engine runtime checks.
  Docker backend checkpoint: 1,774 passed, 22 environment/paid skips, one stale OpenAPI snapshot.
  The snapshot is refreshed and its 12-test suite passes on Windows and Linux.
- Frontend: 143 unit tests, build and three Chromium journeys pass. Strict docs build/eight
  browser checks, Pi harness/conformance, contracts/SDK integrity and review regressions pass.
  Ruff and strict mypy (426 modules) pass. First-party Fable 5.1 review and follow-up found no
  blockers. Detailed commands and review receipt digests are in docs/reviews/TESTLOG.md.
- Generated schemas, frontend contracts and Python/TypeScript/Java/Go SDKs are refreshed.
- Runtime still uses deployed 154edb9. No consumer repository, deployment or paid qualification
  is part of this implementation step. GitHub #95/#96 remain separate.
- Live frozen Allocator comparison and owner optimization acceptance remain open on c252;
  stable hashes and successful output alone do not establish a cache improvement.
- Original checkout contains unrelated changes and is preserved.
