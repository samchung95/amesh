BEGIN;

CREATE TABLE admission_requests (
    request_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    resource_type text NOT NULL CHECK (resource_type IN ('EXECUTION', 'TASK')),
    resource_id uuid NOT NULL,
    policies jsonb NOT NULL DEFAULT '[]'::jsonb,
    priority integer NOT NULL DEFAULT 0,
    outcome text NOT NULL CHECK (
        outcome IN (
            'ADMITTED', 'QUEUED', 'CANCELLED', 'FAILED', 'REPLACED',
            'SKIPPED', 'RELEASED', 'EXPIRED'
        )
    ),
    reason text NOT NULL,
    limiting_policy_id text NULL,
    limiting_scope text NULL,
    limiting_bucket text NULL,
    active_count integer NOT NULL DEFAULT 0 CHECK (active_count >= 0),
    limit_value integer NULL CHECK (limit_value > 0),
    replaced_resource_id uuid NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    admitted_at timestamptz NULL,
    finished_at timestamptz NULL,
    CHECK (jsonb_typeof(policies) = 'array')
);

CREATE TABLE admission_reservations (
    reservation_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    request_id uuid NOT NULL REFERENCES admission_requests(request_id) ON DELETE CASCADE,
    resource_type text NOT NULL CHECK (resource_type IN ('EXECUTION', 'TASK')),
    resource_id uuid NOT NULL,
    policy_id text NOT NULL,
    scope text NOT NULL CHECK (
        scope IN ('GLOBAL', 'TENANT', 'NAMESPACE', 'FLOW', 'WORKER_GROUP', 'KEY')
    ),
    bucket text NOT NULL,
    lease_expires_at timestamptz NOT NULL,
    released_at timestamptz NULL,
    release_reason text NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (tenant_id, request_id, policy_id)
);

CREATE INDEX admission_requests_queue_idx
    ON admission_requests (tenant_id, priority DESC, created_at, request_id)
    WHERE outcome = 'QUEUED';

CREATE INDEX admission_requests_resource_idx
    ON admission_requests (tenant_id, resource_type, resource_id, created_at DESC);

CREATE INDEX admission_reservations_active_idx
    ON admission_reservations (resource_type, bucket, lease_expires_at)
    WHERE released_at IS NULL;

CREATE TABLE tenant_quota_usage (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    quota_type text NOT NULL CHECK (quota_type IN ('STORAGE_BYTES', 'LOG_BYTES', 'API_REQUESTS')),
    window_start timestamptz NOT NULL,
    amount bigint NOT NULL DEFAULT 0 CHECK (amount >= 0),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, quota_type, window_start)
);

CREATE OR REPLACE FUNCTION amesh_admission_active_count(
    requested_resource_type text,
    requested_bucket text
) RETURNS bigint AS $$
    SELECT count(*)
    FROM public.admission_reservations
    WHERE resource_type = requested_resource_type
      AND bucket = requested_bucket
      AND released_at IS NULL
      AND lease_expires_at > clock_timestamp()
$$ LANGUAGE sql STABLE SECURITY DEFINER
   SET search_path = pg_catalog, public;

REVOKE ALL ON FUNCTION amesh_admission_active_count(text, text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION amesh_admission_active_count(text, text) TO amesh_runtime;

GRANT SELECT, INSERT, UPDATE, DELETE ON
    admission_requests,
    admission_reservations,
    tenant_quota_usage
TO amesh_runtime;

GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_quota_usage TO amesh_tenant_admin;

ALTER TABLE admission_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE admission_requests FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON admission_requests TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE admission_reservations ENABLE ROW LEVEL SECURITY;
ALTER TABLE admission_reservations FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON admission_reservations TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE tenant_quota_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_quota_usage FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON tenant_quota_usage TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

COMMIT;
