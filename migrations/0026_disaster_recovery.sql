BEGIN;

CREATE TABLE recovery_exercises (
    id uuid PRIMARY KEY,
    checkpoint_id uuid NOT NULL REFERENCES backup_checkpoints(id),
    profile text NOT NULL,
    scheduled boolean NOT NULL DEFAULT false,
    state text NOT NULL DEFAULT 'RUNNING' CHECK (state IN ('RUNNING', 'PASSED', 'FAILED')),
    actor_id text NOT NULL,
    started_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz NULL,
    rpo_seconds double precision NULL CHECK (rpo_seconds IS NULL OR rpo_seconds >= 0),
    rto_seconds double precision NULL CHECK (rto_seconds IS NULL OR rto_seconds >= 0),
    postgres_client_version text NULL,
    restored_schema_version text NULL,
    objects_total integer NOT NULL DEFAULT 0 CHECK (objects_total >= 0),
    objects_verified integer NOT NULL DEFAULT 0 CHECK (objects_verified >= 0),
    reconciliation jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (
        jsonb_typeof(reconciliation) = 'object'
    ),
    projections jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(projections) = 'object'),
    readiness jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(readiness) = 'object'),
    unresolved_gaps jsonb NOT NULL DEFAULT '[]'::jsonb CHECK (
        jsonb_typeof(unresolved_gaps) = 'array'
    )
);

CREATE INDEX recovery_exercises_checkpoint_started_idx
    ON recovery_exercises (checkpoint_id, started_at DESC);

CREATE INDEX recovery_exercises_failed_started_idx
    ON recovery_exercises (started_at DESC)
    WHERE state = 'FAILED';

CREATE OR REPLACE FUNCTION amesh_rebuild_disposable_projections()
RETURNS TABLE (projection_name text, refreshed boolean)
LANGUAGE plpgsql
AS $$
DECLARE
    projection record;
BEGIN
    FOR projection IN
        SELECT schemaname, matviewname
        FROM pg_matviews
        WHERE schemaname = 'public'
          AND (
              matviewname LIKE 'amesh_search_%'
              OR matviewname LIKE 'amesh_analytics_%'
          )
        ORDER BY matviewname
    LOOP
        EXECUTE format(
            'REFRESH MATERIALIZED VIEW %I.%I',
            projection.schemaname,
            projection.matviewname
        );
        projection_name := projection.matviewname;
        refreshed := true;
        RETURN NEXT;
    END LOOP;
END;
$$;

GRANT SELECT, INSERT, UPDATE ON recovery_exercises TO amesh_runtime;
GRANT EXECUTE ON FUNCTION amesh_rebuild_disposable_projections() TO amesh_runtime;

COMMIT;
