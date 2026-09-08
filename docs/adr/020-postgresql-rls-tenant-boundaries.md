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

## Reviewed instance transaction authority

Issue #67 A1 review, 2026-09-08. The table records every administrative transaction
entrypoint. The role-classification test compares this register with the entire PostgreSQL
package, including aliases and delegated transaction helpers. Adding an entry requires an
instance-scope reason; a tenant-only operation belongs under `transactions.tenant`.

Seven flow-test methods and two administration-audit methods now use tenant transactions.
Migration 0080 grants the flow-test operations access through their existing forced RLS policies.
Federated tenant bindings belong to global identity provisioning; compliance snapshots include
instance grants as well as the requested tenant, so those operations retain admin authority.

| Administrative entrypoint | Instance-scope justification |
| --- | --- |
| `agent_session_admin.py:PostgresAgentSessionFleetRepository.instance_aggregate` | Fleet totals cover every active tenant; only the instance administration boundary exposes this aggregate. |
| `audit_repository.py:PostgresAuditRepository.record_authorization_decision` | Only the request without a tenant uses admin authority to write system-tenant audit evidence; tenant decisions use the tenant transaction. |
| `audit_repository.py:PostgresAuditRepository.compliance_snapshot` | The snapshot combines the requested tenant evidence with instance role grants that can access that tenant; evidence queries retain the tenant predicate. |
| `authentication_repository.py:PostgresAuthenticationRepository.bootstrap_local_admin` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.load_local_identity` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.allow_login_source` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.record_login_failure` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.create_browser_session` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.authenticate_browser_session` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.revoke_session` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.revoke_all_sessions` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.set_local_password` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authentication_repository.py:PostgresAuthenticationRepository.update_password_hash` | Local identities, browser sessions and login-rate controls precede tenant selection and belong to the instance identity plane. |
| `authorization_repository.py:PostgresAuthorizationRepository.policy_version` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.load_policy_snapshot` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.create_principal` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.list_principals` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.add_group_member` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.remove_group_member` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.upsert_role` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.list_roles` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.create_binding` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.list_bindings` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `authorization_repository.py:PostgresAuthorizationRepository.delete_binding` | Principals, groups, reusable roles and bindings form the instance authorization graph; tenant bindings retain explicit target IDs. |
| `credential_repository.py:PostgresCredentialRepository.load_principal` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `credential_repository.py:PostgresCredentialRepository.create_credential` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `credential_repository.py:PostgresCredentialRepository.get_credential` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `credential_repository.py:PostgresCredentialRepository.list_credentials` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `credential_repository.py:PostgresCredentialRepository.authenticate` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `credential_repository.py:PostgresCredentialRepository.record_authentication_failure` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `credential_repository.py:PostgresCredentialRepository.rotate_credential` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `credential_repository.py:PostgresCredentialRepository.revoke_credential` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `credential_repository.py:PostgresCredentialRepository.revoke_all_credentials` | Credential authentication and revocation address instance principals before request tenant resolution; credential scope is checked by the identity service. |
| `feature_flags.py:PostgresFeatureFlagRepository.upsert` | Feature configuration resolves instance defaults together with tenant/namespace overrides; process reload auditing uses the system tenant. |
| `feature_flags.py:PostgresFeatureFlagRepository.list_for_context` | Feature configuration resolves instance defaults together with tenant/namespace overrides; process reload auditing uses the system tenant. |
| `feature_flags.py:PostgresFeatureFlagRepository.audit_configuration_reload` | Feature configuration resolves instance defaults together with tenant/namespace overrides; process reload auditing uses the system tenant. |
| `federation_repository.py:PostgresFederationRepository.record_event` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.create_state` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.attach_request_id` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.consume_state` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.record_assertion` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.resolve_identity` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.list_scim` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository._get_scim_rows` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.create_scim` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.update_scim` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `federation_repository.py:PostgresFederationRepository.delete_scim` | Federation state and provider-scoped SCIM identities belong to the instance identity plane; provider IDs fence records and tenant role mappings retain explicit targets. |
| `operational_control_repository.py:PostgresOperationalControlRepository.create_announcement` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.list_announcements` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.deactivate_announcement` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.create_control` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.list_controls` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.get_control` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.apply_action` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.evaluate` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.acknowledge_active` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operational_control_repository.py:PostgresOperationalControlRepository.list_events` | Instance announcements and controls must combine with tenant-targeted controls; reads retain tenant-or-instance predicates and acknowledgements use the assigned tenant list. |
| `operations_repository.py:PostgresOperationsRepository.record_backup_checkpoint` | Backup, restore, reconciliation and table maintenance operate on the whole database under the instance operations boundary. |
| `operations_repository.py:PostgresOperationsRepository.latest_backup_checkpoint` | Backup, restore, reconciliation and table maintenance operate on the whole database under the instance operations boundary. |
| `operations_repository.py:PostgresOperationsRepository.inspect_table_maintenance` | Backup, restore, reconciliation and table maintenance operate on the whole database under the instance operations boundary. |
| `operations_repository.py:PostgresOperationsRepository.start_recovery_exercise` | Backup, restore, reconciliation and table maintenance operate on the whole database under the instance operations boundary. |
| `operations_repository.py:PostgresOperationsRepository.complete_recovery_exercise` | Backup, restore, reconciliation and table maintenance operate on the whole database under the instance operations boundary. |
| `operations_repository.py:PostgresOperationsRepository.get_recovery_exercise` | Backup, restore, reconciliation and table maintenance operate on the whole database under the instance operations boundary. |
| `operations_repository.py:PostgresOperationsRepository.prepare_restored_state` | Backup, restore, reconciliation and table maintenance operate on the whole database under the instance operations boundary. |
| `operations_repository.py:PostgresOperationsRepository.rebuild_disposable_projections` | Backup, restore, reconciliation and table maintenance operate on the whole database under the instance operations boundary. |
| `repository_support.py:PostgresTransactionManager.admin` | The shared transaction factory enters the restricted instance role; each caller is separately listed here. |
| `service_registry.py:PostgresServiceRegistryRepository.register` | Service identities, ownership, readiness and drain state describe the shared deployment rather than one tenant. |
| `service_registry.py:PostgresServiceRegistryRepository.heartbeat` | Service identities, ownership, readiness and drain state describe the shared deployment rather than one tenant. |
| `service_registry.py:PostgresServiceRegistryRepository.request_drain` | Service identities, ownership, readiness and drain state describe the shared deployment rather than one tenant. |
| `service_registry.py:PostgresServiceRegistryRepository.stop` | Service identities, ownership, readiness and drain state describe the shared deployment rather than one tenant. |
| `service_registry.py:PostgresServiceRegistryRepository.get` | Service identities, ownership, readiness and drain state describe the shared deployment rather than one tenant. |
| `service_registry.py:PostgresServiceRegistryRepository.topology` | Service identities, ownership, readiness and drain state describe the shared deployment rather than one tenant. |
| `tenant_repository.py:PostgresTenantRepository.create` | Tenant lifecycle administration must read inactive tenants and create new ones before an active tenant context exists; targeted operations retain slug/ID predicates. |
| `tenant_repository.py:PostgresTenantRepository.get` | Tenant lifecycle administration must read inactive tenants and create new ones before an active tenant context exists; targeted operations retain slug/ID predicates. |
| `tenant_repository.py:PostgresTenantRepository.list` | Tenant lifecycle administration must read inactive tenants and create new ones before an active tenant context exists; targeted operations retain slug/ID predicates. |
| `tenant_repository.py:PostgresTenantRepository.set_status` | Tenant lifecycle administration must read inactive tenants and create new ones before an active tenant context exists; targeted operations retain slug/ID predicates. |
| `tenant_repository.py:PostgresTenantRepository.set_policy` | Tenant lifecycle administration must read inactive tenants and create new ones before an active tenant context exists; targeted operations retain slug/ID predicates. |
| `tenant_repository.py:PostgresTenantRepository.export` | Instance tenant administration exports one explicitly selected tenant, including inactive tenants; each exported relation uses that tenant ID. |
| `upgrade_repository.py:PostgresUpgradeRepository.inventory` | Migration inventory and event upcasts inspect the installed instance across tenants under the upgrade boundary. |
| `upgrade_repository.py:PostgresUpgradeRepository.flow_documents` | Migration inventory and event upcasts inspect the installed instance across tenants under the upgrade boundary. |
| `upgrade_repository.py:PostgresUpgradeRepository.tenant_slugs` | Migration inventory and event upcasts inspect the installed instance across tenants under the upgrade boundary. |
| `upgrade_repository.py:PostgresUpgradeRepository.preview_event_upcast` | Migration inventory and event upcasts inspect the installed instance across tenants under the upgrade boundary. |
| `upgrade_repository.py:PostgresUpgradeRepository.upcast_events` | Migration inventory and event upcasts inspect the installed instance across tenants under the upgrade boundary. |
| `tenant_context.py:tenant_admin_transaction` | This role-selection primitive checks the migration canary before yielding; it never falls back to the login role. |
