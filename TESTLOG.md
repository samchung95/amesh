# Test Log

## EPIC-105: Concurrency, admission control and fairness — 2026-08-22

Spec source: Agent Hotel card `c17` and canonical `backlog/epics.json` EPIC-105 DoD.

Verified with `uv`, Python 3.13 and PostgreSQL 17 on a fresh 19-migration database:

- [x] Execution admission resolves global, tenant, namespace, flow, worker-group and expression-keyed limits atomically and persists an explainable decision for every request.
- [x] `QUEUE`, `CANCEL`, `FAIL`, `REPLACE` and `SKIP` behaviors have deterministic execution outcomes; global replacement is rejected by the DSL contract.
- [x] Queue ordering combines explicit priority with one-point-per-minute aging, reports stable queue positions and admits waiting work after capacity is released or an expired lease is reconciled.
- [x] Task admission serializes dynamically keyed work and preserves configured priority and worker-group routing through the durable queue.
- [x] Tenant concurrent-execution, queued-execution, log-byte, storage-byte and API-request budgets are enforced with transactionally updated counters.
- [x] Admission explanation, tenant diagnostics and bounded reconciliation are available through authenticated REST endpoints.
- [x] Focused admission integration suite: 6 passed. Full uninstrumented suite: 164 passed, 4 environment-gated tests skipped.
- [x] Branch-coverage suite passed at 82.59%, above the 75% gate, with the instrumentation-sensitive 50 ms execution-deadline case excluded and verified separately without coverage. That unchanged timing test passes uninstrumented and was not redesigned under the requested defer-and-move-forward policy.
- [x] Ruff format/lint, strict mypy, lockfile, generated contracts/planning, backlog, clean-room, compile and Compose configuration gates pass.

Adversarial pass: simultaneous contenders, exhausted capacities, all terminal behaviors, replacement victim cancellation, priority aging, expired leases, dynamic task keys, quota exhaustion and cross-tenant admission diagnostics fail closed or remain tenant isolated as specified.

Product-owner-approved deferrals remain owned by existing epics: the 24-hour profile-M soak is EPIC-611, and the full reference dashboard/alert package is EPIC-607.

Verdict: PASS — EPIC-105 requirements URS-F-0124 through URS-F-0131 are verified.

## EPIC-004: Flow DSL, YAML model and schema — 2026-08-22

Spec source: Agent Hotel card `c5` and canonical `backlog/epics.json` EPIC-004 DoD.

Verified with `uv`, Python 3.13 and PostgreSQL 17:

- [x] YAML 1.2 and JSON documents normalize to the same explicit `amesh.flow/v1` canonical IR and semantic hash; canonical data includes the defaulted `apiVersion`.
- [x] Required fields, field types, canonical identifiers, duplicate input/trigger/task ids, sibling references, nested dependencies and cycles fail deterministically.
- [x] Round-trip edits retain existing comments, ordering, quoting and indentation where practical; JSON edits render as stable indented JSON.
- [x] The resource registry validates core and plugin-defined task, trigger and input configuration with JSON Schema Draft 2020-12 and emits deterministic editor metadata.
- [x] The canonical IR covers namespace, flow id, description, labels, inputs, variables, tasks, triggers, errors, `finally`, outputs and `x-` extensions.
- [x] Parser, structural, reference and resource-schema failures return stable codes, paths, one-based source ranges and remediation hints. Duplicate YAML keys fail with the second-key location.
- [x] Unknown unprefixed flow fields fail; `x-` fields remain canonical and semantic. Comments, key order and YAML layout do not affect semantic hashes.
- [x] Generated `flow.schema.json`, `resource-catalog.json`, execution schemas and OpenAPI output match implementation types.
- [x] A 5,003-line flow measured 0.598 seconds p95 across 10 uninstrumented local runs, below the 1-second target. The pytest performance case uses `no_cover` so coverage tracing does not invalidate the latency measurement.
- [x] Full suite with `AMESH_TEST_DATABASE_URL`: 91 passed, 4 environment-gated tests skipped, 80.29% branch coverage.

Adversarial pass: malformed and duplicate-key YAML, non-object roots, missing fields, invalid identifiers, duplicate ids, missing dependencies, dependency cycles, unknown resource types, wrong plugin property types, unsupported plugin properties and unknown core fields fail closed with machine-readable evidence.

Shared `URS-NFR-USABILITY-001` remains In Progress until EPIC-405 integrates the server contract into the editor. Shared `URS-NFR-MAINTAINABILITY-002` remains In Progress until EPIC-300/400/610 complete their plugin, API and upgrade compatibility owners.

Verdict: PASS — EPIC-004 requirements URS-F-0029 through URS-F-0036 and its implemented contributions to both shared NFRs are verified.

## EPIC-503: Multi-tenancy and resource isolation — 2026-08-21

Spec source: Agent Hotel card `c4` and canonical `backlog/epics.json` EPIC-503 DoD.

Verified with `uv` and PostgreSQL 17:

- [x] Multi-tenant mode requires `X-Amesh-Tenant`; single-tenant mode alone may use the configured default. Unknown, suspended, tombstoned and inaccessible tenants return generic responses without disclosing tenant existence.
- [x] Instance administrators can create, list, inspect, update, suspend, export, tombstone and restore tenants. Every lifecycle operation writes explicit tenant audit evidence marked `superAdmin: true`; ordinary viewer credentials are denied from every tenant-administration route.
- [x] Tenant policy persists retention, storage budget, encryption-key and identity-provider references, plugin allowlists, feature flags, execution concurrency and worker groups. Execution creation enforces the feature flag, plugin allowlist and concurrent-run quota.
- [x] Tenant storage keys are rooted at immutable `tenants/<slug>/` prefixes. Schedulers and recovery workers enumerate only active tenants assigned to their configured worker group.
- [x] Execution, task-run, queue, inbox and outbox interfaces require tenant context. Their PostgreSQL adapters use a transaction-local tenant UUID and `SET LOCAL ROLE amesh_runtime` before accessing forced-RLS tables.
- [x] The runtime role is `NOLOGIN NOBYPASSRLS`; a clean database exposes 18 tenant-isolation policies. A non-superuser, non-owner login with only runtime-role membership resolves its tenant and sees only that tenant, while direct table access and a cross-tenant insert are rejected.
- [x] Queue claim, extension, acknowledgement, release, outbox publication and wait paths are tenant scoped. Tenant-specific notification channels prevent another tenant's enqueue from waking a waiter.
- [x] Same-name flows coexist in separate tenants; flow and execution reads do not cross tenants; inaccessible and nonexistent tenant probes return identical bodies; tenant slugs do not appear as metric labels.
- [x] Migrations 0006–0009 applied to the existing database. A fresh temporary database applied migrations 0001–0009, recorded nine checksums, created the non-bypass runtime, restricted resolver and tenant-administration roles, installed 18 RLS policies and replaced the shared notification function.
- [x] Full suite: `pytest --cov=amesh --cov-branch --cov-report=term-missing` — 82 passed, 4 environment-gated tests skipped, 79.65% branch coverage.
- [x] Ruff format/lint, strict mypy, uv lock, generated OpenAPI/planning, backlog, clean-room, compile, source/wheel build, Compose configuration and Helm 4 lint/render gates pass. The build reports only the pre-existing setuptools license-metadata deprecation warnings.

Adversarial pass: missing tenant context, malformed/unknown/suspended tenant context, an active but unauthorized tenant, cross-tenant RLS reads and writes, cross-tenant queue claims and notifications, plugin denial, disabled execution policy, exhausted tenant concurrency and every unauthorized tenant-administration route fail closed.

Not covered: search projections, cloud object-store adapters and their lifecycle controls, external identity-provider protocols, database backup/restore qualification and an independent pre-GA penetration test. Those remain assigned to EPIC-604/605, EPIC-502 and the HA/DR/release epics. Shared `URS-NFR-SECURITY-001` therefore remains In Progress.

Verdict: PASS — EPIC-503 requirements URS-F-0518 through URS-F-0525 and its implemented contribution to shared URS-NFR-SECURITY-001 are verified.

## EPIC-501: Service accounts, API tokens and credentials — 2026-08-21

Spec source: Agent Hotel card `c3` and canonical `backlog/epics.json` EPIC-501 DoD.

Verified with `uv` and PostgreSQL 17:

- [x] Service-account principals receive direct and group-derived instance, tenant and namespace roles through the existing authorization policy.
- [x] UUIDv7 opaque tokens contain 256 random bits; only keyed HMAC-SHA-256 digests plus name, scopes, audience, expiry, status, quota and last-use metadata persist.
- [x] Issue and rotation responses disclose a secret once; metadata lists expose neither the secret nor digest; current and replacement tokens both authenticate during a bounded overlap.
- [x] Single-token revocation recursively revokes derived children. Principal-wide revocation increments a credential epoch and invalidates every token on its next request.
- [x] Worker/plugin exchange produces a different-audience, scope-narrowed token capped at one hour; an ineligible principal or broadened scope fails deterministically.
- [x] Every token owns an independent PostgreSQL fixed-window quota. Exhaustion returns HTTP 429 without exhausting another token.
- [x] Issue, exchange, use, authentication failure, rotation and revocation write audit evidence containing no token plaintext. The credential table has no plaintext-token column.
- [x] Production rejects the development pepper; current/previous pepper rollover accepts old tokens while new tokens use only the new pepper. Helm renders both values from existing Secret keys without an image rebuild.
- [x] Service accounts have no interactive-login route; durable service-account tokens authenticate outside development, while the development bootstrap token is rejected there.
- [x] Every new credential endpoint has negative permission coverage.
- [x] Migration 0005 applied to the existing database. A fresh temporary database applied migrations 0001–0005 and contained both credential tables, the principal credential epoch and five migration records.
- [x] Full suite: `pytest --cov=amesh --cov-report=term-missing` — 76 passed, 4 environment-gated tests skipped, 79.14% branch coverage.
- [x] Ruff formatting/lint, strict mypy, uv lock, generated OpenAPI/planning, backlog, clean-room, compile, Compose and Helm lint/render gates pass.

Adversarial pass: wrong audience, digest mismatch after pepper rollover, exhausted quota, scope broadening, parent revocation, principal-wide revocation, development token in production and every unauthorized administration route fail closed without token disclosure.

Not covered: human login/browser sessions, external identity providers and general tenant provisioning. Those remain assigned to EPIC-403, EPIC-502 and EPIC-503.

Verdict: PASS — EPIC-501 requirements URS-F-0502 through URS-F-0509 and its contributions to shared URS-NFR-SECURITY-002/006 are verified.

## EPIC-500: Users, groups, roles, bindings and authorization — 2026-08-21

Spec source: Agent Hotel card `c2` and canonical `backlog/epics.json` EPIC-500 DoD.

Verified with `uv` and PostgreSQL 17:

- [x] Typed resource/action permissions cover view, create, update, delete, execute, manage and use with explicit allow/deny effects.
- [x] UUIDv7 principals and bindings support users, groups, service accounts, workers and plugins at instance, tenant and namespace scopes.
- [x] Namespace grants inherit down dotted namespace trees; explicit denies override grants and declared boundaries stop parent inheritance.
- [x] REST resource endpoints authorize server-side with tenant context and generic denials; CLI requests send `X-Amesh-Tenant`; service-account, worker and plugin actors use the same policy service. Realtime/UI surfaces do not yet exist and must consume this boundary when implemented.
- [x] PostgreSQL statement triggers increment a monotonic policy version for every principal, membership, role, permission, binding or boundary mutation. Cached allows are missed immediately after binding and group-membership revocation.
- [x] The administrator-only explanation API returns reason codes, policy versions and matched roles; ordinary 403/404 responses do not disclose inaccessible tenant, namespace or resource details.
- [x] Six immutable built-in roles are seeded. Deleting a binding or group membership that would remove the final effective instance administrator rolls back with HTTP 409.
- [x] Every current product endpoint is catalogued in API acceptance coverage: health, readiness, metrics and content-only flow validation are intentionally anonymous; every resource-bearing operation has negative permission and tenant-isolation evidence. No realtime stream exists yet.
- [x] Authorization administration mutations append actor/resource evidence to `audit_events`.
- [x] Migration 0004 applied to the existing database. A fresh temporary database applied migrations 0001–0004 and contained policy version 1 plus all six built-in roles.
- [x] Full suite: `pytest --cov=amesh --cov-report=term-missing` — 68 passed, 4 environment-gated tests skipped, 78.54% branch coverage.
- [x] Focused evaluator measurement: 100,000 cached-input pure decisions in 0.164400 seconds (1.64 microseconds/decision, 608,273 decisions/second) on the development workstation; this is not a distributed production throughput claim.
- [x] Ruff formatting/lint, strict mypy and generated OpenAPI snapshot gates pass.

Adversarial pass: cross-tenant headers, viewer writes, every administrative surface, mismatched binding principal types, explicit deny, namespace-boundary crossing, stale cached grants, final direct administrator removal and final group-derived administrator removal all fail deterministically.

Not covered: durable login/session credentials, API-token lifecycle, external identity providers, tenant provisioning/isolation and graphical UI consumption. These remain explicitly assigned to EPIC-403, EPIC-501, EPIC-502, EPIC-503 and EPIC-404.

Verdict: PASS — EPIC-500 requirements URS-F-0494 through URS-F-0501 and its authorization contribution to URS-NFR-USABILITY-002 are verified.

## EPIC-002: Canonical resource model and identifiers — 2026-08-21

Spec source: Agent Hotel card `c1` and canonical `backlog/epics.json` EPIC-002 DoD.

Verified with `uv` and PostgreSQL 17:

- [x] Canonical typed natural keys cover tenants, namespaces, flows, revisions, task runs, triggers, workers, plugins and assets; DSL flow/input/task/trigger IDs use the same validators.
- [x] Identifier syntax, the internal reserved prefix, 128-character boundary, dotted namespaces, lowercase tenant slugs and case-preserving behavior have positive and rejected-input tests.
- [x] New execution, task-run, attempt, revision, event, correlation and worker identities use monotonically sortable RFC 9562 UUIDv7 values; PostgreSQL integration verifies persisted UUID versions.
- [x] Managed-resource metadata represents labels, annotations, timezone-aware timestamps, actors, resource versions and active/archived/tombstoned lifecycle state.
- [x] Versioned metadata revisions reject stale expected versions; REST flow writes return an ETag, accept matching `If-Match`, and reject stale tags with HTTP 412.
- [x] Archive, tombstone and restoration transitions increment resource versions and reject invalid same-state transitions; hard deletion remains a retention operation by design.
- [x] Compact sorted UTF-8 JSON produces mapping-order-independent hashes and ETags and rejects non-finite numbers.
- [x] Migration 0003 adds canonical metadata to current managed PostgreSQL resources. A fresh temporary database applied migrations 0001–0003 in order and exposed all expected flow metadata columns.
- [x] Generated flow schema and OpenAPI contracts match the code.
- [x] A real server boot on port 28999 returned `health=ok`, version `0.2.0`, and OpenAPI title `AMESH`; the verified process was stopped after the probe.
- [x] Full suite: `pytest --cov=amesh --cov-report=term-missing` — 53 passed, 4 environment-gated tests skipped, 76.11% branch coverage.
- [x] `ruff format --check`, `ruff check`, strict `mypy`, `uv lock --check`, contract generation, backlog validation, clean-room and build gates pass.

Adversarial pass: malformed/overlength identifiers, non-lowercase tenants, empty namespace segments, internal-prefix IDs, stale resource versions, stale ETags, invalid lifecycle transitions and NaN canonicalization all fail deterministically.

Not covered: user/group authorization policy, tenant isolation enforcement and UI consumption of these contracts. Those belong to the declared dependent epics EPIC-500, EPIC-503 and EPIC-404 rather than EPIC-002.

Verdict: PASS — EPIC-002 requirements URS-F-0015 through URS-F-0021 verified.

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

## EPIC-005: Expression and templating engine — 2026-08-22

Spec source: `backlog/epics/epic-005-expression-and-templating-engine.md` and ADR-022.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] `ExpressionEngine` provides a storage-independent compile, render, preview, task-render and condition adapter contract.
- [x] Native scalar, collection and object rendering covers flow, execution, task, task-run, trigger, input, output, variable, label, namespace, secret and key-value contexts.
- [x] The version-pinned `kestra-pebble/1.3.30-subset-1` corpus passes 12 syntax, control-flow, filter, conversion, date and function cases.
- [x] Syntax and AST validation raise compile errors separately from missing runtime values, invalid conversions and sandbox denials.
- [x] Deterministic tests enforce template, AST, context-memory, collection, nesting, recursion, output and elapsed-time bounds.
- [x] Secret-derived values remain available to task execution but are redacted from previews, expression errors, representations and `core.log` output.
- [x] A PostgreSQL execution proves the executor populates the documented context and renders a dependent task from upstream output.
- [x] A representative four-value render measured 0.2222 ms median and 0.2324 ms p95 over 1,000 warmed in-process renders.
- [x] Full suite: 104 passed, 4 environment-gated tests skipped, 80.05% branch coverage.
- [x] Ruff formatting and lint, strict mypy, backlog validation, clean-room validation, compilation and generated-contract drift gates pass.

Adversarial pass: unsafe attribute access, oversized input/output, excessive recursion, an elapsed deadline, missing values and secret-bearing conversion failures are rejected without exposing the secret.

Compatibility boundary: the checked-in subset is complete for this epic; it does not claim every Pebble construct or externally effectful Kestra function. Those gaps are explicit in `docs/architecture/expressions.md` and require a newly versioned corpus.

Verdict: PASS — EPIC-005 closed.

## EPIC-404: Web UI shell, navigation and accessibility — 2026-08-22

Spec source: `backlog/epics/epic-404-web-ui-shell-navigation-and-accessibility.md`, ADR-023 and `frontend/DESIGN.md`.

Verified with Node 22.22.2, npm 10.9.7, Chromium 151, Python 3.13.12 and PostgreSQL 17:

- [x] The React control room navigates dashboard, flows, executions, namespaces, assets, apps, plugins and administration routes with desktop and 768 px tablet layouts.
- [x] `GET /api/v1/ui/session` derives action visibility from server authorization decisions; denied direct routes render a deterministic policy state and the API remains the enforcement boundary.
- [x] Browser history, reloaded execution deep links, tenant/namespace context and locally saved execution views pass browser acceptance.
- [x] Global live-resource search, `Ctrl+K` keyboard selection, notifications and retry recovery pass browser acceptance.
- [x] English/Simplified Chinese switching, explicit IANA time zones and locale-sensitive date/number unit fixtures pass.
- [x] The skip link, focus transfer, compact-rail accessible names and semantic landmarks pass keyboard/accessibility-tree assertions; axe reports no critical or serious WCAG 2.2 AA findings for the supported dashboard workflow.
- [x] The browser network test observes only `http://127.0.0.1:4173`; telemetry is disabled by default and fonts are bundled.
- [x] Eight frontend unit tests pass at 100% coverage for the isolated API/format units; five browser cases pass across desktop and tablet, with five deliberate cross-project skips.
- [x] The Python suite passes with 107 tests and four environment-gated skips against PostgreSQL.
- [x] ESLint, TypeScript/Vite build, Ruff formatting/lint, strict mypy, uv lock, planning/backlog, clean-room, compilation, Compose and diff gates pass.
- [x] `amesh:epic-404` builds successfully with Node and uv stages and contains the compiled SPA served by FastAPI.

Adversarial pass: an unbound UI session receives the same concealed tenant 404; denied administration remains unreachable by direct URL; a failed flow request recovers through retry; missing static API paths remain 404 instead of falling back to HTML; and the offline browser test makes no external request.

Qualification boundary: Chromium desktop and tablet are automated. Firefox, Edge, Safari, iPadOS and NVDA/VoiceOver remain in the pre-GA manual matrix, and the shared accessibility/privacy NFRs remain In Progress for their other owning epics.

Verdict: PASS — EPIC-404 closed.

## EPIC-007: Execution event model and state machine — 2026-08-22

Spec source: `backlog/epics/epic-007-execution-event-model-and-state-machine.md` and `docs/architecture/execution-semantics.md`.

Verified with Python 3.13.12 and PostgreSQL 17:

- [x] Immutable execution/task-run commands, events, snapshots, accepted transitions and rejected transitions validate as typed versioned contracts; all introduced public contracts have checked-in JSON Schemas.
- [x] Pure transition tables enforce legal execution and task-run lifecycles without infrastructure imports; illegal transitions leave the input snapshot unchanged.
- [x] Stable idempotency keys deduplicate commands/events and repeated persisted task results produce one logical effect.
- [x] Ordered execution and task histories replay to their canonical snapshots; 100 repeated execution replays are byte-equivalent.
- [x] Execution event schema v1 upcasts to v2 with a stable key/reason, while unsupported versions fail explicitly.
- [x] PostgreSQL persists execution/task actor, reason, correlation and causation fields and durable execution/task rejection evidence under forced tenant RLS.
- [x] Every inserted execution/task event creates one versioned outbox envelope in the same transaction; a forced rollback leaves the state version, event table and outbox unchanged.
- [x] A fresh database applies all 11 migrations and exposes `execution_event_outbox`, `task_run_event_outbox`, and forced RLS on both new evidence tables.
- [x] Full suite: 118 passed, four environment-gated tests skipped, 80.89% branch coverage.
- [x] Ruff formatting/lint, strict mypy, uv lock, generated schema/OpenAPI/planning drift, backlog validation, clean-room validation, compilation, Docker Compose rendering and diff checks pass.

Adversarial pass: stale epochs, stale task versions, illegal terminal transitions, repeated commands/events/results, unsupported event schemas, reordered state changes and forced transaction rollback are rejected or deduplicated without corrupting authoritative state.

Qualification boundary: live OpenRouter (`openai/gpt-5.6-luna`) and kind tests remain environment-gated because their credentials/context are absent. Helm was not rerun because the executable is unavailable and this epic changes no chart template. Shared reliability/maintainability NFRs remain In Progress for their remaining owners and distributed failover tests.

Verdict: PASS — EPIC-007 closed.

## EPIC-008: Metadata persistence and migrations — 2026-08-22

Spec source: `backlog/epics/epic-008-metadata-persistence-and-migrations.md` and
`docs/operations/metadata-storage.md`.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] Existing flow/revision/execution/task, tenant, authorization and credential repositories plus
  the new metadata port cover the declared repository owners for triggers, workers, execution logs,
  execution metrics and assets.
- [x] Flow application materializes immutable trigger definitions in the same tenant transaction;
  worker heartbeat and asset writes reject stale resource versions; log and metric foreign keys remain
  tenant-safe.
- [x] Runtime repository work uses explicit PostgreSQL `READ COMMITTED` transactions, migrations use
  `SERIALIZABLE` with an advisory lock, and the existing event-to-outbox rollback test proves state and
  publication atomicity.
- [x] `manifest.json` defines the exact contiguous migration order, mode, mixed-version compatibility
  and rollback guidance; the runner rejects checksum drift, unknown applied versions, unsupported
  PostgreSQL and unsafe contract DDL classified as online-compatible.
- [x] Migration 0012 adds forced tenant RLS, composite foreign keys, versioned identities and database
  constraints for execution, task-run, task-attempt and worker states; a direct invalid-state write is
  rejected by PostgreSQL.
- [x] `/ready` verifies connectivity and exact migration parity. Prometheus exports bounded database
  health, pool size/checkout, query duration, slow-query and applied/expected migration signals.
- [x] Two guarded ephemeral databases independently applied all 12 migrations, produced identical
  canonical schema and seed fingerprints, and returned no changes on a second application.
- [x] The metadata data inventory maps persisted fields to purpose, sensitivity and retention owner;
  retention execution remains with EPIC-608, so the shared privacy NFR remains In Progress.
- [x] Full suite: 123 passed, four environment-gated tests skipped, 82.14% branch coverage.
- [x] Ruff formatting/lint, strict mypy, generated OpenAPI/planning drift, backlog validation,
  clean-room validation, compilation, Compose rendering, uv lock and diff checks pass.

Adversarial pass: stale worker/asset versions, an invalid execution state, unlisted migrations,
checksum drift, absent migration parity and unsafe ephemeral-database names fail without silently
changing accepted metadata. The checked-in OpenRouter smoke default remains
`openai/gpt-5.6-luna`; its live test is environment-gated because no key is present.

Qualification boundary: multi-node PostgreSQL failover, backup/restore, retention purge and supported
release-to-release rolling upgrades remain in their dedicated later epics. They are not claimed by
EPIC-008.

Verdict: PASS — EPIC-008 closed.

## EPIC-009: PostgreSQL transport, inbox and transactional outbox — 2026-08-22

Spec source: `backlog/epics/epic-009-postgresql-transport-inbox-and-transactional-outbox.md`,
`docs/architecture/messaging.md` and `docs/architecture/postgresql-transport.md`.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] `DurableEnvelope` persists a versioned identity, type, tenant, partition, correlation,
  causation, timestamp, trace context and payload; its JSON Schema is checked in and drift-tested.
- [x] Reusing a queue or outbox message identity with changed immutable content is rejected, while an
  exact retry returns the original durable identity.
- [x] Event/outbox triggers publish only with their committed state transaction; forced rollback leaves
  state, event and outbox unchanged.
- [x] Consumer inbox insertion is idempotent. A subprocess crash after inbox commit causes lease
  redelivery with a higher fence and no duplicate logical effect.
- [x] Claim selection admits only the oldest non-terminal row per tenant/lane/partition, preventing a
  second execution/trigger message from overtaking its head under batched `SKIP LOCKED` claims.
- [x] Queue and outbox publication failures honor configurable positive attempt bounds. Exhaustion
  atomically creates forced-RLS dead-letter evidence containing source identity, schema, failure class,
  SHA-256 payload checksum, attempt count and error without duplicating the payload.
- [x] Authorized replay resolves the immutable quarantine record, resets the retained source for a new
  bounded cycle and rejects repeated or stale replay.
- [x] Tenant-authorized diagnostics report eligible/outbox lag, depth, claims, expired claims,
  redeliveries, poison rows, pending dead letters and outbox retry/dead-letter totals.
- [x] A fresh ephemeral database applies all 13 migrations and produces the same canonical schema and
  seed fingerprints as an independent fresh database; a second application is empty.
- [x] Full suite: 126 passed, four environment-gated tests skipped, 82.29% branch coverage.
- [x] Ruff formatting/lint, strict mypy, generated contracts/planning drift, backlog validation,
  clean-room validation, compilation, Compose rendering, uv lock and diff checks pass.

Adversarial pass: changed-content duplicate IDs, concurrent partition candidates, expired fences,
process death after inbox commit, exhausted queue/outbox retries and repeated dead-letter replay are
rejected, serialized or quarantined without losing the durable source row. The checked-in OpenRouter
smoke default remains `openai/gpt-5.6-luna`; its live test is environment-gated because no key is
present.

Qualification boundary: multi-node PostgreSQL failover, cross-region delivery and scale-profile chaos
remain with EPIC-601/603/611. External APIs still require plugin/task idempotency, probe or compensation;
AMESH does not claim generic exactly-once external side effects.

Verdict: PASS — EPIC-009 closed.

## EPIC-100: Executor and orchestration reducer — 2026-08-22

Spec source: `backlog/epics/epic-100-executor-and-orchestration-reducer.md` and
`docs/architecture/execution-semantics.md`.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] Manual, API, scheduled, event and subflow launch sources use one typed contract and persist
  source-specific trigger context; concurrent scheduled occurrences retain one execution identity.
- [x] The pure orchestration reducer derives dependency-ready tasks, retry waiting, terminal success
  and stable failed/blocked diagnostics in canonical flow order; 100 repeated reductions are identical.
- [x] Sequential, parallel and dependency-driven tasks execute from committed task-run state. A false
  condition records a skipped success without invoking the handler or emitting a dispatch command.
- [x] Eligible `TaskRunStarted` events emit `DispatchTaskRun` on `task-dispatch`; task results,
  downstream task events and terminal execution events remain transactionally coupled to the outbox.
- [x] Restart recovery resumes without rerunning completed tasks, and a recovered failed prerequisite
  terminates the unsatisfiable graph with an actionable immutable execution event.
- [x] Two PostgreSQL executor repositories racing for one task produce one running attempt, one
  dispatch and one deterministic loser conflict; stale execution epochs remain fenced.
- [x] A guarded fresh database applied all 14 migrations and all 20 focused executor/scheduler/API
  tests passed.
- [x] Full suite: 130 passed, four environment-gated tests skipped. Coverage excluding tests marked
  `no_cover`: 82%.
- [x] Ruff formatting/lint, strict mypy, planning generation, backlog validation, clean-room,
  compilation, generated-contract, Compose, uv lock and diff gates pass.

Adversarial pass: duplicate launch occurrences, duplicate task results, competing executor claims,
false conditions, failed prerequisites, stale epochs, restart recovery and forced transaction rollback
produce one logical owner/effect or deterministic persisted diagnostics. The checked-in OpenRouter
smoke model remains `openai/gpt-5.6-luna`; its live test is environment-gated without a key.

Qualification boundary: the fixed-topology 60-minute distributed throughput target remains unclaimed
until the deployment qualification epic. Duplicate subflow-delivery qualification remains shared with
EPIC-103; EPIC-100 supplies the typed subflow launch boundary and deterministic executor behavior.

Verdict: PASS — EPIC-100 closed.

## EPIC-102: Scheduler and temporal correctness — 2026-08-22

Spec source: `backlog/epics/epic-102-scheduler-and-temporal-correctness.md` and
`docs/architecture/scheduler-and-triggers.md`.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] `core.cron` and ISO-8601 `core.interval` schedules validate explicit IANA timezones. Cron
  calendar calculation skips nonexistent Berlin wall time and selects the earliest instant once for
  the autumn overlap; interval schedules use a documented elapsed-time anchor.
- [x] Migration 0015 adds tenant-isolated next-fire cursors, last-decision evidence, database-time
  leases and monotonic fencing tokens. A stale owner cannot complete after lease expiry and takeover.
- [x] Skip, catch-up, coalesce and backfill-required policies consume a bounded persisted missed range;
  a restarted worker does not reconsider a completed occurrence.
- [x] Flow/trigger disabled state, pause, aware start/end bounds and boolean conditions are checked
  before launch. Stable revision-scoped occurrence keys deduplicate concurrent and restarted owners.
- [x] The flow-authorized schedule-preview endpoint returns 1–100 future occurrences and explains
  eligibility without changing the durable cursor.
- [x] Two scheduler engines racing one PostgreSQL row produce one owner and one execution. Worker
  database cycles retry after connection interruption so a post-failover connection can be established.
- [x] A guarded fresh database applied all 15 migrations. Full suite: 142 passed, four
  environment-gated tests skipped; coverage excluding `no_cover` tests: 82.50%.
- [x] Frontend suite: eight tests passed with 100% reported coverage and the production Vite build
  completed.
- [x] Ruff formatting/lint, strict mypy, planning generation, backlog validation, clean-room,
  compilation, generated-contract, Compose, uv lock and diff gates pass.

Adversarial pass: DST gaps and overlaps, five missed occurrences under every policy, disabled/paused/
ended/false-condition schedules, concurrent owners, expired fences, scheduler restart, repeated
occurrence identity and a simulated database connection interruption produce a deterministic decision,
one logical execution or a retry without accepting a stale cursor mutation. The checked-in OpenRouter
smoke default remains `openai/gpt-5.6-luna`; its live test is environment-gated without a key.

Qualification boundary: EPIC-102 records `BACKFILL_REQUIRED`; EPIC-106 owns the first-class backfill
resource and lifecycle. Fixed-topology p99 scheduling load and live multi-node PostgreSQL failover remain
shared NFR qualification for the scale and HA epics.

Verdict: PASS — EPIC-102 closed.

## EPIC-101: Worker protocol, leases and heartbeats — 2026-08-22

Spec source: `backlog/epics/epic-101-worker-protocol-leases-and-heartbeats.md` and
`docs/architecture/workers-and-runners.md`.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] Protocol-v1 registration preserves worker identity by tenant/group/instance and advertises
  version, task capabilities, runner types, labels and logical capacity; incompatible protocol or
  runner registrations do not receive work.
- [x] A PostgreSQL transaction claims the durable dispatch queue row and current task attempt with
  one worker, database-time lease and monotonic fence while enforcing capacity and compatibility.
- [x] Fenced heartbeats renew both claims and persist worker/task progress, resource usage and
  cancellation acknowledgement. Stale heartbeats and completions are rejected.
- [x] A worker can drain without receiving new work while a live in-flight claim completes and
  consumes its queue row atomically. Expired claims deterministically requeue or fail/quarantine.
- [x] Authorized `/api/v1/workers` inventory exposes liveness, compatibility, capacity, claimed work
  and utilization; drain uses an expected resource version and rejects stale or unauthorized calls.
- [x] Pull polling and tenant-scoped PostgreSQL notification wake-up use the same durable repository;
  notification remains an optimization over the queue source of truth.
- [x] A guarded fresh database applied all 16 migrations. Full suite: 144 passed, four
  environment-gated tests skipped.
- [x] Frontend suite: eight tests passed with 100% reported coverage and the production Vite build
  completed.

Adversarial pass: incompatible registrations, wrong runners, capacity exhaustion, stale worker
versions, expired claims, reassignment, delayed old-owner completion, explicit fail policy, repeated
drain and read-only drain authorization all produce no accepted stale mutation. The checked-in
OpenRouter smoke default remains `openai/gpt-5.6-luna`; its live test is environment-gated without a
key.

Qualification boundary: the Profile-M target of 50 task starts/second for 60 minutes and live
network-partition/PostgreSQL-failover qualification remain shared NFR work for EPIC-603/601/611.

Verdict: PASS — EPIC-101 closed.

## EPIC-104: Retries, timeouts and execution interventions — 2026-08-22

Spec source: `backlog/epics/epic-104-retries-timeout-pause-cancellation-kill-and-restart.md`
and `docs/architecture/execution-semantics.md`.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] Retry policies enforce attempt count, delay, exponential backoff, maximum interval and stable
  per-attempt jitter; retryable, non-retryable, cancelled, timed-out and infrastructure categories
  are persisted and drive retry eligibility.
- [x] Task handlers use monotonic asyncio deadlines. Execution deadlines are persisted from
  PostgreSQL time and atomically fail/fence active attempts when due.
- [x] Pause admits no new runnable task, resume continues from committed state, and completed task
  output and attempt counts remain unchanged.
- [x] Cancellation first persists a worker-visible request and grace deadline. Force cancellation is
  rejected before that deadline, succeeds after it, invalidates the active attempt and rejects a late
  result.
- [x] Checkpoint restart resets the selected task and its descendants, preserves successful upstream
  output, advances the execution epoch and rejects a stale pre-restart attempt result.
- [x] Authorized preview/apply/history endpoints report affected and preserved tasks, destructive
  consequences, current version/epoch and immutable actor/reason history; a stale preview is rejected.
- [x] A guarded fresh database applied all 17 migrations. Full suite: 151 passed, four
  environment-gated tests skipped; coverage excluding tests marked `no_cover`: 82.56%.
- [x] Frontend suite: eight tests passed with 100% reported coverage; production Vite build and ESLint
  completed.
- [x] Ruff formatting/lint, strict mypy, backlog generation/validation, clean-room, compilation,
  generated-contract, Compose, uv lock and diff gates pass.

Adversarial pass: invalid failure types, bounded retry jitter, execution and task timeouts, pause
admission, force-before-deadline, stale optimistic previews, late post-cancel completion and late
pre-restart completion produce deterministic persisted outcomes without accepting stale work. The
checked-in OpenRouter smoke default remains `openai/gpt-5.6-luna`; its live test is environment-gated
without a key.

Qualification boundary: scheduler, worker and executor temporal decisions use PostgreSQL time and
monotonic local deadlines. Live multi-node plus/minus-30-second clock-skew and PostgreSQL failover
qualification remains shared with EPIC-601; the mapped reliability NFR remains In Progress.

Verdict: PASS — EPIC-104 closed.

## EPIC-107: Subflows, dependencies and system flows — 2026-08-22

Spec source: `backlog/epics/epic-107-subflows-dependencies-and-system-flows.md` and
`docs/architecture/execution-semantics.md`.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] `core.subflow` resolves active or pinned child revisions and atomically persists an idempotent,
  tenant-isolated relationship to the parent execution, task run and attempt.
- [x] Synchronous, asynchronous and detached modes execute with distinct waiting/propagation behavior;
  the API schedules independent children after the parent response and the durable coordinator resumes
  incomplete descendants.
- [x] Typed inputs, inherited and invocation labels, correlation/trace context, output mappings and
  artifact mappings cross the parent/child boundary. Draft-2020-12 schemas reject invalid mapped
  results before the parent task commits.
- [x] Explicit failure, cancellation, pause and restart policy tests cover propagation and prior-child
  reuse. Recursive identities, excessive depth, invalid inputs and invalid output schemas fail
  deterministically.
- [x] System flows require tenant-management authority. Parent and child namespace execution checks
  are independent; denied cross-namespace/system launches create no parent execution. Relationship
  records preserve both namespaces, the initiating actor and pinned revisions.
- [x] Authorized REST endpoints expose child relationships and a child's parent relationship. The API
  end-to-end test applies ordinary and system children in separate namespaces and completes a
  post-response asynchronous child.
- [x] A guarded fresh database applied all 18 migrations. Full suite: 156 passed, four
  environment-gated tests skipped. Coverage excluding the `no_cover` performance case: 155 passed,
  four skipped, one deselected, 83% branch coverage. The 5,000-line validation performance gate also
  passed without instrumentation.
- [x] Frontend suite: eight tests passed with 100% reported coverage; production Vite build and ESLint
  completed.
- [x] Ruff formatting/lint, strict mypy, uv lock, planning/backlog generation and validation,
  clean-room, compilation, generated-contract, Compose and diff gates pass.

Adversarial pass: selected versus active revision, duplicate task-attempt invocation, invalid input
types, invalid mapped output schemas, direct recursion, cancelled and paused children, restart with
child replay disabled, detached child failure, cross-namespace denial and privileged system-flow denial
produce deterministic persisted results. The checked-in OpenRouter smoke default remains
`openai/gpt-5.6-luna`; its live test is environment-gated without a key.

Qualification boundary: `execution_subflows` is the authoritative recovery input for unfinished child
trees. Broad stuck-execution discovery and automated invariant repair remain owned by EPIC-108 rather
than being duplicated in this epic.

Verdict: PASS — EPIC-107 closed.
