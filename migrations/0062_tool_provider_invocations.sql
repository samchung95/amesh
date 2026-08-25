BEGIN;

CREATE TABLE tool_invocations (
    invocation_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    execution_id uuid NOT NULL,
    task_run_id uuid NOT NULL,
    attempt integer NOT NULL CHECK (attempt > 0),
    provider_kind text NOT NULL CHECK (provider_kind IN ('mcp', 'plugin')),
    provider_key text NOT NULL,
    provider_revision integer NOT NULL CHECK (provider_revision > 0),
    tool_name text NOT NULL,
    schema_digest text NOT NULL CHECK (schema_digest ~ '^sha256:[0-9a-f]{64}$'),
    policy_digest text NOT NULL CHECK (policy_digest ~ '^sha256:[0-9a-f]{64}$'),
    state text NOT NULL CHECK (state IN ('STARTED', 'SUCCEEDED', 'FAILED')),
    request_hash text NOT NULL CHECK (request_hash ~ '^[0-9a-f]{64}$'),
    request_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    result jsonb NULL,
    error text NULL,
    started_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    UNIQUE (
        tenant_id, task_run_id, attempt, provider_kind, provider_key,
        provider_revision, tool_name
    ),
    CHECK (
        (state = 'STARTED' AND completed_at IS NULL)
        OR (state = 'SUCCEEDED' AND result IS NOT NULL AND completed_at IS NOT NULL)
        OR (state = 'FAILED' AND error IS NOT NULL AND completed_at IS NOT NULL)
    )
);

CREATE INDEX tool_invocation_execution_idx
    ON tool_invocations (tenant_id, execution_id, task_run_id, attempt);

ALTER TABLE tool_invocations ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_invocations FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON tool_invocations TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE ON tool_invocations TO amesh_runtime;

COMMIT;
