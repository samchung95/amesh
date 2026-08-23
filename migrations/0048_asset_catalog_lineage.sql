BEGIN;

ALTER TABLE assets
    DROP CONSTRAINT assets_tenant_id_provider_external_key_key,
    ADD COLUMN account text NOT NULL DEFAULT 'default',
    ADD COLUMN location text NOT NULL DEFAULT 'global',
    ADD COLUMN namespace_name text NOT NULL DEFAULT 'default',
    ADD COLUMN description text NOT NULL DEFAULT '',
    ADD COLUMN owner text NULL,
    ADD COLUMN contacts jsonb NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN domain_group text NULL,
    ADD COLUMN tags jsonb NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN health text NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN last_materialization_at timestamptz NULL,
    ADD COLUMN source_kind text NOT NULL DEFAULT 'DECLARED',
    ADD CONSTRAINT assets_identity_unique UNIQUE (
        tenant_id, provider, account, location, asset_type, external_key
    ),
    ADD CONSTRAINT assets_tenant_id_id_unique UNIQUE (tenant_id, id),
    ADD CONSTRAINT assets_contacts_array CHECK (jsonb_typeof(contacts) = 'array'),
    ADD CONSTRAINT assets_tags_array CHECK (jsonb_typeof(tags) = 'array'),
    ADD CONSTRAINT assets_health_check
        CHECK (health IN ('UNKNOWN', 'HEALTHY', 'DEGRADED', 'FAILED')),
    ADD CONSTRAINT assets_source_kind_check
        CHECK (source_kind IN ('DECLARED', 'PLUGIN_EVENT'));

CREATE INDEX assets_namespace_catalog_idx
    ON assets (tenant_id, namespace_name, domain_group, provider, display_name);
CREATE INDEX assets_tags_catalog_idx ON assets USING gin (tags jsonb_path_ops);

ALTER TABLE execution_artifacts
    ADD CONSTRAINT execution_artifacts_tenant_execution_id_unique
    UNIQUE (tenant_id, execution_id, id);

CREATE TABLE asset_observations (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    asset_id uuid NOT NULL,
    namespace_name text NOT NULL,
    access_mode text NOT NULL CHECK (access_mode IN ('READ', 'WRITE')),
    evidence_kind text NOT NULL CHECK (evidence_kind IN ('DECLARED', 'OBSERVED', 'INFERRED')),
    confidence numeric(4, 3) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    flow_key text NULL,
    execution_id uuid NULL,
    task_run_id uuid NULL,
    artifact_id uuid NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    created_by text NOT NULL,
    CONSTRAINT asset_observations_metadata_object CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT asset_observations_asset_fk
        FOREIGN KEY (tenant_id, asset_id) REFERENCES assets(tenant_id, id),
    CONSTRAINT asset_observations_execution_fk
        FOREIGN KEY (tenant_id, execution_id) REFERENCES executions(tenant_id, id),
    CONSTRAINT asset_observations_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs(tenant_id, execution_id, id),
    CONSTRAINT asset_observations_artifact_fk
        FOREIGN KEY (tenant_id, execution_id, artifact_id)
        REFERENCES execution_artifacts(tenant_id, execution_id, id)
);

CREATE INDEX asset_observations_asset_timeline_idx
    ON asset_observations (tenant_id, asset_id, observed_at DESC, id);
CREATE INDEX asset_observations_execution_idx
    ON asset_observations (tenant_id, execution_id, access_mode, observed_at);

CREATE TABLE asset_lineage_edges (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    upstream_asset_id uuid NOT NULL,
    downstream_asset_id uuid NOT NULL,
    evidence_kind text NOT NULL CHECK (evidence_kind IN ('DECLARED', 'OBSERVED', 'INFERRED')),
    confidence numeric(4, 3) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    flow_key text NULL,
    execution_id uuid NULL,
    task_run_id uuid NULL,
    artifact_id uuid NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    created_by text NOT NULL,
    CONSTRAINT asset_lineage_distinct_assets CHECK (upstream_asset_id <> downstream_asset_id),
    CONSTRAINT asset_lineage_metadata_object CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT asset_lineage_upstream_fk
        FOREIGN KEY (tenant_id, upstream_asset_id) REFERENCES assets(tenant_id, id),
    CONSTRAINT asset_lineage_downstream_fk
        FOREIGN KEY (tenant_id, downstream_asset_id) REFERENCES assets(tenant_id, id),
    CONSTRAINT asset_lineage_execution_fk
        FOREIGN KEY (tenant_id, execution_id) REFERENCES executions(tenant_id, id),
    CONSTRAINT asset_lineage_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs(tenant_id, execution_id, id),
    CONSTRAINT asset_lineage_artifact_fk
        FOREIGN KEY (tenant_id, execution_id, artifact_id)
        REFERENCES execution_artifacts(tenant_id, execution_id, id),
    CONSTRAINT asset_lineage_identity_unique UNIQUE NULLS NOT DISTINCT (
        tenant_id, upstream_asset_id, downstream_asset_id, evidence_kind,
        flow_key, execution_id, task_run_id, artifact_id
    )
);

CREATE INDEX asset_lineage_upstream_idx
    ON asset_lineage_edges (tenant_id, upstream_asset_id, observed_at DESC);
CREATE INDEX asset_lineage_downstream_idx
    ON asset_lineage_edges (tenant_id, downstream_asset_id, observed_at DESC);

GRANT SELECT, INSERT, UPDATE, DELETE ON asset_observations, asset_lineage_edges TO amesh_runtime;

ALTER TABLE asset_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_observations FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON asset_observations TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE asset_lineage_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_lineage_edges FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON asset_lineage_edges TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
