# High availability and disaster recovery

## Dependency classes

- **Authoritative:** PostgreSQL resources, execution/event state, queues, leases and projection checkpoints; object storage for large files and artifacts.
- **Rebuildable:** PostgreSQL search/analytics projections and derived caches.
- **Ephemeral:** service processes, notifications, local workspaces and in-memory caches.

## Availability objective

The accepted monthly control-plane target is **99.9%**, excluding declared maintenance. Loss of one stateless service instance must not lose acknowledged work. PostgreSQL and object-storage availability are deployment responsibilities with tested on-premises reference topologies.

The 99.9% objective is separate from disaster recovery. Normal pod, node or stateless-service loss should recover within minutes and remain inside the availability budget.

## Accepted recovery objectives

The first stable release uses the deliberately minimal recovery gate:

| Profile | RPO | RTO | Release role |
|---|---:|---:|---|
| v1 minimal/community baseline | <= 48 hours | <= 8 hours | Required stable-release gate |
| Post-GA hardened reference | <= 4 hours | <= 4 hours | Planned target; not a v1 blocker |

These are disaster-recovery objectives after loss of authoritative data or an environment, not ordinary instance-failover targets.

The minimal v1 values must be disclosed prominently. An operator with stricter business requirements must configure and test a tighter backup, replication and restore programme rather than infer that 48-hour data loss is universally acceptable.

## HA design

- Run multiple stateless replicas for webserver, executor, scheduler, trigger, projector and worker-gateway roles.
- Use expiring leases and fencing for stateful ownership.
- Use a highly available PostgreSQL deployment with automated failover and tested connection recovery.
- Ensure object storage is durable and versioned or snapshot-capable.
- Do not acknowledge state-changing requests while PostgreSQL commit status is unknown.
- Treat `LISTEN/NOTIFY` loss as normal; durable polling resumes work.
- Use readiness, graceful shutdown, PodDisruptionBudgets and topology spread in the on-premises Kubernetes reference deployment.
- Never make Kubernetes leader-election objects or etcd authoritative for workflow execution state.

## Backup set

A recoverable backup includes:

1. PostgreSQL base backup and WAL/PITR material, including queue and projection-checkpoint tables;
2. versioned object storage or a storage-consistent snapshot;
3. configuration and secret references;
4. plugin bundles or a registry snapshot;
5. release, schema, compatibility-target and reducer-version metadata;
6. Kubernetes and Helm configuration needed to recreate the service topology;
7. identifier maps and manifests for active migrations.

Search projections may be excluded only when their rebuild time fits the selected RTO.

## Backup policy for the v1 gate

The reference runbook must demonstrate a backup cadence and retention policy capable of meeting RPO <= 48 hours. A scheduled isolated restore must demonstrate RTO <= 8 hours on the published reference topology.

A backup job reporting success is insufficient. Verification requires restoration, checksum validation, reconciliation and measured service readiness.

## Restore sequence

1. Isolate the target environment.
2. Restore PostgreSQL and object storage to a coordinated point.
3. Install matching platform, compatibility and plugin versions.
4. Validate schema, event and object checksums.
5. Keep triggers, dispatch and agent tools disabled.
6. Expire stale leases and reconcile queue, inbox and outbox records.
7. Rebuild projections where required.
8. Review ambiguous running external jobs and model/tool calls.
9. Enable workers, then executors, then triggers, then general writes.
10. Produce a restore evidence report and compare actual RPO/RTO with the selected profile.

## Qualification evidence

A recovery report records:

- backup and restore timestamps;
- recovered PostgreSQL LSN or equivalent point;
- object-store version/snapshot point;
- measured data-loss interval;
- time to API readiness and time to orchestration readiness;
- queue, lease, trigger and object reconciliation results;
- missing, corrupt or ambiguous items;
- topology and bill of materials;
- operator actions and unresolved gaps.
