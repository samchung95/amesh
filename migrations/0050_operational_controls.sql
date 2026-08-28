BEGIN;

CREATE TABLE announcements (
    announcement_id uuid PRIMARY KEY,
    tenant_id uuid NULL REFERENCES tenants(id),
    title text NOT NULL CHECK (title <> ''),
    message text NOT NULL CHECK (message <> ''),
    severity text NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL')),
    audience text NOT NULL CHECK (audience IN ('INSTANCE', 'TENANT', 'NAMESPACE')),
    namespace_name text NULL,
    starts_at timestamptz NOT NULL,
    expires_at timestamptz NOT NULL,
    active boolean NOT NULL DEFAULT true,
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT announcements_window CHECK (expires_at > starts_at),
    CONSTRAINT announcements_audience_target CHECK (
        (audience = 'INSTANCE' AND tenant_id IS NULL AND namespace_name IS NULL)
        OR (audience = 'TENANT' AND tenant_id IS NOT NULL AND namespace_name IS NULL)
        OR (audience = 'NAMESPACE' AND tenant_id IS NOT NULL AND namespace_name IS NOT NULL)
    )
);

CREATE INDEX announcements_visibility_idx
    ON announcements (active, starts_at, expires_at, severity);
CREATE INDEX announcements_tenant_idx
    ON announcements (tenant_id, namespace_name, updated_at DESC);

CREATE TABLE operational_controls (
    control_id uuid PRIMARY KEY,
    tenant_id uuid NULL REFERENCES tenants(id),
    kind text NOT NULL CHECK (kind IN ('MAINTENANCE', 'KILL_SWITCH')),
    control_name text NOT NULL CHECK (control_name <> ''),
    scope text NOT NULL CHECK (
        scope IN ('INSTANCE', 'TENANT', 'NAMESPACE', 'FLOW', 'PLUGIN', 'RUNNER')
    ),
    namespace_name text NULL,
    flow_id text NULL,
    plugin_id text NULL,
    runner_id text NULL,
    boundaries text[] NOT NULL CHECK (
        cardinality(boundaries) > 0
        AND boundaries <@ ARRAY[
            'AUTHORING', 'NEW_EXECUTIONS', 'TRIGGERS', 'API_WRITES', 'WORKER_DISPATCH'
        ]::text[]
    ),
    running_work_policy text NOT NULL CHECK (
        running_work_policy IN ('CONTINUE', 'DRAIN', 'CANCEL')
    ),
    reason text NOT NULL CHECK (length(reason) >= 3),
    state text NOT NULL DEFAULT 'ACTIVE'
        CHECK (state IN ('ACTIVE', 'DEACTIVATED', 'EXPIRED')),
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    expires_at timestamptz NULL,
    review_at timestamptz NULL,
    bypass_until timestamptz NULL,
    bypass_reason text NULL,
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT operational_controls_review CHECK (
        expires_at IS NOT NULL OR review_at IS NOT NULL
    ),
    CONSTRAINT operational_controls_scope_target CHECK (
        (scope = 'INSTANCE' AND tenant_id IS NULL
            AND namespace_name IS NULL AND flow_id IS NULL
            AND plugin_id IS NULL AND runner_id IS NULL)
        OR (scope = 'TENANT' AND tenant_id IS NOT NULL
            AND namespace_name IS NULL AND flow_id IS NULL
            AND plugin_id IS NULL AND runner_id IS NULL)
        OR (scope = 'NAMESPACE' AND tenant_id IS NOT NULL
            AND namespace_name IS NOT NULL AND flow_id IS NULL
            AND plugin_id IS NULL AND runner_id IS NULL)
        OR (scope = 'FLOW' AND tenant_id IS NOT NULL
            AND namespace_name IS NOT NULL AND flow_id IS NOT NULL
            AND plugin_id IS NULL AND runner_id IS NULL)
        OR (scope = 'PLUGIN' AND tenant_id IS NOT NULL
            AND namespace_name IS NULL AND flow_id IS NULL
            AND plugin_id IS NOT NULL AND runner_id IS NULL)
        OR (scope = 'RUNNER' AND tenant_id IS NOT NULL
            AND namespace_name IS NULL AND flow_id IS NULL
            AND plugin_id IS NULL AND runner_id IS NOT NULL)
    )
);

CREATE INDEX operational_controls_effective_idx
    ON operational_controls (state, expires_at, tenant_id, scope, updated_at DESC);
CREATE INDEX operational_controls_boundaries_idx
    ON operational_controls USING gin (boundaries);

CREATE TABLE operational_control_acknowledgements (
    control_id uuid NOT NULL REFERENCES operational_controls(control_id) ON DELETE CASCADE,
    tenant_id uuid NULL REFERENCES tenants(id),
    component_id text NOT NULL,
    component_role text NOT NULL,
    control_version bigint NOT NULL CHECK (control_version > 0),
    acknowledged_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (control_id, component_id)
);

CREATE INDEX operational_control_ack_role_idx
    ON operational_control_acknowledgements (component_role, acknowledged_at DESC);

CREATE TABLE operational_control_events (
    event_id uuid PRIMARY KEY,
    control_id uuid NOT NULL REFERENCES operational_controls(control_id) ON DELETE CASCADE,
    tenant_id uuid NULL REFERENCES tenants(id),
    action text NOT NULL CHECK (
        action IN ('ACTIVATE', 'EXTEND', 'BYPASS', 'DEACTIVATE', 'EXPIRE')
    ),
    actor_id text NOT NULL,
    reason text NOT NULL,
    evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT operational_control_event_evidence_object
        CHECK (jsonb_typeof(evidence) = 'object')
);

CREATE INDEX operational_control_events_history_idx
    ON operational_control_events (tenant_id, occurred_at DESC, event_id DESC);

CREATE OR REPLACE FUNCTION amesh_notify_operational_control_change()
RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'amesh_control_changes',
        json_build_object(
            'resource', TG_TABLE_NAME,
            'id', COALESCE(to_jsonb(NEW)->>'control_id', to_jsonb(NEW)->>'announcement_id'),
            'operation', TG_OP
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER operational_controls_notify
AFTER INSERT OR UPDATE ON operational_controls
FOR EACH ROW EXECUTE FUNCTION amesh_notify_operational_control_change();

CREATE TRIGGER announcements_notify
AFTER INSERT OR UPDATE ON announcements
FOR EACH ROW EXECUTE FUNCTION amesh_notify_operational_control_change();

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES
    ('flow-author', 'announcement', 'view', 'ALLOW'),
    ('operator', 'announcement', 'view', 'ALLOW'),
    ('operator', 'operational_control', 'view', 'ALLOW'),
    ('viewer', 'announcement', 'view', 'ALLOW')
ON CONFLICT DO NOTHING;

GRANT SELECT ON announcements TO amesh_runtime;
GRANT SELECT ON operational_controls TO amesh_runtime;
GRANT SELECT ON operational_control_acknowledgements TO amesh_runtime;
GRANT SELECT ON operational_control_events TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE ON announcements TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON operational_controls TO amesh_tenant_admin;
GRANT SELECT, INSERT, UPDATE ON operational_control_acknowledgements TO amesh_tenant_admin;
GRANT SELECT, INSERT ON operational_control_events TO amesh_tenant_admin;

ALTER TABLE announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcements FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_visibility ON announcements TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

ALTER TABLE operational_controls ENABLE ROW LEVEL SECURITY;
ALTER TABLE operational_controls FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_visibility ON operational_controls TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

ALTER TABLE operational_control_acknowledgements ENABLE ROW LEVEL SECURITY;
ALTER TABLE operational_control_acknowledgements FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_visibility ON operational_control_acknowledgements TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

ALTER TABLE operational_control_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE operational_control_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_visibility ON operational_control_events TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

COMMIT;
