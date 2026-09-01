BEGIN;

CREATE TABLE agent_session_policy_revisions (
    policy_id uuid NOT NULL,
    revision integer NOT NULL CHECK (revision > 0),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NULL,
    application_id text NULL,
    active boolean NOT NULL DEFAULT true,
    admission_enabled boolean NOT NULL,
    max_concurrency integer NOT NULL CHECK (max_concurrency BETWEEN 1 AND 1000),
    max_total_tokens bigint NOT NULL CHECK (max_total_tokens BETWEEN 1 AND 10000000),
    max_cost_usd numeric NOT NULL CHECK (max_cost_usd >= 0),
    max_duration_seconds integer NOT NULL CHECK (max_duration_seconds BETWEEN 1 AND 86400),
    retention_seconds integer NOT NULL CHECK (retention_seconds BETWEEN 0 AND 31536000),
    allowed_provider_ids text[] NOT NULL DEFAULT '{}'::text[],
    allowed_harness_ids text[] NOT NULL DEFAULT '{}'::text[],
    allowed_tool_ids text[] NOT NULL DEFAULT '{}'::text[],
    digest text NOT NULL CHECK (digest ~ '^sha256:[0-9a-f]{64}$'),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (policy_id, revision),
    CHECK (namespace_name IS NULL OR length(namespace_name) BETWEEN 1 AND 255),
    CHECK (application_id IS NULL OR (namespace_name IS NOT NULL AND length(application_id) BETWEEN 1 AND 255)),
    CHECK (cardinality(allowed_provider_ids) <= 100),
    CHECK (cardinality(allowed_harness_ids) <= 100),
    CHECK (cardinality(allowed_tool_ids) <= 100),
    CHECK (array_position(allowed_provider_ids, NULL) IS NULL),
    CHECK (array_position(allowed_harness_ids, NULL) IS NULL),
    CHECK (array_position(allowed_tool_ids, NULL) IS NULL)
);

CREATE UNIQUE INDEX agent_session_policy_active_identity_idx
    ON agent_session_policy_revisions (
        tenant_id,
        COALESCE(namespace_name, ''),
        COALESCE(application_id, '')
    )
    WHERE active;

CREATE INDEX agent_session_policy_history_idx
    ON agent_session_policy_revisions (tenant_id, namespace_name, revision DESC);

ALTER TABLE agent_session_policy_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_session_policy_revisions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_session_policy_revisions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE ON agent_session_policy_revisions TO amesh_runtime;

COMMIT;
