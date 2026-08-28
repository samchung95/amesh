# Audit evidence operations

AMESH stores one tenant-isolated audit chain in PostgreSQL. Migration `0046_audit_evidence_ledger.sql`
hardens all existing audit producers through a database trigger, so older transactional resource
mutations and new authorization decisions share the same field, redaction, retention and hash rules.

## Daily checks

1. Call `GET /api/v1/audit-events/integrity` for each tenant and alert when `valid` is false.
2. Confirm the configured retention window with `GET /api/v1/audit-policy`.
3. Review active holds with `GET /api/v1/audit-legal-holds` before running a purge.
4. Confirm external SIEM subscriptions are enabled, have `includeAudit=true`, and show no exhausted
   webhook delivery.
5. Retain export receipts with the downloaded or object-stored artifact so its SHA-256 and signature
   can be independently checked.

The HMAC key is the configured webhook signing key. Rotate it using the protected configuration
process and retain the old key for the evidence period in which its signatures must remain verifiable.

## Retention procedure

Set retention with `PUT /api/v1/audit-policy`, for example `{"retentionDays":365}`. Create a legal hold
before a purge when an investigation or evidence request covers a time range. The purge deletes only
the expired prefix before the first retained or held event; it cannot create an internal gap. Its
anchor lets later integrity checks prove continuity from the last deliberately removed record.

Releasing a hold marks it inactive and records the releasing actor and time. It does not purge data;
invoke `POST /api/v1/audit-retention/purge` separately after confirming the evidence disposition.

## Tamper response

When integrity verification reports a gap or hash mismatch:

1. stop audit retention purges for that tenant;
2. preserve the database and the most recent signed export/SIEM copy;
3. compare the reported event and predecessor against the independent copy;
4. investigate database access and record the incident through `POST /api/v1/compliance-evidence`;
5. restore through the normal disaster-recovery process if authoritative state is damaged.

Do not rewrite hashes to make a failed report pass. Database permissions, backup controls and external
signed copies remain necessary because a database superuser can alter both rows and server-side
functions.

## Compliance package collection

Record evidence from processes AMESH cannot perform itself—such as vulnerability scanners, incident
review, protected-branch review and restore exercises—through `/api/v1/compliance-evidence`. Export a
package for the desired evidence period and inspect `manifest.json`, missing/empty sections and
signatures before review. The package assists readiness review; operating controls, an evidence period
and independent examination remain customer responsibilities.
