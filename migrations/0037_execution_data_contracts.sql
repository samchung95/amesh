BEGIN;

ALTER TABLE executions
    ADD COLUMN outputs jsonb NOT NULL DEFAULT '{}'::jsonb;

COMMIT;
