BEGIN;

ALTER TABLE execution_events
    ADD COLUMN idempotency_key text NULL,
    ADD COLUMN reason text NULL;

UPDATE execution_events
SET idempotency_key = event_id::text
WHERE idempotency_key IS NULL;

ALTER TABLE execution_events
    ALTER COLUMN idempotency_key SET NOT NULL,
    ADD CONSTRAINT execution_events_idempotency_unique
        UNIQUE (tenant_id, execution_id, idempotency_key);

ALTER TABLE commands_inbox
    ADD COLUMN schema_version integer NOT NULL DEFAULT 1,
    ADD CONSTRAINT commands_inbox_schema_version_positive CHECK (schema_version > 0);

CREATE TABLE task_run_events (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    task_run_id uuid NOT NULL REFERENCES task_runs(id),
    execution_id uuid NOT NULL REFERENCES executions(id),
    sequence bigint NOT NULL CHECK (sequence > 0),
    event_id uuid NOT NULL,
    event_type text NOT NULL,
    schema_version integer NOT NULL CHECK (schema_version > 0),
    idempotency_key text NOT NULL,
    correlation_id uuid NOT NULL,
    causation_id uuid NULL,
    actor_id text NOT NULL,
    reason text NULL,
    occurred_at timestamptz NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (tenant_id, task_run_id, sequence),
    UNIQUE (tenant_id, event_id),
    UNIQUE (tenant_id, task_run_id, idempotency_key)
);

CREATE INDEX task_run_events_execution_sequence_idx
    ON task_run_events (tenant_id, execution_id, task_run_id, sequence);

CREATE TABLE transition_rejections (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    rejection_id uuid NOT NULL,
    command_id uuid NOT NULL,
    idempotency_key text NOT NULL,
    schema_version integer NOT NULL CHECK (schema_version > 0),
    aggregate_type text NOT NULL CHECK (aggregate_type IN ('execution', 'task_run')),
    aggregate_id uuid NOT NULL,
    code text NOT NULL CHECK (
        code IN ('ILLEGAL_TRANSITION', 'VERSION_CONFLICT', 'EPOCH_CONFLICT')
    ),
    current_state text NOT NULL,
    current_version bigint NOT NULL CHECK (current_version >= 0),
    current_epoch bigint NULL CHECK (current_epoch IS NULL OR current_epoch > 0),
    actor_id text NOT NULL,
    reason text NOT NULL,
    correlation_id uuid NOT NULL,
    causation_id uuid NULL,
    occurred_at timestamptz NOT NULL,
    PRIMARY KEY (tenant_id, rejection_id),
    UNIQUE (tenant_id, aggregate_type, aggregate_id, idempotency_key)
);

CREATE INDEX transition_rejections_aggregate_time_idx
    ON transition_rejections (tenant_id, aggregate_type, aggregate_id, occurred_at DESC);

CREATE OR REPLACE FUNCTION amesh_enqueue_execution_event() RETURNS trigger AS $$
DECLARE
    tenant_slug text;
BEGIN
    SELECT slug INTO STRICT tenant_slug FROM tenants WHERE id = NEW.tenant_id;
    INSERT INTO messages_outbox (
        tenant_id,
        message_id,
        subject,
        partition_key,
        envelope,
        available_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        'execution-events',
        'execution:' || NEW.execution_id::text,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', NEW.event_type,
            'schema_version', NEW.schema_version,
            'tenant_id', tenant_slug,
            'partition_key', 'execution:' || NEW.execution_id::text,
            'correlation_id', NEW.correlation_id,
            'causation_id', NEW.causation_id,
            'produced_at', NEW.occurred_at,
            'payload', jsonb_build_object(
                'execution_id', NEW.execution_id,
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

CREATE OR REPLACE FUNCTION amesh_enqueue_task_run_event() RETURNS trigger AS $$
DECLARE
    tenant_slug text;
BEGIN
    SELECT slug INTO STRICT tenant_slug FROM tenants WHERE id = NEW.tenant_id;
    INSERT INTO messages_outbox (
        tenant_id,
        message_id,
        subject,
        partition_key,
        envelope,
        available_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        'task-run-events',
        'execution:' || NEW.execution_id::text,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', NEW.event_type,
            'schema_version', NEW.schema_version,
            'tenant_id', tenant_slug,
            'partition_key', 'execution:' || NEW.execution_id::text,
            'correlation_id', NEW.correlation_id,
            'causation_id', NEW.causation_id,
            'produced_at', NEW.occurred_at,
            'payload', jsonb_build_object(
                'execution_id', NEW.execution_id,
                'task_run_id', NEW.task_run_id,
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

CREATE TRIGGER execution_event_outbox
AFTER INSERT ON execution_events
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_execution_event();

CREATE TRIGGER task_run_event_outbox
AFTER INSERT ON task_run_events
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_task_run_event();

GRANT SELECT, INSERT, UPDATE, DELETE ON task_run_events TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON transition_rejections TO amesh_runtime;

ALTER TABLE task_run_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_run_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON task_run_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE transition_rejections ENABLE ROW LEVEL SECURITY;
ALTER TABLE transition_rejections FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON transition_rejections TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
