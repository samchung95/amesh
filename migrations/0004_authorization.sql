BEGIN;

CREATE TABLE auth_principals (
    id uuid PRIMARY KEY,
    principal_type text NOT NULL
        CHECK (principal_type IN ('USER', 'GROUP', 'SERVICE_ACCOUNT', 'WORKER', 'PLUGIN')),
    handle text NOT NULL,
    display_name text NOT NULL,
    enabled boolean NOT NULL DEFAULT true,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    annotations jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_by text NOT NULL,
    updated_by text NOT NULL,
    resource_version bigint NOT NULL DEFAULT 1,
    lifecycle text NOT NULL DEFAULT 'ACTIVE'
        CHECK (lifecycle IN ('ACTIVE', 'ARCHIVED', 'TOMBSTONED')),
    archived_at timestamptz NULL,
    deleted_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (principal_type, handle)
);

CREATE TABLE auth_group_memberships (
    group_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    member_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (group_id, member_id),
    CHECK (group_id <> member_id)
);

CREATE TABLE auth_roles (
    name text PRIMARY KEY,
    display_name text NOT NULL,
    description text NOT NULL DEFAULT '',
    built_in boolean NOT NULL DEFAULT false,
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE auth_role_permissions (
    role_name text NOT NULL REFERENCES auth_roles(name) ON DELETE CASCADE,
    resource_type text NOT NULL,
    action text NOT NULL
        CHECK (action IN ('*', 'view', 'create', 'update', 'delete', 'execute', 'manage', 'use')),
    effect text NOT NULL CHECK (effect IN ('ALLOW', 'DENY')),
    PRIMARY KEY (role_name, resource_type, action, effect)
);

CREATE TABLE auth_role_bindings (
    id uuid PRIMARY KEY,
    principal_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    role_name text NOT NULL REFERENCES auth_roles(name),
    scope_type text NOT NULL CHECK (scope_type IN ('INSTANCE', 'TENANT', 'NAMESPACE')),
    tenant_id uuid NULL REFERENCES tenants(id) ON DELETE CASCADE,
    namespace_name text NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (
        (scope_type = 'INSTANCE' AND tenant_id IS NULL AND namespace_name IS NULL)
        OR (scope_type = 'TENANT' AND tenant_id IS NOT NULL AND namespace_name IS NULL)
        OR (scope_type = 'NAMESPACE' AND tenant_id IS NOT NULL AND namespace_name IS NOT NULL)
    )
);

CREATE UNIQUE INDEX auth_role_bindings_natural_key
    ON auth_role_bindings (
        principal_id,
        role_name,
        scope_type,
        COALESCE(tenant_id, '00000000-0000-0000-0000-000000000000'::uuid),
        COALESCE(namespace_name, '')
    );

CREATE INDEX auth_role_bindings_principal_idx
    ON auth_role_bindings (principal_id, scope_type, tenant_id, namespace_name);

CREATE TABLE auth_namespace_boundaries (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    namespace_name text NOT NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, namespace_name)
);

CREATE TABLE auth_policy_state (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    version bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
    updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO auth_policy_state (singleton, version) VALUES (true, 1);

INSERT INTO auth_roles (name, display_name, description, built_in, created_by, updated_by)
VALUES
    ('instance-admin', 'Instance administrator', 'Full instance authority.', true, 'migration:0004', 'migration:0004'),
    ('tenant-admin', 'Tenant administrator', 'Full authority inside the binding tenant.', true, 'migration:0004', 'migration:0004'),
    ('namespace-admin', 'Namespace administrator', 'Full authority inside the binding namespace subtree.', true, 'migration:0004', 'migration:0004'),
    ('flow-author', 'Flow author', 'Author flows and start or inspect executions.', true, 'migration:0004', 'migration:0004'),
    ('operator', 'Operator', 'Inspect flows and operate executions.', true, 'migration:0004', 'migration:0004'),
    ('viewer', 'Viewer', 'Read-only access inside the binding scope.', true, 'migration:0004', 'migration:0004');

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES
    ('instance-admin', '*', '*', 'ALLOW'),
    ('tenant-admin', '*', '*', 'ALLOW'),
    ('namespace-admin', '*', '*', 'ALLOW'),
    ('flow-author', 'flow', 'view', 'ALLOW'),
    ('flow-author', 'flow', 'create', 'ALLOW'),
    ('flow-author', 'flow', 'update', 'ALLOW'),
    ('flow-author', 'flow', 'delete', 'ALLOW'),
    ('flow-author', 'flow', 'use', 'ALLOW'),
    ('flow-author', 'execution', 'view', 'ALLOW'),
    ('flow-author', 'execution', 'create', 'ALLOW'),
    ('flow-author', 'execution', 'execute', 'ALLOW'),
    ('operator', 'flow', 'view', 'ALLOW'),
    ('operator', 'execution', 'view', 'ALLOW'),
    ('operator', 'execution', 'create', 'ALLOW'),
    ('operator', 'execution', 'execute', 'ALLOW'),
    ('operator', 'execution', 'manage', 'ALLOW'),
    ('operator', 'worker', 'view', 'ALLOW'),
    ('viewer', '*', 'view', 'ALLOW');

CREATE OR REPLACE FUNCTION bump_auth_policy_version() RETURNS trigger AS $$
BEGIN
    UPDATE auth_policy_state
    SET version = version + 1,
        updated_at = now()
    WHERE singleton = true;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auth_principals_policy_version
AFTER INSERT OR UPDATE OR DELETE ON auth_principals
FOR EACH STATEMENT EXECUTE FUNCTION bump_auth_policy_version();

CREATE TRIGGER auth_group_memberships_policy_version
AFTER INSERT OR UPDATE OR DELETE ON auth_group_memberships
FOR EACH STATEMENT EXECUTE FUNCTION bump_auth_policy_version();

CREATE TRIGGER auth_roles_policy_version
AFTER INSERT OR UPDATE OR DELETE ON auth_roles
FOR EACH STATEMENT EXECUTE FUNCTION bump_auth_policy_version();

CREATE TRIGGER auth_role_permissions_policy_version
AFTER INSERT OR UPDATE OR DELETE ON auth_role_permissions
FOR EACH STATEMENT EXECUTE FUNCTION bump_auth_policy_version();

CREATE TRIGGER auth_role_bindings_policy_version
AFTER INSERT OR UPDATE OR DELETE ON auth_role_bindings
FOR EACH STATEMENT EXECUTE FUNCTION bump_auth_policy_version();

CREATE TRIGGER auth_namespace_boundaries_policy_version
AFTER INSERT OR UPDATE OR DELETE ON auth_namespace_boundaries
FOR EACH STATEMENT EXECUTE FUNCTION bump_auth_policy_version();

COMMIT;
