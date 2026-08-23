BEGIN;

ALTER TABLE execution_events
    ADD COLUMN trace_context jsonb NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE task_run_events
    ADD COLUMN trace_context jsonb NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE execution_events
    ADD CONSTRAINT execution_events_trace_context_object
    CHECK (jsonb_typeof(trace_context) = 'object');

ALTER TABLE task_run_events
    ADD CONSTRAINT task_run_events_trace_context_object
    CHECK (jsonb_typeof(trace_context) = 'object');

CREATE FUNCTION amesh_apply_trace_context()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog, public
AS $$
DECLARE
    configured text;
BEGIN
    IF NEW.trace_context <> '{}'::jsonb THEN
        RETURN NEW;
    END IF;
    configured := current_setting('amesh.trace_context', true);
    IF configured IS NULL OR configured = '' THEN
        RETURN NEW;
    END IF;
    BEGIN
        NEW.trace_context := configured::jsonb;
    EXCEPTION WHEN invalid_text_representation THEN
        NEW.trace_context := '{}'::jsonb;
    END;
    RETURN NEW;
END;
$$;

CREATE TRIGGER execution_events_trace_context
BEFORE INSERT ON execution_events
FOR EACH ROW
EXECUTE FUNCTION amesh_apply_trace_context();

CREATE TRIGGER task_run_events_trace_context
BEFORE INSERT ON task_run_events
FOR EACH ROW
EXECUTE FUNCTION amesh_apply_trace_context();

COMMENT ON COLUMN execution_events.trace_context IS
    'Redacted W3C propagation carrier captured from the tenant transaction.';
COMMENT ON COLUMN task_run_events.trace_context IS
    'Redacted W3C propagation carrier captured from the tenant transaction.';

COMMIT;
