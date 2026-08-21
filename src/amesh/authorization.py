from __future__ import annotations

from dataclasses import dataclass, field

from amesh.domain import AuthorizationDecision, AuthorizationRequest, evaluate_authorization
from amesh.ports.authorization_repository import AuthorizationRepository, PolicyVersionChanged


class AuthorizationDenied(PermissionError):
    """Raised when the policy does not grant a requested operation."""

    def __init__(self, decision: AuthorizationDecision) -> None:
        super().__init__(decision.reason_code)
        self.decision = decision


@dataclass
class AuthorizationService:
    repository: AuthorizationRepository
    max_cache_entries: int = 4096
    _cached_version: int | None = None
    _cache: dict[tuple[object, ...], AuthorizationDecision] = field(default_factory=dict)

    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        if request.actor.bootstrap_admin:
            snapshot = await self.repository.load_policy_snapshot(
                request.actor.principal_id,
                expected_version=await self.repository.policy_version(),
            )
            return evaluate_authorization(request, snapshot)

        for _ in range(3):
            version = await self.repository.policy_version()
            if version != self._cached_version:
                self._cache.clear()
                self._cached_version = version
            key = (
                version,
                request.actor.principal_id,
                request.actor.credential_id,
                request.actor.credential_scopes,
                request.actor.credential_audience,
                request.tenant_id,
                request.namespace,
                request.resource_type,
                request.action,
                request.audience,
            )
            cached = self._cache.get(key)
            if cached is not None:
                return cached
            try:
                snapshot = await self.repository.load_policy_snapshot(
                    request.actor.principal_id,
                    expected_version=version,
                )
            except PolicyVersionChanged:
                continue
            decision = evaluate_authorization(request, snapshot)
            if len(self._cache) >= self.max_cache_entries:
                self._cache.clear()
            self._cache[key] = decision
            return decision
        raise PolicyVersionChanged("authorization policy changed repeatedly during evaluation")

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = await self.decide(request)
        if not decision.allowed:
            raise AuthorizationDenied(decision)
        return decision
