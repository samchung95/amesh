BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'amesh_tenant_resolver') THEN
        CREATE ROLE amesh_tenant_resolver
            NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT BYPASSRLS;
    END IF;
END;
$$;

GRANT USAGE ON SCHEMA public TO amesh_tenant_resolver;
GRANT SELECT ON tenants TO amesh_tenant_resolver;

CREATE OR REPLACE FUNCTION amesh_resolve_active_tenant(tenant_slug text) RETURNS uuid AS $$
    SELECT id
    FROM public.tenants
    WHERE slug = tenant_slug
      AND status = 'ACTIVE'
      AND lifecycle = 'ACTIVE'
$$ LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog, public;

ALTER FUNCTION amesh_resolve_active_tenant(text) OWNER TO amesh_tenant_resolver;
REVOKE ALL ON FUNCTION amesh_resolve_active_tenant(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION amesh_resolve_active_tenant(text) TO amesh_runtime;

COMMIT;
