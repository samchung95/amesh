# Discover workflow resources

The effective workflow-resource catalog is generated from the installed core and plugin set. It is
the source for the control room's task, input and trigger selectors, configuration forms and inline
schema help. A static hand-maintained list would drift when plugins change, so discover the catalog
from the instance you are authoring against.

## Read the effective catalog

```powershell
$headers = @{
  Authorization = 'Bearer development-token'
  'X-Amesh-Tenant' = 'default'
}
$editor = Invoke-RestMethod -Headers $headers `
  -Uri http://localhost:8000/api/v1/flows/editor/schema
$editor.resourceCatalog.resources |
  Select-Object kind, type, @{Name='title'; Expression={$_.editor.title}}
```

Each descriptor contains:

- `kind`: `task`, `input` or `trigger`;
- `type`: the exact value accepted by flow YAML;
- `configurationSchema`: the JSON Schema for that resource's configuration;
- `editor`: title, description, category and property-order hints.

The same response includes the complete flow schema and supported expression contexts. Authorization
is evaluated before the catalog is returned, and plugin policy determines which descriptors are
effective.

## Checked-in core baseline

The generated
[`schemas/resource-catalog.json`](https://github.com/samchung95/amesh/blob/main/schemas/resource-catalog.json)
is the repository's core baseline and is checked for deterministic regeneration. The running endpoint
is the correct source when an installation includes plugins.

Use [Flow DSL and validation](../architecture/flow-dsl.md) for the document structure and
[Build workflows](../workflows/index.md) for task-oriented examples.
