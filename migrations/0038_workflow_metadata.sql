BEGIN;

CREATE TABLE namespace_workflow_metadata (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_id uuid NOT NULL REFERENCES namespaces(id),
    plugin_defaults jsonb NOT NULL DEFAULT '[]'::jsonb,
    policy jsonb NOT NULL DEFAULT '{}'::jsonb,
    resource_version bigint NOT NULL DEFAULT 1 CHECK (resource_version > 0),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, namespace_id),
    CONSTRAINT namespace_workflow_metadata_defaults_array
        CHECK (jsonb_typeof(plugin_defaults) = 'array'),
    CONSTRAINT namespace_workflow_metadata_policy_object
        CHECK (jsonb_typeof(policy) = 'object')
);

ALTER TABLE task_runs
    ADD COLUMN labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD CONSTRAINT task_runs_labels_object CHECK (jsonb_typeof(labels) = 'object');

ALTER TABLE assets
    ADD COLUMN labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD CONSTRAINT assets_labels_object CHECK (jsonb_typeof(labels) = 'object');

CREATE INDEX namespace_workflow_metadata_namespace_idx
    ON namespace_workflow_metadata (tenant_id, namespace_id);
CREATE INDEX flows_labels_gin_idx ON flows USING gin (labels jsonb_path_ops);
CREATE INDEX executions_labels_gin_idx ON executions USING gin (labels jsonb_path_ops);
CREATE INDEX task_runs_labels_gin_idx ON task_runs USING gin (labels jsonb_path_ops);
CREATE INDEX assets_labels_gin_idx ON assets USING gin (labels jsonb_path_ops);
CREATE INDEX backfills_labels_gin_idx ON backfills USING gin (labels jsonb_path_ops);

GRANT SELECT, INSERT, UPDATE, DELETE ON namespace_workflow_metadata TO amesh_runtime;

ALTER TABLE namespace_workflow_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE namespace_workflow_metadata FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON namespace_workflow_metadata TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
