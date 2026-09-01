# Retention, purge and data lifecycle

AMESH applies workflow-data retention through explicit resource policies and durable purge jobs. Audit
retention remains independent: use the audit policy and legal-hold endpoints described in
[Audit evidence](audit-evidence.md).

## Policy scopes

Policies select one resource type: `EXECUTION`, `LOG`, `METRIC`, `ARTIFACT` or `CACHE`. Define them at
instance, tenant, namespace or execution-label scope. Instance policies provide a shared default;
tenant, namespace and label policies narrow operator intent for a tenant. A policy records retention
days, bounded batch size, reason, actor, version and an optional schedule interval.

Open **Administration → Lifecycle** or use `GET/POST /api/v1/lifecycle/policies`. A scheduled policy is
claimed by the maintenance role when `nextRunAt` is due. Each maintenance cycle processes at most one
configured batch per runnable scheduled job, so lifecycle work yields to orchestration.

## Manual purge procedure

1. Review `GET /api/v1/lifecycle/legal-holds` and create a hold if an investigation or recovery window
   must protect data.
2. Create an impact snapshot with `POST /api/v1/lifecycle/previews`. The response reports affected
   records and bytes, active records excluded, held records protected, the cutoff and a five-minute
   confirmation phrase.
3. Review the recovery consequence: hard-purged payloads, objects and projections require a qualified
   backup restore.
4. Submit the exact phrase to `POST /api/v1/lifecycle/jobs/{id}/execute`. The request commits at most
   the policy batch size.
5. Call `POST /api/v1/lifecycle/jobs/{id}/resume` while the job is `READY`, `WAITING_EXTERNAL` or
   `FAILED`. Every batch, object-provider error and retry is retained in job and event evidence.

The CLI follows the same guard:

```text
amesh lifecycle preview POLICY_ID --reason "quarterly workflow cleanup"
amesh lifecycle execute JOB_ID
amesh lifecycle execute JOB_ID --force
amesh lifecycle jobs
amesh lifecycle resume JOB_ID
```

Without `--force`, `execute` prints the record count, byte count, protected and active exclusions,
scope and restore consequence, then exits without deleting data.

## Integrity and deletion order

Only terminal executions and resources owned by terminal executions are eligible. Execution purge
keeps a compact tombstone identity so backfill, human-task, lineage and other retained references stay
valid; it removes or redacts execution inputs/outputs, events, task attempts, agent-session journal
events, logs, metrics, artifacts, cache payloads and evidence. Active executions and cache populations
are never selected. Hosts therefore control progress retention through the existing execution policy
and legal-hold boundary; progress has no parallel retention store.

Artifact URIs are copied into durable lifecycle job items before authoritative artifact metadata is
removed. Search documents are removed only after that metadata decision. The object backend is then
called outside the metadata transaction; a provider failure leaves the item and job retryable without
reintroducing authoritative data. The same job ID, cursor, retry count and evidence survive process
restart.

## Legal holds and audit independence

Lifecycle holds can protect all workflow resource types or a specific type, resource ID, namespace,
label selector and/or data time range. Selection excludes matching records until the hold is released.
Releasing a hold does not start a purge.

Audit events are governed separately by `audit_retention_policies`, `audit_legal_holds` and the
tamper-evident audit chain. A workflow lifecycle policy cannot shorten audit retention or bypass an
audit hold.

## Recovery and failure handling

- `PREVIEWED`: no deletion has occurred; refresh after five minutes.
- `READY` or `RUNNING`: resume to process the next bounded metadata batch.
- `WAITING_EXTERNAL`: authoritative metadata is committed and object deletion is pending.
- `FAILED`: inspect `lastError`, correct object-provider access or availability, then resume.
- `SUCCEEDED`: the recorded scope had no remaining eligible records at the preview cutoff.

Never delete lifecycle job items to clear a failure. Preserve the evidence, correct the dependency and
resume. Restore hard-purged content only through the qualified backup/restore runbook.
