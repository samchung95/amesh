# Dashboard API

Dashboards are versioned, tenant-isolated saved views over AMESH operational projections. Six
read-only built-ins cover instance, tenant, namespace, flow, worker and SLA views. Custom definitions
use the same public contract and can be supplied as JSON or exported YAML for GitOps.

## Endpoints

- `GET /api/v1/dashboards` lists authorized built-in and custom definitions.
- `GET /api/v1/dashboards/{dashboardId}` returns one authorized definition.
- `POST /api/v1/dashboards/{dashboardId}/render` renders every widget with optional runtime filters.
- `POST /api/v1/dashboard-queries` executes one typed query.
- `PUT /api/v1/dashboards/{dashboardId}?expectedVersion=N` creates or updates a custom definition.
- `DELETE /api/v1/dashboards/{dashboardId}?expectedVersion=N` soft-deletes a custom definition.
- `GET /api/v1/dashboards/{dashboardId}/export?format=yaml` exports a definition as YAML; use
  `format=json` for JSON.

Custom writes require `dashboards.manage`; reads require `dashboards.view`. A definition's
`visibility`, `viewerIds` and `editorIds` independently restrict who may see or change that saved
view. They never grant access to its data: each widget is authorized again for its source. A render
keeps the dashboard layout but returns a redacted widget when source access is denied, while a direct
query is rejected.

## Typed query model

Queries select a `source`, `visualization`, `measure`, `aggregation`, up to three allowed
`groupBy` dimensions and filters. Sources are `executions`, `logs`, `metrics`, `sla`, `workers` and
`assets`; visualizations are `timeSeries`, `table`, `counter`, `distribution`, `statusBreakdown` and
`rankedList`. The schema does not contain a SQL field and rejects unknown dimensions or invalid
source/measure pairs.

Filters support `from`, `to`, labels, namespace, flow ID, states, worker groups and bounded custom
dimensions. The server enforces a maximum 90-day explicit range, 500 returned groups, a 20,000-row
scan cap, 100-5,000 ms statement timeout and 1-100% deterministic sampling. Every result reports
`freshnessAt`, scanned/matched row counts, sampling state and whether it is partial.

## GitOps example

```yaml
apiVersion: amesh.dashboard/v1
id: operations
name: Operations
visibility: tenant
viewerIds: []
editorIds: []
widgets:
  - id: execution-status
    title: Execution status
    query:
      source: executions
      visualization: statusBreakdown
      measure: count
      aggregation: count
      groupBy: [state]
      limit: 20
      timeoutMs: 2000
      sampleRate: 1
```

Apply the parsed document body with the versioned `PUT` endpoint. Use `expectedVersion=0` to create
a new ID and the returned `version` for later optimistic-concurrency updates or deletion.
