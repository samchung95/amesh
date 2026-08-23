# Search projection operations

The indexer role polls authoritative tenant resources into the partitioned `search_documents`
projection. PostgreSQL full-text, trigram and JSON/structured indexes serve bounded API queries.
Projection state and immutable rebuild/failure events live in `search_projection_state` and
`search_projection_events`; the latter publishes through the transactional outbox.

## Observe

Use `GET /api/v1/search/status` with tenant and authenticated actor context. Investigate when:

- `condition` is `DEGRADED` or `lastError` is populated;
- `lagSeconds` grows while source writes continue;
- `documentsIndexed` does not converge toward `sourceDocuments`; or
- `condition` remains `REBUILDING` and `progress` stops changing.

Indexer health and search health are intentionally separate from the executor and scheduler. Search
failure does not justify stopping orchestration.

## Rebuild

An authorized operator can start a tenant rebuild:

```http
POST /api/v1/search/rebuild
Content-Type: application/json

{"reason":"recover projection after index change"}
```

Watch the status endpoint until `condition` is `READY`, `progress` is `1`, counts converge and lag is
acceptable. Rebuild is tenant-scoped, replaces only disposable projection rows and preserves all
flows, executions, logs, assets, audit records and orchestration evidence.

## Degraded-service response

1. Confirm the API, executor and scheduler remain healthy; do not pause source writes for search alone.
2. Inspect indexer logs and PostgreSQL availability, statement timeouts and disk capacity.
3. Restore the dependency or correct the projector failure, then request a rebuild.
4. Verify convergence through the status endpoint and run a known tenant-scoped query.

Migration `0044_search_projection.sql` is additive. If rollout fails, stop optional search projection
cycles and forward-fix the schema; do not remove or rewrite authoritative source data. The projection
is included in ordinary PostgreSQL backup, but restore correctness is established by rebuilding it
from authoritative repositories after the primary restore.
