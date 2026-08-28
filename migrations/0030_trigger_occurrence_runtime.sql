BEGIN;

CREATE TABLE trigger_runtime_states (
    trigger_definition_id uuid PRIMARY KEY REFERENCES trigger_definitions(id),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    flow_key text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    trigger_key text NOT NULL,
    trigger_type text NOT NULL,
    active boolean NOT NULL DEFAULT false,
    paused boolean NOT NULL DEFAULT false,
    checkpoint jsonb NOT NULL DEFAULT '{}'::jsonb,
    cursor text NULL,
    last_evaluated_at timestamptz NULL,
    next_evaluation_at timestamptz NULL,
    last_occurrence_at timestamptz NULL,
    last_success_at timestamptz NULL,
    lag_seconds double precision NOT NULL DEFAULT 0 CHECK (lag_seconds >= 0),
    consecutive_failures integer NOT NULL DEFAULT 0 CHECK (consecutive_failures >= 0),
    last_error text NULL,
    last_decision text NOT NULL DEFAULT 'trigger revision materialized',
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT trigger_runtime_checkpoint_object CHECK (jsonb_typeof(checkpoint) = 'object'),
    UNIQUE (tenant_id, namespace_name, flow_key, flow_revision, trigger_key)
);

CREATE TABLE trigger_occurrences (
    occurrence_id uuid NOT NULL,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    trigger_definition_id uuid NOT NULL REFERENCES trigger_runtime_states(trigger_definition_id),
    namespace_name text NOT NULL,
    flow_key text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    trigger_key text NOT NULL,
    trigger_type text NOT NULL,
    occurrence_key text NOT NULL,
    state text NOT NULL CHECK (
        state IN (
            'ACCEPTED', 'DEFERRED', 'PROCESSING', 'RETRY_WAIT',
            'SUCCEEDED', 'DEAD_LETTERED'
        )
    ),
    attempt integer NOT NULL DEFAULT 0 CHECK (attempt >= 0),
    max_attempts integer NOT NULL CHECK (max_attempts > 0),
    available_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
    execution_id uuid NULL,
    replay_of uuid NULL,
    owner_id uuid NULL,
    fencing_token bigint NOT NULL DEFAULT 0 CHECK (fencing_token >= 0),
    lease_expires_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    PRIMARY KEY (tenant_id, occurrence_id),
    UNIQUE (tenant_id, trigger_definition_id, occurrence_key),
    CONSTRAINT trigger_occurrence_payload_object CHECK (jsonb_typeof(payload) = 'object'),
    CONSTRAINT trigger_occurrence_metadata_object CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT trigger_occurrence_evidence_object CHECK (jsonb_typeof(evidence) = 'object'),
    CONSTRAINT trigger_occurrence_owner_lease_pair CHECK (
        (owner_id IS NULL AND lease_expires_at IS NULL)
        OR (owner_id IS NOT NULL AND lease_expires_at IS NOT NULL)
    ),
    CONSTRAINT trigger_occurrence_execution_fk
        FOREIGN KEY (tenant_id, execution_id) REFERENCES executions (tenant_id, id),
    CONSTRAINT trigger_occurrence_replay_fk
        FOREIGN KEY (tenant_id, replay_of)
        REFERENCES trigger_occurrences (tenant_id, occurrence_id)
);

CREATE TABLE trigger_occurrence_events (
    sequence bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    event_id uuid NOT NULL,
    occurrence_id uuid NOT NULL,
    event_type text NOT NULL CHECK (
        event_type IN (
            'ACCEPTED', 'DEFERRED', 'CLAIMED', 'RETRY_SCHEDULED',
            'SUCCEEDED', 'DEAD_LETTERED', 'REPLAYED'
        )
    ),
    reason text NOT NULL,
    actor_id text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (tenant_id, event_id),
    CONSTRAINT trigger_occurrence_event_payload_object CHECK (jsonb_typeof(payload) = 'object'),
    CONSTRAINT trigger_occurrence_event_occurrence_fk
        FOREIGN KEY (tenant_id, occurrence_id)
        REFERENCES trigger_occurrences (tenant_id, occurrence_id)
);

CREATE INDEX trigger_runtime_states_active_idx
    ON trigger_runtime_states (tenant_id, active, namespace_name, flow_key, trigger_key);
CREATE INDEX trigger_runtime_states_next_evaluation_idx
    ON trigger_runtime_states (tenant_id, next_evaluation_at, trigger_definition_id)
    WHERE active AND NOT paused;
CREATE INDEX trigger_occurrences_due_idx
    ON trigger_occurrences (tenant_id, available_at, created_at, occurrence_id)
    WHERE state IN ('ACCEPTED', 'DEFERRED', 'RETRY_WAIT');
CREATE INDEX trigger_occurrences_resource_idx
    ON trigger_occurrences (
        tenant_id, namespace_name, flow_key, trigger_key, created_at DESC
    );
CREATE INDEX trigger_occurrences_execution_idx
    ON trigger_occurrences (tenant_id, execution_id)
    WHERE execution_id IS NOT NULL;

INSERT INTO trigger_runtime_states (
    trigger_definition_id, tenant_id, namespace_name, flow_key, flow_revision,
    trigger_key, trigger_type, active, paused
)
SELECT
    triggers.id,
    triggers.tenant_id,
    namespaces.name,
    flows.flow_key,
    revisions.revision,
    triggers.trigger_key,
    triggers.trigger_type,
    revisions.revision = flows.active_revision
        AND triggers.enabled
        AND NOT COALESCE((revisions.canonical_definition ->> 'disabled')::boolean, false),
    COALESCE((triggers.definition ->> 'paused')::boolean, false)
FROM trigger_definitions AS triggers
JOIN flow_revisions AS revisions ON revisions.id = triggers.flow_revision_id
JOIN flows ON flows.id = revisions.flow_id
JOIN namespaces ON namespaces.id = flows.namespace_id
ON CONFLICT (trigger_definition_id) DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE ON trigger_runtime_states TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON trigger_occurrences TO amesh_runtime;
GRANT SELECT, INSERT ON trigger_occurrence_events TO amesh_runtime;
GRANT USAGE, SELECT ON SEQUENCE trigger_occurrence_events_sequence_seq TO amesh_runtime;

ALTER TABLE trigger_runtime_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE trigger_runtime_states FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON trigger_runtime_states TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE trigger_occurrences ENABLE ROW LEVEL SECURITY;
ALTER TABLE trigger_occurrences FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON trigger_occurrences TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE trigger_occurrence_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE trigger_occurrence_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON trigger_occurrence_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
