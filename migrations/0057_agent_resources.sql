BEGIN;

CREATE TABLE agent_resource_revisions (
    resource_id uuid NOT NULL,
    revision integer NOT NULL CHECK (revision > 0),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    resource_kind text NOT NULL CHECK (
        resource_kind IN ('PROMPT', 'SKILL', 'MODEL_POLICY', 'AGENT')
    ),
    resource_key text NOT NULL,
    digest text NOT NULL CHECK (digest ~ '^sha256:[0-9a-f]{64}$'),
    spec jsonb NOT NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (resource_id, revision),
    UNIQUE (tenant_id, namespace_name, resource_kind, resource_key, revision)
);

CREATE INDEX agent_resource_lookup_idx
    ON agent_resource_revisions (
        tenant_id, namespace_name, resource_kind, resource_key, revision DESC
    );

CREATE TABLE agent_capability_pins (
    pin_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    agent_resource_id uuid NOT NULL,
    agent_revision integer NOT NULL CHECK (agent_revision > 0),
    subject_ref text NOT NULL,
    envelope_digest text NOT NULL CHECK (envelope_digest ~ '^sha256:[0-9a-f]{64}$'),
    envelope jsonb NOT NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (tenant_id, namespace_name, subject_ref),
    FOREIGN KEY (agent_resource_id, agent_revision)
        REFERENCES agent_resource_revisions (resource_id, revision)
);

CREATE INDEX agent_capability_pin_agent_idx
    ON agent_capability_pins (
        tenant_id, namespace_name, agent_resource_id, agent_revision
    );

ALTER TABLE agent_resource_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_resource_revisions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_resource_revisions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE agent_capability_pins ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_capability_pins FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_capability_pins TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT ON
    agent_resource_revisions,
    agent_capability_pins
TO amesh_runtime;

COMMIT;
