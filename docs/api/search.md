# Search API

The search API reads a disposable PostgreSQL projection of authorized flow, execution, task-run, log,
metric, asset and audit metadata. It never becomes authoritative state. Source writes and orchestration
do not wait for search, and a projection can be rebuilt from the source repositories.

## Query

`POST /api/v1/search` accepts a typed JSON request:

```json
{
  "query": "timeout",
  "types": ["FLOW", "EXECUTION", "LOG"],
  "namespace": "operations",
  "states": ["FAILED"],
  "labels": {"team": "platform"},
  "fields": {"flowId": "daily-sync", "level": "ERROR"},
  "from": "2026-08-01T00:00:00Z",
  "to": "2026-08-23T23:59:59Z",
  "ranges": [{"field": "SOURCE_VERSION", "gte": 2}],
  "sort": "RELEVANCE",
  "direction": "DESC",
  "limit": 50
}
```

Supported sorts are `RELEVANCE`, `TITLE`, `OCCURRED_AT`, `UPDATED_AT`, `TYPE` and `STATE`.
Structured ranges support `OCCURRED_AT`, `UPDATED_AT` and `SOURCE_VERSION`. The time window is bounded
to 366 days and the page size to 200. Arbitrary SQL and arbitrary field names are rejected.

Responses include `items`, an opaque `nextCursor`, `deniedTypes`, `projectionVersion`,
`projectionCondition` and `authoritativeFallback`. Pass `nextCursor` back unchanged with the same
filters to fetch the next stable page. A cursor used with different filters returns `400`.

Search authorization is additive: callers need `search:view`, and every requested document type is
independently checked against its underlying `flow`, `execution`, `asset` or `audit` view permission.
Denied types are returned in `deniedTypes` and are never included in the projection query.

## Projection status and rebuild

`GET /api/v1/search/status` returns schema, active and building versions; `READY`, `REBUILDING`,
`DEGRADED` or `DISABLED`; indexed/source counts; progress; lag; checksum state; timestamps; failures;
and the last error.

`POST /api/v1/search/rebuild` requires `search:manage` and a bounded `reason` string. It returns `202`
with rebuild status. Optional `types`, `from` and `to` fields scope the tenant rebuild. A new generation
is populated beside the active generation; reads continue from the active version until exact per-type
counts and checksums pass, then the generation switches atomically. The requested scope determines
which rows are reset; incremental catch-up still covers every type so writes made during the rebuild
are present before the switch.

`GET /api/v1/search/verify` requires `search:manage` and compares authoritative and projected row
counts, identity/version checksums and durable per-type checkpoints. `POST /api/v1/search/control`
accepts `enabled` and `reason`. When disabled, bounded flow and execution queries read authoritative
tables and return `authoritativeFallback: true`; unsupported projected types appear in `deniedTypes`.
Requests return `503` while PostgreSQL itself is unavailable, but source writes and orchestration remain
independent.

See the [search operations runbook](../operations/search.md) for recovery steps.
