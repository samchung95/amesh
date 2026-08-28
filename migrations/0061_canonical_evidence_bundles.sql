BEGIN;

CREATE TABLE execution_evidence_bundles (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    execution_id uuid NOT NULL,
    schema_version text NOT NULL CHECK (schema_version ~ '^[0-9]+\.[0-9]+$'),
    bundle_digest text NOT NULL CHECK (bundle_digest ~ '^sha256:[0-9a-f]{64}$'),
    bundle jsonb NOT NULL CHECK (jsonb_typeof(bundle) = 'object'),
    created_at timestamptz NOT NULL,
    stored_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, execution_id),
    CONSTRAINT execution_evidence_bundles_execution_fk
        FOREIGN KEY (tenant_id, execution_id)
        REFERENCES executions (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT execution_evidence_bundles_digest_unique
        UNIQUE (tenant_id, bundle_digest)
);

CREATE INDEX execution_evidence_bundles_timeline_idx
    ON execution_evidence_bundles (tenant_id, created_at, execution_id);

CREATE FUNCTION amesh_enqueue_evidence_bundle() RETURNS trigger
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
        NEW.execution_id,
        'execution-evidence-bundles',
        'execution:' || NEW.execution_id::text,
        jsonb_build_object(
            'message_id', NEW.execution_id,
            'message_type', 'ExecutionEvidenceBundleStored',
            'schema_version', 1,
            'tenant_id', tenant_slug,
            'partition_key', 'execution:' || NEW.execution_id::text,
            'produced_at', NEW.stored_at,
            'payload', jsonb_build_object(
                'execution_id', NEW.execution_id,
                'schema_version', NEW.schema_version,
                'bundle_digest', NEW.bundle_digest
            )
        ),
        NEW.stored_at
    ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER execution_evidence_bundle_outbox
AFTER INSERT ON execution_evidence_bundles
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_evidence_bundle();

GRANT SELECT, INSERT ON execution_evidence_bundles TO amesh_runtime;

ALTER TABLE execution_evidence_bundles ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_evidence_bundles FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON execution_evidence_bundles TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
