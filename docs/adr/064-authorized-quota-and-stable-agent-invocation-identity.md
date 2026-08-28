# ADR-064: Authorize tenant quota and keep agent invocation identity stable

Status: accepted

Context: Tenant API quota was reserved as soon as a request supplied a syntactically valid tenant
header, before the authenticated actor was known to have authority in that tenant. A cross-tenant
caller could therefore spend another tenant's quota. Separately, governed MCP retries deliberately
derive one invocation UUID from the task run and operation, but PostgreSQL conflict handling looked
up only the attempt-scoped uniqueness key. A later attempt could collide on the stable primary key
without recovering the original invocation.

Decision: Carry deferred, request-local quota state with the resolved tenant context. Reserve one API
request unit only after the first successful authorization in that tenant and before the authorized
operation continues. A request that never receives a tenant grant cannot consume that tenant's API
quota.

Treat `invocation_id` as the durable governed-tool identity across task attempts. Invocation insert
may conflict on either the stable UUID or the attempt-scoped uniqueness key; recovery first resolves
the stable UUID and otherwise resolves the same-attempt record. Reuse is accepted only when the
tenant, execution, task run, operation kind/name and request hash still match. The stored attempt is
evidence of the first claim, not a new permission to repeat the remote effect.

Alternatives: attempt-scoped invocation UUIDs were rejected because they permit ambiguous remote
writes to repeat. Charging quota during tenant-header parsing was rejected because parsing is not
authorization. Charging after the endpoint completes was rejected because a quota failure could
arrive after an operation had already produced side effects.

Consequences: unauthorized cross-tenant probes cannot drain quota, while an authorized request is
charged at most once even when an endpoint evaluates multiple permissions. Retry recovery returns
the original governed invocation and preserves at-most-once ambiguity handling across worker
attempts.
