# Asset catalog and lineage API

AMESH keeps declared and runtime-observed assets in one tenant-scoped catalog. An asset's stable
identity is the tuple `provider`, `account`, `location`, `assetType` and `externalKey`; namespace is
an authorization and ownership boundary rather than part of that identity.

## Register and observe assets

- `POST /api/v1/assets` creates or updates an explicit declaration. Send `expectedVersion` when an
  update must reject a stale writer.
- `POST /api/v1/assets/observations` records a `READ` or `WRITE` observation and its flow, execution,
  task-run or artifact references. A write marks the asset healthy and advances last materialization.
- An isolated plugin can emit the same observation without calling the API by returning a
  `PluginAsset` from `ProcessPluginResult.assets`. The SDK sends it as an authenticated
  `amesh.asset` notification; task-completion persistence writes the catalog observation in the same
  transaction as the task's output evidence.

Example declaration:

```json
{
  "assetId": "019910bf-cf91-7b1d-8e59-14de1ea58dbe",
  "namespace": "team.data",
  "provider": "postgresql",
  "account": "analytics",
  "location": "warehouse.internal:5432",
  "externalKey": "curated.orders",
  "assetType": "table",
  "displayName": "Curated orders",
  "description": "Validated order facts",
  "owner": "analytics",
  "contacts": ["analytics@example.test"],
  "domainGroup": "commerce",
  "tags": ["gold", "qualified"],
  "customMetadata": {"classification": "internal"},
  "labels": {"environment": "production"}
}
```

## Lineage and evidence

`POST /api/v1/assets/lineage` declares an upstream-to-downstream edge. AMESH also infers an edge
when one execution observes a read and a write: its confidence is 80% of the weaker observation.
Repeated declarations for the same evidence context update the existing edge deterministically.

Evidence kinds remain explicit:

- `DECLARED` is supplied by an operator or integration.
- `OBSERVED` comes from a runtime read or write event.
- `INFERRED` is derived from observations in the same execution.

`GET /api/v1/assets/{assetId}` returns the asset, visible upstream/downstream neighbors, recent
observations and edges. The Assets page presents the same graph, health, last materialization,
ownership, contacts, tags and execution/artifact evidence.

## Authorization and export

Asset reads require `asset.view`; declarations, observations and lineage writes require
`asset.update`. Every list and traversal evaluates the asset's namespace. A caller cannot recover a
hidden neighbor from a visible asset's graph, and PostgreSQL row-level security keeps tenants
separate below the API.

`GET /api/v1/assets/export/openlineage?namespace=team.data` exports authorized observations and
edges as OpenLineage `RunEvent` records. AMESH maps the provider identity to a dataset namespace such
as `postgresql://analytics/warehouse.internal:5432` and the stable external key to the dataset name.
This follows the official [OpenLineage RunEvent schema](https://openlineage.io/apidocs/openapi/) and
[dataset naming guidance](https://openlineage.io/docs/spec/naming/); no OpenLineage server is needed
to produce the interchange file.
