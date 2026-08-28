BEGIN;

ALTER TABLE task_runs
    ADD COLUMN retry_at timestamptz NULL;

CREATE INDEX task_runs_retry_ready_idx
    ON task_runs (retry_at, id)
    WHERE state = 'RETRY_DELAY';

COMMIT;
