BEGIN;

ALTER TABLE service_instances
    DROP CONSTRAINT service_instances_state_check;

ALTER TABLE service_instances
    ADD CONSTRAINT service_instances_state_check CHECK (
        state IN ('STARTING', 'READY', 'DEGRADED', 'DRAINING', 'STOPPED')
    ),
    ADD COLUMN last_success_at timestamptz NULL,
    ADD COLUMN last_failure_at timestamptz NULL,
    ADD COLUMN consecutive_failures integer NOT NULL DEFAULT 0 CHECK (
        consecutive_failures >= 0
    ),
    ADD COLUMN last_failure text NULL CHECK (
        last_failure IS NULL OR char_length(last_failure) <= 2048
    );

COMMIT;
