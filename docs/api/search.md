# Search API

The search API reads a disposable PostgreSQL projection of authorized flow, execution, selected log,
asset and audit metadata. It never becomes authoritative state. Source writes and orchestration do not
wait for search, and a projection can be deleted and rebuilt from the source repositories.

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

Responses include `items`, an opaque `nextCursor`, `deniedTypes`, `projectionVersion` and
`projectionCondition`. Pass `nextCursor` back unchanged with the same filters to fetch the next stable
page. A cursor used with different filters returns `400`.

Search authorization is additive: callers need `search:view`, and every requested document type is
independently checked against its underlying `flow`, `execution`, `asset` or `audit` view permission.
Denied types are returned in `deniedTypes` and are never included in the projection query.

## Projection status and rebuild

`GET /api/v1/search/status` returns the tenant projection version, `READY`, `REBUILDING` or `DEGRADED`
condition, indexed/source counts, progress, lag, timestamps, failures and the last error.

`POST /api/v1/search/rebuild` requires `search:manage` and a bounded `reason` string. It returns `202`
with rebuild status. Rebuild deletes only disposable tenant projection rows, increments the projection
version and republishes from authoritative resources. Requests return `503` while the search repository
itself is unavailable; source writes and orchestration remain independent.

See the [search operations runbook](../operations/search.md) for recovery steps.
