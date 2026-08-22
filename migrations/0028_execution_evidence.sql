BEGIN;

ALTER TABLE execution_logs
    ADD COLUMN attempt integer NOT NULL DEFAULT 1 CHECK (attempt > 0),
    ADD COLUMN worker_id uuid NULL,
    ADD COLUMN trace_id text NULL,
    ADD COLUMN source_stream text NOT NULL DEFAULT 'TASK'
        CHECK (source_stream IN ('TASK', 'STDOUT', 'STDERR', 'PLUGIN', 'SYSTEM')),
    ADD COLUMN ingested_at timestamptz NOT NULL DEFAULT clock_timestamp();

ALTER TABLE execution_metrics
    ADD COLUMN attempt integer NOT NULL DEFAULT 1 CHECK (attempt > 0),
    ADD COLUMN ingested_at timestamptz NOT NULL DEFAULT clock_timestamp();
ALTER TABLE execution_metrics DROP CONSTRAINT execution_metrics_metric_kind_check;
ALTER TABLE execution_metrics
    ADD CONSTRAINT execution_metrics_metric_kind_check
    CHECK (metric_kind IN ('COUNTER', 'GAUGE', 'TIMER', 'CUSTOM'));

CREATE TABLE execution_outputs (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    execution_id uuid NOT NULL,
    task_run_id uuid NOT NULL,
    attempt integer NOT NULL CHECK (attempt > 0),
    value jsonb NOT NULL DEFAULT '{}'::jsonb,
    size_bytes bigint NOT NULL CHECK (size_bytes >= 0),
    sensitive boolean NOT NULL DEFAULT false,
    occurred_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT execution_outputs_value_object CHECK (jsonb_typeof(value) = 'object'),
    CONSTRAINT execution_outputs_execution_fk
        FOREIGN KEY (tenant_id, execution_id)
        REFERENCES executions (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT execution_outputs_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs (tenant_id, execution_id, id) ON DELETE CASCADE,
    UNIQUE (tenant_id, task_run_id, attempt)
);

CREATE TABLE execution_artifacts (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    execution_id uuid NOT NULL,
    task_run_id uuid NOT NULL,
    attempt integer NOT NULL CHECK (attempt > 0),
    uri text NOT NULL,
    size_bytes bigint NOT NULL CHECK (size_bytes >= 0),
    media_type text NULL,
    checksum_sha256 text NULL CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$'),
    occurred_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT execution_artifacts_execution_fk
        FOREIGN KEY (tenant_id, execution_id)
        REFERENCES executions (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT execution_artifacts_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs (tenant_id, execution_id, id) ON DELETE CASCADE,
    UNIQUE (tenant_id, task_run_id, attempt, uri)
);

CREATE TABLE execution_evidence_events (
    cursor bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    event_id uuid NOT NULL,
    execution_id uuid NOT NULL,
    task_run_id uuid NULL,
    kind text NOT NULL CHECK (kind IN ('STATE', 'LOG', 'METRIC', 'OUTPUT', 'ARTIFACT')),
    event_type text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    occurred_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT execution_evidence_payload_object CHECK (jsonb_typeof(payload) = 'object'),
    CONSTRAINT execution_evidence_execution_fk
        FOREIGN KEY (tenant_id, execution_id)
        REFERENCES executions (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT execution_evidence_task_run_fk
        FOREIGN KEY (tenant_id, execution_id, task_run_id)
        REFERENCES task_runs (tenant_id, execution_id, id) ON DELETE CASCADE,
    UNIQUE (tenant_id, event_id)
);

CREATE INDEX execution_outputs_timeline_idx
    ON execution_outputs (tenant_id, execution_id, occurred_at, id);
CREATE INDEX execution_artifacts_timeline_idx
    ON execution_artifacts (tenant_id, execution_id, occurred_at, id);
CREATE INDEX execution_evidence_cursor_idx
    ON execution_evidence_events (tenant_id, execution_id, cursor);

CREATE FUNCTION amesh_capture_execution_state_evidence() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO execution_evidence_events (
        tenant_id, event_id, execution_id, task_run_id, kind,
        event_type, payload, occurred_at
    ) VALUES (
        NEW.tenant_id, NEW.event_id, NEW.execution_id, NULL, 'STATE',
        'execution.' || lower(NEW.event_type),
        jsonb_build_object(
            'entity', 'execution',
            'eventType', NEW.event_type,
            'sequence', NEW.sequence,
            'reason', NEW.reason,
            'payload', NEW.payload
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, event_id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE FUNCTION amesh_capture_task_state_evidence() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO execution_evidence_events (
        tenant_id, event_id, execution_id, task_run_id, kind,
        event_type, payload, occurred_at
    ) VALUES (
        NEW.tenant_id, NEW.event_id, NEW.execution_id, NEW.task_run_id, 'STATE',
        'task.' || lower(NEW.event_type),
        jsonb_build_object(
            'entity', 'task',
            'eventType', NEW.event_type,
            'sequence', NEW.sequence,
            'reason', NEW.reason,
            'payload', NEW.payload
        ),
        NEW.occurred_at
    ) ON CONFLICT (tenant_id, event_id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE FUNCTION amesh_capture_task_evidence() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    evidence_kind text;
    evidence_type text;
    evidence_payload jsonb;
BEGIN
    CASE TG_TABLE_NAME
        WHEN 'execution_logs' THEN
            evidence_kind := 'LOG';
            evidence_type := 'log.' || lower(NEW.level);
            evidence_payload := jsonb_build_object(
                'level', NEW.level,
                'logger', NEW.logger,
                'message', NEW.message,
                'fields', NEW.fields,
                'redacted', NEW.redacted,
                'attempt', NEW.attempt,
                'workerId', NEW.worker_id,
                'traceId', NEW.trace_id,
                'sourceStream', NEW.source_stream
            );
        WHEN 'execution_metrics' THEN
            evidence_kind := 'METRIC';
            evidence_type := 'metric.' || lower(NEW.metric_kind);
            evidence_payload := jsonb_build_object(
                'name', NEW.metric_name,
                'kind', NEW.metric_kind,
                'value', NEW.metric_value,
                'unit', NEW.unit,
                'labels', NEW.labels,
                'attempt', NEW.attempt
            );
        WHEN 'execution_outputs' THEN
            evidence_kind := 'OUTPUT';
            evidence_type := 'output.committed';
            evidence_payload := jsonb_build_object(
                'value', NEW.value,
                'sizeBytes', NEW.size_bytes,
                'sensitive', NEW.sensitive,
                'attempt', NEW.attempt
            );
        WHEN 'execution_artifacts' THEN
            evidence_kind := 'ARTIFACT';
            evidence_type := 'artifact.created';
            evidence_payload := jsonb_build_object(
                'uri', NEW.uri,
                'sizeBytes', NEW.size_bytes,
                'mediaType', NEW.media_type,
                'checksumSha256', NEW.checksum_sha256,
                'attempt', NEW.attempt
            );
        ELSE
            RAISE EXCEPTION 'unsupported evidence table %', TG_TABLE_NAME;
    END CASE;
    INSERT INTO execution_evidence_events (
        tenant_id, event_id, execution_id, task_run_id, kind,
        event_type, payload, occurred_at, ingested_at
    ) VALUES (
        NEW.tenant_id, NEW.id, NEW.execution_id, NEW.task_run_id, evidence_kind,
        evidence_type, evidence_payload, NEW.occurred_at, NEW.ingested_at
    ) ON CONFLICT (tenant_id, event_id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER execution_state_evidence_after_insert
AFTER INSERT ON execution_events
FOR EACH ROW EXECUTE FUNCTION amesh_capture_execution_state_evidence();
CREATE TRIGGER task_state_evidence_after_insert
AFTER INSERT ON task_run_events
FOR EACH ROW EXECUTE FUNCTION amesh_capture_task_state_evidence();
CREATE TRIGGER execution_log_evidence_after_insert
AFTER INSERT ON execution_logs
FOR EACH ROW EXECUTE FUNCTION amesh_capture_task_evidence();
CREATE TRIGGER execution_metric_evidence_after_insert
AFTER INSERT ON execution_metrics
FOR EACH ROW EXECUTE FUNCTION amesh_capture_task_evidence();
CREATE TRIGGER execution_output_evidence_after_insert
AFTER INSERT ON execution_outputs
FOR EACH ROW EXECUTE FUNCTION amesh_capture_task_evidence();
CREATE TRIGGER execution_artifact_evidence_after_insert
AFTER INSERT ON execution_artifacts
FOR EACH ROW EXECUTE FUNCTION amesh_capture_task_evidence();

INSERT INTO execution_evidence_events (
    tenant_id, event_id, execution_id, task_run_id, kind,
    event_type, payload, occurred_at
)
SELECT tenant_id, event_id, execution_id, NULL, 'STATE',
       'execution.' || lower(event_type),
       jsonb_build_object(
           'entity', 'execution', 'eventType', event_type,
           'sequence', sequence, 'payload', payload
       ),
       occurred_at
FROM execution_events
ON CONFLICT (tenant_id, event_id) DO NOTHING;

INSERT INTO execution_evidence_events (
    tenant_id, event_id, execution_id, task_run_id, kind,
    event_type, payload, occurred_at
)
SELECT tenant_id, event_id, execution_id, task_run_id, 'STATE',
       'task.' || lower(event_type),
       jsonb_build_object(
           'entity', 'task', 'eventType', event_type,
           'sequence', sequence, 'payload', payload
       ),
       occurred_at
FROM task_run_events
ON CONFLICT (tenant_id, event_id) DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE ON execution_outputs TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON execution_artifacts TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON execution_evidence_events TO amesh_runtime;
GRANT USAGE, SELECT ON SEQUENCE execution_evidence_events_cursor_seq TO amesh_runtime;

DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'execution_outputs',
        'execution_artifacts',
        'execution_evidence_events'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', table_name);
        EXECUTE format(
            'CREATE POLICY tenant_runtime_isolation ON %I TO amesh_runtime '
            'USING (tenant_id = amesh_current_tenant_id()) '
            'WITH CHECK (tenant_id = amesh_current_tenant_id())',
            table_name
        );
    END LOOP;
END;
$$;

COMMIT;
