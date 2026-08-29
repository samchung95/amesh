BEGIN;

ALTER TABLE agent_sessions
    ADD COLUMN harness_adapter text NULL,
    ADD COLUMN harness_version text NULL,
    ADD COLUMN harness_protocol text NULL,
    ADD CONSTRAINT agent_sessions_harness_pin_complete_check CHECK (
        num_nonnulls(harness_adapter, harness_version, harness_protocol) IN (0, 3)
        AND (
            num_nonnulls(harness_adapter, harness_version, harness_protocol) = 0
            OR (
                length(harness_adapter) BETWEEN 1 AND 128
                AND length(harness_version) BETWEEN 1 AND 128
                AND length(harness_protocol) BETWEEN 1 AND 128
            )
        )
    );

CREATE INDEX IF NOT EXISTS executions_agent_session_service_idx
    ON executions (tenant_id, ((trigger_context->>'ameshAgentSessionId')))
    WHERE trigger_context ? 'ameshAgentSessionId';

COMMIT;
