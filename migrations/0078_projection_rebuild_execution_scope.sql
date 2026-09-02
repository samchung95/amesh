BEGIN;

REVOKE EXECUTE ON FUNCTION amesh_rebuild_disposable_projections() FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION amesh_rebuild_disposable_projections() FROM amesh_runtime;
GRANT EXECUTE ON FUNCTION amesh_rebuild_disposable_projections() TO amesh_tenant_admin;

COMMIT;
