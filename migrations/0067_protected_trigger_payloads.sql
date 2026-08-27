BEGIN;

ALTER TABLE trigger_occurrences
    ADD COLUMN protected_payload_key_id text NULL,
    ADD COLUMN protected_payload_context text NULL,
    ADD COLUMN protected_payload_digest text NULL
        CHECK (protected_payload_digest IS NULL
               OR protected_payload_digest ~ '^sha256:[0-9a-f]{64}$'),
    ADD COLUMN protected_payload_ciphertext bytea NULL,
    ADD CONSTRAINT trigger_occurrence_protected_payload_complete_check CHECK (
        (
            protected_payload_key_id IS NULL
            AND protected_payload_context IS NULL
            AND protected_payload_digest IS NULL
            AND protected_payload_ciphertext IS NULL
        )
        OR (
            protected_payload_key_id IS NOT NULL
            AND protected_payload_context IS NOT NULL
            AND protected_payload_digest IS NOT NULL
            AND protected_payload_ciphertext IS NOT NULL
        )
    );

COMMENT ON COLUMN trigger_occurrences.protected_payload_ciphertext IS
    'Application-encrypted recoverable trigger input; never returned by public occurrence projections.';

COMMIT;
