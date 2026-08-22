# Trigger operations

AMESH gives schedules, webhooks, polling/realtime adapters and flow-completion triggers one durable
occurrence ledger. Open **Triggers** in the control room to inspect health, pending work, retries,
dead letters and linked executions.

## Try a webhook and dependent flow

Apply the two examples in order:

```powershell
uv run --extra runtime python -m amesh --token development-token --tenant default apply examples/trigger-source.yaml
uv run --extra runtime python -m amesh --token development-token --tenant default apply examples/trigger-dependent.yaml
```

Send a source event. Reusing `X-Event-Id` returns the same source execution rather than launching a
duplicate:

```powershell
$headers = @{ Authorization = "Bearer development-token"; "X-Event-Id" = "demo-001" }
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/webhooks/demo.triggers/source/incoming -Headers $headers -ContentType application/json -Body '{"message":"hello"}'
```

The source execution completes first. Its terminal transaction creates an occurrence for the
`core.flow` trigger in `trigger-dependent.yaml`; the scheduler service turns that occurrence into a
dependent execution. Inspect both rows at `http://localhost:8000/triggers`.

## Configure occurrence behavior

Every non-temporal trigger accepts:

- `maxPending`: maximum accepted, processing or retry-wait occurrences before new work is deferred;
- `maxAttempts`: total processing attempts before dead-lettering;
- `retryDelay`: positive ISO-8601 delay between attempts;
- `paused`: initial operator pause state.

A `core.flow` trigger additionally accepts the source `namespace`, required `flowId`, terminal
`states`, static `inputs` and `maxDepth`. Omitting `namespace` means the dependent flow's namespace.

## Inspect and control

```text
GET  /api/v1/triggers
GET  /api/v1/trigger-occurrences?state=DEAD_LETTERED
POST /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause
POST /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume
POST /api/v1/trigger-occurrences/{occurrence_id}/replay
```

Pause and resume bodies accept an operator `reason`. Replay creates a new occurrence linked by
`replay_of`; it does not alter the dead-letter record. All control endpoints require trigger-manage
authorization and write audit/evidence events.

## State and recovery

- `ACCEPTED`: durable and ready for a scheduler claim.
- `DEFERRED`: retained but not admitted because the trigger is paused or at its pending limit.
- `PROCESSING`: owned by a fenced, expiring claim.
- `RETRY_WAIT`: failed transiently and eligible after `next_attempt_at`.
- `SUCCEEDED`: linked execution was created successfully.
- `DEAD_LETTERED`: attempts were exhausted; inspect the error and replay manually if appropriate.

Expired processing claims return to eligible work. Polling adapters commit their cursor before source
acknowledgement; realtime adapters acknowledge only after durable acceptance. Trigger health exposes
the latest evaluation, next evaluation, lag, pending/dead counts and recent error or decision.
