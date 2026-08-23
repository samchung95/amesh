# Lifecycle API

All endpoints require tenant context and `lifecycle.manage`; instance-scoped policy writes require
instance management authority.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/lifecycle/policies` | List instance and tenant-effective policies. |
| `POST` | `/api/v1/lifecycle/policies` | Create a scoped manual or scheduled policy. |
| `PUT` | `/api/v1/lifecycle/policies/{policyId}` | Update a policy, optionally with `expectedVersion`. |
| `GET/POST` | `/api/v1/lifecycle/legal-holds` | List or create workflow-data legal holds. |
| `POST` | `/api/v1/lifecycle/legal-holds/{holdId}/release` | Release a hold without purging. |
| `POST` | `/api/v1/lifecycle/previews` | Snapshot affected records, bytes and exclusions. |
| `GET` | `/api/v1/lifecycle/jobs` | List durable job progress, failures and evidence. |
| `GET` | `/api/v1/lifecycle/jobs/{jobId}` | Read one job and its confirmation phrase. |
| `POST` | `/api/v1/lifecycle/jobs/{jobId}/execute` | Confirm a preview and process one batch. |
| `POST` | `/api/v1/lifecycle/jobs/{jobId}/resume` | Process the next batch or retry object deletion. |

Create a namespace-scoped scheduled policy:

```json
{
  "resourceType": "EXECUTION",
  "scope": "NAMESPACE",
  "namespace": "finance.daily",
  "labelSelector": {},
  "retentionDays": 30,
  "batchSize": 100,
  "scheduleIntervalMinutes": 60,
  "enabled": true,
  "reason": "retain finance workflow evidence for thirty days"
}
```

Preview with `{"policyId":"…","reason":"quarterly cleanup"}`. A preview response contains
`estimatedRecords`, `estimatedBytes`, `protectedRecords`, `activeRecords`, `previewExpiresAt` and
`confirmationPhrase`. Submit that phrase unchanged as `{"confirmation":"PURGE 142"}`. A response in
`READY`, `WAITING_EXTERNAL` or `FAILED` is resumable; `SUCCEEDED` means the cutoff has no remaining
eligible records.

See the [retention runbook](../operations/retention.md) for deletion ordering and recovery semantics.
