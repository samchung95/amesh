BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM workers
        GROUP BY tenant_id, worker_group, instance_name
        HAVING count(*) > 1
    ) THEN
        RAISE EXCEPTION 'duplicate worker identities block migration 0012';
    END IF;
END;
$$;

ALTER TABLE executions
    ADD CONSTRAINT executions_state_valid CHECK (
        state IN (
            'CREATED', 'QUEUED', 'RUNNING', 'PAUSED', 'CANCELLING',
            'CANCELLED', 'SUCCESS', 'FAILED', 'WARNING', 'RESTARTING'
        )
    ) NOT VALID;
ALTER TABLE executions VALIDATE CONSTRAINT executions_state_valid;

ALTER TABLE task_runs
    ADD CONSTRAINT task_runs_state_valid CHECK (
        state IN ('WAITING', 'RUNNING', 'RETRY_DELAY', 'SUCCESS', 'FAILED', 'CANCELLED')
    ) NOT VALID;
ALTER TABLE task_runs VALIDATE CONSTRAINT task_runs_state_valid;

ALTER TABLE task_attempts
    ADD CONSTRAINT task_attempts_state_valid CHECK (
        state IN ('RUNNING', 'SUCCESS', 'FAILED', 'CANCELLED', 'TIMED_OUT')
    ) NOT VALID;
ALTER TABLE task_attempts VALIDATE CONSTRAINT task_attempts_state_valid;

ALTER TABLE workers
    ADD CONSTRAINT workers_status_valid CHECK (
        status IN ('STARTING', 'READY', 'DEGRADED', 'DRAINING', 'STOPPED')
    ) NOT VALID;
ALTER TABLE workers VALIDATE CONSTRAINT workers_status_valid;

CREATE UNIQUE INDEX workers_tenant_identity_unique_idx
    ON workers (tenant_id, worker_group, instance_name);
CREATE UNIQUE INDEX flow_revisions_tenant_identity_idx
    ON flow_revisions (tenant_id, id);
CREATE UNIQUE INDEX executions_tenant_identity_idx
    ON executions (tenant_id, id);
CREATE UNIQUE INDEX task_runs_tenant_execution_identity_idx
    ON task_runs (tenant_id, execution_id, id);

CREATE TABLE trigger_definitions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    flow_revision_id uuid NOT NULL,
    trigger_key text NOT NULL,
    trigger_type text NOT NULL,
    definition jsonb NOT NULL,
    enabled boolean NOT NULL DEFAULT true,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT trigger_definitions_definition_object CHECK (jsonb_typeof(definition) = 'object'),
    CONSTRAINT trigger_definitions_flow_revision_fk
        FOREIGN KEY (tenant_id, flow_revision_id)
        REFERENCES flow_revisions (tenant_id, id),
    UNIQUE (tenant_id, flow_revision_id, trigger_key)
);

INSERT INTO trigger_definitions (
    id,
    tenant_id,
    flow_revision_id,
    trigger_key,
    trigger_type,
    definition,
    created_by,
    created_at
)
SELECT
    gen_random_uuid(),
    flow_revisions.tenant_id,
    flow_revisions.id,
    trigger_definition ->> 'id',
    trigger_definition ->> 'type',
    trigger_definition,
    flow_revisions.created_by,
    flow_revisions.created_at
FROM flow_revisions
CROSS JOIN LATERAL jsonb_array_elements(
    COALESCE(flow_revisions.canonical_definition -> 'triggers', '[]'::jsonb)
) AS trigger_definition
ON CONFLICT (tenant_id, flow_revision_id, trigger_key) DO NOTHING;

CREATE TABLE execution_logs (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    execution_id uuid NOT NULL,
    task_run_id uuid NULL,
    level text NOT NULL CHECK (level IN ('TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR')),
    logger text NOT NULL,
    message text NOT NULL,
    fields jsonb NOT NULL DEFAULT '{}'::jsonb,
    redacted boolean NOT NULL DEFAULT false,
    occurred_at timestamptz NOT NULL,
    CONSTRAINT execution_logs_fields_object CHECK (jsonb_typeof(fields) = 'object'),
    CONSTRAINT execution_logs_execution_fk
        FOREIGN KEY (tenant_id, execution_id)
        REFERENCES executions (tenant_id, id),
    CONSTRAINT execution_logs_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs (tenant_id, execution_id, id)
);

CREATE INDEX execution_logs_timeline_idx
    ON execution_logs (tenant_id, execution_id, occurred_at, id);

CREATE TABLE execution_metrics (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    execution_id uuid NOT NULL,
    task_run_id uuid NULL,
    metric_name text NOT NULL,
    metric_kind text NOT NULL CHECK (metric_kind IN ('COUNTER', 'GAUGE', 'TIMER')),
    metric_value numeric NOT NULL,
    unit text NULL,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL,
    CONSTRAINT execution_metrics_labels_object CHECK (jsonb_typeof(labels) = 'object'),
    CONSTRAINT execution_metrics_execution_fk
        FOREIGN KEY (tenant_id, execution_id)
        REFERENCES executions (tenant_id, id),
    CONSTRAINT execution_metrics_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs (tenant_id, execution_id, id)
);

CREATE INDEX execution_metrics_timeline_idx
    ON execution_metrics (tenant_id, execution_id, occurred_at, id);

CREATE TABLE assets (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    provider text NOT NULL,
    external_key text NOT NULL,
    asset_type text NOT NULL,
    display_name text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    resource_version bigint NOT NULL DEFAULT 1 CHECK (resource_version > 0),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT assets_metadata_object CHECK (jsonb_typeof(metadata) = 'object'),
    UNIQUE (tenant_id, provider, external_key)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON trigger_definitions TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON execution_logs TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON execution_metrics TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON assets TO amesh_runtime;

DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'trigger_definitions',
        'execution_logs',
        'execution_metrics',
        'assets'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', table_name);
        EXECUTE format(
            'CREATE POLICY tenant_runtime_isolation ON %I TO amesh_runtime '
            'USING (tenant_id = amesh_current_tenant_id()) '
            'WITH CHECK (tenant_id = amesh_current_tenant_id())',
            table_name
        );
    END LOOP;
END;
$$;

COMMIT;
