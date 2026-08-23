BEGIN;

CREATE TABLE search_documents_v2 (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    projection_version integer NOT NULL CHECK (projection_version > 0),
    document_type text NOT NULL
        CHECK (document_type IN (
            'FLOW', 'EXECUTION', 'TASK_RUN', 'LOG', 'METRIC', 'ASSET', 'AUDIT'
        )),
    document_id text NOT NULL,
    namespace text NULL,
    title text NOT NULL,
    content text NOT NULL DEFAULT '',
    state text NULL,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    fields jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL,
    source_updated_at timestamptz NOT NULL,
    source_version bigint NOT NULL DEFAULT 0 CHECK (source_version >= 0),
    indexed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(content, '')), 'B')
    ) STORED,
    PRIMARY KEY (tenant_id, projection_version, document_type, document_id),
    CONSTRAINT search_documents_v2_labels_object CHECK (jsonb_typeof(labels) = 'object'),
    CONSTRAINT search_documents_v2_fields_object CHECK (jsonb_typeof(fields) = 'object')
) PARTITION BY HASH (tenant_id);

CREATE TABLE search_documents_v2_p0 PARTITION OF search_documents_v2
    FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE search_documents_v2_p1 PARTITION OF search_documents_v2
    FOR VALUES WITH (MODULUS 8, REMAINDER 1);
CREATE TABLE search_documents_v2_p2 PARTITION OF search_documents_v2
    FOR VALUES WITH (MODULUS 8, REMAINDER 2);
CREATE TABLE search_documents_v2_p3 PARTITION OF search_documents_v2
    FOR VALUES WITH (MODULUS 8, REMAINDER 3);
CREATE TABLE search_documents_v2_p4 PARTITION OF search_documents_v2
    FOR VALUES WITH (MODULUS 8, REMAINDER 4);
CREATE TABLE search_documents_v2_p5 PARTITION OF search_documents_v2
    FOR VALUES WITH (MODULUS 8, REMAINDER 5);
CREATE TABLE search_documents_v2_p6 PARTITION OF search_documents_v2
    FOR VALUES WITH (MODULUS 8, REMAINDER 6);
CREATE TABLE search_documents_v2_p7 PARTITION OF search_documents_v2
    FOR VALUES WITH (MODULUS 8, REMAINDER 7);

CREATE INDEX search_documents_v2_full_text_idx
    ON search_documents_v2 USING gin (search_vector);
CREATE INDEX search_documents_v2_title_trgm_idx
    ON search_documents_v2 USING gin (title gin_trgm_ops);
CREATE INDEX search_documents_v2_structured_idx
    ON search_documents_v2 (
        tenant_id, projection_version, document_type, namespace, state, source_updated_at DESC
    );
CREATE INDEX search_documents_v2_labels_idx
    ON search_documents_v2 USING gin (labels jsonb_path_ops);
CREATE INDEX search_documents_v2_fields_idx
    ON search_documents_v2 USING gin (fields jsonb_path_ops);

ALTER TABLE search_projection_state
    ADD COLUMN schema_version integer NOT NULL DEFAULT 2 CHECK (schema_version > 0),
    ADD COLUMN rebuild_version integer NULL CHECK (rebuild_version > 0),
    ADD COLUMN rebuild_types text[] NULL,
    ADD COLUMN rebuild_from timestamptz NULL,
    ADD COLUMN rebuild_to timestamptz NULL,
    ADD COLUMN enabled boolean NOT NULL DEFAULT true,
    ADD COLUMN checkpoints_verified boolean NOT NULL DEFAULT false,
    ADD COLUMN active_checksum text NULL;

ALTER TABLE search_projection_state
    DROP CONSTRAINT search_projection_state_condition_check,
    ADD CONSTRAINT search_projection_state_condition_check
        CHECK (condition IN ('READY', 'REBUILDING', 'DEGRADED', 'DISABLED')),
    ADD CONSTRAINT search_projection_state_rebuild_window_check
        CHECK (rebuild_from IS NULL OR rebuild_to IS NULL OR rebuild_from <= rebuild_to),
    ADD CONSTRAINT search_projection_state_rebuild_types_check
        CHECK (
            rebuild_types IS NULL OR rebuild_types <@ ARRAY[
                'FLOW', 'EXECUTION', 'TASK_RUN', 'LOG', 'METRIC', 'ASSET', 'AUDIT'
            ]::text[]
        );

INSERT INTO search_documents_v2 (
    tenant_id, projection_version, document_type, document_id, namespace, title, content,
    state, labels, fields, occurred_at, source_updated_at, source_version, indexed_at
)
SELECT documents.tenant_id,
       COALESCE(state.projection_version, documents.projection_version),
       documents.document_type, documents.document_id, documents.namespace, documents.title,
       documents.content, documents.state, documents.labels, documents.fields,
       documents.occurred_at, documents.source_updated_at, documents.source_version,
       documents.indexed_at
FROM search_documents AS documents
LEFT JOIN search_projection_state AS state ON state.tenant_id = documents.tenant_id
ON CONFLICT DO NOTHING;

CREATE TABLE search_projection_checkpoints (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    projection_version integer NOT NULL CHECK (projection_version > 0),
    document_type text NOT NULL
        CHECK (document_type IN (
            'FLOW', 'EXECUTION', 'TASK_RUN', 'LOG', 'METRIC', 'ASSET', 'AUDIT'
        )),
    source_count bigint NOT NULL CHECK (source_count >= 0),
    projected_count bigint NOT NULL CHECK (projected_count >= 0),
    source_checksum text NOT NULL,
    projected_checksum text NOT NULL,
    last_position jsonb NOT NULL DEFAULT '{}'::jsonb,
    verified boolean NOT NULL,
    verified_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, projection_version, document_type),
    CONSTRAINT search_projection_checkpoints_position_object
        CHECK (jsonb_typeof(last_position) = 'object')
);

CREATE TABLE search_projection_archives (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    projection_version integer NOT NULL CHECK (projection_version > 0),
    document_type text NOT NULL,
    document_id text NOT NULL,
    namespace text NULL,
    title text NOT NULL,
    content text NOT NULL,
    state text NULL,
    labels jsonb NOT NULL,
    fields jsonb NOT NULL,
    occurred_at timestamptz NOT NULL,
    source_updated_at timestamptz NOT NULL,
    source_version bigint NOT NULL,
    source_policy text NOT NULL,
    archived_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    purge_at timestamptz NOT NULL,
    PRIMARY KEY (tenant_id, projection_version, document_type, document_id)
);

CREATE INDEX search_projection_archives_expiry_idx
    ON search_projection_archives (tenant_id, purge_at, document_type);

CREATE TABLE search_projection_daily_rollups (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    projection_version integer NOT NULL CHECK (projection_version > 0),
    document_type text NOT NULL,
    bucket_date date NOT NULL,
    document_count bigint NOT NULL CHECK (document_count >= 0),
    checksum text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, projection_version, document_type, bucket_date)
);

CREATE MATERIALIZED VIEW search_projection_daily_rollup_v2 AS
SELECT tenant_id,
       projection_version,
       document_type,
       date_trunc('day', occurred_at)::date AS bucket_date,
       count(*)::bigint AS document_count
FROM search_documents_v2
GROUP BY tenant_id, projection_version, document_type, date_trunc('day', occurred_at)::date
WITH NO DATA;

CREATE UNIQUE INDEX search_projection_daily_rollup_v2_identity_idx
    ON search_projection_daily_rollup_v2 (
        tenant_id, projection_version, document_type, bucket_date
    );

CREATE TABLE search_projection_components (
    schema_version integer NOT NULL CHECK (schema_version > 0),
    component_kind text NOT NULL
        CHECK (component_kind IN ('SCHEMA', 'TABLE', 'INDEX', 'MATERIALIZED_VIEW', 'ROLLUP')),
    component_name text NOT NULL,
    definition_checksum text NOT NULL,
    activated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (schema_version, component_kind, component_name)
);

INSERT INTO search_projection_components (
    schema_version, component_kind, component_name, definition_checksum
) VALUES
    (2, 'SCHEMA', 'search-projection-v2', md5('generational-blue-green-projection-v2')),
    (2, 'TABLE', 'search_documents_v2', md5('tenant-generation-type-document')),
    (2, 'INDEX', 'search_documents_v2_full_text_idx', md5('weighted-simple-tsvector-v2')),
    (2, 'MATERIALIZED_VIEW', 'search_projection_daily_rollup_v2', md5('daily-count-v2')),
    (2, 'ROLLUP', 'search_projection_daily_rollups', md5('tenant-generation-type-day-v2'));

GRANT SELECT, INSERT, UPDATE, DELETE ON search_documents_v2 TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON search_projection_checkpoints TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON search_projection_archives TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON search_projection_daily_rollups TO amesh_runtime;
GRANT SELECT ON search_projection_components TO amesh_runtime;

ALTER TABLE search_documents_v2 ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_documents_v2 FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON search_documents_v2 TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE search_projection_checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_projection_checkpoints FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON search_projection_checkpoints TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE search_projection_archives ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_projection_archives FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON search_projection_archives TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE search_projection_daily_rollups ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_projection_daily_rollups FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON search_projection_daily_rollups TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
