BEGIN;

CREATE TABLE dashboard_definitions (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    dashboard_id text NOT NULL CHECK (dashboard_id ~ '^[a-z][a-z0-9_.-]{0,127}$'),
    title text NOT NULL CHECK (title <> ''),
    description text NOT NULL DEFAULT '',
    visibility text NOT NULL CHECK (visibility IN ('PRIVATE', 'TENANT')),
    owner_id text NOT NULL,
    viewer_ids jsonb NOT NULL DEFAULT '[]'::jsonb,
    editor_ids jsonb NOT NULL DEFAULT '[]'::jsonb,
    definition jsonb NOT NULL,
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    source text NOT NULL CHECK (source IN ('API', 'GITOPS')),
    deleted boolean NOT NULL DEFAULT false,
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, dashboard_id),
    CONSTRAINT dashboard_viewers_array CHECK (jsonb_typeof(viewer_ids) = 'array'),
    CONSTRAINT dashboard_editors_array CHECK (jsonb_typeof(editor_ids) = 'array'),
    CONSTRAINT dashboard_definition_object CHECK (jsonb_typeof(definition) = 'object')
);

CREATE TABLE dashboard_definition_events (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    dashboard_id text NOT NULL,
    version bigint NOT NULL CHECK (version > 0),
    event_type text NOT NULL CHECK (
        event_type IN ('DashboardCreated', 'DashboardUpdated', 'DashboardDeleted')
    ),
    actor_id text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT dashboard_event_payload_object CHECK (jsonb_typeof(payload) = 'object')
);

CREATE INDEX dashboard_definitions_list_idx
    ON dashboard_definitions (tenant_id, deleted, title, dashboard_id);
CREATE INDEX dashboard_definition_events_history_idx
    ON dashboard_definition_events (tenant_id, dashboard_id, occurred_at, event_id);

CREATE OR REPLACE FUNCTION amesh_enqueue_dashboard_event() RETURNS trigger AS $$
DECLARE
    tenant_slug text;
BEGIN
    SELECT slug INTO STRICT tenant_slug FROM tenants WHERE id = NEW.tenant_id;
    INSERT INTO messages_outbox (
        tenant_id, message_id, subject, partition_key, envelope, available_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        'dashboard-definition-events',
        'dashboard:' || NEW.dashboard_id,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', NEW.event_type,
            'schema_version', 1,
            'tenant_id', tenant_slug,
            'partition_key', 'dashboard:' || NEW.dashboard_id,
            'produced_at', NEW.occurred_at,
            'payload', jsonb_build_object(
                'dashboard_id', NEW.dashboard_id,
                'version', NEW.version,
                'actor_id', NEW.actor_id,
                'definition', NEW.payload
            )
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER dashboard_definition_event_outbox
AFTER INSERT ON dashboard_definition_events
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_dashboard_event();

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES
    ('operator', 'dashboard', 'view', 'ALLOW'),
    ('operator', 'dashboard', 'create', 'ALLOW'),
    ('operator', 'dashboard', 'update', 'ALLOW'),
    ('operator', 'dashboard', 'delete', 'ALLOW'),
    ('flow-author', 'dashboard', 'view', 'ALLOW'),
    ('flow-author', 'dashboard', 'create', 'ALLOW'),
    ('flow-author', 'dashboard', 'update', 'ALLOW'),
    ('flow-author', 'dashboard', 'delete', 'ALLOW')
ON CONFLICT DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE ON dashboard_definitions TO amesh_runtime;
GRANT SELECT, INSERT ON dashboard_definition_events TO amesh_runtime;

ALTER TABLE dashboard_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboard_definitions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON dashboard_definitions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE dashboard_definition_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboard_definition_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON dashboard_definition_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
