from __future__ import annotations

from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from .identity import NamespaceId, NaturalId, TenantSlug, new_runtime_id
from .resources import ResourceMetadata


class PrincipalType(StrEnum):
    USER = "USER"
    GROUP = "GROUP"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    WORKER = "WORKER"
    PLUGIN = "PLUGIN"
    SYSTEM = "SYSTEM"


class PermissionAction(StrEnum):
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    USE = "use"


class PermissionEffect(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class AuthorizationScopeType(StrEnum):
    INSTANCE = "INSTANCE"
    TENANT = "TENANT"
    NAMESPACE = "NAMESPACE"


def _validate_resource_type(value: str) -> str:
    if value == "*":
        return value
    if not value.replace("_", "").replace("-", "").isalnum():
        raise ValueError("resource type must be '*' or an alphanumeric identifier")
    return value


ResourceType = Annotated[
    str,
    Field(min_length=1, max_length=128),
    AfterValidator(_validate_resource_type),
]


class ActorContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    principal_id: UUID
    principal_type: PrincipalType
    display: str = Field(min_length=1, max_length=255)
    bootstrap_admin: bool = False
    credential_id: UUID | None = None
    credential_scopes: tuple[str, ...] = ("*:*",)
    credential_audience: str = "amesh-api"


class PrincipalDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=new_runtime_id)
    principal_type: PrincipalType
    handle: NaturalId
    display_name: str = Field(min_length=1, max_length=255)
    enabled: bool = True
    metadata: ResourceMetadata = Field(default_factory=ResourceMetadata)

    @model_validator(mode="after")
    def reject_system_principals(self) -> PrincipalDefinition:
        if self.principal_type is PrincipalType.SYSTEM:
            raise ValueError("system principals are runtime-owned and cannot be administered")
        return self


class Permission(BaseModel):
    model_config = ConfigDict(frozen=True)

    resource_type: ResourceType
    action: PermissionAction | str
    effect: PermissionEffect = PermissionEffect.ALLOW

    @model_validator(mode="after")
    def validate_action(self) -> Permission:
        if self.action != "*" and self.action not in PermissionAction:
            raise ValueError("permission action must be '*' or a canonical action")
        return self

    def matches(self, resource_type: str, action: PermissionAction) -> bool:
        return self.resource_type in {"*", resource_type} and self.action in {"*", action}


class RoleDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: NaturalId
    display_name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4096)
    built_in: bool = False
    permissions: tuple[Permission, ...] = ()


class RoleBinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=new_runtime_id)
    principal_id: UUID
    principal_type: PrincipalType
    role_name: NaturalId
    scope_type: AuthorizationScopeType
    tenant_id: TenantSlug | None = None
    namespace: NamespaceId | None = None

    @model_validator(mode="after")
    def validate_scope(self) -> RoleBinding:
        if self.scope_type is AuthorizationScopeType.INSTANCE:
            if self.tenant_id is not None or self.namespace is not None:
                raise ValueError("instance binding cannot declare tenant or namespace")
        elif self.scope_type is AuthorizationScopeType.TENANT:
            if self.tenant_id is None or self.namespace is not None:
                raise ValueError("tenant binding requires only tenant_id")
        elif self.tenant_id is None or self.namespace is None:
            raise ValueError("namespace binding requires tenant_id and namespace")
        return self


class NamespaceAuthorizationBoundary(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant_id: TenantSlug
    namespace: NamespaceId


class AuthorizationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    actor: ActorContext
    tenant_id: TenantSlug | None = None
    namespace: NamespaceId | None = None
    resource_type: ResourceType
    action: PermissionAction
    audience: str = "amesh-api"


class AuthorizationPolicySnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: int = Field(ge=1)
    roles: tuple[RoleDefinition, ...] = ()
    bindings: tuple[RoleBinding, ...] = ()
    group_ids: tuple[UUID, ...] = ()
    boundaries: tuple[NamespaceAuthorizationBoundary, ...] = ()


class AuthorizationDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    allowed: bool
    reason_code: str
    summary: str
    policy_version: int = Field(ge=1)
    matched_role_names: tuple[str, ...] = ()


INSTANCE_ADMIN_ROLE = "instance-admin"


BUILT_IN_ROLES: tuple[RoleDefinition, ...] = (
    RoleDefinition(
        name=INSTANCE_ADMIN_ROLE,
        display_name="Instance administrator",
        description="Full instance authority.",
        built_in=True,
        permissions=(Permission(resource_type="*", action="*"),),
    ),
    RoleDefinition(
        name="tenant-admin",
        display_name="Tenant administrator",
        description="Full authority inside the binding tenant.",
        built_in=True,
        permissions=(Permission(resource_type="*", action="*"),),
    ),
    RoleDefinition(
        name="namespace-admin",
        display_name="Namespace administrator",
        description="Full authority inside the binding namespace subtree.",
        built_in=True,
        permissions=(Permission(resource_type="*", action="*"),),
    ),
    RoleDefinition(
        name="flow-author",
        display_name="Flow author",
        description="Author flows and start or inspect executions.",
        built_in=True,
        permissions=tuple(
            Permission(resource_type="flow", action=action)
            for action in (
                PermissionAction.VIEW,
                PermissionAction.CREATE,
                PermissionAction.UPDATE,
                PermissionAction.DELETE,
                PermissionAction.USE,
            )
        )
        + tuple(
            Permission(resource_type="execution", action=action)
            for action in (
                PermissionAction.VIEW,
                PermissionAction.CREATE,
                PermissionAction.EXECUTE,
            )
        ),
    ),
    RoleDefinition(
        name="operator",
        display_name="Operator",
        description="Inspect flows and operate executions.",
        built_in=True,
        permissions=(
            Permission(resource_type="flow", action=PermissionAction.VIEW),
            Permission(resource_type="execution", action=PermissionAction.VIEW),
            Permission(resource_type="execution", action=PermissionAction.CREATE),
            Permission(resource_type="execution", action=PermissionAction.EXECUTE),
            Permission(resource_type="execution", action=PermissionAction.MANAGE),
            Permission(resource_type="worker", action=PermissionAction.VIEW),
        ),
    ),
    RoleDefinition(
        name="viewer",
        display_name="Viewer",
        description="Read-only access inside the binding scope.",
        built_in=True,
        permissions=(Permission(resource_type="*", action=PermissionAction.VIEW),),
    ),
)


def evaluate_authorization(
    request: AuthorizationRequest,
    snapshot: AuthorizationPolicySnapshot,
) -> AuthorizationDecision:
    if request.actor.bootstrap_admin:
        return AuthorizationDecision(
            allowed=True,
            reason_code="BOOTSTRAP_ADMIN",
            summary="development bootstrap administrator",
            policy_version=snapshot.version,
            matched_role_names=(INSTANCE_ADMIN_ROLE,),
        )

    from .credentials import credential_scope_allows

    if request.actor.credential_audience != request.audience:
        return AuthorizationDecision(
            allowed=False,
            reason_code="CREDENTIAL_AUDIENCE_MISMATCH",
            summary="the credential audience does not match this service",
            policy_version=snapshot.version,
        )
    if not credential_scope_allows(
        request.actor.credential_scopes,
        request.resource_type,
        request.action,
    ):
        return AuthorizationDecision(
            allowed=False,
            reason_code="CREDENTIAL_SCOPE_DENY",
            summary="the credential does not include the requested resource action",
            policy_version=snapshot.version,
        )

    role_by_name = {role.name: role for role in snapshot.roles}
    subject_ids = {request.actor.principal_id, *snapshot.group_ids}
    applicable_roles: set[str] = set()
    allowed_roles: set[str] = set()
    denied_roles: set[str] = set()

    for binding in snapshot.bindings:
        if binding.principal_id not in subject_ids:
            continue
        if not _binding_applies(binding, request, snapshot.boundaries):
            continue
        role = role_by_name.get(binding.role_name)
        if role is None:
            continue
        applicable_roles.add(role.name)
        for permission in role.permissions:
            if not permission.matches(request.resource_type, request.action):
                continue
            if permission.effect is PermissionEffect.DENY:
                denied_roles.add(role.name)
            else:
                allowed_roles.add(role.name)

    if denied_roles:
        return AuthorizationDecision(
            allowed=False,
            reason_code="EXPLICIT_DENY",
            summary="an explicit deny overrides matching grants",
            policy_version=snapshot.version,
            matched_role_names=tuple(sorted(denied_roles)),
        )
    if allowed_roles:
        return AuthorizationDecision(
            allowed=True,
            reason_code="ROLE_GRANT",
            summary="a role grants the requested resource action",
            policy_version=snapshot.version,
            matched_role_names=tuple(sorted(allowed_roles)),
        )
    return AuthorizationDecision(
        allowed=False,
        reason_code="NO_MATCHING_GRANT",
        summary="no role grants the requested resource action in this scope",
        policy_version=snapshot.version,
        matched_role_names=tuple(sorted(applicable_roles)),
    )


def _binding_applies(
    binding: RoleBinding,
    request: AuthorizationRequest,
    boundaries: tuple[NamespaceAuthorizationBoundary, ...],
) -> bool:
    if binding.scope_type is AuthorizationScopeType.INSTANCE:
        return True
    if request.tenant_id is None or binding.tenant_id != request.tenant_id:
        return False
    if binding.scope_type is AuthorizationScopeType.TENANT:
        return True
    if request.namespace is None or binding.namespace is None:
        return False
    if not _is_namespace_ancestor(binding.namespace, request.namespace):
        return False
    return not any(
        boundary.tenant_id == request.tenant_id
        and boundary.namespace != binding.namespace
        and _is_namespace_ancestor(binding.namespace, boundary.namespace)
        and _is_namespace_ancestor(boundary.namespace, request.namespace)
        for boundary in boundaries
    )


def _is_namespace_ancestor(parent: str, child: str) -> bool:
    return child == parent or child.startswith(f"{parent}.")
