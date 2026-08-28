BEGIN;

CREATE TABLE execution_subflows (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    parent_execution_id uuid NOT NULL,
    parent_task_run_id uuid NOT NULL,
    parent_attempt integer NOT NULL CHECK (parent_attempt > 0),
    child_execution_id uuid NOT NULL,
    invocation_key text NOT NULL,
    mode text NOT NULL CHECK (mode IN ('SYNC', 'ASYNC', 'DETACHED')),
    depth integer NOT NULL CHECK (depth > 0),
    target_revision integer NOT NULL CHECK (target_revision > 0),
    propagation jsonb NOT NULL DEFAULT '{}'::jsonb,
    output_mapping jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT execution_subflows_propagation_object CHECK (
        jsonb_typeof(propagation) = 'object'
    ),
    CONSTRAINT execution_subflows_output_mapping_object CHECK (
        jsonb_typeof(output_mapping) = 'object'
    ),
    CONSTRAINT execution_subflows_parent_execution_fk
        FOREIGN KEY (tenant_id, parent_execution_id)
        REFERENCES executions (tenant_id, id),
    CONSTRAINT execution_subflows_parent_task_fk
        FOREIGN KEY (tenant_id, parent_execution_id, parent_task_run_id)
        REFERENCES task_runs (tenant_id, execution_id, id),
    CONSTRAINT execution_subflows_child_execution_fk
        FOREIGN KEY (tenant_id, child_execution_id)
        REFERENCES executions (tenant_id, id),
    UNIQUE (tenant_id, invocation_key),
    UNIQUE (tenant_id, child_execution_id)
);

CREATE INDEX execution_subflows_parent_idx
    ON execution_subflows (tenant_id, parent_execution_id, created_at, id);
CREATE INDEX execution_subflows_child_idx
    ON execution_subflows (tenant_id, child_execution_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON execution_subflows TO amesh_runtime;

ALTER TABLE execution_subflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_subflows FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON execution_subflows TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
