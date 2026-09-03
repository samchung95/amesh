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
security can enforce the existing shared-schema model for tenant-scoped work. Instance-wide control
operations also need a deliberately separate role whose table privileges and query predicates remain
reviewable even when row security cannot express a cross-tenant operation.

## Decision

1. Multi-tenant API mode requires `X-Amesh-Tenant`; explicit single-tenant mode may supply its
   configured tenant slug.
2. Tenant-scoped repository transactions switch to the non-login `amesh_runtime` role, resolve an
   active tenant through a minimal security-definer function and set its UUID transaction-locally.
3. Tenant-bearing workflow, execution, transport, worker, lease and audit tables use forced RLS with
   default-deny behavior outside the matching transaction context.
4. Repository method signatures retain tenant context even when a resource UUID is globally unique.
   SQL filters and RLS are independent layers.
5. Instance-wide identity, authorization, lifecycle, audit, recovery and administration operations
   switch to `amesh_tenant_admin`. That role intentionally has `BYPASSRLS`; explicit table grants
   restrict its surface, and every tenant-bearing read must carry a reviewed predicate.
6. An application transaction must fail before repository work when the restricted-admin grant
   boundary is absent. Only the separately controlled migration command may advance a pre-boundary
   schema; current application binaries never continue as their login role.
7. The internal system tenant owns instance-scoped audit evidence; it is excluded from customer tenant
   listings and runtime work.
8. Object keys derive from `tenants/<slug>/`; worker groups consume only explicitly assigned active
   tenants.

## Consequences

- A missing tenant transaction context yields zero rows or a policy violation rather than broad access.
- Tenant-repository logins must be `NOINHERIT NOSUPERUSER NOBYPASSRLS` and allowed to `SET ROLE
  amesh_runtime`; server-side administration additionally requires membership in
  `amesh_tenant_admin`. Both target roles remain `NOLOGIN`; application sessions must select them
  explicitly rather than inheriting their authority.
- `amesh_runtime` is the forced-RLS tenant boundary. `amesh_tenant_admin` intentionally bypasses RLS
  for instance-wide work, so least-privilege table grants, explicit tenant predicates and restricted
  login tests are part of the security boundary.
- A database must be migrated through `0075_restricted_repository_roles.sql` before current binaries
  start. Migration and backup credentials are operational identities, not application fallbacks.
- A database per tenant remains a future deployment profile, not the v1 reference architecture.
