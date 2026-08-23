BEGIN;

CREATE TABLE flow_test_definitions (
    definition_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    flow_id text NOT NULL,
    test_id text NOT NULL,
    test_name text NOT NULL,
    flow_revision bigint NOT NULL CHECK (flow_revision > 0),
    flow_semantic_hash text NOT NULL CHECK (flow_semantic_hash <> ''),
    plugin_set_hash text NOT NULL CHECK (plugin_set_hash <> ''),
    inputs jsonb NOT NULL DEFAULT '{}'::jsonb,
    variables jsonb NOT NULL DEFAULT '{}'::jsonb,
    fixtures jsonb NOT NULL DEFAULT '{}'::jsonb,
    expected jsonb NOT NULL DEFAULT '{}'::jsonb,
    tags text[] NOT NULL DEFAULT ARRAY[]::text[],
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT flow_test_definition_objects CHECK (
        jsonb_typeof(inputs) = 'object'
        AND jsonb_typeof(variables) = 'object'
        AND jsonb_typeof(fixtures) = 'object'
        AND jsonb_typeof(expected) = 'object'
    ),
    UNIQUE (tenant_id, namespace_name, flow_id, test_id)
);

CREATE INDEX flow_test_definitions_revision_idx
    ON flow_test_definitions (tenant_id, namespace_name, flow_id, flow_revision, test_id);

CREATE TABLE flow_test_runs (
    run_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    flow_id text NOT NULL,
    flow_revision bigint NOT NULL CHECK (flow_revision > 0),
    flow_semantic_hash text NOT NULL CHECK (flow_semantic_hash <> ''),
    plugin_set_hash text NOT NULL CHECK (plugin_set_hash <> ''),
    simulator_version text NOT NULL CHECK (simulator_version <> ''),
    outcome text NOT NULL CHECK (outcome IN ('PASSED', 'FAILED', 'ERROR')),
    result jsonb NOT NULL,
    requested_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT flow_test_run_result_object CHECK (jsonb_typeof(result) = 'object')
);

CREATE INDEX flow_test_runs_gate_idx
    ON flow_test_runs (
        tenant_id,
        namespace_name,
        flow_id,
        flow_revision,
        flow_semantic_hash,
        plugin_set_hash,
        simulator_version,
        created_at DESC
    );

CREATE TABLE flow_test_quality_gates (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    enabled boolean NOT NULL DEFAULT true,
    minimum_coverage numeric(5,2) NOT NULL DEFAULT 0
        CHECK (minimum_coverage >= 0 AND minimum_coverage <= 100),
    required_test_ids text[] NOT NULL DEFAULT ARRAY[]::text[],
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    updated_by text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, namespace_name)
);

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES
    ('flow-author', 'flow_test', 'view', 'ALLOW'),
    ('flow-author', 'flow_test', 'create', 'ALLOW'),
    ('flow-author', 'flow_test', 'update', 'ALLOW'),
    ('flow-author', 'flow_test', 'delete', 'ALLOW'),
    ('flow-author', 'flow_test', 'execute', 'ALLOW'),
    ('operator', 'flow_test', 'view', 'ALLOW'),
    ('operator', 'flow_test', 'execute', 'ALLOW'),
    ('viewer', 'flow_test', 'view', 'ALLOW')
ON CONFLICT DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE ON flow_test_definitions TO amesh_tenant_admin;
GRANT SELECT, INSERT ON flow_test_runs TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON flow_test_quality_gates TO amesh_tenant_admin;

ALTER TABLE flow_test_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE flow_test_definitions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_visibility ON flow_test_definitions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id());

ALTER TABLE flow_test_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE flow_test_runs FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_visibility ON flow_test_runs TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id());

ALTER TABLE flow_test_quality_gates ENABLE ROW LEVEL SECURITY;
ALTER TABLE flow_test_quality_gates FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_visibility ON flow_test_quality_gates TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id());

COMMIT;
