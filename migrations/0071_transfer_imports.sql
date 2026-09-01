BEGIN;

CREATE TABLE agent_transfer_imports (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    import_id text NOT NULL CHECK (length(import_id) BETWEEN 1 AND 1024),
    transfer_kind text NOT NULL CHECK (transfer_kind IN ('PROFILE', 'SESSION')),
    source_tenant_key text NOT NULL CHECK (length(source_tenant_key) BETWEEN 1 AND 255),
    target_tenant_id uuid NOT NULL REFERENCES tenants(id),
    bundle_digest text NOT NULL CHECK (bundle_digest ~ '^[0-9a-f]{64}$'),
    session_id uuid,
    mode text,
    agent_key text,
    agent_revision integer CHECK (agent_revision IS NULL OR agent_revision > 0),
    result jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_by text NOT NULL CHECK (length(created_by) BETWEEN 1 AND 255),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (target_tenant_id, import_id),
    CHECK (
        (transfer_kind = 'PROFILE' AND agent_key IS NOT NULL AND agent_revision IS NOT NULL
            AND session_id IS NULL AND mode IS NULL)
        OR
        (transfer_kind = 'SESSION' AND session_id IS NOT NULL
            AND mode IN ('TERMINAL_HISTORY', 'CLEAN_CHECKPOINT')
            AND agent_key IS NULL AND agent_revision IS NULL)
    )
);

CREATE INDEX agent_transfer_imports_target_idx
    ON agent_transfer_imports (target_tenant_id, created_at DESC);

ALTER TABLE agent_transfer_imports ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_transfer_imports FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_transfer_imports TO amesh_runtime
    USING (target_tenant_id = amesh_current_tenant_id())
    WITH CHECK (target_tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT ON agent_transfer_imports TO amesh_runtime;

COMMIT;
