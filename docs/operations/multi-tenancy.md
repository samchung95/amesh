# Multi-tenancy operations

AMESH uses an explicit request tenant plus PostgreSQL row-level security (RLS). Migrations
`0006_multi_tenancy.sql`, `0007_tenant_queue_notifications.sql` and
`0008_restricted_tenant_resolution.sql`, `0009_tenant_administration_role.sql`, and the current-head
role grants in migrations `0075` through `0078` create the tenant policy, lifecycle/export records,
runtime database roles, forced RLS policies, tenant-specific queue notification channels, restricted
tenant resolver and repository role boundaries.

## Runtime modes

`TENANCY_MODE=single` keeps the development-compatible default: resource requests without
`X-Amesh-Tenant` use `SINGLE_TENANT_SLUG` (default `default`). Set `TENANCY_MODE=multi` for a
multi-tenant server; every resource request then requires `X-Amesh-Tenant: <slug>`. Missing context
returns `400`. Unknown, suspended and tombstoned tenants all return the same `404 tenant unavailable`
response.

The Helm equivalents are:

```yaml
tenancy:
  mode: multi
  singleTenantSlug: default
worker:
  group: regulated
```

Tenant execution, worker, audit, and tenant-scoped authorization paths support a non-superuser,
non-owner login that can `SET ROLE amesh_runtime`. A tenant transaction switches to that
`NOLOGIN NOBYPASSRLS` role, calls the minimal security-definer active-tenant resolver, and sets the
returned UUID transaction-locally. Forced RLS then rejects rows outside that UUID even when an
application query omits a predicate.

Application servers also need membership in `amesh_tenant_admin`. Global identity, credentials,
federation, operations, service-registry, upgrade, and instance-administration transactions switch to
that explicit role after migration `0075_restricted_repository_roles.sql`; migrations `0076` through
`0078` complete authorization row-lock and restricted recovery-operation privileges, including
admin-only projection rebuild execution. Use a `NOINHERIT NOSUPERUSER NOBYPASSRLS` login with only
those two memberships. Worker-only logins need only `amesh_runtime`.
Never grant an application login `amesh_tenant_resolver`, direct `BYPASSRLS`, or superuser.

The supported pre-0075 LTS upgrade preflight continues on the separately controlled migration/session
identity because the restricted admin grants do not exist yet. Apply the complete manifest through
0078 before starting current-head binaries. Keep migration and backup identities separate from the
application login.

## Tenant administration

Only the bootstrap or an effective instance administrator can use `/api/v1/admin/tenants`. The
OpenAPI document defines create, list, get, policy update, suspend, export, delete and restore
operations. For example:

```bash
curl -fsS -X POST http://127.0.0.1:8000/api/v1/admin/tenants \
  -H 'Authorization: Bearer development-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "slug": "acme",
    "displayName": "Acme",
    "policy": {
      "retention_days": 30,
      "max_concurrent_executions": 20,
      "max_storage_bytes": 10737418240,
      "encryption_key_ref": "kms://acme",
      "identity_provider_refs": ["oidc-acme"],
      "plugin_allowlist": ["core.return", "core.http", "agent.llm"],
      "feature_flags": {"executions": true},
      "worker_groups": ["regulated"]
    }
  }'
```

The execution repository enforces the execution feature flag, plugin allowlist and concurrent-run
quota before accepting work. Worker processes discover only active tenants assigned to their
`WORKER_GROUP`. Storage keys are rooted at the immutable `tenants/<slug>/` prefix; retention,
storage-budget, encryption-key and identity-provider references remain part of the authoritative
tenant policy consumed by their respective adapters.

Suspension stops new API, scheduler, execution and worker access without deleting data. Export writes
an immutable tenant snapshot and resource counts. Delete performs an export and then tombstones the
tenant; it does not hard-delete its rows. Restore reactivates retained rows. Operators should export
before deliberate lifecycle changes and confirm the separately audited `tenant.*` event, whose
evidence carries `superAdmin: true`.

## Isolation checks

`tests/api/test_tenant_api.py` proves lifecycle, required context, identical missing-resource errors,
metrics redaction and same-name resource isolation.
`tests/adapters/postgres/test_restricted_repository_roles.py` provisions a non-superuser,
`NOBYPASSRLS` login with exactly the runtime and admin memberships, exercises all eight repository
families, and proves two-tenant audit and authorization isolation. The remaining PostgreSQL tests
cover tenant-scoped queue claims and notification timing, worker-group routing, policy enforcement,
and explicit super-administrator audit attribution.

This is logical multi-tenancy on one PostgreSQL authority. Database backup/restore, regional failure
and penetration-test qualification remain separate HA/DR and release gates; do not represent this
runbook as database-per-tenant or production HA qualification.
