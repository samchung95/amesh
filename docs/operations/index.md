# Operate AMESH

Choose a deployment shape first; the operational guarantees differ.

| Profile | Intended use | Guide |
| --- | --- | --- |
| Development Compose | Local UI, examples and tests | [First-run onboarding](onboarding.md) |
| Compact | Small single-host control plane with external PostgreSQL authority | [Compact deployment](compact-deployment.md) |
| Session orchestrator | Session-focused self-hosted instance or cluster | [Session deployment](../how-to/run-session-orchestrator-self-hosted.md) |
| Distributed/Kubernetes | Separated roles, durable queue and redundant workers | [Kubernetes operator](kubernetes-operator.md) |

The compact profile is one failure domain and does not itself prove an HA objective. Use the
[high-availability topology](high-availability.md), [disaster-recovery runbook](disaster-recovery.md)
and their recorded qualification evidence before making a production claim.

## Configure and secure

- [Configuration and feature flags](configuration.md)
- [Authentication](authentication.md), [authorization](authorization.md) and
  [multi-tenancy](multi-tenancy.md)
- [Credentials and secret references](credentials.md)
- [Networking and TLS boundary](networking.md)
- [Plugin and runner policy](../plugin-sdk/discovery-and-resolution.md)

The development token is unavailable outside development mode. Production startup rejects known
development credentials and other contradictory production settings.

## State and execution infrastructure

- [PostgreSQL](postgresql.md) is authoritative for resources, queues, leases and events.
- [Object storage](object-storage.md) owns durable artifacts, files and governed images.
- [Distributed queue](distributed-queue.md) describes claiming and recovery.
- [Local process](local-process-runner.md), [Docker/OCI](docker-oci-runner.md) and
  [Kubernetes](kubernetes-runner.md) runners define different execution authorities.
- [Scheduler and triggers](triggers.md) cover timed and event-driven starts.

## Observe, retain and recover

- [Observability](observability.md) and [audit evidence](audit-evidence.md)
- [Retention](retention.md), [task cache](task-cache.md) and [execution files](execution-files.md)
- [Upgrades](upgrades.md), [backup and restore](disaster-recovery.md) and
  [session-orchestrator migration](session-orchestrator-migration.md)
- [Session service operations](agent-session-service.md) and
  [session administration](../how-to/administer-agent-sessions.md)

## Local quality gate

Run the supported Docker-local aggregate before proposing a change:

```powershell
.\scripts\verify-local.ps1 -Suite all
```

Use [Run local verification](../how-to/run-local-verification.md) for individual suites, the local
push gate and packaging evidence. The documentation-only suite is available as
`.\scripts\verify-local.ps1 -Suite docs`.
