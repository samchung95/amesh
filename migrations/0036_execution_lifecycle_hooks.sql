BEGIN;

ALTER TABLE executions
    ADD COLUMN lifecycle_evidence jsonb NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE task_runs
    ADD COLUMN lifecycle_phase text NOT NULL DEFAULT 'MAIN',
    ADD CONSTRAINT task_runs_lifecycle_phase_check
        CHECK (lifecycle_phase IN ('MAIN', 'ERROR', 'FINALLY', 'AFTER_EXECUTION'));

CREATE INDEX task_runs_execution_lifecycle_pending_idx
    ON task_runs (tenant_id, execution_id, lifecycle_phase, state)
    WHERE lifecycle_phase <> 'MAIN'
      AND state IN ('WAITING', 'RUNNING', 'RETRY_DELAY');

COMMIT;
