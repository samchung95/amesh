# Self-hosted plugin registry

AMESH includes an open, filesystem-backed registry API for immutable plugin releases. The normative
`amesh.plugin-registry/v1` contract is published as `schemas/plugin-registry.schema.json`; the same
models are exported by `amesh.plugin_sdk`.

## Release contract

Each published release binds one plugin name and semantic version to one SHA-256 bundle digest. A
second bundle with the same name and version is rejected. Publication requires metadata for license,
source, documentation, supported platform range, SDK range and changelog plus three signed
attachments:

- SPDX or CycloneDX software bill of materials;
- vulnerability report;
- in-toto/SLSA-style provenance statement.

The reference self-hosted profile signs bundle bytes, attachment bytes, release metadata and the
registry index with HMAC-SHA-256. Verification uses `hmac.compare_digest`; signing keys must contain
at least 32 bytes and are selected by key ID. This symmetric-key profile is suitable for a controlled
self-hosted deployment. Public release key management and official artifact qualification remain
owned by EPIC-612 and URS-NFR-SECURITY-007.

## Distribution policy

Registry clients fail closed for network sources unless their HTTP(S) origin is allowlisted.
Operators may map an allowed origin to an internal mirror, set an HTTP proxy or disable all network
registry access. Local filesystem indexes remain available for air-gapped use. An offline export is a
signed ZIP containing the index and every referenced content-addressed blob; import verifies index,
metadata, artifact and attachment signatures before writing anything.

Yanking signs a new metadata state and prevents the version from becoming active in a refreshed
catalog. Its bundle, evidence, digest and reason remain available to historical pinned executions.

## API

Authorized viewers can list the signed index and individual releases, download content-addressed
bundles and export the registry. Plugin managers can publish, yank and import:

```text
GET  /api/v1/plugin-registry/index
POST /api/v1/plugin-registry/packages
GET  /api/v1/plugin-registry/packages/{name}/{version}
POST /api/v1/plugin-registry/packages/{name}/{version}/yank
GET  /api/v1/plugin-registry/blobs/{sha256-hex}
GET  /api/v1/plugin-registry/offline-export
POST /api/v1/plugin-registry/offline-import
```

Marketplace responses include downloads, last-maintained time, certification and security status.
Those fields are explicitly informational and never replace signature, provenance or policy checks.

## Configuration

The Compose development profile persists the registry below the existing `plugin-data` volume.
Production deployments must replace the development signing key and distribute verification keys
through their secret manager.

```text
PLUGIN_REGISTRY_ROOT=/var/lib/amesh/plugins/registry
PLUGIN_REGISTRY_SIGNING_KEY_ID=release-2026
PLUGIN_REGISTRY_SIGNING_KEY=secret://plugin-registry-signing-key
PLUGIN_REGISTRY_VERIFICATION_KEYS={"release-2026":"secret value"}
PLUGIN_REGISTRY_ALLOWED_ORIGINS=["https://registry.example"]
PLUGIN_REGISTRY_MIRRORS={"https://registry.example":"https://mirror.internal"}
PLUGIN_REGISTRY_PROXY_URL=http://proxy.internal:8080
PLUGIN_REGISTRY_OFFLINE=false
```

Run the self-hosted conformance suite with:

```powershell
uv run pytest -q tests/plugins/test_registry.py tests/plugin_sdk/test_discovery.py
```
