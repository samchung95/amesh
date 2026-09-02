BEGIN;

GRANT SELECT ON workers, task_attempts, leases, scheduler_states TO amesh_tenant_admin;

ALTER FUNCTION amesh_rebuild_disposable_projections() SECURITY DEFINER;
ALTER FUNCTION amesh_rebuild_disposable_projections()
    SET search_path = pg_catalog, public;

COMMIT;
