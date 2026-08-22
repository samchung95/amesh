# Discover, resolve and install plugins

AMESH builds an immutable `amesh.plugin-catalog/v1` snapshot from the embedded core distribution,
configured package directories, configured registry indexes and the offline installation root. A
refresh creates a new snapshot; an existing flow revision or execution retains its original
`amesh.plugin-resolution/v1` package versions and SHA-256 digests.

## Configure sources

`PLUGIN_DIRECTORIES` and `PLUGIN_REGISTRIES` are JSON arrays. Directory sources recursively find one
`amesh-plugin.json`, `.yaml` or `.yml` manifest per package root and digest every package file.
Registry sources point to a local path, `file://` URI or HTTP(S) index with this shape:

```json
{
  "schemaVersion": "amesh.plugin-registry/v1",
  "packages": [
    {
      "bundle": "packages/example-task-1.2.0.amesh-plugin",
      "contentDigest": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    }
  ]
}
```

Relative bundle locations resolve against the index. AMESH downloads or reads the bundle, verifies
the declared digest, rejects unsafe archive paths and materializes the content under
`PLUGIN_INSTALL_ROOT/<digest>`. `PLUGIN_REGISTRY_TIMEOUT_SECONDS` defaults to 10 seconds. Registry
signatures, SBOMs and publisher policy belong to EPIC-305; SHA-256 content verification is mandatory
now and cannot be disabled.

For Docker Compose, `plugin-data` persists `/var/lib/amesh/plugins`. In a replicated deployment the
installation root must be a shared writable volume, or every replica must use the same immutable
directory/registry configuration. Do not use a pod-local root for an operator upload in HA.

## Inspect and refresh

```powershell
uv run amesh --token development-token plugins list
uv run amesh --token development-token plugins refresh
```

The API equivalents are `GET /api/v1/plugins` and `POST /api/v1/plugins/refresh`. Catalog records are
classified as:

- `active`: highest compatible non-deprecated version selected by default;
- `installed`: another compatible version available for an explicit dependency constraint;
- `deprecated`: retained for historical evidence but not selected for a new resolution;
- `incompatible`: SDK/protocol/dependency requirements cannot be met;
- `quarantined`: invalid content, duplicate identity or duplicate type ownership.

Catalog reads require plugin view permission. Refresh and installation require instance-level plugin
management permission.

## Install an offline bundle

An offline bundle is a ZIP archive with exactly one manifest. Calculate its SHA-256 digest and send
both the bundle and digest:

```powershell
$digest = (Get-FileHash .\example.amesh-plugin -Algorithm SHA256).Hash.ToLowerInvariant()
uv run amesh --token development-token plugins install .\example.amesh-plugin --sha256 $digest
```

The CLI sends the raw bundle to `POST /api/v1/plugins/install?contentDigest=sha256:...`. Installation
is atomic and idempotent by digest. A digest mismatch, malformed manifest, symlink or path traversal
fails before the package appears in the catalog.

## Deterministic resolution and isolation

Each type reference resolves to one package name. The resolver selects the highest exact SemVer that
satisfies all transitive constraints, then records the package version, content digest, source tier
and resource mapping. Conflicting constraints fail flow activation with a structured
`plugin.resolution.dependency_conflict` error.

Each resolved package receives its own content root and exact dependency-root map. Launch plans set
`PYTHONNOUSERSITE=1` and never alter the control-plane process import path. EPIC-302 and EPIC-303 own
trusted and isolated execution respectively; neither may replace these revision pins with a newer
catalog selection while an execution is running.
