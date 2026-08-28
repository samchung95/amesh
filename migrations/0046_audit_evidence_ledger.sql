BEGIN;

CREATE TABLE audit_retention_policies (
    tenant_id uuid PRIMARY KEY REFERENCES tenants(id),
    retention_days integer NOT NULL DEFAULT 365 CHECK (retention_days BETWEEN 1 AND 36500),
    updated_by text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE audit_legal_holds (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    name text NOT NULL CHECK (length(name) BETWEEN 1 AND 128),
    reason text NOT NULL CHECK (length(reason) BETWEEN 1 AND 2048),
    starts_at timestamptz NOT NULL,
    ends_at timestamptz NULL,
    active boolean NOT NULL DEFAULT true,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    released_by text NULL,
    released_at timestamptz NULL,
    CHECK (ends_at IS NULL OR ends_at > starts_at),
    CHECK ((active AND released_by IS NULL AND released_at IS NULL) OR NOT active)
);

CREATE INDEX audit_legal_holds_tenant_active_range_idx
    ON audit_legal_holds (tenant_id, active, starts_at, ends_at);

CREATE TABLE audit_chain_anchors (
    tenant_id uuid PRIMARY KEY REFERENCES tenants(id),
    last_purged_event_id bigint NULL,
    previous_hash text NULL CHECK (previous_hash IS NULL OR previous_hash ~ '^[0-9a-f]{64}$'),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

INSERT INTO audit_chain_anchors (tenant_id)
SELECT id FROM tenants
ON CONFLICT (tenant_id) DO NOTHING;

ALTER TABLE audit_events
    ADD COLUMN trace_id uuid NULL,
    ADD COLUMN previous_hash text NULL,
    ADD COLUMN event_hash text NULL,
    ADD COLUMN retention_until timestamptz NULL;

CREATE OR REPLACE FUNCTION amesh_redact_audit_json(input jsonb) RETURNS jsonb
LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE
AS $$
DECLARE
    result jsonb;
BEGIN
    IF input IS NULL THEN
        RETURN '{}'::jsonb;
    END IF;
    IF jsonb_typeof(input) = 'object' THEN
        SELECT COALESCE(
            jsonb_object_agg(
                key,
                CASE
                    WHEN lower(regexp_replace(key, '[-_ ]', '', 'g')) ~
                        '(password|secret|token|authorization|credential|assertion|apikey|privatekey)'
                    THEN to_jsonb('[REDACTED]'::text)
                    ELSE amesh_redact_audit_json(value)
                END
            ),
            '{}'::jsonb
        )
        INTO result
        FROM jsonb_each(input);
        RETURN result;
    END IF;
    IF jsonb_typeof(input) = 'array' THEN
        SELECT COALESCE(jsonb_agg(amesh_redact_audit_json(value)), '[]'::jsonb)
        INTO result
        FROM jsonb_array_elements(input);
        RETURN result;
    END IF;
    RETURN input;
END;
$$;

CREATE OR REPLACE FUNCTION amesh_compute_audit_hash(input audit_events) RETURNS text
LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$
    SELECT encode(
        digest(
            convert_to(
                (
                    to_jsonb(input)
                    - 'id'
                    - 'event_hash'
                    - 'retention_until'
                )::text,
                'UTF8'
            ),
            'sha256'
        ),
        'hex'
    )
$$;

UPDATE audit_events
SET source = amesh_redact_audit_json(source),
    evidence = amesh_redact_audit_json(evidence),
    reason = COALESCE(reason, CASE WHEN outcome = 'SUCCESS' THEN 'completed' ELSE 'unspecified' END),
    correlation_id = COALESCE(correlation_id, event_id),
    trace_id = COALESCE(
        CASE
            WHEN source ->> 'traceId' ~
                '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            THEN (source ->> 'traceId')::uuid
            ELSE NULL
        END,
        correlation_id,
        event_id
    ),
    retention_until = occurred_at + interval '365 days';

DO $$
DECLARE
    tenant_row record;
    event_row record;
    prior_hash text;
    computed_hash text;
BEGIN
    FOR tenant_row IN SELECT id FROM tenants ORDER BY id LOOP
        prior_hash := NULL;
        FOR event_row IN
            SELECT id FROM audit_events
            WHERE tenant_id = tenant_row.id
            ORDER BY id
        LOOP
            UPDATE audit_events
            SET previous_hash = prior_hash
            WHERE id = event_row.id;
            SELECT amesh_compute_audit_hash(audit_events)
            INTO computed_hash
            FROM audit_events
            WHERE id = event_row.id;
            UPDATE audit_events
            SET event_hash = computed_hash
            WHERE id = event_row.id;
            prior_hash := computed_hash;
        END LOOP;
    END LOOP;
END;
$$;

ALTER TABLE audit_events
    ALTER COLUMN reason SET NOT NULL,
    ALTER COLUMN correlation_id SET NOT NULL,
    ALTER COLUMN trace_id SET NOT NULL,
    ALTER COLUMN event_hash SET NOT NULL,
    ALTER COLUMN retention_until SET NOT NULL;

ALTER TABLE audit_events
    ADD CONSTRAINT audit_events_previous_hash_format
        CHECK (previous_hash IS NULL OR previous_hash ~ '^[0-9a-f]{64}$'),
    ADD CONSTRAINT audit_events_event_hash_format
        CHECK (event_hash ~ '^[0-9a-f]{64}$');

CREATE OR REPLACE FUNCTION amesh_prepare_audit_event() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    prior_hash text;
    policy_days integer;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtextextended(NEW.tenant_id::text, 504));
    NEW.source := amesh_redact_audit_json(NEW.source);
    NEW.evidence := amesh_redact_audit_json(NEW.evidence);
    NEW.reason := COALESCE(
        NEW.reason,
        CASE WHEN NEW.outcome = 'SUCCESS' THEN 'completed' ELSE 'unspecified' END
    );
    NEW.correlation_id := COALESCE(NEW.correlation_id, NEW.event_id);
    NEW.trace_id := COALESCE(
        NEW.trace_id,
        CASE
            WHEN NEW.source ->> 'traceId' ~
                '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            THEN (NEW.source ->> 'traceId')::uuid
            ELSE NULL
        END,
        NEW.correlation_id
    );
    SELECT retention_days INTO policy_days
    FROM audit_retention_policies
    WHERE tenant_id = NEW.tenant_id;
    NEW.retention_until := COALESCE(
        NEW.retention_until,
        NEW.occurred_at + make_interval(days => COALESCE(policy_days, 365))
    );
    SELECT events.event_hash INTO prior_hash
    FROM audit_events AS events
    WHERE events.tenant_id = NEW.tenant_id
    ORDER BY events.id DESC
    LIMIT 1;
    IF prior_hash IS NULL THEN
        SELECT anchors.previous_hash INTO prior_hash
        FROM audit_chain_anchors AS anchors
        WHERE anchors.tenant_id = NEW.tenant_id;
    END IF;
    NEW.previous_hash := prior_hash;
    NEW.event_hash := amesh_compute_audit_hash(NEW);
    RETURN NEW;
END;
$$;

CREATE TRIGGER audit_events_prepare_before_insert
BEFORE INSERT ON audit_events
FOR EACH ROW EXECUTE FUNCTION amesh_prepare_audit_event();

CREATE TABLE audit_export_receipts (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    artifact_kind text NOT NULL CHECK (artifact_kind IN ('AUDIT', 'COMPLIANCE')),
    destination text NOT NULL CHECK (destination IN ('FILE', 'OBJECT_STORAGE')),
    format text NOT NULL,
    event_count integer NOT NULL CHECK (event_count >= 0),
    checksum_sha256 text NOT NULL CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$'),
    signature text NOT NULL,
    object_uri text NULL,
    filters jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX audit_export_receipts_tenant_created_idx
    ON audit_export_receipts (tenant_id, created_at DESC);

CREATE TABLE compliance_evidence_records (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    category text NOT NULL CHECK (category IN (
        'ACCESS_REVIEW', 'CHANGE_EVIDENCE', 'BACKUP_RESTORE',
        'VULNERABILITY', 'INCIDENT', 'PROVENANCE'
    )),
    title text NOT NULL CHECK (length(title) BETWEEN 1 AND 255),
    source_name text NOT NULL CHECK (length(source_name) BETWEEN 1 AND 512),
    occurred_at timestamptz NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    checksum_sha256 text NOT NULL CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$'),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX compliance_evidence_tenant_category_occurred_idx
    ON compliance_evidence_records (tenant_id, category, occurred_at DESC);

ALTER TABLE audit_retention_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_retention_policies FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON audit_retention_policies TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE audit_legal_holds ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_legal_holds FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON audit_legal_holds TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE audit_chain_anchors ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_chain_anchors FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON audit_chain_anchors TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE audit_export_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_export_receipts FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON audit_export_receipts TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE compliance_evidence_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_evidence_records FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON compliance_evidence_records TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE, DELETE ON
    audit_retention_policies,
    audit_legal_holds,
    audit_chain_anchors,
    audit_export_receipts,
    compliance_evidence_records
TO amesh_runtime;

GRANT SELECT ON audit_retention_policies, audit_chain_anchors TO amesh_tenant_admin;

COMMIT;
