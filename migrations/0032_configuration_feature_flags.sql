BEGIN;

CREATE TABLE feature_flags (
    id uuid PRIMARY KEY,
    flag_key varchar(128) NOT NULL,
    scope varchar(16) NOT NULL CHECK (scope IN ('INSTANCE', 'TENANT', 'NAMESPACE')),
    tenant_id uuid NULL REFERENCES tenants(id),
    namespace varchar(255) NULL,
    enabled boolean NOT NULL,
    description text NOT NULL DEFAULT '',
    version bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
    updated_by varchar(255) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT feature_flags_scope_identity UNIQUE NULLS NOT DISTINCT (
        flag_key, scope, tenant_id, namespace
    ),
    CONSTRAINT feature_flags_scope_shape CHECK (
        (scope = 'INSTANCE' AND tenant_id IS NULL AND namespace IS NULL)
        OR (scope = 'TENANT' AND tenant_id IS NOT NULL AND namespace IS NULL)
        OR (scope = 'NAMESPACE' AND tenant_id IS NOT NULL AND namespace IS NOT NULL)
    )
);

CREATE INDEX feature_flags_context_idx
    ON feature_flags (tenant_id, namespace, flag_key, scope);

ALTER TABLE feature_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_flags FORCE ROW LEVEL SECURITY;

CREATE POLICY feature_flags_runtime_read ON feature_flags
    FOR SELECT TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

GRANT SELECT ON feature_flags TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON feature_flags TO amesh_tenant_admin;

COMMIT;
