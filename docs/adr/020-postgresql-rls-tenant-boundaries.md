# ADR-020: PostgreSQL RLS tenant boundaries

- Status: Accepted
- Date: 2026-08-21
- Scope: EPIC-503

## Context

AMESH already stores workflow, execution, event and transport rows in one PostgreSQL database with a
non-null tenant foreign key. Multi-tenant operation must reject missing context, prevent accidental
unscoped repository reads and give adversarial tests a database-enforced boundary.

Application-only filters are easy to omit. Database-per-tenant isolation is stronger but multiplies
migration, connection-pool, backup and restore operations beyond the selected profile. PostgreSQL row
security can enforce the existing shared-schema model, provided application queries do not run as the
schema owner or a `BYPASSRLS` role.

## Decision

1. Multi-tenant API mode requires `X-Amesh-Tenant`; explicit single-tenant mode may supply its
   configured tenant slug.
2. Tenant-scoped repository transactions switch to the non-login `amesh_runtime` role, resolve an
   active tenant through a minimal security-definer function and set its UUID transaction-locally.
3. Tenant-bearing workflow, execution, transport, worker, lease and audit tables use forced RLS with
   default-deny behavior outside the matching transaction context.
4. Repository method signatures retain tenant context even when a resource UUID is globally unique.
   SQL filters and RLS are independent layers.
5. Tenant lifecycle/export operations switch to a narrow `amesh_tenant_admin` role and write a target
   audit event with explicit super-administrator evidence.
6. The internal system tenant owns instance-scoped audit evidence; it is excluded from customer tenant
   listings and runtime work.
7. Object keys derive from `tenants/<slug>/`; worker groups consume only explicitly assigned active
   tenants.

## Consequences

- A missing tenant transaction context yields zero rows or a policy violation rather than broad access.
- Tenant-repository logins must be allowed to `SET ROLE amesh_runtime`; server-side tenant
  administration additionally requires `amesh_tenant_admin`. The resolver roles remain `NOLOGIN` and
  are never granted to an application login.
- A database per tenant remains a future deployment profile, not the v1 reference architecture.
