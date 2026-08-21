BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'amesh_tenant_admin') THEN
        CREATE ROLE amesh_tenant_admin
            NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT BYPASSRLS;
    END IF;
    EXECUTE format('GRANT amesh_tenant_admin TO %I', current_user);
END;
$$;

GRANT USAGE ON SCHEMA public TO amesh_tenant_admin;
GRANT SELECT ON
    tenants,
    namespaces,
    flows,
    executions,
    task_runs,
    tenant_exports,
    audit_events
TO amesh_tenant_admin;
GRANT INSERT, UPDATE ON tenants TO amesh_tenant_admin;
GRANT INSERT ON tenant_exports, audit_events TO amesh_tenant_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO amesh_tenant_admin;

CREATE OR REPLACE FUNCTION amesh_active_tenants_for_worker_group(selected_group text)
RETURNS SETOF text AS $$
    SELECT slug
    FROM public.tenants
    WHERE id <> '00000000-0000-7000-8000-000000000002'::uuid
      AND status = 'ACTIVE'
      AND lifecycle = 'ACTIVE'
      AND jsonb_exists(settings -> 'worker_groups', selected_group)
    ORDER BY slug
$$ LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog, public;

ALTER FUNCTION amesh_active_tenants_for_worker_group(text) OWNER TO amesh_tenant_resolver;
REVOKE ALL ON FUNCTION amesh_active_tenants_for_worker_group(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION amesh_active_tenants_for_worker_group(text) TO amesh_runtime;

COMMIT;
