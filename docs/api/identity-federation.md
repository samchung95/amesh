# Identity federation API

## Provider discovery and browser redirects

`GET /api/v1/auth/providers` returns local and OIDC provider descriptors. Add `identifier` and `tenant` query parameters to apply configured domain and tenant routing. `login_mode=password` providers use `POST /api/v1/auth/login`; `login_mode=redirect` providers use the browser flow.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/auth/federated/{provider}/start` | Create one-time state and redirect to OIDC login. Accepts `tenant` and local-path `returnTo`. |
| `GET` | `/api/v1/auth/federated/{provider}/callback` | OIDC authorization-code callback. |
| `POST` | `/api/v1/auth/logout` | Revoke the current AMESH browser session. |

Successful callbacks set the same HTTP-only session and separate CSRF cookies as local login, then redirect only to a local path. Provider tokens are not returned to the browser application.

SAML, LDAP and SCIM were removed by [ADR-085](../adr/085-remove-unused-compatibility-transfer-and-federation-surfaces.md).
