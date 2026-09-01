# Progress Log

## Current state

- What works: the local MVP, EPIC-827 Agent Session Orchestrator foundation and EPIC-828 live
  multimodal run capability are at migration 72. EPIC-829 adds a comprehensive, searchable user
  documentation site with tested getting-started, workflow, agent-session, extension, integration,
  operations and reference journeys. EPIC-830 adds a privacy-safe historical prompt-cache report
  and a v2 context-compaction marker that preserves a stable model-visible prefix while retaining
  full provenance in the durable receipt. EPIC-833 makes progress overflow nonfatal: one durable
  `TRUNCATED` marker bounds telemetry while the session and final evidence continue. The supported
  Docker-local gate covers backend, frontend, Pi harness, contracts, review regressions, Compose
  profiles, production-image probing and local release archives. A
  tracked native pre-push hook runs that complete gate for ordinary pushes after one-time per-clone
  installation; this clone is enabled.
- What's in flight: none from the requested EPIC-828 through EPIC-833 sequence. EPIC-833 is
  complete and its regression, documentation and generated planning artifacts pass the local gate.
- Known broken / TODO: Kubernetes findings remain on `c130`, cloud/storage findings on `c131`, and
  optional federation/webhook/script findings on `c132`. Repository format, frontend lint and
  specialist environment baselines remain explicit on `c90`, `c88` and `c110`.
- How to run/test: enable the push guard with `make install-git-hooks` on POSIX or
  `.\scripts\install-git-hooks.ps1` in PowerShell. Run the gate directly with
  `make verify-local-all` or `.\scripts\verify-local.ps1 -Suite all`. Focused suites, artifact
  locations and the local-enforcement boundary are documented in
  `docs/how-to/run-local-verification.md`; the running UI is at `http://localhost:8000`.

## Session log

### 2026-09-01 (EPIC-833 durable nonfatal agent-progress backpressure)

- Did: fixed GitHub issue #14 at the durable PostgreSQL sink boundary. The first hard-limit overflow
  stores one deterministic `TRUNCATED` marker; later and concurrent novel frames return the same
  marker with `truncated=true` and `duplicate=false` instead of throwing into the model/harness.
  Exact retries retain `duplicate=true`, conflicting reuse still fails and the pure reducer remains
  terminal after truncation.
- Verified: the focused PostgreSQL regression passed through repository recreation and then stored a
  successful final result, 321 tokens, USD 0.045 and one tool result. The affected 95-test suite had
  one expected skip; the complete Docker-local gate passed 907 backend tests, 122 frontend tests,
  two application and eight documentation browser journeys, 27 Pi conformance cases, production
  image probing and repository/four-SDK packaging.
- Boundary: AMESH owns validation, redaction, ordering, idempotency and hard ingestion/storage
  limits. Clients may filter, collapse or sample accepted events only for presentation.

### 2026-08-31 (EPIC-830 prompt-cache hit-rate forensics and optimization)

- Did: added a read-only, tenant-filtered historical analyzer over durable model-invocation and
  correlated session evidence, with separate coverage, request-hit, token-reuse, write, cost and
  unavailable metrics across safe operational dimensions. Added context projection v2, whose
  model-visible compaction marker omits changing transcript identity while its durable receipt keeps
  full transcript/context digests, indexes, bounds and algorithm provenance; v1 receipts remain
  readable.
- Finding: the frozen history contained 732 model calls, including 695 successes. Of 673 successes
  with normalized cache evidence, 531 had positive reads (78.9004% request hit rate); 1,860,152 of
  13,059,275 normalized input tokens were cached reads (14.2439% token reuse). Turns two and later
  were already strong at 503/507 positive reads. The first reproducible AMESH-controlled break was
  the v1 compaction marker changing with transcript digest/count, so the selected fix targeted that
  prefix instability rather than adding an unsupported provider-specific affinity control.
- Verification: seven analyzer fixtures and the focused context/session/evidence/API/provider
  regressions passed, as did Ruff, strict mypy, generated contracts, four generated SDKs and the
  strict docs suite. The complete Docker-local gate passed 868 backend tests, 120 frontend unit
  tests, two product browser journeys, four Pi tests, 25 harness cases, eight documentation browser
  journeys, production images, planning/licensing checks and release packaging.
- Boundary: no retained cache-effect evidence existed, so savings remain unknown/null. No paid
  provider call was made, and task-result caching, response caching and invocation replay were not
  changed or included in the prompt-cache denominators. This requested sequence is complete.

### 2026-08-31 (EPIC-829 comprehensive user documentation site)

- Did: added a strict Material for MkDocs site with curated navigation, search and task-oriented
  getting-started, platform-concept, workflow, agent-session, integration, extension, operations and
  reference content. Added a non-root, loopback-only Docker documentation profile and `uv`-locked
  build path, plus desktop/tablet browser journeys that exercise navigation, search and accessibility.
- Verification: the focused documentation suite passed its strict build and all eight Chromium/axe
  journeys. A no-cache image build became healthy and served the key pages and search index over
  HTTP 200 as UID 10001 on `127.0.0.1`. The complete local gate also passed all backend, frontend,
  Pi, harness, contract, SDK, planning, licensing, production-image and packaging checks.
- Boundary: the provider-free node test is documented separately from live LLM execution. A live
  agent journey requires the operator's own OpenRouter key; no paid provider request was made for
  EPIC-829. EPIC-830 is the next queued program and will measure past-run cache behavior before any
  cache implementation change.

### 2026-08-31 (EPIC-828 M5-M7 and epic completion)

- Did: exposed authenticated cursor-paginated and NDJSON live progress through the canonical API,
  CLI and generated Python, TypeScript, Java and Go SDKs; added one accessible timeline to Agent
  Sessions, Session Orchestrator and execution detail; and added governed image upload/selection with
  safe reference metadata. Enforced frame, segment, session, buffer and rate budgets with explicit
  truncation and observer timeout semantics. Image modality admission now covers ordinary tasks,
  plugins, workflow propagation, Pi and exact provider routes before external work. Later messages
  now create idempotent durable turns under the same logical session, resume the exact successful
  checkpoint and immutable pins, and keep progress cursors monotonic across turns.
- Verification: the complete Docker-local gate passed Ruff, strict mypy over 289 source files, 858
  backend tests with 178 environment-specific skips and four documented deselections, 120 frontend
  tests with the configured coverage thresholds, the production build, two Chromium/axe journeys,
  four Pi worker tests, the 25-case harness conformance kit, generated contracts and all four SDKs,
  backlog/provenance/REUSE gates, production-image probing and local repository/SDK packaging. The
  chronological UI fixture visibly preserves `thinking 1 -> tool work -> thinking 2 -> terminal`.
- Live qualification: opt-in OpenRouter `openai/gpt-5.6-luna` accepted governed image-plus-text input
  through Pi, returned schema-valid structured output and recorded eight safe progress frames, 215
  input tokens, 112 output tokens, 327 total tokens, USD 0.0001774 and provider-reported prompt-cache
  state. Safe JUnit evidence is stored at `.artifacts/pi-luna-qualification.xml`; provider-specific
  reasoning internals and cache-hit causality are not claimed.
- Boundary: AMESH transports and governs image references but does not provide OCR, vision tooling,
  editing or generation in core. Durable public progress contains only fixed taxonomy-defined
  lifecycle facts; provider-authored summaries, hidden chain-of-thought, prompts, image bytes, signed
  URLs and continuation state are excluded. EPIC-828 is complete; EPIC-829 is the next queued program.

### 2026-08-31 (EPIC-828 M4 Pi progress and durable chronological journal)

- Did: added one provider- and harness-neutral progress sink over the canonical
  `agent_session_events` journal, with row-locked event indexes, idempotent source sequences,
  attempt-aware cursors and permanent segment closure across lifecycle work. The session task now
  gives provider streaming and Pi the same validated tenant/session/attempt context. Pi emits only
  bounded lifecycle, thinking-without-text and hashed tool status; provider-authored summaries are
  replaced with fixed `model.processing` status before journal acceptance.
- Verification: 86 focused domain, provider, Pi adapter, model-task, session-task, migration and
  PostgreSQL-contract assertions passed with three environment-gated skips. Pi's four Node tests
  prove distinct `thinking 1 -> tool work -> thinking 2` segments and no retained thought/tool text.
  Ruff and strict mypy passed across the ten affected source modules.
- Next step when resuming: card c155 exposes cursor replay and live delivery through canonical and
  OpenAI-compatible APIs, the CLI, OpenAPI and generated SDKs.

### 2026-08-31 (EPIC-828 M3 provider streaming and multimodal OpenRouter adapter)

- Did: added an optional provider-neutral streaming interface, safe typed provider deltas and
  OpenAI-compatible SSE assembly. Provider activity forms separate lifecycle segments around
  intervening tool/model work; author-supplied summary text is replaced at the durable boundary and
  private reasoning is retained only as protected continuation state.
  Governed image bytes resolve with tenant and canonical-artifact verification immediately before
  I/O and exist as transient data URLs only in the provider request.
- Verification: 92 focused provider, registry, model-node, session/harness, artifact, workflow and
  API assertions passed with one existing skip. Streaming fixtures cover required SSE flags,
  chronological thinking/tool boundaries, structured final assembly, usage, continuation privacy
  and exact image mapping. Ruff, strict mypy and targeted diff checks passed.
- Next step when resuming: card c154 connects provider/Pi progress to the canonical durable session
  journal with immediate acceptance, idempotent source sequences and restart-safe ordering.

### 2026-08-31 (EPIC-828 M2 platform-wide governed image ingestion and propagation)

- Did: added one Pillow-backed image validation authority and `NamespaceResourceService` image
  upload/resolve operations over immutable tenant artifacts; added authenticated image API routes;
  staged workflow `image` inputs into references; and allowed ordinary model nodes and sessions to
  consume the same ordered content-part contract after image-capability checks. Workflow execution
  and webhook paths now use the shared artifact service, and public state contains references and
  safe display metadata rather than bytes or storage URLs.
- Verification: 91 focused domain, artifact, workflow, model-node, session/harness, provider-registry
  and API assertions passed with one existing skip. Ruff, strict mypy and targeted diff checks passed.
- Boundary: core validates, stores and transports images but does not perform OCR, image editing or
  generation. Image interpretation remains an explicit provider/harness/plugin capability; Pi fails
  closed until its adapter declares and implements that capability.
- Next step when resuming: card c153 implements provider-neutral incremental model delivery and the
  OpenRouter invocation-time image mapping without persisting data URLs or hidden reasoning.

### 2026-08-31 (EPIC-828 M1 chronology, privacy and platform image contracts)

- Did: accepted ADR-068; added allowlisted provider/harness-neutral progress frames, bounded segment
  reducer semantics, stable source idempotency and opaque attempt-aware cursors over the canonical
  journal. Added the shared `amesh.image-ref/v1` artifact value, ordered model content parts and
  image-input capability negotiation before provider I/O. Image references are a platform primitive
  that any workflow/task/plugin node may carry, not a session-only contract.
- Verification: 23 focused domain/provider/generated-contract assertions, 30 provider/adapter
  regressions and 64 session/API regressions passed. Ruff and strict mypy passed for the affected
  source. Five checked-in schemas, canonical planning regeneration and backlog validation passed.
- Boundary: durable progress accepts only fixed taxonomy-defined factual status. Provider-authored
  summaries, raw reasoning, generic provider payloads and image bytes/URLs remain invalid durable
  fields. Image signature/ingestion, runtime propagation and actual consumer resolution belong to M2.
- Next step when resuming: card c152 implements platform-wide image validation, staging and immutable
  reference propagation before provider streaming work begins.

### 2026-08-31 (EPIC-828 live multimodal run program start)

- Did: audited the existing provider, Pi harness, session journal, event stream, workflow file,
  object-storage, OpenAI-compatible and run-inspection boundaries; registered EPIC-828 as the next
  goal with separate progress-streaming and image-input acceptance criteria. The required ordering is
  explicit: non-contiguous segments remain `thinking 1 -> work -> thinking 2`, never a regrouped
  `thinking 1+2 -> work`. Image scope covers session start, supported later turns, workflow start and
  every workflow/task/plugin node through immutable tenant-scoped references; only consumers that
  interpret image content require image-input capability.
- Verification: the two focused existing agent-session stream contract tests passed. The planning
  corpus regeneration and backlog validator are the registration gate; feature tests belong to the
  new milestone cards and are intentionally not claimed here.
- Boundary: public thinking means fixed factual lifecycle status, not provider-authored text or hidden
  chain-of-thought. AMESH will not add OCR, image editing or image generation to core, and arbitrary
  tasks or model routes do not gain image capability without declaring and passing conformance.
- Next step when resuming: complete EPIC-828 M1's versioned progress/content-part contracts, privacy
  rules, ordering and attempt-aware cursor semantics before runtime changes.

### 2026-08-28 (Docker-local pre-push gate)

- Did: added a tracked native pre-push hook, POSIX and PowerShell per-clone installers, a Make target
  and contributor/operator documentation. The hook reuses the canonical complete Docker aggregate;
  it neither duplicates verification commands nor adds a hook-manager dependency.
- Verification: both installers enabled `.githooks` idempotently; shell syntax passed; an unavailable
  Docker endpoint produced hook exit 1; and the real hook passed the complete backend, frontend, Pi,
  contract, review, Compose, production-image and packaging aggregate.
- Boundary: Git's explicit `--no-verify` bypass and clone-local configuration remain; an
  unbypassable gate needs a server-side receive hook or protected-branch status check, which is not
  added while hosted CI remains disabled.
- Next step when resuming: review and merge PR #1 through the named human approval boundary.

### 2026-08-27/28 (PR #1 Docker-local merge preparation)

- Did: resolved the two current supported-path review blockers, completed cross-platform Docker-local
  verification and packaging entry points, removed stale hosted-CI/release claims, reconciled current
  feature/migration/status documentation, fixed generated SDK Markdown links and regenerated the
  canonical planning corpus.
- Verification: the Docker aggregate passed 676 backend tests with 166 environment-gated skips and
  four named deselections, strict mypy over 273 source files, 90 frontend tests plus production build,
  23 Pi conformance cases with byte-identical reports, planning/backlog/clean-room/REUSE/contracts,
  five focused review regressions, four Compose configurations, the production-image Pi
  probe and local repository/four-SDK packaging. SDK generation is deterministic across 2,761 files;
  changed-document and SDK link scans report zero broken relative links. Archive checksums and
  exclusions passed. The rebuilt verifier image contains no local environment-secret file. The
  rebuilt stack reports every role/dependency ready at migration 67/67, and both `/` and
  `/openapi.json` return HTTP 200.
- Deferred: the aggregate does not claim the separately tracked repository-format (`c90`),
  frontend-lint (`c88`), specialist matrix (`c110`) or review-environment (`c130`–`c132`) gates.
- Next step when resuming: commit and push the merge-preparation patch, refresh PR #1 review state and
  hand the clean merge candidate to the named human approver.

### 2026-08-27 (MVP current-head review findings 1–8)

- Did: made fresh executions immediately dispatchable while protecting fresh running work; aligned the split executor with subflow, approval and isolated-plugin handlers; separated redacted webhook evidence from encrypted retry/replay input; reset flow-editor and query state across route/principal changes; and enforced Docker output limits.
- Verification: 49 affected-path backend/PostgreSQL tests passed with two real-Docker cases skipped in that combined run; both real-Docker cases passed separately. The complete Docker-local gate, Compose configuration checks and production image harness probe passed. Scoped Ruff, formatting and strict mypy passed. Five focused frontend assertions, TypeScript, the production build, targeted ESLint and two Chromium journeys passed. The rebuilt stack is ready at migration 67/67; a live protected-webhook canary completed without appearing in public execution or occurrence projections, and the deployed guided create-to-trace Playwright journey passed.
- Deferred: findings 9–11 remain on `c130`: Kubernetes output limits, Helm webhook signing-secret wiring and operator namespace-path isolation.
- Next step when resuming: review and merge the updated single MVP pull request; findings 9–11 remain deferred on `c130`.

### 2026-08-26 (EPIC-822 capability catalog and connection wizard complete)

- Did: added the authorized cross-resource catalog projection, search/filter/detail interface, guided MCP discovery/save/test wizard, exact-reference attachment to agent definitions and new guided workflow drafts, and immutable redacted discovery-test audit evidence.
- Verification: 18 focused Python/API/PostgreSQL/generated-contract tests, Ruff, strict mypy, 40 frontend assertions, targeted ESLint, the production build and a responsive Playwright journey passed. A real local MCP HTTP server proved discovery/save/test without one tool invocation. The rebuilt API remained fully ready at migration 66; authenticated deployed catalog/filter and missing-pin redaction smokes passed.
- Deviations from plan: none. Connection tests intentionally stop at MCP discovery; actual tool invocation remains on the existing governed invocation path.
- Next step when resuming: implement EPIC-823 generic document and artifact pipeline on card `c125`.

### 2026-08-26 (EPIC-821 live agent run inspector and replay complete)

- Did: added safe session summaries and a redacted, event-index-paginated session detail API; projected canonical events into one responsive agent inspector with model, tool, approval, repair, context, usage/cache, schema and terminal facts; and extended the existing replay path with frozen source inputs, exact flow/plugin/envelope/policy pins, source linkage and explicit idempotency keys.
- Verification: 10 focused Python/API/PostgreSQL/contract tests, Ruff, format, strict mypy, 32 frontend assertions, targeted ESLint, the production build and two responsive Playwright journeys passed. Desktop, tablet and mobile screenshots plus axe checks passed. Deployed Luna execution `01a03de7-fdcd-791f-992c-721e38eb0313` exposed a deliberate three-turn, 11-event repair/failure trace without checkpoints or hidden reasoning; readiness remained full at migration 66.
- Deviations from plan: the live qualification intentionally terminates at the deterministic assertion boundary after exhausting two scheduled repairs, so the same trace proves the multi-turn, repair and terminal-failure inspector states without adding a disposable external tool service.
- Next step when resuming: implement EPIC-822 capability catalog and connection wizard on card `c124`.

### 2026-08-26 (EPIC-820 guided agent node builder complete)

- Did: replaced the AI/model direct-call starter with canonical `agent.session`; added authorized exact-revision selection, request-schema compatibility filtering, atomic credential-scope updates, context/repair/data-handling controls, detailed side-effect-free envelope evidence and the existing fixture-backed isolated flow-test action. Guided edits still mutate one YAML document and preserve unsupported fields.
- Verification: eight focused unit tests, targeted ESLint, the production build, Chromium/tablet create-to-reopen Playwright journeys, a 390×844 mobile check, three screenshots and axe checks passed. Live flow `epic820.guided.agent_builder_smoke_3030a781@1` validated and passed admission, previewed envelope `sha256:ff871604535c207d197bd5e2ecdea87b9860bf02e040a4a172b570b727295382`, passed its isolated test with zero production executions, artifacts and secret lookups, and reopened with `researcher-3030a781@1` plus `maxMessages=96`. The rebuilt API returned full readiness at migration 66.
- Deviations from plan: agent definitions requiring fields other than the guided `request` input are intentionally filtered from this starter and remain editable in YAML; this prevents the guide from inventing invalid generic input values.
- Next step when resuming: implement EPIC-821 live agent run inspector and replay on card `c123`.

### 2026-08-26 (EPIC-819 complete: bounded context and prompt-cache evidence)

- Did: added the pure `amesh.recent-complete-turns/v1` projection with message, canonical-byte and estimated-token limits; preserved pinned instructions and newest complete assistant/result groups; kept the canonical checkpoint transcript unchanged; persisted stable per-turn receipts and context events; normalized OpenRouter prompt-cache reads, writes, hit ratio and signed cost effect; and projected that evidence into canonical bundles without conflating it with task cache or invocation replay.
- Verification: 43 focused unit, adapter, API, evidence and PostgreSQL cases passed with one environment-gated skip; the exact Pi Node bridge test passed; strict mypy passed over 266 source files; focused Ruff, generated contracts, backlog validation and diff hygiene passed. A live `openai/gpt-5.6-luna` Pi session completed an AMESH-mediated tool call and schema-valid final result. Rebuilt API and executor services returned full readiness at migration 66.
- Deviations from plan: none. The context estimator is deliberately labeled estimated and every receipt records canonical byte counts and digests so later tokenizers can be compared without rewriting history.
- Next step when resuming: execute EPIC-820 guided agent-node authoring on card `c122`.

### 2026-08-26 (Pi production cutover and agent-session feature parity)

- Did: removed the built-in runtime adapter and made `AgentSessionHarness` a required dependency; injected Pi in API and recovery-executor composition; prevented provider credentials from entering the Pi process; stopped large model content from being echoed over the control channel; and packaged Node 22 plus the exact Pi 0.84.3 lock into local setup, CI and the product image.
- Verification: 16 non-live focused Python tests pass with every existing primary-session behavior routed through real Pi, including fallback, accepted-action restart reuse, continuation, repair, hard limits, approval, memory, evaluation and release evidence; a cutover assertion proves the handler has no implicit fallback. A separate live `openai/gpt-5.6-luna` structured session passed through Pi. Deployed execution `01a03bec-6f6e-7a7e-ac89-2c8d7d9a0278` completed a two-session Luna mesh with 1,320 tokens and two persisted `pi-agent-core` evidence records. The Node bridge test, focused Ruff, strict mypy over 265 source files, Compose configuration, a production image build and four in-image Node/Pi/import/settings probes pass. A result larger than 1 MiB also crosses the adapter without control-frame regression.
- Deviations from plan: the product owner advanced production cutover ahead of the separate context-compaction and cache-evidence slices. EPIC-819 therefore remains open even though Pi is now the sole production session harness.
- Next step when resuming: implement immutable bounded-context projections and compaction receipts, then normalize provider prompt-cache evidence before closing `c121`.

### 2026-08-26 (EPIC-819 evaluation and first harness swap slice)

- Did: created canonical EPIC-819/card `c121`; compared DSH, Pi and Goose from current primary evidence; selected Pi 0.84.3 in ADR-058; extracted the typed one-turn `AgentSessionHarness` and AMESH-locked model gateway; routed the existing session behavior through a compatibility adapter; and added an npm-locked isolated Pi worker plus optional Python adapter.
- Verification: 13 focused Python tests pass, including default compatibility, model-call tampering rejection, the real Pi subprocess adapter and a two-turn Pi session whose one tool effect is AMESH-mediated. The Pi worker's Node test passes a parent-mediated two-model/one-tool loop. Focused Ruff and strict mypy pass.
- Deviations from plan: Pi's new `AgentHarness` facade is incomplete in 0.84.3, so the selected adapter uses the stable direct `Agent` API. The built-in adapter remains the composition default; enabling Pi by default is gated by the remaining EPIC-819 context, cache, restart and live Luna evidence.
- Next step when resuming: add the immutable-transcript/bounded-context projection and compaction receipt, normalize prompt-cache evidence, then qualify restart and a live OpenRouter Luna tool session before closing `c121`.

### 2026-08-26 (EPIC-811 through EPIC-818 neutral orchestration sprint complete)

- Did: completed and deployed the client-neutral orchestration/evidence profile, provider-neutral model and tool boundaries, hardened local profile, restart qualification, differential shadow execution and evidence-backed release controls. Regenerated OpenAPI plus Python, TypeScript, Java and Go SDKs, and added the `/releases` operator UI.
- Verification: 557 backend tests passed with 158 environment-gated skips and two separately deferred deselections; strict mypy passed over 263 source files; Ruff check and new-file format gates passed; SDK generation is deterministic across 2,671 files; the frontend build, 23 client assertions and three Chromium release journeys passed. Live Compose is ready at migration 66/66; authenticated neutral-client, evidence verification, Luna/OpenRouter, differential restart and promote→rollback restart smokes all passed. The isolated hardened profile also passed without Docker/socket, broker or model-provider authority.
- Deviations from plan: none in the nine-epic product scope. Client-specific adapters, workflows, tools, thresholds and cutover remain client responsibilities. The complete-suite plugin event-loop issue was recorded as deferred card `c120` instead of expanding this sprint.
- Next step when resuming: review and merge the single MVP pull request; broader production and external-resource qualification remains on its existing deferred cards.

### 2026-08-25 (EPIC-810 reliable scheduling and role health complete)

- Did: completed EPIC-810 with retry-wait convergence, exact legacy-pin migration or audited flow quarantine, persisted role-cycle health and aggregate enabled-role readiness; disabled only 164 `tests.scheduler.*` test flows in the shared development database to remove test pollution without deleting execution evidence.
- Verification: 61 focused unit/API/Helm/migration/PostgreSQL tests passed. Live Compose applied migration 0060, reported scheduler failure as HTTP 503/DEGRADED, recovered all six roles to READY in 11 seconds, and retained exactly one occurrence and execution `01a03980-1533-7e64-97b7-7d30642bc231` across scheduler restarts before and after the scheduled instant.
- Deviations from plan: no client-specific contract, workflow, domain tool or cutover logic enters AMESH.
- Next step when resuming: finish EPIC-811's deployed neutral-client and tenant/realtime evidence, then close the canonical evidence bundle in EPIC-812.

### 2026-08-25 (human-first product experience umbrella complete)

- Did: reconciled cards `c97` through `c102` into umbrella `c103`; renamed the primary authoring
  surface to Workflows; added trigger and runner visibility to Mission Control; exposed revision,
  environment, policy and finite runner selection before launch; added direct policy remediation;
  and verified the operate, failed-run diagnosis and guided-create journeys at desktop, tablet and
  mobile widths.
- Verification: frontend build, changed-file lint, all 67 unit assertions and all 26 applicable
  Playwright checks pass with 30 intentional project skips. The responsive journey matrix reports
  no critical or serious axe findings. Rebuilt Compose is ready at migration 59/59, and both
  authenticated live journeys pass against `http://localhost:8000`.
- Deviations from plan: the agent-envelope regression still mocked the retired resolve endpoint;
  its fixture was aligned to the side-effect-free preview contract required by the preserved
  advanced-capability journey. No product behavior changed for that correction.
- Next step when resuming: review and merge the single MVP pull request; deferred production-only
  qualification remains separately tracked.

### 2026-08-25 (production determinism assurance complete)

- Did: added a versioned, content-addressed determinism envelope to simulation and persisted launch
  metadata; pinned exact flow/plugin/admission-policy revisions; projected canonical branch-aware
  nodes, dynamic defaults/bounds, nesting and worst-case expansion; rejected undeclared child-graph
  injection; isolated internal evidence from expressions; and surfaced the same controls in
  authoring and the simple execution trace.
- Verification: focused simulation/DSL/API/PostgreSQL/frontend tests, Ruff, strict mypy over 236
  source files, production build and generated SDK/contract gates pass. Rebuilt Compose is ready at
  59/59. Execution `01a0377e-2151-7781-ada8-7c6feefe398b` completed `SUCCESS`, and its persisted
  envelope exactly matched preview digest `1fd1df905e7280fd9ddad40d7807a04abf8574fe39d43e6d7ae1794036320291`.
- Deviations from plan: the first live preview included a transient plugin decision ID in its
  control digest. Plugin decisions remain signed audit evidence, while the corrected control
  envelope uses the same immutable admission-policy pins as runtime. External output remains
  explicitly nondeterministic.
- Next step when resuming: close and publish `c101`, then complete the integrated acceptance and
  publication of umbrella epic `c103`.

### 2026-08-25 (EPIC-806 complete)

- Did: implemented five explicit mesh topologies on the ordinary durable task graph; exact member/session and acyclic-topology validation; deterministic capability/policy/availability/evaluation/cost/latency routing; typed policy-gated and secret-redacted hand-offs; tighter member budgets and fail-closed parent aggregation; authorized route preview; readable mesh/route/handoff trace annotations; ADR-055; API/how-to documentation; generic and live Luna examples; and regenerated API, catalog and SDK contracts.
- Verification: 28 focused Python tests and five frontend assertions pass; Ruff and strict mypy over 235 source files pass; the production frontend build and generated-contract gate pass. Rebuilt Compose is ready at 59/59. OpenRouter Luna execution `01a0374f-5746-7c4c-b983-19fb47fa244e` completed two governed sessions and a typed hand-off with both deterministic and judge gates, 1,172 tokens, `$0.0007354` cost, zero tools, exact member/parent budget evidence and immutable provenance digests.
- Deviations from plan: deployed revision 1 correctly failed closed because its agent resource required business assertions; revision 2 added the declared assertion and passed. Generated Go clients also required Pydantic decimal defaults to omit invalid integer literals from constructors while retaining the same runtime defaults. Agent/model output remains explicitly nondeterministic while topology, route ordering, typed boundaries, policy and budgets are deterministic.
- Next step when resuming: close and publish `c109`, then select `c101` and execute the production-determinism qualification card.

### 2026-08-25 (EPIC-809 complete)

- Did: completed tenant-, namespace- and agent-revision-isolated memory with bounded private/shared scopes, retention, redaction, size limits, metadata-only discovery and audited deletion; exact immutable evaluation fixtures, assertions, weighted rubrics and optional pinned judges; deterministic-first acceptance; direct human release authority; side-effect-free preview; durable memory/evaluation/release events; guided Agents controls; readable trace annotations; migration 0059; ADR-054; API/how-to documentation; an example; and regenerated API/resource/SDK projections.
- Verification: 14 affected Python tests, three real-PostgreSQL integration tests and seven frontend assertions pass; Ruff, strict mypy over 233 source files, the production build and diff gate pass. Rebuilt Compose is ready at 59/59. OpenRouter Luna cold execution `01a03728-0034-7730-82f9-fce320a344fc` and recall execution `01a03728-fc13-70cc-b592-df2fabca6c88` both completed successfully with exact evaluation revision 1, judge/model/cost/token provenance, ordered session events and private-memory write/recall/replacement evidence.
- Deviations from plan: the distributed Compose executor needed the same agent resource/session/memory repositories as the monolithic worker, and its five-second recovery grace raced healthy bounded model calls; the direct deployment blockers were corrected and regression-tested. A live judge rejection at 0.68 against the 0.70 gate was retained as adversarial evidence rather than weakening the gate. Shared agent NFRs remain In Progress for EPIC-806 multi-agent qualification.
- Next step when resuming: close and publish `c108`, then select `c109` / EPIC-806 for multi-agent topology, typed hand-offs and explainable routing.

### 2026-08-25 (EPIC-809 start)

- Did: closed and published EPIC-808 as `15a5e46`; selected `c108`; reconciled agent resources, session checkpoints, flow tests, simulation and durable approvals; and accepted ADR-054 for explicit tenant-RLS memory scopes plus exact evaluation revisions, deterministic-first gates, optional pinned judge evidence and ordinary `core.approval` release authority.
- Deviations from plan: no vector database, separate promotion engine or new dependency is required. Memory recall is exact-key and treated as untrusted user data; semantic retrieval remains outside this epic.
- Next step when resuming: implement migration 0059, immutable evaluation resources, the memory journal and session evaluation/release integration before extending the authorized API and trace.

### 2026-08-25 (EPIC-808 complete)

- Did: completed the recoverable `agent.session` task against one exact capability pin; added migration 0058 with tenant-isolated checkpoints and idempotent session events; mediated stable model and MCP operation identities; enforced cumulative turns, loops, tools, tokens, cost and duration; required direct approval for high-impact tools or sensitive egress; gated final results through the pinned schema plus deterministic business assertions; projected agent events into ordinary execution evidence; exposed an authorized session API and readable trace annotations; and regenerated the API, SDK, backlog and traceability projections.
- Verification: 12 affected-path Python tests plus two real-PostgreSQL migration/repository tests pass; Ruff lint and strict mypy over all 229 source files pass; 26 focused frontend assertions and the production build pass; deterministic contract/planning/SDK checks match 2,355 generated files; Python, TypeScript, Java and containerized Go SDK checks pass. Rebuilt Compose reports migration 58/58 ready. Live OpenRouter execution `01a036f3-eda7-77d1-838d-a46727e3aa8e` used `openai/gpt-5.6-luna`, passed the pinned output schema and one business assertion, and persisted a successful one-turn session with 379 tokens and `$0.0002178` cost.
- Deviations from plan: OpenRouter's strict schema subset required tool arguments to cross the provider boundary as a JSON string while final output uses the pinned object schema; AMESH decodes and validates both before dispatch or acceptance. The repository-wide Ruff format baseline still reports 75 pre-existing files outside this epic; they were not changed. Memory, learned evaluation, human release promotion and multi-agent topology remain with EPIC-809/806.
- Next step when resuming: close and publish `c107`, then select `c108` / EPIC-809 and implement isolated memory plus evaluation/release gates.

### 2026-08-25 (EPIC-808 start)

- Did: selected `c107`; reconciled the existing execution, capability-pin, model/MCP invocation and human-approval boundaries; compared graph expansion, an external agent runtime and a recoverable ordinary task; and accepted ADR-053 for a PostgreSQL checkpoint/event journal with stable per-operation invocation keys.
- Deviations from plan: no dependency or second execution engine is required. Memory, learned evaluation, release promotion and multi-agent topology remain with EPIC-809/806.
- Next step when resuming: implement migration 0058, the session domain/repository, and the bounded handler before wiring execution-trace visibility and deployed acceptance.

### 2026-08-25 (EPIC-807 complete)

- Did: completed versioned prompt, declarative skill, provider-neutral model-policy and agent resources; exact prompt/skill/model/MCP-tool references; deterministic instruction composition; typed input/output schemas; isolated memory declarations; delegated capability, secret, network and filesystem boundaries; hard budget/turn/tool/loop/recursion/concurrency limits; evaluation policy; atomic content-addressed subject pins; revision comparison; provider migration diagnostics; guided Agents UI; REST/CLI operations; MCP tool catalog plus authenticated `list_agents` and `inspect_agent`; migration 0057; ADR-052; API/how-to documentation; and regenerated four-language SDKs.
- Verification: 19 focused domain, PostgreSQL repository, API, MCP, CLI and generated-contract tests pass; the PostgreSQL test proves restart-idempotent pins, conflicting-envelope rejection, tenant isolation and secret-free audit evidence. Ruff passes and strict mypy passes all 225 source files. Two focused frontend unit assertions, changed-file ESLint, the production build and the focused Chromium agent-composition acceptance pass. Deterministic SDK generation matches 2,335 files; Python/TypeScript/Java/Go clients compile or test successfully. Rebuilt Compose is healthy at migration 57/57, and live HTTP acceptance created Luna policy/prompt/agent revision 1 and returned the same persisted pin on retry for envelope `sha256:668c8e99814b8444bd95ca16ba97bbe72f4d84568bf648c5c6b62a4a77609f2b`.
- Deviations from plan: the generated Go tree, including pre-existing files, is reported by `gofmt`; its containerized `go test ./...` gate passes and generator formatting was not changed under this epic. Durable model turns, tool mediation and checkpoint resume intentionally remain EPIC-808 consumers of the EPIC-807 pin. Model output is explicitly nondeterministic.
- Next step when resuming: close and publish `c106`, select `c107` / EPIC-808, and implement bounded durable single-agent sessions against the exact capability pin.

### 2026-08-25 (EPIC-807 start)

- Did: closed and published guided-creation card `c100` as `8aae515`; selected `c106` / EPIC-807; compared workflow embedding, per-kind tables and a typed shared revision ledger; and accepted ADR-052 for exact immutable resource references plus one transactionally persisted capability-envelope pin.
- Deviations from plan: none. This epic defines and resolves agents but does not run an autonomous loop, execute skill code or persist ambient credentials.
- Next step when resuming: implement typed prompt, skill, model-policy, agent and envelope contracts, then add migration 0057 and the transactional resolver repository.

### 2026-08-25 (guided workflow creation complete)

- Did: completed board card `c100` with six intent starters; a numbered guided authoring rail; namespace, task/plugin, trigger, upstream-output, runner, model and secret selectors; one round-trip YAML source shared with visual/code editing; inline validation and policy explanations; dynamic-bound simulation; revision-pinned isolated smoke tests; permission states; and a save-to-run path that lands on the simple execution trace. Accepted ADR-051 and exported responsive visual evidence.
- Verification: six focused model/editor tests and the production frontend build pass; the full suite passes all 62 functional unit assertions while retaining the pre-existing `c94` branch/function coverage-threshold exit; all 23 applicable Playwright tests pass with 27 intentional project/environment skips. The first-run browser acceptance creates and runs a two-step workflow without opening YAML and reports zero critical/serious axe findings. Rebuilt Compose is ready at migration 56, and an authenticated live test saved, policy-checked, simulated with two tasks and zero unknowns, isolated-tested with zero production executions, launched and opened the persisted trace in 7.2 seconds.
- Deviations from plan: no dependency, backend format or parallel execution path was added. The existing unrelated ESLint findings in `ExecutionEvidenceTimeline.tsx` and deferred global coverage threshold remain on their existing owners and were not changed.
- Next step when resuming: close `c100`, commit and publish it, then select `c106` / EPIC-807.

### 2026-08-25 (EPIC-312 complete)

- Did: completed and documented provider-neutral chat, embedding, structured-output and proposed tool-call tasks; explicit model budgets/data policy; a redacted invocation journal; tenant-scoped MCP discovery, immutable schema pins and allowlists; impact/approval gates; authenticated connection APIs; and authorization-checked read-only AMESH MCP tools. Updated URS-F-0383 through URS-F-0390 and regenerated the canonical epic projections.
- Verification: Ruff, strict mypy, lock/diff/compilation gates and 26 affected-path tests passed; the separate live OpenRouter test passed against `openai/gpt-5.6-luna`. Distributed Compose is healthy at migration 56, anonymous `/mcp` returns 401, and a live structured Luna flow completed with validated downstream output, usage, cost, redacted provenance and a durable successful invocation row.
- Deviations from plan: none. The deployed smoke required the existing namespace `team: platform` label and OpenAI-compatible structured schemas to declare a type alongside enum; the checked-in example now reflects both requirements. No durable agent-session, memory or multi-agent scope was absorbed.
- Next step when resuming: select `c106` / EPIC-807 before implementing versioned agent definitions and capability envelopes.

### 2026-08-25 (EPIC-312 connection and MCP-server checkpoint)

- Did: added authenticated discovery and immutable connection-revision REST APIs; resolved credentials only through tenant-scoped secret bindings; verified live tool schemas before save and call; added an audience-bound workload-token verifier; and exposed read-only `list_workflows` and `inspect_execution` MCP tools with per-call authorization and no execution payload/state mutation.
- Verification: API denial/outage/tenant tests, protocol-level anonymous/authenticated MCP tests, schema-drift/dedup/restart/redaction task tests, a fresh migration-56 PostgreSQL repository test and generated-contract tests pass. A live bounded OpenRouter call passed against `openai/gpt-5.6-luna` with token/cost budget evidence.
- Next step when resuming: finish the how-to/reference docs and backlog evidence, run the complete affected-path gates, rebuild Compose and close `c105` only if the deployed smoke tests pass.

### 2026-08-25 (EPIC-312 bounded task checkpoint)

- Did: added the four provider-neutral model operations, explicit provider/budget/data-handling contracts, Draft 2020-12 output/tool validation, Luna/OpenRouter adapter, tenant-scoped MCP connection revisions, live schema pin checks, tool impact controls, redacted invocation provenance and duplicate/restart handling; registered the new task types in the resource catalog and immediate/recovery executors.
- Verification: focused domain, task, DSL and worker tests pass; Ruff and strict mypy pass for the changed task/runtime paths. The unrelated 5,000-line DSL p95 gate remains deferred on board card `c89` and was not changed.
- Next step when resuming: expose authenticated connection discovery/version APIs and mount the authorization-checked read-only AMESH MCP surface.

### 2026-08-25 (EPIC-312 start)

- Did: selected board card `c105`; verified the existing agent handler tests and live `/ready` endpoint; audited the current task, secret-resolution, resource-catalog, executor and MCP seams; recorded the bounded primitive boundary in `ARCHITECTURE.md`; and accepted ADR-050 to reuse locked HTTPX, jsonschema and MCP v2 libraries behind AMESH contracts without adding a dependency.
- Deviations from plan: none. This epic stops at bounded one-shot model/MCP primitives and an authenticated read-only AMESH MCP surface; autonomous sessions, memory and multi-agent routing remain out of scope.
- Next step when resuming: wire provider-neutral model operations and governed MCP calls to the invocation journal, then add connection APIs and the authenticated AMESH MCP server.

### 2026-08-25 (bounded-agent epic decomposition)

- Did: refined EPIC-312 into the bounded provider/model/MCP prerequisite; split the prior broad EPIC-806 requirements into EPIC-807 versioned agent definitions, EPIC-808 durable bounded single-agent sessions, EPIC-809 memory/evaluation/release gates and a narrowed EPIC-806 multi-agent topology layer; recorded ADR-049; regenerated canonical backlog, roadmap, URS, compatibility, traceability and GitHub-issue projections; and created board cards `c105`–`c109` with staged Definitions of Done.
- Verification: `uv run --extra runtime --extra dev python scripts/validate_backlog.py` reports 106 epics, 837 functional requirements, 63 non-functional requirements and 1,000 exact traceability links. The 900-requirement corpus is unchanged; URS-F-0806–0819 and agent NFRs were reassigned across the new durable boundaries.
- Deviations from plan: no runtime, dependency, UI, service or deployment change was made. The roadmap deliberately completes single-agent safety before multi-agent coordination and keeps all agent state inside the existing execution reducer.
- Next step when resuming: select `c105` and complete EPIC-312 before starting EPIC-807.

### 2026-08-24 (Sprint UX-01 complete)

- Did: completed cards `c102`, `c97`, `c98` and `c99` under sprint card `c104`; recorded ADR-048 and the input inventory; replaced constrained text fields with authorized selectors; made Mission Control the operational home; added prioritized Running now/Needs attention views; made the redacted ordered trace the execution default; preserved topology, Gantt, logs, data, history, analytics and YAML; and exported before/after/live visual evidence.
- Verification: 12 focused selector/Mission/trace model tests pass; the production frontend build passes; all 22 applicable Playwright tests pass with 24 intentional project skips; 19 populated after-state captures, five non-happy states and the authenticated live Mission Control/trace report zero critical/serious axe findings, console errors or failed API requests. The live Compose gate proves one running, 94 failed-recently and 105 completed-recently executions, and the rebuilt API is healthy at `http://localhost:8000`.
- Deviations from plan: no dependency or backend service was added. The 58-test complete frontend unit suite passes functionally but the command retains its pre-existing nonzero exit because global branch/function coverage is below 75%, already tracked on deferred card `c94`. Guided creation (`c100`) and production determinism qualification (`c101`) remain separate follow-ons.
- Next step when resuming: start guided workflow creation on `c100`; Sprint UX-01 itself has no remaining work.

### 2026-08-22 (50-epic local completion program, EPIC-220 completion)

- Did: completed EPIC-220 with literal argv and explicit single-string shell modes; working directory, bounded environment and standard input; POSIX UID and typed CPU/memory/file/open-file/process limits; live ordered severity-mapped stdout/stderr; POSIX process-group and Windows process-tree escalation; portable process-tree CPU/peak-memory sampling; signal evidence; and local-runner enablement that defaults off in multi-tenant mode. Linked URS-F-0258 through URS-F-0264 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 40 migrations; 339 tests existed, cards `c15`/`c29` were explicitly deselected, and the remaining 337 produced 329 passes, eight environment/platform skips and zero failures. Ruff and strict mypy passed for 128 source files; focused adapter/API/DSL/generated-contract, backlog, lock, compilation, Compose and diff gates passed. Linux container qualification applied UID 100/open-file limit 32, reported CPU/peak memory, captured SIGTERM 15 and removed a timed-out descendant. The rebuilt services are healthy at 40/40, and deployed execution `01a02a20-5039-71a2-b8f4-282a4cd5499e` completed shell/stdin execution with the enforced open-file limit, stderr and resource metrics.
- Deviations from plan: build-versus-buy selected cross-platform `psutil` 7.2.2 plus its development stubs, added with `uv`; no LLM call was required. One full-suite assertion caught an unnecessary rename of stable escalation labels, so the labels were restored without changing process-group behavior and the clean rerun passed. Deferred cards `c15`, `c29`, `c87` and `c88` remain untouched.
- Next step when resuming: close and commit card `c47`, then select EPIC-221 on card `c48` for the Docker and OCI task runner.

### 2026-08-22 (50-epic local completion program, EPIC-209 completion)

- Did: completed EPIC-209 with a versioned runner-neutral request/result contract; advertised local and Kubernetes capabilities; typed local/Kubernetes extensions; scoped credential, network and security policies; namespace/worker-group runner selection; pre-dispatch compatibility validation; normalized logs, metrics and diagnostics; cancellation/timeout escalation; and idempotent orphan reconciliation. Added the authorized runner-capability API and linked URS-F-0250 through URS-F-0257 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 40 migrations and the isolated complete backend suite collected 327 tests: 321 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff and strict mypy passed for 128 source files; focused runner/API tests, generated contracts/planning, backlog, clean-room, REUSE 6.2.0, uv lock, compilation, Compose and diff gates passed. The rebuilt API/executor/scheduler are healthy at 40/40. Live capability discovery returned both runners, and deployed execution `01a02a08-f238-70f1-972d-59f4a2f5cd53` proved task-level local selection over a Kubernetes execution fallback and completed with `RUNNER_LIVE_OK:66`.
- Deviations from plan: no dependency or LLM call was required. The first live flow exposed that the generated resource catalog did not yet admit the new task-runner fields; the catalog registry was minimally extended and the live rerun passed. Shared security/portability NFRs remain In Progress for their other owning epics, and deferred cards `c15`, `c29`, `c87` and `c88` remain untouched.
- Next step when resuming: close and commit card `c46`, then select EPIC-220 on card `c47` for the local process task runner.

### 2026-08-22 (50-epic local completion program, EPIC-208 completion)

- Did: completed EPIC-208 with unique disposable local directories per task attempt; post-expression internal input resolution with streamed checksum verification; atomic path/glob/JSON-manifest output collection; traversal, drive, symlink and cross-root confinement; a sequential `core.workingDirectory` flowable; guaranteed local cleanup with configured failure-diagnostic retention; total workspace quotas; logical path and ordered transformation lineage; and authorized execution-file list/download APIs. Linked URS-F-0242 through URS-F-0249 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 40 migrations and the isolated complete backend suite collected 320 tests: 312 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff and strict mypy passed for 127 source files; generated API/DSL/planning, backlog, clean-room, lock and diff gates passed. Real MinIO/API acceptance exercised namespace-file materialization, shared child execution, lineage listing and payload download. The rebuilt API/executor/scheduler are healthy at 40/40, and deployed execution `01a029e5-3d9b-75ca-a603-d664617e00a7` completed all three task runs successfully and streamed `result.txt` through the new API.
- Deviations from plan: no dependency or LLM call was required. Docker/OCI and Kubernetes workspace transfer remain with their already selected EPIC-221/222 runner owners; those modes reject this surface explicitly until implemented. The existing deferred cards `c15`, `c29`, `c87` and `c88` remain untouched.
- Next step when resuming: close and commit card `c45`, then select EPIC-209 on card `c46`.

### 2026-08-22 (50-epic local completion program, EPIC-207 completion)

- Did: completed EPIC-207 with inherited and versioned namespace files backed by object storage; child override and tombstone semantics; typed, expiring and compare-and-set key-value data; monotonic value-free change evidence; provider-reference-only secret bindings resolved at task runtime; independent list/read/write/delete/use authorization; value-free audits; checksum-protected import/export bundles; and matching API, CLI and control-room surfaces. Linked URS-F-0234 through URS-F-0241 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 39 migrations and the isolated complete backend suite collected 313 tests: 305 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff and strict mypy passed for 126 source files; 12 frontend unit tests, all eight applicable Playwright cases and the production build passed. The rebuilt API/executor/scheduler are healthy at 39/39. Live acceptance uploaded a file, stored a typed value and secret provider reference, exported a plaintext-free bundle and completed execution `01a029c2-458f-787f-a865-982c4fac3c07` with the value resolved and secret output redacted.
- Deviations from plan: no dependency or LLM call was required. A broad first suite run against the active Compose database was invalid because deployed services consumed shared state; the guarded disposable-database rerun passed without product changes. The existing seven frontend lint findings remain deferred on `c88`.
- Next step when resuming: close and commit card `c44`, then select EPIC-208 on card `c45`.

### 2026-08-22 (50-epic local completion program, EPIC-206 completion)

- Did: completed EPIC-206 with tenant-scoped namespace metadata; protected user/system labels on flows, executions, task runs, assets and backfills; exact plugin-type defaults; recursive forced/non-forced precedence; policy require/deny/normalize controls; immutable revision provenance; JSONB label indexes and dotted filters; authorized metadata APIs; and control-room label/effective-origin panels. Linked URS-F-0227 through URS-F-0233 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 38 migrations and the complete suite passed with 292 tests, six environment/profile skips and cards `c15`/`c29` explicitly deselected. Ruff and strict mypy passed for 123 source files; frontend 11-test coverage and production build passed. The rebuilt API/executor/scheduler are healthy at 38/38. Live acceptance configured parent namespace defaults, applied `metadata-demo`, exposed flow/default provenance and completed execution `01a0299b-bf76-7893-8366-f2920cc5b614` with protected execution/task labels.
- Deviations from plan: no dependency or LLM call was required. The first full run exposed a directly caused cache-key regression because unique system labels were included; cache derivation now uses user labels only and both restart/concurrency cache scenarios pass. The seven existing frontend lint errors remain deferred on `c88`.
- Next step when resuming: close and commit card `c43`, then select EPIC-207 on card `c44` for namespace files, key-value data and secrets.

### 2026-08-22 (50-epic local completion program, EPIC-205 completion)

- Did: completed EPIC-205 with one canonical DSL/API/UI input schema for string, integer/number, boolean, datetime, duration, enum, array, object, file and secret values; required/default/display/prefill/validation metadata; validation before runnable persistence across API, manual, trigger and subflow launches; object-storage file staging; typed terminal outputs; and schema-driven public redaction. Linked URS-F-0219 through URS-F-0226 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 37 migrations and the complete suite passed with 288 tests, six environment/profile skips and cards `c15`/`c29` explicitly deselected. Ruff and strict mypy passed for 122 source files; frontend 11-test coverage and production build passed. The rebuilt API/executor/scheduler are healthy at 37/37. Live API acceptance rejected plaintext secrets without creating rows, completed a valid file-backed execution and redacted sensitive values; headless Chromium rendered five generated input controls and the Run action.
- Deviations from plan: no dependency or LLM call was required. Legacy flows without declarations retain bounded ad-hoc input compatibility, and legacy `INT` normalizes to `integer`. Shared cross-product secret non-disclosure remains In Progress under URS-NFR-SECURITY-003; the existing `c87`/`c88` deferred items remain untouched.
- Next step when resuming: close and commit card `c42`, then select EPIC-206 on card `c43` for labels, metadata and plugin defaults.

### 2026-08-22 (50-epic local completion program, EPIC-205 start)

- Did: selected EPIC-205 on card `c42` and accepted a single canonical data-contract boundary over the existing Pydantic DSL, JSON Schema generator, expression engine and object-storage port. The boundary will own typed validation/defaults, form/API schema derivation, file staging, terminal flow-output rendering and schema-driven public redaction for API, manual, trigger and subflow launches.
- Deviations from plan: no dependency or LLM call is required. Secret inputs use durable `secret://` references so plaintext secret material never enters execution metadata or events; the existing static `variables` context remains separate from execution inputs and the mutable key-value service.
- Next step when resuming: implement the typed DSL/data-contract service and migration 0037, then wire every execution launch path and the control-room run form before fresh-database qualification.

### 2026-08-22 (50-epic local completion program, EPIC-204 completion)

- Did: completed EPIC-204 with durable MAIN/ERROR/FINALLY/AFTER_EXECUTION task phases; local and flow error ownership; bounded state/category/task/expression selectors; attempt-zero nonmatches; restart-safe lifecycle evidence; success, failure and cancellation cleanup; primary-failure preservation with separate cleanup failures; post-terminal context; recursive-handler rejection; and graph/control-room lifecycle metadata. Linked URS-F-0211 through URS-F-0218 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 36 migrations and the complete suite collected 291 tests: 283 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff, strict mypy, generated contracts/planning, backlog, clean-room, REUSE 6.2.0, uv lock, compilation, Compose and diff gates passed. Frontend unit tests and production build passed; unrelated lint debt was deferred to `c88`. The rebuilt API/executor/scheduler are healthy and `/ready` reports migration 36/36.
- Deviations from plan: no package or LLM call was required. Shared-database suite contamination from an earlier pre-migration run was isolated by rerunning on a disposable clean database. Fresh Compose initialization mounts and unrelated frontend payload stringification were recorded on `c87`/`c88` and left unchanged.
- Next step when resuming: close and commit card `c41`, then select EPIC-205 on card `c42` for typed inputs, outputs and variables.

### 2026-08-22 (50-epic local completion program, EPIC-204 start)

- Did: closed and committed EPIC-202 as `4b378f6`, selected EPIC-204 on card `c41`, and accepted ADR-034. Public behavior research confirmed that errors are failure-specific and may be flow/local-flowable scoped, finally runs cleanup before ordinary terminalization, and after-execution work observes an already terminal execution without replacing its state.
- Deviations from plan: no dependency is required. Lifecycle tasks will use ordinary durable task runs with phase metadata and structured execution lifecycle evidence; existing task handlers cover notification, compensation/subflow and diagnostic-artifact outputs. Nested lifecycle handlers will be rejected to bound recursion.
- Next step when resuming: extend the DSL/compiler and migration 0036, then implement restartable error/finally/after-execution reduction and graph visibility.

### 2026-08-22 (50-epic local completion program, EPIC-202 completion)

- Did: completed EPIC-202 with Kestra-shaped `core.if`/`core.switch` flowables; ordered else-if and predicate cases; explicit `FAIL`, `FALSE` and `FALLBACK` expression policies; restart-stable redacted decision evidence; attempt-zero non-selected skips; conditional retries; static duplicate/unreachable validation; additive migration 0035; ADR-033; example and operator documentation. Linked URS-F-0196 through URS-F-0202 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 35 migrations and the complete suite collected 288 tests: 280 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff passed for 639 files, strict mypy passed for 120 source files, and generated contracts/planning, backlog, clean-room, REUSE 6.2.0, lock, Compose and diff gates passed. The rebuilt Compose services are healthy at migration 35/35; live HTTP acceptance selected the expected else-if and predicate branches while non-selected descendants remained at attempt zero.
- Deviations from plan: no package or LLM call was required. Exact switch cases retain the Kestra-compatible `value`/`cases` surface; AMESH extensions add ordered `elseIf`/`predicateCases` and the explicit error policies. Error-hook execution and flow-output materialization remain with their queued EPIC-204/205 lifecycle owners.
- Next step when resuming: close and commit card `c40`, move EPIC-204 on card `c41` to Doing and implement errors, finally and after-execution hooks against URS-F-0211 through URS-F-0218.

### 2026-08-22 (50-epic local completion program, EPIC-006 completion)

- Did: completed EPIC-006 with immutable semantic revision allocation that preserves explicit forward revisions and auto-advances conflicting changes; authorized history, unified/RFC 6902-compatible diff, lifecycle and restore APIs; actor/source/commit/environment/deployment provenance; pinned resource-catalog resolution; execution foreign-key pinning; reference-aware deletion; and tenant-isolated audit/event/outbox evidence through migrations 0033–0034. Linked URS-F-0045 through URS-F-0051 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 34 migrations and the complete suite collected 282 tests: 274 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff passed for 637 files, strict mypy passed for 120 source files, and generated contract/planning, backlog, clean-room, REUSE 6.2.0, lock, Compose and diff gates passed. The rebuilt Compose API/executor/scheduler are healthy at migration 34/34; live acceptance created revisions 100/101, returned two diff operations, disabled revision 101 and restored revision 100.
- Deviations from plan: no package or LLM call was required. Compatibility tests established that an unused explicit forward revision must be retained, while changed content colliding with existing history receives `max + 1`. Revision-event outbox records now follow explicit flow purge through migration 0034.
- Next step when resuming: EPIC-202 is selected on card `c40`; implement conditional branching and switch semantics against URS-F-0196 through URS-F-0202.

### 2026-08-22 (50-epic local completion program, EPIC-003 start)

- Did: selected EPIC-003 on card `c38`; retained pinned Pydantic Settings and PyYAML after build-versus-buy review; accepted ADR-031; implemented ordered file/environment/CLI loading, `secret://` references, secret-free validation errors and structured-log redaction, explicit reloadable metadata, atomic reload rejection, renamed-setting migration and the namespace-over-tenant-over-instance feature-flag contract. Added additive migration 0032 and the PostgreSQL repository boundary.
- Verification: ten focused configuration and feature-flag domain tests pass; Ruff and strict mypy pass for the new core modules.
- Deviations from plan: no new dependency was added. The OpenFeature provider/evaluation shape informed the decision evidence, but its SDK would not supply AMESH's PostgreSQL scope, authorization or audit semantics.
- Next step when resuming: qualify migration 0032 and tenant RLS, then expose authorized configuration, diagnostic, reload and flag APIs.

### 2026-08-22 (50-epic local completion program, EPIC-003 completion)

- Did: completed EPIC-003 with typed source snapshots and provenance; YAML/JSON, environment, CLI and secret-reference precedence; safe deprecation migration; production configuration gates; active-secret API/log/diagnostic redaction; atomic reload; authorized configuration APIs; and audited versioned PostgreSQL instance/tenant/namespace feature flags through migration 0032. Linked URS-F-0022 through URS-F-0028 to evidence.
- Verification: 281 tests collected; 273 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Seventeen focused tests, Ruff, strict mypy, generated contracts/planning, migration, backlog and clean-room gates passed. The rebuilt Compose API/executor/scheduler are healthy at migration 32/32, and deployed HTTP acceptance passed configuration, reload, scoped evaluation and diagnostic-bundle checks.
- Deviations from plan: the first full run's two failures were direct migration-version expectations; updating the owning assertion and applying migration 0032 to the deployed database resolved both. No LLM call or new package was required.
- Next step when resuming: close and commit card `c38`, then select EPIC-006 on card `c39` for flow revisions, change history and promotion.

### 2026-08-22 (50-epic local completion program, EPIC-000 completion)

- Did: completed EPIC-000 with a generated 837-item compatibility inventory, machine-readable public-source provenance and strict clean-room role handoffs, pinned-target validation, release-blocking REUSE 6.2.0 licensing, isolated one-way token-shingle similarity scanning, trademark/contribution policy and a repeatable target-rebase guide. Linked URS-F-0001 through URS-F-0007 to evidence.
- Verification: 272 tests collected against an isolated PostgreSQL database; 264 passed, six environment/profile tests skipped and the two pre-existing card `c15`/`c29` assertions were explicitly deselected. A fresh database applied all 31 migrations. REUSE, Ruff, strict mypy, workflow YAML, package-script syntax, clean-room, planning regeneration, backlog and diff gates passed.
- Deviations from plan: no runtime or LLM change was needed. The first shared-database run was invalid because deployed services consumed test work; the isolated rerun passed without code changes. The configured OpenRouter `openai/gpt-5.6-luna` default is unchanged.
- Next step when resuming: close and commit card `c37`, then select EPIC-003 on card `c38` and implement the typed configuration/feature-flag system.

### 2026-08-21

- Did: fast-forwarded the accepted Python MVP rescope onto `main`; implemented and verified the PostgreSQL durable queue, transactional outbox publisher and consumer inbox; added a live OpenRouter contract test with GPT-5.6 Luna as the default model; established the root architecture and cold-resume tracker; closed W1; implemented persisted execution/task/attempt state and restartable DAG scheduling; closed W2; implemented the runner port, local-process adapter, persisted retry scheduling, timeout/cancellation escalation and stale-attempt fencing; closed W3; implemented timezone-aware cron calculation, transactional occurrence deduplication, sandboxed native expressions, output interpolation and `runIf`; closed W4; implemented the Kubernetes Job adapter and verified pod-deletion reconciliation on kind; closed W5; implemented `core.http`, OpenAI-compatible `agent.llm`, official-SDK `agent.mcp`, authenticated REST and matching CLI surfaces; ran the checked-in Luna → Kubernetes shell → HTTP demo through the API; closed W6; added the uv-locked non-root image, external-PostgreSQL Helm migration hook, server/recovery-worker deployments, RBAC, JSON logs and Prometheus endpoint; installed on a fresh kind cluster and ran the demo through the installed Service; closed W7; reconciled evidence-linked progress into all affected epic files through the canonical planning generator.
- W8 checkpoint: candidate `amesh:mvp-w8f` passed 47 tests at 80.47% branch coverage plus artifact, Helm, policy and exact-image cron/log checks. The owner-accepted soak reached cycle 270 with 270 independently re-read, unique single-attempt successes after 270 task-pod kills, 27 server-pod kills and 13 worker-pod kills; both replacement Deployments were Ready with zero restarts. The two-second soak-only recovery grace intentionally produced fenced losing contenders while preserving exactly-once persisted completion.
- Deviations from plan: on 2026-08-21 the product owner deferred the remaining uninterrupted 24-hour soak and authorized release progression. The full-duration criterion is preserved under EPIC-611 and no broader production-readiness claim is made. The W7 worker remains a deliberately single-tenant delayed recovery loop; general distributed dispatch and HA remain deferred.
- Next step when resuming: continue the dependency-ordered backlog; run EPIC-611's uninterrupted 86,400-second qualification before making broader availability, scale or production-readiness claims. The path-back audit left all 900 broad roadmap requirements `Proposed` because the MVP slices do not satisfy their complete acceptance criteria.

### 2026-08-21 (post-MVP roadmap session 1)

- Did: accepted the five requested roadmap areas; registered the repository with the Agent Hotel daemon; made its board the primary execution tracker; selected dependency-free EPIC-002 as the first card; verified the existing tests; mapped direct dependency chains; researched UUIDv7 and canonical serialization choices.
- Deviations from plan: the finished MVP plan was superseded by the requested roadmap-completion goal. No product code has changed yet.
- Next step when resuming: implement and verify EPIC-002 against card `c1`, update its canonical backlog evidence, and only then select the next dependency-ready epic.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-002 completion)

- Did: added canonical natural-key models; adopted UUIDv7 through the uv-locked `uuid6` package; switched new execution, task-run, attempt, revision, event and worker IDs to UUIDv7; added shared metadata, lifecycle, canonical hash and ETag contracts; persisted managed-resource metadata through migration 0003; exposed flow ETags and REST `If-Match`; regenerated contracts; linked all seven EPIC-002 requirements to evidence.
- Verification: 53 tests passed with real PostgreSQL at 76.11% branch coverage; clean-database migrations 0001–0003 passed; focused ETag and UUIDv7 persistence tests passed; Ruff and strict mypy passed.
- Deviations from plan: the existing Compose database required its already-applied 0001/0002 checksums registered before migration 0003; no schema or product data was reset. The worker software-version column required the new concurrency field to be named `resource_version`.
- Next step when resuming: select EPIC-500 as the next dependency-ready requested epic and begin its architecture-first RBAC design.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-500 completion)

- Did: closed EPIC-002 on card `c1` and committed it as `b9c7eb5`; selected and completed EPIC-500 on card `c2`; accepted ADR-018; added PostgreSQL-authoritative principals, groups, roles, permissions, scoped bindings and namespace boundaries; implemented deny-overrides evaluation, policy-version cache invalidation, group and binding revocation, administrator explanations, built-in roles and effective last-admin protection; applied server-side authorization to every resource API; added tenant-aware CLI requests, shared non-human actor contracts, audit writes, migration 0004 and the administration runbook; linked all eight functional requirements to evidence.
- Verification: 68 tests passed with real PostgreSQL at 78.54% branch coverage; clean-database migrations 0001–0004 passed; every current endpoint has public-or-protected acceptance evidence; Ruff, strict mypy, lock, generated contract/planning, backlog, clean-room, compile, build, Compose, Helm and diff gates passed. The pure evaluator measured 1.64 microseconds per decision over 100,000 local calls without making a distributed throughput claim.
- Deviations from plan: no authorization dependency was added because the evaluated libraries do not replace AMESH-specific persistence, evidence, invalidation and administrator-safety rules; Oso Cloud would also introduce a second external authority. Shared `URS-NFR-USABILITY-002` is `In Progress`: EPIC-500's authorization evidence is complete, while its admission/cache/UI owners remain open.
- Next step when resuming: close board card `c2`, commit EPIC-500, select dependency-ready EPIC-501 and implement durable service-account/API-token credentials before the login/session epic.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-501 start)

- Did: closed and committed EPIC-500 as `8a4b227`; selected EPIC-501 on card `c3`; reviewed Python `secrets`/HMAC, RFC 6750 bearer-token guidance and self-contained token tradeoffs; accepted ADR-019 for 256-bit opaque bearer tokens whose HMAC digests, revocation state, scopes, audiences, expiry, usage and quotas remain PostgreSQL-authoritative.
- Deviations from plan: no credential dependency was added. Self-contained JWT/PASETO tokens would still require authoritative revocation, quota and last-used state, while password hashing is unnecessary for server-generated 256-bit secrets.
- Next step when resuming: implement token/scope domain contracts, migration 0005, the credential repository/service and durable bearer authentication entry point.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-501 completion)

- Did: completed EPIC-501 with PostgreSQL-authoritative service/workload credentials; one-time 256-bit opaque token disclosure; keyed digests; scope/audience/expiry/last-use metadata; independent quotas; bounded rotation overlap; current/previous pepper rollout; immediate token, derived-child and principal-epoch revocation; worker/plugin exchange; production durable bearer authentication; failure/success auditing without plaintext; migration 0005; Helm Secret wiring; ADR-019; API contract and runbook updates; and evidence links for URS-F-0502 through URS-F-0509.
- Verification: 76 tests passed with real PostgreSQL at 79.14% branch coverage; a clean database applied migrations 0001–0005; Ruff, strict mypy, lock, generated OpenAPI/planning, backlog, clean-room, compile, Compose and Helm gates passed. Shared `URS-NFR-SECURITY-002` and `URS-NFR-SECURITY-006` are `In Progress` because their other owning epics remain open.
- Next step when resuming: close board card `c3`, commit EPIC-501, and select the next dependency-ready requested epic.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-503 start)

- Did: closed EPIC-501 as `df29a1a`; selected dependency-ready EPIC-503 on card `c4`; compared application filters, shared-schema PostgreSQL RLS and database-per-tenant approaches; accepted ADR-020 for explicit request context plus transaction-local `amesh_runtime` RLS enforcement.
- Deviations from plan: no tenancy dependency was added. The required lifecycle, policy and repository contracts are AMESH-specific, while PostgreSQL already provides the database isolation primitive.
- Next step when resuming: implement tenant domain contracts, migration 0006, the tenant administration repository/API and tenant-scoped runtime transactions.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-503 completion)

- Did: completed EPIC-503 with explicit multi-tenant request context; tenant lifecycle, policy, export and administration APIs; PostgreSQL forced RLS through non-bypass runtime/administration roles and restricted resolver functions; tenant-scoped execution and durable transport; tenant-specific queue notifications; execution/plugin/feature quotas; worker-group routing; immutable storage prefixes; separately audited super-administration; Helm settings; ADR-020; migrations 0006–0009; and the multi-tenancy runbook. Linked URS-F-0518 through URS-F-0525 to automated evidence.
- Verification: 82 tests passed with real PostgreSQL at 79.65% branch coverage; a clean database applied migrations 0001–0009 and exposed 18 tenant-isolation policies; a non-superuser/non-owner tenant-repository login test passed; Ruff, strict mypy, lock, generated contract/planning, backlog, clean-room, compile, build, Compose and Helm gates passed.
- Deviations from plan: shared URS-NFR-SECURITY-001 remains In Progress because EPIC-604/605 and the independent pre-GA penetration test remain open. No tenancy dependency was added; PostgreSQL RLS and typed AMESH contracts provide the required boundary.
- Next step when resuming: close and commit card `c4`, then select the next dependency-ready epic from the remaining requested frontend, compatibility, login, orchestration-control and HA/DR areas.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-004 start)

- Did: closed EPIC-503 on card `c4` and committed it as `1b35594`; selected dependency-ready EPIC-004 on card `c5`; compared PyYAML source-mark patching, a new parser and `ruamel.yaml` round-trip parsing; accepted ADR-021 for a versioned Pydantic canonical IR, round-trip YAML source tree and Draft 2020-12 resource-schema registry.
- Deviations from plan: this epic adds `ruamel.yaml` and `jsonschema` because comment-preserving edits and standards-complete plugin schema validation are established library responsibilities.
- Next step when resuming: implement the editable document, source-range mapper, resource registry and versioned validation result before extending generated contracts.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-004 completion)

- Did: completed EPIC-004 with YAML 1.2/JSON parsing into `amesh.flow/v1`; comment-preserving programmatic edits; common, reference, cycle and installed-resource validation; source ranges and remediation hints; `x-` extension policy; deterministic semantic hashes; Draft 2020-12 resource schemas/editor metadata; generated contract artifacts; ADR-021 and the flow DSL guide. Linked URS-F-0029 through URS-F-0036 to evidence.
- Verification: 91 tests passed with real PostgreSQL at 80.29% branch coverage; generated flow/resource/OpenAPI contracts matched; a 5,003-line flow measured 0.598 seconds p95 over 10 uninstrumented runs; Ruff, strict mypy and focused API/DSL checks passed.
- Deviations from plan: shared URS-NFR-USABILITY-001 remains In Progress for EPIC-405 editor integration, and URS-NFR-MAINTAINABILITY-002 remains In Progress for EPIC-300/400/610. `ruamel.yaml`, `jsonschema` and the latter's type stubs were added through `uv` after the build-vs-buy review.
- Next step when resuming: close and commit card `c5`, then select dependency-ready EPIC-005 to complete the requested Pebble-compatible expression layer.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-005 start)

- Did: closed EPIC-004 on card `c5` and committed it as `0f6e2f2`; selected dependency-ready EPIC-005 on card `c6`; compared a JVM Pebble boundary, an unavailable maintained Python Pebble port and a versioned compatibility facade over the existing Jinja sandbox; accepted ADR-022 for the explicit `kestra-pebble/1.3.30-subset-1` adapter.
- Deviations from plan: no expression dependency was added. The existing Jinja native sandbox supplies the maintained parser/evaluator primitive; AMESH owns only the bounded compatibility, context and redaction contracts.
- Next step when resuming: implement the engine protocol, typed contexts, selected filters/functions, compile/runtime errors and resource limits before wiring the executor context.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-005 completion)

- Did: completed EPIC-005 with the storage-independent `ExpressionEngine`; typed execution contexts; versioned `kestra-pebble/1.3.30-subset-1` syntax, filters, functions and fixture corpus; immutable sandbox; separate compile/render failures; deterministic template, AST, context, collection, nesting, recursion, output and elapsed-time limits; and secret-aware previews, errors, representations and core logs. Linked URS-F-0037 through URS-F-0044 to evidence.
- Verification: 104 tests passed with real PostgreSQL at 80.05% branch coverage; the 12-case compatibility corpus and executor context integration passed; a representative render measured 0.2324 ms p95 over 1,000 warmed runs; Ruff, strict mypy, backlog, clean-room, compilation and generated-contract gates passed.
- Deviations from plan: no new expression dependency was needed. Compatibility remains explicitly bounded to the published subset; effectful Kestra functions stay with their owning capability epics.
- Next step when resuming: close and commit card `c6`, then select the next dependency-ready epic from the requested graphical frontend, orchestration control and HA/DR areas.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-404 start)

- Did: closed EPIC-005 as `43f095e`; briefly selected EPIC-400, then returned it to To-Do because its full resource surface depends on unfinished backfill, file, key-value and plugin owners and the user directed work to defer blockers and move forward; selected EPIC-404 on card `c8`. Researched the current React ecosystem and accepted ADR-023 for a Vite React SPA, React Router, TanStack Query, i18next, cmdk, AMESH-owned token CSS, Vitest and Playwright/axe.
- Design: established `frontend/DESIGN.md` with a graphite-control-room direction, offline bundled typography, high-contrast signal palette, 44 px controls, keyboard focus, dense operational data surfaces and desktop/tablet/phone layouts before writing components.
- Direct blocker fixed: fresh Docker Compose databases now apply migration 0010, which the completed trigger-context runtime requires.
- Next step when resuming: scaffold the isolated frontend workspace with exact locked packages, implement the shell and server-authoritative session capability endpoint, then test its loading, error, empty, responsive, keyboard, localization and offline states.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-404 completion)

- Did: completed EPIC-404 with a React/Vite control room; AMESH-owned graphite design system; dashboard, flow, execution and execution-detail views; reserved navigation for later product areas; server-authoritative capability rendering; tenant/namespace context; saved views; deep-link fallback; global live-resource command search; notifications; recovery states; bundled typography; English/Simplified Chinese locale and time-zone formatting; telemetry-off deployment policy; FastAPI static serving; and a Node-to-uv container build. Linked URS-F-0430 through URS-F-0437 to evidence and documented the browser/accessibility qualification boundary.
- Verification: 107 Python tests passed with four environment-gated skips against PostgreSQL; eight frontend unit tests passed at 100% isolated-unit coverage; five desktop/tablet browser acceptance cases passed with axe reporting no critical/serious findings and only the local app origin observed; ESLint, TypeScript/Vite, Ruff, strict mypy, uv lock, generated contracts/planning, backlog, clean-room, compilation, Compose, Docker image and diff gates passed.
- Deviations from plan: EPIC-400 remains To-Do because its full API surface depends on unfinished resource owners, but the existing versioned `/api/v1` flow/execution/authorization slice satisfied EPIC-404. Shared URS-NFR-USABILITY-004 and URS-NFR-PRIVACY-001 remain In Progress for their other owners and the pre-GA cross-browser/screen-reader matrix.
- Next step when resuming: close and commit card `c8`, then select the next dependency-ready epic from the remaining login, orchestration-control and HA/DR areas.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-007 completion)

- Did: selected dependency-ready EPIC-007 after deferring the EPIC-403/EPIC-502 circular dependency; added immutable typed/versioned execution and task-run command, event, snapshot, transition and rejection contracts; pure lifecycle reducers; stable idempotency; replay and execution-v1 upcasting; PostgreSQL task history and rejection evidence; schema-v2 execution metadata; and same-transaction event-to-outbox triggers. Updated generated schemas, migration documentation, execution semantics and canonical requirement evidence.
- Verified: 118 Python/PostgreSQL tests pass with four environment-gated skips at 80.89% branch coverage; a fresh database applies all 11 migrations and exposes forced RLS plus both outbox triggers; 100 repeated replays are byte-equivalent; duplicate task results have one logical effect; stale execution/task transitions preserve state and record evidence; forced rollback leaves neither event nor outbox row. Ruff, strict mypy, uv lock, planning/contracts, backlog, clean-room, compile, Compose and diff gates pass.
- Deviations from plan: the live OpenRouter smoke remains environment-gated because `OPENROUTER_API_KEY` is absent; its checked-in default remains `openai/gpt-5.6-luna`. Helm was not rerun because the Helm executable is absent and EPIC-007 changes no chart template; the fresh migration and Compose configuration were verified directly. Shared reliability and maintainability NFRs remain In Progress for EPIC-008/009/100/103/108 and distributed failover qualification.
- Next step when resuming: close EPIC-007 and select the next dependency-ready backlog epic in the loops/subflows/backfill/recovery chain.

### 2026-08-22 (post-MVP requested-area completion, EPIC-403)

- Did: completed the last uncovered requested capability with one-time local administrator bootstrap, Argon2id local passwords, a provider-neutral authentication registry, opaque PostgreSQL-authoritative browser sessions, production secure-cookie/CSRF policy, expiry and rotation, lockout/rate limiting, logout/global revocation/password rotation, secret-free audit/metrics, RBAC-protected multi-user administration, federated-only policy and the graphical local-account login gate. Applied migration 0027 to the development database and linked URS-F-0422 through URS-F-0429 to evidence.
- Verification: four authentication API/CLI tests passed against disposable PostgreSQL databases; the compiled React UI completed a real headless-browser login through a live AMESH server; frontend lint, ten unit tests, production build and five applicable Playwright shell cases passed; all non-deferred backend tests passed on a clean 27-migration database; Ruff formatting/lint, strict mypy, uv lock, generated OpenAPI/planning, backlog validation, Compose, Helm production/development profiles and the production Docker image passed.
- Deviations from plan: the EPIC-403/EPIC-502 cycle was corrected so EPIC-403 owns local login plus the provider boundary and EPIC-502 owns concrete federation. The unrelated EPIC-104 deadline timing assertion and metric-registration test-order dependency were not changed and remain recorded on cards `c15` and `c29`.
- Next step when resuming: select a new explicitly requested backlog item; the five areas in this execution goal are complete within their published qualification boundaries.

### 2026-08-22 (local deployment handoff)

- Did: deployed the committed API and compiled control-room frontend through Docker Compose without replacing the PostgreSQL or MinIO volumes; bootstrapped the first local administrator; and fixed the runtime wheel package-data declaration that had omitted `amesh/web` from `site-packages`.
- Verification: Compose reported healthy API/PostgreSQL services; `/ready` reported 27 of 27 migrations; `/` returned the compiled HTML; API and headless-Chromium login reached the expected administrator session and Dashboard; HttpOnly session, CSRF and logout checks passed.
- Next step when resuming: leave the local stack running for user testing at `http://localhost:8000`.

### 2026-08-22 (deployed Flows view repair)

- Did: reproduced the reported recovery view as an HTTP 500 from `/api/v1/flows`; traced it to one valid persisted flow whose concurrent transaction timestamps differed by 536 microseconds; normalized the timestamp at the PostgreSQL adapter boundary without weakening the domain metadata invariant; added a regression test; and rebuilt the running API image.
- Verification: the regression failed on the original Pydantic validation error and passed after the fix; Ruff and strict mypy passed; a fresh Chromium session against Compose signed in, rendered Dashboard metrics, opened the 863-flow catalog, and observed HTTP 200 from both flow and execution queries with no recovery view.
- Next step when resuming: leave the repaired stack running for user testing at `http://localhost:8000`.

### 2026-08-22 (50-epic local completion program start)

- Did: classified all 70 open canonical epics by full Definition of Done; excluded 20 with non-local qualification gates; registered the remaining 50 as authoritative Agent Hotel cards `c37`–`c86`; and selected dependency-free EPIC-000 as the first milestone.
- Deviations from plan: the prior five-area scope is superseded by the product owner's explicit 50-epic local completion goal. External prerequisite epics remain open; only their smallest locally testable contract may be implemented when it directly blocks a selected epic.
- Next step when resuming: complete EPIC-000 requirements URS-F-0001 through URS-F-0007, verify its clean-room governance gates and evidence, deploy any affected service, update the canonical backlog and move card `c37` to Done.

### 2026-08-26 (ordered agent-product sprint, EPIC-823 completion)

- Did: completed the generic document and artifact pipeline with exact tenant-scoped artifact references, the provider-neutral `amesh.document-extractor/v1` contract, an exactly pinned `pypdf==6.16.1` reference plugin, bounded child-process parsing, immutable source/parser lineage, typed downstream results, guided PDF selection and an execution result inspector.
- Verification: 27 consolidated Python contract/API/PostgreSQL/MinIO/integration tests, Ruff, strict mypy, 41 focused frontend assertions, scoped ESLint, the production build, six responsive fixture journeys and one deployed Chromium journey passed. Compose remained ready at migration 66/66; live execution `01a03e31-1a44-70f0-92b9-e1d8095ac1fa` completed `SUCCESS` and persisted `document-result.json`.
- Next step when resuming: implement EPIC-824's versioned harness conformance kit, deterministic machine report, authority-isolation failure matrix and explicit fail-closed adapter composition.

### 2026-08-26 (ordered agent-product sprint, EPIC-824 completion)

- Did: completed the versioned agent-harness conformance and portability boundary. Pi 0.84.3 now runs behind an explicit fail-closed registry and versioned bounded-frame protocol; AMESH owns the only model gateway, tool dispatch, credentials, workflow state, budgets and output acceptance. Added a documented adapter port/template, deterministic machine report, exact dependency/license provenance, two-run CI comparison and production-image probe.
- Verification: the complete 23-case provider-free kit passed twice with byte-identical reports and digest `sha256:b1b26b67b6b6793738f5f612320de8873beb719acb65ea62f22dced644e29022`; focused Python, Node, Ruff and strict-mypy gates passed with only the opt-in live-provider test skipped. OpenAPI and all four generated SDKs were refreshed deterministically and passed Python, TypeScript, Java and Go builds/tests. The rebuilt image passed the real Pi probe, Compose reported migration 66/66 ready, and live execution `01a03e4e-6ffc-74a8-b044-980bdc87dae9` completed `SUCCESS` with two `openai/gpt-5.6-luna` sessions through `pi-agent-core` 0.84.3 plus token, cost and prompt-cache evidence.
- Next step when resuming: the ordered EPIC-819 through EPIC-824 sprint is complete; use the single MVP pull request as the review and merge boundary.

### 2026-08-30 (EPIC-827 administration and portability, M1 completion)

- Did: registered EPIC-827 and its six milestones on the authoritative board; accepted ADR-067
  separating the application session data plane, session administration plane and canonical runtime
  authorities; added session-specific resources and the `session-client`, `session-operator` and
  `session-admin` roles; migrated data-plane create/read/control authorization with a bounded legacy
  execution-permission upgrade bridge; and added migration 0069 with the role grants and fleet query
  indexes.
- Verification: 48 focused authorization/API/manifest tests passed, plus an isolated PostgreSQL
  migration test proving all three roles and both indexes exist. The explicit-deny adversarial case,
  namespace-before-stream boundary, Ruff, application import and diff checks passed.
- Next step when resuming: card c145 is Doing; finish the cursor-paginated session fleet and separate
  administration API, including owner/harness filters, safe instance aggregates, usage/cost and
  dependency posture, before moving to the administration UI.

### 2026-08-30 (EPIC-827 administration and portability, M2 completion)

- Did: added a separately authorized tenant fleet projection over canonical executions and latest
  agent-session attempts, tenant/filter-bound keyset cursors, owner/agent/harness/state/time filters,
  bounded usage/cost/dependency aggregates and a metadata-only instance overview with explicit
  tenant drill-down.
- Verification: eight API and PostgreSQL tests passed on a fresh isolated database, including cursor
  traversal, filter binding and cross-tenant isolation. Ruff, diff checks and deterministic OpenAPI
  generation for Python, TypeScript, Java and Go passed.
- Next step when resuming: card c146 owns the dedicated responsive session administration workbench,
  trace drill-down and guarded individual/bulk lifecycle controls.

### 2026-08-30 (EPIC-827 administration and portability, M3 completion)

- Did: added the dedicated Session Orchestrator administration workbench with fleet and capacity
  summary, structured filters, cursor traversal, canonical trace drill-down, separately authorized
  instance pulse and individually fenced lifecycle controls. Added a bounded 25-session bulk command
  contract with exact confirmation and independent per-item results over the existing execution
  control authority.
- Verification: five focused bulk API tests and 32 focused frontend assertions passed. Changed-file
  ESLint, the production Vite build and four responsive Chromium/tablet Playwright cases with axe
  passed; the durable workbench screenshot was refreshed.
- Next step when resuming: card c147 owns versioned tenant/namespace/application policy governance,
  effective provenance, admission/capacity enforcement and retention integration.

### 2026-08-30 (EPIC-827 administration and portability, M4 completion)

- Did: added immutable tenant/namespace/application session policies with cumulative launch-time
  admission, quota and dependency enforcement; authenticated application identity binding; canonical
  policy provenance; optimistic mutation/audit; and a separately gated policy workbench. Integrated
  terminal-session expiry into the existing previewed, legal-hold-aware lifecycle purge authority.
- Verification: 54 focused backend/API/PostgreSQL tests and 35 frontend assertions passed, together
  with Ruff, strict mypy, changed-file ESLint, the production build and responsive Chromium/tablet
  Playwright/axe journeys.
- Next step when resuming: card c148 owns digest-protected profile transfer and checkpoint-safe,
  idempotent canonical session migration with compatibility planning and UI.

### 2026-08-30 (EPIC-827 administration and portability, M5 completion)

- Did: added digest-protected profile export/import and compatibility planning; terminal/clean-
  checkpoint session transfer with canonical record, pin, cursor, evidence and artifact preservation;
  deterministic tenant-local ID remapping; strict migration RBAC; idempotent import receipts; and a
  plan-first portability workbench using JSON files and stable credential acknowledgements.
- Verification: 20 focused Python/API/PostgreSQL tests and 36 frontend assertions passed, including
  secret exclusion, ambiguous-effect rejection, injected rollback, duplicate replay and an artifact-
  bearing round trip. Ruff, strict mypy, changed-file ESLint, the production build, generated OpenAPI/
  four-SDK drift across 3,077 files and Chromium/tablet Playwright/axe journeys passed.
- Next step when resuming: card c149 owns the self-hosted Docker/Helm session-orchestrator profile,
  verified readiness and the coordinated whole-cluster migration/cutover qualification boundary.

### 2026-08-30 (EPIC-827 administration and portability, M6 and epic completion)

- Did: added a separately deployable, loopback-only Docker Compose and Helm session-orchestrator
  profile for the webserver, executor and scheduler over external PostgreSQL and S3-compatible
  storage. The profile uses file-backed or existing-secret credentials, hardened preflight and
  role-aware health without a Docker socket, Docker runner, broker credential or model-provider key.
  Added the operator deployment guide and the coordinated admission-drain, database/object recovery-
  point, secret-rebind, compatibility, cutover and rollback runbook; selective moves use the M5
  portability workbench.
- Verification: a fresh-image isolated smoke applied all 71 migrations and reported preflight, API,
  executor, scheduler, PostgreSQL and object storage ready. Five deployment tests, Compose rendering,
  Helm lint, focused Ruff/strict-mypy, 107 aggregate EPIC backend/API/PostgreSQL tests, 39 focused
  frontend assertions, production build and Chromium/tablet Playwright journeys passed. The complete
  Docker-local push gate passed 786 backend tests, 109 frontend tests, both Chromium agent-session
  journeys, the 23-case Pi conformance kit twice, generated contracts, backlog/license/review gates,
  the production-image probe and repository/four-SDK packaging. The opt-in OpenRouter
  `openai/gpt-5.6-luna` session smoke passed separately.
- Scope boundary: multi-region operation, arbitrary external-dependency recovery and production-HA
  qualification remain explicit non-claims. EPIC-827 is complete; no successor work was started.

### 2026-08-31 (GitHub issues #4–#7 and EPIC-831 completion)

- Did: revalidated every open GitHub issue against current source and tests. Issue #5's governed
  multimodal path was already present in EPIC-828 and received its missing live qualification.
  Implemented bounded repair for provider-side action-schema rejection (#4), allowlisted durable
  OpenAI-compatible provider diagnostics (#6), and the versioned required ordered tool-plan API,
  DSL, checkpoint ledger, exact pre-I/O dispatch gate, early-final repair gate and safe evidence
  contract in EPIC-831 (#7). OpenAPI and Python, TypeScript, Java and Go SDKs are current.
- Verification: 158 focused provider-free tests passed with two expected environment skips. Ruff,
  formatting, strict mypy, generated-contract/SDK drift, backlog validation and strict documentation
  passed. The complete Docker-local gate passed 892 backend tests, 120 frontend tests, two application
  and eight documentation Playwright journeys, 25 Pi conformance cases, production-image probing and
  release packaging. The opt-in `openai/gpt-5.6-luna` Pi run passed with real governed PNG pixels,
  structured output, 352 reported tokens, billed cost, cache telemetry, safe chronological progress
  and terminal-result restart reuse.
- Scope boundary: no unrelated open issue, deferred board card or adjacent warning was changed.
  Cards c160–c162 are ready to close with the publishing PR.
