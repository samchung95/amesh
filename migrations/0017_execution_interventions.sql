BEGIN;

ALTER TABLE executions
    ADD COLUMN timeout_at timestamptz NULL,
    ADD COLUMN cancel_deadline_at timestamptz NULL,
    ADD CONSTRAINT executions_timeout_after_creation CHECK (
        timeout_at IS NULL OR timeout_at > created_at
    ),
    ADD CONSTRAINT executions_cancel_deadline_state CHECK (
        cancel_deadline_at IS NULL OR state = 'CANCELLING'
    );

ALTER TABLE task_attempts
    ADD COLUMN cancellation_requested_at timestamptz NULL,
    ADD COLUMN failure_category text NULL,
    ADD CONSTRAINT task_attempts_failure_category_valid CHECK (
        failure_category IS NULL OR failure_category IN (
            'RETRYABLE',
            'NON_RETRYABLE',
            'CANCELLED',
            'TIMED_OUT',
            'INFRASTRUCTURE'
        )
    );

CREATE INDEX executions_due_timeout_idx
    ON executions (timeout_at, id)
    WHERE state IN ('RUNNING', 'PAUSED') AND timeout_at IS NOT NULL;

CREATE INDEX executions_cancel_deadline_idx
    ON executions (cancel_deadline_at, id)
    WHERE state = 'CANCELLING' AND cancel_deadline_at IS NOT NULL;

COMMIT;
