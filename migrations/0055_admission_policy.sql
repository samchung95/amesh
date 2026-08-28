BEGIN;

CREATE TABLE admission_policy_revisions (
    policy_id uuid NOT NULL,
    revision integer NOT NULL CHECK (revision > 0),
    tenant_id uuid NULL REFERENCES tenants(id),
    namespace_name text NULL,
    policy_key text NOT NULL,
    scope text NOT NULL CHECK (scope IN ('INSTANCE', 'TENANT', 'NAMESPACE')),
    active boolean NOT NULL DEFAULT true,
    digest text NOT NULL CHECK (digest ~ '^sha256:[0-9a-f]{64}$'),
    document jsonb NOT NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (policy_id, revision),
    CHECK (
        (scope = 'INSTANCE' AND tenant_id IS NULL AND namespace_name IS NULL)
        OR (scope = 'TENANT' AND tenant_id IS NOT NULL AND namespace_name IS NULL)
        OR (scope = 'NAMESPACE' AND tenant_id IS NOT NULL AND namespace_name IS NOT NULL)
    )
);

CREATE UNIQUE INDEX admission_policy_active_identity_idx
    ON admission_policy_revisions (
        scope,
        COALESCE(tenant_id, '00000000-0000-0000-0000-000000000000'::uuid),
        COALESCE(namespace_name, ''),
        policy_key
    )
    WHERE active;

CREATE INDEX admission_policy_effective_idx
    ON admission_policy_revisions (tenant_id, namespace_name, active, policy_key);

CREATE TABLE admission_policy_decisions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    stage text NOT NULL CHECK (
        stage IN ('VALIDATE', 'SAVE', 'PROMOTE', 'LAUNCH', 'DISPATCH')
    ),
    outcome text NOT NULL CHECK (
        outcome IN ('ALLOW', 'DENY', 'WARN', 'MUTATE_DEFAULT', 'REQUIRE_APPROVAL')
    ),
    allowed boolean NOT NULL,
    actor_id text NOT NULL,
    flow_key text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    execution_id uuid NULL,
    task_run_id uuid NULL,
    decision jsonb NOT NULL,
    decided_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX admission_policy_decision_history_idx
    ON admission_policy_decisions (tenant_id, decided_at DESC, id DESC);
CREATE INDEX admission_policy_decision_execution_idx
    ON admission_policy_decisions (tenant_id, execution_id, task_run_id)
    WHERE execution_id IS NOT NULL;

ALTER TABLE admission_policy_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE admission_policy_revisions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON admission_policy_revisions TO amesh_runtime
    USING (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id());

ALTER TABLE admission_policy_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE admission_policy_decisions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON admission_policy_decisions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE, DELETE ON
    admission_policy_revisions,
    admission_policy_decisions
TO amesh_runtime;

COMMIT;
