BEGIN;

CREATE TABLE workflow_apps (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    app_id text NOT NULL CHECK (app_id ~ '^[a-z][a-z0-9_.-]{0,127}$'),
    current_revision integer NOT NULL CHECK (current_revision > 0),
    resource_version bigint NOT NULL CHECK (resource_version > 0),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, namespace_name, app_id)
);

CREATE TABLE workflow_app_revisions (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    app_id text NOT NULL,
    revision integer NOT NULL CHECK (revision > 0),
    flow_id text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    definition jsonb NOT NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, namespace_name, app_id, revision),
    CONSTRAINT workflow_app_revision_parent_fk
        FOREIGN KEY (tenant_id, namespace_name, app_id)
        REFERENCES workflow_apps(tenant_id, namespace_name, app_id),
    CONSTRAINT workflow_app_definition_object CHECK (jsonb_typeof(definition) = 'object')
);

CREATE INDEX workflow_apps_list_idx
    ON workflow_apps (tenant_id, namespace_name, updated_at DESC, app_id);

CREATE TABLE human_tasks (
    human_task_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    execution_id uuid NOT NULL,
    task_run_id uuid NOT NULL,
    attempt integer NOT NULL CHECK (attempt > 0),
    title text NOT NULL CHECK (title <> ''),
    description text NOT NULL DEFAULT '',
    form jsonb NOT NULL DEFAULT '{"fields":[],"layout":[]}'::jsonb,
    assignee_ids uuid[] NOT NULL DEFAULT '{}',
    group_ids uuid[] NOT NULL DEFAULT '{}',
    deadline_at timestamptz NULL,
    escalation_assignee_ids uuid[] NOT NULL DEFAULT '{}',
    escalation_group_ids uuid[] NOT NULL DEFAULT '{}',
    state text NOT NULL DEFAULT 'OPEN'
        CHECK (state IN ('OPEN', 'ESCALATED', 'APPROVED', 'REJECTED', 'CHANGES_REQUESTED')),
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    resume_state text NOT NULL DEFAULT 'WAITING'
        CHECK (resume_state IN ('WAITING', 'PENDING', 'COMPLETED')),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    decided_by uuid NULL,
    decided_at timestamptz NULL,
    reason text NOT NULL DEFAULT '',
    form_values jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT human_tasks_identity_unique UNIQUE (tenant_id, task_run_id, attempt),
    CONSTRAINT human_tasks_execution_fk
        FOREIGN KEY (tenant_id, execution_id) REFERENCES executions(tenant_id, id),
    CONSTRAINT human_tasks_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs(tenant_id, execution_id, id),
    CONSTRAINT human_tasks_form_object CHECK (jsonb_typeof(form) = 'object'),
    CONSTRAINT human_tasks_values_object CHECK (jsonb_typeof(form_values) = 'object'),
    CONSTRAINT human_tasks_participants CHECK (
        cardinality(assignee_ids) > 0 OR cardinality(group_ids) > 0
    )
);

CREATE INDEX human_tasks_inbox_idx
    ON human_tasks (tenant_id, state, deadline_at, created_at DESC);
CREATE INDEX human_tasks_assignees_idx ON human_tasks USING gin (assignee_ids);
CREATE INDEX human_tasks_groups_idx ON human_tasks USING gin (group_ids);
CREATE INDEX human_tasks_pending_resume_idx
    ON human_tasks (tenant_id, updated_at, human_task_id)
    WHERE resume_state = 'PENDING';

CREATE TABLE human_task_actions (
    action_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    human_task_id uuid NOT NULL REFERENCES human_tasks(human_task_id) ON DELETE CASCADE,
    idempotency_key text NOT NULL,
    action text NOT NULL CHECK (
        action IN ('APPROVE', 'REJECT', 'REQUEST_CHANGES', 'COMMENT', 'ATTACH',
                   'DELEGATE', 'ESCALATE')
    ),
    actor_id uuid NULL,
    reason text NOT NULL DEFAULT '',
    form_values jsonb NOT NULL DEFAULT '{}'::jsonb,
    comment text NOT NULL DEFAULT '',
    artifact_uri text NULL,
    assignee_ids uuid[] NOT NULL DEFAULT '{}',
    group_ids uuid[] NOT NULL DEFAULT '{}',
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT human_task_action_identity_unique
        UNIQUE (tenant_id, human_task_id, idempotency_key),
    CONSTRAINT human_task_action_values_object CHECK (jsonb_typeof(form_values) = 'object')
);

CREATE INDEX human_task_actions_history_idx
    ON human_task_actions (tenant_id, human_task_id, occurred_at, action_id);

CREATE TABLE human_task_notifications (
    notification_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    human_task_id uuid NOT NULL REFERENCES human_tasks(human_task_id) ON DELETE CASCADE,
    recipient_id uuid NOT NULL,
    recipient_type text NOT NULL CHECK (recipient_type IN ('USER', 'GROUP')),
    kind text NOT NULL CHECK (kind IN ('ASSIGNED', 'ESCALATED', 'DELEGATED', 'DECIDED')),
    title text NOT NULL,
    message text NOT NULL,
    deadline_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    read_at timestamptz NULL,
    CONSTRAINT human_task_notification_identity_unique
        UNIQUE (tenant_id, human_task_id, recipient_id, recipient_type, kind)
);

CREATE INDEX human_task_notifications_recipient_idx
    ON human_task_notifications (tenant_id, recipient_id, read_at, created_at DESC);

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES
    ('flow-author', 'app', 'view', 'ALLOW'),
    ('flow-author', 'app', 'create', 'ALLOW'),
    ('flow-author', 'app', 'update', 'ALLOW'),
    ('flow-author', 'app', 'execute', 'ALLOW'),
    ('flow-author', 'human_task', 'view', 'ALLOW'),
    ('flow-author', 'human_task', 'update', 'ALLOW'),
    ('operator', 'app', 'view', 'ALLOW'),
    ('operator', 'app', 'execute', 'ALLOW'),
    ('operator', 'human_task', 'view', 'ALLOW'),
    ('operator', 'human_task', 'update', 'ALLOW'),
    ('operator', 'human_task', 'manage', 'ALLOW'),
    ('viewer', 'app', 'view', 'ALLOW')
ON CONFLICT DO NOTHING;

GRANT SELECT, INSERT, UPDATE ON workflow_apps TO amesh_runtime;
GRANT SELECT, INSERT ON workflow_app_revisions TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE ON human_tasks TO amesh_runtime;
GRANT SELECT, INSERT ON human_task_actions TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE ON human_task_notifications TO amesh_runtime;

ALTER TABLE workflow_apps ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_apps FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON workflow_apps TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE workflow_app_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_app_revisions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON workflow_app_revisions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE human_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE human_tasks FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON human_tasks TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE human_task_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE human_task_actions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON human_task_actions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE human_task_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE human_task_notifications FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON human_task_notifications TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
