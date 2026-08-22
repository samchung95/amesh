BEGIN;

CREATE TABLE realtime_events (
    cursor bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_id uuid NOT NULL,
    namespace_name text NULL,
    flow_id text NULL,
    execution_id uuid NULL,
    task_run_id uuid NULL,
    event_type text NOT NULL,
    severity text NOT NULL CHECK (severity IN ('TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR')),
    payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(payload) = 'object'),
    occurred_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (tenant_id, event_id),
    CONSTRAINT realtime_events_execution_fk
        FOREIGN KEY (tenant_id, execution_id)
        REFERENCES executions (tenant_id, id) ON DELETE CASCADE
);

CREATE INDEX realtime_events_tenant_cursor_idx ON realtime_events (tenant_id, cursor);
CREATE INDEX realtime_events_execution_cursor_idx
    ON realtime_events (tenant_id, execution_id, cursor) WHERE execution_id IS NOT NULL;
CREATE INDEX realtime_events_scope_cursor_idx
    ON realtime_events (tenant_id, namespace_name, flow_id, cursor);

CREATE TABLE webhook_subscriptions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name text NOT NULL,
    url text NOT NULL CHECK (url ~ '^https?://'),
    filters jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(filters) = 'object'),
    enabled boolean NOT NULL DEFAULT true,
    max_attempts integer NOT NULL DEFAULT 8 CHECK (max_attempts BETWEEN 1 AND 25),
    signing_version integer NOT NULL DEFAULT 1 CHECK (signing_version > 0),
    last_enqueued_cursor bigint NOT NULL DEFAULT 0 CHECK (last_enqueued_cursor >= 0),
    resource_version bigint NOT NULL DEFAULT 1 CHECK (resource_version > 0),
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (tenant_id, name)
);

CREATE TABLE webhook_deliveries (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    subscription_id uuid NOT NULL REFERENCES webhook_subscriptions(id) ON DELETE CASCADE,
    event_cursor bigint NULL,
    event_id uuid NULL,
    event_type text NOT NULL,
    event_occurred_at timestamptz NOT NULL,
    payload jsonb NOT NULL CHECK (jsonb_typeof(payload) = 'object'),
    delivery_kind text NOT NULL CHECK (delivery_kind IN ('EVENT', 'TEST', 'REPLAY')),
    original_delivery_id uuid NULL REFERENCES webhook_deliveries(id),
    signing_version integer NOT NULL CHECK (signing_version > 0),
    status text NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'DELIVERING', 'RETRY', 'DELIVERED', 'FAILED')),
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    next_attempt_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    locked_by text NULL,
    locked_until timestamptz NULL,
    response_status integer NULL,
    error_code text NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    delivered_at timestamptz NULL,
    UNIQUE (tenant_id, subscription_id, event_cursor)
);

CREATE INDEX webhook_deliveries_due_idx
    ON webhook_deliveries (tenant_id, next_attempt_at, created_at)
    WHERE status IN ('PENDING', 'RETRY', 'DELIVERING');
CREATE INDEX webhook_deliveries_history_idx
    ON webhook_deliveries (tenant_id, subscription_id, created_at DESC, id DESC);

CREATE TABLE webhook_delivery_attempts (
    delivery_id uuid NOT NULL REFERENCES webhook_deliveries(id) ON DELETE CASCADE,
    attempt integer NOT NULL CHECK (attempt > 0),
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    request_timestamp bigint NOT NULL,
    response_status integer NULL,
    outcome text NOT NULL CHECK (outcome IN ('DELIVERED', 'RETRY', 'FAILED')),
    error_code text NULL,
    attempted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    duration_ms integer NOT NULL CHECK (duration_ms >= 0),
    PRIMARY KEY (delivery_id, attempt)
);

CREATE OR REPLACE FUNCTION amesh_capture_execution_realtime() RETURNS trigger AS $$
DECLARE
    execution_namespace text;
    execution_flow text;
    event_severity text;
BEGIN
    SELECT namespace_name, flow_key
    INTO STRICT execution_namespace, execution_flow
    FROM executions
    WHERE tenant_id = NEW.tenant_id AND id = NEW.execution_id;

    event_severity := CASE
        WHEN NEW.kind = 'LOG' AND upper(COALESCE(NEW.payload ->> 'level', 'INFO'))
             IN ('TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR')
            THEN upper(NEW.payload ->> 'level')
        ELSE 'INFO'
    END;

    INSERT INTO realtime_events (
        tenant_id, event_id, namespace_name, flow_id, execution_id, task_run_id,
        event_type, severity, payload, occurred_at, ingested_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        execution_namespace,
        execution_flow,
        NEW.execution_id,
        NEW.task_run_id,
        NEW.event_type,
        event_severity,
        jsonb_build_object('source', 'execution-evidence', 'kind', NEW.kind, 'data', NEW.payload),
        NEW.occurred_at,
        NEW.ingested_at
    ) ON CONFLICT (tenant_id, event_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public;

CREATE OR REPLACE FUNCTION amesh_capture_audit_realtime() RETURNS trigger AS $$
DECLARE
    audit_execution_id uuid;
BEGIN
    audit_execution_id := CASE
        WHEN NEW.resource_type = 'execution'
         AND COALESCE(NEW.resource_id, '') ~
             '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        THEN NEW.resource_id::uuid
        ELSE NULL
    END;
    INSERT INTO realtime_events (
        tenant_id, event_id, namespace_name, flow_id, execution_id,
        event_type, severity, payload, occurred_at
    ) VALUES (
        NEW.tenant_id,
        NEW.event_id,
        NULLIF(NEW.source ->> 'namespace', ''),
        NULLIF(NEW.source ->> 'flowId', ''),
        audit_execution_id,
        'audit.' || lower(NEW.action),
        CASE WHEN upper(NEW.outcome) IN ('DENIED', 'FAILED', 'ERROR')
             THEN 'WARNING' ELSE 'INFO' END,
        jsonb_build_object(
            'source', 'audit',
            'actorId', NEW.actor_id,
            'delegatedActorId', NEW.delegated_actor_id,
            'action', NEW.action,
            'resourceType', NEW.resource_type,
            'resourceId', NEW.resource_id,
            'outcome', NEW.outcome,
            'reason', NEW.reason,
            'context', NEW.source,
            'evidence', NEW.evidence
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, event_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public;

CREATE TRIGGER execution_evidence_realtime_after_insert
AFTER INSERT ON execution_evidence_events
FOR EACH ROW EXECUTE FUNCTION amesh_capture_execution_realtime();

CREATE TRIGGER audit_realtime_after_insert
AFTER INSERT ON audit_events
FOR EACH ROW EXECUTE FUNCTION amesh_capture_audit_realtime();

INSERT INTO realtime_events (
    tenant_id, event_id, namespace_name, flow_id, execution_id, task_run_id,
    event_type, severity, payload, occurred_at, ingested_at
)
SELECT evidence.tenant_id, evidence.event_id, executions.namespace_name, executions.flow_key,
       evidence.execution_id, evidence.task_run_id, evidence.event_type,
       CASE WHEN evidence.kind = 'LOG'
             AND upper(COALESCE(evidence.payload ->> 'level', 'INFO'))
                  IN ('TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR')
            THEN upper(evidence.payload ->> 'level') ELSE 'INFO' END,
       jsonb_build_object('source', 'execution-evidence', 'kind', evidence.kind,
                          'data', evidence.payload),
       evidence.occurred_at, evidence.ingested_at
FROM execution_evidence_events AS evidence
JOIN executions
  ON executions.tenant_id = evidence.tenant_id AND executions.id = evidence.execution_id
ON CONFLICT (tenant_id, event_id) DO NOTHING;

INSERT INTO realtime_events (
    tenant_id, event_id, namespace_name, flow_id, execution_id,
    event_type, severity, payload, occurred_at
)
SELECT audit.tenant_id, audit.event_id, NULLIF(audit.source ->> 'namespace', ''),
       NULLIF(audit.source ->> 'flowId', ''),
       CASE WHEN audit.resource_type = 'execution'
                  AND COALESCE(audit.resource_id, '') ~
                      '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            THEN audit.resource_id::uuid ELSE NULL END,
       'audit.' || lower(audit.action),
       CASE WHEN upper(audit.outcome) IN ('DENIED', 'FAILED', 'ERROR')
            THEN 'WARNING' ELSE 'INFO' END,
       jsonb_build_object(
           'source', 'audit', 'actorId', audit.actor_id,
           'delegatedActorId', audit.delegated_actor_id, 'action', audit.action,
           'resourceType', audit.resource_type, 'resourceId', audit.resource_id,
           'outcome', audit.outcome, 'reason', audit.reason,
           'context', audit.source, 'evidence', audit.evidence
       ),
       audit.occurred_at
FROM audit_events AS audit
ON CONFLICT (tenant_id, event_id) DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE ON realtime_events TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON webhook_subscriptions TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON webhook_deliveries TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON webhook_delivery_attempts TO amesh_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO amesh_runtime;

ALTER TABLE realtime_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE realtime_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON realtime_events TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE webhook_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_subscriptions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON webhook_subscriptions TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_deliveries FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON webhook_deliveries TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE webhook_delivery_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_delivery_attempts FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON webhook_delivery_attempts TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
