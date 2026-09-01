BEGIN;

INSERT INTO auth_roles (name, display_name, description, built_in, created_by, updated_by)
VALUES
    (
        'session-client',
        'Session client',
        'Create and inspect sessions owned by the bound principal.',
        true,
        'migration:0069',
        'migration:0069'
    ),
    (
        'session-operator',
        'Session operator',
        'Inspect and control the session fleet inside the binding scope.',
        true,
        'migration:0069',
        'migration:0069'
    ),
    (
        'session-admin',
        'Session administrator',
        'Administer session fleets, policies and portable migrations.',
        true,
        'migration:0069',
        'migration:0069'
    )
ON CONFLICT (name) DO NOTHING;

INSERT INTO auth_role_permissions (role_name, resource_type, action, effect)
VALUES
    ('flow-author', 'agent_session', 'view', 'ALLOW'),
    ('flow-author', 'agent_session', 'create', 'ALLOW'),
    ('operator', 'agent_session', 'view', 'ALLOW'),
    ('operator', 'agent_session', 'create', 'ALLOW'),
    ('operator', 'agent_session', 'list', 'ALLOW'),
    ('operator', 'agent_session', 'manage', 'ALLOW'),
    ('operator', 'agent_session_administration', 'view', 'ALLOW'),
    ('operator', 'agent_session_policy', 'view', 'ALLOW'),
    ('session-client', 'agent_session', 'view', 'ALLOW'),
    ('session-client', 'agent_session', 'create', 'ALLOW'),
    ('session-operator', 'agent_session', 'view', 'ALLOW'),
    ('session-operator', 'agent_session', 'create', 'ALLOW'),
    ('session-operator', 'agent_session', 'list', 'ALLOW'),
    ('session-operator', 'agent_session', 'manage', 'ALLOW'),
    ('session-operator', 'agent_session_administration', 'view', 'ALLOW'),
    ('session-operator', 'agent_session_policy', 'view', 'ALLOW'),
    ('session-operator', 'agent_session_migration', 'view', 'ALLOW'),
    ('session-admin', 'agent_session', 'view', 'ALLOW'),
    ('session-admin', 'agent_session', 'create', 'ALLOW'),
    ('session-admin', 'agent_session', 'list', 'ALLOW'),
    ('session-admin', 'agent_session', 'manage', 'ALLOW'),
    ('session-admin', 'agent_session_administration', 'view', 'ALLOW'),
    ('session-admin', 'agent_session_administration', 'create', 'ALLOW'),
    ('session-admin', 'agent_session_administration', 'manage', 'ALLOW'),
    ('session-admin', 'agent_session_policy', 'view', 'ALLOW'),
    ('session-admin', 'agent_session_policy', 'create', 'ALLOW'),
    ('session-admin', 'agent_session_policy', 'manage', 'ALLOW'),
    ('session-admin', 'agent_session_migration', 'view', 'ALLOW'),
    ('session-admin', 'agent_session_migration', 'create', 'ALLOW'),
    ('session-admin', 'agent_session_migration', 'manage', 'ALLOW')
ON CONFLICT DO NOTHING;

CREATE INDEX IF NOT EXISTS executions_agent_session_fleet_keyset_idx
    ON executions (tenant_id, created_at DESC, id DESC)
    WHERE trigger_context ? 'ameshAgentSessionId';

CREATE INDEX IF NOT EXISTS agent_sessions_latest_attempt_idx
    ON agent_sessions (
        tenant_id,
        execution_id,
        attempt DESC,
        updated_at DESC,
        session_id DESC
    );

COMMIT;
