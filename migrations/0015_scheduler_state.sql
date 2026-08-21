BEGIN;

CREATE TABLE scheduler_states (
    trigger_definition_id uuid PRIMARY KEY REFERENCES trigger_definitions(id),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    flow_key text NOT NULL,
    flow_revision integer NOT NULL CHECK (flow_revision > 0),
    trigger_key text NOT NULL,
    next_fire_at timestamptz NULL,
    last_evaluated_at timestamptz NULL,
    last_occurrence_at timestamptz NULL,
    owner_id uuid NULL,
    fencing_token bigint NOT NULL DEFAULT 0 CHECK (fencing_token >= 0),
    lease_expires_at timestamptz NULL,
    last_decision text NOT NULL DEFAULT 'schedule initialized',
    missed_count integer NOT NULL DEFAULT 0 CHECK (missed_count >= 0),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT scheduler_states_owner_lease_pair CHECK (
        (owner_id IS NULL AND lease_expires_at IS NULL)
        OR (owner_id IS NOT NULL AND lease_expires_at IS NOT NULL)
    ),
    UNIQUE (tenant_id, namespace_name, flow_key, flow_revision, trigger_key)
);

CREATE INDEX scheduler_states_due_idx
    ON scheduler_states (next_fire_at, lease_expires_at, trigger_definition_id)
    WHERE next_fire_at IS NOT NULL;

GRANT SELECT, INSERT, UPDATE, DELETE ON scheduler_states TO amesh_runtime;

ALTER TABLE scheduler_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE scheduler_states FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON scheduler_states TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
