BEGIN;

CREATE OR REPLACE FUNCTION amesh_enqueue_task_run_event() RETURNS trigger AS $$
DECLARE
    tenant_slug text;
    outbox_subject text;
    envelope_type text;
BEGIN
    SELECT slug INTO STRICT tenant_slug FROM tenants WHERE id = NEW.tenant_id;
    IF NEW.event_type = 'TaskRunStarted'
       AND COALESCE((NEW.payload ->> 'dispatch')::boolean, true) THEN
        outbox_subject := 'task-dispatch';
        envelope_type := 'DispatchTaskRun';
    ELSE
        outbox_subject := 'task-run-events';
        envelope_type := NEW.event_type;
    END IF;
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
        outbox_subject,
        'execution:' || NEW.execution_id::text,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', envelope_type,
            'schema_version', NEW.schema_version,
            'tenant_id', tenant_slug,
            'partition_key', 'execution:' || NEW.execution_id::text,
            'correlation_id', NEW.correlation_id,
            'causation_id', NEW.causation_id,
            'produced_at', NEW.occurred_at,
            'trace_context', '{}'::jsonb,
            'payload', jsonb_build_object(
                'execution_id', NEW.execution_id,
                'task_run_id', NEW.task_run_id,
                'sequence', NEW.sequence,
                'actor_id', NEW.actor_id,
                'reason', NEW.reason,
                'event_type', NEW.event_type,
                'event', NEW.payload
            )
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMIT;
