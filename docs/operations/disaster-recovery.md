# Disaster recovery

AMESH recovery points coordinate a PostgreSQL snapshot, the exact object versions visible at that
point, and a redacted deployment-configuration fingerprint. A recovery point is valid only after its
manifest has been uploaded and a `backup_checkpoints` row records the manifest checksum and snapshot
WAL LSN.

## Recovery contract

Authoritative state is the PostgreSQL database, immutable execution/event history, and tenant object
versions. Search and analytics materialized views named `amesh_search_*` or `amesh_analytics_*` are
disposable. Worker heartbeats, service registrations, queue claims, leases and scheduler ownership are
fenced after restoration and must not be treated as live.

The manifest contains:

- the exported PostgreSQL snapshot timestamp, WAL LSN, server version and schema migration;
- a checksum-protected custom-format database dump;
- each active tenant's object URI, SHA-256 checksum, size, backend and provider version identifier;
- the AMESH release and a fingerprint of non-secret database, storage and tenancy references.

Secrets are never copied into the manifest. Back up the referenced Kubernetes Secrets, Helm values,
certificates and provider identity configuration through the platform's protected configuration-backup
process.

## Create and verify a recovery point

The runtime image contains the PostgreSQL 17 client used by the reference PostgreSQL 17 deployment.
AMESH rejects a client older than the source server. The database credential must be able to export a
snapshot; verification also needs permission to create and drop a disposable database on the isolated
recovery target.

```bash
uv run --extra runtime amesh recovery create --actor operator:backup
uv run --extra runtime amesh recovery verify-latest \
  --profile v1 --actor operator:restore-test
```

`verify-latest` performs these gates:

1. verify the manifest checksum recorded in PostgreSQL;
2. read every object by its exact provider version and verify its SHA-256 digest before consumption;
3. restore the custom PostgreSQL archive into a newly created isolated database;
4. stop restored service/worker identities, expire claims and leases, and fence scheduler ownership;
5. rebuild disposable search/analytics projections;
6. run bounded tenant reconciliation and check schema/runtime readiness;
7. drop the isolated database and persist the result in `recovery_exercises`.

A passed result has `objectsVerified == objectsTotal`, no live restored ownership, zero unresolved
reconciliation findings and an empty `unresolvedGaps` list. A failed result remains durable for review.

To create and verify in one invocation:

```bash
uv run --extra runtime amesh recovery exercise \
  --profile v1 --actor operator:dr-exercise
```

## Scheduled exercises

The Helm job is disabled until recovery credentials and an isolated target are configured. Enable a
daily exercise, which keeps the v1 scheduled recovery-point interval below 48 hours:

```bash
helm upgrade --install amesh charts/amesh \
  --set recovery.enabled=true \
  --set 'recovery.schedule=0 3 * * *' \
  --set recovery.profile=v1
```

The CronJob uses `concurrencyPolicy: Forbid`; a second exercise cannot overlap the first. Alert on a
`FAILED` `recovery_exercises.state` or any non-empty `unresolved_gaps`. Do not delete failed evidence
until the gap has been resolved and a later exercise passes.

## Point-in-time recovery procedure

Logical dumps qualify isolated restores, while production PITR uses the PostgreSQL base-backup and
continuous-WAL archive operated for the deployment:

1. select the desired `backup_checkpoints` record and retrieve its checksum-verified manifest;
2. restore the latest base backup before the manifest's `snapshotAt` into an isolated target;
3. replay WAL to the manifest `databaseLsn` (or its `snapshotAt` when the provider accepts time only),
   and stop recovery before opening the database to AMESH services;
4. retrieve tenant objects using each manifest `versionId`, verifying size and SHA-256 before making
   that version current in the recovery bucket;
5. restore the protected configuration references and verify their fingerprint intentionally;
6. run the same ownership fencing, projection rebuild, reconciliation and readiness gates represented
   by `amesh recovery verify-latest`;
7. switch traffic only after the exercise report has no unresolved gap.

Never combine a database point from one manifest with object versions from another. If a provider has
purged a recorded object version, recovery must fail rather than silently use the current object.

## Tenant-scoped transfer

Tenant export/import carries the tenant policy, active flow definitions and exact object versions in a
canonical SHA-256-protected bundle. Import creates a new tenant slug and copies every object through the
same verified streaming path.

```bash
uv run --extra runtime amesh tenant-transfer export source tenant-transfer.json \
  --actor operator:tenant-export
uv run --extra runtime amesh tenant-transfer import tenant-transfer.json destination \
  --actor operator:tenant-import
```

The destination slug must not already exist. A checksum mismatch is rejected before tenant creation.

## Reference objectives and measured evidence

The first stable profile targets RPO at most 48 hours and RTO at most 8 hours. The default daily
schedule bounds the scheduled-backup interval to 24 hours. On 2026-08-22, the checked-in PostgreSQL 17
and versioned-MinIO reference exercise applied all 26 migrations and completed a real isolated restore in
1.017 seconds with a measured 0.553-second recovery-point age, one of one objects verified, zero
unresolved reconciliation findings and zero ownership leaks. This is functional reference evidence,
not a scale or regional-failover claim. The post-GA 4-hour RPO/RTO profile still requires a schedule,
WAL archive and qualification environment sized for that target.
