BEGIN;

ALTER TABLE agent_resource_revisions
    DROP CONSTRAINT agent_resource_revisions_resource_kind_check;
ALTER TABLE agent_resource_revisions
    ADD CONSTRAINT agent_resource_revisions_resource_kind_check CHECK (
        resource_kind IN ('PROMPT', 'SKILL', 'MODEL_POLICY', 'EVALUATION', 'AGENT')
    );

CREATE TABLE agent_memory_entries (
    entry_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    scope text NOT NULL CHECK (scope IN ('EXECUTION', 'PRIVATE', 'SHARED')),
    scope_key text NOT NULL,
    source_execution_id uuid NOT NULL,
    producer_agent_key text NOT NULL,
    producer_agent_revision integer NOT NULL CHECK (producer_agent_revision > 0),
    memory_key text NOT NULL,
    content jsonb NOT NULL,
    content_digest text NOT NULL CHECK (content_digest ~ '^sha256:[0-9a-f]{64}$'),
    byte_size integer NOT NULL CHECK (byte_size >= 0),
    provenance jsonb NOT NULL DEFAULT '{}'::jsonb,
    redacted boolean NOT NULL DEFAULT true,
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    expires_at timestamptz NOT NULL,
    deleted_at timestamptz NULL,
    CONSTRAINT agent_memory_source_execution_fk
        FOREIGN KEY (tenant_id, source_execution_id)
        REFERENCES executions (tenant_id, id) ON DELETE CASCADE,
    UNIQUE (tenant_id, namespace_name, scope, scope_key, memory_key)
);

CREATE INDEX agent_memory_active_scope_idx
    ON agent_memory_entries (
        tenant_id, namespace_name, scope, scope_key, expires_at, memory_key
    )
    WHERE deleted_at IS NULL;

CREATE INDEX agent_memory_agent_catalog_idx
    ON agent_memory_entries (
        tenant_id, namespace_name, producer_agent_key, updated_at DESC
    )
    WHERE deleted_at IS NULL;

ALTER TABLE agent_memory_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory_entries FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_memory_entries TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE ON agent_memory_entries TO amesh_runtime;

COMMIT;
