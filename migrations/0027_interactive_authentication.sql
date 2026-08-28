BEGIN;

CREATE TABLE auth_local_credentials (
    principal_id uuid PRIMARY KEY REFERENCES auth_principals(id) ON DELETE CASCADE,
    password_hash text NOT NULL,
    failed_attempts integer NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0),
    locked_until timestamptz NULL,
    password_changed_at timestamptz NOT NULL DEFAULT now(),
    last_authenticated_at timestamptz NULL,
    created_by text NOT NULL,
    updated_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE auth_browser_sessions (
    id uuid PRIMARY KEY,
    principal_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    provider text NOT NULL,
    token_hash bytea NOT NULL,
    previous_token_hash bytea NULL,
    previous_token_valid_until timestamptz NULL,
    csrf_hash bytea NOT NULL,
    status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'REVOKED')),
    issued_credential_version bigint NOT NULL CHECK (issued_credential_version >= 1),
    created_at timestamptz NOT NULL,
    last_seen_at timestamptz NOT NULL,
    idle_expires_at timestamptz NOT NULL,
    absolute_expires_at timestamptz NOT NULL,
    rotated_at timestamptz NOT NULL,
    revoked_at timestamptz NULL,
    revoked_by text NULL,
    CHECK (idle_expires_at <= absolute_expires_at),
    CHECK (created_at < absolute_expires_at),
    CHECK ((previous_token_hash IS NULL) = (previous_token_valid_until IS NULL)),
    CHECK ((status = 'REVOKED') = (revoked_at IS NOT NULL))
);

CREATE UNIQUE INDEX auth_browser_sessions_token_idx
    ON auth_browser_sessions (token_hash);

CREATE UNIQUE INDEX auth_browser_sessions_previous_token_idx
    ON auth_browser_sessions (previous_token_hash)
    WHERE previous_token_hash IS NOT NULL;

CREATE INDEX auth_browser_sessions_principal_active_idx
    ON auth_browser_sessions (principal_id, absolute_expires_at)
    WHERE status = 'ACTIVE';

CREATE INDEX auth_browser_sessions_expiry_idx
    ON auth_browser_sessions (LEAST(idle_expires_at, absolute_expires_at))
    WHERE status = 'ACTIVE';

CREATE TABLE auth_login_rate_windows (
    source_hash bytea NOT NULL,
    window_started_at timestamptz NOT NULL,
    request_count integer NOT NULL CHECK (request_count > 0),
    PRIMARY KEY (source_hash, window_started_at)
);

COMMIT;
