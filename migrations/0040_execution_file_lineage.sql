BEGIN;

ALTER TABLE execution_artifacts
    ADD COLUMN logical_path text NULL,
    ADD COLUMN lineage jsonb NOT NULL DEFAULT '[]'::jsonb,
    ADD CONSTRAINT execution_artifacts_logical_path_check
        CHECK (logical_path IS NULL OR (length(logical_path) BETWEEN 1 AND 4096)),
    ADD CONSTRAINT execution_artifacts_lineage_array_check
        CHECK (jsonb_typeof(lineage) = 'array');

CREATE INDEX execution_artifacts_lineage_idx
    ON execution_artifacts USING gin (lineage jsonb_path_ops);

COMMIT;
