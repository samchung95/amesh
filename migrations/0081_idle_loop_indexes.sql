BEGIN;

-- Recovery reads the open executions instead of scanning terminal history every cycle.
CREATE INDEX executions_recovery_open_idx
    ON executions (tenant_id, id)
    WHERE state NOT IN ('CANCELLED', 'SUCCESS', 'FAILED', 'WARNING');

-- Incremental search projection reads recent source changes instead of anti-joining history.
CREATE INDEX executions_tenant_updated_idx ON executions (tenant_id, updated_at);
CREATE INDEX task_runs_tenant_updated_idx ON task_runs (tenant_id, updated_at);
CREATE INDEX execution_logs_tenant_ingested_idx ON execution_logs (tenant_id, ingested_at);
CREATE INDEX execution_metrics_tenant_ingested_idx ON execution_metrics (tenant_id, ingested_at);

-- The scheduler's expired-lease sweep reads in-flight occurrences, not the settled history.
CREATE INDEX trigger_occurrences_processing_lease_idx
    ON trigger_occurrences (tenant_id, lease_expires_at)
    WHERE state = 'PROCESSING';

COMMIT;
