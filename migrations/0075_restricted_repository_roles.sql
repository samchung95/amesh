BEGIN;

GRANT EXECUTE ON FUNCTION amesh_resolve_active_tenant(text) TO amesh_tenant_admin;
GRANT EXECUTE ON FUNCTION amesh_rebuild_disposable_projections() TO amesh_tenant_admin;

GRANT SELECT, INSERT, UPDATE ON auth_principals TO amesh_tenant_admin;
GRANT SELECT, INSERT, DELETE ON auth_group_memberships TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON auth_roles TO amesh_tenant_admin;
GRANT SELECT, INSERT, DELETE ON auth_role_permissions TO amesh_tenant_admin;
GRANT SELECT, INSERT, DELETE ON auth_role_bindings TO amesh_tenant_admin;
GRANT SELECT, INSERT, DELETE ON auth_namespace_boundaries TO amesh_tenant_admin;
GRANT SELECT, UPDATE ON auth_policy_state TO amesh_tenant_admin;

GRANT SELECT, INSERT, UPDATE ON auth_local_credentials TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON auth_browser_sessions TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON auth_login_rate_windows TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON auth_credentials TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON auth_credential_usage_windows TO amesh_tenant_admin;

GRANT SELECT, INSERT, UPDATE ON auth_federated_identities TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON auth_federation_states TO amesh_tenant_admin;
GRANT SELECT, INSERT, DELETE ON auth_federation_replays TO amesh_tenant_admin;
GRANT SELECT, INSERT, DELETE ON auth_federation_group_memberships TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON auth_scim_resources TO amesh_tenant_admin;

GRANT SELECT, INSERT ON backup_checkpoints TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON recovery_exercises TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON service_instances TO amesh_tenant_admin;
GRANT SELECT ON amesh_schema_migrations TO amesh_tenant_admin;

GRANT SELECT ON tenants, flow_revisions, executions TO amesh_tenant_admin;
GRANT SELECT, UPDATE ON execution_events TO amesh_tenant_admin;
GRANT SELECT, UPDATE ON durable_work_queue TO amesh_tenant_admin;
GRANT UPDATE ON workers, task_attempts, leases, scheduler_states TO amesh_tenant_admin;

GRANT SELECT ON
    audit_events,
    audit_retention_policies,
    audit_legal_holds,
    audit_chain_anchors,
    audit_export_receipts,
    compliance_evidence_records
TO amesh_tenant_admin;

COMMIT;
