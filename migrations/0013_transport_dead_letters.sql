BEGIN;

ALTER TABLE messages_outbox
    ADD COLUMN max_attempts integer NOT NULL DEFAULT 25 CHECK (max_attempts > 0),
    ADD COLUMN dead_lettered_at timestamptz NULL;

ALTER TABLE messages_outbox
    ADD CONSTRAINT messages_outbox_envelope_object
        CHECK (jsonb_typeof(envelope) = 'object') NOT VALID;
ALTER TABLE messages_outbox VALIDATE CONSTRAINT messages_outbox_envelope_object;

ALTER TABLE durable_work_queue
    ADD CONSTRAINT durable_work_queue_envelope_object
        CHECK (jsonb_typeof(envelope) = 'object') NOT VALID;
ALTER TABLE durable_work_queue VALIDATE CONSTRAINT durable_work_queue_envelope_object;

CREATE TABLE durable_dead_letters (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    source_type text NOT NULL CHECK (source_type IN ('QUEUE', 'OUTBOX')),
    source_id bigint NOT NULL,
    message_id uuid NOT NULL,
    lane text NOT NULL,
    partition_key text NOT NULL,
    message_type text NOT NULL,
    schema_version integer NOT NULL CHECK (schema_version > 0),
    failure_class text NOT NULL,
    payload_checksum text NOT NULL CHECK (length(payload_checksum) = 64),
    attempt_count integer NOT NULL CHECK (attempt_count > 0),
    last_error text NOT NULL,
    quarantined_at timestamptz NOT NULL DEFAULT now(),
    resolution text NOT NULL DEFAULT 'PENDING'
        CHECK (resolution IN ('PENDING', 'REPLAYED', 'DISCARDED')),
    resolved_at timestamptz NULL,
    resolved_by text NULL
);

CREATE UNIQUE INDEX durable_dead_letters_pending_source_idx
    ON durable_dead_letters (tenant_id, source_type, source_id)
    WHERE resolution = 'PENDING';
CREATE INDEX durable_dead_letters_tenant_timeline_idx
    ON durable_dead_letters (tenant_id, quarantined_at DESC, id);
CREATE INDEX messages_outbox_partition_order_idx
    ON messages_outbox (tenant_id, subject, partition_key, sequence)
    WHERE published_at IS NULL AND dead_lettered_at IS NULL;

GRANT SELECT, INSERT, UPDATE, DELETE ON durable_dead_letters TO amesh_runtime;

ALTER TABLE durable_dead_letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE durable_dead_letters FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON durable_dead_letters TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
