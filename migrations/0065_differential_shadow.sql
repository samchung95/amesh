BEGIN;

CREATE TABLE differential_specs (
    spec_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_name text NOT NULL CHECK (char_length(namespace_name) BETWEEN 1 AND 255),
    idempotency_key text NOT NULL CHECK (char_length(idempotency_key) BETWEEN 1 AND 512),
    left_configuration jsonb NOT NULL CHECK (jsonb_typeof(left_configuration) = 'object'),
    right_configuration jsonb NOT NULL CHECK (jsonb_typeof(right_configuration) = 'object'),
    inputs jsonb NOT NULL,
    input_digest text NOT NULL CHECK (input_digest ~ '^sha256:[0-9a-f]{64}$'),
    fixtures jsonb NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(fixtures) = 'array'),
    policy jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(policy) = 'object'),
    left_run_id uuid NULL,
    right_run_id uuid NULL,
    state text NOT NULL DEFAULT 'PENDING'
        CHECK (state IN ('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED')),
    report jsonb NULL CHECK (report IS NULL OR jsonb_typeof(report) = 'object'),
    version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
    actor_id text NOT NULL CHECK (char_length(actor_id) BETWEEN 1 AND 255),
    error text NULL CHECK (error IS NULL OR char_length(error) <= 4096),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    UNIQUE (tenant_id, spec_id),
    UNIQUE (tenant_id, namespace_name, idempotency_key),
    CHECK (
        left_configuration ? 'key'
        AND char_length(left_configuration ->> 'key') BETWEEN 1 AND 512
        AND jsonb_typeof(left_configuration -> 'revision') = 'number'
        AND (left_configuration ->> 'revision') ~ '^[1-9][0-9]*$'
        AND (left_configuration ->> 'digest') IS NOT NULL
        AND (left_configuration ->> 'digest') ~ '^sha256:[0-9a-f]{64}$'
    ),
    CHECK (
        right_configuration ? 'key'
        AND char_length(right_configuration ->> 'key') BETWEEN 1 AND 512
        AND jsonb_typeof(right_configuration -> 'revision') = 'number'
        AND (right_configuration ->> 'revision') ~ '^[1-9][0-9]*$'
        AND (right_configuration ->> 'digest') IS NOT NULL
        AND (right_configuration ->> 'digest') ~ '^sha256:[0-9a-f]{64}$'
    ),
    CHECK (
        (state IN ('PENDING', 'RUNNING') AND completed_at IS NULL)
        OR (state IN ('SUCCEEDED', 'FAILED') AND completed_at IS NOT NULL)
    )
);

CREATE INDEX differential_specs_timeline_idx
    ON differential_specs (tenant_id, namespace_name, updated_at DESC, spec_id DESC);

CREATE TABLE differential_runs (
    run_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    spec_id uuid NOT NULL,
    side text NOT NULL CHECK (side IN ('LEFT', 'RIGHT')),
    configuration_digest text NOT NULL CHECK (configuration_digest ~ '^sha256:[0-9a-f]{64}$'),
    input_digest text NOT NULL CHECK (input_digest ~ '^sha256:[0-9a-f]{64}$'),
    state text NOT NULL DEFAULT 'PENDING'
        CHECK (state IN ('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED')),
    attempt integer NOT NULL DEFAULT 0 CHECK (attempt >= 0),
    observation jsonb NULL CHECK (observation IS NULL OR jsonb_typeof(observation) = 'object'),
    error text NULL CHECK (error IS NULL OR char_length(error) <= 4096),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    CONSTRAINT differential_runs_spec_fk
        FOREIGN KEY (tenant_id, spec_id)
        REFERENCES differential_specs (tenant_id, spec_id) ON DELETE CASCADE,
    UNIQUE (tenant_id, run_id),
    UNIQUE (tenant_id, spec_id, side),
    CHECK (
        (state IN ('PENDING', 'RUNNING') AND completed_at IS NULL)
        OR (state IN ('SUCCEEDED', 'FAILED') AND completed_at IS NOT NULL)
    ),
    CHECK ((state = 'SUCCEEDED' AND observation IS NOT NULL) OR state <> 'SUCCEEDED')
);

CREATE INDEX differential_runs_resume_idx
    ON differential_runs (tenant_id, state, updated_at, run_id);

ALTER TABLE differential_specs
    ADD CONSTRAINT differential_specs_left_run_fk
        FOREIGN KEY (tenant_id, left_run_id)
        REFERENCES differential_runs (tenant_id, run_id),
    ADD CONSTRAINT differential_specs_right_run_fk
        FOREIGN KEY (tenant_id, right_run_id)
        REFERENCES differential_runs (tenant_id, run_id);

CREATE TABLE differential_events (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    spec_id uuid NOT NULL,
    run_id uuid NULL,
    sequence bigint NOT NULL CHECK (sequence > 0),
    event_key text NOT NULL CHECK (char_length(event_key) BETWEEN 1 AND 512),
    event_type text NOT NULL CHECK (char_length(event_type) BETWEEN 1 AND 128),
    payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(payload) = 'object'),
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT differential_events_spec_fk
        FOREIGN KEY (tenant_id, spec_id)
        REFERENCES differential_specs (tenant_id, spec_id) ON DELETE CASCADE,
    CONSTRAINT differential_events_run_fk
        FOREIGN KEY (tenant_id, run_id)
        REFERENCES differential_runs (tenant_id, run_id) ON DELETE CASCADE,
    UNIQUE (tenant_id, spec_id, sequence),
    UNIQUE (tenant_id, spec_id, event_key)
);

CREATE INDEX differential_events_timeline_idx
    ON differential_events (tenant_id, spec_id, sequence);

CREATE FUNCTION amesh_enqueue_differential_event() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    tenant_slug text;
BEGIN
    SELECT slug INTO STRICT tenant_slug FROM tenants WHERE id = NEW.tenant_id;
    INSERT INTO messages_outbox (
        tenant_id,
        message_id,
        subject,
        partition_key,
        envelope,
        available_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        'differential-shadow',
        'differential:' || NEW.spec_id::text,
        jsonb_build_object(
            'message_id', NEW.event_id,
            'message_type', NEW.event_type,
            'schema_version', 1,
            'tenant_id', tenant_slug,
            'partition_key', 'differential:' || NEW.spec_id::text,
            'produced_at', NEW.occurred_at,
            'payload', jsonb_build_object(
                'spec_id', NEW.spec_id,
                'run_id', NEW.run_id,
                'sequence', NEW.sequence,
                'event_key', NEW.event_key,
                'event', NEW.payload
            )
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER differential_event_outbox
AFTER INSERT ON differential_events
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_differential_event();

GRANT SELECT, INSERT, UPDATE ON differential_specs, differential_runs, differential_events
    TO amesh_runtime;

ALTER TABLE differential_specs ENABLE ROW LEVEL SECURITY;
ALTER TABLE differential_specs FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON differential_specs TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE differential_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE differential_runs FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON differential_runs TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE differential_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE differential_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON differential_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
