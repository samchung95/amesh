# API contracts

- `openapi.json` is generated from the foundation FastAPI application.
- Pull-request CI regenerates the contract and uses `oasdiff` to reject error-level breaking changes
  against the target branch. Warning-level findings remain visible for review.
- The current endpoints cover health, flow validation and management, execution control, webhook triggers, logs, reconnectable realtime events, signed outbound webhook subscriptions, authorization administration, decision explanation, service-account API tokens and workload credential exchange.
- Flow validation accepts YAML or JSON and returns the versioned `amesh.flow/v1` canonical form. Blocking issues include stable codes, data paths, source ranges and remediation hints; see the [flow DSL contract](../architecture/flow-dsl.md).
- Resource-bearing operations authenticate and authorize server-side. The development bootstrap token is unavailable outside development mode; durable service/workload credentials work in every mode, and interactive users use revocable PostgreSQL-backed browser sessions with CSRF protection.
- They are not the complete compatibility API; gaps remain explicit until the version-pinned ADR-009 façade epics are verified.

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

Future generated SDKs must consume the supported API contract, not internal Python classes.
