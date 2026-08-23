BEGIN;

CREATE TABLE plugin_policy_rules (
    id uuid PRIMARY KEY,
    tenant_id uuid NULL REFERENCES tenants(id),
    namespace_name text NULL,
    scope text NOT NULL CHECK (scope IN ('INSTANCE', 'TENANT', 'NAMESPACE')),
    effect text NOT NULL CHECK (effect IN ('ALLOW', 'DENY')),
    stages text[] NOT NULL CHECK (
        cardinality(stages) > 0
        AND stages <@ ARRAY['AUTHORING', 'VALIDATION', 'EXECUTION', 'ADMINISTRATION']::text[]
    ),
    package_pattern text NOT NULL,
    version_range text NOT NULL,
    vendor_pattern text NOT NULL,
    plugin_types text[] NOT NULL DEFAULT '{}'::text[],
    capabilities text[] NOT NULL DEFAULT '{}'::text[],
    priority integer NOT NULL DEFAULT 0 CHECK (priority BETWEEN -10000 AND 10000),
    reason text NOT NULL,
    enabled boolean NOT NULL DEFAULT true,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_by text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (
        (scope = 'INSTANCE' AND tenant_id IS NULL AND namespace_name IS NULL)
        OR (scope = 'TENANT' AND tenant_id IS NOT NULL AND namespace_name IS NULL)
        OR (scope = 'NAMESPACE' AND tenant_id IS NOT NULL AND namespace_name IS NOT NULL)
    )
);

CREATE INDEX plugin_policy_rules_effective_idx
    ON plugin_policy_rules (tenant_id, namespace_name, enabled, priority DESC, id);

CREATE TABLE plugin_quarantines (
    id uuid PRIMARY KEY,
    tenant_id uuid NULL REFERENCES tenants(id),
    namespace_name text NULL,
    scope text NOT NULL CHECK (scope IN ('INSTANCE', 'TENANT', 'NAMESPACE')),
    package_name text NOT NULL,
    version text NOT NULL,
    reason text NOT NULL,
    state text NOT NULL DEFAULT 'ACTIVE' CHECK (state IN ('ACTIVE', 'RELEASED')),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    released_by text NULL,
    released_at timestamptz NULL,
    CHECK (
        (scope = 'INSTANCE' AND tenant_id IS NULL AND namespace_name IS NULL)
        OR (scope = 'TENANT' AND tenant_id IS NOT NULL AND namespace_name IS NULL)
        OR (scope = 'NAMESPACE' AND tenant_id IS NOT NULL AND namespace_name IS NOT NULL)
    ),
    CHECK (
        (state = 'ACTIVE' AND released_by IS NULL AND released_at IS NULL)
        OR (state = 'RELEASED' AND released_by IS NOT NULL AND released_at IS NOT NULL)
    )
);

CREATE UNIQUE INDEX plugin_quarantines_active_identity_idx
    ON plugin_quarantines (
        scope,
        COALESCE(tenant_id, '00000000-0000-0000-0000-000000000000'::uuid),
        COALESCE(namespace_name, ''),
        package_name,
        version
    ) WHERE state = 'ACTIVE';

CREATE TABLE plugin_policy_decisions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    stage text NOT NULL CHECK (
        stage IN ('AUTHORING', 'VALIDATION', 'EXECUTION', 'ADMINISTRATION')
    ),
    allowed boolean NOT NULL,
    flow_key text NULL,
    flow_revision integer NULL,
    actor_id text NOT NULL,
    decision jsonb NOT NULL,
    decided_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX plugin_policy_decisions_history_idx
    ON plugin_policy_decisions (tenant_id, decided_at DESC, id);
CREATE INDEX plugin_policy_decisions_denied_idx
    ON plugin_policy_decisions (tenant_id, stage, decided_at DESC)
    WHERE NOT allowed;

ALTER TABLE plugin_policy_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE plugin_policy_rules FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON plugin_policy_rules TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

ALTER TABLE plugin_quarantines ENABLE ROW LEVEL SECURITY;
ALTER TABLE plugin_quarantines FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON plugin_quarantines TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

ALTER TABLE plugin_policy_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE plugin_policy_decisions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON plugin_policy_decisions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE, DELETE ON
    plugin_policy_rules,
    plugin_quarantines,
    plugin_policy_decisions
TO amesh_runtime;

COMMIT;
