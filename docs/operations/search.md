# Search projection operations

The indexer role polls authoritative tenant resources into generation-partitioned
`search_documents_v2`. PostgreSQL full-text, trigram and JSON/structured indexes serve bounded API
queries across flows, executions, task runs, logs, metrics, assets and audits. Projection state,
per-type checkpoints, daily rollups and immutable rebuild/failure/control events live in
`search_projection_state`, `search_projection_checkpoints`, `search_projection_daily_rollups` and
`search_projection_events`; events publish through the transactional outbox.

## Observe

Use `GET /api/v1/search/status` with tenant and authenticated actor context. Investigate when:

- `condition` is `DEGRADED` or `lastError` is populated;
- `lagSeconds` grows while source writes continue;
- `documentsIndexed` does not converge toward `sourceDocuments`; or
- `condition` remains `REBUILDING` and `progress` stops changing;
- `checkpointsVerified` remains false after projection work converges; or
- `buildingVersion` remains populated without a matching completion event.

Indexer health and search health are intentionally separate from the executor and scheduler. Search
failure does not justify stopping orchestration.

## Rebuild

An authorized operator can start a tenant rebuild:

```http
POST /api/v1/search/rebuild
Content-Type: application/json

{
  "reason":"recover August log and metric projection after index change",
  "types":["LOG","METRIC"],
  "from":"2026-08-01T00:00:00Z",
  "to":"2026-08-31T23:59:59Z"
}
```

Watch the status endpoint until `condition` is `READY`, `buildingVersion` clears, `progress` is `1`,
counts converge and `checkpointsVerified` is true. The old generation serves queries throughout the
build. The atomic switch replaces only disposable projection rows and preserves all authoritative
resources and orchestration evidence. Rebuild scope controls which copied rows are reset; the indexer
then catches up every resource type so concurrent source writes cannot be omitted from verification.

Use `GET /api/v1/search/verify` to inspect the source/projected count and checksum for each document
type. Disable projection with `POST /api/v1/search/control` and `{"enabled":false,"reason":"..."}`
when a rebuild must pause. Bounded flow and execution search then falls back to authoritative tables;
task-run, log, metric, asset and audit searches remain unavailable until projection resumes.

When an authoritative source row expires under its own retention policy, the next projector cycle
moves its full tenant-protected search row into `search_projection_archives` before removing it from
the active generation. Archive rows carry the source-policy reason and a seven-day purge timestamp.
The search backend never expires data before its authoritative source.

## Degraded-service response

1. Confirm the API, executor and scheduler remain healthy; do not pause source writes for search alone.
2. Inspect indexer logs and PostgreSQL availability, statement timeouts and disk capacity.
3. Restore the dependency or correct the projector failure, then request a rebuild.
4. Verify convergence through the status endpoint and run a known tenant-scoped query.

Migration `0052_search_projection_backend.sql` adds the v2 schema beside the v1 table, records schema,
table, index, materialized-view and rollup components, and seeds an active generation from v1. If
rollout fails, stop optional search projection cycles, disable projected reads and forward-fix the v2
schema; do not remove or rewrite authoritative source data. Restore correctness is established by
rebuilding and verifying the projection after the primary PostgreSQL restore.
