BEGIN;

-- Progress uses the canonical agent_session_events journal.  This partial index
-- keeps replay reads bounded without creating a second transcript store.
CREATE INDEX agent_session_progress_events_idx
    ON agent_session_events (tenant_id, session_id, event_index)
    WHERE event_type = 'progress.frame';

COMMIT;
