BEGIN;

ALTER TABLE executions
    ADD COLUMN trigger_context jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD CONSTRAINT executions_trigger_context_object
        CHECK (jsonb_typeof(trigger_context) = 'object');

COMMIT;
