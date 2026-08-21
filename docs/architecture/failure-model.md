# Failure model

| Failure | Expected behavior |
|---|---|
| Webserver dies before commit | Client receives failure or connection loss; retry with same idempotency key is safe |
| Webserver dies after commit before response | Retry returns original committed result |
| Outbox publisher dies after publish before mark | Message may redeliver; consumer inbox deduplicates |
| Executor dies mid-decision | No partial state outside transaction; another executor reprocesses event |
| Executors race for one task | One compare-and-swap owns the attempt and dispatch; losing executors observe the committed running state |
| Failed prerequisite survives executor loss | Restarted orchestration terminates the unsatisfiable graph with stable failed/blocked diagnostics |
| Scheduler partition | New epoch fences old scheduler; duplicate occurrence identity prevents double launch |
| Worker loses network | Lease expires; policy requeues or quarantines; late completion is fenced |
| Runner continues after lease loss | Workload may have external effects; platform rejects stale result and surfaces ambiguity |
| Database unavailable | State-changing acceptance stops; already-running external workloads follow bounded worker policy |
| Event bus unavailable | Outbox retains committed messages; compact API may continue until configured pressure limit |
| Object storage unavailable | Tasks requiring files wait or fail by policy; metadata never pretends upload succeeded |
| Search unavailable | Orchestration continues; read APIs fall back where supported and show stale/degraded status |
| Secret provider unavailable | New secret-dependent work retries or fails; cached secrets follow bounded policy |
| Plugin crashes | Invocation is retried or failed by policy; supervisor restarts service; control plane remains alive |
| Poison event | Consumer quarantines after bounded retries; partition handling follows documented policy |
| Clock skew | Leases use database/authority time where practical; deadlines use monotonic local clocks |
| Restore from backup | Search rebuilds, messages reconcile, leases expire and ambiguous external work is quarantined |

## Ambiguous external work

No architecture can infer an external side effect after a worker disappears unless the destination
supports idempotency or queryable operation identity. The platform records `UNKNOWN_EXTERNAL_OUTCOME`
evidence and applies plugin-declared recovery strategy. It never marks success without evidence.
