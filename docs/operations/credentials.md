# Service-account and workload credentials

AMESH stores API and derived workload credentials in PostgreSQL after migration
`0005_service_credentials.sql`. The database contains a UUIDv7 token ID, HMAC-SHA-256 digest and
non-secret lifecycle metadata; it never contains the bearer secret.

## Production configuration

Set a high-entropy `AMESH_TOKEN_PEPPER` through deployment configuration. Production startup rejects
the checked-in development value. `AMESH_PREVIOUS_TOKEN_PEPPER` is optional and accepts tokens made
with the preceding pepper during a controlled rollover. Neither value belongs in an image or source
file.

For Helm, put `token-pepper` in the Secret selected by `tokenPepper.existingSecret`. During rollover,
add the old value under another key and set `tokenPepper.previousKey` to that key name.

The shared `AMESH_ADMIN_TOKEN` remains development-only. Production API callers use a token issued
to an enabled `SERVICE_ACCOUNT`, `WORKER` or `PLUGIN` principal. Service accounts have no interactive
login path.

## Issue and use an API token

An instance administrator first creates a service-account principal and assigns its roles, groups and
instance, tenant or namespace bindings through the authorization APIs. Issue a token with:

```http
POST /api/v1/admin/principals/{principalId}/credentials
Authorization: Bearer <administrator-token>
Content-Type: application/json

{
  "name": "deployment-bot",
  "scopes": ["flow:view", "execution:execute"],
  "audience": "amesh-api",
  "expiresAt": "2026-08-22T00:00:00Z",
  "rateLimitPerMinute": 600
}
```

Copy the response `token` immediately. Listing the principal's credentials later returns name,
scopes, audience, expiry, status and last-use time, but never the secret or digest. Send the copied
value only in `Authorization: Bearer <token>`.

Effective authority is the intersection of the token scopes and the principal's current roles,
groups and tenant/namespace bindings. Each token has an independent fixed-window request quota; an
exhausted token receives HTTP `429` and `Retry-After: 60` without consuming another token's quota.

## Rotate and revoke

Rotate a token with `POST /api/v1/admin/credentials/{credentialId}/rotate`. The body
`{"overlapSeconds":300}` keeps the prior token usable for five minutes while clients change over;
the maximum overlap is 24 hours. The replacement secret is again shown only in that response.

Revoke one token and its derived children with
`DELETE /api/v1/admin/credentials/{credentialId}`. Revoke every credential for a principal with
`DELETE /api/v1/admin/principals/{principalId}/credentials`. Principal-wide revocation increments a
credential epoch used by current tokens and future session implementations, so the next validation
fails without a cache or server restart.

To rotate the HMAC pepper without rebuilding an image:

1. Deploy a new `AMESH_TOKEN_PEPPER` and set `AMESH_PREVIOUS_TOKEN_PEPPER` to the old value.
2. Rotate active API tokens and move callers to their one-time replacement values.
3. After the longest declared token/overlap window, remove `AMESH_PREVIOUS_TOKEN_PEPPER`.

New tokens always use the current pepper; old tokens remain valid during the configured transition.

## Workload exchange and audit

An authenticated `WORKER` or `PLUGIN` API token may call `POST /api/v1/credentials/exchange`. The
derived token must use a different audience, expires in at most one hour, and cannot broaden its
parent scopes. Revoking the parent immediately revokes its derived credentials.

Creation, exchange, successful use, failed authentication, rotation and revocation append
`audit_events` evidence containing token IDs and non-secret metadata only. Operators should alert on
repeated `credential.authenticate` failures and sustained `429` responses.
