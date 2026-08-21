BEGIN;

CREATE TABLE backfills (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    namespace_name text NOT NULL,
    flow_key text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    state text NOT NULL CHECK (state IN ('RUNNING', 'PAUSED', 'CANCELLED', 'COMPLETED')),
    selection_kind text NOT NULL CHECK (
        selection_kind IN ('TIME_RANGE', 'PARTITIONS', 'OCCURRENCES', 'REPLAY')
    ),
    selection jsonb NOT NULL,
    inputs jsonb NOT NULL DEFAULT '{}'::jsonb,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    max_concurrency integer NOT NULL CHECK (max_concurrency > 0),
    rate_per_minute integer NOT NULL CHECK (rate_per_minute > 0),
    priority integer NOT NULL DEFAULT 0,
    task_count integer NOT NULL CHECK (task_count >= 0),
    total_items integer NOT NULL CHECK (total_items >= 0),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    finished_at timestamptz NULL,
    CONSTRAINT backfills_selection_object CHECK (jsonb_typeof(selection) = 'object'),
    CONSTRAINT backfills_inputs_object CHECK (jsonb_typeof(inputs) = 'object'),
    CONSTRAINT backfills_labels_object CHECK (jsonb_typeof(labels) = 'object'),
    UNIQUE (tenant_id, id)
);

CREATE INDEX backfills_tenant_state_idx
    ON backfills (tenant_id, state, created_at, id);

CREATE TABLE backfill_items (
    item_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    backfill_id uuid NOT NULL,
    occurrence_key text NOT NULL,
    state text NOT NULL DEFAULT 'PENDING'
        CHECK (state IN ('PENDING', 'CREATED', 'CANCELLED')),
    scheduled_for timestamptz NULL,
    partition_key text NULL,
    source_execution_id uuid NULL,
    execution_id uuid NULL,
    launched_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT backfill_items_backfill_fk
        FOREIGN KEY (tenant_id, backfill_id)
        REFERENCES backfills (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT backfill_items_execution_fk
        FOREIGN KEY (tenant_id, execution_id)
        REFERENCES executions (tenant_id, id),
    UNIQUE (tenant_id, backfill_id, occurrence_key),
    UNIQUE (tenant_id, backfill_id, execution_id)
);

CREATE INDEX backfill_items_pending_idx
    ON backfill_items (tenant_id, backfill_id, created_at, item_id)
    WHERE state = 'PENDING';
CREATE INDEX backfill_items_source_idx
    ON backfill_items (tenant_id, source_execution_id)
    WHERE source_execution_id IS NOT NULL;

CREATE TABLE backfill_events (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    backfill_id uuid NOT NULL,
    sequence integer NOT NULL CHECK (sequence > 0),
    event_type text NOT NULL,
    actor_id text NOT NULL,
    reason text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT backfill_events_backfill_fk
        FOREIGN KEY (tenant_id, backfill_id)
        REFERENCES backfills (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT backfill_events_payload_object CHECK (jsonb_typeof(payload) = 'object'),
    UNIQUE (tenant_id, backfill_id, sequence)
);

CREATE OR REPLACE FUNCTION amesh_enqueue_backfill_event() RETURNS trigger AS $$
DECLARE
    tenant_slug text;
BEGIN
    SELECT slug INTO STRICT tenant_slug FROM tenants WHERE id = NEW.tenant_id;
    INSERT INTO messages_outbox (
        tenant_id, message_id, subject, partition_key, envelope, available_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        'backfill-events',
        'backfill:' || NEW.backfill_id::text,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', NEW.event_type,
            'schema_version', 1,
            'tenant_id', tenant_slug,
            'partition_key', 'backfill:' || NEW.backfill_id::text,
            'correlation_id', NEW.backfill_id,
            'causation_id', NULL,
            'produced_at', NEW.occurred_at,
            'payload', jsonb_build_object(
                'backfill_id', NEW.backfill_id,
                'sequence', NEW.sequence,
                'actor_id', NEW.actor_id,
                'reason', NEW.reason,
                'event', NEW.payload
            )
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER backfill_event_outbox
AFTER INSERT ON backfill_events
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_backfill_event();

GRANT SELECT, INSERT, UPDATE, DELETE ON backfills, backfill_items, backfill_events
TO amesh_runtime;

ALTER TABLE backfills ENABLE ROW LEVEL SECURITY;
ALTER TABLE backfills FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON backfills TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE backfill_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE backfill_items FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON backfill_items TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE backfill_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE backfill_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON backfill_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
