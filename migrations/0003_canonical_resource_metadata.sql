BEGIN;

ALTER TABLE tenants
    ADD COLUMN labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN annotations jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN created_by text NOT NULL DEFAULT 'system',
    ADD COLUMN updated_by text NOT NULL DEFAULT 'system',
    ADD COLUMN lifecycle text NOT NULL DEFAULT 'ACTIVE'
        CHECK (lifecycle IN ('ACTIVE', 'ARCHIVED', 'TOMBSTONED')),
    ADD COLUMN archived_at timestamptz NULL,
    ADD COLUMN deleted_at timestamptz NULL;

ALTER TABLE namespaces
    ADD COLUMN labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN annotations jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN created_by text NOT NULL DEFAULT 'system',
    ADD COLUMN updated_by text NOT NULL DEFAULT 'system',
    ADD COLUMN lifecycle text NOT NULL DEFAULT 'ACTIVE'
        CHECK (lifecycle IN ('ACTIVE', 'ARCHIVED', 'TOMBSTONED')),
    ADD COLUMN archived_at timestamptz NULL,
    ADD COLUMN deleted_at timestamptz NULL;

ALTER TABLE flows
    ADD COLUMN labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN annotations jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN created_by text NOT NULL DEFAULT 'system',
    ADD COLUMN updated_by text NOT NULL DEFAULT 'system',
    ADD COLUMN lifecycle text NOT NULL DEFAULT 'ACTIVE'
        CHECK (lifecycle IN ('ACTIVE', 'ARCHIVED', 'TOMBSTONED')),
    ADD COLUMN archived_at timestamptz NULL,
    ADD COLUMN deleted_at timestamptz NULL;

ALTER TABLE executions
    ADD COLUMN annotations jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN created_by text NOT NULL DEFAULT 'system',
    ADD COLUMN updated_by text NOT NULL DEFAULT 'system',
    ADD COLUMN lifecycle text NOT NULL DEFAULT 'ACTIVE'
        CHECK (lifecycle IN ('ACTIVE', 'ARCHIVED', 'TOMBSTONED')),
    ADD COLUMN archived_at timestamptz NULL,
    ADD COLUMN deleted_at timestamptz NULL;

ALTER TABLE workers
    ADD COLUMN annotations jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN resource_version bigint NOT NULL DEFAULT 1,
    ADD COLUMN created_by text NOT NULL DEFAULT 'system',
    ADD COLUMN updated_by text NOT NULL DEFAULT 'system',
    ADD COLUMN lifecycle text NOT NULL DEFAULT 'ACTIVE'
        CHECK (lifecycle IN ('ACTIVE', 'ARCHIVED', 'TOMBSTONED')),
    ADD COLUMN archived_at timestamptz NULL,
    ADD COLUMN deleted_at timestamptz NULL,
    ADD COLUMN created_at timestamptz NOT NULL DEFAULT now(),
    ADD COLUMN updated_at timestamptz NOT NULL DEFAULT now();

COMMIT;
