# ADR-037: Namespace shared resources stay tenant-fenced and value-safe

- Status: Accepted
- Date: 2026-08-22
- Owners: workflow, storage, authorization

## Context

EPIC-207 requires reusable namespace files, typed key-values and secrets without making workflow
revisions carry mutable data or plaintext credentials. Kestra's public namespace-file and KV-store
documentation establishes the compatibility target: files live in internal storage, KV entries are
typed and namespace-scoped, and secrets are resolved when expressions run. AMESH also needs explicit
tenant isolation, optimistic concurrency, audit evidence and portable environment promotion.

## Decision

Namespace resources use three separate PostgreSQL authorities and the existing verified object store:

- Namespace files keep immutable object versions. Metadata points at the current version, parent
  namespaces resolve before the child override, and a child tombstone explicitly hides a parent file.
- Key-values are local to one namespace and strongly typed as string, number, boolean, datetime,
  date, duration or JSON. Writes support TTL, metadata and compare-and-set. A monotonic cursor ledger
  supports bounded polling without including values in change records.
- Secret bindings store only an `env` provider and environment-variable name. The executor resolves
  the environment value immediately before rendering a task that declares the logical secret key.
  Plaintext is redacted before task completion and is never written to a revision, resource API,
  bundle or audit event.

Authorization evaluates independent `list`, `read`, `write`, `delete` and `use` actions. Execution
launch requires `use` for every referenced resource class. Access and mutation audits record identity,
resource coordinates, type, version and checksums but omit KV and secret values.

Promotion uses a checksum-protected `amesh.namespace-resources/v1` bundle. Files are encoded,
key-values retain their declared type, and secrets carry provider references only.

## Consequences

- Existing object-storage durability and tenant fencing apply to namespace files.
- A file move reuses an immutable object version; garbage collection remains governed by existing
  storage retention rather than deleting bytes during a metadata mutation.
- The initial secret provider is deliberately limited to environment variables. Adding Vault or a
  cloud secret manager requires a new provider adapter and qualification, not a plaintext fallback.
- Working-directory materialization remains owned by EPIC-208; EPIC-207 resolves declared namespace
  files to verified internal object URIs.

## References

- [Kestra namespace files](https://kestra.io/docs/concepts/namespace-files)
- [Kestra key-value store](https://kestra.io/docs/concepts/kv-store)
- [Kestra secrets](https://kestra.io/docs/concepts/secret)
