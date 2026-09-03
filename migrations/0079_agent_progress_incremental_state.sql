BEGIN;

ALTER TABLE agent_sessions
    ADD CONSTRAINT agent_sessions_tenant_session_unique
    UNIQUE (tenant_id, session_id);

ALTER TABLE agent_session_events
    ADD CONSTRAINT agent_session_events_progress_identity_unique
    UNIQUE (tenant_id, session_id, event_index, event_id);

CREATE TABLE agent_session_progress_state (
    session_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    active_segment_id uuid NULL,
    active_segment_frame_count bigint NOT NULL DEFAULT 0
        CHECK (active_segment_frame_count >= 0),
    segment_count bigint NOT NULL DEFAULT 0 CHECK (segment_count >= 0),
    accepted_frame_count bigint NOT NULL DEFAULT 0 CHECK (accepted_frame_count >= 0),
    last_occurred_at timestamptz NULL,
    truncated_event_id uuid NULL,
    truncated_event_index bigint NULL CHECK (truncated_event_index > 0),
    UNIQUE (tenant_id, session_id),
    CHECK (
        (truncated_event_id IS NULL AND truncated_event_index IS NULL)
        OR (truncated_event_id IS NOT NULL AND truncated_event_index IS NOT NULL)
    ),
    CONSTRAINT agent_session_progress_state_session_fk
        FOREIGN KEY (tenant_id, session_id)
        REFERENCES agent_sessions (tenant_id, session_id) ON DELETE CASCADE,
    CONSTRAINT agent_session_progress_state_truncated_event_fk
        FOREIGN KEY (tenant_id, session_id, truncated_event_index, truncated_event_id)
        REFERENCES agent_session_events (tenant_id, session_id, event_index, event_id)
        ON DELETE CASCADE
);

CREATE TABLE agent_session_progress_sources (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    session_id uuid NOT NULL,
    source_id text NOT NULL CHECK (length(source_id) BETWEEN 1 AND 128),
    last_sequence bigint NOT NULL CHECK (last_sequence > 0),
    PRIMARY KEY (tenant_id, session_id, source_id),
    CONSTRAINT agent_session_progress_sources_session_fk
        FOREIGN KEY (tenant_id, session_id)
        REFERENCES agent_sessions (tenant_id, session_id) ON DELETE CASCADE
);

CREATE TABLE agent_session_progress_closed_segments (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    session_id uuid NOT NULL,
    segment_id uuid NOT NULL,
    PRIMARY KEY (tenant_id, session_id, segment_id),
    CONSTRAINT agent_session_progress_closed_segments_session_fk
        FOREIGN KEY (tenant_id, session_id)
        REFERENCES agent_sessions (tenant_id, session_id) ON DELETE CASCADE
);

CREATE TABLE agent_session_progress_timestamps (
    event_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    session_id uuid NOT NULL,
    event_index bigint NOT NULL CHECK (event_index > 0),
    frame_occurred_at timestamptz NOT NULL,
    UNIQUE (tenant_id, session_id, event_index),
    CONSTRAINT agent_session_progress_timestamps_session_fk
        FOREIGN KEY (tenant_id, session_id)
        REFERENCES agent_sessions (tenant_id, session_id) ON DELETE CASCADE,
    CONSTRAINT agent_session_progress_timestamps_event_fk
        FOREIGN KEY (tenant_id, session_id, event_index, event_id)
        REFERENCES agent_session_events (tenant_id, session_id, event_index, event_id)
        ON DELETE CASCADE
);

CREATE INDEX agent_session_progress_rate_idx
    ON agent_session_progress_timestamps (
        tenant_id, session_id, frame_occurred_at DESC, event_index DESC
    );

WITH last_events AS (
    SELECT DISTINCT ON (tenant_id, session_id)
           tenant_id, session_id, event_type, payload
    FROM agent_session_events
    ORDER BY tenant_id, session_id, event_index DESC
),
progress_summary AS (
    SELECT tenant_id,
           session_id,
           count(*) AS accepted_frame_count,
           count(DISTINCT payload->'frame'->>'segmentId')
               FILTER (WHERE payload->'frame'->>'segmentId' IS NOT NULL) AS segment_count,
           (array_agg(
               (payload->'frame'->>'occurredAt')::timestamptz
               ORDER BY event_index DESC
           ))[1] AS last_occurred_at
    FROM agent_session_events
    WHERE event_type = 'progress.frame'
    GROUP BY tenant_id, session_id
),
active_segments AS (
    SELECT tenant_id,
           session_id,
           CASE
               WHEN event_type = 'progress.frame'
                AND payload->'frame'->>'segmentId' IS NOT NULL
                AND payload->'frame'->>'status' NOT IN (
                    'COMPLETED', 'FAILED', 'CANCELLED', 'TRUNCATED'
                )
               THEN (payload->'frame'->>'segmentId')::uuid
               ELSE NULL
           END AS active_segment_id
    FROM last_events
),
truncated_events AS (
    SELECT DISTINCT ON (tenant_id, session_id)
           tenant_id, session_id, event_id, event_index
    FROM agent_session_events
    WHERE event_type = 'progress.frame'
      AND payload->'frame'->>'status' = 'TRUNCATED'
    ORDER BY tenant_id, session_id, event_index DESC
)
INSERT INTO agent_session_progress_state (
    session_id,
    tenant_id,
    active_segment_id,
    active_segment_frame_count,
    segment_count,
    accepted_frame_count,
    last_occurred_at,
    truncated_event_id,
    truncated_event_index
)
SELECT sessions.session_id,
       sessions.tenant_id,
       active_segments.active_segment_id,
       CASE
           WHEN active_segments.active_segment_id IS NULL THEN 0
           ELSE (
               SELECT count(*)
               FROM agent_session_events AS active_events
               WHERE active_events.tenant_id = sessions.tenant_id
                 AND active_events.session_id = sessions.session_id
                 AND active_events.event_type = 'progress.frame'
                 AND active_events.payload->'frame'->>'segmentId'
                     = active_segments.active_segment_id::text
           )
       END,
       COALESCE(progress_summary.segment_count, 0),
       COALESCE(progress_summary.accepted_frame_count, 0),
       progress_summary.last_occurred_at,
       truncated_events.event_id,
       truncated_events.event_index
FROM agent_sessions AS sessions
LEFT JOIN progress_summary
  ON progress_summary.tenant_id = sessions.tenant_id
 AND progress_summary.session_id = sessions.session_id
LEFT JOIN active_segments
  ON active_segments.tenant_id = sessions.tenant_id
 AND active_segments.session_id = sessions.session_id
LEFT JOIN truncated_events
  ON truncated_events.tenant_id = sessions.tenant_id
 AND truncated_events.session_id = sessions.session_id;

INSERT INTO agent_session_progress_sources (tenant_id, session_id, source_id, last_sequence)
SELECT DISTINCT ON (
           events.tenant_id,
           events.session_id,
           events.payload->'frame'->>'sourceId'
       )
       events.tenant_id,
       events.session_id,
       events.payload->'frame'->>'sourceId',
       (events.payload->'frame'->>'sourceSequence')::bigint
FROM agent_session_events AS events
WHERE events.event_type = 'progress.frame'
ORDER BY events.tenant_id,
         events.session_id,
         events.payload->'frame'->>'sourceId',
         (events.payload->'frame'->>'sourceSequence')::bigint DESC,
         events.event_index DESC;

INSERT INTO agent_session_progress_timestamps (
    tenant_id, session_id, event_id, event_index, frame_occurred_at
)
SELECT tenant_id,
       session_id,
       event_id,
       event_index,
       (payload->'frame'->>'occurredAt')::timestamptz
FROM agent_session_events
WHERE event_type = 'progress.frame';

INSERT INTO agent_session_progress_closed_segments (tenant_id, session_id, segment_id)
SELECT DISTINCT events.tenant_id,
       events.session_id,
       (events.payload->'frame'->>'segmentId')::uuid
FROM agent_session_events AS events
JOIN agent_session_progress_state AS progress_state
  ON progress_state.tenant_id = events.tenant_id
 AND progress_state.session_id = events.session_id
WHERE events.event_type = 'progress.frame'
  AND events.payload->'frame'->>'segmentId' IS NOT NULL
  AND (events.payload->'frame'->>'segmentId')::uuid
      IS DISTINCT FROM progress_state.active_segment_id;

ALTER TABLE agent_session_progress_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_session_progress_state FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_session_progress_state TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE agent_session_progress_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_session_progress_sources FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_session_progress_sources TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE agent_session_progress_closed_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_session_progress_closed_segments FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_session_progress_closed_segments TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

ALTER TABLE agent_session_progress_timestamps ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_session_progress_timestamps FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_runtime_isolation ON agent_session_progress_timestamps TO amesh_runtime
    USING (tenant_id = amesh_current_tenant_id())
    WITH CHECK (tenant_id = amesh_current_tenant_id());

GRANT SELECT, INSERT, UPDATE ON
    agent_session_progress_state,
    agent_session_progress_sources
TO amesh_runtime;
GRANT SELECT, INSERT ON agent_session_progress_closed_segments TO amesh_runtime;
GRANT SELECT, INSERT ON agent_session_progress_timestamps TO amesh_runtime;

COMMIT;
