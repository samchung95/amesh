BEGIN;

ALTER TABLE agent_invocations
    ADD COLUMN continuation_provider_id text NULL,
    ADD COLUMN continuation_provider_revision text NULL,
    ADD COLUMN continuation_key_id text NULL,
    ADD COLUMN continuation_token_digest text NULL
        CHECK (continuation_token_digest IS NULL
               OR continuation_token_digest ~ '^sha256:[0-9a-f]{64}$'),
    ADD COLUMN continuation_ciphertext bytea NULL,
    ADD CONSTRAINT agent_invocations_continuation_complete_check CHECK (
        (
            continuation_provider_id IS NULL
            AND continuation_provider_revision IS NULL
            AND continuation_key_id IS NULL
            AND continuation_token_digest IS NULL
            AND continuation_ciphertext IS NULL
        )
        OR (
            kind = 'MODEL'
            AND state = 'SUCCEEDED'
            AND continuation_provider_id IS NOT NULL
            AND continuation_provider_revision IS NOT NULL
            AND continuation_key_id IS NOT NULL
            AND continuation_token_digest IS NOT NULL
            AND continuation_ciphertext IS NOT NULL
        )
    );

COMMENT ON COLUMN agent_invocations.continuation_ciphertext IS
    'Application-encrypted opaque provider continuation; never returned by public invocation projections.';

COMMIT;
