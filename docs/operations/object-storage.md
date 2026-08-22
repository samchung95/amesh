# Object storage operations

AMESH stores large workflow payloads and artifacts behind one tenant-scoped streaming contract. The
supported production adapters are S3-compatible storage, Azure Blob Storage and Google Cloud Storage;
MinIO is the checked-in self-hosted conformance environment.

## Backend configuration

Set `OBJECT_STORAGE_BACKEND` to `s3`, `azure` or `gcs`. Every backend uses
`OBJECT_STORAGE_BUCKET` as its bucket or Azure container and writes only below
`tenants/<tenant-id>/`. Object URIs are opaque (`s3://`, `azure://` or `gs://`) and an adapter rejects
another tenant's prefix before making a provider request.

| Capability | S3 compatible | Azure Blob | Google Cloud Storage |
|---|---|---|---|
| Private/custom endpoint | `OBJECT_STORAGE_ENDPOINT` | `OBJECT_STORAGE_AZURE_ACCOUNT_URL` | `OBJECT_STORAGE_GCS_ENDPOINT` |
| Static credential | access/secret keys | account key | service-account file |
| Workload identity | ambient AWS provider chain | `DefaultAzureCredential` | application default credentials |
| Customer-managed encryption | KMS key ID | encryption scope | Cloud KMS key name |
| Proxy/custom CA | shared proxy and CA settings | shared proxy and CA settings | shared proxy and CA settings |

Set `OBJECT_STORAGE_WORKLOAD_IDENTITY=true` to omit static credentials. The Helm chart defaults to
that mode so an operator can attach AWS IRSA, Azure Workload Identity or GKE Workload Identity to the
AMESH service account. Static S3/Azure credentials may instead come from
`objectStorage.existingSecret`. `OBJECT_STORAGE_ENCRYPTION_KEY_ID`,
`OBJECT_STORAGE_PROXY_URL` and `OBJECT_STORAGE_CA_FILE` are optional shared settings.

For local development, `docker compose up -d postgres minio minio-init` creates the `amesh` bucket
and enables versioning before the API starts.

## Integrity and consistency

Uploads are multipart or resumable and keep only one provider part in memory. Every object receives a
SHA-256 digest in provider metadata. After a write, AMESH retries `head` according to
`OBJECT_STORAGE_CONSISTENCY_ATTEMPTS` and `OBJECT_STORAGE_CONSISTENCY_DELAY_SECONDS`, then compares
the visible size and digest with the completed upload.

Downloads are verified before bytes reach the caller. AMESH hashes the provider stream into a
spooled temporary file, retaining at most `OBJECT_STORAGE_SPOOL_MEMORY_BYTES` in process memory, and
only yields the file after size and digest match. A mismatch raises `ObjectIntegrityError` and
increments `amesh_storage_corruption_total`.

`VerifiedObjectStore.get_range` maps an inclusive start/exclusive end byte interval to each
provider's native range mechanism. The service rejects invalid or out-of-object intervals and checks
the returned length. Use the normal `get` path when a full-object cryptographic verification is
required; a partial range cannot independently reproduce the stored full-object SHA-256 digest.

Object metadata records the provider URI and version, tenant-relative key, size, content type,
SHA-256 digest, encryption key, creation time, creator, lineage references, retention timestamp and
legal-hold state. Creator and lineage values are written with the object and survive verified backend
migration.

Use the configured backend and tenant to verify an inventory:

```powershell
uv run amesh --tenant default storage validate
uv run amesh --tenant default storage validate --metadata-only
```

The command exits nonzero when content verification finds corruption. Prometheus also publishes
backend-bounded request, latency, transfer-byte, inventory-byte, object-count and corruption metrics;
tenant IDs and object keys are never metric labels.

## Retention and deletion

Lifecycle metadata is stored with the object. A lifecycle delete is blocked when the authoritative
reference check reports the object as referenced, a legal hold is active or the retention timestamp
is in the future. An accepted delete returns an explicit deletion-marker outcome. Production buckets
must enable versioning or provider soft delete so EPIC-609 recovery can restore a prior object version.

Callers must use `VerifiedObjectStore.apply_lifecycle` and pass the result of their authoritative
reference check; direct provider deletes bypass AMESH policy and are unsupported.

Automated garbage collection uses `VerifiedObjectStore.collect_unreferenced`. It asks the caller's
authoritative reference checker before deletion and blocks objects newer than
`OBJECT_STORAGE_GC_SAFETY_WINDOW_SECONDS` (24 hours by default), as well as referenced, retained or
held objects. The bounded `limit` controls work per pass.

## Backend migration

Create a JSON file containing the destination `Settings` fields, including its backend, bucket,
endpoint or account URL, identity mode and encryption key. Then run:

```powershell
uv run amesh --tenant default storage migrate destination-storage.json `
  --checkpoint .amesh-storage-migration.json
```

Objects copy in deterministic key order through verified source downloads and verified destination
uploads. The checkpoint is atomically replaced after each object and records the last key, object and
byte counts, and both backend identities. Re-running the same command resumes after the last committed
key. Source objects are not deleted automatically.

## Qualification boundary

The automated suite covers the common contract, deterministic S3/Azure/GCS provider fakes,
cross-tenant rejection, corruption injection, interrupted migration and a 10 GiB logical transfer
below the 256 MiB process-memory target. The development gate also runs multipart, lifecycle,
inventory and versioned-delete behavior against real MinIO. Live managed-provider certification,
private-network policy and provider outage drills remain environment-specific release qualification
under EPIC-706; they are not implied by the portable adapter tests.
