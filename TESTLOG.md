# Test Log

## M-0: Repository housekeeping + M-1: MVP re-scope — 2026-08-19

Spec source: PLAN.md M-0/M-1 DoD (housekeeping items from the 2026-08-18 repo review).

Verified (commands run from the repo root with the project's Python 3.12 venv):

- [x] `ruff format --check .` — 202 files, clean (was: 6 files needing reformat).
- [x] `ruff check .` — clean (was: 12 errors).
- [x] `python -m mypy` — strict, 18 source files, no issues (was: 3 pre-existing errors in `dsl/validator.py`, confirmed pre-existing via `git stash` against the baseline commit).
- [x] `python -m pytest` — 16 passed (13 baseline + 3 new regression tests), 1 benign starlette deprecation warning.
- [x] `python scripts/validate_backlog.py` — 103 epics, 900 requirements, 992 trace links valid.
- [x] `python scripts/check_clean_room.py` — lexical gate passed.
- [x] `python scripts/regenerate_planning_artifacts.py` then `git status` — zero drift (after `newline="\n"` fix; previously produced CRLF churn for every generated file on Windows).
- [x] `python scripts/generate_contracts.py` then `git status` — zero drift; fastapi/pydantic/pydantic-settings now pinned exactly so the byte-stable contract test cannot break via unpinned upgrades.
- [x] CLI smoke (real app): `python -m amesh validate examples/hello-world.yaml` → valid, stable semantic hash.
- [x] `dependsOn` bug: snake_case `depends_on` cycle now detected (`test_snake_case_depends_on_is_honoured`); snake/camel documents hash identically (`test_snake_case_and_camel_case_dependencies_hash_identically`).
- [x] Proto rename: `grep -r openorchestrator proto/` → no matches; packages are `amesh.worker.v1` / `amesh.plugin.v1`.
- [x] Git: repository initialized, baseline commit of the full tree, work on branch `worktree-housekeeping-mvp-rescope`.

Adversarial pass:

- Mixed spelling (`dependsOn` + `depends_on` on one task): **bug found** — validated silently with the snake_case copy riding along as an inert extra in the canonical dump. Fixed with a `mode="before"` validator rejecting conflicting spellings; regression test `test_conflicting_dependency_spellings_are_rejected`; probe re-run now rejects.
- Regeneration determinism on Windows: **bug found** — both generator scripts emitted CRLF via `write_text` default newline translation, which would trip the CI drift gates for any contributor on Windows. Fixed with `newline="\n"`; regeneration re-run shows zero modified files.

Not covered (deliberate):

- Proto files are not compiled (no `protoc` in the toolchain; repo commits no generated code) — the rename is textual and README-consistent only.
- `make validate` via GNU make (not present on this Windows host) — the underlying commands were run individually instead.
- The FastAPI server was exercised through the test client and CLI, not a live `uvicorn` boot.
- App-level defects noted in the review but scoped out of housekeeping (post-body 2 MiB guard, unbounded `applied_event_ids`, reducer fencing) — tracked for MVP weeks 1–2 in PLAN.md.

Verdict: PASS — M-0 and M-1 closed.

## ADR-016: Python confirmed as production core — 2026-08-19

Spec source: product-owner decision ("keep the current architecture") recorded via the mechanism ADR-010 itself mandates (a superseding ADR).

Verified:

- [x] ADR-016 written; ADR index, ADR-010 (superseded banner), ADR-001 (amended banner) updated.
- [x] Production-core claims updated in README (table, prose, diagram), DECISIONS_NEEDED, decision-register (Q-006 + binding consequence 1), IMPLEMENTATION_STATUS, project-baseline.json, plugins/README, docs/architecture/README, mvp-scope, PLAN, CHANGELOG (new Unreleased entry).
- [x] Canonical `requirements/urs.json` metadata note updated; hardcoded URS bullet in `scripts/regenerate_planning_artifacts.py` updated; artifacts regenerated with zero residual drift.
- [x] Full gate chain re-run: ruff format/check clean, mypy strict clean, 16 tests pass, backlog valid, clean-room gate passes.
- [x] Repo-wide audit: `grep -rn "Java 25"` — every remaining mention sits in a dated historical document or under an explicit superseded/historical banner (ADR-010 body, backend-language-evaluation, generation-validation, changelog history, ADR-016's own context).

Not covered (deliberate): epic bodies and requirement texts still carrying Java-era phrasing inside `backlog/epics.json`/`urs.json` requirement records — all are plugin-SDK/script-language mentions that remain correct; any core-language rewording belongs to the post-MVP reconciliation pass per mvp-scope section 6.

Verdict: PASS — decision recorded consistently.

## W1: PostgreSQL transport adapter — 2026-08-21

Spec source: `PLAN.md` W1 DoD and `docs/product/mvp-scope.md` week-1 exit check.

Verified with `uv` and PostgreSQL 17 from `compose.yaml`:

- [x] Idempotent durable-queue enqueue returns one queue identity for duplicate message IDs.
- [x] `FOR UPDATE SKIP LOCKED` claims issue expiring leases and monotonically increasing fencing tokens.
- [x] Lease extension, retry release and fenced acknowledgement succeed for the current owner.
- [x] An expired worker cannot acknowledge after a replacement receives a higher fencing token.
- [x] Transactional outbox publication creates one durable queue row and marks the outbox row published in the same PostgreSQL transaction.
- [x] Consumer-inbox insertion returns true once and false for duplicate delivery.
- [x] A separate worker process exits after committing its inbox identity but before acknowledgement; the replacement reclaims with token 2, detects the duplicate and completes without a second logical effect.
- [x] Full suite: 22 tests pass, including the live OpenRouter `openai/gpt-5.6-luna` contract test.
- [x] `ruff format --check .`, `ruff check .`, strict `mypy`, backlog validation, clean-room validation, compilation and generated-artifact drift checks pass.

Adversarial pass: duplicate enqueue, duplicate delivery, abandoned lease, stale acknowledgement and process death between inbox commit and queue acknowledgement all preserve one effective delivery.

Not covered: coupling an execution-state transition and outbox append in one application unit of work; that repository boundary is introduced in W2 where execution state exists.

Verdict: PASS — W1 closed.

## W2: Executor with persisted task-run state — 2026-08-21

Spec source: `PLAN.md` W2 DoD and `docs/product/mvp-scope.md` week-2 exit check.

Verified:

- [x] `examples/parallel-dag.yaml` is validated, persisted and executed through the AMESH executor service.
- [x] Execution creation persists the flow revision, three initial execution events and stable task-run identities.
- [x] Every task attempt is stored separately with its result before dependant tasks become eligible.
- [x] Independent ready tasks execute as one asynchronous wave; `combine` waits for both extract tasks.
- [x] The test stops after one successful task, disposes the engine/service, constructs a fresh instance and completes from PostgreSQL state.
- [x] Successful pre-restart work is not repeated: all three task runs finish with exactly one attempt.
- [x] The event stream is `Created → Queued → Started → Succeeded` with monotonic sequence numbers.
- [x] Full suite: 23 tests pass at 82.92% branch coverage; Ruff, strict mypy, backlog, clean-room, compilation and generation gates pass.

Adversarial pass: a complete loss of in-memory executor state between DAG steps does not lose progress or rerun the persisted successful task.

Not covered: expression interpolation inside task values, worker dispatch and retries; these are W4 and W3 responsibilities respectively.

Verdict: PASS — W2 closed.

## W3: Worker + local process runner — 2026-08-21

Spec source: `PLAN.md` W3 DoD and `docs/product/mvp-scope.md` week-3 exit check.

Verified with `uv` and PostgreSQL 17 from `compose.yaml`:

- [x] The runner port carries a stable attempt identity and fencing token plus command, environment, working-directory, timeout and cancellation-grace inputs.
- [x] The local-process adapter launches argv directly without shell parsing and captures stdout, stderr, exit code and duration in a normalized result.
- [x] Task timeout first terminates the child and escalates to kill after the configured grace period.
- [x] Cancellation accepts only the current attempt identity and fencing token; a stale cancellation request is rejected.
- [x] Failed execution is persisted as an attempt failure and `RETRY_DELAY`; the next eligible run starts attempt 2 and completes successfully.
- [x] PostgreSQL compare-and-set completion rejects attempt 1 after retry attempt 2 has started.
- [x] The pre-existing restart test still resumes `examples/parallel-dag.yaml` through a fresh engine and service.
- [x] Flow JSON Schema was regenerated for retry, timeout, command and environment fields.
- [x] Full suite: 27 passed, 1 opt-in LLM test skipped, 83.59% branch coverage.
- [x] `ruff format --check .`, `ruff check .`, strict `mypy`, backlog validation, clean-room validation, compilation and generated-artifact drift checks pass.
- [x] EPIC-104, EPIC-209 and EPIC-220 record the verified W3 MVP slice with evidence links while leaving broader parity requirements open.

Adversarial pass: once retry attempt 2 owns the task run, an obsolete attempt 1 completion cannot mutate durable state.

Not covered: the broader epic requirements for pause/restart actions, maximum retry interval/jitter, execution-level timeout, log streaming metadata, process resource limits and cross-platform process-group qualification; these are outside the accepted W3 MVP slice.

Verdict: PASS — W3 closed.

## W4: Cron scheduler + native expressions — 2026-08-21

Spec source: `PLAN.md` W4 DoD and `docs/product/mvp-scope.md` week-4 exit check.

Verified with `uv` and PostgreSQL 17 from `compose.yaml`:

- [x] `core.cron` triggers validate cron syntax and explicit IANA timezone names; the flow JSON Schema is regenerated.
- [x] Cron iteration returns the expected timezone-aware next occurrence.
- [x] The stable idempotency key includes flow revision, trigger identity and scheduled UTC instant.
- [x] Two concurrent scheduler/repository instances firing the same occurrence return the same execution identity.
- [x] A fresh scheduler and database engine firing that occurrence after the first execution completes still return the same identity.
- [x] PostgreSQL contains one execution for the flow occurrence; initial events and task runs are created only by the winning insert transaction.
- [x] The sandboxed native Jinja engine renders nested task values from `inputs`, successful task `outputs` and flow `vars`.
- [x] Output from the first task renders into the dependent task as a native value; the dependent result is `hello world`.
- [x] A false boolean `runIf` persists `{"skipped": true}` without calling the task handler, and the flow completes.
- [x] Missing expression values and non-boolean `runIf` values fail deterministically.
- [x] Full suite: 30 passed, 1 opt-in LLM test skipped, 83.71% branch coverage.
- [x] `ruff format --check .`, `ruff check .`, strict `mypy`, backlog validation, clean-room validation, compilation and generated-artifact drift checks pass.
- [x] EPIC-004, EPIC-005 and EPIC-102 record the verified W4 MVP slice; previously completed W1/W2 progress was also reconciled into EPIC-009, EPIC-100 and EPIC-201.

Adversarial pass: concurrent scheduling plus a new scheduler process after completion cannot create a second logical occurrence.

Not covered: scheduler leases/cursors, catch-up policies, DST qualification, Pebble compatibility, secret contexts and template resource budgets; these are outside the accepted W4 MVP slice.

Verdict: PASS — W4 closed.

## W5: Kubernetes Job runner — 2026-08-21

Spec source: `PLAN.md` W5 DoD and `docs/product/mvp-scope.md` week-5 exit check.

Verified with `uv`, PostgreSQL 17, kind v0.32.0 and Kubernetes v1.36.1:

- [x] The existing runner-neutral request now drives the official Kubernetes async client; no `kubectl` subprocess is used by application code.
- [x] Each attempt maps to one deterministic DNS-safe Job name carrying attempt and fencing labels.
- [x] A pre-existing Job with matching ownership is reconciled instead of duplicated; a mismatched fence is rejected.
- [x] The Job spec carries the requested image, argv command, environment, resource request/limit and active deadline.
- [x] The executor persists the task attempt before the Kubernetes Job is created and accepts the terminal result through the existing attempt compare-and-set path.
- [x] The real kind test waits for the task pod to run, deletes it with zero grace, and observes the Job controller create a replacement.
- [x] The runner does not mistake the deleted-pod failure counter for a terminal Job failure; it waits for a `Failed=True` condition or replacement success.
- [x] The replacement pod exits 0 and emits `completed`; its distinct pod name, log and exit code are persisted on the original task attempt.
- [x] The owned Job is deleted idempotently after terminal result capture; the test namespace is removed.
- [x] Flow JSON Schema was regenerated for image and resource fields.
- [x] Full suite: 31 passed, 1 opt-in LLM test skipped, 81.21% branch coverage.
- [x] `ruff format --check .`, `ruff check .`, strict `mypy`, backlog validation, clean-room validation, compilation and generated-artifact drift checks pass.
- [x] EPIC-004, EPIC-209 and EPIC-222 record the verified W5 MVP slice with evidence links.

Adversarial pass: a non-terminal failed-pod count cannot prematurely fail a still-reconciling Job, and the replacement pod completes the same durable attempt.

Not covered: multi-cluster selection, service-account policy, streaming reconnects, workload identity and comprehensive Kubernetes failure classification; these remain outside the accepted W5 MVP slice.

Verdict: PASS — W5 closed.

## W6: Agent tasks + REST/CLI — 2026-08-21

Spec source: `PLAN.md` W6 DoD and `docs/product/mvp-scope.md` week-6 exit check.

Verified with `uv`, PostgreSQL 17, kind v0.32.0 / Kubernetes v1.36.1, the official MCP v2 client and live OpenRouter `openai/gpt-5.6-luna`:

- [x] `core.http` executes configured HTTP requests and captures status, headers and JSON/text bodies.
- [x] `agent.llm` uses an OpenAI-compatible chat-completions contract with OpenRouter and Luna as the default model; the live adapter smoke passes.
- [x] `agent.mcp` invokes a named tool through the official MCP client; an in-process MCP server verifies structured results.
- [x] Static-bearer-protected REST endpoints apply/list flows, create/list/get executions, return task logs and invoke webhooks; missing credentials are rejected.
- [x] CLI commands mirror validation, flow apply/list, execution run/get/log and webhook operations.
- [x] `examples/agent-shell-http.yaml` is applied and triggered through the REST API; Luna produces the plan, a real Kubernetes Job executes the shell step and the final HTTP task reaches the callback.
- [x] PostgreSQL stores the completed execution and task outputs for the live three-task chain.
- [x] Generated JSON Schema and OpenAPI contracts were refreshed.
- [x] Full suite: 38 tests pass with the live OpenRouter, PostgreSQL and kind gates enabled.
- [x] `ruff format --check`, `ruff check`, strict `mypy`, planning-artifact drift, clean-room and compilation gates pass.
- [x] EPIC-103, EPIC-306, EPIC-312, EPIC-400, EPIC-402 and EPIC-403 record the verified W6 MVP slices with evidence links.

Adversarial pass: unauthenticated control-plane calls are rejected, repeat flow application is idempotent, and all three provider/runner boundaries execute through their production handlers rather than test-only substitutes.

Not covered: multi-user identity, RBAC, pagination, asynchronous API dispatch, generated SDKs, provider breadth and autonomous agent loops; these remain outside the accepted W6 MVP slice.

Verdict: PASS — W6 closed.

## W7: Helm chart + observability — 2026-08-21

Spec source: `PLAN.md` W7 DoD and `docs/product/mvp-scope.md` week-7 exit check.

Verified with `uv`, Docker Desktop, Helm v4.2.4, a newly created kind v0.32.0 / Kubernetes v1.36.1 cluster, external PostgreSQL 17 and live OpenRouter Luna:

- [x] The container installs the frozen `uv.lock` with uv v0.11.31 and runs as numeric UID 100/GID 101.
- [x] `helm lint` and `helm template` pass for `charts/amesh`.
- [x] A fresh kind cluster receives only the locally built `amesh:mvp` image before installation.
- [x] PostgreSQL is deployed outside the AMESH chart; the chart consumes its URL and admin/OpenRouter credentials from existing Secrets.
- [x] The pre-install migration hook applies and records `0001_foundation.sql` and `0002_mvp_task_retry.sql` under an advisory lock.
- [x] Server and delayed recovery-worker Deployments roll out Ready with one namespace-scoped ServiceAccount and task-Job Role.
- [x] Health/readiness probes pass and server/worker stdout contains valid newline-delimited JSON records.
- [x] `/metrics` returns Prometheus process/build metrics plus normalized AMESH HTTP request counters through the installed Service.
- [x] The checked-in `examples/agent-shell-http.yaml` is applied through the installed API; live Luna, a real busybox Kubernetes Job and the HTTP callback all return `SUCCESS`.
- [x] Full suite: 41 tests pass at 78.27% branch coverage with live OpenRouter, PostgreSQL and kind gates enabled.
- [x] `ruff format --check`, `ruff check`, strict `mypy`, generated contracts, planning-artifact drift, clean-room, compilation, Helm lint and Helm render gates pass.
- [x] EPIC-111, EPIC-606 and EPIC-607 record the verified W7 MVP slices with evidence links.

Adversarial pass: Helm starts no server or worker until the migration hook succeeds, production credentials are not embedded in chart values, and the image's numeric non-root identity satisfies Kubernetes `runAsNonRoot` enforcement.

Not covered: multi-architecture/offline bundles, ingress, autoscaling, upgrades, multiple distributions, OpenTelemetry, dashboards and log shipping; these remain outside the accepted W7 MVP slice.

Verdict: PASS — W7 closed.

## W8: Hardening, release qualification and tag — 2026-08-21

Spec source: `PLAN.md` W8 DoD and `docs/product/mvp-scope.md` week-8 exit check, amended by the product owner on 2026-08-21 to accept the verified cycle-270 evidence and defer the remaining uninterrupted 24-hour run to EPIC-611.

Verified with `uv`, PostgreSQL 17, Docker Desktop, Helm v4.2.4, kind v0.32.0 / Kubernetes v1.36.1 and live OpenRouter `openai/gpt-5.6-luna`:

- [x] The exact `amesh:mvp-w8f` image ran the recovery workload from 2026-08-21T02:24:39Z through cycle 270 at 2026-08-21T11:04:43Z, more than 8 hours 40 minutes of continuous induced failure.
- [x] All 270 executions persisted unique IDs and finished `SUCCESS` with exactly one task run, attempt 1 and the exact cycle-specific stdout when independently reread through the API.
- [x] Every task pod was deleted and reconciled; the run also deleted 27 server pods and 13 worker pods. No accepted execution was lost or duplicated, and replacement server/worker Deployments were Ready with zero restarts.
- [x] The product owner explicitly deferred the remaining uninterrupted 86,400-second qualification. The deferred acceptance criterion is recorded in EPIC-611 and gates broader availability, scale and production-readiness claims.
- [x] The Helm quickstart was reproduced on a separate clean kind cluster: migrations, server and worker rollouts, health, metrics and the checked-in Luna → Kubernetes Job → HTTP flow all passed.
- [x] The exact release-candidate image passed deployed cron occurrence and structured `core.log` checks; live `/health` returned version `0.2.0` and `/metrics` exposed AMESH request metrics.
- [x] Final suite: 47 tests pass at 80.47% branch coverage with live Luna, PostgreSQL and kind gates enabled.
- [x] Ruff formatting/lint and strict mypy pass for 69 formatted files and 42 typed source files.
- [x] `uv lock --check`, generated contracts, planning regeneration/drift, backlog validation, clean-room validation, compilation, Docker Compose rendering, Helm lint/render and `git diff --check` pass.
- [x] `uv build` creates `amesh-0.2.0.tar.gz` and `amesh-0.2.0-py3-none-any.whl`; isolated wheel import and `uvx` CLI checks both report `0.2.0`; the image runs as numeric user `100:101`.
- [x] EPIC-001, EPIC-108, EPIC-606 and EPIC-611 record the W8 evidence and deferral through canonical generation; all broad epic states remain open.
- [x] Path-back reconciliation did not mark any broad URS requirement Verified: the MVP provides evidence-bearing slices but does not satisfy the complete acceptance criteria of those roadmap requirements.

Adversarial pass: the accepted partial soak continuously removed the active task pod, periodically replaced the API server and recovery worker, and independently revalidated every persisted execution after fencing contention.

Not covered: the deferred uninterrupted 24-hour run, HA, profile-M load, multi-node control plane, backup/restore, cross-distribution qualification and other broader EPIC-611 requirements. These are not claimed by `v0.2.0-mvp`.

Verdict: PASS — W8 closed under the product-owner-amended exit; full-duration qualification remains open in EPIC-611.
