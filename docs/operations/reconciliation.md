# Reconciliation operations

AMESH scans durable PostgreSQL state for recoverable drift every 60 seconds. A tenant administrator
can also run a targeted scan through `POST /api/v1/reconciliations`. Every run and finding is durable,
tenant-scoped and available through the corresponding list and detail endpoints.

## Invariants and actions

| Invariant | Evidence | Apply behavior |
| --- | --- | --- |
| `EXPIRED_LEASE` | A claimed queue row has passed its database-time lease | Requeue when attempts remain; quarantine an exhausted claim |
| `ORPHAN_TASK_RUN` | A running task has no matching current attempt | Quarantine for operator review |
| `STUCK_EXECUTION` | An active execution is stale and has no live attempt | Quarantine for operator review |
| `MISSING_DISPATCH` | A task-start event has no outbox projection | Rebuild the outbox row from the immutable event |
| `UNPROJECTED_EVENT` | An execution or task event has no outbox projection | Rebuild the outbox row from the immutable event |
| `MISSING_SCHEDULE_PROJECTION` | An enabled cron or interval trigger has no scheduler cursor | Recreate the disposable cursor; the scheduler initializes its next occurrence |

Repairs use the observed aggregate version or fencing token and are idempotent. If the authoritative
row changes before apply, AMESH quarantines the finding rather than applying a stale decision. The
`maxRepairs` cap bounds mutation per run; otherwise repairable findings remain `DETECTED` for the next
pass. Apply repairs, deferrals and quarantines create audit events with the operator, reason, run ID,
observed version and evidence.

## Preview and apply

Use dry-run first for manual intervention:

```bash
curl -fsS -X POST http://localhost:8000/api/v1/reconciliations \
  -H 'Authorization: Bearer development-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "DRY_RUN",
    "executionId": "0198d8f3-8977-7f28-8ca7-ae47d0ad6dc1",
    "staleAfterSeconds": 300,
    "maxFindings": 500,
    "idempotencyKey": "inspect-0198d8f3",
    "reason": "investigate stalled execution"
  }'
```

Change `mode` to `APPLY`, set `maxRepairs` from 1 to 100 and use a new idempotency key to repair safe
findings. Repeating the same tenant/idempotency key returns the original run without applying a repair
again. Omit the target for a tenant scan, or select exactly one of `executionId`,
`triggerDefinitionId`, `workerId`, or a `since`/`until` time range. List and fetch evidence with:

```bash
curl -fsS -H 'Authorization: Bearer development-token' \
  'http://localhost:8000/api/v1/reconciliations?limit=20'
curl -fsS -H 'Authorization: Bearer development-token' \
  'http://localhost:8000/api/v1/reconciliations/<run-id>'
```

The automatic worker uses apply mode with `WORKER_RECONCILIATION_MAX_REPAIRS=10`. Configure its scan
period with `WORKER_RECONCILIATION_INTERVAL_SECONDS` and stale threshold with
`WORKER_RECONCILIATION_STUCK_AFTER_SECONDS`. The lower bounds are 5 seconds for the interval and 30
seconds for stale detection.

## Metrics and response

Alert on sustained unresolved findings rather than a single bounded pass:

- `amesh_reconciliation_runs_total{mode}`
- `amesh_reconciliation_findings_total{invariant,disposition}`
- `amesh_reconciliation_unresolved{invariant}`
- `amesh_reconciliation_duration_seconds`

For `QUARANTINED` findings, inspect the finding detail and linked audit event before changing
authoritative execution or task state. Re-run a dry scan after resolving the cause. A recoverable
finding should disappear after one successful apply pass; if it remains, stop automatic intervention
for that tenant and retain the run and audit IDs for investigation.
