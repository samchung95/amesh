# Test Log

## EPIC-834 lossless durable agent-progress ingress — 2026-09-01

Spec sources: Agent Hotel cards `c174`–`c178`, EPIC-834 and ADR-071.

- [x] Domain regression accepts 64 frames at one timestamp with default limits and produces no
  truncation; optional explicit ceilings reject before acceptance instead of writing a marker.
- [x] PostgreSQL regressions persist 24 burst frames as individual journal/evidence rows, prove
  exact receipts and cursor order, reject conflicting identities, retain exact retries across
  repository recreation and append only one durable `FAILED` active-segment closure.
- [x] Historical `TRUNCATED` rows remain readable and exactly retryable, while a newly submitted
  marker is rejected as historical-only. Provider-stream and Pi harness failure tests invoke the
  durable closure boundary after accepted progress.
- [x] Focused Ruff and strict mypy passed. Planning regeneration and validation report 131 epics,
  837 functional requirements, 63 non-functional requirements and 1,000 traceability links;
  generated contracts and strict MkDocs/diagram rendering passed.
- [x] `.\scripts\verify-local.ps1 -Suite all` passed: 909 backend tests with 181 expected skips and
  four documented deselections; 122 frontend tests; two application and eight documentation
  Playwright journeys; six Pi worker tests and all 27 conformance cases; clean-room/REUSE checks;
  production-image probing; and local repository plus four-SDK packaging.

Verdict: PASS — valid progress is complete and durable with producer backpressure; runtime
truncation is removed and caught producer failures close active progress truthfully when the journal
is available.

## EPIC-833 durable nonfatal agent-progress backpressure — 2026-09-01

Spec sources: Agent Hotel cards `c169`–`c172`, GitHub issue #14, EPIC-833 and ADR-068.

- [x] A focused PostgreSQL regression reproduces the prior rate overflow, asserts normal
  `(duplicate=false, truncated=false)`, exact retry `(true, false)` and first/later/concurrent
  overflow `(false, true)` receipts, and proves one deterministic marker across repository
  recreation while conflicting source reuse still fails.
- [x] The same regression transitions the truncated session to `SUCCEEDED` and verifies a durable
  schema-valid final result, 321 tokens, USD 0.045, one tool call, its tool result and correlated
  execution evidence.
- [x] `docker compose -f compose.verify.yaml run --rm --entrypoint sh verify -lc
  'AMESH_TEST_DATABASE_URL="$DATABASE_URL" uv run --frozen --extra runtime --extra dev pytest -q
  tests/adapters/postgres/test_agent_session_repository.py'` passed all three repository tests.
- [x] `uv run --extra runtime --extra dev pytest -q tests/domain/test_agent_progress.py
  tests/adapters/test_agent_session_harness.py tests/tasks/test_bounded_agent_tasks.py
  tests/tasks/test_agent_sessions.py` passed 95 tests with one expected live-provider skip.
- [x] Focused Ruff and strict mypy passed; backlog validation reports 130 epics, 837 functional
  requirements, 63 non-functional requirements and 1,000 trace links; MkDocs built strictly and the
  generated-contract test passed.
- [x] `.\scripts\verify-local.ps1 -Suite all` passed: 907 backend tests with 180 expected skips,
  122 frontend tests, two application and eight documentation Playwright journeys, six Pi worker
  tests, all 27 Pi conformance cases, clean-room/REUSE checks, production-image probing and local
  repository plus four-SDK packaging.

Verdict: PASS — issue #14 is fixed at the provider-neutral durable sink boundary and EPIC-833 is
complete.

## GitHub issue #13 OpenRouter completion-token compatibility — 2026-09-01

Spec source: GitHub issue #13 acceptance criteria.

- [x] The reported Luna `azure/eu` request was reproduced as failing because the OpenRouter adapter
  replaced supported `max_completion_tokens` with unsupported `max_tokens` before enabling
  `provider.require_parameters`.
- [x] Completion-token selection now occurs before provider I/O through the immutable exact-model
  profile and provider-route tag overrides. Luna `azure/eu` retains `max_completion_tokens`, Luna
  `openai` uses `max_tokens`, and DeepSeek routes use `max_tokens`; the adapter preserves the
  negotiated field while adding `require_parameters=true`.
- [x] Focused regressions cover structured output, `provider.only`, both wire aliases, preserved
  caller payloads and the non-OpenRouter path. The 44-test provider/task matrix, Ruff and strict
  mypy passed.
- [x] The operator explicitly accepted deferring paid endpoint confirmation until funded OpenRouter
  credit is available. The deterministic local regression reaches the transport with the
  route-compatible payload and retains the existing bounded, redacted failure diagnostic contract;
  no live-provider qualification claim is made.

Verdict: PASS / LIVE QUALIFICATION DEFERRED BY OPERATOR.

## EPIC-832 harness-owned context budgets and DeepSeek V4 parity — 2026-09-01

Spec sources: Agent Hotel card `c163`, ADR-070 and the EPIC-832 definition of done.

- [x] Workflow/session regressions prove an A-to-B-to-C graph transfers only explicitly rendered,
  schema-validated final results. Dependency order does not inject upstream transcripts, hidden
  reasoning or tool history into a downstream model context, while explicit output expressions
  retain their existing compatibility behavior.
- [x] The Pi protocol v2 receives the canonical transcript plus AMESH-calculated hard budgets, owns
  model-visible projection through `transformContext`, preserves pinned and newest complete groups,
  and returns a content-addressed v3 receipt. AMESH verifies the selected subset, bytes, estimated
  tokens, immutable call identity and exact provider result before accepting the turn; legacy v1/v2
  receipts remain readable.
- [x] `deepseek/deepseek-v4-flash-vision-exp` is an exact provider-neutral catalog choice with its
  image, context/output-limit and JSON-object structured-output profile. Local schema validation and
  bounded repair remain authoritative, and the OpenRouter edge translates the completion limit to
  the route-supported `max_tokens` parameter without introducing a DeepSeek core execution branch.
- [x] The affected provider-free matrix passed 168 tests with three expected live skips. Pi passed
  six worker tests and all 27 protocol/conformance cases; strict mypy, Ruff, SDK and generated-contract
  drift checks, backlog validation and strict documentation passed.
- [x] `.\scripts\verify-local.ps1 -Suite all` completed with exit code 0: 907 backend tests passed,
  179 environment-specific tests skipped and four documented cases deselected; 122 frontend unit
  tests, the production build, two product Playwright journeys, six Pi tests, 27 harness conformance
  cases, generated API/SDK contracts, backlog/provenance/REUSE, documentation, production-image and
  local packaging gates passed.
- [x] The operator explicitly accepted deferring the final paid OpenRouter Pi rerun until funded
  credit is available. Both Luna and DeepSeek plain structured smoke cases passed in the last run;
  the account then returned `no credits remaining` before the session cases could be requalified.
  The redacted result is retained at `.artifacts/live-openrouter/junit.xml`; this deferral does not
  support a live-provider qualification claim.

Verdict: PASS / LIVE QUALIFICATION DEFERRED BY OPERATOR — the implementation and complete
Docker-local gate pass. Do not promote the opt-in DeepSeek live qualification until it is rerun with
funded OpenRouter credentials.

## EPIC-830 prompt-cache hit-rate forensics and optimization — 2026-08-31

Spec sources: Agent Hotel card `c159` and the EPIC-830 definition of done.

- [x] The read-only audit covered 732 model invocations from `2026-08-24 23:57:08.155386+00`
  through `2026-08-31 00:52:09.893429+00`: 695 succeeded and 37 failed. Of the successful
  calls, 673 reported normalized cache evidence and 22 remained unavailable; failures were kept
  unclassifiable rather than counted as misses.
- [x] Among the 673 reported calls, 531 had positive reads, 142 reported zero reads, 632 had
  positive writes, 504 read and wrote, 27 read only, 128 wrote only and 14 reported zero for both.
  The reported-cohort request hit rate was 78.9004%; the coverage-inclusive successful-call rate
  was 76.4029%. Cached reads were 1,860,152 of 13,059,275 normalized input tokens, for 14.2439%
  token-weighted reuse.
- [x] Historical normalized billed cost evidence covered 677 calls and USD 3.581890107. No retained
  `promptCache.costEffectUsd` evidence existed, so cache-effect and savings values remain null. The
  report keeps task-result caching, provider response caching and invocation replay outside every
  prompt-cache denominator.
- [x] The measured session cohort showed positive reads on 503 of 507 reported turns two and later.
  The first reproducible AMESH-controlled prefix break was the v1 compaction marker: its canonical
  bytes changed as transcript digest/count changed. The v2 marker is byte-stable across the frozen
  growth fixture while full transcript/context digests, retained/omitted indexes, bounds and
  complete-turn provenance still change or validate in the durable receipt.
- [x] Seven report fixtures plus focused context, session, evidence, API and provider regressions
  passed. Ruff, strict mypy, generated-contract checks, SDK generation/drift checks and
  `git diff --check` passed. The strict documentation suite passed all eight desktop/tablet
  Playwright/axe journeys.
- [x] `.\scripts\verify-local.ps1 -Suite all` passed 868 backend tests with 178 expected skips and
  four documented deselections; 120 frontend unit tests; the production build; two product
  Playwright journeys; four Pi worker tests; the 25-case harness conformance kit; eight docs
  Playwright/axe journeys; generated contracts and Python/TypeScript/Java/Go SDKs; backlog,
  clean-room, REUSE, production-image and local packaging gates.

Verdict: PASS — EPIC-830 is complete. No paid provider call was made; the before/after result is a
provider-free prompt-identity qualification, not a claim of measured OpenRouter savings.

## EPIC-829 comprehensive user documentation site — 2026-08-31

Spec sources: Agent Hotel card `c158` and the EPIC-829 definition of done.

- [x] `./scripts/verify-local.ps1 -Suite docs` passed the strict MkDocs build and all eight
  Chromium documentation journeys across desktop and tablet viewports, including navigation,
  search and automated WCAG A/AA checks.
- [x] The documentation image built without cache, the Compose profile became healthy, and `/`,
  `/getting-started/`, `/workflows/`, `/agents/` and `/search/search_index.json` each returned HTTP
  200. The service ran as UID 10001 and published only on `127.0.0.1` at the documented port.
- [x] `./scripts/verify-local.ps1 -Suite all` passed Ruff; strict mypy over 289 source files; 858
  backend tests with 178 environment-specific skips and four documented deselections; 120 frontend
  tests; the production build; configured browser, Pi and harness suites; generated contracts and
  SDKs; backlog/provenance/REUSE gates; production-image probing; documentation; and local release
  packaging.
- [x] `uv lock --check` and `git diff --check` passed. The guides distinguish the provider-free
  isolated node test from a live agent call and require the operator's own OpenRouter key for the
  latter; EPIC-829 made no paid provider call.

Verdict: PASS — EPIC-829 is complete.

## EPIC-828 M5-M7 live clients, UI and release qualification — 2026-08-31

Spec sources: Agent Hotel cards `c155`-`c157`, ADR-068 and the EPIC-828 definition of done.

Exact workflow qualification evidence: the branch/loop/subflow, tenant, checksum, retry-identity
and no-binary-copy contract is
`tests/workflow/test_image_data_contracts.py::test_governed_image_ref_survives_branch_loop_subflow_and_retry`;
the runnable operator journey and validated flow inputs are
[`docs/how-to/route-governed-images-through-workflows.md`](docs/how-to/route-governed-images-through-workflows.md),
[`examples/governed-image-routing.yaml`](examples/governed-image-routing.yaml) and
[`examples/governed-image-child.yaml`](examples/governed-image-child.yaml).

- [x] Authenticated page and NDJSON endpoints replay a tenant/session-bound opaque cursor, deliver
  progress while work is active, emit heartbeats, close after terminal state and preserve attempt
  transitions without gaps or duplicates. CLI watch and all four generated SDKs use that contract.
- [x] Frame, segment, session, buffer and source-rate limits fail closed with one deterministic
  `TRUNCATED` terminal boundary. Slow initial observers receive a bounded timeout and attached live
  observers cannot block or mutate canonical execution.
- [x] Agent Sessions, Session Orchestrator and execution detail render the same accessible timeline.
  Browser evidence preserves separate `thinking 1`, tool, `thinking 2` and terminal activities, plus
  safe image metadata, reconnect/loading/empty/failure states and responsive/reduced-motion behavior.
- [x] `POST /api/v1/agent-sessions/{sessionId}/messages` creates one idempotent durable execution turn
  under the same logical session, resumes the exact successful checkpoint and immutable pins, admits
  governed images before provider I/O, and preserves a monotonic reconnect cursor across turns.
  Exact task/API/PostgreSQL evidence is linked from the EPIC-828 verification plan.
- [x] Workflow image staging is content-addressed and retry-stable. Ordinary task, plugin, isolated
  wire and Pi boundaries carry the shared reference; image interpretation requires an explicit
  modality declaration and fails before provider or plugin work when unsupported.
- [x] Provider-authored status text is replaced by fixed taxonomy status before persistence, image
  display evidence contains only safe immutable metadata, and the live stream emits its immediate
  heartbeat followed by no more than one heartbeat per five seconds while polling remains responsive.
- [x] The complete Docker-local gate passed: Ruff; strict mypy over 289 source files; 858 backend
  tests, 178 environment-specific skips and four documented deselections; 120 frontend tests and
  configured coverage; production build; two Chromium/axe journeys; four Pi tests; 25 harness
  conformance cases; generated contracts and Python/TypeScript/Java/Go SDKs; backlog, clean-room,
  REUSE, production-image and local packaging checks.
- [x] The opt-in OpenRouter `openai/gpt-5.6-luna` Pi qualification passed with image-plus-text input,
  schema-valid output, eight safe progress frames, 215 input tokens, 112 output tokens, 327 total
  tokens, USD 0.0001774 and provider-reported prompt-cache state. The safe JUnit record is
  `.artifacts/pi-luna-qualification.xml`; no hidden reasoning or raw image data is recorded.

Adversarial pass: exercised corrupt and mismatched images, oversized content, cross-tenant
references, unsupported plugin/provider/harness routes, duplicate source frames, noncontiguous
segments, cross-turn idempotency, reconnect/restart cursors, observer timeout, truncation, redaction,
provider-authored personal-data canaries and terminal replay. Each failed closed or preserved the
canonical authorized history.

Verdict: PASS — M5, M6, M7 and EPIC-828 are complete.

## EPIC-828 M4 Pi progress and durable chronological journal — 2026-08-31

Spec sources: Agent Hotel card `c154`, ADR-068 and the EPIC-828 acceptance criteria.

- [x] Provider and Pi progress use one validated tenant, logical-session, execution, task-run and
  attempt context and append immediately to the existing session journal under the session-row lock.
- [x] Source sequences are idempotent, event indexes share canonical lifecycle ordering, cursors
  carry attempt identity, and any intervening journal event permanently closes the prior segment.
- [x] Pi emits bounded model/tool/terminal status plus thinking boundaries without thought text,
  hashes tool identifiers, cannot publish provider summaries, and retains no provider/tool authority.
- [x] The executable Pi fixture proves separate `thinking 1 -> tool work -> thinking 2` segments;
  provider summary text is replaced by the fixed `model.processing` status before journal acceptance.
- [x] Eighty-six focused Python assertions passed with three environment-gated PostgreSQL skips;
  four Pi Node tests passed. Ruff and strict mypy passed for all affected source modules.

Verdict: PASS — M4 is complete. Public live/replay surfaces continue on card `c155`.

## EPIC-828 M3 provider streaming and multimodal OpenRouter adapter — 2026-08-31

Spec sources: Agent Hotel card `c153`, ADR-068 and the EPIC-828 acceptance criteria.

- [x] An additive provider-neutral stream returns only typed progress deltas and one assembled
  terminal response; existing unary providers and calls remain unchanged.
- [x] OpenAI-compatible SSE requests opt into streaming/usage, enforce timeout and response bounds,
  assemble content/tool/usage fields and preserve provider reasoning only in protected continuation.
- [x] Explicit provider-public summaries use separate segment identities across intervening tool or
  model work, preserving `thinking 1 -> work -> thinking 2` instead of regrouping summaries.
- [x] Governed image references resolve through a tenant- and actor-bound artifact authority only at
  provider I/O; bytes are revalidated against exact size/checksum/type/dimensions and mapped to a
  transient provider data URL that is never returned or persisted.
- [x] Ninety-two focused provider, registry, model-node, session/harness, artifact, workflow and API
  assertions passed with one existing skip. Ruff, strict mypy and targeted diff checks passed.

Verdict: PASS — M3 is complete. Pi propagation and durable journal acceptance continue on `c154`.

## EPIC-828 M2 platform-wide governed image ingestion and propagation — 2026-08-31

Spec sources: Agent Hotel card `c152`, ADR-068 and the EPIC-828 acceptance criteria.

- [x] PNG, JPEG, WebP and GIF bytes are signature-checked through pinned Pillow 12.3.0 before
  storage; declared type, byte, dimension, decoded-pixel and decompression limits fail closed.
- [x] Namespace image upload/resolve produces one immutable `amesh.image-ref/v1` value with exact
  tenant, version, checksum and safe display metadata; storage URIs and bytes are absent from public
  payloads.
- [x] Workflow `image` inputs accept inline base64 only at ingestion, replace it with the governed
  reference, and reuse the same artifact across validation, task binding, retries and checkpoints.
- [x] Ordinary `agent.chat`, `agent.structured`, `agent.toolCall` and `agent.session` paths preserve
  ordered text/image parts and reject an unsupported provider, route or harness before model I/O.
- [x] Ninety-one focused domain, artifact, workflow, model-node, session/harness, provider-registry
  and API assertions passed with one existing skip. Ruff, strict mypy and targeted diff checks passed.

Verdict: PASS — M2 is complete. Provider streaming and image resolution continue on card `c153`.

## EPIC-828 M1 chronology, privacy and platform image contracts — 2026-08-31

Spec sources: Agent Hotel card `c151`, ADR-068 and the EPIC-828 acceptance criteria.

- [x] `amesh.agent-progress/v1` accepts only bounded typed activity/status/correlation fields plus a
  factual status detail or explicitly classified public provider summary; arbitrary reasoning and
  scratchpad fields fail validation.
- [x] The pure sequence reducer enforces contiguous source identity, idempotent duplicate content,
  permanent segment closure and the exact `thinking 1 -> tool work -> thinking 2` boundary.
- [x] `amesh.agent-session-cursor/v1` round-trips as an opaque token bound to the logical service
  session and carries attempt-session, attempt and event-index position across retries.
- [x] `amesh.image-ref/v1` reuses the immutable tenant artifact contract, bounds portable media,
  bytes and decoded pixels, and cannot carry base64, remote URLs, signed URLs or credentials.
- [x] Ordered model content preserves text/image placement, count and aggregate limits. The image
  reference remains a base workflow/task/plugin value; provider capability negotiation rejects an
  image route before adapter I/O when `image_input` is absent.
- [x] Five generated JSON Schemas match their Pydantic sources. Twenty-three focused contract tests,
  30 provider/adapter regressions and 64 session/API regressions passed; affected Ruff and strict
  mypy checks, planning regeneration and backlog validation passed.

Verdict: PASS — M1 is complete. Runtime ingestion and propagation begin on card `c152`.

## Docker-local pre-push gate — 2026-08-28

Spec sources: Agent Hotel card `c139` and ADR-065.

- [x] The POSIX hook and installer pass `sh -n`; the PowerShell and POSIX installers both enable
  clone-local `core.hooksPath=.githooks` idempotently and refuse to replace a different configured
  hook directory.
- [x] `DOCKER_HOST=tcp://127.0.0.1:1 git hook run pre-push ...` returns exit 1 after Docker refuses
  the connection, proving verification failure propagates through the hook and rejects the Git
  operation.
- [x] `git hook run pre-push -- origin https://github.com/samchung95/amesh.git` executes the complete
  Docker-local aggregate and returns 0: Ruff, strict mypy over 273 source files, 676 backend tests,
  90 frontend assertions plus production build, two byte-identical 23-case Pi reports,
  planning/backlog/clean-room/REUSE/contracts, five review regressions, four Compose configurations,
  the production-image Pi probe and repository/four-SDK packaging all pass.
- [x] The repository contains no executable GitHub Actions workflow, and the push gate performs no
  publication, signing, attestation or release upload.

Boundary: native Git permits `git push --no-verify`, and clone owners can change local hook
configuration. This is the complete supported local guard, not an unbypassable remote policy.

Verdict: PASS. The installed hook blocks ordinary pushes when the canonical Docker gate fails and
allows them only after the complete aggregate succeeds.

## PR #1 Docker-local merge preparation — 2026-08-27/28

Spec sources: Agent Hotel cards `c135`–`c138`, ADR-062 and ADR-064.

- [x] The two supported-path review blockers pass real-PostgreSQL regressions: MCP retries reuse one
  stable invocation identity while validating immutable ownership/content, and a cross-tenant denial
  creates no target-tenant API quota row.
- [x] `.\scripts\verify-local.ps1 -Suite all` passed: Ruff lint, strict mypy over 273 source files,
  676 backend tests, 166 environment-gated skips and four named deselections; 21 frontend test files
  with 90 assertions plus the production build; the Pi Node test and 23-case conformance report twice
  with byte comparison; planning/backlog/clean-room/REUSE/generated-contract/compile checks; and the
  five focused review regressions.
- [x] Default, compact, verifier and hardened Compose configurations validate. The production image
  builds and its Pi harness probe reports `passed: true` for `pi-agent-core` 0.84.3.
- [x] The verifier build context excludes `.env` and derived environment files while retaining the
  public `.env.example`; the rebuilt image contains no local environment-secret file.
- [x] Docker-local packaging created `amesh.zip`, `amesh.tar.gz` and four SDK archives. All recorded
  SHA-256 checksums match, and the repository archive
  contains no `.agent-hotel`, `.claude`, virtual environment, `node_modules`, `build` or `dist` path.
- [x] SDK generation `--check` reports 2,761 current files. Generated SDK Markdown and all changed
  non-SDK Markdown each report zero broken relative links; planning validation reports 122 epics, 837
  functional requirements, 63 non-functional requirements and 1,000 traceability links.
- [x] `docker compose up -d --build` rebuilt the exact working source. `/ready` reports `ready`, all six
  roles and every dependency `READY`, and migration 67/67 with
  `0067_protected_trigger_payloads.sql`; `/` and `/openapi.json` return HTTP 200.

Not claimed: repository-wide formatting (`c90`), frontend lint (`c88`), specialist toolchain/database
matrices (`c110`) and deferred review environments (`c130`–`c132`) are not represented as green by
the aggregate. Publication, signing and hosted attestation were not performed.

Verdict: PASS. The local merge candidate satisfies the Docker-local release boundary.

## MVP current-head review findings 1–8 — 2026-08-27

Spec sources: Agent Hotel card `c134`, PR #1 current-head review and ADR-063.

- [x] Fresh executions without running work are immediately recoverable; a fresh `RUNNING` task is
  grace-protected even when its execution row is old, and an abandoned running task becomes eligible.
- [x] Split-role execution composes durable subflow, human approval and isolated-plugin handlers and
  closes the isolated runtime during service shutdown.
- [x] Sensitive webhook occurrences expose a redacted public payload while PostgreSQL stores no
  plaintext copy; delayed processing and manual replay both launch with the authenticated original.
- [x] In-place flow A→B navigation renders B without stale A source, and logout or same-tenant
  principal change removes protected React Query data.
- [x] Docker stops on `outputLimitBytes`, fails the task, bounds outputs/logs, preserves credential
  redaction and removes the owned container in both fake- and real-engine tests.
- [x] The combined affected-path suite passed 49 tests with two real-Docker cases skipped there; the
  complete Docker runner file passed all 10 cases with real-engine testing enabled. Scoped Ruff,
  formatting and strict mypy passed. Five frontend assertions, targeted ESLint, TypeScript/build and
  two Chromium journeys passed.
- [x] The complete Docker-local gate, both Compose configuration checks and the production image Pi
  harness probe passed. Backlog generation/validation and clean-room/REUSE checks were included.
- [x] The rebuilt deployment reports every role and dependency ready at migration 67/67. A live
  sensitive-webhook canary completed `SUCCESS`, remained redacted in execution inputs, trigger body
  and occurrence projections, and persisted only redacted public JSON plus non-plaintext ciphertext.
- [x] Chromium completed the deployed token-login, guided workflow creation, validation, simulation,
  isolated test, launch and simple-trace journey.

Not covered: Kubernetes runner output limits, Helm webhook-secret wiring and Kubernetes-operator path
isolation are explicitly deferred as findings 9–11 on card `c130`.

Verdict: PASS. Findings 1–8 satisfy review gate `c134`.

## EPIC-822: Capability catalog and connection wizard — 2026-08-26

Spec sources: Agent Hotel card `c124`, canonical EPIC-822 and ADR-059.

- [x] One server-side projection independently authorizes and safely aggregates immutable agent
  resources, MCP connection/tool pins and plugin packages. Exact revisions, digests, schemas,
  impacts, permissions, compatibility, attachment requirements and source-access states are exposed
  without endpoints, credential values, prompt bodies, plugin bundles or registry internals.
- [x] The Agents UI searches, filters and inspects the canonical projection; exact prompt, skill,
  model-policy, evaluation and MCP-tool references populate the guided agent builder, while an exact
  agent reference opens an unsaved guided workflow draft using that revision.
- [x] The connection wizard accepts an HTTP(S) endpoint, an authorized secret-binding reference,
  timeout and reviewed tool allowlist. Its exact-revision test performs MCP discovery only, compares
  pinned schema digests and records a fixed-shape redacted immutable audit receipt with
  `DISCOVERY_ONLY` effect boundary.
- [x] Eighteen focused Python/API/PostgreSQL/generated-contract tests, Ruff check/format and strict
  mypy passed. Forty frontend assertions, targeted ESLint and the production build passed.
- [x] Chromium completed the catalog, MCP-tool attach, connection discovery/save/test and exact-agent
  workflow-attach journey at desktop and 390×844 mobile sizes. A real local MCP HTTP server completed
  discovery/save/test while its tool-call counter remained zero.
- [x] The API/frontend image rebuilt successfully. `/ready` reported all dependencies and roles ready
  at migration 66; authenticated deployed catalog/filter requests returned the versioned projection,
  and a missing exact connection test returned a generic redacted 404.

Commands:

```text
AMESH_TEST_DATABASE_URL=<local PostgreSQL> uv run --frozen --extra runtime --extra dev pytest -q tests/adapters/postgres/test_audit_repository.py tests/api/test_agent_connections_api.py tests/api/test_capability_catalog_api.py tests/test_capability_catalog.py tests/test_generated_contracts.py
uv run --frozen --extra runtime --extra dev ruff check <EPIC-822 Python files>
uv run --frozen --extra runtime --extra dev ruff format --check <EPIC-822 Python files>
uv run --frozen --extra runtime --extra dev mypy --strict <EPIC-822 production modules>
npm run test:unit -- src/components/CapabilityCatalog.test.tsx src/components/ConnectionWizard.test.tsx src/components/capabilityCatalogModel.test.ts src/components/guidedWorkflowModel.test.ts src/api/client.test.ts
npm run build
npx playwright test e2e/shell.spec.ts --project=chromium --grep "browses the canonical capability catalog"
docker compose up -d --build api
uv run --frozen python scripts/regenerate_planning_artifacts.py
uv run --frozen python scripts/validate_backlog.py
```

Verdict: PASS. EPIC-822 is complete.

## EPIC-821: Live agent run inspector and frozen replay — 2026-08-26

Spec sources: Agent Hotel card `c123` and canonical EPIC-821.

- [x] Authorized list and paginated detail endpoints expose canonical session facts and stable event
  indexes while excluding checkpoint messages, prompts, continuations, sensitive keys, oversized raw
  payloads and hidden reasoning.
- [x] Execution detail renders state/phase, current turn, model, tools, approvals, repairs, context,
  token/cost/cache, schema and final/failure evidence in one responsive chronological inspector. It
  reuses the existing authorized execution controls and evidence drill-down.
- [x] Frozen replay rejects input overrides and requires a source-input digest plus exact flow,
  plugin-set, determinism-envelope and admission-policy pins. The existing backfill service records
  source linkage, converges duplicate idempotency keys and permits a distinct intentional key.
- [x] Ten focused Python/API/PostgreSQL/generated-contract tests, Ruff check/format, strict mypy, 32
  frontend assertions, targeted ESLint and the production build passed.
- [x] Chromium and tablet Playwright journeys passed; the Chromium journey also verified 390×844
  mobile layout, no horizontal overflow, frozen preview/create payload identity and no critical or
  serious axe finding. Desktop, tablet and mobile screenshots were exported under
  `docs/product/ui-audit/screenshots/agent-run/`.
- [x] Deployed `openai/gpt-5.6-luna` execution
  `01a03de7-fdcd-791f-992c-721e38eb0313` persisted three model turns, three context projections,
  two scheduled repairs and an intentional terminal validation failure across 11 events. The live
  detail endpoint returned the complete canonical trace with neither checkpoint nor reasoning data.

Commands:

```text
uv run --frozen --extra runtime --extra dev pytest tests/test_backfill_contract.py tests/api/test_backfill_api.py tests/api/test_agent_sessions_api.py tests/adapters/postgres/test_backfills.py tests/adapters/postgres/test_agent_session_repository.py tests/test_generated_contracts.py -q
uv run --frozen --extra runtime --extra dev ruff check <EPIC-821 Python files>
uv run --frozen --extra runtime --extra dev ruff format --check <EPIC-821 Python files>
uv run --frozen --extra runtime --extra dev mypy <EPIC-821 production modules>
npm run test:unit -- src/components/agentRunInspectorModel.test.ts src/components/executionDebugModel.test.ts src/api/client.test.ts
npm run build
npx playwright test e2e/shell.spec.ts --grep "inspects a canonical agent run and submits one frozen replay" --project=chromium --project=tablet
uv run --frozen python scripts/regenerate_planning_artifacts.py
uv run --frozen python scripts/validate_backlog.py
```

Verdict: PASS. EPIC-821 is complete.

## EPIC-820: Guided agent node builder — 2026-08-26

Spec sources: Agent Hotel card `c122`, canonical EPIC-820, ADR-051 and ADR-059.

- [x] The AI/model intent emits `agent.session`, exact AGENT revision, request input mapping,
  synchronized secret scopes, fail/repair policy, data handling and deterministic context limits.
- [x] Authorized AGENT revisions whose required schema fits the guided `request` mapping are exposed as
  labeled selectors; incompatible revisions remain available in YAML. Empty and preview-failure states
  are actionable.
- [x] Envelope preview enumerates exact agent, prompt, skill, model-policy and evaluation revisions,
  routes, MCP connection/tool pins, output schema, memory, permissions and hard budgets while external
  calls are suppressed.
- [x] The agent-node test reuses the persisted ordinary flow-test definition/run endpoints with an
  inline fixture. It creates no production execution, artifact or secret lookup and never calls Pi,
  the model provider or a tool.
- [x] Eight focused unit tests, targeted ESLint and the production build passed. Chromium and tablet
  complete create/preview/save/test/reopen journeys passed; Chromium additionally verified the
  reopened builder at 390×844. Axe reported no critical or serious finding, and desktop, tablet and
  mobile screenshots were exported.
- [x] Deployed live flow `epic820.guided.agent_builder_smoke_3030a781@1` validated and passed admission,
  previewed exact `researcher-3030a781@1`, passed the isolated test with zero effects and reopened from
  PostgreSQL with the same pin and `maxMessages=96`. API readiness remained full at migration 66.

Commands:

```text
npm run test:unit -- src/components/guidedWorkflowModel.test.ts
npx eslint src/components/guidedWorkflowModel.ts src/components/GuidedWorkflowBuilder.tsx src/pages/FlowEditorPage.tsx src/components/guidedWorkflowModel.test.ts e2e/shell.spec.ts
npm run build
npx playwright test e2e/shell.spec.ts --grep "builds, previews, tests, saves and reopens a guided agent session node"
docker compose up -d --build api
```

Verdict: PASS. EPIC-820 is complete.

## EPIC-819: Bounded context and provider-cache evidence — 2026-08-26

Spec sources: Agent Hotel card `c121`, canonical EPIC-819 and ADR-058.

- [x] `amesh.recent-complete-turns/v1` deterministically derives bounded model context from an
  unchanged checkpoint transcript, retains pinned prefix messages and newest complete assistant/tool
  groups, and fails closed when that minimum safe set cannot fit.
- [x] Every model turn persists a stable receipt with transcript/context hashes, source indexes,
  message/byte/estimated-token measurements and headroom. Idempotency keys prevent duplicate receipt
  events after restart, and PostgreSQL reload preserves both transcript and latest receipt.
- [x] OpenRouter cached read tokens, cache-write tokens and signed cache-cost effect normalize into an
  explicit `reported`/`unavailable` prompt-cache record with hit ratio. Evidence bundles keep it
  distinct from task-cache and invocation-replay facts.
- [x] The focused domain, provider, Pi-adapter, session, API, evidence and real-PostgreSQL suite passed
  43 cases with one environment-gated skip. Strict mypy passed over 266 source files; focused Ruff,
  the exact Pi Node test, generated contracts, backlog validation and `git diff --check` passed.
- [x] A live `openai/gpt-5.6-luna` session ran through Pi, used an AMESH-mediated tool exactly once,
  returned schema-valid structured output and persisted two context receipts plus normalized provider
  usage evidence.
- [x] API and executor images rebuilt successfully and `/ready` reported every dependency and role
  ready at migration 66.

Commands:

```text
uv run --frozen pytest -q tests/domain/test_agent_context.py tests/model_providers/test_model_provider_registry.py tests/adapters/test_agent_session_harness.py tests/tasks/test_agent_sessions.py tests/test_evidence_bundle.py tests/api/test_agent_sessions_api.py tests/adapters/postgres/test_agent_session_repository.py
uv run --frozen pytest -q tests/tasks/test_agent_sessions.py -k live_openrouter_luna_session_runs_through_pi
uv run --frozen mypy src
npm test --prefix harnesses/pi
docker compose up -d --build api executor
```

Verdict: PASS. EPIC-819 is complete.

## EPIC-819: Pi production cutover and feature parity — 2026-08-26

Spec sources: Agent Hotel card `c121`, canonical EPIC-819, ADR-058 and the product-owner cutover directive.

- [x] `agent_session_handler` now requires an injected harness. API and recovery-executor composition
  explicitly construct Pi 0.84.3, and the built-in adapter/fallback no longer exists.
- [x] Every existing primary agent-session behavior test runs through the real Pi subprocess: ordered
  provider fallback, accepted-action restart reuse, continuation handles, invalid-output repair, hard
  turn/tool limits, approval denial, AMESH-only MCP dispatch, memory, evaluation and human release.
- [x] The Pi child receives an allowlisted process environment without `OPENROUTER_API_KEY` or other
  provider credentials. The parent still locks the exact authorized model call and owns all effects.
- [x] Sixteen non-live focused Python tests pass, including an explicit assertion that the session
  factory has no implicit harness fallback. A model result larger than the old 1 MiB control-frame
  limit is returned unchanged because the worker no longer echoes full model content over JSONL.
- [x] A separately enabled live structured session passed through Pi using exact model
  `openai/gpt-5.6-luna`, persisted Pi harness evidence and returned a schema-valid final result.
- [x] The Node bridge test, focused Ruff, strict mypy over 265 source files and Compose configuration
  pass. The production image builds and its non-root runtime reports Node `v22.23.2`, Pi `0.84.3`, a
  loadable worker module and the configured worker command.
- [x] Rebuilt API and executor services returned full readiness at migration 66. Deployed execution
  `01a03bec-6f6e-7a7e-ac89-2c8d7d9a0278` completed a two-member Luna mesh successfully with 1,320
  total tokens, and its canonical evidence contains two `pi-agent-core` model-response records.

Commands:

```text
uv run --extra runtime --extra dev pytest -q tests/adapters/test_agent_session_harness.py tests/tasks/test_agent_sessions.py
npm test --prefix harnesses/pi
uv run --extra runtime --extra dev mypy src
docker compose config --quiet
docker build --tag amesh:pi-cutover .
```

Verdict: PASS for the production harness cutover and existing `agent.session` feature parity.
EPIC-819 remains open only for bounded-context/compaction receipts and normalized provider-cache
evidence.

## EPIC-819: Harness evaluation and first Pi adapter slice — 2026-08-26

Spec sources: Agent Hotel card `c121`, canonical EPIC-819 and ADR-058.

- [x] Current primary evidence compared DSH, Pi and Goose for authority preservation, embedding
  size, platform availability, OpenRouter/provider fit, context/cache hooks, maintenance and license.
  Pi 0.84.3 scored highest for this repository; ADR-058 records the weighted decision and rejects
  Pi's incomplete `AgentHarness` facade in favor of the established direct `Agent` API.
- [x] The original agent-session model turn now crosses a typed `AgentSessionHarness` port. The
  injected AMESH model gateway accepts only the exact authorized provider, model, route, budget,
  continuation and stable invocation key; a tampering test proves rejection before model I/O.
- [x] The built-in compatibility adapter preserves all existing session tests and records public
  harness adapter/version evidence on accepted model responses.
- [x] `@earendil-works/pi-agent-core` and `@earendil-works/pi-ai` are exactly locked to 0.84.3 in the
  isolated Node 22 worker. Its custom stream and tool handler issue JSONL requests to the parent and
  contain no provider credential or native tool effect.
- [x] Thirteen focused Python tests passed. They include the real Pi subprocess adapter and a
  two-model-turn session in which Pi proposes one tool, AMESH records policy authorization, the MCP
  handler performs one effect, and Pi-routed execution returns schema-valid final output.
- [x] The Pi Node test passed one parent-mediated sequence with two model requests, one tool request
  and one final result. Focused Ruff and strict mypy passed.

Commands:

```text
uv run --extra runtime --extra dev ruff check src/amesh/adapters/agent_session_harness.py src/amesh/ports/agent_session_harness.py src/amesh/tasks/session.py tests/adapters/test_agent_session_harness.py tests/tasks/test_agent_sessions.py
uv run --extra runtime --extra dev mypy src/amesh/ports/agent_session_harness.py src/amesh/adapters/agent_session_harness.py src/amesh/tasks/session.py
uv run --extra runtime --extra dev pytest tests/adapters/test_agent_session_harness.py tests/tasks/test_agent_sessions.py -q
cd harnesses/pi && npm test
```

Verdict: PASS for the first replacement slice. EPIC-819 remains open for bounded context and
compaction receipts, provider prompt-cache evidence, restart qualification and the live OpenRouter
Luna tool-session gate.

## EPIC-811–EPIC-818: Neutral orchestration qualification sprint — 2026-08-26

Spec sources: Agent Hotel cards `c112` through `c119` and the canonical
`backlog/epics/epic-811-*.md` through `epic-818-*.md` definitions of done.

- [x] **EPIC-811 — external orchestration:** the v1 neutral profile, OpenAPI and generated SDKs
  cover nine validate/apply/read/launch/inspect/control operations with stable error categories,
  tenant authorization, correlation and idempotency. The live uv harness returned execution
  `01a039c5-4225-735e-b4f7-e7af5d4a5dbc` for the same key before and after an API restart; three
  live PostgreSQL realtime reconnect tests passed.
- [x] **EPIC-812 — evidence:** the same execution exported 13 canonical trace records with bundle
  digest `sha256:eced2443a98deae4cc15c372a09e72553cafa907b2e924f570919cbb0f347576`.
  API and uv CLI verification agreed on the digest and returned `verified: true`; redaction,
  pagination, externalization and corruption/conflict behavior passed focused tests.
- [x] **EPIC-813 — model providers:** capability negotiation, exact revisions, structured output,
  tools, encrypted opaque continuation, timeout/retry/cancel, ambiguity, normalized usage and billed
  cost passed against two independent provider fixtures. The environment-gated live OpenRouter test
  passed against exact model `openai/gpt-5.6-luna` with content, usage and billed-cost evidence.
- [x] **EPIC-814 — tool providers:** the shared conformance suite passed the actual MCP and isolated
  plugin adapters locally and against PostgreSQL, including pinned discovery/schema identity,
  policy denial, redaction, timeout/cancellation, accepted-result reuse and restart ambiguity.
- [x] **EPIC-815 — hardened local profile:** eight tests and a fresh isolated Compose run on loopback
  port 18016 passed migration/preflight, real login, workflow execution and evidence retrieval. The
  profile exposed no database port, mounted no Docker socket, carried no broker/OpenRouter secret,
  and used a password-free database URL with a permission-restricted `PGPASSFILE` secret.
- [x] **EPIC-816 — restart qualification:** `uv run python scripts/qualify_restart_idempotency.py`
  produced `build/epic-816-qualification.json` with all 40 fault-boundary scenarios passing, zero
  lost accepted records, zero duplicate logical decisions, stable accepted-result reuse, stale-fence
  rejection and non-repeated ambiguous outcomes. A 1 MiB payload externalized with verified
  integrity, and deliberate corruption was detected. The generated report is local evidence; the
  exact reproducible command and limits are maintained in
  [`run-restart-idempotency-qualification.md`](docs/how-to/run-restart-idempotency-qualification.md).
- [x] **EPIC-817 — differential shadow:** live spec
  `561a6327-631e-4c1e-8341-8e61cebad3bc` created independent left/right runs
  `01a039cb-1c7a-7d12-9f46-5902b9e468f1` and `01a039cb-1c8f-7681-abf1-cd2240845e23`, denied
  uncontrolled effects, reported zero deterministic failures, and returned the identical durable
  report after an API restart.
- [x] **EPIC-818 — release gates:** 23 frontend client assertions, the production build, nine
  backend/UI-session checks and three Chromium Playwright scenarios passed with no serious or
  critical axe finding. Live target `epic818-qual-f6003249d4d94572b640672f78112e2e`
  rejected missing evidence with HTTP 409, promoted revisions 1 and 2, rolled back to the exact
  revision-1 digest at version 3, then preserved `PROMOTE → PROMOTE → ROLLBACK` after API restart.

Cross-sprint gates: 557 backend tests passed, 158 environment-gated tests skipped and two separately
tracked baseline tests were deselected; Ruff check passed, strict mypy passed over 263 source files,
and all new sprint Python files pass Ruff format. Contract generation is deterministic across 2,671
files; Python, TypeScript, Java and Go SDK checks pass. The two deselections are the already deferred
5,000-line DSL performance budget (`c89`) and the full-suite-only async plugin-registry isolation
issue (`c120`) that passes alone; neither affects an EPIC-811–818 path.

Qualification boundary: these epics prove the checked-in local profiles and provider-neutral core
contracts. Client domain tools, client parity thresholds, production cutover, multi-region HA and
external-cloud certification remain explicitly outside this sprint.

Verdict: PASS — EPIC-811 through EPIC-818 satisfy their published local definitions of done.

## EPIC-810: Reliable scheduling and truthful role-aware health — 2026-08-25

Spec source: Agent Hotel card `c111` and
`backlog/epics/epic-810-reliable-scheduling-and-truthful-role-aware-health.md`.

- [x] A PostgreSQL regression forces temporal execution creation to fail, observes one durable
  `RETRY_WAIT` occurrence, advances the fenced schedule cursor on the duplicate evaluation and lets
  the trigger worker create exactly one execution with the original occurrence key.
- [x] Resolvable legacy plugin payloads conditionally migrate to exact v1 pins with one
  `plugin.resolution.migrate` audit event. Unresolvable payloads disable the owning flow with one
  `plugin.resolution.quarantine` event, and disabled flows do not enter scheduler evaluation.
- [x] Migration 0060 persists `DEGRADED`, `lastSuccessAt`, `lastFailureAt`, a bounded redacted failure
  summary and `consecutiveFailures`. The API reports every configured role as READY, DEGRADED,
  STARTING, DRAINING, UNAVAILABLE or DISABLED and returns 503 unless every enabled role has a live
  READY instance.
- [x] Sixty-one focused scheduler, trigger-runtime, plugin-policy, service-registry, configuration,
  API, worker, Helm and migration tests passed together; Ruff and strict mypy passed for affected
  production modules.
- [x] Rebuilt Compose applied migration 60/60. A quota-induced scheduler cycle failure produced HTTP
  503 and persisted DEGRADED evidence; after reversibly disabling 164 leaked `tests.scheduler.*`
  flows, all six enabled roles returned READY in 11 seconds and the failure timestamp remained as
  recovery evidence.
- [x] Bounded cron flow `smoke.epic810/epic810_restart_151710` fired once at
  `2026-08-25T15:18:00Z`. Restarts before and after the instant retained one occurrence and one
  execution, `01a03980-1533-7e64-97b7-7d30642bc231`; final `/ready` returned HTTP 200 with all six
  roles READY and scheduler logs contained no recurring post-recovery error.

Security review: health failures are redacted and bounded before persistence, service mutations are
generation-fenced, plugin compatibility mutations are tenant-scoped and conditional, and quarantine
and migration actions are audited. No domain calendar, client adapter or broker capability was added.

Verdict: PASS — EPIC-810 and card `c111` are verified.

## c103: Human-first control room and workflow experience overhaul — 2026-08-25

Spec source: Agent Hotel umbrella card `c103`, its completed workstreams `c97` through `c102`, and
canonical UI epic EPIC-404.

- [x] Mission Control is the default operational surface and shows running, queued, retrying,
  paused, waiting-approval, failed-recently and completed-recently states. Active rows expose the
  workflow, current step, progress, elapsed time, trigger and runner, with direct simple-trace links.
- [x] The default trace tells an ordered run story and keeps pins, deterministic bounds, epoch/version
  fences, topology, Gantt, logs, data and audit history available through progressive disclosure.
- [x] Guided creation starts from six intent-based starters, uses catalog-backed finite choices,
  preserves YAML/visual authoring, and gates Run now through save, policy validation, deterministic
  simulation and an isolated test. Launch context exposes revision, environment, policy and runner;
  denied policy decisions provide a direct remediation action.
- [x] All 67 frontend unit assertions, the production build, changed-file ESLint and all 26 applicable
  Playwright checks pass with 30 intentional cross-project skips. The three required viewport
  journeys satisfy the interaction/time budgets and report zero critical or serious axe findings.
- [x] Rebuilt Compose is ready at migration 59/59. Two authenticated live Chromium journeys pass:
  Mission Control opens the running execution and its simple trace, while guided creation saves,
  validates, simulates, isolated-tests, launches and traces a real workflow. The live manifest records
  one running, 86 failed-recently and 113 completed-recently executions with no console errors or
  failed requests.

Verdict: PASS — card `c103` and the human-first EPIC-404 follow-on are verified.

## c101: Production workflow determinism assurance — 2026-08-25

Spec source: Agent Hotel card `c101`, ADR-056 and
`backlog/epics/epic-800-deterministic-simulation-and-dry-run-engine.md`.

- [x] Simulation and runtime expose the same versioned determinism envelope: exact revision,
  semantic hash, plugin-set hash, admission-policy pins, canonical nodes and branches, dynamic
  defaults/bounds, nesting depth, worst-case task runs and external-output disclosure.
- [x] Runtime metadata is immutable evidence and is excluded from user expression contexts.
  Branch IDs, iteration keys, subflow relationships, committed decisions and epoch/version fences
  remain visible through the graph and execution trace.
- [x] Arbitrary plugin child-graph injection and task nesting beyond 16 levels are rejected; loops
  and subflows retain typed iteration, duration, task-run, concurrency, depth and inline-payload
  limits.
- [x] Twenty-two focused simulation/DSL tests, the affected PostgreSQL launch/admission tests,
  execution/restart/replay suites and focused frontend model/Playwright acceptance pass. Ruff,
  strict mypy over 236 source files, the production frontend build, generated-contract checks and
  all four generated SDK checks pass.
- [x] Rebuilt Compose is ready at migration 59/59. Bounded conditional/foreach execution
  `01a0377e-2151-7781-ada8-7c6feefe398b` completed `SUCCESS`; preview and runtime both produced
  envelope digest `1fd1df905e7280fd9ddad40d7807a04abf8574fe39d43e6d7ae1794036320291`
  with identical semantic/plugin hashes and admission policy revision.

Qualification boundary: orchestration graph, order, decisions, bounds and pinned controls are
deterministic. External LLM, HTTP and user-code outputs remain explicitly nondeterministic and
require pinned metadata or recorded fixtures for replay.

Verdict: PASS — card `c101` and the production-determinism assurance for EPIC-800 are verified.

## EPIC-806: Multi-agent topology, typed hand-offs and routing — 2026-08-25

Spec source: Agent Hotel card `c109`, ADR-055 and
`backlog/epics/epic-806-first-class-agent-mesh-runtime-and-governance.md`.

Verified with `uv`, PostgreSQL 17, Docker Compose, OpenRouter `openai/gpt-5.6-luna`, React and the
four generated SDKs:

- [x] `agent.mesh` compiles supervisor, router, peer-to-peer, hierarchical and swarm declarations
  into the existing durable task plan, rejects cycles and exact-member/session mismatches, and
  bounds parent concurrency, sessions, tokens, cost, duration and tool calls.
- [x] `agent.route` gates declared capability, policy and availability before deterministically
  ranking evaluation score, projected cost, latency and stable member ID. The authorized preview
  and persisted result expose every admitted and rejected assessment plus a decision digest.
- [x] `agent.handoff` requires exact source and destination agent revisions, direct graph
  dependencies, destination capabilities, an allow policy and a typed payload. It redacts secrets
  before recording source, destination, rationale, context, schema, policy and hand-off digests.
- [x] Session and parent reducers enforce the tighter member/agent limits and fail closed on
  persisted aggregate overrun. A pinned ordered provider-substitution test survives primary
  outage without changing the session state contract and preserves nondeterminism disclosure.
- [x] Twenty-eight focused Python tests and five focused frontend assertions passed. Ruff, strict
  mypy over 235 source files, the production frontend build, checked generated contracts and
  `git diff --check` passed.
- [x] OpenAPI, the resource catalog and all four SDKs regenerated. Rebuilt Compose is ready at
  migration 59/59.
- [x] Deployed execution `01a0374f-5746-7c4c-b983-19fb47fa244e` completed `SUCCESS` with two Luna
  sessions and one typed hand-off. It recorded 1,172 session tokens, `$0.0007354` cost, zero tool
  calls, both deterministic and pinned-judge gates, exact member budgets, a hand-off digest and the
  parent mesh provenance graph.

Adversarial pass: exercised topology cycles, unregistered members, reservation overcommit,
unwired hand-offs, capability and policy denial, schema failure, secret redaction, parent budget
overrun and primary-provider outage. Deployed revision 1 failed closed because required business
assertions were absent; revision 2 supplied them and passed without weakening the gate.

Qualification boundary: graph topology, routing, hand-offs, budgets and evidence are deterministic;
model and judge text remain explicitly nondeterministic.

Verdict: PASS — EPIC-806, `URS-F-0808`, `URS-F-0810`, `URS-F-0811` and
`URS-NFR-AGENT-001` through `URS-NFR-AGENT-004` are verified.

## EPIC-809: Agent memory, evaluation and release gates — 2026-08-25

Spec source: Agent Hotel card `c108`, ADR-054 and
`backlog/epics/epic-809-agent-memory-evaluation-and-release-gates.md`.

Verified with `uv`, PostgreSQL 17, Docker Compose, OpenRouter `openai/gpt-5.6-luna`, React and the
four generated SDKs:

- [x] Migration 0059 persists tenant-RLS memory at exact execution, private agent-revision or named
  shared scope. Tests cover tenant, namespace, agent and revision isolation; size and retention;
  redaction; duplicate-operation reuse; metadata-only reads; scoped deletion and audit evidence.
- [x] Immutable evaluation revisions combine deterministic JSON-schema assertions and weighted
  rubrics with an optional exact model-policy judge. Judge provenance includes route, model, usage,
  cost, score, uncertainty, rationale and nondeterminism; a deterministic failure cannot be
  overridden by a judge.
- [x] Human release is an ordinary direct `core.approval` dependency. Tests prove a passing judge
  cannot release high-impact output alone, and a provider outage uses only pinned ordered fallback.
- [x] Side-effect-free agent and fixture previews suppress external calls and disclose unknown model
  behavior. The Agents UI guides evaluation, judge, memory and release selection; the execution
  trace renders recall, evaluation, approval, write and acceptance evidence.
- [x] Fourteen focused Python tests, three real-PostgreSQL integration tests and seven focused
  frontend assertions passed. Ruff, strict mypy over 233 source files, the production frontend
  build and `git diff --check` passed.
- [x] OpenAPI, the resource catalog and all four SDKs regenerated. Rebuilt Compose is ready at
  migration 59/59; its executor recovery grace now exceeds the bounded 120-second agent session.
- [x] Cold execution `01a03728-0034-7730-82f9-fce320a344fc` completed `SUCCESS` with no recalled
  memory, evaluation revision 1, judge score 0.90, 683 tokens, `$0.0004646` cost and memory write
  version 3. Recall execution `01a03728-fc13-70cc-b592-df2fabca6c88` completed `SUCCESS` with the
  exact prior entry, judge score 0.90, 828 tokens, `$0.0005016` cost and replacement version 4.
  Both journaled `session.started -> model.response -> evaluation.completed -> memory.written ->
  output.accepted`.

Adversarial pass: exercised cross-tenant/private/shared confusion, oversize and expired entries,
duplicate writes, deletion, recalled prompt-injection text, deterministic evaluation failure,
passing-judge release denial, judge-provider outage and judge uncertainty. A live recall candidate
scored 0.68 against the 0.70 judge gate and was rejected, proving that nondeterministic evaluation
remains observable and cannot silently promote output.

Qualification boundary: exact memory and deterministic evaluation/release controls are qualified;
model and judge text remain explicitly nondeterministic. Mesh-wide routing, hand-offs and provider
substitution remain with EPIC-806, so shared agent NFRs remain In Progress.

Verdict: PASS — EPIC-809 and `URS-F-0812`, `URS-F-0816` and `URS-F-0819` are verified.

## UX-03: Guided workflow creation — 2026-08-25

Spec source: Agent Hotel card `c100`, ADR-051 and
`docs/product/guided-workflow-creation.md`.

Verified with React/TypeScript, Vitest, Playwright and the live Docker Compose deployment:

- [x] Six intent starters create ordinary canonical YAML for schedules, webhooks/APIs, data
  pipelines, approvals, bounded Luna tasks and blank advanced workflows.
- [x] Guided identity, input, trigger, step, dependency, output, runner, model and secret controls
  mutate the same round-trip source used by visual and YAML modes; comments and unsupported root
  fields are preserved and disclosed.
- [x] Readiness composes server validation, plain-language admission policy, side-effect-free
  simulation, dynamic unknown/cost/runner bounds and a revision-pinned isolated smoke test before
  Run now opens the persisted simple trace.
- [x] Permission denial, draft recovery and unsaved-navigation behavior remain visible; all ordinary
  form controls are keyboard accessible.
- [x] Six focused unit checks passed, the production build passed, and all 62 complete-suite unit
  assertions passed. The command retains the pre-existing nonzero `c94` exit because global branch
  and function coverage remain below 75%.
- [x] All 23 applicable Playwright tests passed with 27 intentional project/environment skips. The
  no-YAML two-step first-run acceptance completed in 3.4 seconds with zero critical/serious axe
  findings, and the deterministic responsive screenshot export passed.
- [x] The rebuilt Compose API is ready at migration 56. An authenticated live browser run completed
  save, policy admission, a two-task/zero-unknown simulation, a test with zero production
  executions, launch and persisted trace navigation in 7.2 seconds.

Adversarial pass: invalid YAML falls back to the code editor; guided edits clear stale readiness;
code-only fields survive guide changes; unauthorized roles see disabled actions and plain-language
denials; simulation and tests require an unchanged saved revision.

Verdict: PASS — board card `c100` is verified.

## EPIC-808: Durable bounded single-agent sessions — 2026-08-25

Spec source: Agent Hotel card `c107`, ADR-053 and
`backlog/epics/epic-808-durable-bounded-single-agent-sessions.md`.

Verified with `uv`, PostgreSQL 17, Docker Compose, OpenRouter `openai/gpt-5.6-luna`, React and the
four generated SDKs:

- [x] One exact capability-envelope revision runs as an ordinary recoverable `agent.session` task.
  Migration 0058 persists tenant-isolated checkpoints and idempotent events, and stable model/tool
  operation identities reuse accepted effects after restart.
- [x] AMESH accepts one model proposal at a time, rejects unpinned tools, validates tool arguments
  before dispatch, requires a direct approved predecessor for high-impact tools or sensitive
  egress, and retains the accepted pending action before any external tool effect.
- [x] Cumulative turns, loop iterations, tool calls, tokens, cost and duration fail closed at the
  pinned envelope limits. Invalid final output either fails or uses only the declared bounded repair
  allowance; success requires the pinned output schema plus every deterministic business assertion.
- [x] Session start, model, policy, approval, tool, repair, acceptance and failure events project
  into ordinary execution evidence. The authorized session endpoint and React trace annotations
  expose phase, counters, validation gates and the explicit nondeterminism disclosure.
- [x] Twelve affected-path Python tests and two real-PostgreSQL migration/repository tests passed.
  Ruff lint passed and strict mypy passed all 229 source files. Twenty-six focused frontend
  assertions and the production TypeScript/Vite build passed.
- [x] OpenAPI, planning artifacts and all four SDKs regenerate deterministically across 2,355 files.
  Python compilation, TypeScript build, Java compilation and containerized Go tests passed.
- [x] Rebuilt Compose reports migration 58/58 ready. Live execution
  `01a036f3-eda7-77d1-838d-a46727e3aa8e` completed `SUCCESS` through OpenRouter Luna with a
  schema-valid summary, one passed business assertion, one durable model turn, 379 tokens and
  recorded cost `$0.0002178`.

Adversarial pass: exercised process loss after an accepted tool proposal, reused primitive results,
secret-redacted checkpoints, invalid-output repair, runaway turn/loop limits, unapproved
high-impact tools, missing exact authority and tenant isolation. OpenRouter's strict schema subset
was exercised live; tool arguments cross that provider edge as JSON text and AMESH decodes and
validates the object before dispatch.

Qualification boundary: model text remains explicitly nondeterministic. EPIC-808 qualifies durable
single-session control and deterministic acceptance gates, not memory quality, learned evaluation,
release promotion or multi-agent routing. Those remain fail-closed for EPIC-809/806. The full Ruff
format check still reports 75 pre-existing files outside this epic; no unrelated formatting was
included.

Verdict: PASS — EPIC-808 and `URS-F-0809`, `URS-F-0813`, `URS-F-0814` and `URS-F-0817` are verified.

## EPIC-312: Provider-neutral model, structured-output and MCP primitives — 2026-08-25

Spec source: Agent Hotel card `c105` and canonical
`backlog/epics/epic-312-provider-neutral-model-structured-output-and-mcp-primitives.md`.

Verified with `uv`, Python 3.13, PostgreSQL 17, Docker Compose, MCP v2 and OpenRouter:

- [x] Provider-neutral chat, embedding, structured-output and proposed tool-call tasks share one
  adapter port. Draft 2020-12 validation blocks invalid structured results and tool arguments before
  downstream work or tool execution.
- [x] Task contracts require an explicit endpoint, credential scope, model, token/cost budget,
  timeout, retry and data-handling policy. Redaction tests prove credential canaries are absent from
  provider payloads, invocation failures and task evidence.
- [x] PostgreSQL migration 56 adds immutable tenant-scoped MCP connection revisions and an invocation
  journal. Fresh-database tests cover revision lookup, completed-call reuse and rejection of an
  ambiguous started call after restart.
- [x] Governed MCP tests cover discovery, an allowlisted subset of a larger tool catalog, schema
  drift, input/output schema validation, duplicate-call reuse, write permission and direct approval
  for high-impact tools. API denial and upstream outage fail closed without returning credentials.
- [x] The AMESH MCP v2 endpoint rejects anonymous requests and exposes only authorization-checked
  read-only workflow listing and execution inspection. Protocol tests verify tenant-scoped reads,
  workload-token audience checks, read-only annotations and omission of task inputs/outputs.
- [x] `ruff check src tests scripts`, strict `mypy src`, `uv lock --check`, Python compilation and
  `git diff --check` passed. The complete affected-path command passed 26 domain, PostgreSQL, API,
  task, MCP protocol, migration, generated-contract, worker and service-role tests.
- [x] The live OpenRouter test passed against `openai/gpt-5.6-luna`. The rebuilt distributed Compose
  deployment is healthy at migration 56; execution `01a03635-e6e8-7d06-acf5-3ca8ec25afb8`
  completed with schema-validated output, 88 reported tokens, recorded cost, hash-only prompt
  provenance and a durable `SUCCEEDED` invocation row.

Adversarial pass: exercised invalid schemas, exceeded cost, credential leakage, duplicate and
restart ambiguity, unapproved tools, schema drift, missing approval, denied authorization, MCP
outage and anonymous MCP access. The first deployed structured request exposed an OpenAI structured
schema-subset constraint; the checked-in example now declares both `type` and `enum` and passed live.

Qualification boundary: `openai/gpt-5.6-luna` through OpenRouter is the qualified live adapter/model
pair. No third-party MCP server received production qualification; the external-client contract is
covered with in-process protocol and failure tests. Durable agent sessions, memory/evaluation and
multi-agent routing remain on `c106` through `c109`.

Verdict: PASS — EPIC-312 and URS-F-0383 through URS-F-0390 are verified.

## Bounded-agent roadmap definition — 2026-08-25

Spec source: product-owner request, ADR-049 and Agent Hotel cards `c105`–`c109`.

Verified with `uv` and the canonical planning generator:

- [x] EPIC-312, EPIC-807, EPIC-808, EPIC-809 and EPIC-806 form a dependency-ordered path from
  bounded model/MCP primitives through versioned capability envelopes, one durable agent session,
  memory/evaluation gates and final multi-agent routing.
- [x] URS-F-0806 through URS-F-0819 and all four agent NFRs map exactly to the new durable contract
  boundaries; the frozen corpus remains 837 functional plus 63 non-functional requirements.
- [x] `uv run python scripts/regenerate_planning_artifacts.py` reproduced the same diff hash on a
  second run, generated 106 epic projections and retained exactly 1,000 trace links.
- [x] `uv run --extra runtime --extra dev python scripts/validate_backlog.py` passed canonical JSON,
  Markdown bodies, issue export, parity, compatibility-inventory and exact traceability checks.
- [x] A scoped dependency reachability check found no cycle introduced by the five agent epics; the
  renamed EPIC-312 projection exists and its stale prior filename is absent.
- [x] Board revision 296 contains five To-Do cards with explicit dependencies, acceptance gates,
  verification requirements and non-goals; no card was represented as implemented.
- [x] `git diff --check` passed before publication.

Adversarial pass: checked duplicate/missing epic IDs, stale generated bodies, unmapped requirements,
trace-link count drift, regeneration nondeterminism, backward dependency reachability and accidental
runtime/dependency changes. Runtime tests and live deployment were not run because this milestone
changes planning artifacts only.

Verdict: PASS — roadmap definition is complete; implementation remains open on `c105`–`c109`.

## EPIC-608: Retention, purge and data lifecycle — 2026-08-23

Spec source: Agent Hotel card `c78` and
`backlog/epics/epic-608-retention-purge-and-data-lifecycle.md`.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript and Docker Compose:

- [x] Migration `0054_retention_lifecycle.sql` adds tenant-protected versioned policies, legal
  holds, purge jobs/items/evidence and transactional lifecycle events. A fresh database applied all
  54 migrations and PostgreSQL integration covered policy ownership and scope precedence.
- [x] Execution, log, metric, artifact and cache policies support instance, tenant, namespace and
  label scopes. Preview snapshots expose eligible bytes/records plus protected and active counts;
  API, CLI and UI execution require the exact `PURGE N` confirmation phrase.
- [x] Terminal execution data is scrubbed in bounded resumable batches while an execution/task-run
  tombstone preserves referential integrity. Events, logs, metrics, artifacts, caches and search
  projections are removed in authoritative order, and active orchestration is excluded.
- [x] Legal holds exclude matching metadata during preview and provider object-retention state is
  rechecked after the database decision. A simulated provider hold produced durable `FAILED` state
  and retry evidence; releasing it and resuming completed the object deletion and job.
- [x] Manual and scheduled policy paths, progress/failure/resume APIs, the `amesh lifecycle` CLI and
  the Administration Lifecycle view pass integration and interaction tests. Generated OpenAPI plus
  Python, TypeScript, Java and Go clients are current; retention and data-inventory docs are linked.
- [x] Fifteen focused backend/API/CLI/migration/role checks and all 46 frontend tests passed. Ruff
  passed `src`, `tests` and `scripts`; strict mypy passed all 198 source files; the production UI built.
- [x] Distributed and compact deployments are ready at migration 54. Live distributed HTTP created a
  tenant policy, previewed zero records/bytes, required `PURGE 0` and completed a `SUCCEEDED` job.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: external object-store provider qualification and long-duration high-volume
purge soak remain deferred. A broad shared-database run stopped on pre-existing authorization/queue
test contamination and a stale migration-51 assertion outside this epic; the fresh-database lifecycle
suite is green. Existing frontend lint and global coverage baselines remain deferred and unchanged.

Verdict: PASS — EPIC-608 functional requirements URS-F-0646 through URS-F-0653 are verified.

## EPIC-607: OpenTelemetry, Prometheus and log shipping — 2026-08-23

Spec source: Agent Hotel card `c77` and
`backlog/epics/epic-607-opentelemetry-prometheus-and-log-shipping.md`.

Verified with `uv`, Python 3.13, PostgreSQL 17, OpenTelemetry 1.44 and Docker Compose:

- [x] The official OpenTelemetry SDK emits redacted spans for API, scheduler, executor, worker,
  storage, messaging, plugin and runner operations. W3C `traceparent` propagation passes through
  commands, reducer events, durable envelopes, task/runner/plugin requests and subflow triggers.
- [x] Migration `0053_observability_trace_context.sql` captures the active redacted carrier on
  execution and task-run events. A fresh database applied all 53 migrations and exposed both columns
  and triggers; live repository integration proved both event streams persisted the parent carrier.
- [x] Prometheus publishes bounded operation, queue, worker-capacity, admission-pressure, database,
  search-lag, stuck-work, exporter-failure and log-drop signals without tenant, flow, execution,
  task-run, correlation or trace IDs as default labels.
- [x] Newline JSON logs include component, version, correlation and trace metadata. Bounded non-blocking
  queues ship to stdout, rotating file or UDP syslog; overflow and exporter failure increment metrics
  without failing the operation. A seeded secret was absent from exported span attributes/events.
- [x] Helm packages a seven-panel Grafana dashboard plus availability, latency, saturation, failure,
  lag and stuck-work alerts. Every alert has severity, symptom, likely causes, impact and a resolvable
  runbook section. The tenant-scoped diagnostic API returns fixed metrics, component/version evidence
  and only tenant-matched redacted recent errors.
- [x] Focused telemetry, configuration, reducer, transport, worker, storage and plugin suites passed.
  Ruff passed affected paths, strict mypy passed all 194 source files, both Compose files validated,
  and Python/TypeScript/Java/Go generated SDK freshness covered 1,828 files.
- [x] The distributed six-role deployment and compact deployment rebuilt and are healthy. Live HTTP
  responses include `traceparent`; `/metrics` exposes the new signals; logs contain JSON trace/span,
  component and version fields; diagnostics report version 0.2.0; both databases are at migration 53.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: the provisional 50,000-log-record/second standard-cluster target, simulated
Prometheus firing review and shared pre-GA security/support-bundle qualification remain deferred. The
local implementation proves bounded overload and telemetry-outage isolation; no external cluster
throughput claim is made. The existing c29 order-dependent uninitialized storage-histogram assertion
remains deferred and does not affect the EPIC-607 paths.

Verdict: PASS — EPIC-607 functional requirements URS-F-0638 through URS-F-0645 and
URS-NFR-OPERABILITY-002 are verified.

## EPIC-604: Search and analytics projection backend — 2026-08-23

Spec source: Agent Hotel card `c76` and canonical `backlog/epics.json` EPIC-604 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript and Docker Compose:

- [x] Migration `0052_search_projection_backend.sql` adds a tenant-protected, eight-way
  hash-partitioned v2 projection for flows, executions, task runs, logs, metrics, assets and audits;
  schema/table/index/materialized-view/rollup component versions; durable per-type checkpoints;
  retention archives; daily rollups; forced RLS; grants; and seed-forward from v1.
- [x] The indexer performs bounded incremental projection into versioned generations. Exact per-type
  identity/version counts and checksums gate an atomic generation switch. Projector failure state,
  durable resume, scoped tenant/type/time rebuild and a concurrent non-selected source write during a
  scoped rebuild all pass on a fresh PostgreSQL database while the active generation remains readable.
- [x] Tenant-isolation tests prove disjoint source and search results. Deleted source rows move into a
  tenant-protected archive with source-retention policy and purge time before leaving the projection;
  verified checkpoints and daily rollups persist for the active generation.
- [x] Authorized status, exact verification, scoped rebuild and enable/disable APIs pass positive and
  negative tests. Disabled projection serves bounded authoritative flow/execution queries, marks
  `authoritativeFallback`, and explicitly denies projection-only resource types.
- [x] A 50,000-row structured/full-text projection query returned 50 bounded results across 20 measured
  calls with the integration test's p95 below 0.5 seconds. The separate external 10-million-document
  qualification remains deferred and is not claimed.
- [x] Thirteen affected backend, API, migration, role, compact/preflight and generated-contract tests
  passed. Ruff passed affected paths, strict mypy passed all 194 source files, 20 frontend assertions
  passed, the production frontend built, and Python/TypeScript/Java/Go SDK checks covered 1,828 files.
- [x] The distributed deployment rebuilt API/indexer images, completed a live scoped blue-green switch
  to generation 2 at approximately 388,000 authoritative documents, kept orchestration roles healthy,
  and passed live disable → authoritative flow fallback with projected log denial → enable. The compact
  deployment is healthy on port 8100 with 52/52 migrations and schema version 2.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: the EPIC-604 search contribution to graceful degradation and tenant isolation
is locally exercised. Shared `URS-NFR-RELIABILITY-005` still requires the remaining optional-service
outage/latency work mapped to EPIC-401/409/607, and shared `URS-NFR-SECURITY-001` still requires the
independent pre-GA penetration test. Neither shared NFR is promoted here.

Verdict: PASS — EPIC-604 functional requirements URS-F-0614 through URS-F-0621 are verified.

## EPIC-600: Standalone server and compact deployment — 2026-08-23

Spec source: Agent Hotel card `c75` and canonical `backlog/epics.json` EPIC-600 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript and Docker Compose:

- [x] `amesh-compact` starts webserver, executor, scheduler, worker, indexer and maintenance as
  supervised tasks in one process. The distributed Compose profile starts the same six roles as
  independent services; both use PostgreSQL for authoritative state, leases and queueing.
- [x] The configurable local filesystem adapter provides immutable SHA-256 object versions,
  tenant-scoped opaque URIs, ranges, lifecycle metadata, reload and deletion. The existing
  S3-compatible adapter remains selectable through configuration.
- [x] `amesh-preflight` fails startup before admission for invalid configuration, credentials,
  database, migration or storage state. `/health` remains a distinct liveness signal while `/ready`
  reports READY, DEGRADED or UNAVAILABLE dependencies and exact migration parity.
- [x] `uv build --wheel --out-dir dist/epic600` succeeded. Wheel inspection found the compact and
  preflight modules, all 51 migration SQL files and the `amesh`, `amesh-compact`, `amesh-migrate` and
  `amesh-preflight` console scripts. Both Compose files pass `docker compose config --quiet`.
- [x] Twenty-six focused compact, preflight, local-storage and deployment tests passed. The expanded
  affected-path run passed 28 tests before the pre-existing shared-live-database final-admin test
  contamination recorded on board card `c95`; its new readiness assertions passed before that
  unrelated failure. Ruff, strict mypy across 194 source files, generated-contract checks and
  `git diff --check` passed.
- [x] Frontend client and blueprint unit suites passed 20 assertions, the production frontend build
  passed, and OpenAPI plus Python, TypeScript, Java and Go SDKs are current.
- [x] Live compact deployment on port 8100 reported 51/51 migrations and all six roles live, ready
  and AVAILABLE. `examples/hello-world.yaml` completed SUCCESS with `Hello World`; restart retained
  the flow. SIGTERM stopped admission, drained the process in 1.46 seconds and persisted all six
  roles as STOPPED before a healthy restart.
- [x] Live distributed deployment on port 8000 reported every readiness dependency READY at 51/51,
  and all six service roles were live, ready and AVAILABLE through the authenticated topology API.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: the local compact and distributed reference paths are qualified. The shared
`URS-NFR-AVAILABILITY-001` 99.9% monthly SLO requires an external production-profile soak, and
`URS-NFR-USABILITY-003` requires the scheduled external contributor study; neither is claimed here.

Verdict: PASS — EPIC-600 functional requirements URS-F-0582 through URS-F-0589 and the locally
qualifiable health-model requirement URS-NFR-OPERABILITY-001 are verified.

## EPIC-510: Flow unit tests and quality gates — 2026-08-23

Spec source: Agent Hotel card `c74` and canonical `backlog/epics.json` EPIC-510 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] Migration `0051_flow_tests_quality_gates.sql` applies to a fresh database and durably stores
  tenant-isolated test definitions, immutable runs and namespace promotion gates with optimistic
  versions, authorization grants, row-level security and lifecycle audit events.
- [x] The versioned `amesh.flow-test/v1` simulator evaluates inputs, variables, expressions,
  branches, retries, error/finally/after handlers and generated loop task graphs without dispatching
  production work. Inline, plugin and recorded fixtures replay deterministic external responses.
- [x] Assertions cover terminal state, outputs and task states. Observed task, branch, handler and
  condition coverage includes an explicit disclaimer that it is not proof of full workflow semantics.
- [x] Authorized API, JSON-emitting CLI, graphical Unit tests page and CI-friendly exit codes run
  selected revision-pinned tests. The gate requires exact passing flow semantic, plugin-set and
  simulator-version pins before ACTIVE promotion; a gated new revision is automatically DRAFT.
- [x] Fresh-PostgreSQL integration proved durable reload, stale-version rejection, audit persistence,
  gate rejection/recovery and zero production executions or artifacts. Secret-like test data is
  rejected before persistence, and run results report zero secret lookups.
- [x] Ruff passed affected paths and strict mypy passed all 191 source files. Sixteen focused backend
  tests, 17 frontend client assertions, the production frontend build, generated-contract checks and
  the targeted Chromium acceptance test passed; all four generated SDKs are current.
- [x] API, executor, scheduler and indexer images rebuilt successfully and are healthy. Live readiness
  reports 51/51 with `0051_flow_tests_quality_gates.sql`. The deployed
  `tests.flowtests.live.promotion_demo` was blocked before testing, passed at 66.67% observed coverage
  with zero side effects, and then promoted to ACTIVE through both HTTP and CLI paths.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: this epic implements the smallest revision-pinned simulator contract needed
for deterministic flow tests. Broader simulator estimation, plan-diff and signing work remains in
EPIC-800, and observed coverage is intentionally not claimed as semantic proof.

Deferred unrelated test hygiene: the isolated observability test still expects a storage histogram
to have been initialized by another test; its database readiness assertions passed at 51/51, and the
live readiness endpoint independently passed. No storage code was changed.

Verdict: PASS — EPIC-510 functional requirements URS-F-0574 through URS-F-0581 are verified.

## EPIC-509: Announcements, maintenance mode and kill switch — 2026-08-23

Spec source: Agent Hotel card `c73` and canonical `backlog/epics.json` EPIC-509 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] Migration `0050_operational_controls.sql` applies to a fresh database and adds scheduled
  announcements, scoped maintenance/kill-switch state, component acknowledgements, lifecycle
  evidence, expiry processing, tenant RLS and PostgreSQL change notifications.
- [x] Instance, tenant, namespace, flow, plugin and runner scopes independently gate authoring, new
  executions, triggers, API writes and worker dispatch. Emergency controls require actor, reason and
  expiry or review time; optimistic versions protect extend, bypass and deactivate actions.
- [x] Existing work follows an explicit `CONTINUE`, `DRAIN` or `CANCEL` policy. Direct worker tests
  proved DRAIN preserves running work without dispatch, cron launch is blocked before persistence,
  and accepted trigger occurrences can be deferred without consuming a delivery attempt.
- [x] Fresh-PostgreSQL repository coverage proved tenant isolation, runtime RLS, target matching,
  severity ordering, version conflict, acknowledgement, bypass, deactivation, automatic expiry and
  `ACTIVATE`/`BYPASS`/`DEACTIVATE`/`EXPIRE` evidence. Authorized API coverage proved announcement
  publication, an actual HTTP `423` write gate, acknowledgement visibility and recovery actions.
- [x] The Administration Controls UI publishes announcements and operates maintenance or kill
  switches with boundary, scope, target, running-policy and expiry controls. Targeted Chromium
  acceptance, the existing administration regression and the production frontend build passed.
- [x] Ruff passed on affected paths and strict mypy passed across 187 source files. Focused migration,
  scheduler, trigger, backfill, worker, service-role, repository, API and generated-contract tests
  passed; OpenAPI and Python, TypeScript, Java and Go SDKs are current.
- [x] API, executor, scheduler and indexer images rebuilt successfully and are healthy. Live readiness
  reports 50/50 with `0050_operational_controls.sql`. A live control rejected a tenant write with
  HTTP `423`, then exposed version-1 acknowledgements from webserver, scheduler, executor and indexer
  within six seconds before bypass/deactivation; the test announcement was also removed.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: local durable drain, retry and propagation behavior is qualified. External
multi-node rolling-upgrade transfer, failure-zone behavior and silent-loss certification remain
unverified under shared `URS-NFR-AVAILABILITY-004`; EPIC-509 does not claim those external results.

Deferred unrelated test hygiene: the broad API run still sees the existing exact UI-capability list
drift introduced by EPIC-508 and shared live-database final-admin contamination. Focused EPIC-509 API
coverage passes against a fresh database. The known `c29` storage-metric registration assertion also
remains dependent on process registration state. These findings do not affect the shipped control
path.

Verdict: PASS — EPIC-509 functional requirements URS-F-0566 through URS-F-0573 are verified.

## EPIC-508: Apps, forms and human approval tasks — 2026-08-23

Spec source: Agent Hotel card `c72` and canonical `backlog/epics.json` EPIC-508 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] Migration `0049_workflow_apps_human_tasks.sql` applies to a fresh database and adds immutable
  app revisions plus tenant-RLS-protected human-task, action and participant-notification ledgers.
- [x] Apps pin a flow revision, retain optimistic resource versions, reload historical revisions and
  generate controls from flow display, help, placeholder, default, values, validation and schema
  metadata. Explicit layouts reject unknown fields or missing required inputs.
- [x] `core.approval` durably defers execution without retaining a worker, accepts user/group
  participants, deadlines and escalation participants, and creates its task idempotently across
  executor recovery. Delegation, comment and artifact actions share the durable action ledger.
- [x] Fresh-PostgreSQL coverage proved outsider filtering, deadline escalation, terminal decision
  audit/evidence, process-safe pending resume and duplicate decision convergence to one successful
  task result and one successful execution.
- [x] Authorized API coverage created/listed/read immutable app revisions, generated an app form,
  rejected a stale update, listed an assigned approval, approved it and proved participant notices do
  not contain execution IDs or submitted form values.
- [x] The Apps UI launches a dynamic form, operates the approval inbox and serves both direct and
  shell-free embed links. Targeted Chromium acceptance and the production frontend build passed.
- [x] Ruff passed on affected paths and strict mypy passed across 186 source files. Focused migration,
  executor, worker, repository and API regression tests passed; generated OpenAPI and four SDKs are
  current across 1,688 files.
- [x] API, executor, scheduler and indexer images rebuilt successfully and are healthy. Live readiness
  reports 49/49 with `0049_workflow_apps_human_tasks.sql`. A live sample app launched, exposed its
  approval, recorded `APPROVED` and completed its execution `SUCCESS` with decision evidence.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: app authoring is API-first in this epic; the graphical surface covers app
launch, link/embed use and participant approval operations.

Verdict: PASS — EPIC-508 functional requirements URS-F-0558 through URS-F-0565 are verified.

## EPIC-507: Assets, lineage and catalog — 2026-08-23

Spec source: Agent Hotel card `c71` and canonical `backlog/epics.json` EPIC-507 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] Migration `0048_asset_catalog_lineage.sql` applies to a fresh database and extends the existing
  catalog with provider/account/location/type/external-key identity, namespace governance metadata,
  tenant RLS, durable observations and confidence-bearing lineage edges.
- [x] Explicit declarations and authenticated isolated-plugin `amesh.asset` READ/WRITE notifications
  use the same normalized persistence contract. Runtime evidence retains flow, execution, task-run and
  artifact references; a write advances health and last materialization.
- [x] PostgreSQL integration proved full identity discrimination, duplicate edge convergence, restart
  reload, tenant separation, declared and inferred lineage, 0.8 confidence derivation and official
  OpenLineage dataset naming/event export.
- [x] Authorized API coverage registered assets, observations and lineage, hid a denied-namespace
  neighbor from list and traversal results, returned catalog detail, and exported OpenLineage events.
- [x] The Assets UI lists and filters catalog entries, displays upstream/downstream and execution or
  artifact evidence, creates explicit declarations, and downloads the OpenLineage export. Targeted
  Chromium acceptance and the production frontend build passed.
- [x] Ruff passed on affected paths and strict mypy passed across 181 source files. Focused migration,
  executor, plugin, PostgreSQL, API and UI-session tests passed; the fresh-schema repository test and
  generated contracts/SDKs were executed with `uv`.
- [x] API, executor, scheduler and indexer images rebuilt successfully. Live readiness reports 48/48
  with `0048_asset_catalog_lineage.sql` after the explicit migration runner completed.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: OpenLineage is an export interchange contract; this epic does not qualify or
operate an external OpenLineage catalog service.

Verdict: PASS — EPIC-507 functional requirements URS-F-0550 through URS-F-0557 are verified.

## EPIC-505: Plugin allow, restrict and version policy — 2026-08-23

Spec source: Agent Hotel card `c70` and canonical `backlog/epics.json` EPIC-505 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] Scoped allow/deny rules match packages, plugin types, semantic-version ranges, vendors and
  capabilities at instance, tenant and namespace levels. Explicit deny and quarantine override allow;
  the production-oriented default fails closed for unreviewed third-party plugins while retaining the
  built-in `amesh.core` trust root.
- [x] Authoring, validation, execution and administration are separate policy stages. Flow save and
  execution start both enforce policy, and execution uses the revision's frozen package/version/digest
  resolution rather than re-resolving a mutable catalog.
- [x] Durable quarantine preserves version/reason/actor/history, prevents duplicate active entries,
  supports audited release, and previews exact affected flow revisions and currently running
  executions before mutation.
- [x] The authorized API exposes effective rules and decision sources, rule/quarantine lifecycle,
  impact preview and decision history. Offline bundle installation passes through the administration
  gate before catalog mutation.
- [x] The Plugins UI explains the effective default/source, manages rules, lists active quarantines
  and requires a preview before emergency disable. Chromium verified the preview-before-mutation flow
  and capability-gated controls.
- [x] Ruff passed on affected Python paths; strict mypy passed across 181 source files. Focused unit,
  PostgreSQL, API, plugin pinning, worker and migration tests passed. Frontend production build, all 43
  unit assertions, targeted Chromium end-to-end coverage and generated-SDK currency across 1,564 files
  passed.
- [x] The full repository run's directly caused worker mock incompatibility was corrected and its
  regression passes. Remaining failures are pre-existing or live-database test-isolation issues
  tracked on cards `c15`, `c29` and `c95`; no unrelated subsystem was changed. The existing global
  frontend lint issue remains tracked on `c88`.
- [x] API, executor, scheduler and indexer containers are healthy. Live readiness reports 47/47 with
  `0047_plugin_governance.sql`; live effective-policy evaluation, temporary rule lifecycle and a
  non-mutating quarantine impact preview passed.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable LLM tests
  remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: `URS-NFR-SECURITY-010` remains In Progress until EPIC-003, EPIC-403 and
EPIC-612 plus the production security baseline scanner complete the whole-platform fail-closed
qualification.

Verdict: PASS — EPIC-505 functional requirements URS-F-0534 through URS-F-0541 are verified.

## EPIC-504: Immutable audit log and evidence export — 2026-08-23

Spec source: Agent Hotel card `c69` and canonical `backlog/epics.json` EPIC-504 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and Docker Compose:

- [x] Migration `0046_audit_evidence_ledger.sql` applied repeatably to fresh databases and hardened
  the shared audit table with recursive protected-field redaction, required reason/correlation/trace
  context, per-tenant serialized SHA-256 chaining, independent retention, legal holds and purge
  anchors. The trigger also passed through the restricted tenant-administrator write path.
- [x] PostgreSQL integration inserted a nested secret canary and observed only `[REDACTED]`, verified
  a valid chain, proved an active hold blocks expired-prefix purge, released the hold, preserved the
  purge anchor, and then detected a deliberately modified row as `HASH_MISMATCH`.
- [x] Every authorization decision, including a cached decision, calls the configured audit sink.
  Existing transactional authentication, resource, execution, secret, policy and administration
  producers continue through the same database-enforced audit contract.
- [x] The authorized HTTP lifecycle changed retention, created/listed a legal hold, recorded redacted
  compliance evidence, queried the ledger, observed `audit.read` evidence, verified integrity,
  downloaded signed JSON and a signed compliance ZIP, and denied a principal without tenant access
  using the non-disclosing `404 tenant unavailable` boundary.
- [x] Deterministic artifacts carry SHA-256 checksums and `v1=` HMAC signatures. The compliance ZIP
  contains access-review, change, audit, backup/restore, vulnerability, incident and provenance
  sections plus a signed manifest. Object-storage upload passed in memory; the existing signed,
  retryable realtime webhook subscription with `includeAudit=true` supplies the external SIEM path.
- [x] Ruff and strict mypy across 178 source files passed. Eighteen focused domain, authorization,
  PostgreSQL, API, migration and operations tests passed. OpenAPI/schema generation and all four
  generated SDKs are current across 1,504 files; backlog regeneration, validation and clean-room
  gates passed.
- [x] The full repository run identified only already-tracked unrelated baseline failures: executor
  timing (`c15`), the 5,000-line DSL performance threshold (`c89`) and test-order-dependent storage
  metric registration (`c29`). Migration-count assertions directly affected by 0046 were updated and
  pass; no unrelated subsystem was changed.
- [x] API, executor, scheduler and indexer containers are healthy. Live readiness reports 46/46 with
  `0046_audit_evidence_ledger.sql`; the default tenant's 157-event chain verified, and live audit JSON
  and compliance ZIP downloads both returned signed artifacts.
- [x] No LLM behavior was involved, so no billable OpenRouter call was required. Applicable future LLM
  tests remain pinned to `openai/gpt-5.6-luna`.

Qualification boundary: this is functional compliance-readiness evidence, not SOC 2 or ISO/IEC 27001
certification. Shared audit completeness, whole-platform data inventory and control-crosswalk NFRs
remain In Progress until their broader pre-GA evidence and independent review gates complete.

Verdict: PASS — EPIC-504 functional requirements URS-F-0526 through URS-F-0533 and URS-F-0835 are
verified.

## EPIC-502: SSO, OIDC, SAML, LDAP and SCIM — 2026-08-23

Spec source: Agent Hotel card `c68` and canonical `backlog/epics.json` EPIC-502 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] Locally signed OIDC tokens exercised authorization code plus PKCE S256, state, nonce,
  configurable claims, asymmetric algorithm allowlisting, issuer/audience/expiry validation, 60-second
  clock skew, live JWKS signing-key rotation, one-time replay rejection, domain/tenant routing, provider
  denial and outage behavior. Rotating the mounted client-secret file changed the next token request.
- [x] Strict SAML service-provider configuration produced signed AuthnRequests and metadata containing
  current and next certificates. The runtime requires signed assertions, signed requests/logout,
  non-deprecated algorithms, replay-fenced response/assertion identifiers and configured IdP
  certificate bundles.
- [x] LDAP/AD configuration rejected cleartext transport, required verified TLS for LDAPS or StartTLS,
  performed user-bind/group lookup, and mapped the authenticated claims through the same federated
  identity boundary.
- [x] PostgreSQL integration verified one-time state, replay fences, immutable provider/subject links,
  ambiguous-email rejection, explicit tenant role and provider-owned group mapping, and SCIM lifecycle.
  The SCIM API test covered token rotation, bearer/provider isolation, user/group create/list/filter,
  PATCH, disable/reactivate, session fencing, membership changes and deprovision/delete.
- [x] Ruff and strict mypy across 174 source files passed. The eight focused domain, PostgreSQL and API
  tests passed; generated-contract and SDK-manifest tests passed; OpenAPI/schema generation was
  deterministic and all four SDKs were current across 1,428 files. Python bytecode, TypeScript targets
  and Java sources compiled. Go was not installed locally and its compile check is not claimed.
- [x] Fifteen focused frontend client assertions, targeted ESLint, the production build and the
  Chromium provider-routing workflow passed. The isolated client-test command still reports the
  existing global branch/function coverage threshold tracked on card `c94`; all selected assertions
  passed and the production artifact was generated.
- [x] Compose validation and image build passed. Helm identity values and templates were inspected, but
  the workstation has no Helm executable, so render qualification is deferred and not claimed.
- [x] API, executor, scheduler and indexer containers are healthy. Live readiness reports 45/45
  migrations with `0045_identity_federation.sql`; the new identity tables exist, the UI returns 200,
  provider discovery returns the configured local provider, missing SCIM bearer returns 401, and
  Authlib, ldap3, python3-saml and xmlsec import inside the production image.
- [x] No LLM behavior was involved, so no OpenRouter call was required. OpenRouter remains configured
  for `openai/gpt-5.6-luna` when an applicable LLM epic requires it.

Qualification boundary: no external enterprise IdP account is needed for local protocol conformance;
operators must supply their own issuer/directory endpoints and mounted credentials for live vendor
interoperability. Shared `URS-NFR-SECURITY-006` remains In Progress until its EPIC-506 and EPIC-613
component/certificate work is complete.

Verdict: PASS — EPIC-502 functional requirements URS-F-0510 through URS-F-0517 are verified.

## EPIC-411: Blueprints, playground and onboarding — 2026-08-23

Spec source: Agent Hotel card `c67` and canonical `backlog/epics.json` EPIC-411 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] Three checked-in versioned local blueprints represent built-in, organization and community
  catalogs. Domain and API tests verified search/source filtering, typed/default parameters,
  documentation, license and immutable SHA-256 provenance.
- [x] Every blueprint instantiated into a valid native flow. The authorized API returns YAML plus
  validation evidence without a repository dependency; Chromium transferred the built-in example to
  the existing editor as a dirty unsaved draft and observed no execution request.
- [x] The playground reuses native expression redaction and flow validation. Focused tests and live
  deployment returned `[REDACTED]` for a token-shaped input and explicit `false` values for persistence,
  execution, credential access and infrastructure access.
- [x] The setup guide reports live database/migration, object-storage, executor and interactive-auth
  readiness. Its four completion steps are tenant/principal scoped in browser local storage and
  survived Chromium reload without an external telemetry request.
- [x] All 43 frontend unit tests passed; the production build, targeted ESLint and full Playwright
  matrix passed with 13 Chromium workflows and 13 tablet-inapplicable skips. The blueprint workflow
  reported no critical or serious axe findings. The separate global branch-coverage threshold remains
  deferred on board card `c94` after reporting 69.23% against 75%.
- [x] Focused domain/API/generated-contract tests passed. Ruff, strict mypy across 170 source files,
  deterministic OpenAPI/schema generation, planning regeneration and backlog validation passed.
  Python and TypeScript generated clients compiled, Java assembled, and SDK freshness covered 1,380
  files; Go was not installed locally and was not claimed.
- [x] The broad backend collection had one non-functional timing miss: the existing board-card `c89`
  5,000-line DSL p95 check measured 1.009 seconds against 1.000. It is unrelated to the blueprint path;
  all seven focused blueprint domain/API tests and the generated-contract check passed.
- [x] Rebuilt API, executor, scheduler and indexer containers are healthy. Live readiness reported
  44/44 migrations; catalog/API smoke returned three sources and a valid draft; headless Chromium
  opened `/blueprints`, rendered three cards, all four all-false playground safety facts and four ready
  onboarding prerequisites with zero alerts.
- [x] No dependency or LLM call was required. OpenRouter remains configured for
  `openai/gpt-5.6-luna` when a later behavior test needs an LLM.

Qualification boundary: the recurring external quarterly median required by shared
`URS-NFR-USABILITY-003` cannot be produced by local development and is deferred on card `c93`. The
local documented path and automated first-run workflow are complete; the shared NFR remains Proposed.

Verdict: PASS — EPIC-411 functional requirements URS-F-0486 through URS-F-0493 are verified.

## EPIC-410: Namespace, settings and administration UI — 2026-08-23

Spec source: Agent Hotel card `c66` and canonical `backlog/epics.json` EPIC-410 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] The permission-gated administration workbench browses dotted namespace hierarchy, selected
  resource counts and inherited workflow/plugin-default provenance, while linking to the existing
  namespace resource manager.
- [x] Existing server-authoritative user, group, role, binding, service-account, token and identity
  provider contracts are composed into one access view. Issued token material is shown once.
- [x] Readiness, service topology, workers, admission queues, object storage, migrations and search
  freshness are available in the ten-second operations view.
- [x] Retention, announcements, maintenance mode and the execution kill switch use typed tenant
  controls backed by the existing versioned feature-flag repository. Ordinary feature flags remain
  independently manageable.
- [x] High-risk applies require a five-minute HMAC approval bound to actor, tenant and complete draft,
  an impact/recovery preview and exact confirmation. Tampered, expired, cross-actor and changed-draft
  tests all rejected deterministically.
- [x] Successful control state plus its immutable `SUCCESS` audit entry commit atomically. Rejected
  confirmations and version conflicts record `REJECTED` evidence without changing the control. A
  fresh PostgreSQL integration test verified both outcomes and cross-tenant audit isolation.
- [x] Effective configuration reports provenance and reloadability while both server and UI hard-redact
  secret-typed values. Browser acceptance confirmed the canary secret was absent.
- [x] Focused domain/API tests, Ruff and strict mypy passed; 17 focused frontend unit tests, targeted
  lint, the production build and the Chromium administration workflow passed. Axe found no critical
  or serious finding in the guarded workflow.
- [x] The rebuilt API/UI container reached healthy state; `/ready` reported 44/44 migrations and the
  deployed `/administration` route returned HTTP 200. Live guarded preview/apply persisted a disabled
  announcement with `SUCCESS` audit evidence, while direct reserved feature-flag bypass returned 409.
- [x] No dependency or LLM call was required. OpenRouter remains configured for
  `openai/gpt-5.6-luna` when a later behavior test needs an LLM.

Verdict: PASS — EPIC-410 functional requirements URS-F-0478 through URS-F-0485 are verified.

## EPIC-409: Search, indexing and retrieval projections — 2026-08-23

Spec source: Agent Hotel card `c65` and canonical `backlog/epics.json` EPIC-409 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] The indexer projects authorized flow, execution, selected non-sensitive log, asset and audit
  metadata into a replaceable tenant-hash-partitioned PostgreSQL projection. Redacted log content is
  not indexed and source repositories remain authoritative.
- [x] Typed full-text, trigram, field, range, state, label, namespace and time filters passed repository
  tests. Relevance and whitelisted field sorts use deterministic tie-breakers and opaque cursors reject
  changed request fingerprints.
- [x] A tenant rebuild deleted only projection rows, incremented its version, repopulated from sources
  and emitted immutable requested/completed evidence through the outbox. Status exposed condition,
  counts, progress, lag, timestamps, failures and last error.
- [x] A forced search failure recorded `DEGRADED` state while a new execution was accepted and the
  indexer continued webhook/outbox work. A following healthy projection converged and returned
  `READY`, demonstrating optional-search outage isolation.
- [x] Fresh-database integration exercised PostgreSQL RLS with two tenants and observed disjoint result
  IDs. The API separately authorized every requested resource type, reported denied types and never
  sent them to the repository.
- [x] A repeatable local 50,000-document search corpus passed the provisional p95 below 500 ms gate for
  the fixed structured/full-text workload. The dedicated 10-million-retained-execution qualification
  is deferred to a scale environment and does not block local functional delivery.
- [x] The control room provides command-palette results and a dedicated workbench with all filters,
  cursor paging, deep links, status, lag/failure indicators and authorized rebuild. Chromium covered
  the workflow; 35 frontend unit tests, the production build and targeted lint passed.
- [x] Focused API, service-role, authenticated MVP, repository and migration tests passed. Ruff and
  strict mypy for 168 source files passed. Rebuilt API, executor, scheduler and indexer containers are
  healthy; `/ready` reports `0044_search_projection.sql` at 44/44, live search returned tenant results
  and the deployed `/search` HTML route returned HTTP 200.
- [x] No LLM call or Python dependency was required. OpenRouter remains configured for
  `openai/gpt-5.6-luna` when a later behavior test needs an LLM.

Verdict: PASS — EPIC-409 functional requirements URS-F-0470 through URS-F-0477 are verified.

## EPIC-408: Dashboards, query language and saved views — 2026-08-23

Spec source: Agent Hotel card `c64` and canonical `backlog/epics.json` EPIC-408 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, React/TypeScript, Chromium and Docker Compose:

- [x] Six code-defined instance, tenant, namespace, flow, worker and SLA dashboards execute across
  the execution, log, metric, SLA, worker and asset projections. They cover time series, tables,
  counters, distributions, status breakdowns and ranked lists.
- [x] The public typed model accepts only enumerated sources, measures, aggregations and
  visualizations plus whitelisted dimensions; invalid dimensions and source/measure pairs return a
  deterministic validation error and no API accepts raw SQL.
- [x] Time, labels, namespace, flow, state, worker group and custom dimensions are supported. The
  repository enforces the 90-day range, 500-result limit, 20,000-row scan cap, 100-5,000 ms database
  timeout and deterministic sampling before bounded aggregation.
- [x] Custom API/GitOps definitions use optimistic versions, independent private/tenant viewer and
  editor ACLs, immutable definition events and transactional outbox publication. YAML/JSON export,
  deep-link sharing and soft deletion were exercised.
- [x] Widget source authorization remains independent from definition authorization. An SLA render
  under a principal lacking check access returned explicit redacted placeholders, while its direct
  query was denied. Results report freshness, scanned/matched counts, sampling and partial state.
- [x] The control room renders all supported chart forms, edits typed custom views and exposes filter,
  freshness, partial, sampled, authorization and redaction state. Chromium covered filtering,
  creation, permission fields, export and deletion; axe reported no critical or serious findings.
- [x] Fresh PostgreSQL repository and API suites applied all 43 migrations and passed every built-in
  source. Frontend unit tests passed 31 tests with 91.27% statement coverage; the production build,
  targeted lint, strict mypy for 165 source files and focused Ruff checks passed.
- [x] Generated OpenAPI and Python, TypeScript, Java and Go SDK surfaces include the dashboard API.
  Rebuilt API, executor, scheduler and indexer containers are healthy; `/ready` reports migration
  `0043_dashboards.sql` at 43/43 and the deployed frontend returns HTTP 200.
- [x] No LLM call or Python dependency was required. OpenRouter remains configured for
  `openai/gpt-5.6-luna` when a later behavior test needs an LLM.

Verdict: PASS — EPIC-408 functional requirements URS-F-0462 through URS-F-0469 are verified.

## EPIC-303: Isolated language-neutral plugin runtime — 2026-08-23

Spec source: Agent Hotel card `c53` and canonical `backlog/epics.json` EPIC-303 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, JDK 21, Dockerized Go 1.23 and
TypeScript/Node 22, and Docker Compose:

- [x] The generated `amesh.plugin.wire/v1` JSON-RPC 2.0 newline-frame contract covers exact
  manifest/schema discovery, configuration validation, execution, cancellation, authenticated
  heartbeats, logs, metrics, artifacts and structured request/response errors. Handshake tests
  negotiate the version and complete required feature set before any plugin callback.
- [x] Exact package name/version/SHA-256 revision pins select administrator-configured managed local
  processes. Commands run without a shell from the package root in a minimal environment; stdio
  entry points execute outside API/executor processes and runtime-owner collisions fail closed.
- [x] Every process receives a random session ID and short-lived opaque workload token over stdin,
  never through its environment. Every successful response and notification echoes and verifies the
  identity. Per-call envelopes include fresh declared capability tokens, only declared-and-resolved
  secret scopes/files, exact declared egress and administrator-approved platform APIs.
- [x] Per-package semaphores enforce concurrency. Invocation wall time, heartbeat silence, combined
  stdout/stderr and frame bytes, and process-tree CPU/RSS are bounded; typed cancellation and stable
  retryable, timed-out, cancelled, configuration and user-code failures were verified.
- [x] A child deliberately exited on attempt one. The next call started a fresh service and runtime
  counters reported one crash/one restart. A real PostgreSQL-backed `InProcessExecutor` then proved
  the same failure reached attempt two on the existing durable task run and completed successfully.
- [x] Python's `serve_stdio_plugin` receives both the typed request and capability envelope and
  streams typed evidence. The shared generated schema plus checked-in Java, strict TypeScript and Go
  contract surfaces compiled successfully with JDK 21, TypeScript/Node 22 and Go 1.23.
- [x] Authorized `GET /api/v1/plugins/isolated-runtime` exposes catalog generation, state, active and
  completed calls, starts/restarts/crashes, last PID and stable last-error code. The rebuilt deployed
  API returned `{"catalogGeneration":1,"plugins":[]}` with no services configured; API, executor
  and scheduler were healthy and `/ready` reported all 40 migrations applied.
- [x] Ten focused runtime/SDK checks passed with PostgreSQL enabled. A fresh migrated disposable
  database ran the 392-test collection with only authoritative cards `c15`/`c29` deselected:
  380 passed, ten environment/profile tests skipped, two deselected and no failures. The disposable
  database was dropped afterward.
- [x] Ruff, strict mypy for 146 source files, `uv lock --check`, generated OpenAPI/schema/planning,
  clean-room, backlog, Compose and diff gates passed. No Python dependency or LLM call was needed;
  OpenRouter remains configured for `openai/gpt-5.6-luna` when a later behavior test needs an LLM.

The reference launcher satisfies the managed local-process branch of URS-F-0314. OCI and remote
service deployment remain alternative administration profiles rather than a prerequisite for this
locally verified runtime. Shared deployment-wide privilege and isolation qualification remains In
Progress under URS-NFR-SECURITY-002 and URS-NFR-SECURITY-008's other owning epics.

Verdict: PASS — EPIC-303 functional requirements URS-F-0313 through URS-F-0320 are verified.

## EPIC-302: Trusted in-process plugin runtime — 2026-08-23

Spec source: Agent Hotel card `c52` and canonical `backlog/epics.json` EPIC-302 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and Docker Compose:

- [x] Only configured exact package name/version/SHA-256 digest approvals are imported. Unapproved
  package code was never imported, duplicate approvals failed configuration and missing or invalid
  approvals remained quarantined without preventing the service from starting.
- [x] Approved Python modules load beneath digest-derived private namespaces without changing
  `sys.path`; normal and timeout paths proved bounded async start/stop lifecycle hooks and namespace
  unload. Registration ownership prevents a different package from overriding a task identity.
- [x] Task callbacks dispatch through the exact package version and digest stored in
  `amesh.plugin-resolution/v1`. Both 1.0.0 and 2.0.0 were loaded concurrently and the selected pin
  invoked the correct version; a real PostgreSQL-backed `InProcessExecutor` completed a pinned
  plugin task and persisted its result.
- [x] Callback timeouts open a per-package circuit, reject calls while open and admit a bounded
  half-open probe after reset. Repeated timeout/unhandled/invocation-fence violations quarantine the
  exact version; configuration, compatibility and capability errors do not trip the circuit.
- [x] Authorized `GET /api/v1/plugins/trusted-runtime` status and Prometheus counters, histograms and
  gauges report lifecycle/circuit state, calls, errors, invariant violations, latency, quarantines,
  plugin-owned memory and observed host-process RSS.
- [x] The operator guide explicitly states that private Python namespaces are dependency and
  registration containment, not a security sandbox: trusted code shares the host process, memory,
  interpreter, environment, filesystem, network and credentials. Untrusted code remains EPIC-303.
- [x] Nine focused trusted-runtime tests passed, including approval denial, lifecycle failure,
  authorization, exact-version dispatch and PostgreSQL-backed execution. Generated settings and
  OpenAPI contracts match the checked-in files.
- [x] A freshly migrated disposable database ran the 382-test collection with the two authoritative
  `c15`/`c29` tests deselected: 370 passed, ten environment/profile tests skipped, two deselected and
  no failures. The disposable database was dropped after the run.
- [x] Ruff, strict mypy for 143 source files, clean-room policy, planning regeneration, backlog,
  Compose and generated-contract gates passed. Compose shares persistent `plugin-data` with both API
  and executor services. Rebuilt API, executor and scheduler services were healthy; the live
  authorized runtime endpoint returned generation one with no approvals configured and `/metrics`
  exposed the trusted-plugin series.

The circuit breaker uses small runtime-owned state because the reviewed general-purpose packages do
not integrate AMESH's exact package identity, structured errors, lifecycle, telemetry and quarantine
rules. No dependency or LLM invocation was required; OpenRouter remains configured for
`openai/gpt-5.6-luna` when a later behavior test needs an LLM.

Verdict: PASS — EPIC-302 functional requirements URS-F-0305 through URS-F-0312 are verified.
Language-neutral supervised process/OCI isolation remains explicitly with EPIC-303.

## EPIC-301: Plugin discovery, resolution and dependency isolation — 2026-08-23

Spec source: Agent Hotel card `c51` and canonical `backlog/epics.json` EPIC-301 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, `semantic-version` 2.10.0 and Docker Compose:

- [x] Immutable catalog snapshots discover the embedded core distribution, configured JSON/YAML
  directories and SHA-256-verified local, file-URI or HTTP(S) registry bundles. Invalid sources and
  manifests remain visible as secret-free quarantined records.
- [x] Type references resolve through deterministic SemVer backtracking to exact package versions,
  content digests and transitive dependencies. Duplicate identities/types, incompatible platform or
  protocol ranges, missing dependencies and unsatisfiable combined constraints fail before flow
  activation.
- [x] The API flow path validates against active plugin schemas and persists
  `amesh.plugin-resolution/v1` in each immutable flow revision. PostgreSQL integration evidence proved
  that an execution created after a catalog refresh retained revision one's 1.0.0 pin while a changed
  revision selected 2.0.0.
- [x] Content-addressed installation roots, exact dependency-root maps and `PYTHONNOUSERSITE=1` launch
  plans keep plugin versions outside the control-plane import path. Trusted and isolated callback
  execution remain owned by EPIC-302/303.
- [x] Refresh creates a new catalog generation without mutating returned resolutions. Status APIs
  expose installed, active, deprecated, incompatible and quarantined versions under authorization;
  refresh and installation require instance-level plugin management.
- [x] API and CLI offline installation accept one bounded ZIP bundle plus its required SHA-256 digest,
  reject mismatches, path traversal and symlinks, and install atomically/idempotently by digest.
  Compose persists `/var/lib/amesh/plugins` in the `plugin-data` volume.
- [x] Generated manifest, catalog, registry, resolution and OpenAPI contracts match the checked-in
  files. Forty focused plugin/configuration/generated-contract/DSL tests passed.
- [x] A freshly migrated disposable database ran the 373-test collection with the two authoritative
  `c15`/`c29` tests deselected: 361 passed, ten environment/profile tests skipped, two deselected and
  no failures. The disposable database was dropped after the run.
- [x] Ruff, strict mypy for 141 source files, uv lock, clean-room policy, planning regeneration,
  backlog validation, Compose validation and diff checks passed. The rebuilt API, executor and
  scheduler are healthy; both REST and deployed CLI catalog reads returned active `amesh.core@0.2.0`.

The dependency choice used the maintained `semantic-version` SemVer 2.0 range implementation rather
than a local parser. No LLM invocation was required; OpenRouter remains configured for
`openai/gpt-5.6-luna` when a later behavior test needs an LLM.

Verdict: PASS — EPIC-301 functional requirements URS-F-0297 through URS-F-0304 are verified. Signing,
SBOM/provenance policy and supervised callback execution remain explicitly with EPIC-305 and
EPIC-302/303 respectively.

## EPIC-300: Plugin SDK and manifest contract — 2026-08-23

Spec source: Agent Hotel card `c50` and canonical `backlog/epics.json` EPIC-300 DoD.

Verified with `uv`, Python 3.13, Pydantic 2.13.4 and JSON Schema Draft 2020-12:

- [x] `amesh.plugin/v1` validates dotted identity, SemVer version, vendor, license, platform/protocol
  compatibility, unique dependencies, typed entry points and deprecation declarations. Malformed
  versions, schemas and duplicate entry points fail before use.
- [x] Task, trigger, condition, runner, storage, secret, expression and notification have typed Python
  protocols and result models. All bindings consume the same `amesh.plugin.rpc/v1` JSON request/
  response envelope, so implementation language and stdio/gRPC/HTTP transport remain outside the
  stable platform semantics.
- [x] Draft 2020-12 declarations generate configuration/output schemas, documentation metadata and
  ordered UI controls. Enum, number, boolean, list, object and write-only/password fields map to
  deterministic controls without replacing schema validation.
- [x] One local `PluginFixture` contract ran successfully for every extension type. The harness checks
  protocol/identity, capability grants and configuration before handler dispatch, preserves invocation
  fencing and normalizes deliberate or unexpected runtime failures.
- [x] Required capabilities, restricted egress destinations, workspace read/write access and secret
  scopes are explicit and deny-first. Capability tokens use secret-typed fields; configuration and
  runtime responses do not echo request secrets.
- [x] Configuration, compatibility, capability and runtime errors expose stable code, phase, JSON
  path, remediation hint, retryability and non-secret details. No raw unexpected exception message
  crosses the contract boundary.
- [x] The published compatibility policy prevents breaking plugin-contract changes in patch/minor
  releases, separates manifest/extension/protocol versions and defines normal and emergency
  deprecation/removal windows.
- [x] Twenty-two focused SDK/generated-schema/DSL tests passed. A fresh 40-migration database ran the
  364-test collection with the two authoritative `c15`/`c29` tests deselected: 355 passed, seven
  environment/profile tests skipped and no failures.
- [x] Ruff, strict mypy for 139 source files, generated manifest/request/response contracts, uv lock,
  clean-room policy, planning regeneration, backlog validation and diff-scope gates passed.

No dependency or LLM invocation was required. OpenRouter remains configured for
`openai/gpt-5.6-luna` when a later plugin behavior test actually needs an LLM.

Verdict: PASS — EPIC-300 functional requirements URS-F-0289 through URS-F-0296 are verified. The
plugin-contract slice of shared URS-NFR-MAINTAINABILITY-002 is complete; shared DSL/API/event and
upgrade surfaces remain In Progress under their owning epics.

## EPIC-222: Kubernetes task runner — 2026-08-23

Spec source: Agent Hotel card `c49` and canonical `backlog/epics.json` EPIC-222 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, Kubernetes client 35.0.0 and the existing
kind/Kubernetes v1.36.1 cluster:

- [x] Operator-owned profiles select kubeconfig context, namespace, service account, node selector,
  runtime class, workload identity and typed Job template fields by most-specific namespace/worker
  scope. Task-level placement and identity cannot escape the selected profile.
- [x] Job construction applies independent requests/limits, ephemeral-storage and `emptyDir` limits,
  runtime-default seccomp, task security policy, hardened transfer containers and deny/restricted
  egress NetworkPolicies. Restricted egress rejects non-CIDR policy values deterministically.
- [x] Workspaces cross the Kubernetes exec API through a gated init container and controlled sidecar;
  a real kind task read `input.txt`, wrote `output.txt`, returned logs and restored the output locally.
  Escaping and prohibited archive members are rejected before restoration.
- [x] API log polling retries transient failures and emits only unseen per-Pod suffixes. A deleted task
  Pod was replaced inside the same Job and attempt; a fresh runner reconnected to the original Job and
  completed the persisted attempt without incrementing it.
- [x] Scheduling, image, infrastructure, eviction and user-process paths produce distinct diagnostic
  reasons. Fenced cancellation/reconciliation delete owned NetworkPolicies, remove the cleanup
  finalizer and delete Jobs with foreground propagation; repeated cleanup tolerates absent resources.
- [x] Live profile inspection verified service-account token automount only for workload identity,
  operator node placement, profile labels/annotations, ephemeral resource limits, finalizer ownership
  and deny-egress NetworkPolicy creation. No long-lived cloud credential was injected.
- [x] Eighteen focused runner/contract tests and three live kind tests passed. A freshly migrated
  40-migration database ran the final 355-test non-deferred collection: 348 passed, seven
  environment/profile tests skipped and two authoritative tests on cards `c15`/`c29` deselected.
- [x] Ruff, strict mypy for 133 source files, uv lock, generated contracts and planning artifacts,
  clean-room policy, backlog validation, Helm/RBAC coverage, Compose configuration and diff-scope
  gates passed. Every disposable database was dropped after its run.
- [x] The rebuilt API, executor and scheduler are healthy. The live capability API advertises
  Kubernetes files/working-directory support; inherit/none/restricted networking; finalizer cleanup;
  and typed templates, profile policy, reconnect, sidecar transfer, workload identity and failure
  classification features.

No LLM invocation was required for deterministic runner behavior. The checked-in and deployed
OpenRouter model remains `openai/gpt-5.6-luna`.

Verdict: PASS — EPIC-222 functional requirements URS-F-0273 through URS-F-0280 are verified. The
Kubernetes-runner slice of shared URS-NFR-SECURITY-008 is complete; isolated third-party plugin
execution remains In Progress under its owning epics.

## EPIC-221: Docker and OCI task runner — 2026-08-23

Spec source: Agent Hotel card `c48` and canonical `backlog/epics.json` EPIC-221 DoD.

Verified with `uv`, Python 3.13, Docker SDK 7.2.0, Docker Desktop's Linux Engine, PostgreSQL 17,
MinIO and the deployed Compose control plane:

- [x] Docker tasks accept typed YAML/API configuration, resolve allowed tags to immutable repository
  digests under explicit pull policy, and reject disallowed registries or tags before container
  creation. Required argv-only signature and vulnerability verifiers fail closed.
- [x] Disposable Engine qualification applied CPU, memory, process, open-file, user, dropped-
  capability, no-new-privilege, read-only-root-filesystem and `none` network controls. Inspection
  proved the untrusted container had no Docker socket mount.
- [x] Input and output workspaces crossed the Engine archive API through an owned named volume.
  Traversal-capable archive member types were rejected before the host workspace changed.
- [x] Short-lived container stdout/stderr streamed separately after attachment-before-start. Results
  included exit status, duration, CPU, peak memory, immutable image, OOM and runtime diagnostics.
- [x] Fenced cancellation stopped a live container. Completion and repeated orphan reconciliation
  removed owned containers and volumes idempotently; scoped registry credentials did not enter the
  task environment.
- [x] Rootless and remote Engine endpoints use the standard Docker SDK connection contract. The
  development Compose profile mounts the socket only into trusted AMESH runner services, never into
  task containers.
- [x] The focused Docker suite produced six passes and one opt-in skip; its opt-in real-Engine test
  passed separately. Runner/configuration/Kubernetes compatibility tests, Ruff, strict mypy for 131
  source files, uv lock, generated contracts, clean-room, backlog, Compose and diff gates passed.
- [x] A fresh database applied all 40 migrations. The final non-deferred suite produced 336 passes,
  eight environment/profile skips and no failures. Three assertions owned by deferred cards `c15`
  and `c29` were deselected; `c29` includes the stale migration-31 observability assertion found by
  the first correctly wired full run.
- [x] The rebuilt API, executor and scheduler are healthy and advertise local, Docker and Kubernetes
  runners. Deployed execution `01a02a40-5c93-7ecb-a5e0-7693f281c8ed` completed `SUCCESS`, exposed
  separate `docker-stdout-ok`/`docker-stderr-ok`, resolved `alpine:3.21` to SHA-256, uploaded
  `result.txt` containing `docker-output-ok`, and left zero owned containers or volumes.

No LLM invocation was required for deterministic runner behavior; the only live LLM test remained
environment-gated and its configured OpenRouter default is `openai/gpt-5.6-luna`.

Verdict: PASS — EPIC-221 functional requirements URS-F-0265 through URS-F-0272 are verified. The
Docker-runner slice of shared URS-NFR-SECURITY-008 is complete; plugin and Kubernetes isolation remain
In Progress under their owning epics.

## EPIC-220: Local process task runner — 2026-08-22

Spec source: Agent Hotel card `c47` and canonical `backlog/epics.json` EPIC-220 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and the deployed Compose Linux control plane:

- [x] Argv execution never invokes a shell. Explicit `taskRunner.shell: true` accepts exactly one
  command string and exposes the native shell boundary in validated YAML.
- [x] Working directory, bounded/declared environment and standard input are applied. Linux/macOS
  workers apply numeric UID plus CPU, memory, file-size, open-file and process limits before spawn;
  Windows rejects those POSIX-only controls before process creation.
- [x] Stdout and stderr are read concurrently and delivered before process exit with one sequence,
  UTC occurrence time and `INFO`/`ERROR` mapping. Terminal task evidence retains that metadata.
- [x] Cancellation, timeout and reconciliation terminate the full POSIX process group or Windows
  process tree, wait for the declared grace period and then kill remaining descendants.
- [x] Local execution defaults enabled for single-tenant mode and disabled for multi-tenant mode;
  an explicit setting plus the matching runner policy is required to enable it for trusted tenants.
- [x] Results capture exit code, POSIX signal, duration, CPU seconds and peak process-tree memory.
  `psutil` 7.2.2 was selected for maintained Linux/macOS/Windows measurement and tree traversal.
- [x] A fresh database applied all 40 migrations. Of 339 tests, only deferred cards `c15`/`c29`
  were deselected; the remaining 337 produced 329 passes, eight environment/platform skips and no
  failures.
- [x] Ruff and strict mypy passed for 128 source files. Focused adapter/API/DSL/generated-contract,
  backlog, clean-room, REUSE, uv lock, compilation, Compose and diff gates passed.
- [x] Linux qualification enforced UID 100/open-file limit 32, captured signal 15, measured CPU/peak
  memory and proved a timed-out child did not survive. The rebuilt services are healthy at 40/40.
- [x] Deployed execution `01a02a20-5039-71a2-b8f4-282a4cd5499e` completed explicit shell/stdin work,
  returned `SHELL:FROM_STDIN`, enforced `ulimit -n` at 32 and exposed stderr and resource metrics.

No LLM invocation was required for deterministic process behavior; the configured OpenRouter
`openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-220 functional requirements URS-F-0258 through URS-F-0264 are verified.

## EPIC-209: Task runner interface and capability model — 2026-08-22

Spec source: Agent Hotel card `c46` and canonical `backlog/epics.json` EPIC-209 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and the deployed Compose control plane:

- [x] Contract 1.0 defines runner-neutral identity, command, image, environment, workspace, files,
  resources, timeout, cancellation, network, security and scoped-credential inputs.
- [x] Local and Kubernetes adapters advertise typed capabilities. Unsupported combinations are
  rejected before subprocess spawn or Kubernetes Job creation with actionable diagnostics.
- [x] Results normalize terminal state, exit code, timestamps, logs, output metadata, diagnostics
  and metrics while preserving typed adapter extensions outside the neutral core.
- [x] Cancellation and timeout escalation are bounded and observable. Idempotent reconciliation
  cleans owned orphan local processes and Kubernetes Jobs without affecting foreign work.
- [x] Task-level selection overrides namespace/worker-group policy and execution fallback; allowed
  runner lists gate dispatch. Credential scopes must be declared by the task contract.
- [x] The authorized capability API exposes contract version, constraints and escalation behavior.
  Generated OpenAPI, flow schema and resource catalog artifacts match the checked-in contract.
- [x] A fresh database applied all 40 migrations. The isolated complete suite collected 327 tests:
  321 passed, six environment/profile tests skipped and only cards `c15`/`c29` were deselected.
- [x] Ruff and strict mypy passed for 128 source files. Focused runner/API tests, generated planning,
  backlog, clean-room, REUSE 6.2.0, uv lock, compilation, Compose and diff gates passed.
- [x] The rebuilt API, executor and scheduler are healthy at 40/40. Live capability discovery
  returned both adapters, and execution `01a02a08-f238-70f1-972d-59f4a2f5cd53` completed through
  the task-selected local runner with `RUNNER_LIVE_OK:66` despite a Kubernetes execution fallback.

No LLM invocation was required for deterministic runner-contract behavior; the configured
OpenRouter `openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-209 functional requirements URS-F-0250 through URS-F-0257 are verified.

## EPIC-208: Working directories and execution files — 2026-08-22

Spec source: Agent Hotel card `c45` and canonical `backlog/epics.json` EPIC-208 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, MinIO and the deployed Compose control plane:

- [x] Every local task attempt receives a distinct opaque directory as its process `cwd`,
  `WORKING_DIR` and `OUTPUT_DIR`; successful and failed attempts remove it after collection.
- [x] Declared internal inputs resolve after expressions, stream in bounded chunks and match stored
  size/SHA-256 metadata before their atomic local rename.
- [x] Exact output paths, globs and JSON manifests stream to object storage. A multi-file failure
  deletes already uploaded members so no partial artifact batch is committed.
- [x] Static and runtime checks reject absolute paths, drives, parent traversal and symlinks. Hashed
  tenant/execution/task roots prevent caller-selected paths from crossing attempt boundaries.
- [x] `core.workingDirectory` runs children sequentially in one execution-scoped directory, collects
  parent outputs at terminalization and then cleans the shared root.
- [x] `workspaceQuotaBytes` covers all user files. `retainDiagnosticsOnFailure` uploads a bounded
  inventory/runner diagnostic before cleanup.
- [x] Migration 0040 stores logical paths and ordered source/execution/attempt/path lineage on ordinary
  artifact evidence. Authorized list/download endpoints preserve execution and tenant permissions.
- [x] A fresh database applied all 40 migrations. The isolated complete suite collected 320 tests:
  312 passed, six environment/profile tests skipped and only cards `c15`/`c29` were deselected.
- [x] Ruff and strict mypy passed for 127 source files. Generated API/DSL/planning artifacts, backlog,
  clean-room, uv lock and diff checks passed.
- [x] The rebuilt API, executor and scheduler are healthy at 40/40. Deployed execution
  `01a029e5-3d9b-75ca-a603-d664617e00a7` completed its shared parent and both children, returned
  lineage for `result.txt`, and streamed the expected transformed content from MinIO.

No LLM invocation was required for deterministic filesystem and object-transfer behavior; the
configured OpenRouter `openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-208 functional requirements URS-F-0242 through URS-F-0249 are verified.

## EPIC-207: Namespace files, key-value data and secrets — 2026-08-22

Spec source: Agent Hotel card `c44` and canonical `backlog/epics.json` EPIC-207 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, MinIO and the deployed Compose control plane:

- [x] Namespace files retain immutable versions in object storage with hierarchical inheritance,
  nearest-child override, explicit tombstones, move, version history and bounded path validation.
- [x] Namespace key-value data supports string, number, boolean, datetime, date, duration and JSON
  values, expiration, metadata, compare-and-set versions and monotonic value-free change records.
- [x] Secret bindings persist only provider references. The environment provider resolves values at
  task runtime, while revisions, APIs, audits, bundles and execution outputs do not expose plaintext.
- [x] List, read, write, delete and runtime-use permissions are independently evaluated. Mutations
  create tenant-bounded, value-free audit records.
- [x] Versioned API, CLI and React control-room surfaces cover files, values, secret references and
  checksum-protected namespace resource bundle import/export.
- [x] A fresh database applied all 39 migrations. The isolated complete suite collected 313 tests:
  305 passed, six environment/profile tests skipped and only cards `c15`/`c29` were deselected.
- [x] Ruff passed and strict mypy passed for 126 source files. Twelve frontend unit tests, eight
  applicable Playwright tests and the production build passed; eight profile-specific browser cases
  skipped. The seven pre-existing lint findings remain isolated on card `c88`.
- [x] The rebuilt API, executor and scheduler are healthy at 39/39. Live acceptance uploaded
  `config/rules.json`, read `release.channel=stable`, used a provider reference, exported a bundle
  without resolved plaintext and completed execution `01a029c2-458f-787f-a865-982c4fac3c07` with
  `authorization: [REDACTED]` and `releaseChannel: stable`.

No LLM invocation was required for deterministic shared-resource storage and resolution; the
configured OpenRouter `openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-207 functional requirements URS-F-0234 through URS-F-0241 are verified.

## EPIC-205: Inputs, outputs and variables — 2026-08-22

Spec source: Agent Hotel card `c42` and canonical `backlog/epics.json` EPIC-205 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17, MinIO and the deployed Compose control plane:

- [x] The canonical contract supports string, integer/number, boolean, datetime, duration, enum,
  array, object, file and secret inputs with required/default/display/prefill/validation metadata.
- [x] Manual, API, trigger and subflow launches validate before runnable persistence; legacy
  undeclared input maps and the existing `INT` spelling remain compatible.
- [x] Inline files move to tenant-scoped object storage under bounded payload/file limits; execution
  metadata contains the internal object reference rather than the encoded content.
- [x] Terminal outputs render against completed context, persist in migration 0037 and appear in
  execution detail. Schema-sensitive inputs/outputs and matching secret values are redacted from
  public executions, task results, evidence, event and log surfaces.
- [x] `GET /flows/{namespace}/{flowId}/data-contract` and the React run form derive from the same
  schema. Headless Chromium rendered five controls, including enum, file and password inputs.
- [x] A fresh 37-migration database passed 288 tests with six environment/profile skips and only
  the pre-existing cards `c15`/`c29` deselected. Ruff and strict mypy passed for 122 source files.
- [x] Eleven frontend tests passed with 98.57% statement and 100% line coverage; the production
  build passed. The seven pre-existing lint findings remain isolated on card `c88`.
- [x] The rebuilt API, executor and scheduler are healthy at 37/37. Live acceptance rejected a
  plaintext secret without creating an execution, staged a file, completed successfully and
  returned redacted sensitive fields. The production SPA served the generated run form.

No LLM invocation was required for deterministic schema validation; the configured OpenRouter
`openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-205 functional requirements URS-F-0219 through URS-F-0226 are verified.

## EPIC-204: Errors, finally and after-execution hooks — 2026-08-22

Spec source: Agent Hotel card `c41` and canonical `backlog/epics.json` EPIC-204 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and the deployed Compose control plane:

- [x] Local flowable and flow-owned error groups persist as ordinary durable ERROR-phase task runs;
  state, category, task identity and safe-expression selectors use handler-scoped failure context.
- [x] Nonmatching handlers are skipped at attempt zero. Selected handlers can emit ordinary
  notification, compensation and diagnostic-artifact outputs through the runnable task contract.
- [x] `finally` runs for success, primary failure and committed cancellation; `afterExecution` starts
  only after the primary terminal state is persisted and observes that terminal context.
- [x] A repository/executor restart at the after-execution boundary resumes exactly once. Primary
  failure evidence remains authoritative while a failing cleanup task is recorded separately.
- [x] Recursive lifecycle handlers are rejected. Graph responses and the control room expose each
  node's lifecycle phase, local handler owner and `handles` relationship.
- [x] A fresh database applied all 36 migrations. The complete suite collected 291 tests: 283 passed,
  six environment/profile tests skipped and the pre-existing card `c15`/`c29` assertions were
  explicitly deselected.
- [x] Ruff and strict mypy passed for 120 source files. Generated contracts/planning, backlog,
  clean-room, uv lock, REUSE 6.2.0, compilation, Compose and diff gates passed.
- [x] Frontend unit tests (10) and the production build passed. Seven pre-existing lint errors in an
  untouched component are deferred on `c88`; missing fresh-Compose mounts are deferred on `c87`.
- [x] The rebuilt local API, executor and scheduler are healthy; `/ready` reports 36/36 with
  `0036_execution_lifecycle_hooks.sql` latest.

No LLM invocation was required for deterministic lifecycle reduction; the configured OpenRouter
`openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-204 functional requirements URS-F-0211 through URS-F-0218 are verified.

## EPIC-202: Conditional branching and switch semantics — 2026-08-22

Spec source: Agent Hotel card `c40` and canonical `backlog/epics.json` EPIC-202 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and the deployed Compose control plane:

- [x] `core.if` selects ordered then, else-if or else branches and `core.switch` selects exact,
  ordered predicate or default cases; nested branch paths retain deterministic task ordering.
- [x] The selected branch, redacted rendered context, ordered evaluations and explicit `FAIL`,
  `FALSE` or `FALLBACK` policy are committed before child eligibility and reused after restart.
- [x] Non-selected branch descendants receive durable `TaskRunSkipped` events, terminal success and
  control evidence at attempt zero without creating task attempts.
- [x] Task `runIf`, trigger, retry, error and output condition contracts share the typed expression
  policy; retry decisions include attempt and normalized failure context.
- [x] Static validation rejects duplicate branch identifiers/conditions and branches following a
  provably unconditional case. ADR-033, flow/execution documentation, migration notes and the
  conditional-flowables example document the contract.
- [x] A fresh database applied all 35 migrations. The complete suite collected 288 tests: 280
  passed, six environment/profile tests skipped and the pre-existing card `c15`/`c29` assertions
  were explicitly deselected.
- [x] Ruff formatting and lint passed for 639 files, strict mypy passed for 120 source files, and
  generated contract/planning, backlog, clean-room, uv lock, REUSE 6.2.0, Compose and diff gates
  passed.
- [x] The rebuilt local API, executor, scheduler and PostgreSQL services are healthy at migration
  35/35. Deployed HTTP acceptance selected `else-if:secondary` and `predicate:high_score`, ran both
  selected children once and persisted every non-selected child at attempt zero.

No LLM invocation was required for deterministic branching or expression evaluation; the configured
OpenRouter `openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-202 functional requirements URS-F-0196 through URS-F-0202 are verified.

## EPIC-006: Flow revisions, change history and promotion — 2026-08-22

Spec source: Agent Hotel card `c39` and canonical `backlog/epics.json` EPIC-006 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and the deployed Compose control plane:

- [x] Same-revision semantic reapply is idempotent; an unused explicit forward revision is preserved;
  and changed content colliding with existing history receives the next revision without mutating old
  canonical definitions.
- [x] Authorized history exposes actor, source, commit, environment, deployment and exact versioned
  resource-catalog resolution metadata. Diff responses include a unified human diff and deterministic
  RFC 6902-compatible machine operations.
- [x] Draft, active, disabled and archived promotion is durable and audited. Non-active flows reject
  execution, and restore selects an earlier row without changing its definition, hash or history.
- [x] Executions retain their exact revision foreign key and thereby the associated resource-resolution
  set. Selected revisions and revisions referenced by executions or direct audit evidence reject
  deletion with deterministic conflict responses.
- [x] Flow revision mutations create tenant-isolated event, audit and transactional outbox evidence;
  event/outbox retention follows explicit owning-flow purge.
- [x] A fresh database applied all 34 migrations. The complete suite collected 282 tests: 274 passed,
  six environment/profile tests skipped and the pre-existing card `c15`/`c29` assertions were
  explicitly deselected.
- [x] Ruff formatting and lint passed for 637 files, strict mypy passed for 120 source files, and
  generated OpenAPI/planning artifacts, backlog, clean-room, uv lock, REUSE 6.2.0, Compose and diff
  gates passed.
- [x] The rebuilt local API, executor, scheduler and PostgreSQL services are healthy at migration
  34/34. Deployed HTTP acceptance created revisions 100/101, returned two machine diff operations,
  disabled revision 101 and restored revision 100 as active.

No LLM invocation was required for deterministic revision storage or comparison; the configured
OpenRouter `openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-006 functional requirements URS-F-0045 through URS-F-0051 are verified.

## EPIC-003: Configuration and feature flag system — 2026-08-22

Spec source: Agent Hotel card `c38` and canonical `backlog/epics.json` EPIC-003 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and the deployed Compose control plane:

- [x] Ordered YAML/JSON files, environment variables, `--config`/`--set` arguments and
  `secret://` references resolve with documented precedence, typed validation and winning-source
  provenance; unknown, unavailable and contradictory candidates fail with secret-free diagnostics.
- [x] Configuration snapshots redact all six current secret fields. Canary values are absent from
  snapshots, API responses, tenant-bounded diagnostic bundles and structured log messages.
- [x] Reload atomically accepts only declared log/telemetry/update-check settings and rejects a
  restart-required change without publishing any part of the candidate. Accepted and rejected reloads
  have durable audit contracts.
- [x] Migration 0032 persists versioned instance, tenant and namespace flags with namespace → tenant
  → instance → default resolution, optimistic version conflicts, audit evidence and runtime RLS.
- [x] Renamed settings migrate with deprecation warnings; production validation fails closed for
  development authentication, token pepper, object-store identity, plugin trust and declared public
  TLS posture. Telemetry and update checks are off by default in the offline loader test.
- [x] Seventeen focused configuration, feature-flag, migration, authentication and API tests passed.
  The complete suite collected 281 tests: 273 passed, six environment/profile tests skipped and the
  pre-existing card `c15`/`c29` assertions were explicitly deselected.
- [x] Ruff formatting and lint passed for 216 files, strict mypy passed for 119 source files, generated
  OpenAPI/planning artifacts, clean-room/backlog validation and migration ordering passed.
- [x] The rebuilt local API, executor, scheduler and PostgreSQL services are healthy at migration
  32/32. Deployed HTTP acceptance returned six redacted secret entries, two scoped flags,
  `NAMESPACE_MATCH`, a tenant-bounded diagnostic bundle and a successful no-change reload.

No LLM invocation was required for deterministic configuration or flag evaluation; the configured
OpenRouter `openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-003 functional requirements URS-F-0022 through URS-F-0028 are verified. Its
shared security, operability and privacy NFRs remain In Progress for their other owners.

## EPIC-000: Clean-room governance and parity baseline — 2026-08-22

Spec source: Agent Hotel card `c37` and canonical `backlog/epics.json` EPIC-000 DoD.

Verified with `uv`, Python 3.13 and an isolated PostgreSQL 17 database:

- [x] All 837 functional requirements have generated, schema-validated compatibility inventory
  records pinned to Kestra 1.3.30, with source identifiers, explicit dispositions and evidence.
- [x] Machine-readable provenance defines public reference sources, domain defaults and strict
  researcher/implementer/reviewer/verifier handoffs that prohibit upstream source content.
- [x] Clean-room tests reject target drift, forbidden lexical markers and reference trees inside the
  implementation repository, and detect copied synthetic token sequences without emitting content.
- [x] CI, release and packaging gates use pinned REUSE 6.2.0 license validation. The isolated release
  job additionally checks the pinned upstream commit and one-way token-shingle similarity before build.
- [x] REUSE 3.3 lint passed for all 4,074 files with zero missing, invalid, deprecated or unreadable
  licenses; workflow YAML parsing and Git Bash package-script syntax checks passed.
- [x] A fresh database applied all 31 migrations. The complete suite collected 272 tests: 264 passed,
  six environment/profile tests skipped and two pre-existing assertions on cards `c15` and `c29`
  were explicitly deselected as directed.
- [x] Ruff formatting and lint passed for 210 files, strict mypy passed for 116 source files, planning
  regeneration and backlog validation passed for 103 epics and 900 requirements, and diff whitespace
  validation passed.

No LLM invocation was required for deterministic governance validation; the configured OpenRouter
`openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-000 functional requirements URS-F-0001 through URS-F-0007 are verified.

## EPIC-110: SLA, checks and execution policy evaluation — 2026-08-22

Spec source: Agent Hotel card `c36` and canonical `backlog/epics.json` EPIC-110 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and the deployed React control room:

- [x] The versioned flow DSL validates and canonicalizes duration, start-delay, freshness,
  completion-window, output and expression checks, including WARN/FAIL severity and bounded
  notification/system-flow actions; invalid threshold, expression and action targets are rejected.
- [x] Explicit checks, selected namespace policies and matching plugin-default policies materialize
  with immutable flow revisions. Explicit IDs take precedence and policy updates write tenant audit
  evidence.
- [x] Execution start/terminal transactions and PostgreSQL-time deadline cycles persist independent
  PASS/WARN/FAIL/ERROR outcomes with reason, point, subject, timing/expression evidence and labels.
- [x] Compliance aggregation passed for tenant, namespace, flow, label and time groupings through the
  authorized API. The `/checks` control-room route renders flow aggregation, evaluation evidence,
  execution links and the reusable-policy inventory with a 10-second refresh.
- [x] NOTIFY uses the existing durable outbox with a retry-stable envelope. RUN_FLOW uses ordinary
  idempotent execution launch. Leased actions have bounded attempts; unique evaluation/action
  identities and `maxDepth` persist recursive actions as SKIPPED.
- [x] Fresh-database migration repeatability applied all 31 migrations twice with matching schema and
  seed fingerprints.
- [x] Complete backend suite: 267 collected; 260 passed, six environment/profile skips and the
  pre-existing EPIC-104 50 ms execution-deadline timing test explicitly deselected.
- [x] Ruff, formatting, strict mypy, generated flow/OpenAPI contracts, planning/backlog validation and
  diff-whitespace checks passed. Frontend production build and 10 unit tests passed; modified-file
  ESLint passed. Chromium acceptance passed six desktop tests with one tablet-only skip.
- [x] Deployed acceptance reported migration 31/31 and healthy API/executor/scheduler services.
  `demo.checks/checked-result` execution `01a028a6-2301-75f0-bbd1-8a66b6de320a` completed SUCCESS;
  start, duration, freshness, completion, output and expression checks returned six PASS results and
  `demo.checks.checked-result` compliance was 100%. `/checks` and all check APIs returned HTTP 200.

No LLM invocation was required for deterministic check evaluation; the configured OpenRouter
`openai/gpt-5.6-luna` default is unchanged.

Verdict: PASS — EPIC-110 functional requirements URS-F-0164 through URS-F-0171 are verified.

## EPIC-109: Task and execution cache — 2026-08-22

Spec source: Agent Hotel card `c34` and canonical `backlog/epics.json` EPIC-109 DoD.

Verified with `uv`, Python 3.13, PostgreSQL 17 and the deployed React control room:

- [x] Kestra-style `taskCache.enabled` and positive ISO-8601 `ttl` survive YAML validation and the
  generated public flow schema; AMESH extensions cover namespace, task/flow/namespace scope,
  revision invalidation, selected context and explicit code/plugin version.
- [x] Canonical keys change with declared inputs, flow revision, code version, tenant and resolved
  security context. Raw secret values are not stored, and PostgreSQL forced RLS fences tenant rows.
- [x] Cache entries retain redacted outputs, typed metrics and internal artifact references. A cache
  hit creates normal current-execution task/output/evidence projections with source lineage.
- [x] Durable decision evidence covers `MISS`, `HIT`, `MISS_EXPIRED`, `MISS_INVALIDATED`,
  `MISS_CONCURRENT`, `BYPASS` and `REFRESH`. The execution-detail UI renders the human-readable
  reason, key and source attempt; purge writes both cache-ledger and tenant audit records.
- [x] Leased per-key population lets a concurrent non-owner compute a safe duplicate without
  overwriting the owner's entry. Failure/deferral abandons ownership, and restart tests reuse the
  PostgreSQL entry through a fresh engine/repository instance.
- [x] Authorized API acceptance lists and purges by prefix/resource scope; the execution launch
  contract supports `USE`, `BYPASS` and `REFRESH`.
- [x] Fresh-database complete suite: 251 collected, 244 passed, six environment/profile skips and the
  pre-existing Agent Hotel `c15` 50 ms deadline timing test explicitly deselected.
- [x] Frontend: 10 unit tests passed; Chromium acceptance passed four desktop tests with one
  tablet-only skip; modified-file ESLint and production build passed.
- [x] Migration repeatability/idempotency, Ruff, formatting, strict mypy, generated contracts,
  planning/backlog validation, clean-room, Compose and uv-lock gates passed.
- [x] Deployed acceptance on migration 29 ran `demo.cache/cached-result` through
  `MISS → HIT → purge → MISS_INVALIDATED`. Hit execution
  `01a0284d-11d2-7a91-bde3-1aa2a77955c6` rendered its source execution in headless Chromium with
  no HTTP 5xx responses.

Qualification boundary: EPIC-109 has no standalone performance NFR and is not a profile-M critical
path. Shared `URS-NFR-USABILITY-002` remains In Progress until admission and policy decision catalogs
in EPIC-105 and EPIC-802 are also complete. No LLM invocation was needed for deterministic cache
testing; the configured OpenRouter Luna default is unchanged.

Verdict: PASS — EPIC-109 functional requirements URS-F-0156 through URS-F-0163 are verified.

## Deployed Dashboard and Flows recovery-state repair — 2026-08-22

Spec source: Agent Hotel card `c31` and EPIC-404 deployment follow-up.

- [x] Runtime logs reproduced `/api/v1/flows` as HTTP 500 while `/api/v1/executions?limit=200`
  remained HTTP 200.
- [x] PostgreSQL contained one affected flow among 862 rows: `updated_at` preceded `created_at`
  by 536 microseconds after a concurrent upsert used an older transaction timestamp.
- [x] The focused regression reproduced the original Pydantic validation error before the fix and
  passed after flow deserialization normalized the timestamp at the persistence boundary.
- [x] Focused Ruff and strict mypy checks passed.
- [x] `docker compose up -d --build api` rebuilt a healthy API without replacing the PostgreSQL or
  MinIO volumes.
- [x] Fresh headless Chromium login rendered Dashboard metrics, opened Flows, displayed `863 / 863
  flows`, observed HTTP 200 from flow and execution queries, and found no recovery-state heading.

Verdict: PASS — the reported deployed view is repaired and the local stack remains running.

## EPIC-603: PostgreSQL distributed work queue and notifications — 2026-08-22

Spec source: Agent Hotel card `c23` and canonical `backlog/epics.json` EPIC-603 DoD.

Verified with `uv`, Python 3.13 and PostgreSQL 17:

- [x] PostgreSQL remains the only internal durable transport: queue, transactional outbox, consumer
  inbox, expiring lease/fence and immutable dead-letter evidence converge under duplicate delivery.
- [x] Migration 0023 assigns a stable 16-bit SHA-256 virtual shard to every partition. Consumers claim
  an assigned shard while the oldest non-terminal tenant/lane/partition row prevents overtaking.
- [x] Consumers declare supported envelope schema versions. An old consumer waits at an unsupported
  head; an overlapping rolling-upgrade consumer drains both versions without mutating committed rows.
- [x] Independent lanes, replay, poison quarantine and bounded terminal queue/outbox/inbox/dead-letter
  retention pass against an ephemeral database with all 23 migrations.
- [x] Tenant diagnostics expose shard depth/skew, oldest age, expired leases, redelivery, one-minute
  throughput, p95 claim latency, PostgreSQL state and diagnostics transaction latency without payloads.
- [x] Notification waiting uses the configured SQLAlchemy pool connection, preserving reconnect and
  TLS behavior. A fresh engine publishes and completes a previously committed outbox row; a crashed
  subprocess claim is recovered and fenced in under one second with no duplicate inbox effect.
- [x] Focused migration/transport/operations/observability suite: 20 passed.
- [x] A fresh database applied all 23 migrations; the complete product suite passed 199 tests with
  four environment-gated tests skipped.
- [x] The four-consumer 60-second PostgreSQL 17 run produced and completed 3,000/3,000 messages in
  60.014 seconds: 49.988 starts/second, 0.029011-second p95, 0.111138-second maximum and zero lag.
- [x] Ruff formatting/lint, strict mypy, generated contracts/planning, backlog, clean-room, compilation,
  Compose, uv lock and diff gates pass.

Adversarial pass: duplicate identities, wrong virtual shard, unsupported schema head, stale fence,
expired lease, poison exhaustion, repeated replay, process exit, engine replacement, tenant mismatch
and lost-notification polling preserve committed work or fail deterministically.

Qualification boundary: the canonical performance NFR requires a 60-minute run, and the availability
NFR requires credentialed multi-replica/zone failure. Both shared NFRs remain In Progress for the HA
qualification stage; this epic makes no 60-minute or zone-loss claim.

Verdict: PASS — EPIC-603 functional requirements URS-F-0606 through URS-F-0613 are verified; shared
URS-NFR-AVAILABILITY-002 and URS-NFR-PERFORMANCE-004 remain In Progress.

## EPIC-602: PostgreSQL transactional backend — 2026-08-22

Spec source: Agent Hotel card `c22` and canonical `backlog/epics.json` EPIC-602 DoD.

Verified with `uv`, Python 3.13 and PostgreSQL 15, 16, 17 and 18:

- [x] A centralized async engine factory applies bounded pools, overflow and timeout limits,
  pre-ping/recycle recovery, asyncpg prepared-statement caching and explicit TLS modes.
- [x] Optional replica routing is limited to documented stale-tolerant flow and execution list reads;
  commands and consistency-sensitive reads remain on the primary.
- [x] PostgreSQL 15–18 each applied all 22 migrations and passed the migration/operations suite.
- [x] Queue claim and outbox plans use their partial covering indexes; scheduler due-work selection uses
  its due index. PostgreSQL 17 qualification measured a 0.477 ms critical-query p95, below the
  published 50 ms local threshold; versions 15, 16 and 18 measured 0.437, 0.447 and 0.469 ms.
- [x] Migration 0022 adds an auditable WAL-LSN/object-manifest backup checkpoint used by the
  documented coordinated PostgreSQL/object-store PITR procedure.
- [x] The operations repository inventories table bloat/statistics signals and partition presence;
  the qualification command emits version, TLS, schema, index, query-plan and maintenance evidence.
- [x] The complete product suite passes against a fresh 22-migration PostgreSQL 17 database;
  configuration, engine, migration, operations, observability and API routing tests are included.
- [x] Compose validation, Ruff formatting/lint, strict mypy, planning/backlog validation, generated
  contracts, clean-room, lockfile, compilation and diff gates pass.

Qualification boundary: the accepted profile is self-managed PostgreSQL 15–18. High-volume
retention/partition rollout remains In Progress under EPIC-608, and credentialed AWS RDS, Azure
Database for PostgreSQL and Google Cloud SQL qualification remains deferred to EPIC-706. No
managed-cloud support claim is made. The shared availability and encryption NFRs remain In Progress.

Verdict: PASS — EPIC-602 closes through the accepted self-managed profile and explicit product-owner
re-scope; URS-F-0598, 0599, 0600, 0601, 0604 and 0605 are verified.

## EPIC-203: Loops, foreach, while and until — 2026-08-22

Spec source: Agent Hotel card `c21` and canonical `backlog/epics.json` EPIC-203 DoD.

Verified with `uv`, Python 3.13 and PostgreSQL 17 on a fresh 21-migration database:

- [x] `core.foreach` consumes arrays, deterministically ordered maps, ranges, batches and chunked JSONL object manifests.
- [x] Child expressions receive stable iteration index, key, value and parent identity.
- [x] Per-loop concurrency is bounded and parent results remain index ordered when children finish out of order.
- [x] `core.while` checks before execution and `core.until` checks afterward, with prior successful child outputs available to the next checkpoint.
- [x] Iteration, duration and generated-task-run limits fail with durable diagnostics.
- [x] A fresh executor resumes acknowledged iteration children without duplicate attempts and reruns only interrupted work.
- [x] Continue, break, fail-fast, continue-on-error and collect-all semantics produce deterministic aggregates.
- [x] Oversized aggregates spill through the tenant-scoped object-store interface with size and SHA-256 metadata.
- [x] Execution detail reads exclude generated rows by default; graph reads reduce them to per-template state/count summaries rendered by the control room.
- [x] Focused loop/API integration suite: 8 passed. Fresh-database product suite: 190 passed and 4 environment-gated tests skipped.
- [x] The branch-coverage run measured 82.52%, above the 75% gate; its five failures came from unrelated stale data in the long-lived shared database, while the subsequent isolated-database run passed completely.
- [x] A 100,000-item streamed range enumerated in 0.333 seconds with 0.002 MiB measured peak allocation, and its summarized graph remained two nodes. Full persisted-run/browser qualification stays In Progress under shared `URS-NFR-PERFORMANCE-006` and EPIC-407.
- [x] Ruff format/lint, strict mypy, generated contracts, frontend lint/unit tests and production build pass.

Adversarial pass: invalid expansion bounds, child failure policies, interrupted attempts, out-of-order completion, duration exhaustion, object-manifest chunk boundaries and tenant-bounded graph aggregation fail closed or converge as specified.

Verdict: PASS — EPIC-203 functional requirements URS-F-0203 through URS-F-0210 are verified; shared URS-NFR-PERFORMANCE-006 remains In Progress.

## EPIC-201: Sequential, parallel and DAG flowables — 2026-08-22

Spec source: Agent Hotel card `c20` and canonical `backlog/epics.json` EPIC-201 DoD.

Verified with `uv`, Python 3.13 and PostgreSQL 17 on a fresh 21-migration database:

- [x] Nested `core.sequential`, `core.parallel` and `core.dag` definitions compile to deterministic parent/child task plans and persist every task-run identity before execution.
- [x] Sequential children run in declared order; parallel and DAG children run from explicit dependency edges and respect enclosing `maxConcurrency` limits.
- [x] Missing nested references and dependency cycles fail validation before flow revision creation.
- [x] Flowable parents aggregate declared child order, states, successful outputs and normalized errors under `FAIL_FAST`, `CONTINUE_ON_ERROR` and `COLLECT_ALL`.
- [x] Independent parallel siblings receive no sibling-private outputs; dependency-driven children receive only transitive predecessor outputs.
- [x] A fresh executor instance resumes the persisted nested DAG after one child succeeds, with no duplicate attempts.
- [x] Authorized flow and execution graph endpoints expose expanded nodes, containment/dependency edges and live task states; the control-room flow and execution pages render them.
- [x] Focused DSL, PostgreSQL restart/policy and API graph tests pass on an isolated database. Full product suite: 184 passed and 4 environment-gated tests skipped; the separately enabled OpenRouter Luna smoke reached the provider but returned no `choices` and is deferred as external, unrelated evidence per product-owner direction.
- [x] Branch-coverage suite: 183 passed, 4 skipped and the already-known instrumentation-sensitive deadline test was separately covered by the uninstrumented run; 83.26% exceeded the 75% gate.
- [x] A 1,000-child nested DAG compiled 100 times at a 1.329 ms local mean; no distributed throughput claim is made.
- [x] Ruff format/lint, strict mypy, generated contracts/planning, backlog, clean-room, compile, frontend lint/unit tests and production frontend build pass.

Adversarial pass: nested reference/cycle rejection, process restart, bounded concurrency, fail-fast short-circuiting, continuation after failure, collect-all completion, sibling-output isolation and tenant-authorized graph reads fail closed or converge as specified.

Verdict: PASS — EPIC-201 requirements URS-F-0188 through URS-F-0195 are verified.

## EPIC-200: Runnable task contract — 2026-08-22

Spec source: Agent Hotel card `c19` and canonical `backlog/epics.json` EPIC-200 DoD.

Verified with `uv`, Python 3.13 and PostgreSQL 17 on a fresh 21-migration database:

- [x] Installed task configurations are checked against registered JSON Schemas before execution creation; invalid core and plugin configuration fails deterministically.
- [x] Every attempt retains a distinct durable identity and immutable history, with duplicate completion converging on the first committed result and stale attempts rejected.
- [x] The typed handler context contains inputs, outputs, variables, labels, trigger data, declared secret scopes/files and a durable cancellation channel; context-provider output cannot add undeclared files.
- [x] Plain and structured task completions persist output plus logs, metrics, artifact references, exit metadata and encoded-size evidence.
- [x] Configuration, user-code, infrastructure and platform failures have stable categories; output, log and artifact limits fail the attempt before oversized evidence commits.
- [x] Async deferral stores only a hashed, optional-expiry resume token, emits `TaskRunDeferred`, survives a fresh executor instance and does not re-invoke the handler while waiting.
- [x] The tenant-authorized resume API rejects unauthenticated, wrong-token, expired and oversized callbacks, while a valid duplicate returns the original committed completion.
- [x] Focused unit, PostgreSQL restart and API suite: 12 passed on a fresh database.
- [x] Full uninstrumented suite: 181 passed, 4 environment-gated tests skipped. Branch-coverage suite: 180 passed, 4 skipped, 1 instrumentation-sensitive deadline test deselected and separately verified by the full suite; 82.88% coverage exceeded the 75% gate.
- [x] Ruff formatting/lint, strict mypy, lockfile, generated contracts/planning, backlog, clean-room, compile, frontend lint, 8 frontend unit tests and production frontend build pass.

Adversarial pass: invalid schemas, missing secret providers, undeclared files, each evidence limit, wrong and expired resume tokens, duplicate callbacks, restart recovery and stale attempts fail closed or converge as specified. Resume-token plaintext is not persisted.

Verdict: PASS — EPIC-200 requirements URS-F-0180 through URS-F-0187 are verified.

## EPIC-106: Backfill, replay and historical reprocessing — 2026-08-22

Spec source: Agent Hotel card `c18` and canonical `backlog/epics.json` EPIC-106 DoD.

Verified with `uv`, Python 3.13 and PostgreSQL 17 on a fresh 20-migration database:

- [x] Time ranges, partitions, selected occurrence timestamps and prior-execution IDs expand to bounded deterministic item sets.
- [x] Dry-run preview creates no state and reports execution count, task/cost impact, side-effect warnings and an occurrence-scoped idempotency-key template.
- [x] Submission pins one flow revision and applies backfill concurrency, rolling rate, execution-admission priority, labels and input overrides.
- [x] Backfills are tenant-scoped first-class resources with list/get monitoring and pause, resume, cancel and automatic-completion states.
- [x] Replay retains source lineage, inputs and labels while allowing explicit overrides; all replay sources must match the pinned flow revision.
- [x] Generated executions use deterministic idempotency keys, normal admission controls and durable item linkage; a fresh service instance resumes pending items without regenerating completed occurrences.
- [x] Aggregate monitoring reports pending, running, succeeded, failed and cancelled items, total execution duration, estimated cost units and actual task-based cost units.
- [x] Backfill state/item evidence emits transactional outbox events. Cancellation stops pending generation while already-created executions retain their ordinary lifecycle.
- [x] Focused domain, PostgreSQL and API suite: 5 passed. Full uninstrumented suite: 169 passed, 4 environment-gated tests skipped.
- [x] Branch-coverage suite passed at 82.55%, above the 75% gate, with the instrumentation-sensitive 50 ms execution-deadline case excluded and verified separately without coverage.

Adversarial pass: ambiguous selectors, naive timestamps, oversized ranges, mismatched replay sources, lifecycle conflicts, tenant authorization, rate/concurrency pressure, restart pumping and repeated idempotent pumping fail closed or converge as specified.

Verdict: PASS — EPIC-106 requirements URS-F-0132 through URS-F-0139 are verified.

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

## EPIC-108: Recovery, reconciliation and invariant repair — 2026-08-22

Spec source: `backlog/epics/epic-108-recovery-reconciliation-and-invariant-repair.md` and
`docs/operations/reconciliation.md`.

Verified with `uv`, Python 3.13.12 and PostgreSQL 17:

- [x] Migration 0024 persists tenant-isolated reconciliation runs and findings with durable
  idempotency keys, evidence, dispositions, resolution timestamps and operator runbook links.
- [x] The reconciler detects expired queue leases, orphan running tasks, stale active executions,
  missing task dispatches, unprojected execution/task events and missing schedule projections.
- [x] Dry-run does not mutate workload state. Apply uses observed versions/fences to rebuild outbox
  and scheduler projections or requeue recoverable leases; stale or ambiguous state is quarantined.
- [x] Tenant, execution, trigger, worker and time-range targeting share a global finding cap and a
  bounded repair cap. Deferred repairable findings remain detected for the next pass.
- [x] Every apply outcome is audited. Tenant-management REST endpoints provide run, list and detail
  access, while the worker automatically runs bounded per-tenant reconciliation once per minute.
- [x] Prometheus exposes run, finding, unresolved-invariant and duration metrics. The Helm worker
  values and environment example expose the reconciliation interval, cap and stale threshold.
- [x] Seven focused unit/API/PostgreSQL tests passed. Fault injection proved dry-run isolation,
  idempotent repeated apply, one-repair throttling, ambiguous quarantine and second-pass convergence.
- [x] A guarded fresh database applied all 24 migrations. Full suite: 207 passed and four
  environment-gated tests skipped. Generated OpenAPI, formatting, Ruff and strict mypy gates pass.
- [x] The live OpenRouter contract test passed using `openai/gpt-5.6-luna`.

Qualification boundary: the reference repairable faults converged in seconds, satisfying
URS-NFR-RELIABILITY-007. The shared acknowledged-command failover target remains In Progress for the
distributed HA stage; this epic does not claim zone or PostgreSQL failover qualification.

Verdict: PASS — EPIC-108 closed.

## EPIC-601: Distributed services and high availability — 2026-08-22

Spec source: `backlog/epics/epic-601-distributed-services-and-high-availability.md` and
`docs/operations/high-availability.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17 and Helm 4.0.0:

- [x] Webserver, executor, scheduler, worker gateway, indexer and maintenance are independent process
  roles and Helm Deployments; each role owns only its bounded service cycle.
- [x] Migration 0025 persists role, instance, version, failure domain, heartbeat, ownership,
  partition strategy and dependency status. Replacement increments a generation and changes the
  incarnation ID, causing old process heartbeats to fail their fence.
- [x] Instance-admin topology and drain APIs are authenticated. Drain uses an expected resource
  version, writes an audit event and keeps a draining process from taking another work cycle.
- [x] A real indexer role process registered, became ready, accepted a drain and persisted `STOPPED`.
  Stale incarnation heartbeats and stale drain requests were rejected.
- [x] Scheduler cursor, worker claim and service incarnation ownership all use PostgreSQL time,
  leases/generations and fencing; Kubernetes leader state is not authoritative.
- [x] Default and small/medium/large Helm profiles define rolling-update bounds, graceful pre-stop,
  PDBs where replicas permit, zone spread and separate liveness/readiness checks. Helm lint passed
  for all four configurations.
- [x] The operator runbook documents S/M/L replica counts, quorum dependencies, status inspection,
  version skew, drain/replacement and the dependency-certification boundary.
- [x] A guarded fresh database applied all 25 migrations. Full suite: 213 passed and four
  environment-gated tests skipped. Generated OpenAPI, Compose, formatting, Ruff and strict mypy pass.

Adversarial pass: replaced service incarnation, stale heartbeat, stale optimistic drain, active drain
heartbeat, two-zone redundancy, stopped peer, version skew and unauthorized topology/drain access all
produce deterministic outcomes without accepting stale ownership.

Qualification boundary: stale-owner fencing and reconciliation convergence are verified. The
60-second credentialed multi-zone failover, 24-hour/100,000-execution Profile M workload, measured
two-to-four replica efficiency, live upgrade rehearsal and complete dashboard/alert catalog remain In
Progress in EPIC-611/606/607. No external PostgreSQL/object-store quorum or long-run capacity claim is
made by this functional closure.

Verdict: PASS — EPIC-601 functional scope closed.

## EPIC-605: Object storage backends and lifecycle — 2026-08-22

Spec source: `backlog/epics/epic-605-object-storage-backends-and-lifecycle.md` and
`docs/operations/object-storage.md`.

Verified with `uv`, Python 3.13.12, MinIO and Helm 4.0.0:

- [x] The execution path selects S3-compatible, Azure Blob or Google Cloud Storage through one
  tenant-scoped streaming contract. Provider-fake conformance covers upload, download, metadata,
  inventory, lifecycle and tenant-prefix rejection for all three adapters.
- [x] Typed environment and Helm settings cover static credentials, ambient workload identity,
  private/custom endpoints, proxy, custom CA and customer-managed encryption identifiers. The chart
  emits only the static secret keys relevant to the selected backend.
- [x] Every upload records SHA-256 metadata and retries read-after-write visibility. Downloads spool
  in bounded memory and compare size plus SHA-256 before yielding any bytes; corruption injection
  produces `ObjectIntegrityError` and a corruption metric.
- [x] Lifecycle application blocks referenced, legally held and not-yet-expired objects. An accepted
  deletion returns an explicit deletion marker; the reference MinIO bucket is versioned.
- [x] Backend migration streams in deterministic key order, verifies both sides and atomically saves
  an object/byte/key checkpoint after every copy. An interruption after the first object resumed
  without recopying it. The `amesh storage validate` and `storage migrate` CLI commands expose both
  operations.
- [x] Prometheus exposes bounded backend/operation request, latency, transfer-byte, inventory and
  corruption signals without tenant or object labels.
- [x] A 10 GiB logical upload completed below the 256 MiB process-memory target. A real MinIO run
  passed multipart upload, verified download, lifecycle blocking, inventory validation and versioned
  delete.
- [x] A guarded fresh database applied all 25 migrations. Full suite: 224 passed and four
  environment-gated tests skipped. Ruff formatting/lint, strict mypy, uv lock, Compose, all four Helm
  profile lints, planning regeneration/validation and diff checks pass.

Qualification boundary: managed Azure/GCP accounts, private network policy and provider outage drills
remain release-environment certification under EPIC-706. EPIC-609 consumes the verified inventory and
version-aware adapter contract next; URS-F-0629 remains In Progress until the coordinated restore
exercise passes. The checked-in OpenRouter default remains `openai/gpt-5.6-luna`; this storage change
does not invoke an LLM.

Verdict: PASS — EPIC-605 portable storage scope closed.

## EPIC-609: Backup, restore and disaster recovery — 2026-08-22

Spec source: `backlog/epics/epic-609-backup-restore-and-disaster-recovery.md` and
`docs/operations/disaster-recovery.md`.

Verified with `uv`, PostgreSQL 17.11, the production runtime image, versioned MinIO and Helm 4.0.0:

- [x] Migration 0026 persists recovery-exercise state, RPO/RTO, native client/schema versions,
  object totals, reconciliation/projection/readiness reports and unresolved gaps. It also provides a
  bounded rebuild function for `amesh_search_*` and `amesh_analytics_*` materialized views.
- [x] Backup creation held an exported repeatable-read PostgreSQL snapshot while inventorying exact
  object versions, produced a custom-format dump, uploaded a canonical SHA-256 manifest, and recorded
  the snapshot WAL LSN only after durable object writes completed.
- [x] The runtime image's PostgreSQL 17 tools performed a real `pg_restore` into a guarded disposable
  database. Restored service and worker identities were stopped, queue/task/generic leases expired,
  scheduler ownership fenced, projections rebuilt and tenant reconciliation executed before readiness.
- [x] S3, Azure and GCS provider fakes read explicit object versions. The end-to-end recovery test
  overwrote an object after backup and proved verification still consumed the manifest's earlier
  version and checksum.
- [x] Tenant transfer exports policy, active flows and exact object versions in a canonical
  checksum-protected bundle; import creates a new tenant and streams verified flows/objects. A mutated
  bundle was rejected before import.
- [x] `amesh recovery create`, `verify-latest` and `exercise`, plus tenant-transfer export/import, are
  available through the uv-managed CLI. The opt-in Helm CronJob runs the same exercise path with
  overlap forbidden and durable failed-gap evidence.
- [x] A clean reference exercise applied all 26 migrations and passed with 0.553 seconds RPO, 1.017
  seconds RTO, one of one objects verified, zero reconciliation gaps and zero restored ownership.
  A separate restored database containing pre-existing invariant violations correctly recorded a
  `FAILED` exercise and its 49 unresolved findings instead of producing a false pass.
- [x] The real isolated restore integration test passed inside the production image. Focused storage,
  tenant-transfer, migration and recovery tests passed; frontend 8/8 tests and build passed. Docker
  image build, Helm lint/template, Compose config, Ruff formatting/lint, strict mypy, uv lock and
  planning regeneration/validation passed.

Full-suite audit on a clean 26-migration database: 224 passed and six environment gates skipped; one
pre-existing timing-sensitive executor deadline test failed with inconsistent timeout outcomes both in
the suite and alone. No recovery, storage, tenancy, migration, Helm or frontend test failed, and the
executor path was not changed by EPIC-609.

Qualification boundary: the measured values qualify the small functional PostgreSQL 17 + MinIO
reference exercise against the v1 RPO <= 48 hours and RTO <= 8 hours gate. They are not scale,
multi-zone or regional-failover evidence. The post-GA 4-hour profile still needs an appropriately
sized WAL archive, schedule and qualification environment. The checked-in OpenRouter default remains
`openai/gpt-5.6-luna`; recovery does not invoke an LLM.

Verdict: PASS — EPIC-609 closed.

## EPIC-403: Authentication session and credential entry points — 2026-08-22

Spec source: `backlog/epics/epic-403-authentication-session-and-credential-entry-points.md`
and `docs/operations/authentication.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17, Chromium, React/Vite and Helm 4.0.0:

- [x] One guarded CLI operation creates the first local user, Argon2id credential and instance-admin
  binding without a default password; a repeated bootstrap is rejected and password material is
  absent from stdout, stderr and durable audit evidence.
- [x] Multiple local users can receive separately administered passwords and log into the graphical
  frontend. Their existing tenant/namespace role bindings are enforced by the same server-side RBAC
  and PostgreSQL RLS paths used by durable bearer credentials.
- [x] Browser sessions store only keyed opaque-token and CSRF digests in PostgreSQL. Production
  cookies use `__Host-` names, Secure, HttpOnly and SameSite=Lax where applicable; unsafe cookie
  requests require the matching CSRF header.
- [x] Rotation overlap, idle expiry, absolute expiry, logout, administrator/session-wide revocation
  and password rotation were exercised. Principal credential epochs fence previously issued sessions.
- [x] Unknown identities and invalid secrets return the same public failure; account lockout and
  source-window rate limits are deterministic, and bounded Prometheus outcomes expose no identity or
  secret labels.
- [x] The authentication service consumes a provider-neutral adapter protocol and delegates a fake
  OIDC assertion through it. Federated-only policy removes local login while retaining registered
  federated providers. Concrete OIDC/SAML/LDAP/SCIM adapters remain EPIC-502.
- [x] A live AMESH server backed by an isolated 27-migration PostgreSQL database served the compiled
  React application. Headless Chromium signed in as the bootstrapped administrator, reached the
  Dashboard and observed the expected HttpOnly session and readable CSRF cookie policy.
- [x] Four focused API/CLI tests passed. Frontend ESLint, ten unit tests, the production build and five
  applicable Playwright shell cases passed. All non-deferred backend tests passed on a clean database;
  card `c15` preserves the unrelated EPIC-104 timing assertion and card `c29` preserves the unrelated
  order-dependent metric assertion.
- [x] Ruff formatting/lint, strict mypy, `uv lock --check`, generated OpenAPI/planning artifacts,
  backlog validation, Compose config, Helm production/development lint and the production Docker
  image all passed.

Qualification boundary: this closes local multi-user login and the provider-neutral boundary. It does
not claim concrete enterprise federation, which remains EPIC-502, or broader production qualification
beyond the already published EPIC-601/609 profiles.

Verdict: PASS — EPIC-403 closed.

## Local Docker deployment handoff — 2026-08-22

Spec source: board card `c30`.

- [x] `docker compose up -d --build api` built and started the current AMESH API/frontend image
  while preserving the named PostgreSQL and MinIO volumes.
- [x] `/ready` returned HTTP 200 with 27 applied and expected migrations; PostgreSQL retained the
  bootstrapped `admin` user through container recreation.
- [x] The installed runtime package resolved `amesh/web`, and `/` served the compiled React HTML.
- [x] A real local-account API session returned the administrator identity, an HttpOnly session
  cookie and a CSRF cookie; CSRF-authenticated logout returned 204.
- [x] Headless Chromium signed in through the rendered form, reached Dashboard, checked the cookie
  policy and logged out.

Adversarial pass: the initial image was healthy but returned 404 for `/`; container inspection showed
that the built assets existed under `/app/src` but were absent from the installed wheel. Declaring the
HTML and asset directories as `amesh` package data fixed the installed runtime path.

Verdict: PASS — local stack left running for user testing.

## EPIC-400: Versioned REST API and OpenAPI contract — 2026-08-22

Spec source: board card `c7` DoD and
`backlog/epics/epic-400-versioned-rest-api-and-openapi-contract.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17, FastAPI 0.141.1, Docker Compose and
`oasdiff`:

- [x] Authenticated PostgreSQL integration covered synchronous compatibility, `202` asynchronous
  launch, durable initial `RUNNING`, polling to `SUCCESS`, header/body idempotency replay and conflict,
  bounded mixed-result bulk launch, collection filtering/sorting/selection and streamed NDJSON logs.
- [x] Problem-details unit and authorization integration checks covered media type, stable fields,
  invalid cursors, missing bulk items and indistinguishable missing/unauthorized tenant responses.
- [x] Generated OpenAPI passed the repository contract test. `oasdiff breaking --fail-on ERR` against
  the prior checked-in contract reported no errors; two warnings document pre-existing runtime
  bounds that are now represented on the execution `limit` parameter.
- [x] The full suite passed on an isolated database with all 27 migrations: 233 passed and 6
  environment-gated tests skipped. The disposable database was then force-dropped and its absence
  verified. Focused service-role/configuration tests passed after the Compose recovery wiring.
- [x] The rebuilt live stack launched 20 local shell executions through `Prefer: respond-async`:
  p95 response 87.1 ms, maximum 96.0 ms, all 20 completed `SUCCESS`, and logs streamed successfully.
- [x] A forced zero-grace API container restart interrupted execution
  `01a027f9-4d0f-7edf-8048-84081140ae8c`; the independent Compose executor logged recovery and the
  durable execution completed `SUCCESS` with its expected output.

Adversarial pass: malformed cursors return 400, conflicting idempotency representations return 400,
bulk failure does not roll back successful items, tenant concealment does not vary its problem code,
and an API process loss after acceptance is recovered by the independent executor.

Qualification boundary: ADR-025 limits EPIC-400 to authoritative v0.2 resources. Namespace files,
key-values, secret providers and installable plugins remain EPIC-207/506/300/301. Ten-million-record
filter/index qualification remains EPIC-409; this epic measured the launch critical path only.

Verdict: PASS — EPIC-400 closed.

## EPIC-010: Internal object storage and artifact addressing — 2026-08-22

Spec source: board card `c32` and
`backlog/epics/epic-010-internal-object-storage-and-artifact-addressing.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17 and versioned MinIO:

- [x] S3, Azure Blob and Google Cloud Storage adapters implement one tenant-scoped contract for
  multipart/resumable upload, streaming full download, native ranged download, provider metadata,
  lifecycle, inventory and deletion. Local development uses the same S3 path against MinIO.
- [x] Object metadata persists size, content type, SHA-256, encryption key, provider version,
  creation time, creator, lineage, retention and legal-hold state. Checksum-verified migration
  preserves creator and lineage.
- [x] Opaque provider URIs are rejected before provider access when the scheme, container, tenant
  prefix or normalized path does not match the authorized tenant.
- [x] `collect_unreferenced` runs in bounded passes, consults the caller's authoritative reference
  checker and blocks objects within `OBJECT_STORAGE_GC_SAFETY_WINDOW_SECONDS`, as well as referenced,
  retained and legally held objects.
- [x] Corruption injection is rejected before a full download yields bytes. The logical 10 GiB upload
  stayed below the 256 MiB memory target, and the architecture dependency test kept storage SDKs
  outside the core domain boundary.
- [x] Fourteen focused storage/configuration tests passed with the environment-gated MinIO case
  skipped; the same MinIO case then passed live against `http://localhost:9000`, including multipart
  upload, persisted provenance, native range retrieval, inventory, lifecycle and versioned deletion.
- [x] The full suite passed on a clean database with all 27 migrations: 237 passed and five
  environment-gated tests skipped. The disposable database was force-dropped and its absence
  verified.
- [x] Ruff formatting/lint, strict mypy, `uv lock --check`, generated contracts/planning artifacts,
  backlog validation, clean-room policy, Compose configuration and diff hygiene passed.

Adversarial pass: cross-tenant URIs, invalid and out-of-object ranges, delayed write visibility,
checksum corruption, referenced objects, retention, legal holds and young unreferenced objects all
produce deterministic non-consumption or non-deletion outcomes.

Qualification boundary: managed Azure/GCP certification and provider-outage drills remain EPIC-706.
Shared maintainability and portability NFRs remain In Progress for their other owning epics. The
checked-in OpenRouter default remains `openai/gpt-5.6-luna`; object storage does not invoke an LLM.

Verdict: PASS — EPIC-010 closed.

## EPIC-206: Labels, metadata and plugin defaults — 2026-08-22

Spec source: board card `c43` and
`backlog/epics/epic-206-labels-metadata-and-plugin-defaults.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17, FastAPI 0.141.1, React/Vite and
Docker Compose:

- [x] User and protected system labels persist on flows, executions, task runs, assets and backfills.
  Spoofed `amesh.` and `system.` labels fail before persistence; execution/task labels inherit the
  flow and invocation metadata without changing cache identity.
- [x] Parent and child namespace metadata resolves exact plugin-type values with recursive merge.
  Non-forced values use parent, child, flow, task precedence; forced values give the broader policy
  priority. Unit evidence checks nested merges, normalization, exact-type mismatch and origins.
- [x] Effective task values and per-property source/namespace/forced provenance are pinned in the
  immutable flow revision and exposed by authorized metadata APIs and the flow detail page. Existing
  executions do not re-resolve changed namespace policy.
- [x] Namespace policy requires, denies and normalizes selected labels/defaults. Optimistic version
  conflicts return 412, policy violations are deterministic, and the new management API passes the
  viewer-denial authorization matrix.
- [x] Migration 0038 applies tenant RLS to namespace metadata and adds five JSONB GIN label indexes.
  Dotted collection filtering selected `metadata.labels.team=platform` in API integration evidence.
- [x] A clean 38-migration database ran the full 300-test collection: 292 passed, six environment/
  profile tests skipped and the known cards `c15`/`c29` were deselected. The first run found one
  directly caused cache-key regression; the minimal user-label-only cache context fix passed both
  restart and concurrent-population scenarios before the complete rerun passed.
- [x] Ruff, strict mypy for 123 source files, generated contracts, frontend 11-test coverage and the
  production frontend build passed. The seven unrelated lint failures remain recorded on `c88`.
- [x] The rebuilt Compose stack reports 38/38 migrations. Live namespace configuration and example
  flow application exposed effective defaults/origins; execution
  `01a0299b-bf76-7893-8366-f2920cc5b614` completed `SUCCESS` with protected flow/execution/task labels.

No package or LLM call was required; OpenRouter model configuration remains unchanged.

Verdict: PASS — EPIC-206 closed.

## EPIC-111: Logs, metrics, outputs and artifact events — 2026-08-22

Spec source: board card `c33` and
`backlog/epics/epic-111-logs-metrics-outputs-and-artifact-events.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17, FastAPI 0.141.1, React/Vite and
Docker Compose:

- [x] Task completion projects structured task logs and shell stdout/stderr, counters/gauges/timers/
  custom metrics, bounded output documents and internal-storage artifact references into separate
  tenant-isolated tables. Event/ingest time, attempt, worker, trace, logger, severity and source stream
  fields survive the projection.
- [x] Execution/task transitions and task evidence append to one monotonic cursor stream. Authorized
  JSON paging and reconnectable NDJSON return only events after the supplied opaque cursor; the React
  execution detail page polls the API and renders a filterable live evidence timeline.
- [x] Task-attempt evidence remains the immutable restart source. Projection occurs only after a fenced
  completion wins, and a duplicate deferred completion created exactly one log, metric, output and
  artifact projection.
- [x] Declared sensitive keys, known sensitive field names and resolved secret values are redacted
  before persistence. A seeded `secret-value` canary was absent from attempt result/evidence and all
  evidence event payloads; the optional exporter applied a second redaction pass.
- [x] Export policy enforces a retention cutoff, deterministic sampling and batches of at most 1,000.
  A forced sink outage returned without raising and retained the prior cursor for retry; execution
  never calls the optional sink.
- [x] A 50,000-record local Docker PostgreSQL burst persisted 50,000 log rows and 50,000 matching cursor
  events in 4.084 seconds (12,241.8 records/second) using the set-based projection. No loss occurred.
  This is a bounded single-node measurement, not qualification of the provisional 50,000 records/
  second standard-cluster target, which remains In Progress with EPIC-607.
- [x] The clean 28-migration suite passed with the known EPIC-104 50 ms deadline assertion deselected:
  245 tests collected, six environment-gated tests skipped, and one board-tracked test deselected.
  Running the complete suite reproduced only card `c15`: the task expired before dispatch and was
  `CANCELLED` rather than the assertion's expected `FAILED`. It was not changed under the scope lock.
- [x] Ruff formatting/lint, strict mypy, `uv lock --check`, frontend ten-test coverage run, production
  frontend build, generated OpenAPI, migration repeatability, backlog validation and Compose config
  passed. Both 28-migration disposable databases were force-dropped after the verification runs.
- [x] The rebuilt live stack reported 28/28 migrations ready. Flow `demo.evidence/live_evidence`
  completed both tasks successfully; execution `01a0282f-4fd8-79fc-b5bb-c94e386ea2bd` exposed 14
  events spanning `STATE`, `LOG` and `OUTPUT`, including the durable core log and shell stdout.

Qualification boundary: the single-node functional evidence contract is complete. The shared
standard-cluster ingestion rate and broader telemetry shipping/collector qualification remain
EPIC-607; shared cross-product secret non-disclosure remains In Progress for EPIC-205/506/607.

Verdict: PASS — EPIC-111 closed.

## EPIC-103: Trigger runtime and occurrence lifecycle — 2026-08-22

Spec source: board card `c35` and
`backlog/epics/epic-103-trigger-runtime-and-occurrence-lifecycle.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17, FastAPI 0.141.1, React/Vite and
Docker Compose:

- [x] Migration 0030 persists tenant-isolated trigger revision state, checkpoints, deduplicated
  occurrences and immutable lifecycle events. Revision replacement activates/deactivates runtime
  instances transactionally; leased claims reject stale owners.
- [x] Connector-provided and derived keys converge repeated source delivery on one occurrence.
  Backpressure, pause/resume, retry delay, attempt exhaustion, dead-letter and immutable manual replay
  passed PostgreSQL and authorized API tests.
- [x] Polling and realtime adapter tests proved that checkpoints/occurrences commit before the source
  acknowledgement hook runs. Flow completion inserted a `core.flow` occurrence in the source terminal
  transaction and the generic scheduler worker launched the dependent flow without source polling.
- [x] The control room exposes a searchable Triggers health/occurrence view with access-aware
  pause/resume and replay actions. Ten frontend unit tests, the production build and six applicable
  Chromium E2E checks passed; six duplicate tablet cases were intentionally skipped by the suite.
- [x] The clean 30-migration backend suite passed with 249 tests passing, six environment-gated tests
  skipped and the known board-tracked EPIC-104 timing assertion deselected. Deployment then exposed
  two direct scheduler blockers: expanded trigger defaults changed the rehydrated hash of older flow
  revisions, and one flow-specific scheduling failure terminated the service. Persisted canonical
  provenance and per-flow failure isolation were added; all nine scheduler/trigger integration tests
  and all three worker unit tests passed afterward.
- [x] Ruff formatting/lint, strict mypy, `uv lock --check`, generated OpenAPI/schema/planning
  artifacts, backlog validation, example-flow validation and Compose configuration passed.
- [x] The rebuilt live stack reported 30/30 migrations with API, executor and scheduler healthy.
  Webhook event `epic103-live-20260822155827` returned source execution
  `01a0287a-7151-709d-a2d8-49ba140fe458` as `SUCCESS`; repeating the event returned the same execution.
  Its terminal transaction produced occurrence `4f77e470-3b5e-4825-aea7-03284f35c2ee`, which launched
  dependent execution `01a0287a-7c0b-7704-8224-b11e1768c991` as `SUCCESS`. The live trigger API exposed
  both definitions and `GET /triggers` served the production SPA with HTTP 200.

Qualification boundary: EPIC-103's single-node functional contract is complete. Shared product-wide
duplicate-injection qualification remains In Progress under URS-NFR-RELIABILITY-002; connector-pack
emulators and fault injection remain EPIC-304.

Verdict: PASS — EPIC-103 closed.

## EPIC-304: Trigger, condition and notification extension contracts — 2026-08-23

Spec source: board card `c54` and
`backlog/epics/epic-304-trigger-condition-and-notification-extension-contracts.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17 and Docker Compose:

- [x] Polling adapters normalized source and partition identities, converged duplicate deliveries,
  persisted checkpoints before source acknowledgement and exposed only manifest-declared secrets.
- [x] Realtime adapters enforced bounded in-flight delivery, accepted occurrences before source
  acknowledgement, closed streams after bounded consumption and closed faulted connections.
- [x] Conditions returned boolean decisions, reasons and structured evidence. Invalid configuration
  returned stable local schema errors without opening the connector.
- [x] Notifications received typed execution/task lifecycle events and delivery policy; retry,
  timeout, cancellation and secret-scope behavior used the shared extension call contract.
- [x] Polling, realtime, condition and notification emulators injected duplicates, retryable failures,
  delays and disconnects. Focused contract/runtime/generated-schema coverage passed: 23 tests passed
  and one environment-gated plugin test skipped.
- [x] The clean 40-migration backend suite passed: 392 tests collected, 380 passed, 10
  environment-gated tests skipped and the two board-tracked EPIC-104/observability tests deselected.
  The exact disposable PostgreSQL database was force-dropped after the run.
- [x] Ruff, strict mypy and generated contract checks passed. The normative
  `amesh.plugin.extension/v1` schema and connector-development guide were generated and linked.

Qualification boundary: the language-neutral schema and Python reference adapters/emulators are
complete. Connector-specific external-service certification belongs to the integration-pack epics.

Verdict: PASS — EPIC-304 closed.

## EPIC-305: Plugin registry, signing, SBOM and marketplace metadata — 2026-08-23

Spec source: board card `c55` and
`backlog/epics/epic-305-plugin-registry-signing-sbom-and-marketplace-metadata.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17, React/Vite and Docker Compose:

- [x] The self-hosted registry rejected a second digest for an existing plugin name/version and
  retained content-addressed artifact and evidence blobs after a signed yank decision.
- [x] Publication required license/source/documentation/platform/SDK/changelog metadata plus signed
  SBOM, vulnerability and provenance attachments. Index, release metadata, artifact and attachment
  tampering failed verification before catalog installation or offline import.
- [x] Registry client policy allowed only configured HTTP(S) origins, rewrote configured mirrors,
  carried proxy settings and rejected network access in offline mode. Signed offline export/import
  reproduced the release without a proprietary service.
- [x] Authorized publish, list, release, download, yank, offline-export and offline-import API routes
  passed. Marketplace responses and the responsive Plugins view expose downloads, maintenance,
  certification and security status with an explicit non-guarantee disclaimer.
- [x] Focused registry/discovery/configuration/generated-contract coverage passed: 22 tests passed and
  one PostgreSQL-gated discovery test skipped. Twelve frontend unit tests and the production Vite
  build passed.
- [x] The clean 40-migration backend suite passed: 395 tests collected, 383 passed, 10
  environment-gated tests skipped and the two board-tracked EPIC-104/observability tests deselected.
  The exact disposable PostgreSQL database was force-dropped after the run.
- [x] Ruff, strict mypy over 151 source files, generated OpenAPI/schema, Compose and diff checks
  passed. Frontend lint still reports the board-deferred evidence timeline findings plus two
  test-typing findings; no production build or test is blocked.
- [x] The rebuilt API, executor and scheduler were healthy. The non-root image now owns the persisted
  plugin directory; the live signed index served a `compose-local` signature and one immutable demo
  release with all three required attachments, while `/plugins` returned the production SPA.

Qualification boundary: the functional self-hosted HMAC-SHA-256 reference profile is complete.
Official public-key release-pipeline provenance/SBOM/signature qualification remains
URS-NFR-SECURITY-007 under EPIC-001/612. Full air-gapped core/governance qualification remains
URS-NFR-PORTABILITY-001 under EPIC-804.

Verdict: PASS — EPIC-305 functional scope closed.

## EPIC-306: Core utility plugin pack — 2026-08-23

Spec source: board card `c56` and
`backlog/epics/epic-306-core-utility-plugin-pack.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17 and Docker Compose:

- [x] Protected HTTP fixtures covered bearer authentication, bounded JSON pagination, response-byte
  rejection and private-address SSRF denial. Download wrote only to the assigned workspace.
- [x] Workspace fixtures covered ZIP compression/extraction, SHA checksums, copy, move and delete;
  traversal and compression-ratio bomb inputs failed deterministically without escaping the workspace.
- [x] JSON, YAML, CSV, XML and text transformations produced deterministic native values. XML document
  type/entity declarations and oversized payloads are rejected before transformation.
- [x] Sleep, fail, log, return, debug and assertion tasks are present in the versioned catalog. Debug
  exposes selected context and secret-scope names without secret values; sleep honors cancellation.
- [x] Manual, webhook, cron/interval and flow triggers are present in the core distribution and retain
  their existing authorized execution and durable occurrence implementations. Injected SMTP and HTTP
  fixtures verified email and generic-webhook notification primitives without external services.
- [x] A fresh 40-migration PostgreSQL execution rendered utility dependencies and persisted outputs.
  The full isolated collection contained 407 tests: 395 passed, ten environment/profile tests skipped
  and the two authoritative `c15`/`c29` tests were explicitly deselected. The disposable databases
  were force-dropped after their runs.
- [x] Ruff, strict mypy over 155 source files, generated resource/OpenAPI/schema contracts, example
  validation, configuration tests and diff checks passed.
- [x] The rebuilt API, executor and scheduler were healthy. Live flow `examples.plugins.core_utilities`
  revision 1 completed execution `01a02b05-4373-7c55-8801-dc553791df17` as `SUCCESS`; all five task
  runs persisted, normalization and return produced `AMESH`, the assertion was true and the frontend
  execution deep link returned HTTP 200.

Verdict: PASS — EPIC-306 closed.

## EPIC-307: Multi-language script plugin pack — 2026-08-23

Spec source: board card `c57` and
`backlog/epics/epic-307-multi-language-script-plugin-pack.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17 and Docker Compose:

- [x] First-party shell, Python, Node.js, Java, R and PowerShell task types compiled into the
  existing local, Docker or Kubernetes runner contract. Per-language contract tests confirmed
  script text, argv and environment values remain separate through dispatch.
- [x] Inline, namespace-file, immutable repository-artifact and packaged-workspace sources passed
  catalog validation and adapter tests. Six checked-in sample flows validate against the generated
  resource catalog.
- [x] Runtime dependency installation failed closed until organization policy enabled it, every
  dependency carried a name/version/SHA-256 record, and the task requested allowlisted restricted
  egress. Image defaults and organization-approved overrides accepted only immutable SHA-256
  references.
- [x] Ordered stdout/stderr logs, duration/CPU/peak-memory metrics, output-file/manifests and helper
  paths use the shared runner/workspace contract. Each task output records language, interpreter,
  image digest, source origin and package metadata.
- [x] The fresh 40-migration backend collection contained 420 tests. With the c15 timing-sensitive
  execution controls, c29 order-sensitive observability check and c89 full-suite performance timing
  check explicitly deselected, 416 tests ran: 406 passed and ten environment/profile tests skipped.
  The disposable PostgreSQL database was force-dropped. The c89 check separately passed three
  consecutive isolated runs after measuring 1.061 seconds once under full-suite load.
- [x] Ruff, strict mypy over 157 source files, generated resource/OpenAPI/schema contracts,
  configuration coverage and all six example validations passed.
- [x] The rebuilt API, executor and scheduler were healthy. Live flow
  `examples.plugins.script_python` revision 1 completed execution
  `01a02b1c-7989-703a-8cc7-beb2dedebe4e` as `SUCCESS`; stdout was `python:amesh`, and the persisted
  result included the runner metrics and immutable runtime metadata.

Verdict: PASS — EPIC-307 closed.

## EPIC-313: Plugin developer portal and certification suite — 2026-08-23

Spec source: board card `c58` and
`backlog/epics/epic-313-plugin-developer-portal-and-certification-suite.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17 and Docker Compose:

- [x] `amesh plugins scaffold` generated a versioned Python starter, `uv` project, manifest,
  license placeholder, supported-release matrix and five certification fixture/evidence pairs.
  The local sandbox accepted a valid manifest-driven configuration and returned deterministic
  diagnostics for an invalid one.
- [x] One `amesh plugins certify` invocation reported manifest, schema, contract, security,
  license and compatibility outcomes. Pending fixture evidence produced Community status; passing
  evidence produced Verified status; immutable source/public CI evidence produced Certified status.
- [x] Retry, cancellation, large-file, secret-redaction and worker-restart reference fixtures are
  published in the starter and portable example catalog. Missing or non-passing evidence failed the
  contract category deterministically.
- [x] Metadata generated human-readable Markdown and sample YAML. The checked-in certification
  JSON Schema matched the runtime model.
- [x] Release matrices accepted compatible `0.2.x` versions and rejected an incompatible `0.3.0`.
  Repeated certification of identical public-CI inputs produced the same SHA-256 input digest.
- [x] The fresh 40-migration backend collection contained 426 tests. With the four authoritative
  c15/c29/c89 timing or ordering checks explicitly deselected, 422 tests ran: 412 passed and ten
  environment/profile tests skipped. The disposable PostgreSQL database was force-dropped.
- [x] Ruff, strict mypy over 158 source files, generated contract parity, 21 focused backend checks,
  all 12 frontend tests and the production frontend build passed. The unrelated pre-existing
  frontend lint findings remain deferred on board card `c88`.
- [x] A live `uv` smoke generated `example.live`, produced its documentation, accepted its starter
  sample in the local sandbox and emitted a six-check Community report with a deterministic digest.
  Rebuilt API, executor and scheduler containers reached healthy state, and the frontend root
  returned HTTP 200.

Verdict: PASS — EPIC-313 closed.

## EPIC-401: Realtime API, webhooks and event subscriptions — 2026-08-23

Spec source: board card `c59` and
`backlog/epics/epic-401-realtime-api-webhooks-and-event-subscriptions.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17 and Docker Compose:

- [x] Tenant-scoped execution evidence and audit events project into a durable ordered cursor.
  Authorized pages and SSE filter by namespace, flow, execution, event type and severity; reconnects
  accept opaque cursors or `Last-Event-ID`.
- [x] SSE clients receive bounded batches, a documented finite disconnect policy, heartbeats and an
  explicit gap event when the requested cursor predates retained data.
- [x] Outbound webhook subscriptions support private-destination denial, HMAC-SHA-256 signatures,
  derived-secret rotation, endpoint tests, bounded retries, stable delivery identifiers, selected
  replay and immutable delivery-attempt history.
- [x] Stream and webhook payloads redact structural secrets and values identified by flow input or
  output sensitivity metadata. Audit events require the audit permission in addition to stream
  access.
- [x] Webhook preparation and delivery run only in the optional indexer role. A simulated 503
  destination produced a durable retry while a new execution was still created, then the same
  delivery completed successfully when the destination recovered.
- [x] The focused fresh-database suite passed 18 checks. The full fresh 41-migration regression
  suite passed with the four authoritative c15/c29/c89 timing or ordering checks explicitly
  deselected and the disposable PostgreSQL databases force-dropped.
- [x] Ruff, strict mypy, generated OpenAPI/schema contracts, migration ordering, least-privilege
  runtime-role behavior, tenant lifecycle cleanup and diff checks passed.

Qualification boundary: EPIC-401 completes the outbound-webhook outage slice. The shared
`URS-NFR-RELIABILITY-005` remains Proposed until EPIC-409, EPIC-604 and EPIC-607 qualify the search,
analytics and telemetry outage slices.

Verdict: PASS — EPIC-401 closed.

## EPIC-402: CLI and generated client SDKs — 2026-08-23

Spec source: board card `c60` and
`backlog/epics/epic-402-cli-and-generated-client-sdks.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17 and Docker Compose:

- [x] The CLI preserves the existing flow, execution, namespace, file and plugin commands and adds
  named configuration profiles, authentication token lifecycle, declarative flow operations and
  administration commands. Human, JSON and quiet modes return stable documented exit codes.
- [x] Credentials are delegated to the operating-system keyring and never written to profile JSON.
  `AMESH_SERVICE_ACCOUNT_TOKEN` provides a non-interactive CI path with deterministic precedence.
- [x] Declarative flow apply and diff accept files or standard input; export returns canonical stored
  revisions; flow-revision and tenant deletion present impact, scope and recovery information and
  require an explicit `--force`.
- [x] OpenAPI Generator 7.24.0, pinned by container digest, produced typed Python, TypeScript Fetch,
  Java and Go clients for API version 0.2.0. All four expose the flow-document operation, compatibility
  metadata and pagination helpers; Python compiled, TypeScript typechecked, Java packaged and Go tested.
- [x] Deterministic ZIP packaging, SHA-256 manifests, release attestations and CI freshness checks cover
  the four client artifacts. Shell completion and command reference output are generated from the
  argparse command model.
- [x] The focused CLI, SDK, flow-document and generated-contract suite passed. SDK regeneration checked
  1,144 files byte-for-byte and deterministic package tests passed.
- [x] The fresh 41-migration backend collection contained 434 tests. With the four authoritative
  c15/c29/c89 timing or ordering checks explicitly deselected, 430 tests ran: 420 passed and ten
  environment/profile tests skipped. The disposable PostgreSQL database was force-dropped.
- [x] Ruff lint, strict mypy, focused Ruff formatting, generated OpenAPI/schema contracts and diff
  checks passed. The unrelated repository-wide Python formatting baseline remains deferred on board
  card `c90`.

Qualification boundary: the EPIC-402 slices of `URS-NFR-USABILITY-005` and
`URS-NFR-MAINTAINABILITY-005` are complete. Both shared NFRs remain Proposed until their other owning
epics complete their destructive-action and generated-artifact qualification slices.

Verdict: PASS — EPIC-402 closed.

## EPIC-405: Flow code editor and validation experience — 2026-08-23

Spec source: board card `c61` and
`backlog/epics/epic-405-flow-code-editor-and-validation-experience.md`.

Verified with `uv`, Python 3.13.12, PostgreSQL 17, React 19, CodeMirror 6 and Docker Compose:

- [x] The graphical workbench provides YAML syntax highlighting, folding, search, multi-selection,
  server formatting and accessible keyboard editing. Completion combines the canonical flow schema
  with core and active installed-plugin resource properties and documentation.
- [x] The browser continuously invokes the same plugin-aware validation contract used by save and
  maps server codes, hints and exact source offsets into CodeMirror diagnostics and focusable issue
  controls. The isolated five-run 5,000-line validation gate passed below its one-second p95 target.
- [x] Bounded expression preview accepts only public sample-context roots, strips resolver roots,
  redacts sensitive nested keys before evaluation and never returns the supplied sensitive value.
- [x] Drafts are isolated by tenant, principal and flow in local storage. Browser unload and in-app
  navigation warn on unsaved changes; Chromium acceptance verified draft persistence and dismissal.
- [x] Authorized editor APIs publish the versioned schema, canonical document, historical revision
  list and draft-to-revision diff. Existing audited save, disable and restore commands power the UI;
  local import/export and clone preserve a YAML-first workflow.
- [x] Frontend production build, 17 unit/coverage checks and the complete Playwright matrix passed:
  nine Chromium workflows passed, nine tablet-inapplicable workflows skipped, and the workbench had
  no critical or serious WCAG 2.2 AA axe findings.
- [x] Ruff, strict mypy over 161 source files, generated schema/OpenAPI parity, backlog validation and
  deterministic SDK regeneration passed. Python compiled, TypeScript typechecked, Java packaged and
  Go tested; SDK freshness covered 1,160 files.
- [x] A fresh 41-migration backend collection contained 435 tests. With the four authoritative
  c15/c29/c89 timing or ordering checks explicitly deselected, 431 ran: 421 passed and ten
  environment/profile tests skipped. The exact disposable database was force-dropped.
- [x] Rebuilt API, executor, scheduler and indexer containers reached healthy state. Live readiness
  reported 41/41 migrations; the authorized editor schema exposed 67 resources, server formatting
  accepted a core flow, the frontend returned HTTP 200 and headless Chromium opened `/flows/new`
  with a valid editable workbench.

Qualification boundary: EPIC-405 completes its slices of `URS-NFR-USABILITY-001` and
`URS-NFR-USABILITY-004`. Both shared requirements remain Proposed until all owning epics and the
pre-GA assistive-technology matrix complete. Repository-wide frontend lint and Python formatting
baselines remain deferred on board cards `c88` and `c90`.

Verdict: PASS — EPIC-405 closed.

## 2026-08-23 — EPIC-406 visual no-code editor and topology model

Scope: `URS-F-0446` through `URS-F-0453`.

- [x] Build-versus-buy review selected exact-pinned `@xyflow/react` 12.11.2 (MIT) because its
  maintained canvas supplies the required pan, zoom, mini map, connection and keyboard-accessibility
  primitives. `npm install` and the container's clean `npm ci` reported zero vulnerabilities.
- [x] The visual model derives nodes, nested groups, lifecycle handlers and explicit dependencies from
  the current canonical YAML draft. Conditions, retries, timeouts, concurrency and subflow targets are
  exposed as node metadata; flow and execution detail graphs now use the same interactive canvas
  language.
- [x] Installed-resource schemas drive the task palette and configuration inspector. Supported paths
  add, configure, connect, disconnect, reorder, group and remove tasks; unknown types or fields are
  labelled for direct YAML fallback.
- [x] YAML AST transformations preserve comments, key order and unrelated extension content. Every
  mutation is staged for review, generated changes are labelled, and task/dependency removal is marked
  `LOSSY TRANSFORMATION` before acceptance.
- [x] Five focused model tests passed. They cover topology expansion, cycles/missing/cross-group link
  rejection, comment-preserving round trips and all visual mutations; the 500-task graph case completed
  in 33 ms against the one-second local budget.
- [x] The production frontend build and all 22 unit/coverage checks passed: 90.74% statements, 80%
  branches, 86.44% functions and 91.66% lines for the governed modules. Targeted ESLint passed.
- [x] The complete Playwright matrix passed: nine Chromium workflows passed and nine
  tablet-inapplicable workflows skipped. The authoring workflow added and configured a task, accepted
  generated YAML, reviewed/cancelled a lossy removal, fell back to YAML, retained its draft and had no
  critical or serious WCAG 2.2 AA axe findings.
- [x] Fourteen canonical DSL checks, strict mypy across 161 source files and Ruff checks passed. No
  public API, DSL, event, persistence or plugin contract changed; accepted YAML continues through the
  EPIC-405 authorized and audited server validation/save path.
- [x] Planning artifacts regenerated and the canonical backlog validator passed with 103 epics, 837
  functional requirements, 63 non-functional requirements and 992 trace links.
- [x] API, executor, scheduler and indexer images rebuilt and the six-service local stack is running.
  Live readiness reports 41/41 migrations, the frontend deep link returns HTTP 200, and headless
  Chromium verified the deployed Create flow heading, interactive topology, mini map and starter task.

Qualification boundary: React Flow's commercial attribution remains visible under its MIT license.
The repository-wide chunk-size and frontend lint baselines remain deferred on their existing board
cards; neither blocks the verified EPIC-406 workflow.

Verdict: PASS — EPIC-406 closed.

## 2026-08-23 — EPIC-407 execution details, Gantt, logs and debugging UI

Scope: `URS-F-0454` through `URS-F-0461` and `URS-NFR-PERFORMANCE-006`.

- [x] The execution workbench exposes identity, immutable revision, creator, trigger, labels, inputs,
  duration, parent/child links and actor/causation-linked state history in a single permission-aware
  view. Inputs, outputs and evidence retain the existing authorization and redaction boundary.
- [x] Topology and Gantt views share task selection. Durable state evidence derives queue, wait and
  runner spans for every attempt; executions above 1,000 task runs use a paged aggregate presentation.
- [x] The reconnectable NDJSON evidence stream resumes from its opaque cursor. Logs filter by task,
  attempt, level, worker, time and text; browser retention is capped at 5,000 evidence events and only
  the latest 300 matching logs render.
- [x] Data panels display authorized execution/task inputs and outputs, metrics, cache decisions,
  artifact references, download actions and errors. History correlates future state evidence with the
  actor, causative event, correlation ID and intervention history introduced by migration 0042.
- [x] Pause, resume, cancel, kill and restart expose only state-valid actions and require an impact
  preview plus operator reason. Replay and backfill use the existing preview/create contract and the
  same confirmation boundary.
- [x] Tab, selected-task, filter and task-offset URL parameters survived direct Chromium navigation.
  The browser workflow crossed Data, Logs, Gantt and History and confirmed a pause impact preview.
- [x] A fresh PostgreSQL database applied all 42 migrations, inserted exactly 100,000 task runs, then
  returned a complete aggregate and a 100-row page in under five seconds with less than 16 MiB traced
  Python peak memory. The 100,000-event frontend model retained exactly the newest 5,000 events in
  under one second.
- [x] The production frontend build, 27 unit/coverage checks, targeted ESLint and the Chromium
  Playwright suite passed. The debugger workflow reported no critical or serious WCAG 2.2 AA axe
  findings.
- [x] Focused Ruff, strict mypy over 161 source files, migration ordering, fresh-database API and
  PostgreSQL performance checks passed. OpenAPI and all four SDKs were regenerated from the versioned
  bounded-detail contract.
- [x] API, executor, scheduler and indexer images rebuilt successfully. All six local services are
  healthy; readiness reports 42/42 migrations, the frontend returns HTTP 200 and a live authorized
  bounded detail call returned its page and complete task summary.

Qualification boundary: `URS-NFR-USABILITY-004` remains In Progress until the shared manual
NVDA/VoiceOver and Firefox/Safari/iPadOS pre-GA release matrix is recorded. That manual qualification
does not block the verified EPIC-407 workflow. Repository-wide lint, formatting and unrelated timing
baselines remain deferred on their existing board cards.

Verdict: PASS — EPIC-407 closed.

## 2026-08-23 — EPIC-610 upgrades, migrations and LTS policy

Scope: `URS-F-0662` through `URS-F-0669`, `URS-NFR-MAINTAINABILITY-002`,
`URS-NFR-MAINTAINABILITY-003` and `URS-NFR-OPERABILITY-006`.

- [x] The versioned release catalog declares the 0.1.0 and 0.2.0 LTS support windows, exact schema
  boundaries, component/protocol minimums, directed rolling compatibility, capacity limits, a
  168-hour rollback window and restoration guidance.
- [x] Preflight and postflight reports cover schema/checksum drift, expand-only migrations, runtime
  configuration, plugin compatibility, every stored flow revision, object-storage metadata,
  database/queue/execution capacity, live component skew, persisted event schema and rollback
  evidence. Unsafe service registration is rejected with direct remediation.
- [x] A fresh PostgreSQL fixture applied migration boundary 0032, persisted a representative flow,
  successful execution and schema-1 event, verified rolling preflight, applied migrations 0033–0054,
  reported the historical event warning, upcast it in a confirmed locked batch with audit evidence,
  and produced a warning-free postflight report.
- [x] Domain and configuration migration tests, service-skew tests, authorized API tests, CLI force
  and canonical-output tests, migration manifest checks and generated-contract checks passed. The
  focused PostgreSQL collection passed four tests; the non-database collection passed eight tests.
- [x] Strict mypy over 204 source files and focused Ruff checks passed. Generated OpenAPI and Python,
  TypeScript, Java and Go SDKs are current across 1,948 files.
- [x] The focused frontend client suite passed 19 tests and the production TypeScript/Vite build
  completed. The full 47-test frontend collection passed, while the pre-existing repository-wide
  branch/function coverage baseline remained below its global threshold on board card `c94`.
- [x] Distributed and compact images rebuilt healthy at migration 54. Against the retained local
  dataset of 103,236 revisions/1,792 unique definitions, live preflight completed in 4.91 seconds and
  correctly blocked on 424 invalid historical definitions and 960,564 queued items; postflight
  completed in 4.34 seconds. Policy, event preview (`UPCAST 0`), flow migration and the HTML upgrade
  deep link all returned successfully, while compact readiness reported 54/54 migrations.

Qualification boundary: external multi-node transfer, dependency failover and long-duration
availability qualification remain deferred under `URS-NFR-AVAILABILITY-004`; EPIC-610 makes no
broader availability claim beyond the locally reproducible LTS upgrade path.

Verdict: PASS — EPIC-610 closed.

## 2026-08-23 — EPIC-613 TLS, proxy and private networking

Scope: `URS-F-0686` through `URS-F-0693` and `URS-NFR-SECURITY-004`; the EPIC-613
certificate-rotation contribution to shared `URS-NFR-SECURITY-006` is complete.

- [x] Direct Uvicorn TLS loads a TLS 1.2-or-newer context with a modern cipher policy and optional or
  required client-certificate authentication. A generated certificate pair loaded successfully, a
  second mounted pair replaced it, and required client CA verification remained enabled.
- [x] Application-owned forwarding disabled Uvicorn's implicit rewriting. A trusted socket peer
  applied HTTPS host/client origin, while the same headers from an untrusted peer produced the
  deterministic `UNTRUSTED_FORWARDED_HEADERS` rejection.
- [x] HTTP, download, webhook and OpenRouter task paths share explicit HTTP/HTTPS proxy, no-proxy,
  custom CA/client-certificate, hostname/CIDR egress allowlist, DNS resolution, redirect revalidation
  and private-address protections. Focused handler and HTTP utility tests passed.
- [x] The Helm 4 trusted-proxy/Ingress/NetworkPolicy and direct-required-mTLS profiles both rendered.
  Direct mTLS mounted the network Secret into all roles, selected the HTTPS service port and used
  client-auth-compatible TCP probes; the split topology and zero-unavailable rollout remained intact.
- [x] The authorized operations API and Administration Operations view expose connection hosts,
  certificate fingerprints/readability, configured-proxy booleans, no-proxy policy and DNS results.
  Seeded proxy credentials did not appear in configuration snapshots or network diagnostics.
- [x] Twenty-one focused networking/configuration/HTTP tests, the PostgreSQL configuration API test,
  20 frontend client tests, the TypeScript/Vite production build, focused Ruff, and strict mypy over
  205 source files passed. Generated OpenAPI and Python, TypeScript, Java and Go SDKs are current
  across 1,964 files. The live OpenRouter smoke test remained skipped because no API key is configured;
  the tested default remains `openai/gpt-5.6-luna`.
- [x] Planning artifacts regenerated and the canonical backlog validator passed with 103 epics, 837
  functional requirements, 63 non-functional requirements and 992 trace links.
- [x] Rebuilt distributed and compact Docker Compose deployments were healthy. The live authenticated
  diagnostics route returned local `disabled` TLS mode and `compact` topology without proxy secrets,
  `/ready` reported `ready`, and the Administration operations deep link returned HTTP 200.

Qualification boundary: provider-specific private load balancers and certificate controllers require
an operated cloud/on-prem environment. Live multi-node certificate rotation is deferred to that
environment; the local contract verifies mounted material replacement, two-replica zero-unavailable
rollout and both TLS topology renders. Shared `URS-NFR-SECURITY-006` remains In Progress pending
EPIC-506 external-secret-manager lifecycle work.

Verdict: PASS — EPIC-613 closed.

## 2026-08-23 — EPIC-701 Terraform and OpenTofu provider

Scope: `URS-F-0702` through `URS-F-0709`.

- [x] A first-party Go provider serves Terraform plugin protocol v5 and exposes 14 named resources
  plus the same 14 data sources: flows, namespaces, files, key-values, dashboards, apps, users,
  groups, roles, bindings, service accounts, tenants, worker groups and plugin policies.
- [x] The public REST/SCIM transport passed stable-ID, import, refresh, plan, apply, native-delete,
  declared retained-lifecycle and immutable-replacement checks. A live key-value scenario passed
  create, clean refresh, out-of-band drift detection, reconciliation, cross-CLI refresh, import and
  OpenTofu destroy.
- [x] Provider credentials and secret environments are sensitive. Placeholder expansion occurs only
  in request memory, response paths containing secrets remain redacted across refresh, recursive
  credential fields are removed, and transport errors do not include response bodies.
- [x] Canonical JSON/YAML comparison suppresses formatting-only changes while retaining actual remote
  drift. Server-managed defaults are excluded on import and caller-owned fields remain plan-visible.
- [x] Schema-generated provider documentation and examples cover all 28 resource/data-source
  surfaces. Terraform 1.15.8 and OpenTofu 1.12.1 each loaded exactly 14 resources and 14 data sources.
- [x] Go formatting, tests, vet and static compilation passed. The PostgreSQL plugin-policy API test,
  focused Ruff, strict mypy, generated OpenAPI and all four generated SDK checks passed.
- [x] GoReleaser produced Linux, macOS and Windows archives for amd64 and arm64. The six archive
  checksums and protocol manifest verified, and an ephemeral RSA qualification key produced a valid
  detached checksum signature.
- [x] Planning artifacts regenerated and the canonical backlog validator passed with 103 epics, 837
  functional requirements, 63 non-functional requirements and 992 trace links.
- [x] Rebuilt distributed and compact deployments are healthy at migration 54. A live authorized
  plugin-policy rule passed create, the provider-required single-resource GET, and cleanup; the
  Administration Operations browser deep link returned HTTP 200.

Qualification boundary: actual GitHub release and public Registry publication require an operator-owned
repository plus its production GPG private key. Local qualification verifies the identical build,
manifest, checksum and detached-signature path without making an external publication claim.

Verdict: PASS — EPIC-701 closed.

## 2026-08-23 — EPIC-702 Kubernetes operator and declarative resources

Scope: `URS-F-0710` through `URS-F-0717`.

- [x] Nine generated `platform.amesh.io/v1alpha1` CRDs cover flows, namespace bundles, files,
  key-values, dashboards, apps, roles, bindings and plugin policies. Every version is served/stored,
  has structural OpenAPI schema and exposes the status subresource.
- [x] The Python operator uses only public AMESH API/SCIM contracts. Status records observed
  generation, safe remote identifiers/digests and `Ready`/`DriftDetected` conditions; PostgreSQL,
  not Kubernetes etcd, remains authoritative for platform and execution runtime state.
- [x] Namespace and label watches, tenant-target selection and one-deployment-per-cluster operation
  are explicit. Named Kubernetes Secrets are read at reconciliation time for rotation; plaintext did
  not appear in status, events, environment variables or response-body errors.
- [x] Bounded retry/backoff, periodic drift detection and `Delete`/`Retain` finalizers passed focused
  tests. Server-added key-value defaults are comparison-normalized, and live resource, event and
  remote revision counts stayed unchanged across repeated resync intervals.
- [x] Sixteen focused operator/Helm tests, Ruff and strict mypy passed. All nine CRDs passed live
  Kubernetes server-side dry-run; Helm 3.19.0 lint and template passed for the opt-in operator profile.
- [x] A live kind deployment passed create, `Ready=True`, Prometheus scrape, Kubernetes events,
  out-of-band drift repair, remote Delete and remote Retain. Acceptance resources were removed after
  verification; the operator, current server/worker image and established CRDs remain available.
- [x] CI regenerates CRDs, rejects schema drift, runs focused contracts and validates the Helm
  profile. ADR-043, the operator runbook and an apply-ready key-value example document scope,
  credentials, version migration and recovery boundaries.
- [x] Planning artifacts regenerated and the canonical backlog validator passed.

Qualification boundary: production multi-cluster failure testing requires operated clusters. The
local contract verifies scoped per-cluster deployment configuration and per-tenant Secret targets.
`v1alpha1` is the only served/storage version, so no conversion webhook is installed until a second
breaking version exists; ADR-043 requires conversion or storage migration before removal.

Verdict: PASS — EPIC-702 closed.

## 2026-08-23 — EPIC-703 public SDKs and embedded integration libraries

Scope: `URS-F-0718` through `URS-F-0725`.

- [x] The pinned OpenAPI generator produced current typed Python, TypeScript, Java and Go packages
  across 1,971 files. Handwritten operational facades are copied deterministically from
  `scripts/sdk_templates`; a clean regeneration check reported no drift.
- [x] Every facade sends bearer and tenant authentication, launches with one stable idempotency key,
  retries only reads and idempotent launches, returns generated execution/log/artifact models,
  normalizes errors and supports terminal wait, fenced cancel, log streaming and artifact download.
- [x] Python exposes thread-safe sync and async clients, TypeScript is async, Java uses an immutable
  JDK HTTP client configuration and Go uses contexts. All four accept caller-controlled transports.
- [x] Exact-byte webhook HMAC verification, constant-time comparison and timestamp-window rejection
  passed in all four languages. Python additionally verified normalized authorization errors and
  NDJSON consumption.
- [x] Python Ruff and four pytest scenarios passed; TypeScript compiled twice and its Node test
  passed; Java packaged and its standalone mock-server test passed; Go formatting and tests passed.
- [x] A live kind conformance run applied `examples/hello-world.yaml`; Python, TypeScript, Java and
  Go each launched the flow, observed `SUCCESS`, retrieved it, listed logs and listed artifacts.
- [x] Pull-request CI now verifies deterministic generation and compiles/tests every language. Tag
  release CI repeats the four-language tests against a fresh Compose API/executor before release.
- [x] ADR-044, the public SDK guide and web, CLI, CI and event-consumer examples document semantic
  compatibility, concurrency, customization, credentials, retry and webhook boundaries.

Qualification boundary: public PyPI, npm and Maven Central publication requires operator-owned
registry accounts. The qualified local release surface is the deterministic four-language package
set and GitHub Release archives with SHA-256 checksums.

Verdict: PASS — EPIC-703 closed.

## 2026-08-23 — EPIC-704 Kestra migration importer and conformance suite

Scope: `URS-F-0726` through `URS-F-0733`, `URS-F-0820` through `URS-F-0825`, and
`URS-F-0829` through `URS-F-0833`.

- [x] The source-preserving Kestra 1.3.30 importer retained comments and order, classified exact,
  compatibility-adapted and blocked source paths, emitted a source-located patch for every
  adaptation, preserved unsupported values and produced a valid native candidate only when no
  blocker remained.
- [x] The digest-pinned `kestra/kestra:v1.3.30` server at revision `db49f3b` accepted the shared
  core flow through its authenticated black-box validator. AMESH accepted the same source and
  mapped labels, task/trigger types, task timeout, retry, concurrency, errors and outputs.
- [x] The declared REST façade exposes flow validation, execution launch and the compatibility
  manifest with generated schemas. The declared CLI validates/migrates flows and plans/imports
  bundles with documented flags, exit codes and JSON output. Specific execution actions remain
  ordered ahead of the generic compatibility launch route.
- [x] Pebble subset fixtures and normalized execution observations compare validation class, state
  sequence, graph, outputs, API/CLI payloads, errors and duration tolerance. Shadow plans suppress
  or mock external tasks and block idempotent mode unless an explicit idempotency key is present.
- [x] Migration fixtures round-tripped all 26 declared resource, governance and history kinds with
  exact payloads, stable identifiers, checksums, tenant/reference validation, chronological events,
  external secret references, bounded checkpoints, replay-safe writes and reconciliation.
- [x] Twenty-six compatibility/Pebble tests passed. The wider affected API/CLI collection passed 37
  tests. Focused Ruff, strict mypy over 213 source files, deterministic OpenAPI/SDK generation and
  Python, TypeScript, Java and Go SDK compilation/conformance passed.
- [x] ADR-045, the operator runbook, fixture provenance and the machine manifest document the pinned
  target, evidence, cutover/rollback procedure and gaps. CI repeats the focused suite and pinned
  black-box validation and rejects an unsupported full-version claim.

Qualification boundary: the manifest intentionally reports blocking plugin-type, complete-Pebble
and bounded REST/CLI gaps, so AMESH makes no full Kestra 1.3.30 compatibility claim. The repository-
wide Python run also reported three unrelated baseline failures: a stale UI capability expectation,
a Windows asyncpg event-loop teardown and a load-sensitive one-second DSL performance threshold.
They were not changed under the active epic's scope lock.

Verdict: PASS — EPIC-704 closed for the manifest-declared surface.

## 2026-08-23 — EPIC-800 deterministic simulation and dry-run engine

Scope: `URS-F-0750` through `URS-F-0757`.

- [x] Revision-pinned plans expanded the canonical task graph with supplied inputs and trigger
  context, evaluated conditions, retries and concurrency keys, and included a non-persisting plugin
  execution-policy preview.
- [x] Mocks, recorded fixtures and schema-only placeholders suppressed external task dispatch.
  Missing fixtures, iteration counts, expressions and estimate models remained typed unknowns rather
  than fabricated success values.
- [x] Declared models produced task-count, critical-path, runner-demand, storage, API-call and cost
  estimates. Plan comparison detected task, plugin-set, estimate and unknown changes.
- [x] Canonical plan evidence used domain-separated HMAC-SHA256; deterministic verification accepted
  the original payload and rejected a modified semantic hash.
- [x] `amesh.simulator/v1` and `amesh.reducer/v1` are emitted in every plan. A focused conformance
  scenario produced the same initial runnable task order as the real production reducer.
- [x] Sixteen focused Python simulation/API/CLI/flow-test scenarios passed with Ruff and strict
  mypy. Twenty-one frontend API-client tests and the production TypeScript/Vite build passed.
- [x] ADR-046, the simulation API/CLI guide, generated OpenAPI/SDK contracts and the flow detail
  preview document and expose the same side-effect-free behavior.

Qualification boundary: estimates are present only for declared models and are not billing or
scheduling guarantees. Plans with unknowns remain useful previews but are not complete-execution
claims. No epic-specific performance or recovery NFR is mapped.

Verdict: PASS — EPIC-800 closed.

## 2026-08-23 — EPIC-802 policy as code and admission controller

Scope: `URS-F-0766` through `URS-F-0773`.

- [x] The documented `amesh.policy/v1` format evaluates immutable instance, tenant and namespace
  revisions at validation, save, promotion, launch and task dispatch. Decisions pin policy IDs,
  revisions and SHA-256 document digests.
- [x] Typed actor, tenant, namespace, flow, plugin, runner, image, secret-scope, network and resource
  contexts passed rule evaluation. Sensitive flow inputs were redacted before evaluation evidence,
  and internal mutated input is excluded from API, audit and decision-history serialization.
- [x] Deny, warn, mutate-default and require-approval outcomes passed positive and blocking fixtures.
  Default mutations never overwrite an explicit value; approval keys are stable policy/rule IDs.
- [x] Enforcing timeouts denied and advisory timeouts warned. Matched conditions, reasons, warnings,
  mutations, approval keys, input hashes and timing remained human-readable in decision evidence.
- [x] Live ephemeral PostgreSQL tests passed immutable policy revision, tenant-RLS decision history,
  audit linkage and real save/launch/dispatch enforcement. A denied dispatch failed the task and
  retained policy evidence on the execution and task paths.
- [x] Focused policy/API/migration tests, affected executor/flow/plugin regression, Ruff and strict
  mypy passed. The React/TypeScript production build passed and all 22 focused API-client assertions
  passed; the focused-only invocation continues to report the repository's global coverage threshold.
- [x] OpenAPI plus Python, TypeScript, Java and Go SDKs regenerated deterministically across 2,183
  files. Python tests, TypeScript build/client test, Java package and containerized Go tests passed.
- [x] ADR-047, the admission-policy API guide, migration 0055, supported upgrade boundary and the
  canonical backlog/traceability artifacts are current; backlog validation passed with 103 epics,
  837 functional requirements, 63 non-functional requirements and 992 trace links.

Qualification boundary: `amesh.policy/v1` is the supported local declarative engine, not an OPA or
Kestra policy-language compatibility claim. External identity/provider qualification remains governed
by its owning epics and does not block this local policy lifecycle.

Verdict: PASS — EPIC-802 closed.

## 2026-08-25 — EPIC-807 versioned agent definitions and capability envelopes

Scope: `URS-F-0806`, `URS-F-0807`, `URS-F-0815`, and `URS-F-0818`; incremental evidence for
`URS-NFR-AGENT-003` and `URS-NFR-AGENT-004`.

- [x] Prompt, declarative skill, model-policy and agent resources share one tenant- and namespace-
  scoped immutable revision ledger. Agent definitions use exact resource and governed MCP tool
  revisions, not mutable latest references.
- [x] Resolution validated schema digests, credentials, network hosts, delegated capabilities,
  tool impact, typed input/output schemas, memory declarations, hard limits and evaluation policy;
  it then persisted one content-addressed `amesh.agent-envelope/v1` pin atomically per subject.
- [x] Restart-idempotent retry returned the original pin. A different envelope for the same subject,
  a missing exact revision, an undelegated skill, an unapproved high-impact tool and cross-tenant
  access all failed closed. Audit evidence omitted credential references and values.
- [x] Provider policy supports ordered fallback routes behind the provider-neutral OpenAI-compatible
  adapter. Revision and migration diagnostics disclose route changes, preserve the durable state
  schema and never claim deterministic provider output.
- [x] The guided Agents page exposes kind, exact-resource, MCP-tool, schema, memory and limit
  selectors; the REST API and CLI create/list/get/resolve/compare/diagnose the same resources.
  Authenticated MCP adds read-only agent discovery and exact inspection without credential values.
- [x] Nineteen focused domain, PostgreSQL repository, API, MCP, CLI and generated-contract tests
  passed. Ruff passed and strict mypy passed all 225 source files. Two frontend unit assertions,
  changed-file ESLint, the production build and one Chromium acceptance passed.
- [x] OpenAPI and all four generated SDKs are deterministic across 2,335 files. Python and Go tests,
  TypeScript compilation/execution-client acceptance and Java compilation passed.
- [x] Rebuilt Compose applied migration 57 and reports 57/57 dependencies ready. Live HTTP acceptance
  created OpenRouter `openai/gpt-5.6-luna` policy, prompt and agent revision 1 and proved an
  idempotent persisted workflow-execution pin with envelope
  `sha256:668c8e99814b8444bd95ca16ba97bbe72f4d84568bf648c5c6b62a4a77609f2b`.

Qualification boundary: the envelope makes configuration resolution deterministic and inspectable;
it does not make model output deterministic. EPIC-808 consumes the pin for durable turns, tool
mediation and checkpoint resume. The shared agent isolation and provider-portability NFRs remain
In Progress until the later single-agent, memory/evaluation and multi-agent epics complete their
adversarial scenarios. The generated Go tree has a pre-existing formatting baseline, while its
containerized test suite passes; that unrelated generator cleanup was not included.

Verdict: PASS — EPIC-807 closed.

## 2026-08-26 — EPIC-823 generic document and artifact pipeline

- [x] `amesh.artifact-ref/v1` carries exact content address, media type, byte size, checksum,
  tenant/namespace, provenance and retention without a storage URI, credential or host path.
- [x] `amesh.document-extractor/v1` accepts the exact artifact reference and emits pages, chunks,
  source locators, text, token count and immutable source/extractor/parser provenance.
- [x] The exactly pinned `pypdf==6.16.1` implementation runs through the ordinary task-plugin
  harness in a killable child process with byte, page, token, time and output limits. Unsupported,
  encrypted, malformed, identity-mismatched and parser-failure fixtures fail without a result file.
- [x] One real PostgreSQL/MinIO journey uploaded a PDF, read its public reference, executed an
  extractor plus downstream consumer, verified ordered evidence and downloaded checksum-identical
  `document-result.json`.
- [x] The namespace UI selects or uploads PDFs; the guided workflow builder emits exact file
  bindings; and the Data trace renders parser identity, provenance, pages/chunks and extracted text.
- [x] The consolidated Python set passed 27 tests. Ruff and strict mypy passed. Three frontend unit
  files passed 41 assertions; scoped ESLint, the production build and six desktop/tablet Playwright
  fixture journeys passed.
- [x] The rebuilt deployment reported all 66 migrations ready. Live execution
  `01a03e31-1a44-70f0-92b9-e1d8095ac1fa` reached `SUCCESS`; a Chromium journey verified its exact
  artifact, `amesh.core.document.extract@0.2.0`, `pypdf@6.16.1`, extracted text and persisted result.
- [x] Generated JSON Schemas/OpenAPI, ADR-060, the PDF how-to, namespace resource guide, execution
  file guide, plugin manifest guide and guided authoring guide describe the implemented contracts.

Qualification boundary: the core contract is media- and parser-neutral, while this epic qualifies
PDF text extraction through one replaceable reference plugin. Domain-specific document semantics and
direct plugin access to storage credentials remain explicit non-goals.

Verdict: PASS — EPIC-823 closed.

## 2026-08-26 — EPIC-824 agent harness conformance and portability

- [x] The versioned `amesh.agent-harness-conformance-manifest/v1` kit covers structured output,
  multi-turn tools, approval denial, token/cost/tool/turn limits, timeout, malformed and undeclared
  actions, continuation, restart reuse, context compaction and provider-cache evidence.
- [x] All 23 manifest cases passed twice in the same environment with byte-identical canonical reports,
  zero failures/skips and report digest
  `sha256:b1b26b67b6b6793738f5f612320de8873beb719acb65ea62f22dced644e29022`.
- [x] Failure injection proved the harness cannot mutate the authorized provider call, invoke the
  gateway twice, fabricate/change the gateway result, receive provider credentials, dispatch native
  tools or commit workflow state. AMESH rejected malformed and unpinned tool actions before MCP.
- [x] Pi 0.84.3 completed the versioned handshake, bounded both control-frame directions, preserved a
  model result larger than the control limit and mapped deadline expiry to `TIMED_OUT`.
- [x] The explicit registry selected Pi by configuration and rejected an unknown adapter without a
  built-in fallback. The documented port and adapter template preserve public `agent.session` behavior.
- [x] The local Docker gate runs the kit twice, compares reports and probes the production image.
  Provenance records exact Python/Node, worker, lockfile and all 93 npm package versions,
  integrity values and licenses; no dependency license is unknown.
- [x] The focused Python suite, Pi Node test, Ruff and strict mypy passed; the only skip was the
  separately opt-in live-provider test. Generated schemas and backlog validation passed.
- [x] The rebuilt `amesh-api` image passed `python -m amesh.harness_probe`; Compose reported all 66
  migrations and roles ready. Live execution `01a03e4e-6ffc-74a8-b044-980bdc87dae9` reached
  `SUCCESS`: both agent sessions used `openai/gpt-5.6-luna` through `pi-agent-core` 0.84.3 and exposed
  normalized token, billed-cost and prompt-cache evidence.
- [x] The sprint OpenAPI contract and Python, TypeScript, Java and Go SDKs regenerated deterministically
  across 2,763 files. Manifest-digest/contract tests, Python execution-client tests, TypeScript build
  and execution test, Java package/execution test, and containerized Go tests passed.

Qualification boundary: Pi remains the only shipped production adapter. The conformance port and kit
make future DSH, Goose or other adapters evaluable, but this epic does not ship them or permit an
operator to switch harnesses during an active session.

Verdict: PASS — EPIC-824 closed.

## 2026-08-27 — Docker-local MVP and first external agent-team qualification

- [x] Executable GitHub Actions CI/release workflows and the SDK workflow example were removed.
  `Dockerfile.verify`, `compose.verify.yaml` and `scripts/verify-local.sh` now provide the explicit
  developer-invoked backend, frontend, Pi-harness and contract gates.
- [x] The Docker-local backend, frontend and Pi-harness phases passed against the final code. Ruff
  passed, strict mypy passed all 273 source files, the Python suite completed without a test failure,
  the frontend unit/build gates passed, and the 23-case Pi report was byte-identical across two runs.
- [x] After correcting the new epic's catalog metadata, the Docker-local contract phase passed:
  122 epics, 837 functional requirements, 63 non-functional requirements, 1,000 trace links,
  clean-room checks, REUSE compliance, generated-contract equality and compile checks.
- [x] PR #1's 133 review occurrences were deduplicated by active-path risk. The remaining direct
  local-runner race was fixed by reserving an attempt before process creation; its concurrent
  regression, focused Ruff and focused mypy passed. Capability-gated and edge findings remain
  explicitly deferred in [`mvp-pr-1-risk-triage.md`](docs/reviews/mvp-pr-1-risk-triage.md).
- [x] EPIC-825 added generic immutable agent-tool argument bindings from RFC 6901 session-input
  pointers. The same contract is present in OpenAPI and regenerated Python, TypeScript, Java and Go
  clients; it contains no VibeStonks domain semantics.
- [x] The rebuilt VibeStonks API reused frozen snapshot `bmi_5a34aa92b556a2420ce81a4e`, AMESH flow
  revision 9 and execution `01a03f8c-0042-7dfe-9520-c418632ce1e3`. It returned the same idempotent
  artifact `bmda_7e88ce79b7818e32ae7e9632` across repeated requests, with 12 successful Luna sessions,
  12 durable evidence records, one `DO_NOTHING` disposition and zero broker commands. Its focused
  client/integration suite passed 120 tests plus 20 subtests.

Qualification boundary: VibeStonks owns its financial prompts, agent roster, MCP research tools,
frozen-domain bundle and accepted decision contract. AMESH owns only generic durable orchestration,
provider/harness mediation, exact revision execution, deterministic bindings, retries and evidence.
This is a research-only local qualification and does not grant either service broker authority.

Verdict: PASS — local MVP and first external agent-team use case qualified.

## 2026-08-29 — EPIC-826 multi-tenant agent session service

- [x] The canonical `/api/v1/agent-sessions` surface creates one bounded request from an exact agent
  revision and exposes owner-scoped listing, detail, reconnectable durable events, structured result,
  pause, cancel, resume and retry over the existing execution reducer and PostgreSQL session journal.
  Actor-scoped idempotency resolves accepted retries before admission, and ordinary listing filters
  ownership before its SQL limit; global or tenant `MANAGE` remains an explicit privileged path.
- [x] The documented text-only `/v1/chat/completions` and `/v1/responses` subset maps onto that same
  canonical authority. Non-streaming and buffered SSE fixtures, malformed requests, immutable profile
  tuning, durable usage, queued/running backpressure, typed errors and accepted-session recovery URLs
  passed. A later conversational turn remains a new request carrying the desired history.
- [x] The public contract is harness-neutral. Pi is the current exact `pi-agent-core` 0.84.3 pin behind
  the typed registry/factory port and `amesh.pi-worker/v1`; adapter, version and protocol persist with
  each attempt, and resume rejects any mismatch before provider work. Future harness metadata is
  allowlisted before public evidence so prompts, reasoning, debug values and credentials cannot leak.
- [x] The React Session Control Room and uv-managed CLI expose authorized agent selection, safe
  harness provenance, lifecycle state, trace events, budgets, controls and final output. The focused
  frontend model/client suite passed 31 assertions, the production build passed, and the Chromium
  journey passed its axe check and refreshed
  `docs/product/ui-audit/screenshots/agent-sessions/chromium-control-room.png`.
- [x] OpenAPI plus Python, TypeScript, Java and Go SDKs regenerated deterministically; the 2,893-file
  SDK drift check and generated-contract test passed. Backlog regeneration and validation report 123
  epics, 837 functional requirements, 63 non-functional requirements and 1,000 trace links.
- [x] The complete Docker-local push gate passed: Ruff, strict mypy across 274 source files, 735
  backend tests with 169 environment/capability skips and four documented deselections, 97 frontend
  tests, the Chromium journey, two deterministic 23-case Pi conformance runs, clean-room and REUSE
  checks, review regressions, production-image probe, repository archives and four SDK packages.
- [x] The published synthetic report at
  `docs/reference/agent-session-reference-qualification.json` passed with 10,000
  seeded terminal sessions, 1,000 concurrent logical cursor readers and three PostgreSQL projection
  repositories. It observed zero duplicate service/event identities, zero duplicate guard claims,
  zero cross-tenant events, zero reader mismatches and zero missing seeded final-result projections.
  Seed throughput was 2,560.575 sessions/s; cursor-read wall time was 5.176793 s and p95 was
  5,010.420 ms. Report SHA-256:
  `d60ecf10437b5e350a3931e06a3019debfb7f00d0efb6a88aafdc751bfcfd5a2`.
- [x] The opt-in OpenRouter `openai/gpt-5.6-luna` Pi smoke passed after loading the local `.env`
  key into the host test process. Two model responses traversed `pi-agent-core`, one
  AMESH-mediated tool effect occurred, the structured final answer was non-empty, both context
  projections were recorded and prompt-cache status was normalized as reported or unavailable.

Qualification boundary: the reference workload directly seeds terminal PostgreSQL projections, so
it measures projection integrity and cursor/guard behavior rather than accepted-work recovery or a
production SLO. Existing recovery suites remain the evidence for accepted-work fencing and
idempotency. Remote transport, external-provider performance, production HA, backup and restore are
not qualified here. Pi is the only shipped harness adapter, but session clients contain no Pi fields
and another adapter can be selected for new sessions after it passes the same conformance contract.

Verdict: PASS — EPIC-826 closed for the published local reference profile.

## 2026-08-30 — EPIC-827 M1 session control-plane boundary and RBAC

Spec source: Agent Hotel card c144 DoD.

- [x] ADR-067 and the architecture/design records separate the application session data plane,
  session administration plane and reused canonical runtime authorities without adding another
  executor, queue, transcript database or evidence ledger.
- [x] `agent_session` create, own-view, fleet-list and lifecycle-manage capabilities plus separate
  administration, policy and migration resources are mapped to the built-in `session-client`,
  `session-operator` and `session-admin` roles at the existing instance/tenant/namespace scopes.
- [x] Data-plane session create/read/control routes enforce the new resources. A bounded compatibility
  path accepts legacy execution grants only for no-grant or credential-scope upgrade cases; an
  explicit session deny was exercised and did not fall back.
- [x] Migration 0069 seeded the roles/grants and fleet indexes in a fresh ephemeral PostgreSQL
  database. The focused domain, API and manifest suite passed 49 tests, and the isolated PostgreSQL
  migration assertion passed.
- [x] Focused Ruff and `git diff --check` passed. Importing the application succeeded after the
  concurrently developed fleet adapter module became available.

Adversarial pass: verified a principal with an explicit session denial cannot inherit a legacy
execution grant, unknown/other-owner sessions retain the generic denial boundary, namespace-scoped
stream authorization completes before response bytes, and migration role/index creation succeeds in
an isolated database.

Not covered: fleet pagination, policy mutation, UI and portability are owned by cards c145-c149.

Verdict: PASS — M1 closed; EPIC-827 remains in progress.

## 2026-08-30 — EPIC-827 M2 session fleet and administration API

Spec source: Agent Hotel card c145 DoD.

- [x] `GET /api/v1/admin/agent-sessions` requires both session-administration view and fleet-list
  authorization with no legacy execution-permission fallback. It reads canonical execution/session
  authorities through tenant RLS and exposes fixed newest-first keyset pagination.
- [x] Opaque cursors are bound to the tenant and exact filters. State, namespace, agent, owner,
  harness and creation-time filters plus a limit capped at 100 passed contract tests.
- [x] Fleet rows expose owner, immutable agent/harness provenance, bounded counters and dependency
  posture without checkpoint content, prompts, final results, arguments, credentials or reasoning.
  Aggregates cover the complete filtered set rather than only the current page.
- [x] The instance endpoint exposes only tenant ID/slug and lifecycle counts. Detailed inspection
  requires a separate tenant-authorized request, so it cannot become an elevated query parameter.
- [x] Eight focused API/PostgreSQL tests passed against a fresh ephemeral database. They exercised
  multiple tenants, keyset traversal, filters, cursor mismatch rejection and absence of cross-tenant
  session rows. Seven provider-free tests also passed with the database test correctly skipped when
  its explicit URL was absent.
- [x] Ruff and `git diff --check` passed. OpenAPI and Python, TypeScript, Java and Go SDK generation
  is deterministic and current across 2,921 generated files.

Adversarial pass: reused a cursor against a different tenant/filter fingerprint, queried two tenant
fleets from one database, attempted administration access with no matching grant and inspected the
serialized row/instance shapes for protected session content. Each case failed closed or remained
within the documented metadata boundary.

Not covered: UI controls, policy mutation and portable migration are owned by cards c146-c149.

Verdict: PASS — M2 closed; EPIC-827 remains in progress.

## 2026-08-30 — EPIC-827 M3 session administration workbench and controls

Spec source: Agent Hotel card c146 DoD.

- [x] The dedicated `/session-administration` workbench presents tenant fleet totals, active and
  terminal state, bounded usage/cost, dependency posture, typed filters, fixed cursor pagination,
  immutable agent/harness provenance and canonical session trace drill-down.
- [x] Individual and bounded bulk lifecycle controls reuse the canonical execution command path.
  Bulk requests require one independently fenced `expectedVersion`/`expectedEpoch` pair per session,
  an exact action/count confirmation phrase and a reason; partial outcomes return per-session status.
- [x] Session selection is capped at 25 in both the API model and browser interaction. Instance
  aggregates are fetched only with the separate instance-view capability, while ordinary session
  clients retain their owner-scoped data-plane view.
- [x] Five focused bulk-control API tests passed. Thirty-two focused frontend model, client and
  component assertions passed; changed-file ESLint and the production Vite build passed.
- [x] Four Chromium/tablet Playwright cases passed with axe checks and refreshed the durable
  administration-workbench screenshot.

Adversarial pass: exercised stale version/epoch fences, mismatched confirmations, more than 25
selected sessions, per-item partial failures and a tenant administrator without instance-level
visibility. Each case failed closed or stayed within its authorized scope.

Not covered: policy mutation, portable transfer and deployment migration are owned by cards
c147-c149.

Verdict: PASS — M3 closed; EPIC-827 remains in progress.

## 2026-08-30 — EPIC-827 M4 session policy, quota and dependency governance

Spec source: Agent Hotel card c147 DoD.

- [x] Immutable tenant, namespace and application policy revisions govern admission, concurrency,
  token, cost, duration, retention and provider/harness/tool allowlists. Updates use an expected
  revision and record actor/digest provenance in the canonical audit log.
- [x] Application policy selection is bound to the authenticated principal identity. Omitted or
  spoofed application IDs cannot bypass an application policy; the effective identity and applied
  policy chain persist with the canonical execution and fleet/detail projections.
- [x] Cumulative evaluation fails closed at launch, uses the tightest numeric limits and requires
  every applied non-empty allowlist to accept the immutable dependency pins. Existing data-plane and
  OpenAI-compatible contracts remain backward compatible when no policy is configured.
- [x] Session retention is enforced through the existing lifecycle authority from terminal time.
  Preview/confirmation, bounded batches, tenant RLS, legal holds, artifact deletion decisions,
  tombstones and lifecycle audit events are reused; active and paused sessions remain ineligible.
- [x] The workbench separately gates policy view/manage, displays exact revisions, digests and the
  effective chain, and provides a structured editor with explicit optimistic-conflict feedback.
- [x] Fifty-four focused backend/API/PostgreSQL tests and 35 focused frontend assertions passed.
  Ruff, strict mypy, changed-file ESLint and the production Vite build passed. Chromium and tablet
  Playwright journeys passed with axe after correcting the policy-region locator; the durable
  workbench screenshot was refreshed.

Adversarial pass: attempted application identity spoofing, stale revision mutation, dependency
allowlist violations, policy-disabled admission, immediate terminal retention across tenants and a
purge containing active, paused, non-session and legal-held executions. Each case failed closed or
preserved the protected record.

Not covered: portable profile/session transfer and deployment migration are owned by cards c148-c149.

Verdict: PASS — M4 closed; EPIC-827 remains in progress.

## 2026-08-30 — EPIC-827 M5 portable profiles and checkpoint-safe session migration

Spec source: Agent Hotel card c148 DoD.

- [x] `amesh.profile/v1` exports the exact immutable agent/dependency histories and MCP references,
  rejects secret plaintext, seals canonical JSON with SHA-256 and plans destination create/reuse or
  conflict outcomes before mutation. Imports are digest-bound and idempotent.
- [x] `amesh.session-transfer/v1` accepts only completed terminal history or a paused `READY` clean
  checkpoint with exact capability/harness pins and no active lease, admission claim, approval,
  pending checkpoint work or `STARTED` external invocation.
- [x] Canonical execution, task, session, invocation, event, evidence and artifact records import in
  one PostgreSQL transaction with deterministic tenant-local ID mappings, preserved public identity
  and contiguous cursors. Duplicate imports return the original receipt; a changed digest under the
  same import identity is rejected.
- [x] Artifact-bearing round-trip coverage verifies destination tenant, size and checksum before
  mutation and preserves one artifact/evidence identity. An injected mid-import failure left neither
  canonical records nor an import receipt.
- [x] The distinct administration routes require migration view for export/plan and migration manage
  for import, with no legacy execution fallback. OpenAPI and Python, TypeScript, Java and Go SDKs are
  current across 3,077 generated files.
- [x] The workbench supports selected-session/profile download, JSON file upload, exact digest/source/
  target/mode diagnostics, constrained stable credential acknowledgements, mandatory plan invalidation
  when inputs change and explicit imported/already-present results.
- [x] Twenty focused Python/API/PostgreSQL tests and 36 focused frontend assertions passed. Ruff,
  strict mypy, changed-file ESLint, the production build, generated-contract drift and responsive
  Chromium/tablet Playwright journeys with axe passed; both durable screenshots were refreshed.

Adversarial pass: attempted checksum tampering, secret-bearing export, tenant mismatch, cursor gaps,
ambiguous invocation transfer, stale credential renaming, missing/mismatched artifacts, an injected
transaction failure, duplicate replay, import-identity digest reuse and permissions without the
session-migration grant. Each failed closed or returned the original idempotent receipt.

Not covered: whole-cluster drain/restore/cutover and deployment qualification are owned by card c149.

Verdict: PASS — M5 closed; EPIC-827 remains in progress.

## 2026-08-30 — EPIC-827 M6 self-hosted deployment and release qualification

Spec source: Agent Hotel card c149 DoD.

- [x] `compose.session-orchestrator.yaml` runs only migrate, preflight, API, executor and scheduler
  roles, publishes the API on loopback and uses external PostgreSQL and S3-compatible object storage.
  It mounts no Docker socket, disables the Docker runner and carries no broker or model-provider
  credential.
- [x] PostgreSQL authentication, object-store credentials, the administrator token, token pepper,
  continuation encryption key and signing keys are file-backed Docker secrets. The Helm profile uses
  operator-created existing Secrets for the same boundaries and supports external identity/SCIM
  configuration without embedding credentials.
- [x] Hardened preflight gates service startup. API, executor and scheduler expose role-aware health;
  disabled worker, indexer and maintenance roles remain explicitly disabled rather than appearing
  unhealthy.
- [x] The self-hosting guide documents deployment, secrets, external dependencies, admission policy
  and supported identity boundaries. The whole-cluster migration runbook coordinates admission drain,
  canonical work drain, PostgreSQL/object-store recovery points, secret rebinding, compatibility
  checks, fencing, cutover and rollback. Selective profile/session moves use the M5 plan-first UI.
- [x] A fresh-image isolated Compose smoke applied 71/71 migrations through
  `0071_transfer_imports.sql`; hardened preflight reported ready; API, executor and scheduler were
  healthy; and `/ready` returned HTTP 200 with database, object storage, service registry and enabled
  roles `READY`. Exact temporary containers, networks, image aliases and secret files were removed.
- [x] Five deployment-profile tests, Compose rendering and Helm lint passed. The focused aggregate
  passed 107 backend/API/PostgreSQL tests on a fresh disposable database, 39 frontend assertions,
  production build, changed-file lint, strict mypy and Chromium/tablet Playwright/axe journeys.
- [x] The complete Docker-local push gate passed repository-wide Ruff and strict mypy, 786 backend
  tests with 177 environment-specific skips and four documented deselections, 109 frontend tests,
  both Chromium agent-session journeys, the 23-case Pi conformance kit twice, generated-contract,
  backlog, clean-room, REUSE and review gates, production-image probing and repository/four-SDK
  packaging.
- [x] The opt-in live OpenRouter `openai/gpt-5.6-luna` Pi session test passed after the offline gates;
  the provider key was loaded from local environment only and was not printed or persisted.

Adversarial pass: rendered the deployment profiles and verified absence of Docker socket access,
Docker execution, broker credentials, provider credentials, public API binding and embedded secret
values. The migration and transfer suites covered cross-tenant denial, digest conflict, duplicate
import, ambiguous external work, injected rollback, artifact integrity and legal-hold retention.

Explicit non-claims: this local qualification does not claim multi-region failover, arbitrary
external-dependency portability, production availability SLOs or production-HA recovery time.

Verdict: PASS — M6 and EPIC-827 closed for the documented self-hosted reference profile.

## 2026-08-31 — Open issue repair and EPIC-831 qualification

Spec sources: GitHub issues #4–#7 and Agent Hotel cards c160–c162.

- [x] Provider-side JSON/schema rejection carries a typed non-secret rejection result into the
  configured session repair path, counts rejected usage/cost, records bounded rejection/exhaustion
  evidence and uses a distinct durable repair invocation key. Canonical instructions require a brief
  public rationale and explicitly exclude chain-of-thought.
- [x] OpenAI-compatible non-2xx, streaming and HTTP-200 error envelopes preserve only bounded
  status/type/code/message diagnostics. JSON, plain-text, malformed and oversized fixtures passed;
  credentials, headers, prompts, request bodies and raw response bodies were absent from durable
  model/session evidence.
- [x] `amesh.agent-tool-plan/v1` expands ordered steps and bounded `forEach` candidates from immutable
  input, applies root/item RFC 6901 bindings, persists canonical digests and a restart-safe ledger,
  checks the exact next call before approval/tool I/O and rejects early final output until complete.
  API, DSL, OpenAPI and all four generated SDKs are current; no-plan sessions retain prior behavior.
- [x] The EPIC-828 provider-free multimodal regression slice passed as part of 158 focused tests, and
  the live Pi/OpenRouter `openai/gpt-5.6-luna` test delivered a real governed PNG to the model. It
  reported 233 input, 119 output and 352 total tokens, USD 0.00020834, reported prompt-cache state and
  eight safe chronological frames; a second call reused the terminal result without another model
  response.
- [x] The complete Docker-local aggregate passed: repository Ruff and strict mypy; 892 backend tests
  (178 environment-gated skips and four documented deselections); 120 frontend tests and production
  build; two application and eight documentation Chromium/tablet Playwright journeys; 25 Pi
  conformance cases; generated contracts, backlog, clean-room and REUSE gates; production-image probe;
  and repository plus four-SDK packaging.

Verdict: PASS — issues #4–#7 are implemented and qualified for publication; EPIC-831 is complete.

## 2026-09-02 — EPIC-835 agent reliability and EPIC-836 model-engine qualification

Spec sources: GitHub issues #10–#12, #16 and #17; Agent Hotel cards c180–c186; EPIC-835 and
EPIC-836.

- [x] Pi progress sources include the canonical invocation/repair identity. A real Pi worker plus
  PostgreSQL regression rejected an invalid structured result, accepted its repair and preserved
  unique chronological progress without weakening exact-retry or conflict behavior.
- [x] Durable invocation accounting preserves safely known prompt, completion, reasoning, cache and
  total tokens plus explicit exact, lower-bound or in-doubt billing state across valid, invalid,
  rejected, failed, timed-out, cancelled and replayed attempts.
- [x] Provider-bounded session policy can remove selected AMESH application ceilings and task/model/
  tool timeouts while retaining provider physical limits, cancellation, policy provenance and legacy
  bounded defaults.
- [x] Encrypted continuation bindings remain ordered against exact retained assistant messages across
  projection, restart and three-turn transport; public state and clean transfer exclude protected
  continuation bodies.
- [x] Terminal progress cursors close at EOF, committed later-attempt events replay before close and
  an uncommitted running retry retains heartbeat behavior.
- [x] The provider-neutral model-engine contract selects direct HTTP, official Codex App Server or
  GitHub Copilot CLI through `engineRef`. Isolated account homes and authorized/audited status,
  login and logout cover text/images, structured output, chronological progress, continuation,
  context, effort, timeout/cancellation and truthful usage/quota semantics. Native tools, MCP,
  remote access and updater behavior fail closed.
- [x] Independent Fable 5 review approved the final engine routing, notification, timeout, usage,
  login parsing, progress-retry and Windows process-home cleanup changes.
- [x] The complete Docker-local aggregate passed repository-wide Ruff and strict mypy; 1,009 backend
  tests (184 environment-specific skips and four documented deselections); 122 frontend tests and
  production build; two application and eight documentation Playwright journeys; eight Pi worker
  tests and all 27 Pi conformance cases; generated contracts, backlog, clean-room and REUSE gates;
  production-image probing; and repository plus four-SDK packaging.

Live-auth boundary: deterministic fixtures and production dispatch qualify the implementation
without protected credentials. A live isolated OpenAI ChatGPT-subscription or GitHub Copilot run was
not claimed because the official browser/device flow requires the operator's interactive approval.
AMESH did not copy the workstation CLI identity, scrape tokens or bypass that authorization.

Verdict: PASS — EPIC-835 and EPIC-836 are complete at the documented local and operator-authorized
deployment boundary; issues #10–#12, #16 and #17 are ready to close through the publishing PR.

## 2026-09-02 — Copilot Windows reinstall-prompt hotfix

Spec source: Agent Hotel card c187 and the reported repeated “Would you like to reinstall GitHub
Copilot CLI?” prompt.

- [x] A regression with the VS Code extension bootstrapper first on PATH and npm `copilot.CMD`
  second proves AMESH launches only the installed CLI.
- [x] A bootstrapper-only regression proves AMESH returns a typed configuration error without
  spawning any installer or updater.
- [x] Managed invocation, login and logout processes centrally receive
  `COPILOT_AUTO_UPDATE=false`; the existing invocation fixture asserts the child environment.
- [x] Local candidate inspection selected `C:\nvm4w\nodejs\copilot.CMD`; the rejected candidate was
  the VS Code `globalStorage\github.copilot-chat\copilotCli\copilot.BAT` bootstrapper. No install or
  update was performed.
- [x] The affected engine/account/runtime slice passed 23 tests. Ruff, strict mypy and strict docs
  build passed, and an independent release-blocking review reported no findings.
- [x] The complete Docker-local aggregate passed 1,011 backend tests (184 environment-specific
  skips and four documented deselections), 122 frontend tests and production build, two application
  and eight documentation Playwright journeys, eight Pi worker tests, all 27 Pi conformance cases,
  generated contracts, backlog, clean-room and REUSE gates, production-image probing, and
  repository plus four-SDK packaging.

Verdict: PASS — the AMESH-owned Copilot launch path cannot enter the VS Code reinstall prompt loop.

## 2026-09-02 — EPIC-837 milestone 6 pure domain and session reducer

Spec sources: GitHub issues #19 and #26; Agent Hotel card c195; EPIC-837 milestone 6.

- [x] Domain execution commands no longer read ambient observability state. Runtime shells attach
  current trace context explicitly, and a clean subprocess import proves `amesh.domain` loads none
  of SQLAlchemy, OpenTelemetry, Prometheus, Pillow or YAML.
- [x] Typed agent-session lifecycle events and a pure reducer govern every legal state/phase
  transition. Exhaustive matrix tests cover valid and invalid paths, fresh-session starts, terminal
  immutability and the requirement that successful sessions contain a final result.
- [x] The PostgreSQL session repository applies the reducer after its idempotency lookup, preserving
  exact terminal retries while rejecting new events after completion. All four focused PostgreSQL
  repository tests passed in Docker.
- [x] Historical/public session event and record serialization remains compatible, and blueprint and
  image-validation compatibility exports remain available through the lazy domain surface.
- [x] Two independent release-blocking re-reviews found no remaining scope or failure-path blockers.
- [x] The complete Docker-local aggregate passed repository formatting, Ruff and strict mypy; 1,091
  backend tests (186 environment-gated skips); 123 frontend tests and production build; two
  application and eight documentation Playwright journeys; 11 Pi worker tests and all 27 Pi
  conformance cases; generated contracts, backlog, clean-room and REUSE gates; production-image and
  model-engine probes; and repository plus four-SDK packaging.

Verdict: PASS — EPIC-837 milestone 6 is complete and issue #26 is ready to close through PR #36.

## 2026-09-02 — EPIC-837 milestone 7 unified application composition

Spec sources: GitHub issues #19 and #27; Agent Hotel card c196; EPIC-837 milestone 7.

- [x] `amesh.app` remains the stable import and monkeypatch surface while the API implementation now
  lives under `amesh.api`; a fresh-process regression proves module identity and server imports.
- [x] Execution launch is a framework-neutral application service. Synchronous, detached and
  successful-subflow scheduling preserve the existing durable records and runtime ownership rules.
- [x] API launch and worker recovery use the same injected runner, handler, HTTP-policy and executor
  builders. API recovery remains limited to session/subflow work, while worker recovery retains
  shell and script types.
- [x] Transactional construction tests prove Docker/Kubernetes clients close if runner, handler or
  executor composition fails before ownership reaches the entry point.
- [x] Local administration and service-role webhook composition use the shared authentication and
  outbound HTTP policy builders; existing CLI and worker monkeypatch seams remain compatible.
- [x] The canonical OpenAPI document remains exactly 772,147 bytes with SHA-256
  `4e66ab75960907a0890436381fc3b09aa7e161c7c3d4d2b382adfc541984da04`; 12 focused application and
  compatibility tests passed.
- [x] The complete Docker-local aggregate passed repository formatting, Ruff and strict mypy over
  308 source files; 1,103 backend tests with 186 environment-gated skips; 123 frontend tests and
  production build; application/documentation Playwright journeys; Pi worker and conformance suites;
  generated-contract, backlog, clean-room and REUSE gates; production-image probes; and repository
  plus four-SDK packaging.

Verdict: PASS — EPIC-837 milestone 7 is complete and issue #27 is ready to close through PR #37.
