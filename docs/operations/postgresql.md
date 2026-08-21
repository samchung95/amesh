# PostgreSQL operations and qualification

AMESH supports PostgreSQL 15, 16, 17 and 18 for its transactional backend. Every CI run applies the
complete migration set to all four majors and exercises migration repeatability plus backup-checkpoint
operations. PostgreSQL supports each major for five years and recommends the newest minor release;
AMESH deliberately sets a narrower version-15 floor even while version 14 remains upstream-supported.
See the [PostgreSQL version policy](https://www.postgresql.org/support/versioning/).

## Connection budget and TLS

Each API or worker process uses an async queue pool with pre-ping, recycling and asyncpg's prepared
statement cache. Its maximum database connections are `DATABASE_POOL_SIZE + DATABASE_MAX_OVERFLOW`.
Multiply that value by the maximum pod/process count, include migration and operator connections, and
keep the result under the server or proxy budget. Configure:

| Setting | Default | Purpose |
| --- | ---: | --- |
| `DATABASE_POOL_SIZE` | 10 | Persistent connections per process |
| `DATABASE_MAX_OVERFLOW` | 10 | Short-lived overflow per process |
| `DATABASE_POOL_TIMEOUT_SECONDS` | 30 | Maximum checkout wait |
| `DATABASE_POOL_RECYCLE_SECONDS` | 1800 | Maximum pooled connection age |
| `DATABASE_PREPARED_STATEMENT_CACHE_SIZE` | 100 | Prepared statements per connection |
| `DATABASE_TLS_MODE` | `disable` locally; `verify-full` in Helm | `disable`, encrypted `require`, or certificate/hostname-verifying `verify-full` |
| `DATABASE_TLS_CA_FILE` | system roots | Optional provider/customer CA bundle |

Production profiles use `verify-full`; `require` is an explicit compatibility escape hatch that
encrypts without authenticating the server. AWS RDS documents forced SSL and TLS behavior in its
[PostgreSQL SSL guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Concepts.General.SSL.html),
Azure recommends hostname/certificate verification and TLS 1.2 or 1.3 in its
[TLS guide](https://learn.microsoft.com/en-us/azure/postgresql/security/security-tls), and Cloud SQL
documents its managed CA modes in the
[PostgreSQL instance settings](https://cloud.google.com/sql/docs/postgres/instance-settings).

Set `DATABASE_READ_REPLICA_URL` only for a replica with the same schema and tenant-role configuration.
AMESH routes only flow-list and execution-list reads there; execution detail, graph, authorization,
scheduler, queue, lease and all mutation paths remain on the primary. Replica loss may fail those two
stale-tolerant endpoints but cannot alter orchestration decisions.

## Qualification report

Run the same check against self-managed PostgreSQL or a managed endpoint:

```bash
uv run python scripts/qualify_postgres.py \
  --profile self-managed \
  --max-p95-ms 50 \
  --output postgres-qualification.json
```

Add `--require-tls` for every production/managed run. The command fails on unsupported majors, missing
critical indexes, inactive required TLS or a `SELECT 1` p95 above the declared threshold. Its report
contains JSON `EXPLAIN` plans for queue claim, outbox publication and due-schedule reads, the installed
migration version, table size/dead-row/autovacuum/analyze inventory and the latest backup checkpoint.
The 50 ms p95 is a connectivity/control-query guard, not a throughput claim.

Local qualification on 2026-08-22 applied the then-current 22 migrations and passed the checkpoint/maintenance
contract on each supported major:

| PostgreSQL | `SELECT 1` p95 | Missing critical indexes | Result |
| ---: | ---: | ---: | --- |
| 15 | 0.437 ms | 0 | Pass |
| 16 | 0.447 ms | 0 | Pass |
| 17 | 0.477 ms | 0 | Pass |
| 18 | 0.469 ms | 0 | Pass |

On PostgreSQL 17, queue claim and outbox publication selected their partial indexes with index-only
scans. The due-schedule plan selected `scheduler_states_due_idx` through a bitmap index/heap scan before
its bounded sort. These are empty-schema control plans; every environment must retain its JSON plan and
repeat the report with representative data before raising load limits.

The repository CI matrix is the release gate for self-managed PostgreSQL 15–18. Credentialed AWS RDS,
Azure Flexible Server and Google Cloud SQL runs are deferred to EPIC-706 reference environments; a
release must not claim those provider profiles until their generated reports are attached.

## Maintenance boundaries

The qualification report is the starting inventory for autovacuum lag, dead-row pressure, statistics
age, relation size and partition presence. Operators retain PostgreSQL autovacuum, run `ANALYZE` after
bulk imports, and investigate sustained dead-row growth before changing per-table vacuum settings.
Queue and scheduler transactions remain short and use the critical partial indexes; maintenance must
not hold locks across worker or network operations.

Profile M keeps hot transactional tables unpartitioned because its qualified envelope does not justify
the operational cost of a live partition-key rewrite. Retention/purge and a higher-volume partitioning
profile remain EPIC-608 work. Crossing the published envelope requires a new plan report and migration,
not ad-hoc production DDL.

## Backup-consistent checkpoint

First produce and durably store a versioned object manifest. Then record its checksum with the current
PostgreSQL WAL location:

```bash
uv run python scripts/record_backup_checkpoint.py \
  --manifest-uri s3://amesh/backups/2026-08-22/objects.json \
  --manifest-sha256 <lowercase-sha256> \
  --actor operator@example.com
```

`backup_checkpoints` stores the database LSN, exact schema migration, manifest URI/checksum, actor and
database timestamp in one transaction. The base backup and WAL archive must cover that LSN; the object
store must retain every version named by the manifest. A restore selects a checkpoint, restores
PostgreSQL to at least its LSN, verifies the object manifest checksum and then follows the staged
reconciliation sequence in [High availability and disaster recovery](../architecture/ha-and-dr.md).
