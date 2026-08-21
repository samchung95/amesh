BEGIN;

ALTER TABLE task_attempts
    ADD COLUMN evidence jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE task_attempts
    ADD CONSTRAINT task_attempts_evidence_object CHECK (jsonb_typeof(evidence) = 'object');

ALTER TABLE task_attempts DROP CONSTRAINT task_attempts_failure_category_valid;
ALTER TABLE task_attempts
    ADD CONSTRAINT task_attempts_failure_category_valid CHECK (
        failure_category IS NULL OR failure_category IN (
            'RETRYABLE', 'NON_RETRYABLE', 'CANCELLED', 'TIMED_OUT',
            'INFRASTRUCTURE', 'CONFIGURATION', 'USER_CODE', 'PLATFORM'
        )
    ) NOT VALID;
ALTER TABLE task_attempts VALIDATE CONSTRAINT task_attempts_failure_category_valid;

CREATE TABLE task_deferrals (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    task_run_id uuid NOT NULL REFERENCES task_runs(id) ON DELETE CASCADE,
    attempt integer NOT NULL CHECK (attempt > 0),
    resume_token_digest text NOT NULL,
    state text NOT NULL DEFAULT 'WAITING'
        CHECK (state IN ('WAITING', 'COMPLETED', 'EXPIRED')),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    expires_at timestamptz NULL,
    deferred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    resumed_at timestamptz NULL,
    CONSTRAINT task_deferrals_metadata_object CHECK (jsonb_typeof(metadata) = 'object'),
    PRIMARY KEY (tenant_id, task_run_id, attempt)
);

CREATE UNIQUE INDEX task_deferrals_waiting_task_idx
    ON task_deferrals (tenant_id, task_run_id)
    WHERE state = 'WAITING';
CREATE INDEX task_deferrals_expiry_idx
    ON task_deferrals (tenant_id, expires_at)
    WHERE state = 'WAITING' AND expires_at IS NOT NULL;

GRANT SELECT, INSERT, UPDATE, DELETE ON task_deferrals TO amesh_runtime;

ALTER TABLE task_deferrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_deferrals FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON task_deferrals TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
