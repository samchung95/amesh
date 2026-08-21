BEGIN;

CREATE TABLE backup_checkpoints (
    id uuid PRIMARY KEY,
    database_lsn pg_lsn NOT NULL,
    object_manifest_uri text NOT NULL,
    object_manifest_checksum text NOT NULL
        CHECK (object_manifest_checksum ~ '^[0-9a-f]{64}$'),
    schema_version text NOT NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX backup_checkpoints_created_idx
    ON backup_checkpoints (created_at DESC, id DESC);

COMMIT;
