# Identity federation and SCIM API

## Provider discovery and browser redirects

`GET /api/v1/auth/providers` returns local, OIDC, SAML and LDAP provider descriptors. Add `identifier` and `tenant` query parameters to apply configured domain and tenant routing. `login_mode=password` providers use `POST /api/v1/auth/login`; `login_mode=redirect` providers use the browser flow.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/auth/federated/{provider}/start` | Create one-time state and redirect to OIDC or SAML login. Accepts `tenant` and local-path `returnTo`. |
| `GET` | `/api/v1/auth/federated/{provider}/callback` | OIDC authorization-code callback. |
| `POST` | `/api/v1/auth/federated/{provider}/callback` | SAML HTTP-POST assertion consumer service. |
| `GET` | `/api/v1/auth/federated/{provider}/saml/metadata` | Strict SAML service-provider metadata, including rollover certificates. |
| `POST` | `/api/v1/auth/logout` | Revoke the current AMESH browser session. |

Successful callbacks set the same HTTP-only session and separate CSRF cookies as local login, then redirect only to a local path. Provider tokens and assertions are not returned to the browser application.

## SCIM 2.0

Send `Authorization: Bearer <provider token>` to all `/scim/v2` routes. The token selects one configured provider boundary; there is no tenant header and callers cannot choose another tenant.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/scim/v2/ServiceProviderConfig` | Discover PATCH, filter, ETag and bearer support. |
| `GET`, `POST` | `/scim/v2/Users` | List/filter or provision users. |
| `GET`, `PATCH`, `DELETE` | `/scim/v2/Users/{id}` | Read, update/disable or deprovision one user. |
| `GET`, `POST` | `/scim/v2/Groups` | List/filter or provision groups. |
| `GET`, `PATCH`, `DELETE` | `/scim/v2/Groups/{id}` | Read, update membership or deprovision one group. |

Supported filters are `userName eq "value"` and `displayName eq "value"`. User PATCH supports `active` and `displayName`. Group PATCH supports `displayName`, add/replace `members`, and `Remove` with `members[value eq "uuid"]`. Responses use weak version ETags and standard SCIM schema URNs.

Errors use the platform Problem Detail envelope today; clients should use the HTTP status as the stable decision: `400` unsupported filter/PATCH, `401` missing or invalid bearer, `404` outside the provider boundary or absent, `409` conflicting resource, and `503` unavailable credential material.
