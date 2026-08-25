# API contracts

- `openapi.json` is generated from the foundation FastAPI application.
- Pull-request CI regenerates the contract and uses `oasdiff` to reject error-level breaking changes
  against the target branch. Warning-level findings remain visible for review.
- The current endpoints cover health, flow validation and management, execution control, webhook triggers, logs, reconnectable realtime events, signed outbound webhook subscriptions, authorization administration, decision explanation, service-account API tokens and workload credential exchange.
- Flow validation accepts YAML or JSON and returns the versioned `amesh.flow/v1` canonical form. Blocking issues include stable codes, data paths, source ranges and remediation hints; see the [flow DSL contract](../architecture/flow-dsl.md).
- Resource-bearing operations authenticate and authorize server-side. The development bootstrap token is unavailable outside development mode; durable service/workload credentials work in every mode, and interactive users use revocable PostgreSQL-backed browser sessions with CSRF protection.
- Enterprise provider discovery, OIDC/SAML browser redirects, LDAP authentication and tenant-bound
  SCIM provisioning are documented in the [identity and SCIM API guide](identity-and-scim.md).
- They are not the complete compatibility API; gaps remain explicit until the version-pinned ADR-009 façade epics are verified.
- Generated Python, TypeScript, Java and Go packages and their high-level execution facade are
  documented in the [public SDK guide](sdks.md).
- Compile signed revision-pinned plans, declare side-effect substitutions and compare plan/plugin
  changes through the [deterministic simulation API](simulations.md).
- Author immutable scoped rules, validate flows and inspect pinned lifecycle decisions through the
  [admission policy API](admission-policies.md).

## v1 conventions

- Existing collection arrays remain the response body. `limit`, opaque `cursor`, repeatable
  `filter=field=value`, `sort=field,-field`, and `fields=field,field` query parameters are opt-in;
  `X-Total-Count` and `X-Next-Cursor` carry page metadata.
- Create an execution synchronously by default, or send `Prefer: respond-async` to receive `202`,
  `Preference-Applied`, and a `Location` to poll. `Idempotency-Key` is the preferred replay key.
  The Compose profile runs the executor recovery role with the local process runner; Kubernetes keeps
  the default Kubernetes Job recovery mode.
- Bulk execution launch accepts 1–100 items and returns `207 Multi-Status` with an independent
  result for each item.
- Errors use `application/problem+json`. Execution logs are also available as streaming NDJSON at
  `/api/v1/executions/{execution_id}/logs/stream`.
- Execution detail accepts `taskOffset` and `taskLimit` (maximum 1,000) and returns only that task-run
  window plus `taskRunSummary`, whose state totals cover the complete execution. Reconnect debugging
  evidence with `/api/v1/executions/{execution_id}/evidence/stream`; each NDJSON record carries the
  next opaque cursor.
- Reconnect state, log and authorized audit changes with `GET /api/v1/realtime/stream`; use the
  returned SSE `id` as `Last-Event-ID`. Signed outbound subscriptions, retries, endpoint tests and
  selected replay are documented in the [realtime API guide](realtime.md).
- Cache-enabled flows accept execution `cacheMode` values `USE`, `BYPASS` and `REFRESH`. Inspect
  tenant entries with `GET /api/v1/task-cache` and soft-purge a key prefix or resource scope with
  `POST /api/v1/task-cache/purge`; see the [task cache runbook](../operations/task-cache.md).
- Inspect durable trigger health and occurrences with `GET /api/v1/triggers` and
  `GET /api/v1/trigger-occurrences`. Authorized operators can pause/resume a trigger or replay a
  dead-lettered occurrence; see the [trigger runbook](../operations/triggers.md).
- Manage reusable execution-check policies with `GET/PUT /api/v1/check-policies`, inspect evidence
  with `GET /api/v1/check-evaluations`, and aggregate it with `GET /api/v1/check-compliance`; see the
  [execution-check runbook](../operations/execution-checks.md).
- List, render, save and export typed operational dashboards through `/api/v1/dashboards`; direct
  typed queries use `/api/v1/dashboard-queries`. See the [dashboard API guide](dashboards.md).
- Search authorized flow, execution, selected log, asset and audit metadata with the typed
  `/api/v1/search` contract. Inspect or rebuild its disposable tenant projection through the adjacent
  status and rebuild endpoints; see the [search API guide](search.md).
- Compose namespace, identity, runtime, effective-configuration and guarded tenant controls through
  the administration surface. High-risk changes require a short-lived actor/tenant/draft-bound
  preview and immutable success or rejection evidence; see the [administration API guide](administration.md).
- Search and preview versioned local blueprints, instantiate them as unsaved validated drafts, and
  validate isolated expressions or flow fragments through the [blueprint API](blueprints.md).
- Query the tamper-evident ledger, manage audit-only retention and legal holds, deliver signed SIEM
  events, and build redacted readiness packages through the
  [audit and compliance API](audit-and-compliance.md).
- Define workflow-data retention, preview destructive impact and resume bounded purge jobs through the
  [lifecycle API](lifecycle.md); audit retention remains independent.
- Inspect the LTS catalog, run upgrade gates and explicitly migrate persisted events or configuration
  through the [upgrade API](upgrades.md).
- Inspect redacted TLS, certificate, proxy, connection and DNS posture through the
  [network diagnostics API](network-diagnostics.md).
- Inspect scoped plugin rules and their decision sources, validate candidate flow pins, and perform
  impact-gated emergency version disable through the
  [plugin governance API](plugin-governance.md).
- Declare or observe data and infrastructure assets, traverse permission-filtered lineage and export
  OpenLineage events through the [asset catalog and lineage API](asset-catalog-and-lineage.md).
- Publish pinned workflow forms, launch them from authenticated links or embeds, and operate durable
  participant approvals through the [workflow apps and human tasks API](workflow-apps-and-human-tasks.md).
- Publish announcements and operate scoped maintenance or kill switches through the
  [operational controls API](operational-controls.md).
- Define isolated revision-pinned simulations, inspect observed coverage and enforce namespace
  promotion policy through the [flow tests API](flow-tests.md).
- Define immutable prompt, skill, model-policy and agent resources; inspect exact dependencies; and
  atomically pin effective capability envelopes through the
  [agent primitive API](agent-primitives.md).
- Discover the client-neutral external orchestration profile, including correlation,
  idempotent launch, reconnectable events and signed webhook guarantees, through the
  [external orchestration API guide](external-orchestration.md).

Future generated SDKs must consume the supported API contract, not internal Python classes.
