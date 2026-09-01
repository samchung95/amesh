BEGIN;

ALTER TABLE agent_session_policy_revisions
    ADD COLUMN ceiling_mode text NOT NULL DEFAULT 'BOUNDED',
    ALTER COLUMN max_total_tokens DROP NOT NULL,
    ALTER COLUMN max_cost_usd DROP NOT NULL,
    ALTER COLUMN max_duration_seconds DROP NOT NULL,
    ADD CONSTRAINT agent_session_policy_ceiling_mode_check CHECK (
        ceiling_mode IN ('BOUNDED', 'PROVIDER_BOUNDED')
    ),
    ADD CONSTRAINT agent_session_policy_bounded_limits_check CHECK (
        ceiling_mode = 'PROVIDER_BOUNDED'
        OR (
            max_total_tokens IS NOT NULL
            AND max_cost_usd IS NOT NULL
            AND max_duration_seconds IS NOT NULL
        )
    );

COMMENT ON COLUMN agent_session_policy_revisions.ceiling_mode IS
    'Explicit AMESH application-ceiling mode; BOUNDED preserves legacy finite-limit behavior.';

COMMIT;
