BEGIN;

CREATE TABLE task_cache_entries (
    entry_id uuid NOT NULL,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    key_hash text NOT NULL CHECK (key_hash ~ '^[0-9a-f]{64}$'),
    key_prefix text NOT NULL,
    cache_namespace text NOT NULL,
    scope text NOT NULL CHECK (scope IN ('TASK', 'FLOW', 'NAMESPACE')),
    namespace_name text NOT NULL,
    flow_id text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    task_id text NOT NULL,
    task_type text NOT NULL,
    security_context_hash text NOT NULL
        CHECK (security_context_hash ~ '^[0-9a-f]{64}$'),
    invalidation_policy text NOT NULL,
    state text NOT NULL CHECK (state IN ('POPULATING', 'READY', 'INVALIDATED')),
    owner_token uuid NULL,
    lease_expires_at timestamptz NULL,
    output jsonb NULL,
    evidence jsonb NULL,
    source_execution_id uuid NULL,
    source_task_run_id uuid NULL,
    source_attempt integer NULL CHECK (source_attempt IS NULL OR source_attempt > 0),
    expires_at timestamptz NOT NULL,
    hit_count bigint NOT NULL DEFAULT 0 CHECK (hit_count >= 0),
    last_hit_at timestamptz NULL,
    invalidation_reason text NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, entry_id),
    UNIQUE (tenant_id, key_hash),
    CONSTRAINT task_cache_output_object
        CHECK (output IS NULL OR jsonb_typeof(output) = 'object'),
    CONSTRAINT task_cache_evidence_object
        CHECK (evidence IS NULL OR jsonb_typeof(evidence) = 'object')
);

CREATE TABLE task_cache_events (
    sequence bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    event_id uuid NOT NULL,
    entry_id uuid NULL,
    key_hash text NULL CHECK (key_hash IS NULL OR key_hash ~ '^[0-9a-f]{64}$'),
    event_type text NOT NULL CHECK (
        event_type IN (
            'HIT', 'MISS', 'MISS_EXPIRED', 'MISS_INVALIDATED',
            'MISS_CONCURRENT', 'REFRESH', 'BYPASS', 'FILLED', 'ABANDONED', 'PURGED'
        )
    ),
    reason text NOT NULL,
    execution_id uuid NULL,
    task_run_id uuid NULL,
    attempt integer NULL CHECK (attempt IS NULL OR attempt > 0),
    actor_id text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (tenant_id, event_id),
    CONSTRAINT task_cache_event_payload_object CHECK (jsonb_typeof(payload) = 'object'),
    CONSTRAINT task_cache_event_entry_fk
        FOREIGN KEY (tenant_id, entry_id)
        REFERENCES task_cache_entries (tenant_id, entry_id)
);

CREATE INDEX task_cache_entries_prefix_idx
    ON task_cache_entries (tenant_id, key_prefix text_pattern_ops);
CREATE INDEX task_cache_entries_resource_idx
    ON task_cache_entries (tenant_id, namespace_name, flow_id, task_id, updated_at DESC);
CREATE INDEX task_cache_entries_expiry_idx
    ON task_cache_entries (tenant_id, state, expires_at);
CREATE INDEX task_cache_events_execution_idx
    ON task_cache_events (tenant_id, execution_id, sequence);

GRANT SELECT, INSERT, UPDATE, DELETE ON task_cache_entries TO amesh_runtime;
GRANT SELECT, INSERT ON task_cache_events TO amesh_runtime;
GRANT USAGE, SELECT ON SEQUENCE task_cache_events_sequence_seq TO amesh_runtime;

ALTER TABLE task_cache_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_cache_entries FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON task_cache_entries TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE task_cache_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_cache_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON task_cache_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
