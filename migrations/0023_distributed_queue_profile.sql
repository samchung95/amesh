BEGIN;

ALTER TABLE durable_work_queue
    ADD COLUMN shard_key integer GENERATED ALWAYS AS (
        get_byte(digest(partition_key, 'sha256'), 0) * 256
        + get_byte(digest(partition_key, 'sha256'), 1)
    ) STORED,
    ADD COLUMN last_claimed_at timestamptz NULL;

CREATE INDEX durable_work_queue_shard_claim_idx
    ON durable_work_queue (
        tenant_id,
        lane,
        shard_key,
        priority DESC,
        available_at,
        id
    )
    WHERE state = 'READY';

COMMIT;
