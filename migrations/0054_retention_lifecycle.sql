BEGIN;

CREATE TABLE lifecycle_policies (
    id uuid PRIMARY KEY,
    tenant_id uuid NULL REFERENCES tenants(id),
    resource_type text NOT NULL CHECK (
        resource_type IN ('EXECUTION', 'LOG', 'METRIC', 'ARTIFACT', 'CACHE')
    ),
    scope text NOT NULL CHECK (scope IN ('INSTANCE', 'TENANT', 'NAMESPACE', 'LABEL')),
    namespace_name text NULL,
    label_selector jsonb NOT NULL DEFAULT '{}'::jsonb,
    retention_days integer NOT NULL CHECK (retention_days BETWEEN 1 AND 36500),
    batch_size integer NOT NULL DEFAULT 100 CHECK (batch_size BETWEEN 1 AND 1000),
    schedule_interval_minutes integer NULL CHECK (
        schedule_interval_minutes IS NULL OR schedule_interval_minutes BETWEEN 5 AND 525600
    ),
    next_run_at timestamptz NULL,
    enabled boolean NOT NULL DEFAULT true,
    reason text NOT NULL CHECK (length(reason) BETWEEN 3 AND 2048),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_by text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    CONSTRAINT lifecycle_policy_labels_object CHECK (jsonb_typeof(label_selector) = 'object'),
    CONSTRAINT lifecycle_policy_scope_shape CHECK (
        (scope = 'INSTANCE' AND tenant_id IS NULL AND namespace_name IS NULL
            AND label_selector = '{}'::jsonb)
        OR (scope = 'TENANT' AND tenant_id IS NOT NULL AND namespace_name IS NULL
            AND label_selector = '{}'::jsonb)
        OR (scope = 'NAMESPACE' AND tenant_id IS NOT NULL AND namespace_name IS NOT NULL
            AND label_selector = '{}'::jsonb)
        OR (scope = 'LABEL' AND tenant_id IS NOT NULL AND namespace_name IS NULL
            AND label_selector <> '{}'::jsonb)
    ),
    CONSTRAINT lifecycle_policy_schedule_shape CHECK (
        (schedule_interval_minutes IS NULL AND next_run_at IS NULL)
        OR (schedule_interval_minutes IS NOT NULL AND next_run_at IS NOT NULL)
    )
);

CREATE INDEX lifecycle_policies_effective_idx
    ON lifecycle_policies (tenant_id, resource_type, scope, enabled, updated_at DESC);
CREATE INDEX lifecycle_policies_due_idx
    ON lifecycle_policies (next_run_at, id)
    WHERE enabled AND schedule_interval_minutes IS NOT NULL;

CREATE TABLE lifecycle_legal_holds (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    name text NOT NULL CHECK (length(name) BETWEEN 1 AND 128),
    reason text NOT NULL CHECK (length(reason) BETWEEN 3 AND 2048),
    resource_type text NOT NULL CHECK (
        resource_type IN ('ALL', 'EXECUTION', 'LOG', 'METRIC', 'ARTIFACT', 'CACHE')
    ),
    resource_id text NULL,
    namespace_name text NULL,
    label_selector jsonb NOT NULL DEFAULT '{}'::jsonb,
    data_from timestamptz NULL,
    data_to timestamptz NULL,
    active boolean NOT NULL DEFAULT true,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    released_by text NULL,
    released_at timestamptz NULL,
    CONSTRAINT lifecycle_hold_labels_object CHECK (jsonb_typeof(label_selector) = 'object'),
    CONSTRAINT lifecycle_hold_range CHECK (data_to IS NULL OR data_from IS NULL OR data_to > data_from),
    CONSTRAINT lifecycle_hold_release_shape CHECK (
        (active AND released_by IS NULL AND released_at IS NULL) OR NOT active
    )
);

CREATE INDEX lifecycle_legal_holds_match_idx
    ON lifecycle_legal_holds (tenant_id, active, resource_type, data_from, data_to);

CREATE TABLE lifecycle_jobs (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    policy_id uuid NOT NULL REFERENCES lifecycle_policies(id),
    trigger_kind text NOT NULL CHECK (trigger_kind IN ('MANUAL', 'SCHEDULED')),
    state text NOT NULL CHECK (
        state IN ('PREVIEWED', 'READY', 'RUNNING', 'WAITING_EXTERNAL', 'SUCCEEDED', 'FAILED')
    ),
    cutoff timestamptz NOT NULL,
    policy_snapshot jsonb NOT NULL,
    estimated_records bigint NOT NULL CHECK (estimated_records >= 0),
    estimated_bytes bigint NOT NULL CHECK (estimated_bytes >= 0),
    protected_records bigint NOT NULL DEFAULT 0 CHECK (protected_records >= 0),
    active_records bigint NOT NULL DEFAULT 0 CHECK (active_records >= 0),
    processed_records bigint NOT NULL DEFAULT 0 CHECK (processed_records >= 0),
    processed_bytes bigint NOT NULL DEFAULT 0 CHECK (processed_bytes >= 0),
    batch_size integer NOT NULL CHECK (batch_size BETWEEN 1 AND 1000),
    cursor text NULL,
    retry_count integer NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
    last_error text NULL,
    evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
    reason text NOT NULL CHECK (length(reason) BETWEEN 3 AND 2048),
    actor_id text NOT NULL,
    preview_expires_at timestamptz NOT NULL,
    started_at timestamptz NULL,
    completed_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT lifecycle_job_policy_snapshot_object CHECK (jsonb_typeof(policy_snapshot) = 'object'),
    CONSTRAINT lifecycle_job_evidence_object CHECK (jsonb_typeof(evidence) = 'object')
);

CREATE UNIQUE INDEX lifecycle_jobs_one_active_policy_idx
    ON lifecycle_jobs (tenant_id, policy_id)
    WHERE state IN ('READY', 'RUNNING', 'WAITING_EXTERNAL');
CREATE INDEX lifecycle_jobs_history_idx
    ON lifecycle_jobs (tenant_id, created_at DESC, id);

CREATE TABLE lifecycle_job_items (
    job_id uuid NOT NULL REFERENCES lifecycle_jobs(id) ON DELETE CASCADE,
    ordinal bigint GENERATED ALWAYS AS IDENTITY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    resource_type text NOT NULL,
    resource_id text NOT NULL,
    execution_id uuid NULL,
    object_uri text NULL,
    size_bytes bigint NOT NULL DEFAULT 0 CHECK (size_bytes >= 0),
    state text NOT NULL CHECK (state IN ('PURGED', 'PENDING_EXTERNAL', 'DELETED', 'FAILED')),
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    last_error text NULL,
    decided_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    PRIMARY KEY (job_id, ordinal),
    UNIQUE (job_id, resource_type, resource_id)
);

CREATE INDEX lifecycle_job_items_pending_idx
    ON lifecycle_job_items (tenant_id, job_id, ordinal)
    WHERE state IN ('PENDING_EXTERNAL', 'FAILED');

CREATE TABLE lifecycle_events (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    policy_id uuid NULL REFERENCES lifecycle_policies(id),
    job_id uuid NULL REFERENCES lifecycle_jobs(id),
    event_type text NOT NULL,
    actor_id text NOT NULL,
    reason text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT lifecycle_event_payload_object CHECK (jsonb_typeof(payload) = 'object')
);

CREATE INDEX lifecycle_events_history_idx
    ON lifecycle_events (tenant_id, occurred_at DESC, event_id);

CREATE OR REPLACE FUNCTION amesh_enqueue_lifecycle_event() RETURNS trigger AS $$
BEGIN
    INSERT INTO messages_outbox (
        tenant_id, message_id, subject, partition_key, envelope, available_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        'lifecycle-events',
        'lifecycle:' || NEW.tenant_id::text,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', NEW.event_type,
            'schema_version', 1,
            'tenant_id', (SELECT slug FROM tenants WHERE id = NEW.tenant_id),
            'partition_key', 'lifecycle:' || NEW.tenant_id::text,
            'produced_at', NEW.occurred_at,
            'payload', jsonb_build_object(
                'policyId', NEW.policy_id,
                'jobId', NEW.job_id,
                'actorId', NEW.actor_id,
                'reason', NEW.reason,
                'evidence', NEW.payload
            )
        ),
        NEW.occurred_at
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER lifecycle_events_enqueue_after_insert
AFTER INSERT ON lifecycle_events
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_lifecycle_event();

GRANT SELECT, INSERT, UPDATE, DELETE ON
    lifecycle_policies,
    lifecycle_legal_holds,
    lifecycle_jobs,
    lifecycle_job_items,
    lifecycle_events
TO amesh_runtime;
GRANT USAGE, SELECT ON SEQUENCE lifecycle_job_items_ordinal_seq TO amesh_runtime;

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES ('operator', 'lifecycle', 'manage', 'ALLOW')
ON CONFLICT DO NOTHING;

DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'lifecycle_policies',
        'lifecycle_legal_holds',
        'lifecycle_jobs',
        'lifecycle_job_items',
        'lifecycle_events'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', table_name);
    END LOOP;
END;
$$;

CREATE POLICY tenant_runtime_isolation ON lifecycle_policies TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'lifecycle_legal_holds',
        'lifecycle_jobs',
        'lifecycle_job_items',
        'lifecycle_events'
    ] LOOP
        EXECUTE format(
            'CREATE POLICY tenant_runtime_isolation ON %I TO amesh_runtime '
            'USING (tenant_id = amesh_current_tenant_id()) '
            'WITH CHECK (tenant_id = amesh_current_tenant_id())',
            table_name
        );
    END LOOP;
END;
$$;

COMMIT;
