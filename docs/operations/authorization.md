# Authorization operations

AMESH stores authorization policy in PostgreSQL. Apply migration
`0004_authorization.sql` before starting a server with EPIC-500 APIs.

## Development bootstrap

The shared `AMESH_ADMIN_TOKEN` is a local bootstrap credential only. It works when both
`APP_ENV=development` and `AUTH_MODE=development`. Any other combination rejects it; durable
service-account and workload credentials are described in the [credential runbook](credentials.md).
Tenant lifecycle, policy and RLS operations are described in the
[multi-tenancy runbook](multi-tenancy.md).

Send the selected tenant on resource requests:

```bash
uv run --extra runtime python -m amesh \
  --token development-token \
  --tenant default flows
```

HTTP clients use `Authorization: Bearer ...` and `X-Amesh-Tenant: <tenant>`. Namespace-scoped
authorization is derived from the resource or route. A denied request returns `403` with the generic
body `{"detail":"not authorized"}`. A tenant-scoped request with no applicable tenant role returns
the same `404 tenant unavailable` response as an unknown tenant so tenant existence is not disclosed.

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
action and affected authorization resource. Credential issuance, use, failure, rotation and
revocation use the same audit store without token plaintext. Interactive user login uses the separate
provider-neutral authentication service documented in the [authentication runbook](authentication.md);
external identity-provider protocols remain EPIC-502 work.

## Agent session roles

The session service uses product-specific resources while retaining tenant and namespace binding
semantics:

| Built-in role | Intended authority |
| --- | --- |
| `session-client` | Create sessions and view sessions owned by the principal. |
| `session-operator` | View the scoped fleet, inspect policy posture and control sessions. |
| `session-admin` | Administer the scoped fleet, policies and portable migrations. |

The canonical actions stay `create`, `view`, `list` and `manage`; ownership and fleet boundaries are
enforced by the session API rather than encoded as role names. Administrative routes additionally
require `agent_session_administration`, `agent_session_policy` or `agent_session_migration` grants.
Instance, tenant and namespace administrator wildcard grants continue to apply within their binding
scope.

Existing data-plane clients may temporarily fall back to equivalent `execution` grants when no
session grant or credential scope matches. Explicit session denies are authoritative, and the
separate administration API has no execution-permission fallback.
