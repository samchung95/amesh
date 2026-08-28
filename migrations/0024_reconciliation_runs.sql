BEGIN;

CREATE TABLE reconciliation_runs (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    mode text NOT NULL CHECK (mode IN ('DRY_RUN', 'APPLY')),
    target_type text NOT NULL CHECK (
        target_type IN ('TENANT', 'EXECUTION', 'TRIGGER', 'WORKER', 'TIME_RANGE')
    ),
    target_id text NULL,
    since timestamptz NULL,
    until timestamptz NULL,
    stale_after_seconds integer NOT NULL CHECK (stale_after_seconds BETWEEN 30 AND 86400),
    max_findings integer NOT NULL CHECK (max_findings BETWEEN 1 AND 1000),
    max_repairs integer NOT NULL CHECK (max_repairs BETWEEN 0 AND 100),
    repairs_applied integer NOT NULL DEFAULT 0 CHECK (repairs_applied >= 0),
    finding_count integer NOT NULL DEFAULT 0 CHECK (finding_count >= 0),
    unresolved_count integer NOT NULL DEFAULT 0 CHECK (unresolved_count >= 0),
    state text NOT NULL DEFAULT 'RUNNING' CHECK (state IN ('RUNNING', 'COMPLETED', 'FAILED')),
    actor_id text NOT NULL,
    reason text NOT NULL,
    idempotency_key text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    UNIQUE (tenant_id, id),
    UNIQUE (tenant_id, idempotency_key)
);

CREATE TABLE reconciliation_findings (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    run_id uuid NOT NULL,
    invariant_type text NOT NULL CHECK (
        invariant_type IN (
            'EXPIRED_LEASE',
            'ORPHAN_TASK_RUN',
            'STUCK_EXECUTION',
            'MISSING_DISPATCH',
            'UNPROJECTED_EVENT',
            'MISSING_SCHEDULE_PROJECTION'
        )
    ),
    resource_type text NOT NULL,
    resource_id text NOT NULL,
    expected_version bigint NULL CHECK (expected_version IS NULL OR expected_version >= 0),
    disposition text NOT NULL CHECK (
        disposition IN ('DETECTED', 'REPAIRED', 'QUARANTINED')
    ),
    repair_action text NULL,
    detail jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(detail) = 'object'),
    runbook text NOT NULL,
    observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    resolved_at timestamptz NULL,
    FOREIGN KEY (tenant_id, run_id) REFERENCES reconciliation_runs(tenant_id, id),
    UNIQUE (run_id, invariant_type, resource_type, resource_id)
);

CREATE INDEX reconciliation_runs_tenant_timeline_idx
    ON reconciliation_runs (tenant_id, created_at DESC, id DESC);
CREATE INDEX reconciliation_findings_unresolved_idx
    ON reconciliation_findings (tenant_id, invariant_type, observed_at, id)
    WHERE disposition IN ('DETECTED', 'QUARANTINED');

GRANT SELECT, INSERT, UPDATE, DELETE ON reconciliation_runs TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON reconciliation_findings TO amesh_runtime;

ALTER TABLE reconciliation_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reconciliation_runs FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON reconciliation_runs TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE reconciliation_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE reconciliation_findings FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON reconciliation_findings TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
