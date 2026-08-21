# Deployment architecture

## Reference environment

The first real production environment and release-qualification topology is **on-premises Kubernetes deployed through Helm**. See [`on-premises-kubernetes.md`](on-premises-kubernetes.md) for the full design.

The reference environment has no mandatory public-cloud control plane, managed database, managed object store, hosted telemetry service or licence server.

## Supported profiles

### Development

Docker Compose starts AMESH, PostgreSQL and MinIO. No separate internal broker or search service is required. Development authentication must fail closed when production mode is selected.

Development is not a durability or availability qualification environment.

### Single-host production

A single deployable may host webserver, executor, scheduler, trigger, projector, maintenance and worker roles. PostgreSQL remains external or separately supervised, and S3-compatible object storage is recommended. Local-process and Docker runners are supported.

This profile is secondary and is not the v1 performance reference.

### On-premises Kubernetes production

Helm is the reference packaging target. Roles scale independently, use PodDisruptionBudgets and topology spread, and coordinate solely through PostgreSQL leases/queues plus object storage. Kubernetes task execution uses dedicated runner service accounts, execution namespaces and deny-by-default network policy.

The checked-in chart materializes webserver, executor, scheduler, worker, indexer and maintenance as
separate Deployments. See the [HA runbook](../operations/high-availability.md) for the tested S/M/L
replica profiles and graceful-drain contract.

The chart supports external PostgreSQL, S3-compatible object storage, ingress, TLS, identity, secrets and observability components without requiring a specific vendor.

### Portable Kubernetes

The same chart must run on upstream Kubernetes and at least one common on-premises distribution. Distribution-specific values are permitted, but workflow and execution semantics must remain portable.

## Stateful dependencies

- PostgreSQL is required for resource state, events, queues, leases, projections and audit records.
- S3-compatible object storage is required for production-scale artifacts, namespace files, migration bundles and large payloads.
- Identity and secret providers are optional integrations with safe local alternatives for development.
- No Kafka, Redpanda, NATS, Elasticsearch or OpenSearch cluster is required by the baseline architecture.
- Kubernetes etcd is never authoritative for execution runtime state.

## Packaging rules

- Official images support linux/amd64 and linux/arm64.
- Images run as non-root with read-only filesystems where practical.
- Configuration is validated at startup and effective non-secret configuration is observable.
- Database migrations are explicit, reversible where possible and classified before release.
- Every release includes checksums, SBOM, provenance and AGPL corresponding-source availability.
- Every stable release produces a signed offline bundle for disconnected installation and upgrade.
- The offline bundle includes images, Helm charts, CRDs, migrations, selected plugins, checksums, signatures, SBOMs, provenance and operator documentation.
- Update checks and product telemetry are disabled by default or explicitly opt-in.

## v1 qualification targets

The on-premises Kubernetes reference profile qualifies:

- 99.9% monthly control-plane availability objective;
- scale profile M: 100,000 executions/day, 1,000 active task runs, 50 task starts/second and 10 million retained execution records;
- first stable release recovery: RPO no more than 48 hours and RTO no more than 8 hours;
- clean installation, offline installation, rolling upgrade, rollback rehearsal, backup/restore and selected fault scenarios.
