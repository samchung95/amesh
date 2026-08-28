# High-availability operations

AMESH service processes are disposable. PostgreSQL queue rows, events, leases and fences remain the
orchestration source of truth; Kubernetes placement and process memory do not. The Helm chart runs
the webserver, executor, scheduler, worker gateway, indexer and maintenance roles as independent
Deployments.

## Reference profiles

| Profile | Web | Executor | Scheduler | Worker | Indexer | Maintenance | Availability intent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Small | 1 | 1 | 1 | 1 | 1 | 1 | Functional single-instance deployment; no instance-loss claim |
| Medium | 2 | 2 | 2 | 2 | 2 | 1 | Profile M, zone-spread critical roles, one planned/unplanned stateless loss |
| Large | 4 | 4 | 3 | 4 | 3 | 2 | Higher control-plane concurrency; PostgreSQL remains the shared limit |

Install a profile by layering its values over the chart defaults:

```bash
helm upgrade --install amesh charts/amesh \
  --namespace amesh-system \
  --values charts/amesh/profiles/medium.yaml \
  --wait --timeout 10m
```

Medium and large use hard `topology.kubernetes.io/zone` spread constraints. Critical roles have
PodDisruptionBudgets and rolling updates with zero unavailable pods. The small profile disables PDBs
so it can run on one node. Use the large profile only after measuring the target PostgreSQL and
object-store deployments; replica count does not remove shared-dependency limits.

## Role ownership

- `webserver` serves authenticated REST/UI traffic and registers HTTP readiness.
- `executor` resumes durable running executions after an instance disappears.
- `scheduler` claims fenced schedule cursors and coordinates durable backfills.
- `worker` recovers expired worker claims; external task workers retain their own protocol fences.
- `indexer` moves committed transactional outbox records into durable partitioned lanes.
- `maintenance` runs bounded tenant reconciliation and invariant repair.

Each process registers `(role, instanceName)` with a random incarnation ID and monotonic generation.
A replacement using the same identity increments the generation and changes the ID, so the old
process can no longer heartbeat. Scheduler, worker and queue mutations retain their existing
database-time leases and fencing tokens. This prevents a stale pod or split-brain process from
committing ownership after replacement.

## Quorum dependencies

AMESH does not use Kubernetes leader-election data as orchestration truth. Availability depends on:

- an external PostgreSQL HA topology that can elect exactly one writable primary and preserve
  acknowledged commits;
- replicated or versioned S3-compatible object storage for durable artifacts;
- Kubernetes only for stateless placement, traffic routing and process replacement.

Place PostgreSQL and object storage across failure domains according to their operators' quorum
rules. A two-pod AMESH role does not compensate for a single non-redundant PostgreSQL primary.

## Status, version skew and ownership

An instance administrator can inspect all observed roles:

```bash
curl -fsS -H 'Authorization: Bearer development-token' \
  http://localhost:8000/api/v1/operations/topology
```

The response shows incarnation generation, liveness, current/draining/stopped state, version
compatibility, observed failure domain, owned work summary, durable partition strategy and dependency
health. Each role summary is `REDUNDANT`, `AVAILABLE`, `DRAINING` or `UNAVAILABLE`. `REDUNDANT`
requires at least two ready instances in distinct observed failure domains.

`GET /ready` evaluates every role named by `SERVICE_ENABLED_ROLES`. Roles not in that set are reported
as `DISABLED` and do not affect HTTP readiness. Enabled roles use these semantics:

- `STARTING`: registered, live, but no successful work cycle has completed yet;
- `READY`: live and the most recent bounded cycle succeeded;
- `DEGRADED`: live, but a caught cycle failure is persisted with `lastFailureAt`, a redacted
  `lastFailure` summary and incremented `consecutiveFailures`;
- `DRAINING`: live but intentionally taking no new cycle;
- `UNAVAILABLE`: no live instance is registered.

Every successful cycle updates `lastSuccessAt`, clears the failure summary and resets
`consecutiveFailures`. Every enabled role must have at least one live `READY` instance for aggregate
readiness to return HTTP 200. `/health` remains process liveness only and never substitutes for this
progress check.

During a rolling upgrade, watch `versionSkew`, role versions, stale instances, queue diagnostics and
reconciliation metrics. Mixed versions are visible and expected only during the documented overlap
window.

## Drain and replace

The chart's pre-stop hook requests an audited drain using the instance's current resource version.
The role finishes its active bounded cycle, observes `DRAINING`, takes no new cycle, marks itself
stopped and exits. To drain manually:

```bash
curl -fsS -X POST \
  -H 'Authorization: Bearer development-token' \
  -H 'Content-Type: application/json' \
  http://localhost:8000/api/v1/operations/services/<instance-id>/drain \
  -d '{"expectedVersion": 12, "reason": "node maintenance"}'
```

A stale expected version returns `409`; refresh topology before retrying. Do not force-delete the
final ready scheduler or executor during planned maintenance. If a pod disappears without draining,
Kubernetes replaces it, old scheduler/worker writes fail their fences, durable polling resumes after
lease expiry and maintenance reconciliation repairs safe projection drift.

Liveness probes only verify that the role process can execute; readiness verifies a live `READY`
registry heartbeat through PostgreSQL. A database outage therefore removes the role from traffic or
work eligibility without turning a healthy-but-degraded process into a restart loop.

## Qualification boundary

Automated tests prove role separation, fenced incarnation replacement, stale drain rejection,
zone-aware redundancy reporting, API authorization and S/M/L chart contracts. Existing scheduler,
worker, queue and reconciliation suites prove stale-owner rejection and durable takeover. The prior
MVP Kubernetes fault run deleted server, worker and task pods without losing or duplicating its 270
accepted executions.

The 100,000-execution/24-hour mixed workload and measured two-to-four replica scaling efficiency are
long-running certification gates owned by EPIC-611. PostgreSQL/object-store multi-zone failover must
also be repeated against the actual operated dependencies; this local functional qualification does
not certify an arbitrary external database or object store.
