# Authorization operations

AMESH stores authorization policy in PostgreSQL. Apply migration
`0004_authorization.sql` before starting a server with EPIC-500 APIs.

## Development bootstrap

The shared `AMESH_ADMIN_TOKEN` is a local bootstrap credential only. It works when both
`APP_ENV=development` and `AUTH_MODE=development`. Any other combination rejects it and requires the
future durable credential provider from EPIC-403/EPIC-501.

Send the selected tenant on resource requests:

```bash
uv run --extra runtime python -m amesh \
  --token development-token \
  --tenant default flows
```

HTTP clients use `Authorization: Bearer ...` and `X-Amesh-Tenant: <tenant>`. Namespace-scoped
authorization is derived from the resource or route. A denied request returns `403` with the generic
body `{"detail":"not authorized"}`.

## Policy administration

The OpenAPI document lists the `/api/v1/admin/principals`, `/groups`, `/roles`, `/bindings` and
namespace-boundary operations. Bindings target one of these scopes:

- `INSTANCE`: no tenant or namespace;
- `TENANT`: `tenant_id` only;
- `NAMESPACE`: both `tenant_id` and a dotted namespace.

Use `/api/v1/authorization/explain` as an instance administrator to inspect the policy version,
reason code and matched roles for a decision. This endpoint never returns protected resource content.

Binding and group-membership revocations increment `auth_policy_state.version` in the same transaction.
No server restart or manual cache flush is required. Removing a binding or group membership that would
leave zero enabled effective instance administrators returns `409` and rolls back.

Principal, group, role, binding and boundary mutations append an `audit_events` row with the actor,
action and affected authorization resource. Credential creation, login sessions, token rotation and
external identity providers are intentionally handled by EPIC-403, EPIC-501 and EPIC-502.
