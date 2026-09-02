# API and UI architecture

## API

The REST API is the supported automation contract. It is versioned under `/api/v1` initially and described
by generated OpenAPI. Common conventions include:

- cursor pagination;
- field filters and stable sorting;
- RFC 7807-style structured errors with platform error codes;
- `Idempotency-Key` for state-changing create/action calls;
- `If-Match` or expected version for optimistic concurrency;
- streaming upload/download for files and exports;
- explicit tenant context;
- authorization before existence disclosure.

Execution evidence uses an authorized JSON page plus newline-delimited JSON stream. Both accept an
opaque reconnect cursor over the durable state/log/metric/output/artifact event sequence. WebSockets
may be added for interactive bidirectional features without changing that cursor contract.

### Application composition boundary

`amesh.app:app` remains the stable server and test import path. It aliases the implementation module
under `amesh.api` so legacy imports, dependency overrides and monkeypatches keep the same module-global
identity while API code moves into feature modules incrementally. The checked-in OpenAPI document is
the route-parity gate for that decomposition.

Execution launch is an application service rather than route-local persistence logic. API launch and
worker recovery share the builders in `amesh.application` for runner selection and lifecycle, handler
registration, outbound HTTP policy and executor recovery types. The API supplies request authorization
and HTTP error mapping; the worker supplies recovery controls and system-subflow policy. CLI execution
uses the public API, while local administrative authentication and service-role webhook delivery use
the same settings-driven composition helpers.

## UI

The frontend is a client of public APIs; it has no privileged database path. Major bounded areas are:

```text
shell/auth
dashboard
flows/editor/topology
executions/gantt/logs
namespaces/files/kv/secrets metadata
assets/lineage
apps/approvals
plugins/registry
administration/identity/policy/health
```

Plugin schemas drive forms and completion. The canonical YAML/IR remains the source of flow semantics;
the visual editor is a projection and editor of the same model.

Dashboards are also public-API clients. Their restricted typed query contract selects only supported
operational projections and never accepts database SQL. Saved-view authorization is evaluated before
the underlying execution, log, metric, SLA, worker or asset permission; a denied source remains an
explicitly redacted widget rather than leaking data through the dashboard definition.

## Frontend safety

- Secrets are never embedded in initial HTML or browser telemetry.
- HTML and Markdown from plugins, logs or descriptions are sanitized.
- Destructive actions use server-generated impact previews.
- Realtime streams enforce the same permissions as REST queries.
- Large execution graphs and logs use pagination, aggregation and virtualization.
- Accessibility is checked by locally invoked Playwright/axe journeys and manual review for key
  workflows. The broader GA browser and assistive-technology matrix remains deferred on `c91`.
