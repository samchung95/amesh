BEGIN;

CREATE OR REPLACE FUNCTION amesh_capture_execution_state_evidence() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO execution_evidence_events (
        tenant_id, event_id, execution_id, task_run_id, kind,
        event_type, payload, occurred_at
    ) VALUES (
        NEW.tenant_id, NEW.event_id, NEW.execution_id, NULL, 'STATE',
        'execution.' || lower(NEW.event_type),
        jsonb_build_object(
            'entity', 'execution',
            'eventType', NEW.event_type,
            'sequence', NEW.sequence,
            'actorId', NEW.actor_id,
            'causationId', NEW.causation_id,
            'correlationId', NEW.correlation_id,
            'reason', NEW.reason,
            'payload', NEW.payload
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, event_id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION amesh_capture_task_state_evidence() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO execution_evidence_events (
        tenant_id, event_id, execution_id, task_run_id, kind,
        event_type, payload, occurred_at
    ) VALUES (
        NEW.tenant_id, NEW.event_id, NEW.execution_id, NEW.task_run_id, 'STATE',
        'task.' || lower(NEW.event_type),
        jsonb_build_object(
            'entity', 'task',
            'eventType', NEW.event_type,
            'sequence', NEW.sequence,
            'actorId', NEW.actor_id,
            'causationId', NEW.causation_id,
            'correlationId', NEW.correlation_id,
            'reason', NEW.reason,
            'payload', NEW.payload
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, event_id) DO NOTHING;
    RETURN NEW;
END;
$$;

COMMIT;
