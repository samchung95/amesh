BEGIN;

CREATE TABLE promotion_policies (
    policy_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    target_kind text NOT NULL CHECK (target_kind IN ('WORKFLOW', 'AGENT')),
    target_key text NOT NULL,
    target_revision bigint NOT NULL CHECK (target_revision > 0),
    configuration_digest text NOT NULL CHECK (configuration_digest ~ '^sha256:[0-9a-f]{64}$'),
    policy_digest text NOT NULL CHECK (policy_digest ~ '^sha256:[0-9a-f]{64}$'),
    policy jsonb NOT NULL CHECK (jsonb_typeof(policy) = 'object'),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (tenant_id, target_kind, target_key, policy_digest)
);

CREATE INDEX promotion_policies_target_idx
    ON promotion_policies (tenant_id, target_kind, target_key, target_revision, created_at DESC);

CREATE TABLE promotion_evidence (
    evidence_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    kind text NOT NULL CHECK (kind IN ('TEST', 'ASSERTION', 'DIFFERENTIAL', 'HEALTH', 'BUDGET', 'APPROVAL')),
    evidence_key text NOT NULL,
    evidence_digest text NOT NULL CHECK (evidence_digest ~ '^sha256:[0-9a-f]{64}$'),
    configuration_digest text NOT NULL CHECK (configuration_digest ~ '^sha256:[0-9a-f]{64}$'),
    passed boolean NOT NULL,
    captured_at timestamptz NOT NULL,
    expires_at timestamptz NULL,
    details jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(details) = 'object'),
    UNIQUE (tenant_id, evidence_digest),
    CHECK (expires_at IS NULL OR expires_at > captured_at)
);

CREATE INDEX promotion_evidence_lookup_idx
    ON promotion_evidence (tenant_id, kind, evidence_key, configuration_digest, captured_at DESC);

CREATE TABLE release_targets (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    target_kind text NOT NULL CHECK (target_kind IN ('WORKFLOW', 'AGENT')),
    target_key text NOT NULL,
    active_revision bigint NULL CHECK (active_revision IS NULL OR active_revision > 0),
    active_configuration_digest text NULL
        CHECK (active_configuration_digest IS NULL OR active_configuration_digest ~ '^sha256:[0-9a-f]{64}$'),
    state text NOT NULL CHECK (state IN ('ACTIVE', 'KILLED')),
    version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, target_kind, target_key),
    CHECK ((state = 'ACTIVE' AND active_revision IS NOT NULL AND active_configuration_digest IS NOT NULL)
           OR state = 'KILLED')
);

CREATE TABLE release_history (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    target_kind text NOT NULL CHECK (target_kind IN ('WORKFLOW', 'AGENT')),
    target_key text NOT NULL,
    action text NOT NULL CHECK (action IN ('PROMOTE', 'ROLLBACK', 'KILL_SWITCH')),
    from_revision bigint NULL CHECK (from_revision IS NULL OR from_revision > 0),
    to_revision bigint NULL CHECK (to_revision IS NULL OR to_revision > 0),
    to_configuration_digest text NULL
        CHECK (to_configuration_digest IS NULL OR to_configuration_digest ~ '^sha256:[0-9a-f]{64}$'),
    gate_digest text NULL CHECK (gate_digest IS NULL OR gate_digest ~ '^sha256:[0-9a-f]{64}$'),
    actor_id text NOT NULL,
    reason text NOT NULL CHECK (length(reason) BETWEEN 1 AND 2048),
    version bigint NOT NULL CHECK (version > 0),
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (tenant_id, target_kind, target_key)
        REFERENCES release_targets (tenant_id, target_kind, target_key)
);

CREATE INDEX release_history_target_idx
    ON release_history (tenant_id, target_kind, target_key, version DESC);

CREATE OR REPLACE FUNCTION amesh_enqueue_promotion_event() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    tenant_slug text;
BEGIN
    SELECT slug INTO STRICT tenant_slug FROM tenants WHERE id = NEW.tenant_id;
    IF TG_TABLE_NAME = 'promotion_policies' THEN
        INSERT INTO messages_outbox (tenant_id, message_id, subject, partition_key, envelope, available_at)
        VALUES (
            NEW.tenant_id, NEW.policy_id, 'promotion-policies',
            'release:' || NEW.target_kind::text || ':' || NEW.target_key,
            jsonb_build_object(
                'message_id', NEW.policy_id, 'message_type', 'PromotionPolicyStored',
                'schema_version', 1, 'tenant_id', tenant_slug,
                'partition_key', 'release:' || NEW.target_kind::text || ':' || NEW.target_key,
                'produced_at', clock_timestamp(),
                'payload', jsonb_build_object('policy_id', NEW.policy_id, 'policy_digest', NEW.policy_digest)
            ),
            clock_timestamp()
        ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
        RETURN NEW;
    END IF;

    IF TG_TABLE_NAME = 'promotion_evidence' THEN
        INSERT INTO messages_outbox (tenant_id, message_id, subject, partition_key, envelope, available_at)
        VALUES (
            NEW.tenant_id, NEW.evidence_id, 'promotion-evidence', 'evidence:' || NEW.evidence_key,
            jsonb_build_object(
                'message_id', NEW.evidence_id, 'message_type', 'PromotionEvidenceStored',
                'schema_version', 1, 'tenant_id', tenant_slug,
                'partition_key', 'evidence:' || NEW.evidence_key,
                'produced_at', clock_timestamp(),
                'payload', jsonb_build_object('evidence_id', NEW.evidence_id, 'evidence_digest', NEW.evidence_digest)
            ),
            clock_timestamp()
        ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
        RETURN NEW;
    END IF;

    INSERT INTO messages_outbox (tenant_id, message_id, subject, partition_key, envelope, available_at)
    VALUES (
        NEW.tenant_id, NEW.event_id, 'release-history',
        'release:' || NEW.target_kind::text || ':' || NEW.target_key,
        jsonb_build_object(
            'message_id', NEW.event_id, 'message_type', 'ReleaseActionRecorded',
            'schema_version', 1, 'tenant_id', tenant_slug,
            'partition_key', 'release:' || NEW.target_kind::text || ':' || NEW.target_key,
            'produced_at', clock_timestamp(),
            'payload', jsonb_build_object('event_id', NEW.event_id, 'action', NEW.action, 'version', NEW.version)
        ),
        clock_timestamp()
    ) ON CONFLICT (tenant_id, message_id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER promotion_policy_outbox AFTER INSERT ON promotion_policies
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_promotion_event();
CREATE TRIGGER promotion_evidence_outbox AFTER INSERT ON promotion_evidence
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_promotion_event();
CREATE TRIGGER release_history_outbox AFTER INSERT ON release_history
FOR EACH ROW EXECUTE FUNCTION amesh_enqueue_promotion_event();

GRANT SELECT, INSERT ON promotion_policies, promotion_evidence TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE ON release_targets TO amesh_runtime;
GRANT SELECT, INSERT ON release_history TO amesh_runtime;

ALTER TABLE promotion_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE promotion_policies FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON promotion_policies TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());
ALTER TABLE promotion_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE promotion_evidence FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON promotion_evidence TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());
ALTER TABLE release_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE release_targets FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON release_targets TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());
ALTER TABLE release_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE release_history FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON release_history TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
