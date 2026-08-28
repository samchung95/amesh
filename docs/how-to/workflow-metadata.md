# Configure workflow labels and plugin defaults

Set namespace metadata through the authorized API. Parent namespaces are inherited automatically.

```http
PUT /api/v1/namespaces/examples/workflow-metadata
Content-Type: application/json

{
  "pluginDefaults": [
    {
      "type": "core.return",
      "values": {"workerGroup": "standard", "region": "apac"}
    }
  ],
  "policy": {
    "requiredLabels": {"team": "platform"},
    "normalizeLabels": {"environment": "LOWERCASE"},
    "requiredDefaults": {"core.return": ["region"]}
  }
}
```

Use `expectedVersion` on a later update for optimistic concurrency. Read the applicable lineage with:

```http
GET /api/v1/namespaces/examples/jobs/workflow-metadata
```

Flows may add labels and non-forced defaults. Tasks use `runLabels` for task-run labels. Defaults
match the complete plugin type, not a type prefix.

```yaml
labels:
  team: platform
  environment: PROD
pluginDefaults:
  - type: core.return
    values:
      timeoutSeconds: 30
tasks:
  - id: done
    type: core.return
    runLabels:
      stage: acceptance
    value: ok
```

The prefixes `amesh.` and `system.` are reserved. AMESH attaches those system labels itself to flows,
executions, task runs, assets and backfills.

Open the flow detail page or call the metadata endpoint to inspect resolved values and their origins:

```http
GET /api/v1/flows/examples/jobs/metadata-demo/metadata
```

Collection filters accept dotted label paths, for example:

```http
GET /api/v1/flows?metadata.labels.team=platform
```

Namespace changes are applied when a new flow revision is created; existing execution revisions do
not change underneath running or historical work.
