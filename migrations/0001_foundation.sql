BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE tenants (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug text NOT NULL UNIQUE,
    display_name text NOT NULL,
    status text NOT NULL DEFAULT 'ACTIVE',
    version bigint NOT NULL DEFAULT 1,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE namespaces (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    name text NOT NULL,
    parent_id uuid NULL REFERENCES namespaces(id),
    version bigint NOT NULL DEFAULT 1,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, name)
);

CREATE TABLE flows (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    namespace_id uuid NOT NULL REFERENCES namespaces(id),
    flow_key text NOT NULL,
    active_revision integer NULL,
    status text NOT NULL DEFAULT 'DRAFT',
    version bigint NOT NULL DEFAULT 1,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, namespace_id, flow_key)
);

CREATE TABLE flow_revisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    flow_id uuid NOT NULL REFERENCES flows(id),
    revision integer NOT NULL,
    semantic_hash text NOT NULL,
    canonical_definition jsonb NOT NULL,
    plugin_resolution jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, flow_id, revision),
    UNIQUE (tenant_id, flow_id, semantic_hash)
);

ALTER TABLE flows
    ADD CONSTRAINT flows_active_revision_fk
    FOREIGN KEY (tenant_id, id, active_revision)
    REFERENCES flow_revisions (tenant_id, flow_id, revision)
    DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE executions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    flow_id uuid NOT NULL REFERENCES flows(id),
    flow_revision_id uuid NOT NULL REFERENCES flow_revisions(id),
    namespace_name text NOT NULL,
    flow_key text NOT NULL,
    state text NOT NULL,
    epoch integer NOT NULL DEFAULT 1,
    version bigint NOT NULL DEFAULT 0,
    idempotency_key text NULL,
    inputs jsonb NOT NULL DEFAULT '{}'::jsonb,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    terminal_at timestamptz NULL,
    UNIQUE (tenant_id, idempotency_key)
);

CREATE INDEX executions_tenant_flow_created_idx
    ON executions (tenant_id, flow_id, created_at DESC);
CREATE INDEX executions_tenant_state_updated_idx
    ON executions (tenant_id, state, updated_at DESC);

CREATE TABLE execution_events (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    execution_id uuid NOT NULL REFERENCES executions(id),
    sequence bigint NOT NULL,
    event_id uuid NOT NULL,
    event_type text NOT NULL,
    schema_version integer NOT NULL,
    correlation_id uuid NOT NULL,
    causation_id uuid NULL,
    actor_id text NOT NULL,
    occurred_at timestamptz NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (tenant_id, execution_id, sequence),
    UNIQUE (tenant_id, event_id)
);

CREATE TABLE commands_inbox (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    command_id uuid NOT NULL,
    idempotency_key text NOT NULL,
    command_type text NOT NULL,
    request_hash text NOT NULL,
    response_status integer NULL,
    response_body jsonb NULL,
    committed_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, command_id),
    UNIQUE (tenant_id, idempotency_key)
);

CREATE TABLE messages_outbox (
    sequence bigserial PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    message_id uuid NOT NULL,
    subject text NOT NULL,
    partition_key text NOT NULL,
    envelope jsonb NOT NULL,
    available_at timestamptz NOT NULL DEFAULT now(),
    published_at timestamptz NULL,
    attempts integer NOT NULL DEFAULT 0,
    last_error text NULL,
    UNIQUE (tenant_id, message_id)
);

CREATE INDEX messages_outbox_pending_idx
    ON messages_outbox (available_at, sequence)
    WHERE published_at IS NULL;

-- Authoritative PostgreSQL work queue. LISTEN/NOTIFY only reduces polling latency;
-- queue rows, transactions and fencing tokens define correctness.
CREATE TABLE durable_work_queue (
    id bigserial PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    message_id uuid NOT NULL,
    lane text NOT NULL,
    partition_key text NOT NULL,
    message_type text NOT NULL,
    schema_version integer NOT NULL CHECK (schema_version > 0),
    envelope jsonb NOT NULL,
    priority integer NOT NULL DEFAULT 0,
    available_at timestamptz NOT NULL DEFAULT now(),
    state text NOT NULL DEFAULT 'READY'
        CHECK (state IN ('READY', 'CLAIMED', 'COMPLETED', 'DEAD_LETTER')),
    delivery_attempt integer NOT NULL DEFAULT 0 CHECK (delivery_attempt >= 0),
    max_attempts integer NOT NULL DEFAULT 25 CHECK (max_attempts > 0),
    claimed_by text NULL,
    fencing_token bigint NOT NULL DEFAULT 0 CHECK (fencing_token >= 0),
    lease_expires_at timestamptz NULL,
    last_error text NULL,
    completed_at timestamptz NULL,
    dead_lettered_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, message_id)
);

CREATE INDEX durable_work_queue_claim_idx
    ON durable_work_queue (lane, priority DESC, available_at, id)
    WHERE state = 'READY';

CREATE INDEX durable_work_queue_expired_claim_idx
    ON durable_work_queue (lease_expires_at, id)
    WHERE state = 'CLAIMED';

CREATE INDEX durable_work_queue_partition_idx
    ON durable_work_queue (tenant_id, lane, partition_key, id);

CREATE OR REPLACE FUNCTION notify_amesh_work() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('amesh_work', NEW.lane);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER durable_work_queue_notify
AFTER INSERT ON durable_work_queue
FOR EACH ROW EXECUTE FUNCTION notify_amesh_work();

CREATE TABLE consumed_messages (
    consumer_name text NOT NULL,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    message_id uuid NOT NULL,
    consumed_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (consumer_name, tenant_id, message_id)
);

CREATE TABLE workers (
    id uuid PRIMARY KEY,
    tenant_id uuid NULL REFERENCES tenants(id),
    worker_group text NOT NULL,
    instance_name text NOT NULL,
    version text NOT NULL,
    capabilities jsonb NOT NULL DEFAULT '{}'::jsonb,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    status text NOT NULL,
    last_heartbeat_at timestamptz NOT NULL,
    registered_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE task_runs (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    execution_id uuid NOT NULL REFERENCES executions(id),
    task_path text NOT NULL,
    iteration_key text NULL,
    state text NOT NULL,
    current_attempt integer NOT NULL DEFAULT 0,
    version bigint NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, execution_id, task_path, iteration_key)
);

CREATE TABLE task_attempts (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    task_run_id uuid NOT NULL REFERENCES task_runs(id),
    attempt integer NOT NULL,
    state text NOT NULL,
    worker_id uuid NULL REFERENCES workers(id),
    fencing_token bigint NOT NULL,
    lease_expires_at timestamptz NULL,
    started_at timestamptz NULL,
    finished_at timestamptz NULL,
    result jsonb NULL,
    UNIQUE (tenant_id, task_run_id, attempt)
);

CREATE TABLE leases (
    resource_type text NOT NULL,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    resource_id text NOT NULL,
    owner_id uuid NOT NULL,
    fencing_token bigint NOT NULL,
    expires_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (resource_type, tenant_id, resource_id)
);

CREATE TABLE audit_events (
    id bigserial PRIMARY KEY,
    tenant_id uuid NULL REFERENCES tenants(id),
    event_id uuid NOT NULL UNIQUE,
    actor_id text NOT NULL,
    delegated_actor_id text NULL,
    action text NOT NULL,
    resource_type text NOT NULL,
    resource_id text NULL,
    outcome text NOT NULL,
    reason text NULL,
    correlation_id uuid NULL,
    source jsonb NOT NULL DEFAULT '{}'::jsonb,
    evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL
);

INSERT INTO tenants (slug, display_name) VALUES ('default', 'Default tenant');

COMMIT;
