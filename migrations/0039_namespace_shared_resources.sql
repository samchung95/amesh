BEGIN;

ALTER TABLE auth_role_permissions DROP CONSTRAINT auth_role_permissions_action_check;
ALTER TABLE auth_role_permissions ADD CONSTRAINT auth_role_permissions_action_check
    CHECK (action IN (
        '*', 'view', 'create', 'update', 'delete', 'execute', 'manage', 'use',
        'list', 'read', 'write'
    ));

CREATE TABLE namespace_files (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_id uuid NOT NULL REFERENCES namespaces(id),
    path text NOT NULL CHECK (path <> '' AND path !~ '(^|/)\\.\\.?(/|$)'),
    current_version bigint NOT NULL CHECK (current_version > 0),
    resource_version bigint NOT NULL CHECK (resource_version > 0),
    deleted boolean NOT NULL DEFAULT false,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, namespace_id, path)
);

CREATE TABLE namespace_file_versions (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_id uuid NOT NULL REFERENCES namespaces(id),
    path text NOT NULL,
    version bigint NOT NULL CHECK (version > 0),
    object_uri text NOT NULL,
    size_bytes bigint NOT NULL CHECK (size_bytes >= 0),
    checksum_sha256 text NOT NULL CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$'),
    content_type text NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, namespace_id, path, version),
    FOREIGN KEY (tenant_id, namespace_id, path)
        REFERENCES namespace_files(tenant_id, namespace_id, path) ON DELETE CASCADE
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE namespace_key_values (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_id uuid NOT NULL REFERENCES namespaces(id),
    key text NOT NULL CHECK (key <> '' AND length(key) <= 256),
    value_type text NOT NULL CHECK (
        value_type IN ('STRING', 'NUMBER', 'BOOLEAN', 'DATETIME', 'DATE', 'DURATION', 'JSON')
    ),
    value jsonb NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    expires_at timestamptz NULL,
    resource_version bigint NOT NULL CHECK (resource_version > 0),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, namespace_id, key)
);

CREATE TABLE namespace_key_value_changes (
    cursor bigserial PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_id uuid NOT NULL REFERENCES namespaces(id),
    key text NOT NULL,
    operation text NOT NULL CHECK (operation IN ('UPSERT', 'DELETE', 'EXPIRE')),
    resource_version bigint NOT NULL CHECK (resource_version > 0),
    value_type text NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE namespace_secret_bindings (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_id uuid NOT NULL REFERENCES namespaces(id),
    key text NOT NULL CHECK (key <> '' AND length(key) <= 256),
    provider text NOT NULL CHECK (provider IN ('env')),
    provider_reference text NOT NULL CHECK (provider_reference <> ''),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    resource_version bigint NOT NULL CHECK (resource_version > 0),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, namespace_id, key)
);

CREATE INDEX namespace_files_path_idx
    ON namespace_files (tenant_id, namespace_id, path) WHERE deleted = false;
CREATE INDEX namespace_file_versions_created_idx
    ON namespace_file_versions (tenant_id, namespace_id, path, version DESC);
CREATE INDEX namespace_key_values_expiry_idx
    ON namespace_key_values (tenant_id, expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX namespace_key_value_changes_poll_idx
    ON namespace_key_value_changes (tenant_id, namespace_id, cursor);

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES
    ('flow-author', 'namespace_file', 'list', 'ALLOW'),
    ('flow-author', 'namespace_file', 'read', 'ALLOW'),
    ('flow-author', 'namespace_file', 'write', 'ALLOW'),
    ('flow-author', 'namespace_file', 'delete', 'ALLOW'),
    ('flow-author', 'namespace_file', 'use', 'ALLOW'),
    ('flow-author', 'key_value', 'list', 'ALLOW'),
    ('flow-author', 'key_value', 'read', 'ALLOW'),
    ('flow-author', 'key_value', 'write', 'ALLOW'),
    ('flow-author', 'key_value', 'delete', 'ALLOW'),
    ('flow-author', 'key_value', 'use', 'ALLOW'),
    ('flow-author', 'secret', 'list', 'ALLOW'),
    ('flow-author', 'secret', 'use', 'ALLOW'),
    ('viewer', 'namespace_file', 'list', 'ALLOW'),
    ('viewer', 'namespace_file', 'read', 'ALLOW'),
    ('viewer', 'key_value', 'list', 'ALLOW'),
    ('viewer', 'key_value', 'read', 'ALLOW'),
    ('viewer', 'secret', 'list', 'ALLOW')
ON CONFLICT DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE ON
    namespace_files,
    namespace_file_versions,
    namespace_key_values,
    namespace_key_value_changes,
    namespace_secret_bindings
TO amesh_runtime;
GRANT USAGE, SELECT ON SEQUENCE namespace_key_value_changes_cursor_seq TO amesh_runtime;

ALTER TABLE namespace_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE namespace_files FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON namespace_files TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE namespace_file_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE namespace_file_versions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON namespace_file_versions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE namespace_key_values ENABLE ROW LEVEL SECURITY;
ALTER TABLE namespace_key_values FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON namespace_key_values TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE namespace_key_value_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE namespace_key_value_changes FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON namespace_key_value_changes TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE namespace_secret_bindings ENABLE ROW LEVEL SECURITY;
ALTER TABLE namespace_secret_bindings FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON namespace_secret_bindings TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
