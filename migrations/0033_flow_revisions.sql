BEGIN;

ALTER TABLE flow_revisions
    ADD COLUMN source text NULL,
    ADD COLUMN source_commit text NULL,
    ADD COLUMN environment text NULL,
    ADD COLUMN deployment_metadata jsonb NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE flows
    ADD CONSTRAINT flows_status_check
    CHECK (status IN ('DRAFT', 'ACTIVE', 'DISABLED', 'ARCHIVED'));

CREATE TABLE flow_revision_events (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    flow_id uuid NOT NULL REFERENCES flows(id),
    revision integer NOT NULL CHECK (revision > 0),
    event_type text NOT NULL,
    actor_id text NOT NULL,
    reason text NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX flow_revision_events_history_idx
    ON flow_revision_events (tenant_id, flow_id, occurred_at, event_id);

CREATE OR REPLACE FUNCTION amesh_enqueue_flow_revision_event() RETURNS trigger AS $$
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
        'flow-revision-events',
        'flow:' || NEW.flow_id::text,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', NEW.event_type,
            'schema_version', 1,
            'tenant_id', tenant_slug,
            'partition_key', 'flow:' || NEW.flow_id::text,
            'produced_at', NEW.occurred_at,
            'payload', jsonb_build_object(
                'flow_id', NEW.flow_id,
                'revision', NEW.revision,
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

CREATE TRIGGER flow_revision_event_outbox
AFTER INSERT ON flow_revision_events
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_flow_revision_event();

CREATE OR REPLACE FUNCTION amesh_protect_referenced_flow_revision() RETURNS trigger AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM flows
        WHERE tenant_id = OLD.tenant_id
          AND id = OLD.flow_id
          AND active_revision = OLD.revision
    ) THEN
        RAISE EXCEPTION 'cannot delete the selected flow revision'
            USING ERRCODE = '23503';
    END IF;
    IF EXISTS (
        SELECT 1 FROM executions
        WHERE tenant_id = OLD.tenant_id
          AND flow_revision_id = OLD.id
    ) THEN
        RAISE EXCEPTION 'cannot delete a flow revision referenced by executions'
            USING ERRCODE = '23503';
    END IF;
    IF EXISTS (
        SELECT 1 FROM audit_events
        WHERE tenant_id = OLD.tenant_id
          AND resource_type = 'flow_revision'
          AND resource_id = OLD.id::text
    ) THEN
        RAISE EXCEPTION 'cannot delete a flow revision referenced by audit evidence'
            USING ERRCODE = '23503';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER protect_referenced_flow_revision
BEFORE DELETE ON flow_revisions
FOR EACH ROW EXECUTE FUNCTION amesh_protect_referenced_flow_revision();

GRANT SELECT, INSERT, UPDATE, DELETE ON flow_revision_events TO amesh_runtime;

ALTER TABLE flow_revision_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE flow_revision_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON flow_revision_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
