BEGIN;

ALTER TABLE workers
    ADD COLUMN protocol_version integer NOT NULL DEFAULT 1,
    ADD COLUMN runner_types jsonb NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN capacity integer NOT NULL DEFAULT 1,
    ADD COLUMN heartbeat_progress jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN resource_usage jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN cancellation_acknowledged boolean NOT NULL DEFAULT false,
    ADD CONSTRAINT workers_protocol_version_positive CHECK (protocol_version > 0),
    ADD CONSTRAINT workers_capacity_positive CHECK (capacity > 0),
    ADD CONSTRAINT workers_runner_types_array CHECK (jsonb_typeof(runner_types) = 'array'),
    ADD CONSTRAINT workers_heartbeat_progress_object CHECK (
        jsonb_typeof(heartbeat_progress) = 'object'
    ),
    ADD CONSTRAINT workers_resource_usage_object CHECK (jsonb_typeof(resource_usage) = 'object');

ALTER TABLE task_attempts
    ADD COLUMN queue_id bigint NULL REFERENCES durable_work_queue(id),
    ADD COLUMN last_heartbeat_at timestamptz NULL,
    ADD COLUMN progress jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN resource_usage jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN cancellation_acknowledged boolean NOT NULL DEFAULT false,
    ADD CONSTRAINT task_attempts_progress_object CHECK (jsonb_typeof(progress) = 'object'),
    ADD CONSTRAINT task_attempts_resource_usage_object CHECK (
        jsonb_typeof(resource_usage) = 'object'
    );

CREATE UNIQUE INDEX task_attempts_queue_identity_idx
    ON task_attempts (tenant_id, queue_id)
    WHERE queue_id IS NOT NULL;

CREATE INDEX task_attempts_live_worker_claim_idx
    ON task_attempts (tenant_id, worker_id, lease_expires_at)
    WHERE state = 'RUNNING' AND worker_id IS NOT NULL;

COMMIT;
