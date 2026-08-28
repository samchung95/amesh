BEGIN;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE search_documents (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    document_type text NOT NULL
        CHECK (document_type IN ('FLOW', 'EXECUTION', 'LOG', 'ASSET', 'AUDIT')),
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
    projection_version integer NOT NULL DEFAULT 1 CHECK (projection_version > 0),
    indexed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(content, '')), 'B')
    ) STORED,
    PRIMARY KEY (tenant_id, document_type, document_id),
    CONSTRAINT search_documents_labels_object CHECK (jsonb_typeof(labels) = 'object'),
    CONSTRAINT search_documents_fields_object CHECK (jsonb_typeof(fields) = 'object')
) PARTITION BY HASH (tenant_id);

CREATE TABLE search_documents_p0 PARTITION OF search_documents
    FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE search_documents_p1 PARTITION OF search_documents
    FOR VALUES WITH (MODULUS 8, REMAINDER 1);
CREATE TABLE search_documents_p2 PARTITION OF search_documents
    FOR VALUES WITH (MODULUS 8, REMAINDER 2);
CREATE TABLE search_documents_p3 PARTITION OF search_documents
    FOR VALUES WITH (MODULUS 8, REMAINDER 3);
CREATE TABLE search_documents_p4 PARTITION OF search_documents
    FOR VALUES WITH (MODULUS 8, REMAINDER 4);
CREATE TABLE search_documents_p5 PARTITION OF search_documents
    FOR VALUES WITH (MODULUS 8, REMAINDER 5);
CREATE TABLE search_documents_p6 PARTITION OF search_documents
    FOR VALUES WITH (MODULUS 8, REMAINDER 6);
CREATE TABLE search_documents_p7 PARTITION OF search_documents
    FOR VALUES WITH (MODULUS 8, REMAINDER 7);

CREATE INDEX search_documents_full_text_idx
    ON search_documents USING gin (search_vector);
CREATE INDEX search_documents_title_trgm_idx
    ON search_documents USING gin (title gin_trgm_ops);
CREATE INDEX search_documents_structured_idx
    ON search_documents (tenant_id, document_type, namespace, state, source_updated_at DESC);
CREATE INDEX search_documents_labels_idx
    ON search_documents USING gin (labels jsonb_path_ops);
CREATE INDEX search_documents_fields_idx
    ON search_documents USING gin (fields jsonb_path_ops);

CREATE TABLE search_projection_state (
    tenant_id uuid PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
    projection_version integer NOT NULL DEFAULT 1 CHECK (projection_version > 0),
    condition text NOT NULL DEFAULT 'READY'
        CHECK (condition IN ('READY', 'REBUILDING', 'DEGRADED')),
    documents_indexed bigint NOT NULL DEFAULT 0 CHECK (documents_indexed >= 0),
    source_documents bigint NOT NULL DEFAULT 0 CHECK (source_documents >= 0),
    last_projected_at timestamptz NULL,
    latest_source_at timestamptz NULL,
    rebuild_started_at timestamptz NULL,
    rebuild_completed_at timestamptz NULL,
    failure_count bigint NOT NULL DEFAULT 0 CHECK (failure_count >= 0),
    last_error text NULL,
    error_at timestamptz NULL,
    resource_version bigint NOT NULL DEFAULT 1 CHECK (resource_version > 0),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE search_projection_events (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_type text NOT NULL,
    actor_id text NOT NULL,
    reason text NULL,
    projection_version integer NOT NULL CHECK (projection_version > 0),
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT search_projection_events_payload_object CHECK (jsonb_typeof(payload) = 'object')
);

CREATE INDEX search_projection_events_history_idx
    ON search_projection_events (tenant_id, occurred_at, event_id);

CREATE OR REPLACE FUNCTION amesh_enqueue_search_projection_event() RETURNS trigger AS $$
DECLARE
    tenant_slug text;
BEGIN
    SELECT slug INTO STRICT tenant_slug FROM tenants WHERE id = NEW.tenant_id;
    INSERT INTO messages_outbox (
        tenant_id, message_id, subject, partition_key, envelope, available_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        'search-projection-events',
        'search:' || NEW.tenant_id::text,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', NEW.event_type,
            'schema_version', 1,
            'tenant_id', tenant_slug,
            'partition_key', 'search:' || NEW.tenant_id::text,
            'produced_at', NEW.occurred_at,
            'payload', jsonb_build_object(
                'projection_version', NEW.projection_version,
                'actor_id', NEW.actor_id,
                'reason', NEW.reason,
                'event', NEW.payload
            )
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER search_projection_event_outbox
AFTER INSERT ON search_projection_events
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_search_projection_event();

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES
    ('flow-author', 'search', 'view', 'ALLOW'),
    ('operator', 'search', 'view', 'ALLOW'),
    ('operator', 'search', 'manage', 'ALLOW')
ON CONFLICT DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE ON search_documents TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON search_projection_state TO amesh_runtime;
GRANT SELECT, INSERT ON search_projection_events TO amesh_runtime;

ALTER TABLE search_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_documents FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON search_documents TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE search_projection_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_projection_state FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON search_projection_state TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE search_projection_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_projection_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON search_projection_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
