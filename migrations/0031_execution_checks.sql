BEGIN;

CREATE TABLE namespace_check_policies (
    policy_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    policy_key text NOT NULL,
    source text NOT NULL CHECK (source IN ('NAMESPACE', 'PLUGIN_DEFAULT')),
    task_type text NULL,
    definition jsonb NOT NULL,
    enabled boolean NOT NULL DEFAULT true,
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT namespace_check_policy_definition_object
        CHECK (jsonb_typeof(definition) = 'object'),
    CONSTRAINT namespace_check_policy_plugin_target
        CHECK (source <> 'PLUGIN_DEFAULT' OR task_type IS NOT NULL),
    UNIQUE (tenant_id, namespace_name, policy_key)
);

CREATE TABLE flow_check_definitions (
    check_definition_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    flow_revision_id uuid NOT NULL REFERENCES flow_revisions(id),
    namespace_name text NOT NULL,
    flow_key text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    check_key text NOT NULL,
    check_type text NOT NULL CHECK (
        check_type IN (
            'DURATION', 'START_DELAY', 'FRESHNESS',
            'COMPLETION_WINDOW', 'OUTPUT', 'EXPRESSION'
        )
    ),
    source text NOT NULL CHECK (source IN ('EXPLICIT', 'NAMESPACE', 'PLUGIN_DEFAULT')),
    source_policy_id uuid NULL REFERENCES namespace_check_policies(policy_id),
    definition jsonb NOT NULL,
    active boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT flow_check_definition_object CHECK (jsonb_typeof(definition) = 'object'),
    CONSTRAINT flow_check_definition_revision_fk
        FOREIGN KEY (tenant_id, flow_revision_id)
        REFERENCES flow_revisions (tenant_id, id),
    UNIQUE (tenant_id, flow_revision_id, check_key)
);

CREATE TABLE check_deadlines (
    deadline_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    check_definition_id uuid NOT NULL REFERENCES flow_check_definitions(check_definition_id),
    execution_id uuid NULL,
    subject_key text NOT NULL,
    deadline_type text NOT NULL CHECK (
        deadline_type IN ('DURATION', 'START_DELAY', 'FRESHNESS', 'COMPLETION_WINDOW')
    ),
    due_at timestamptz NOT NULL,
    state text NOT NULL DEFAULT 'PENDING' CHECK (state IN ('PENDING', 'PROCESSED')),
    processed_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT check_deadline_execution_fk
        FOREIGN KEY (tenant_id, execution_id) REFERENCES executions (tenant_id, id),
    UNIQUE (tenant_id, check_definition_id, subject_key)
);

CREATE TABLE check_evaluations (
    evaluation_id uuid NOT NULL,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    check_definition_id uuid NOT NULL REFERENCES flow_check_definitions(check_definition_id),
    execution_id uuid NULL,
    namespace_name text NOT NULL,
    flow_key text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    check_key text NOT NULL,
    check_type text NOT NULL,
    source text NOT NULL,
    evaluation_point text NOT NULL CHECK (
        evaluation_point IN ('STARTED', 'TERMINAL', 'DEADLINE', 'FRESHNESS')
    ),
    subject_key text NOT NULL,
    outcome text NOT NULL CHECK (outcome IN ('PASS', 'WARN', 'FAIL', 'ERROR')),
    severity text NOT NULL CHECK (severity IN ('WARN', 'FAIL')),
    reason text NOT NULL,
    evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    evaluated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, evaluation_id),
    CONSTRAINT check_evaluation_execution_fk
        FOREIGN KEY (tenant_id, execution_id) REFERENCES executions (tenant_id, id),
    CONSTRAINT check_evaluation_evidence_object CHECK (jsonb_typeof(evidence) = 'object'),
    CONSTRAINT check_evaluation_labels_object CHECK (jsonb_typeof(labels) = 'object'),
    UNIQUE (tenant_id, check_definition_id, subject_key, evaluation_point)
);

CREATE TABLE check_action_queue (
    action_id uuid NOT NULL,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    evaluation_id uuid NOT NULL,
    execution_id uuid NULL,
    action_index integer NOT NULL CHECK (action_index >= 0),
    action_type text NOT NULL CHECK (action_type IN ('NOTIFY', 'RUN_FLOW')),
    state text NOT NULL DEFAULT 'PENDING' CHECK (
        state IN (
            'PENDING', 'PROCESSING', 'RETRY_WAIT',
            'SUCCEEDED', 'DEAD_LETTERED', 'SKIPPED'
        )
    ),
    target_namespace text NULL,
    target_flow_key text NULL,
    channel text NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    policy_depth integer NOT NULL DEFAULT 0 CHECK (policy_depth >= 0),
    max_depth integer NOT NULL CHECK (max_depth > 0),
    attempt integer NOT NULL DEFAULT 0 CHECK (attempt >= 0),
    max_attempts integer NOT NULL CHECK (max_attempts > 0),
    available_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    owner_id uuid NULL,
    fencing_token bigint NOT NULL DEFAULT 0 CHECK (fencing_token >= 0),
    lease_expires_at timestamptz NULL,
    last_error text NULL,
    evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    PRIMARY KEY (tenant_id, action_id),
    CONSTRAINT check_action_evaluation_fk
        FOREIGN KEY (tenant_id, evaluation_id)
        REFERENCES check_evaluations (tenant_id, evaluation_id),
    CONSTRAINT check_action_execution_fk
        FOREIGN KEY (tenant_id, execution_id) REFERENCES executions (tenant_id, id),
    CONSTRAINT check_action_payload_object CHECK (jsonb_typeof(payload) = 'object'),
    CONSTRAINT check_action_evidence_object CHECK (jsonb_typeof(evidence) = 'object'),
    CONSTRAINT check_action_owner_lease_pair CHECK (
        (owner_id IS NULL AND lease_expires_at IS NULL)
        OR (owner_id IS NOT NULL AND lease_expires_at IS NOT NULL)
    ),
    UNIQUE (tenant_id, evaluation_id, action_index)
);

CREATE INDEX flow_check_definitions_active_idx
    ON flow_check_definitions (tenant_id, active, namespace_name, flow_key, check_key);
CREATE INDEX check_deadlines_due_idx
    ON check_deadlines (tenant_id, due_at, deadline_id) WHERE state = 'PENDING';
CREATE INDEX check_evaluations_timeline_idx
    ON check_evaluations (tenant_id, evaluated_at DESC, evaluation_id);
CREATE INDEX check_evaluations_resource_idx
    ON check_evaluations (tenant_id, namespace_name, flow_key, evaluated_at DESC);
CREATE INDEX check_action_queue_due_idx
    ON check_action_queue (tenant_id, available_at, created_at, action_id)
    WHERE state IN ('PENDING', 'RETRY_WAIT');
CREATE INDEX check_action_queue_expired_idx
    ON check_action_queue (tenant_id, lease_expires_at, action_id)
    WHERE state = 'PROCESSING';

GRANT SELECT, INSERT, UPDATE, DELETE ON namespace_check_policies TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON flow_check_definitions TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON check_deadlines TO amesh_runtime;
GRANT SELECT, INSERT ON check_evaluations TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE ON check_action_queue TO amesh_runtime;

ALTER TABLE namespace_check_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE namespace_check_policies FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON namespace_check_policies TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE flow_check_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE flow_check_definitions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON flow_check_definitions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE check_deadlines ENABLE ROW LEVEL SECURITY;
ALTER TABLE check_deadlines FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON check_deadlines TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE check_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE check_evaluations FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON check_evaluations TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE check_action_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE check_action_queue FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON check_action_queue TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
