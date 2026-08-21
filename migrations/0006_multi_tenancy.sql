BEGIN;

INSERT INTO tenants (
    id,
    slug,
    display_name,
    status,
    version,
    created_by,
    updated_by
) VALUES (
    '00000000-0000-7000-8000-000000000002',
    'amesh-system',
    'AMESH system tenant',
    'ACTIVE',
    1,
    'migration:0006',
    'migration:0006'
)
ON CONFLICT (slug) DO NOTHING;

ALTER TABLE tenants
    ADD COLUMN settings jsonb NOT NULL DEFAULT '{
        "retention_days": 30,
        "max_concurrent_executions": 100,
        "max_storage_bytes": 10737418240,
        "encryption_key_ref": null,
        "identity_provider_refs": [],
        "plugin_allowlist": ["*"],
        "feature_flags": {},
        "worker_groups": ["default"]
    }'::jsonb,
    ADD COLUMN storage_prefix text NULL;

UPDATE tenants
SET storage_prefix = 'tenants/' || slug || '/'
WHERE storage_prefix IS NULL;

ALTER TABLE tenants
    ALTER COLUMN storage_prefix SET NOT NULL,
    ADD CONSTRAINT tenants_storage_prefix_unique UNIQUE (storage_prefix),
    ADD CONSTRAINT tenants_status_check
        CHECK (status IN ('ACTIVE', 'SUSPENDED', 'TOMBSTONED')),
    ADD CONSTRAINT tenants_settings_object_check
        CHECK (jsonb_typeof(settings) = 'object');

CREATE TABLE tenant_exports (
    export_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    snapshot jsonb NOT NULL,
    resource_counts jsonb NOT NULL,
    exported_by text NOT NULL,
    exported_at timestamptz NOT NULL DEFAULT now(),
    CHECK (jsonb_typeof(snapshot) = 'object'),
    CHECK (jsonb_typeof(resource_counts) = 'object')
);

CREATE INDEX tenant_exports_tenant_exported_idx
    ON tenant_exports (tenant_id, exported_at DESC);

UPDATE workers
SET tenant_id = (SELECT id FROM tenants WHERE slug = 'default')
WHERE tenant_id IS NULL;

ALTER TABLE workers
    ALTER COLUMN tenant_id SET NOT NULL;

UPDATE audit_events
SET tenant_id = '00000000-0000-7000-8000-000000000002'
WHERE tenant_id IS NULL;

ALTER TABLE audit_events
    ALTER COLUMN tenant_id SET DEFAULT '00000000-0000-7000-8000-000000000002',
    ALTER COLUMN tenant_id SET NOT NULL;

CREATE INDEX audit_events_tenant_occurred_idx
    ON audit_events (tenant_id, occurred_at DESC, id DESC);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'amesh_runtime') THEN
        CREATE ROLE amesh_runtime
            NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
    END IF;
    EXECUTE format('GRANT amesh_runtime TO %I', current_user);
END;
$$;

GRANT USAGE ON SCHEMA public TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO amesh_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO amesh_runtime;

CREATE OR REPLACE FUNCTION amesh_current_tenant_id() RETURNS uuid AS $$
    SELECT CASE
        WHEN current_setting('amesh.tenant_id', true) ~
             '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        THEN current_setting('amesh.tenant_id', true)::uuid
        ELSE NULL
    END
$$ LANGUAGE sql STABLE;

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON tenants TO amesh_runtime
    USING (id = amesh_current_tenant_id())
    WITH CHECK (id = amesh_current_tenant_id());

DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'namespaces',
        'flows',
        'flow_revisions',
        'executions',
        'execution_events',
        'commands_inbox',
        'messages_outbox',
        'durable_work_queue',
        'consumed_messages',
        'workers',
        'task_runs',
        'task_attempts',
        'leases',
        'audit_events',
        'tenant_exports',
        'auth_namespace_boundaries'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', table_name);
        EXECUTE format(
            'CREATE POLICY tenant_runtime_isolation ON %I TO amesh_runtime '
            'USING (tenant_id = amesh_current_tenant_id()) '
            'WITH CHECK (tenant_id = amesh_current_tenant_id())',
            table_name
        );
    END LOOP;
END;
$$;

ALTER TABLE auth_role_bindings ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_role_bindings FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON auth_role_bindings TO amesh_runtime
    USING (
        tenant_id = amesh_current_tenant_id()
        OR (
            tenant_id IS NULL
            AND amesh_current_tenant_id() = '00000000-0000-7000-8000-000000000002'
        )
    )
    WITH CHECK (
        tenant_id = amesh_current_tenant_id()
        OR (
            tenant_id IS NULL
            AND amesh_current_tenant_id() = '00000000-0000-7000-8000-000000000002'
        )
    );

COMMIT;
