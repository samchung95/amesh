# Project: AMESH — 2-month MVP

## Goal

Ship a demonstrable durable orchestrator in 8 weeks: a YAML-defined workflow of process, container and agent tasks runs durably on Kubernetes, surviving control-plane and worker crashes without lost or duplicated work. Full scope, deferral register, cons and week-by-week exits: [docs/product/mvp-scope.md](docs/product/mvp-scope.md).

## Out of scope (deferred, not deleted — see the deferral register)

Java 25 core, Kestra/Pebble parity, Docker standalone runner, isolated plugin runtime and SDKs, multi-tenancy/RBAC/SSO, web UI, HA/backup drills, subflows/loops/backfill/caches/SLA, object-storage artifact pipeline, search/analytics projections, compliance evidence, migration tooling, marketplace, agent merge-quorum enforcement.

## Milestones

- [x] M-0: Repository housekeeping — DoD: git initialized with baseline commit; ruff/mypy/pytest/backlog/clean-room/drift gates all green locally; `dependsOn` silent-drop bug fixed with regression tests; proto packages renamed to `amesh.*`; schema-affecting deps pinned. *(Verified 2026-08-19: 15 tests pass, all gates green, commits `20f248f` + `8fc0261`.)*
- [x] M-1: MVP re-scope authored — DoD: `docs/product/mvp-scope.md` exists with in-scope table, deferral register mapping every cut to its epic and resume trigger, cons list, and 8 weekly exit checks. *(Verified 2026-08-19: document committed.)*
- [x] W1: PostgreSQL transport adapter — DoD: claim/lease/fence/ack + inbox/outbox pass kill-during-claim and duplicate-delivery tests against real PostgreSQL. *(Verified 2026-08-21: 22 tests pass, including real PostgreSQL process-crash recovery, stale fencing and duplicate-inbox scenarios; full lint, strict mypy, clean-room, backlog and generation gates pass.)*
- [x] W2: Executor with task-run state — DoD: `examples/parallel-dag.yaml` executes end-to-end; restart mid-run resumes. *(Verified 2026-08-21: PostgreSQL-backed execution/task/attempt state resumes through a fresh engine and service without rerunning successful tasks; 23 tests pass at 82.92% coverage with all repository gates green.)*
- [x] W3: Worker + local process runner — DoD: retry/timeout/cancel work; fencing rejects a stale worker's late result. *(Verified 2026-08-21: local subprocess execution captures results, timeout and fenced cancellation terminate work, persisted retry attempts resume after delay, and PostgreSQL rejects a late result from superseded attempt 1 after attempt 2 starts; 27 tests pass at 83.59% coverage with all repository gates green.)*
- [x] W4: Scheduler + expressions — DoD: cron fires exactly once per occurrence across restarts; outputs flow between tasks; `runIf` evaluated. *(Verified 2026-08-21: concurrent and freshly restarted schedulers converge on one PostgreSQL execution per stable cron occurrence key; sandboxed native Jinja renders inputs, prior outputs and vars, and false `runIf` paths skip handler invocation; 30 tests pass at 83.71% coverage with all repository gates green.)*
- [x] W5: Kubernetes Job runner — DoD: tasks run as Jobs on kind; pod deletion mid-task reconciles. *(Verified 2026-08-21: an AMESH execution creates a deterministic Job on kind v0.32.0 / Kubernetes v1.36.1; deleting its running pod causes the Job controller to create a replacement, whose log and exit code complete the same fenced PostgreSQL attempt; 31 tests pass at 81.21% coverage with all repository gates green.)*
- [x] W6: Agent tasks + REST/CLI — DoD: LLM → shell → HTTP demo flow triggered via API runs on K8s. *(Verified 2026-08-21: the authenticated REST API applies/lists flows, creates/lists/gets executions, returns task logs and accepts webhooks; the CLI mirrors those flows; `agent.llm`, Kubernetes shell and `core.http` complete the checked-in demo against real OpenRouter Luna, PostgreSQL and kind; all 38 tests and repository gates pass.)*
- [x] W7: Helm chart + observability — DoD: `helm install` on fresh kind cluster runs the demo flow; `/metrics` live. *(Verified 2026-08-21: a uv-locked non-root image installed on a new kind v1.36.1 cluster as migration, server and recovery-worker roles against external PostgreSQL; both migrations and rollouts completed, JSON logs and Prometheus metrics were live, and the installed API completed the checked-in Luna → Job → HTTP flow; 41 tests pass at 78.27% branch coverage with all gates green.)*
- [x] W8: Hardening + soak + tag — DoD amended by the product owner on 2026-08-21: accept the verified 270-cycle induced-pod-kill run, defer the remaining uninterrupted 24-hour qualification to EPIC-611, reproduce the quickstart cleanly and tag `v0.2.0-mvp`. *(Verified 2026-08-21: 270 unique single-attempt successes after 270 task-pod, 27 server-pod and 13 worker-pod deletions; clean-cluster quickstart reproduced; 47 tests pass at 80.47% branch coverage with live Luna, PostgreSQL and kind; artifact, Helm, policy and deployed-health gates pass.)*

## Open questions

None currently.

## Decisions log

- 2026-08-19 — Keep Kubernetes in the MVP twice (runs on K8s via Helm; runs tasks as K8s Jobs); defer the standalone Docker runner (EPIC-221) to pay for it — user requirement; Docker runner duplicates ~70% of the Job runner surface for no MVP-visible capability.
- 2026-08-19 — **Product owner confirmed Python as the production core** ("keep the current architecture — slow but robust"); ADR-016 supersedes ADR-010, the Java port is cancelled, and the post-MVP checkpoint becomes a performance review. Robustness claims rest on the PostgreSQL/fencing/pure-reducer design; throughput claims require measurement.
- 2026-08-19 — Expressions are AMESH-native (Jinja2-backed, namespaced), not Pebble-compatible; parity remains a deferred, pinned workstream.
- 2026-08-19 — Planning corpus (900 requirements) is frozen during the MVP; reconciliation pass updates statuses post-MVP.
- 2026-08-19 — Pinned fastapi/pydantic/pydantic-settings exactly because the generated-contracts test asserts byte-stable output.
- 2026-08-21 — Use OpenRouter for live LLM integration tests with `openai/gpt-5.6-luna` as the base model and an environment-overridable model list — user requirement; the core model contract remains provider-neutral.
- 2026-08-21 — Use Jinja2's sandboxed native environment for the explicitly accepted AMESH-native expression subset and croniter for cron calculation; keep occurrence durability in PostgreSQL execution idempotency rather than introducing a second scheduler datastore.
- 2026-08-21 — Use the official Kubernetes Python client 36 async API for the Job runner; deterministic attempt-derived Job names provide reconciliation while PostgreSQL remains authoritative for fenced completion.
- 2026-08-21 — Product owner deferred the remaining uninterrupted 24-hour W8 soak and authorized release progression after cycle 270. The verified partial run is accepted for `v0.2.0-mvp`; the full 86,400-second qualification remains open in EPIC-611 and gates broader availability, scale and production-readiness claims.
