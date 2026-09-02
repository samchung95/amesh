BEGIN;

ALTER TABLE agent_invocations
    ADD COLUMN accounting jsonb NULL,
    DROP CONSTRAINT agent_invocations_state_check,
    DROP CONSTRAINT agent_invocations_check,
    ADD CONSTRAINT agent_invocations_state_check CHECK (
        state IN ('STARTED', 'SUCCEEDED', 'FAILED', 'IN_DOUBT')
    ),
    ADD CONSTRAINT agent_invocations_completion_state_check CHECK (
        (state = 'STARTED' AND completed_at IS NULL)
        OR (state IN ('SUCCEEDED', 'FAILED', 'IN_DOUBT') AND completed_at IS NOT NULL)
    ),
    ADD CONSTRAINT agent_invocations_accounting_shape_check CHECK (
        accounting IS NULL
        OR (
            jsonb_typeof(accounting) = 'object'
            AND octet_length(accounting::text) <= 4096
        )
    );

COMMENT ON COLUMN agent_invocations.accounting IS
    'Bounded provider-neutral numeric usage and cost evidence; never raw model output or reasoning content.';

COMMIT;
