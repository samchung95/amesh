# Project: AMESH — roadmap completion

## Goal

Implement GitHub #93 through Agent Hotel c246 (contract), c247 (session enforcement)
and c248 (public contracts and qualification). Tools may satisfy explicit structured-result
conditions in any order, using generated/corrected arguments, before the same executing
agent session may complete. Preserve ordered plans, existing authorization and invocation
journals, bounded repair and recovery behavior.

The user authorized implementation, refreshed documentation, pushing a PR and merging this
three-ticket batch. Baseline main is `45a741356ee5d6c02c7ea8d4f951cce49c7447e3` (PR #92).
The Agent Hotel daemon board remains authoritative; c245 is the existing parent.
ADR-069 records the extension and compatibility decision. No new dependency or migration.

## Out of scope

External-cloud, external-SaaS, hosted-release, independent-certification, multi-region and long-duration qualification gates are deferred for EPIC-001, 011, 223, 308–311, 506, 606, 611–612, 700, 705–706, 801 and 803–805. EPIC-815 qualifies only its checked-in hardened local profile and does not close those broader production gates. Client-specific adapters, workflows, domain tools, parity decisions and cutover remain outside AMESH and belong in each client repository. DSH and Goose production adapters, hot-swapping a harness during an active session, EPIC-104, opportunistic refactors, adjacent defects, cards `c15`/`c29` and broader production claims remain excluded. GitHub-hosted CI/CD, GitHub release publication and hosted provenance attestation are intentionally absent until the product owner reauthorizes them.

## Open questions

None for this batch. Consumer deployment/cutover, paid-provider qualification and AURA's
manual attached-browser acceptance remain separate from implementing and merging #93.

## Decisions log

- 2026-09-09 — Extend the existing required-tool plan with opt-in unordered result conditions;
  reuse JSON Schema and the session journal. Preserve legacy ordered digest encoding and bind
  accepted evidence to the executing session record. See ADR-069 and c246–c248.

- 2026-09-06 — Implement the approved #77 stable-envelope finding as opt-in `NATIVE_V3`:
  identical tools/business schema across phases, controller-owned dispatch and strict final
  validation, unchanged V1/V2 checkpoints. Qualify paired real-harness evidence before fresh
  Vibe acceptance and Fable sign-off; no broker actions or unrelated improvements.
- 2026-08-19 — Keep Kubernetes in the MVP twice (runs on K8s via Helm; runs tasks as K8s Jobs); defer the standalone Docker runner (EPIC-221) to pay for it — user requirement; Docker runner duplicates ~70% of the Job runner surface for no MVP-visible capability.
- 2026-08-19 — **Product owner confirmed Python as the production core** ("keep the current architecture — slow but robust"); ADR-016 supersedes ADR-010, the Java port is cancelled, and the post-MVP checkpoint becomes a performance review. Robustness claims rest on the PostgreSQL/fencing/pure-reducer design; throughput claims require measurement.
- 2026-08-19 — Expressions are AMESH-native (Jinja2-backed, namespaced), not Pebble-compatible; parity remains a deferred, pinned workstream.
- 2026-08-19 — Planning corpus (900 requirements) is frozen during the MVP; reconciliation pass updates statuses post-MVP.
- 2026-08-19 — Pinned fastapi/pydantic/pydantic-settings exactly because the generated-contracts test asserts byte-stable output.
- 2026-08-21 — Use OpenRouter for live LLM integration tests with `openai/gpt-5.6-luna` as the base model and an environment-overridable model list — user requirement; the core model contract remains provider-neutral.
- 2026-08-25 — Keep EPIC-809 memory, evaluation and release subordinate to the existing session: explicit tenant-RLS memory scopes, exact immutable evaluation revisions, deterministic-first gates, optional pinned judge evidence and ordinary human approval.
- 2026-08-21 — Use Jinja2's sandboxed native environment for the explicitly accepted AMESH-native expression subset and croniter for cron calculation; keep occurrence durability in PostgreSQL execution idempotency rather than introducing a second scheduler datastore.
- 2026-08-21 — Use the official Kubernetes Python client 36 async API for the Job runner; deterministic attempt-derived Job names provide reconciliation while PostgreSQL remains authoritative for fenced completion.
- 2026-08-21 — Product owner deferred the remaining uninterrupted 24-hour W8 soak and authorized release progression after cycle 270. The verified partial run is accepted for `v0.2.0-mvp`; the full 86,400-second qualification remains open in EPIC-611 and gates broader availability, scale and production-readiness claims.
- 2026-08-21 — Use the Agent Hotel daemon board as the live execution tracker and keep `backlog/epics.json` as the canonical product-requirement source; `PLAN.md` records scope and decisions only.
- 2026-08-21 — Execute one dependency-ready epic at a time. Direct prerequisite epics enter scope only when the canonical dependency graph makes them necessary for one of the five requested product areas.
- 2026-08-21 — Start with EPIC-002 because it has no dependencies and its identity/resource contracts directly unlock RBAC, multi-tenancy and the REST/UI chain.
- 2026-08-22 — Break the EPIC-403/EPIC-502 planning cycle: EPIC-403 owns local login, durable browser sessions and the provider-neutral authentication boundary; EPIC-502 consumes that boundary for concrete OIDC, SAML, LDAP and SCIM adapters. Federated providers do not block the requested local multi-user login.
- 2026-08-22 — Complete EPIC-400 against the authoritative v0.2 resource profile and preserve `/api/v1`; add opt-in `Prefer: respond-async` execution launch plus common contract behavior. Per the product owner's prior “defer and move forward” direction, file/KV/secret/plugin lifecycle APIs stay with EPIC-207/506/300/301 instead of receiving placeholder persistence in the API layer.
- 2026-08-22 — Register the 50 locally closeable open epics as Agent Hotel cards `c37`–`c86` and execute them dependency-first. Defer the 20 external qualification epics and unrelated failures; implement only a minimum local prerequisite contract when a selected epic cannot otherwise be completed or verified.
- 2026-08-24 — Commit Sprint UX-01 to cards `c102`, `c97`, `c98` and `c99`, integrated by `c104`: audit first, then selectors, Mission Control and the simple execution trace. Preserve advanced operational and authoring surfaces; defer guided creation and production determinism qualification to their existing cards.
- 2026-08-24 — Complete Sprint UX-01 without a new dependency: use native accessible selectors for bounded catalogs, pure server-evidence projections for Mission Control and trace, cap Needs attention to 12 prioritized items, and retain the complete history through its dedicated route.
- 2026-08-25 — Decompose bounded agent execution into dependency-ordered EPIC-312, EPIC-807, EPIC-808, EPIC-809 and EPIC-806. Keep one execution engine, mediate every model/tool action through pinned capabilities, and require structured-output plus policy/evaluation gates before success. Reassign URS-F-0806–0819 across these boundaries rather than expanding the frozen 900-requirement corpus.
- 2026-08-25 — Implement guided workflow creation as a projection over canonical round-trip YAML. Reuse catalog schemas, validation, policy admission, simulation, isolated tests and persisted traces; do not introduce a wizard-only document or execution path.
- 2026-08-25 — Store prompts, skills, model policies and agent definitions in one typed immutable revision ledger, while keeping MCP connection pins in their existing ledger. Resolve exact references transactionally into one persisted capability-envelope pin; provider substitution always requires a new policy revision and explicit nondeterminism diagnostics.
- 2026-08-25 — Run `agent.session` as one recoverable workflow task with a PostgreSQL checkpoint/event journal. Models may propose one pinned tool or final output; AMESH alone validates, dispatches and enforces cumulative hard limits. Reuse accepted primitive calls through stable session operation keys and fail closed on ambiguous external outcomes.
- 2026-08-25 — Define EPIC-810 through EPIC-818 as decomposition-only implementation and qualification boundaries over the frozen 900-requirement corpus. AMESH owns generic durable scheduling, provider-neutral orchestration/evidence/model/tool contracts, local hardening, restart qualification, shadow comparison and promotion enforcement; clients retain domain semantics, thresholds, adapters, workflows and cutover authority.
- 2026-08-26 — Close EPIC-810 through EPIC-818 at their documented local qualification boundary. Live Compose, isolated hardened Compose, OpenRouter Luna, restart/idempotency, differential shadow and release rollback evidence are recorded in `docs/reviews/TESTLOG.md`; this does not broaden the deferred external-cloud, multi-region, long-duration or client-cutover claims.
- 2026-08-26 — Select `@earendil-works/pi-agent-core` 0.84.3 over DSH and Goose for EPIC-819. Use Pi's stable direct `Agent` API in an isolated npm-locked worker, keep Python under `uv`, and require all Pi model/tool requests to return through AMESH-owned gateways. The built-in compatibility adapter remains the default until bounded context, cache evidence and restart/live qualification pass.
- 2026-08-26 — Product-owner cutover directive supersedes EPIC-819's initial default deferral: Pi is mandatory in API and recovery-executor composition with no built-in fallback after the existing session behavior matrix, restart reuse, production-image and live Luna gates pass. Context compaction and cache evidence remain open without blocking the harness cutover.
- 2026-08-26 — Execute EPIC-819 through EPIC-824 sequentially. Reuse the canonical workflow document, immutable resource ledgers, execution/session journal, evidence bundle, object storage and plugin boundary; new UI and catalog surfaces are projections over those authorities, document extraction is a replaceable plugin operation, and Pi remains the fail-closed production harness while a portable conformance kit is added.
- 2026-08-27 — Remove executable GitHub Actions workflows. Replace hosted CI/CD with explicit Docker-local verification: one core verification image plus separately invokable compatibility/toolchain suites. Do not replace GitHub release publication or hosted attestation with implicit local side effects.
- 2026-08-27 — Use VibeStonks as the first external AMESH agent-team client without putting finance semantics in AMESH. AMESH owns generic durable execution, exact capability pins, budgets, retries, checkpoints, evidence and idempotency; VibeStonks owns its client adapter, team content, market-data MCP, decision acceptance, risk and all broker authority.
- 2026-08-27 — Resolve current-head MVP review findings 1–8 as local review gate `c134`. Explicitly defer Kubernetes output bounds, Helm webhook-secret wiring and operator path isolation (findings 9–11) to `c130`; do not represent those cluster-only gates as locally qualified.
- 2026-08-27 — Close the next PR #1 review gate by fixing only the two supported-path blockers:
  preserve stable MCP invocation identity across retries and consume tenant API quota only after
  successful authorization. Route Kubernetes findings to `c130`, cloud/storage findings to `c131`
  and optional federation/webhook/script findings to `c132`.
- 2026-08-27 — Treat Docker-local verification as the merge boundary: the passing aggregate covers
  core checks, four Compose configurations, the production-image probe and local artifact creation.
  Keep repository-wide format/frontend-lint baselines and specialist matrices visible on `c90`,
  `c88` and `c110`; local verification never publishes artifacts.
- 2026-08-28 — Gate ordinary developer pushes with a tracked native Git pre-push hook configured per
  clone. Reuse the complete Make/PowerShell Docker aggregate without a hook-manager dependency;
  retain the explicit Git `--no-verify` and server-side-enforcement boundary while hosted CI remains
  disabled.
- 2026-08-29 — Define EPIC-826 as an independently consumable, horizontally scalable agent-session
  product surface on the existing webserver role over the execution reducer and session journal. Keep
  the canonical API provider- and harness-neutral; Pi is the current exact default pin, and future adapters must pass
  the same conformance contract without changing client APIs. Treat OpenAI compatibility as a
  documented adapter, pre-existing fine-tuned model identifiers as model-profile data, and model
   training, proprietary ChatGPT internals, active-session hot-swaps and a second session engine as
   explicit non-goals.
- 2026-08-30 — Define EPIC-827 as a separate session-administration product boundary without a
  second runtime authority. Keep application session APIs backward compatible; introduce explicit
  session RBAC, bounded fleet projections, policy/capacity controls and digest-protected migration.
  Permit session transfer only for terminal sessions or clean paused checkpoints with no ambiguous
  external invocation, and never include secret plaintext in a portable bundle.
- 2026-08-31 — Define EPIC-828 as one live multimodal-run boundary with independently verifiable
  chronology and image-input workstreams. Assign global order when a safe progress event enters the
  canonical journal; close a segment across any intervening activity so `thinking 1 -> work ->
  thinking 2` cannot be regrouped later. Carry images as tenant-authorized, digest-pinned object
  references through the shared artifact, workflow, task and plugin contracts; allow every node to
  carry the value, resolve bytes only at a capability-gated consumer boundary, and never persist
  hidden reasoning or raw image bytes in public events.
- 2026-08-31 — Queue EPIC-829 after EPIC-828 for a Material for MkDocs user site using the existing
  Markdown and `uv`/Docker toolchain. Queue EPIC-830 after documentation to measure historical
  provider prompt-cache evidence, locate the first proven reuse break, implement only evidence-backed
  platform-neutral improvements and compare a frozen before/after workload.
- 2026-08-31 — Revalidate GitHub issues against current source before creating duplicate work. Treat
  #5 as EPIC-828 publication/qualification rather than a second implementation, repair #4 and #6 at
  the provider/session evidence boundary, and implement #7 as provider- and harness-neutral
  `requiredToolPlan` governance in AMESH. Expand once from immutable session input, gate exact calls
  before external I/O, persist a restart-safe ledger and keep plan arguments out of public evidence.
- 2026-08-31 — Define EPIC-832 as a harness-owned context-management boundary under AMESH hard
  enforcement. Preserve explicit workflow expression compatibility and schema-validated final-result
  handoffs without propagating private transcripts. Pass a context window, input ceiling and
  completion reserve to Pi's locked `transformContext` seam; verify its selected messages and receipt
  at the AMESH gateway before provider I/O. Qualify `deepseek/deepseek-v4-flash-vision-exp` through the
  same provider-neutral Luna matrix rather than adding a DeepSeek-specific core path.
- 2026-09-01 — Define EPIC-833 as a durable progress-backpressure correction for GitHub issue #14.
  Keep the pure append-only reducer terminal after `TRUNCATED`, but make the PostgreSQL sink return
  the persisted marker as a truthful truncated no-op for later frames so telemetry overflow cannot
  fail model, session or workflow execution. Keep client filtering and display coalescing separate
  from AMESH-owned validation, redaction, idempotency and hard storage/rate bounds.
- 2026-09-01 — Create EPIC-834 and ADR-071 after the product owner selected complete activity over
  write batching. Treat the PostgreSQL journal as the durable FIFO, acknowledge each frame only after
  commit and allow storage latency to throttle producers. Disable default rate/count truncation and
  generate no new `TRUNCATED` frames; retain historical decoding. Do not add a volatile batch or a
  second broker because either weakens restart semantics or adds another durable authority without
  eliminating per-frame durable ingress.
- 2026-09-02 — Group verified GitHub issues #10–#12 into EPIC-835 and ADR-072. Keep PostgreSQL
  progress conflicts strict by scoping Pi sources to canonical invocation keys; checkpoint safe
  provider accounting before response validation; and represent no AMESH ceiling with an explicit
  provider-bounded mode rather than sentinel values or changed omission semantics.
- 2026-09-02 — Extend EPIC-835 through issues #16 and #17: bind encrypted provider continuations to
  exact retained assistant messages and recognize a reconnect cursor whose attempt is already
  terminal without suppressing committed retry events. Activate EPIC-836 under ADR-074. Direct HTTP
  keeps its endpoint/secret route; subscription engines use an authorized `engineRef`, isolated
  server-owned homes and only the official Codex App Server or Copilot CLI programmatic contracts.
- 2026-09-03 — Define EPIC-838 after re-verifying GitHub issue #42 against merged main. Accept the
  work that demonstrably landed, classify the migration-path environment claim as stale, defer only
  the currently non-failing `python -m amesh.app` replacement hazard, and resolve the remaining
  valid or partial claims through child issues #43–#53 in dependency order. Partition the canonical
  epic catalog by lifecycle state under ADR-075 while all planning consumers retain one aggregate
  deterministic view.
- 2026-09-05 — Create integration-readiness epic #69 and child issues #70–#72 from the bounded
  repository review. Start with schema-correct onboarding and truthful status. Reuse #66/PR #68;
  do not absorb #67 debt, Sonar findings or refactors. Confirm the deployment target, recovery point
  and change window before upgrade, and the consumer repo/provider budget before live qualification.
