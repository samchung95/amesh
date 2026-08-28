BEGIN;

CREATE TABLE service_instances (
    id uuid PRIMARY KEY,
    role text NOT NULL CHECK (
        role IN ('webserver', 'executor', 'scheduler', 'worker', 'indexer', 'maintenance')
    ),
    instance_name text NOT NULL,
    version text NOT NULL,
    failure_zone text NULL,
    state text NOT NULL DEFAULT 'STARTING' CHECK (
        state IN ('STARTING', 'READY', 'DRAINING', 'STOPPED')
    ),
    generation bigint NOT NULL DEFAULT 1 CHECK (generation > 0),
    resource_version bigint NOT NULL DEFAULT 1 CHECK (resource_version > 0),
    labels jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(labels) = 'object'),
    ownership jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(ownership) = 'object'),
    partitions jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(partitions) = 'object'),
    dependencies jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(dependencies) = 'object'),
    registered_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    last_heartbeat_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    stopped_at timestamptz NULL,
    UNIQUE (role, instance_name)
);

CREATE INDEX service_instances_role_state_heartbeat_idx
    ON service_instances (role, state, last_heartbeat_at DESC);

GRANT SELECT, INSERT, UPDATE, DELETE ON service_instances TO amesh_runtime;

COMMIT;
