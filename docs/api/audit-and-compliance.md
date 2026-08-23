# Audit and compliance API

The tenant audit API exposes the tamper-evident audit ledger, independent retention controls and
redacted evidence packages. Every route requires an authenticated actor and an `X-Amesh-Tenant`
context. The built-in `auditor` role can inspect and export evidence; audit-policy and legal-hold
changes require `audit:manage` and therefore remain administrator operations.

## Query and integrity

`GET /api/v1/audit-events` returns cursor-paged events with actor, delegated actor, tenant, resource,
action, outcome, reason, source, time, correlation, trace, retention and hash-chain fields. Optional
filters are `action`, `resourceType`, `outcome`, `occurredFrom` and `occurredTo`. Reading the ledger
creates a new `audit.read` event.

`GET /api/v1/audit-events/integrity` verifies each event hash and its link to the preceding event or
retention anchor. A failed response identifies the first broken event and reports `CHAIN_GAP` or
`HASH_MISMATCH`. Integrity checks are also audited.

## Retention and legal hold

- `GET/PUT /api/v1/audit-policy` reads or changes the tenant's audit retention days.
- `GET/POST /api/v1/audit-legal-holds` lists or creates time-bounded or open-ended holds.
- `DELETE /api/v1/audit-legal-holds/{id}` releases an active hold; it does not delete the hold record.
- `POST /api/v1/audit-retention/purge` removes only an expired contiguous ledger prefix. It stops at
  the first event covered by an active hold and preserves the last removed hash as a chain anchor.

Audit retention is separate from workflow, log and object-storage retention.

## Signed exports and SIEM delivery

`GET /api/v1/audit-events/export` downloads canonical JSON or NDJSON. `POST /api/v1/audit-exports`
writes the same artifact to configured object storage and returns its URI. Both paths return or record
a SHA-256 checksum and `v1=` HMAC signature, and both create an export audit event.

For an external SIEM, create a signed realtime webhook subscription through
`POST /api/v1/realtime/subscriptions` with `filters.includeAudit=true`. Existing webhook signing,
bounded retry, endpoint-test and replay behavior applies; see [Realtime API](realtime.md).

## Compliance readiness packages

`POST/GET /api/v1/compliance-evidence` records and lists supplied access-review, change,
backup/restore, vulnerability, incident or provenance evidence. Payloads are recursively redacted
before persistence and checksummed.

`GET /api/v1/compliance-packages/export` downloads a deterministic ZIP. `POST
/api/v1/compliance-packages` writes it to object storage. The package contains separate access review,
change, audit, backup/restore, vulnerability, incident and provenance JSON sections plus a signed
manifest of section hashes. Packages are readiness evidence, not a certification claim.

Protected fields such as passwords, secrets, tokens, authorization values, credentials, assertions,
API keys and private keys are replaced with `[REDACTED]` before audit persistence and again before
artifact generation.
