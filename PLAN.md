# Project: AMESH — 2-month MVP

## Goal

Ship a demonstrable durable orchestrator in 8 weeks: a YAML-defined workflow of process, container and agent tasks runs durably on Kubernetes, surviving control-plane and worker crashes without lost or duplicated work. Full scope, deferral register, cons and week-by-week exits: [docs/product/mvp-scope.md](docs/product/mvp-scope.md).

## Out of scope (deferred, not deleted — see the deferral register)

Java 25 core, Kestra/Pebble parity, Docker standalone runner, isolated plugin runtime and SDKs, multi-tenancy/RBAC/SSO, web UI, HA/backup drills, subflows/loops/backfill/caches/SLA, object-storage artifact pipeline, search/analytics projections, compliance evidence, migration tooling, marketplace, agent merge-quorum enforcement.

## Milestones

- [x] M-0: Repository housekeeping — DoD: git initialized with baseline commit; ruff/mypy/pytest/backlog/clean-room/drift gates all green locally; `dependsOn` silent-drop bug fixed with regression tests; proto packages renamed to `amesh.*`; schema-affecting deps pinned. *(Verified 2026-08-19: 15 tests pass, all gates green, commits `20f248f` + `8fc0261`.)*
- [x] M-1: MVP re-scope authored — DoD: `docs/product/mvp-scope.md` exists with in-scope table, deferral register mapping every cut to its epic and resume trigger, cons list, and 8 weekly exit checks. *(Verified 2026-08-19: document committed.)*
- [ ] W1: PostgreSQL transport adapter — DoD: claim/lease/fence/ack + inbox/outbox pass kill-during-claim and duplicate-delivery tests against real PostgreSQL.
- [ ] W2: Executor with task-run state — DoD: `examples/parallel-dag.yaml` executes end-to-end; restart mid-run resumes.
- [ ] W3: Worker + local process runner — DoD: retry/timeout/cancel work; fencing rejects a stale worker's late result.
- [ ] W4: Scheduler + expressions — DoD: cron fires exactly once per occurrence across restarts; outputs flow between tasks; `runIf` evaluated.
- [ ] W5: Kubernetes Job runner — DoD: tasks run as Jobs on kind; pod deletion mid-task reconciles.
- [ ] W6: Agent tasks + REST/CLI — DoD: LLM → shell → HTTP demo flow triggered via API runs on K8s.
- [ ] W7: Helm chart + observability — DoD: `helm install` on fresh kind cluster runs the demo flow; `/metrics` live.
- [ ] W8: Hardening + soak + tag — DoD: 24h soak with induced pod kills, zero lost/duplicated executions; quickstart reproduced clean; `v0.2.0-mvp` tagged.

## Open questions

- LLM provider/key for the week-6 `agent.llm` demo.

## Decisions log

- 2026-08-19 — Keep Kubernetes in the MVP twice (runs on K8s via Helm; runs tasks as K8s Jobs); defer the standalone Docker runner (EPIC-221) to pay for it — user requirement; Docker runner duplicates ~70% of the Job runner surface for no MVP-visible capability.
- 2026-08-19 — **Product owner confirmed Python as the production core** ("keep the current architecture — slow but robust"); ADR-016 supersedes ADR-010, the Java port is cancelled, and the post-MVP checkpoint becomes a performance review. Robustness claims rest on the PostgreSQL/fencing/pure-reducer design; throughput claims require measurement.
- 2026-08-19 — Expressions are AMESH-native (Jinja2-backed, namespaced), not Pebble-compatible; parity remains a deferred, pinned workstream.
- 2026-08-19 — Planning corpus (900 requirements) is frozen during the MVP; reconciliation pass updates statuses post-MVP.
- 2026-08-19 — Pinned fastapi/pydantic/pydantic-settings exactly because the generated-contracts test asserts byte-stable output.
