from __future__ import annotations

from uuid import uuid4

import pytest

from amesh.domain import (
    BUILT_IN_ROLES,
    ActorContext,
    AuthorizationPolicySnapshot,
    AuthorizationRequest,
    AuthorizationScopeType,
    NamespaceAuthorizationBoundary,
    Permission,
    PermissionAction,
    PermissionEffect,
    PrincipalType,
    RoleBinding,
    RoleDefinition,
    evaluate_authorization,
)


def _actor() -> ActorContext:
    return ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="test-user",
    )


def _request(actor: ActorContext, **overrides: object) -> AuthorizationRequest:
    values: dict[str, object] = {
        "actor": actor,
        "tenant_id": "tenant-a",
        "namespace": "team.private.app",
        "resource_type": "flow",
        "action": PermissionAction.VIEW,
    }
    values.update(overrides)
    return AuthorizationRequest.model_validate(values)


def test_builtin_roles_are_explicit_and_viewer_is_read_only() -> None:
    roles = {role.name: role for role in BUILT_IN_ROLES}

    assert set(roles) == {
        "auditor",
        "flow-author",
        "instance-admin",
        "namespace-admin",
        "operator",
        "session-admin",
        "session-client",
        "session-operator",
        "tenant-admin",
        "viewer",
    }
    assert roles["viewer"].permissions == (
        Permission(resource_type="*", action=PermissionAction.VIEW),
        Permission(resource_type="namespace_file", action=PermissionAction.LIST),
        Permission(resource_type="namespace_file", action=PermissionAction.READ),
        Permission(resource_type="key_value", action=PermissionAction.LIST),
        Permission(resource_type="key_value", action=PermissionAction.READ),
        Permission(resource_type="secret", action=PermissionAction.LIST),
    )


def test_session_roles_map_product_capabilities_to_canonical_permissions() -> None:
    roles = {role.name: role for role in BUILT_IN_ROLES}

    assert roles["session-client"].permissions == (
        Permission(resource_type="agent_session", action=PermissionAction.VIEW),
        Permission(resource_type="agent_session", action=PermissionAction.CREATE),
    )
    assert roles["session-operator"].permissions == (
        Permission(resource_type="agent_session", action=PermissionAction.VIEW),
        Permission(resource_type="agent_session", action=PermissionAction.CREATE),
        Permission(resource_type="agent_session", action=PermissionAction.LIST),
        Permission(resource_type="agent_session", action=PermissionAction.MANAGE),
        Permission(
            resource_type="agent_session_administration",
            action=PermissionAction.VIEW,
        ),
        Permission(resource_type="agent_session_policy", action=PermissionAction.VIEW),
        Permission(resource_type="agent_session_migration", action=PermissionAction.VIEW),
    )
    assert roles["session-admin"].permissions == (
        Permission(resource_type="agent_session", action=PermissionAction.VIEW),
        Permission(resource_type="agent_session", action=PermissionAction.CREATE),
        Permission(resource_type="agent_session", action=PermissionAction.LIST),
        Permission(resource_type="agent_session", action=PermissionAction.MANAGE),
        Permission(
            resource_type="agent_session_administration",
            action=PermissionAction.VIEW,
        ),
        Permission(
            resource_type="agent_session_administration",
            action=PermissionAction.CREATE,
        ),
        Permission(
            resource_type="agent_session_administration",
            action=PermissionAction.MANAGE,
        ),
        Permission(resource_type="agent_session_policy", action=PermissionAction.VIEW),
        Permission(resource_type="agent_session_policy", action=PermissionAction.CREATE),
        Permission(resource_type="agent_session_policy", action=PermissionAction.MANAGE),
        Permission(resource_type="agent_session_migration", action=PermissionAction.VIEW),
        Permission(resource_type="agent_session_migration", action=PermissionAction.CREATE),
        Permission(resource_type="agent_session_migration", action=PermissionAction.MANAGE),
    )

    for role_name in ("session-client", "session-operator", "session-admin"):
        assert all(
            permission.action == "*" or permission.action in PermissionAction
            for permission in roles[role_name].permissions
        )


def test_legacy_author_roles_retain_execution_and_gain_session_permissions() -> None:
    roles = {role.name: role for role in BUILT_IN_ROLES}

    flow_author_permissions = set(roles["flow-author"].permissions)
    assert {
        Permission(resource_type="execution", action=PermissionAction.EXECUTE),
        Permission(resource_type="agent_session", action=PermissionAction.VIEW),
        Permission(resource_type="agent_session", action=PermissionAction.CREATE),
    } <= flow_author_permissions

    operator_permissions = set(roles["operator"].permissions)
    assert {
        Permission(resource_type="execution", action=PermissionAction.MANAGE),
        Permission(resource_type="agent_session", action=PermissionAction.LIST),
        Permission(resource_type="agent_session", action=PermissionAction.MANAGE),
        Permission(
            resource_type="agent_session_administration",
            action=PermissionAction.VIEW,
        ),
        Permission(resource_type="agent_session_policy", action=PermissionAction.VIEW),
    } <= operator_permissions


def test_tenant_binding_does_not_cross_tenants() -> None:
    actor = _actor()
    snapshot = AuthorizationPolicySnapshot(
        version=1,
        roles=BUILT_IN_ROLES,
        bindings=(
            RoleBinding(
                principal_id=actor.principal_id,
                principal_type=actor.principal_type,
                role_name="viewer",
                scope_type=AuthorizationScopeType.TENANT,
                tenant_id="tenant-a",
            ),
        ),
    )

    assert evaluate_authorization(_request(actor), snapshot).allowed
    denied = evaluate_authorization(_request(actor, tenant_id="tenant-b"), snapshot)
    assert not denied.allowed
    assert denied.reason_code == "NO_MATCHING_GRANT"


def test_tenant_role_cannot_authorize_instance_resource() -> None:
    actor = _actor()
    snapshot = AuthorizationPolicySnapshot(
        version=1,
        roles=BUILT_IN_ROLES,
        bindings=(
            RoleBinding(
                principal_id=actor.principal_id,
                principal_type=actor.principal_type,
                role_name="tenant-admin",
                scope_type=AuthorizationScopeType.TENANT,
                tenant_id="tenant-a",
            ),
        ),
    )

    assert not evaluate_authorization(_request(actor, tenant_id=None), snapshot).allowed


def test_group_binding_grants_permission_to_member() -> None:
    actor = _actor()
    group_id = uuid4()
    snapshot = AuthorizationPolicySnapshot(
        version=7,
        roles=BUILT_IN_ROLES,
        group_ids=(group_id,),
        bindings=(
            RoleBinding(
                principal_id=group_id,
                principal_type=PrincipalType.GROUP,
                role_name="operator",
                scope_type=AuthorizationScopeType.TENANT,
                tenant_id="tenant-a",
            ),
        ),
    )

    decision = evaluate_authorization(
        _request(actor, resource_type="execution", action=PermissionAction.EXECUTE),
        snapshot,
    )

    assert decision.allowed
    assert decision.policy_version == 7
    assert decision.matched_role_names == ("operator",)


def test_namespace_boundary_stops_parent_inheritance() -> None:
    actor = _actor()
    parent_binding = RoleBinding(
        principal_id=actor.principal_id,
        principal_type=actor.principal_type,
        role_name="viewer",
        scope_type=AuthorizationScopeType.NAMESPACE,
        tenant_id="tenant-a",
        namespace="team",
    )
    bounded = AuthorizationPolicySnapshot(
        version=1,
        roles=BUILT_IN_ROLES,
        bindings=(parent_binding,),
        boundaries=(
            NamespaceAuthorizationBoundary(
                tenant_id="tenant-a",
                namespace="team.private",
            ),
        ),
    )

    assert evaluate_authorization(_request(actor, namespace="team.public"), bounded).allowed
    assert not evaluate_authorization(_request(actor), bounded).allowed


def test_explicit_deny_overrides_group_and_direct_grants() -> None:
    actor = _actor()
    deny_role = RoleDefinition(
        name="blocked-flow-reader",
        display_name="Blocked flow reader",
        permissions=(
            Permission(
                resource_type="flow",
                action=PermissionAction.VIEW,
                effect=PermissionEffect.DENY,
            ),
        ),
    )
    snapshot = AuthorizationPolicySnapshot(
        version=1,
        roles=(*BUILT_IN_ROLES, deny_role),
        bindings=(
            RoleBinding(
                principal_id=actor.principal_id,
                principal_type=actor.principal_type,
                role_name="viewer",
                scope_type=AuthorizationScopeType.TENANT,
                tenant_id="tenant-a",
            ),
            RoleBinding(
                principal_id=actor.principal_id,
                principal_type=actor.principal_type,
                role_name=deny_role.name,
                scope_type=AuthorizationScopeType.NAMESPACE,
                tenant_id="tenant-a",
                namespace="team.private",
            ),
        ),
    )

    decision = evaluate_authorization(_request(actor), snapshot)

    assert not decision.allowed
    assert decision.reason_code == "EXPLICIT_DENY"
    assert decision.matched_role_names == (deny_role.name,)


def test_denial_summary_does_not_include_resource_identity() -> None:
    actor = _actor()
    request = _request(actor)

    decision = evaluate_authorization(
        request,
        AuthorizationPolicySnapshot(version=1),
    )

    assert not decision.allowed
    assert request.namespace not in decision.summary
    assert request.tenant_id not in decision.summary


@pytest.mark.parametrize(
    "principal_type",
    [PrincipalType.SERVICE_ACCOUNT, PrincipalType.WORKER, PrincipalType.PLUGIN],
)
def test_nonhuman_callers_use_the_same_server_side_policy(
    principal_type: PrincipalType,
) -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=principal_type,
        display=principal_type.value.lower(),
    )
    snapshot = AuthorizationPolicySnapshot(
        version=1,
        roles=BUILT_IN_ROLES,
        bindings=(
            RoleBinding(
                principal_id=actor.principal_id,
                principal_type=principal_type,
                role_name="viewer",
                scope_type=AuthorizationScopeType.TENANT,
                tenant_id="tenant-a",
            ),
        ),
    )

    assert evaluate_authorization(_request(actor), snapshot).allowed


def test_credential_scope_and_audience_narrow_role_grants() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.SERVICE_ACCOUNT,
        display="automation",
        credential_id=uuid4(),
        credential_scopes=("flow:view",),
        credential_audience="amesh-api",
    )
    snapshot = AuthorizationPolicySnapshot(
        version=1,
        roles=BUILT_IN_ROLES,
        bindings=(
            RoleBinding(
                principal_id=actor.principal_id,
                principal_type=actor.principal_type,
                role_name="tenant-admin",
                scope_type=AuthorizationScopeType.TENANT,
                tenant_id="tenant-a",
            ),
        ),
    )

    assert evaluate_authorization(_request(actor), snapshot).allowed
    scope_denied = evaluate_authorization(
        _request(actor, action=PermissionAction.UPDATE),
        snapshot,
    )
    assert scope_denied.reason_code == "CREDENTIAL_SCOPE_DENY"
    audience_denied = evaluate_authorization(
        _request(actor, audience="amesh-worker"),
        snapshot,
    )
    assert audience_denied.reason_code == "CREDENTIAL_AUDIENCE_MISMATCH"
