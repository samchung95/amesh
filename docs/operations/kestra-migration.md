# Kestra 1.3.30 compatibility and migration

AMESH provides a clean-room, version-pinned compatibility surface for evaluating and staging Kestra
1.3.30 flows and exports. It does not currently claim complete Kestra compatibility; the machine
manifest lists the exact declared surface and every release-blocking gap.

## Inspect and validate

Print the compatibility contract:

```console
uv run amesh kestra compatibility manifest
```

Classify a flow without changing it:

```console
uv run amesh kestra flow validate flow.yaml
```

The result contains `exact`, `compatibility-adapted` and `blocked` mappings, source locations and
mechanical patches. `valid: false` and exit code 1 mean at least one construct cannot be migrated
without an explicit adapter. The original comment and key ordering remain available in
`roundTripDocument`; no unsupported field is silently removed.

Write a native candidate only when the complete source document is supported:

```console
uv run amesh kestra flow migrate flow.yaml --output-path amesh-flow.yaml
```

The corresponding REST routes are:

- `POST /api/v1/main/flows/validate`
- `POST /api/v1/executions/{namespace}/{flow_id}`
- `GET /api/v1/compatibility/kestra/manifest`

Request/response schemas, statuses, pagination behavior and error schema are declared in
`kestra-compatibility-1.3.30.json` and the generated OpenAPI document.

## Plan and stage a full migration

Migration bundles use schema `amesh.kestra-migration/v1`. Each record includes a resource kind,
stable source and target identifiers, tenant and namespace, exact payload, references, optional
historical timestamp, external secret references and a SHA-256 checksum. The bundle covers flows,
namespace resources, labels, revisions, dashboards, exported resources, identity and governance,
system/plugin/audit configuration, and execution/task/state/log/metric/artifact/audit history.

Dry-run a bundle:

```console
uv run amesh kestra migration plan export.json --secret-binding vault/production
```

Cutover remains blocked for checksum failure, duplicate or missing identities, cross-tenant
references, reversed or missing history timestamps, plaintext secret-like values, or unresolved
required secret bindings.

Import a bounded batch into an inert side-by-side staging directory:

```console
uv run amesh kestra migration import export.json \
  --target-dir .amesh-migration/staging \
  --max-records 500 \
  --secret-binding vault/production
```

Repeat the command after interruption. The checkpoint resumes at the next record and acknowledged
records are checksum-compared rather than duplicated. When the bundle completes, reconciliation
reports missing or different target records.

## Cutover and rollback

Keep source mutations frozen while applying the final delta. Reconcile counts, identifiers,
chronology and checksums, resolve all required secret bindings, then enable workers before triggers.
For rollback, disable target triggers and workers, retain the source read-only, export imported
identifier and external-action evidence, and resume the source from the final recorded checkpoint.
Historical imports never replay work automatically; shadow comparisons suppress, mock or
idempotently isolate external effects.
