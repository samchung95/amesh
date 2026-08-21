from __future__ import annotations

from typing import Protocol
from uuid import UUID

from amesh.domain import (
    AuthorizationPolicySnapshot,
    NamespaceAuthorizationBoundary,
    PrincipalDefinition,
    RoleBinding,
    RoleDefinition,
)


class PolicyVersionChanged(RuntimeError):
    """Raised when a policy snapshot changes while it is being loaded."""


class LastAdministratorError(RuntimeError):
    """Raised when a mutation would remove the final instance administrator."""


class AuthorizationRepository(Protocol):
    async def policy_version(self) -> int: ...

    async def load_policy_snapshot(
        self,
        actor_id: UUID,
        *,
        expected_version: int,
    ) -> AuthorizationPolicySnapshot: ...

    async def create_principal(
        self,
        principal: PrincipalDefinition,
        *,
        actor_id: str,
    ) -> PrincipalDefinition: ...

    async def list_principals(self) -> list[PrincipalDefinition]: ...

    async def add_group_member(
        self,
        group_id: UUID,
        member_id: UUID,
        *,
        actor_id: str,
    ) -> None: ...

    async def remove_group_member(
        self,
        group_id: UUID,
        member_id: UUID,
        *,
        actor_id: str,
    ) -> None: ...

    async def upsert_role(
        self,
        role: RoleDefinition,
        *,
        actor_id: str,
    ) -> RoleDefinition: ...

    async def list_roles(self) -> list[RoleDefinition]: ...

    async def create_binding(
        self,
        binding: RoleBinding,
        *,
        actor_id: str,
    ) -> RoleBinding: ...

    async def list_bindings(self) -> list[RoleBinding]: ...

    async def delete_binding(self, binding_id: UUID, *, actor_id: str) -> None: ...

    async def set_namespace_boundary(
        self,
        boundary: NamespaceAuthorizationBoundary,
        *,
        actor_id: str,
    ) -> NamespaceAuthorizationBoundary: ...
