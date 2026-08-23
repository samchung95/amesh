# Blueprint and playground API

The blueprint catalog is a read-only, versioned authoring surface. It never persists a flow or starts
an execution. Every route uses the authenticated tenant and the ordinary server-side flow permission
boundary.

## Catalog and draft endpoints

- `GET /api/v1/blueprints` lists summary metadata. Optional `q` searches IDs, titles, summaries,
  documentation and tags; optional `source` accepts `BUILTIN`, `ORGANIZATION` or `COMMUNITY`.
- `GET /api/v1/blueprints/{blueprintId}/{version}` returns the exact template, typed parameters,
  documentation, license and provenance digest.
- `POST /api/v1/blueprints/{blueprintId}/{version}/instantiate` accepts a `parameters` object and
  returns a YAML `document` plus native flow validation evidence.

Instantiation uses declared string, namespace and flow-ID parameters only. Unknown or invalid values
return `422`; unknown versions return `404`. The response is an unsaved draft. The caller must
explicitly save it through `PUT /api/v1/flows`, then explicitly create an execution. No repository,
queue or runner is called by the instantiate route.

The checked-in local catalog contains built-in, organization-style and community-style examples.
Every entry is `localOnly`, carries a semantic version and immutable SHA-256 provenance, and uses
resources available in the reference Compose deployment.

## Isolated playground

`POST /api/v1/playground/simulate` accepts an optional native expression and optional YAML flow
fragment. A fragment may be one task, a task list or a flow with `tasks`. At least one subject is
required.

The server redacts sensitive context keys, evaluates expressions with the native compatibility
engine, and validates fragments with the installed resource catalog. `core.log` and `core.return`
receive a deterministic preview step; other resources are validation-only. The response always
includes this machine-readable safety evidence:

```json
{
  "persisted": false,
  "executed": false,
  "credentialAccess": false,
  "infrastructureAccess": false
}
```

The playground does not invoke a task handler, credential provider, object store, runner or workflow
repository. It is therefore suitable for local syntax learning, not production side-effect testing.

See the [first-run guide](../operations/onboarding.md) for the web workflow.
