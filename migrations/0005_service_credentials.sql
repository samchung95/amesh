BEGIN;

ALTER TABLE auth_principals
    ADD COLUMN credential_version bigint NOT NULL DEFAULT 1
        CHECK (credential_version >= 1);

CREATE TABLE auth_credentials (
    id uuid PRIMARY KEY,
    principal_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    name text NOT NULL,
    kind text NOT NULL CHECK (kind IN ('API_TOKEN', 'DERIVED_TOKEN')),
    token_hash bytea NOT NULL UNIQUE,
    scopes text[] NOT NULL,
    audience text NOT NULL,
    status text NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'SUPERSEDED', 'REVOKED')),
    expires_at timestamptz NOT NULL,
    rate_limit_per_minute integer NOT NULL CHECK (rate_limit_per_minute > 0),
    issued_credential_version bigint NOT NULL CHECK (issued_credential_version >= 1),
    parent_token_id uuid NULL REFERENCES auth_credentials(id) ON DELETE CASCADE,
    superseded_by uuid NULL REFERENCES auth_credentials(id) ON DELETE SET NULL,
    overlap_expires_at timestamptz NULL,
    last_used_at timestamptz NULL,
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    revoked_by text NULL,
    revoked_at timestamptz NULL,
    CHECK (cardinality(scopes) > 0),
    CHECK ((kind = 'DERIVED_TOKEN') = (parent_token_id IS NOT NULL)),
    CHECK (
        (status = 'SUPERSEDED') =
        (superseded_by IS NOT NULL AND overlap_expires_at IS NOT NULL)
    ),
    CHECK ((status = 'REVOKED') = (revoked_at IS NOT NULL))
);

CREATE INDEX auth_credentials_principal_status_idx
    ON auth_credentials (principal_id, status, created_at DESC);

CREATE INDEX auth_credentials_expiry_idx
    ON auth_credentials (expires_at)
    WHERE status <> 'REVOKED';

CREATE INDEX auth_credentials_parent_idx
    ON auth_credentials (parent_token_id)
    WHERE parent_token_id IS NOT NULL;

CREATE TABLE auth_credential_usage_windows (
    credential_id uuid NOT NULL REFERENCES auth_credentials(id) ON DELETE CASCADE,
    window_started_at timestamptz NOT NULL,
    request_count integer NOT NULL CHECK (request_count > 0),
    PRIMARY KEY (credential_id, window_started_at)
);

COMMIT;
