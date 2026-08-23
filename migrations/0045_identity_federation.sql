BEGIN;

CREATE TABLE auth_federated_identities (
    provider_id text NOT NULL,
    subject text NOT NULL,
    principal_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    normalized_email text NOT NULL,
    last_authenticated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (provider_id, subject),
    UNIQUE (principal_id),
    UNIQUE (normalized_email)
);

CREATE TABLE auth_federation_states (
    state_hash bytea PRIMARY KEY,
    provider_id text NOT NULL,
    protocol text NOT NULL CHECK (protocol IN ('oidc', 'saml')),
    request_id text NULL,
    nonce text NULL,
    code_verifier text NULL,
    tenant_slug text NULL,
    return_to text NOT NULL,
    expires_at timestamptz NOT NULL,
    consumed_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK ((protocol = 'oidc') = (nonce IS NOT NULL AND code_verifier IS NOT NULL))
);

CREATE INDEX auth_federation_states_expiry_idx
    ON auth_federation_states (expires_at)
    WHERE consumed_at IS NULL;

CREATE TABLE auth_federation_replays (
    provider_id text NOT NULL,
    assertion_id text NOT NULL,
    expires_at timestamptz NOT NULL,
    accepted_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (provider_id, assertion_id)
);

CREATE TABLE auth_federation_group_memberships (
    provider_id text NOT NULL,
    principal_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    group_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (provider_id, principal_id, group_id)
);

CREATE TABLE auth_scim_resources (
    provider_id text NOT NULL,
    resource_type text NOT NULL CHECK (resource_type IN ('User', 'Group')),
    resource_name text NOT NULL,
    external_id text NULL,
    principal_id uuid NOT NULL REFERENCES auth_principals(id) ON DELETE CASCADE,
    version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (provider_id, resource_type, principal_id),
    UNIQUE (provider_id, resource_type, resource_name),
    UNIQUE (provider_id, resource_type, external_id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON auth_federated_identities TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON auth_federation_states TO amesh_runtime;
GRANT SELECT, INSERT, DELETE ON auth_federation_replays TO amesh_runtime;
GRANT SELECT, INSERT, DELETE ON auth_federation_group_memberships TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON auth_scim_resources TO amesh_runtime;

COMMIT;
