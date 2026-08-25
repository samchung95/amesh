BEGIN;

CREATE TABLE agent_mcp_connection_revisions (
    connection_id uuid NOT NULL,
    revision integer NOT NULL CHECK (revision > 0),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    connection_key text NOT NULL,
    digest text NOT NULL CHECK (digest ~ '^sha256:[0-9a-f]{64}$'),
    spec jsonb NOT NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (connection_id, revision),
    UNIQUE (tenant_id, namespace_name, connection_key, revision)
);

CREATE INDEX agent_mcp_connection_lookup_idx
    ON agent_mcp_connection_revisions (
        tenant_id, namespace_name, connection_key, revision DESC
    );

CREATE TABLE agent_invocations (
    invocation_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    execution_id uuid NOT NULL,
    task_run_id uuid NOT NULL,
    attempt integer NOT NULL CHECK (attempt > 0),
    kind text NOT NULL CHECK (kind IN ('MODEL', 'MCP')),
    operation text NOT NULL,
    state text NOT NULL CHECK (state IN ('STARTED', 'SUCCEEDED', 'FAILED')),
    request_hash text NOT NULL CHECK (request_hash ~ '^[0-9a-f]{64}$'),
    request_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    result jsonb NULL,
    error text NULL,
    started_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    UNIQUE (tenant_id, task_run_id, attempt, kind, operation),
    CHECK (
        (state = 'STARTED' AND completed_at IS NULL)
        OR (state IN ('SUCCEEDED', 'FAILED') AND completed_at IS NOT NULL)
    )
);

CREATE INDEX agent_invocation_execution_idx
    ON agent_invocations (tenant_id, execution_id, task_run_id, attempt);

ALTER TABLE agent_mcp_connection_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_mcp_connection_revisions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_mcp_connection_revisions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE agent_invocations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_invocations FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_invocations TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE ON
    agent_mcp_connection_revisions,
    agent_invocations
TO amesh_runtime;

COMMIT;
