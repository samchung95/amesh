from __future__ import annotations

from uuid import UUID, uuid4

from amesh.authorization import AuthorizationService
from amesh.domain import (
    BUILT_IN_ROLES,
    ActorContext,
    AuthorizationPolicySnapshot,
    AuthorizationRequest,
    AuthorizationScopeType,
    PermissionAction,
    PrincipalType,
    RoleBinding,
)
from amesh.ports import PolicyVersionChanged


class PolicyRepositoryStub:
    def __init__(self, actor_id: UUID) -> None:
        self.actor_id = actor_id
        self.version = 1
        self.loads = 0
        self.binding = RoleBinding(
            principal_id=actor_id,
            principal_type=PrincipalType.USER,
            role_name="viewer",
            scope_type=AuthorizationScopeType.TENANT,
            tenant_id="tenant-a",
        )

    async def policy_version(self) -> int:
        return self.version

    async def load_policy_snapshot(
        self,
        actor_id: UUID,
        *,
        expected_version: int,
    ) -> AuthorizationPolicySnapshot:
        if expected_version != self.version:
            raise PolicyVersionChanged
        assert actor_id == self.actor_id
        self.loads += 1
        bindings = () if self.binding is None else (self.binding,)
        return AuthorizationPolicySnapshot(
            version=self.version,
            roles=BUILT_IN_ROLES,
            bindings=bindings,
        )


def test_decision_cache_is_invalidated_by_policy_version() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="user",
    )
    repository = PolicyRepositoryStub(actor.principal_id)
    service = AuthorizationService(repository)  # type: ignore[arg-type]
    request = AuthorizationRequest(
        actor=actor,
        tenant_id="tenant-a",
        resource_type="flow",
        action=PermissionAction.VIEW,
    )

    async def scenario() -> None:
        assert (await service.decide(request)).allowed
        assert (await service.decide(request)).allowed
        assert repository.loads == 1

        repository.binding = None
        repository.version += 1

        assert not (await service.decide(request)).allowed
        assert repository.loads == 2

    import asyncio

    asyncio.run(scenario())
