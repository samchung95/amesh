BEGIN;

CREATE TABLE agent_sessions (
    session_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL,
    execution_id uuid NOT NULL,
    task_run_id uuid NOT NULL,
    attempt integer NOT NULL CHECK (attempt > 0),
    capability_pin_id uuid NOT NULL REFERENCES agent_capability_pins(pin_id),
    envelope_digest text NOT NULL CHECK (envelope_digest ~ '^sha256:[0-9a-f]{64}$'),
    state text NOT NULL CHECK (state IN ('RUNNING', 'SUCCEEDED', 'FAILED')),
    phase text NOT NULL CHECK (
        phase IN ('READY', 'MODEL', 'POLICY', 'APPROVAL', 'TOOL', 'VALIDATING', 'COMPLETE')
    ),
    version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
    checkpoint jsonb NOT NULL DEFAULT '{}'::jsonb,
    counters jsonb NOT NULL DEFAULT '{}'::jsonb,
    final_result jsonb NULL,
    error text NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    CONSTRAINT agent_sessions_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs (tenant_id, execution_id, id) ON DELETE CASCADE,
    UNIQUE (tenant_id, task_run_id, attempt),
    CHECK (
        (state = 'RUNNING' AND completed_at IS NULL)
        OR (state IN ('SUCCEEDED', 'FAILED') AND completed_at IS NOT NULL)
    )
);

CREATE INDEX agent_sessions_execution_idx
    ON agent_sessions (tenant_id, execution_id, updated_at DESC);

CREATE TABLE agent_session_events (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    execution_id uuid NOT NULL,
    task_run_id uuid NOT NULL,
    session_id uuid NOT NULL REFERENCES agent_sessions(session_id) ON DELETE CASCADE,
    event_index bigint NOT NULL CHECK (event_index > 0),
    event_key text NOT NULL,
    event_type text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT agent_session_events_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs (tenant_id, execution_id, id) ON DELETE CASCADE,
    UNIQUE (tenant_id, session_id, event_index),
    UNIQUE (tenant_id, session_id, event_key)
);

CREATE FUNCTION amesh_capture_agent_session_evidence() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO execution_evidence_events (
        tenant_id, event_id, execution_id, task_run_id, kind,
        event_type, payload, occurred_at
    ) VALUES (
        NEW.tenant_id, NEW.event_id, NEW.execution_id, NEW.task_run_id, 'STATE',
        'agent.' || lower(NEW.event_type),
        jsonb_build_object(
            'entity', 'agentSession',
            'sessionId', NEW.session_id,
            'eventIndex', NEW.event_index,
            'eventKey', NEW.event_key,
            'payload', NEW.payload
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, event_id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER agent_session_evidence_after_insert
AFTER INSERT ON agent_session_events
FOR EACH ROW EXECUTE FUNCTION amesh_capture_agent_session_evidence();

ALTER TABLE agent_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_sessions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_sessions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE agent_session_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_session_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_session_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE ON agent_sessions, agent_session_events TO amesh_runtime;

COMMIT;
