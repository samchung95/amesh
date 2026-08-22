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

## Frontend safety

- Secrets are never embedded in initial HTML or browser telemetry.
- HTML and Markdown from plugins, logs or descriptions are sanitized.
- Destructive actions use server-generated impact previews.
- Realtime streams enforce the same permissions as REST queries.
- Large execution graphs and logs use pagination, aggregation and virtualization.
- Accessibility is tested in CI and manually for key workflows.
