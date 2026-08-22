BEGIN;

ALTER TABLE task_runs
    ADD COLUMN terminal_result jsonb NULL,
    ADD COLUMN control_evidence jsonb NOT NULL DEFAULT '{}'::jsonb;

COMMIT;
