"""Optional REST router for the tenant-scoped release gate service.

The application composition root supplies service and authorization dependencies.  Keeping the
router factory independent lets clients and the existing UI share the same exact command surface.
"""

from collections.abc import Awaitable, Callable, Mapping
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from amesh.domain.promotion import (
    EvidenceArtifact,
    PromotionError,
    PromotionPolicy,
    PromotionTargetKind,
)
from amesh.promotion import PromotionService


class PromotionApplyRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    expected_version: int = Field(alias="expectedVersion", ge=0)
    reason: str = Field(min_length=1, max_length=2048)
    approvals: Mapping[str, int] = Field(default_factory=dict)


class PromotionPreviewRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    approvals: Mapping[str, int] = Field(default_factory=dict)


class PromotionRollbackRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    to_revision: int = Field(alias="toRevision", ge=1)
    expected_version: int = Field(alias="expectedVersion", ge=0)
    reason: str = Field(min_length=1, max_length=2048)


class PromotionKillSwitchRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    expected_version: int = Field(alias="expectedVersion", ge=0)
    reason: str = Field(min_length=1, max_length=2048)


Authorize = Callable[[str], Awaitable[None]]
ServiceDependency = Callable[..., object]
TenantDependency = Callable[..., object]
ActorDependency = Callable[..., object]


async def _header_actor(actor_id: Annotated[str, Header(alias="X-Actor-Id")]) -> str:
    return actor_id


def build_promotion_router(
    service_dependency: ServiceDependency,
    tenant_dependency: TenantDependency,
    authorization_dependency: Callable[..., object],
    actor_dependency: ActorDependency | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/releases", tags=["releases"])
    actor_resolver = actor_dependency or _header_actor

    @router.post("/policies", response_model=PromotionPolicy, status_code=status.HTTP_201_CREATED)
    async def create_policy(
        policy: PromotionPolicy,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[PromotionService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
    ) -> PromotionPolicy:
        await check("manage")
        if policy.tenant_id != current_tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="tenant mismatch")
        return await current_service.create_policy(policy)

    @router.post("/evidence", response_model=EvidenceArtifact, status_code=status.HTTP_201_CREATED)
    async def record_evidence(
        artifact: EvidenceArtifact,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[PromotionService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
    ) -> EvidenceArtifact:
        await check("manage")
        if artifact.tenant_id != current_tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="tenant mismatch")
        return await current_service.record_evidence(artifact)

    @router.post("/policies/{policy_id}/preview")
    async def preview_policy(
        policy_id: UUID,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[PromotionService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
        request: PromotionPreviewRequest | None = None,
    ) -> object:
        await check("preview")
        policy = await current_service.get_policy(current_tenant, policy_id)
        return await current_service.preview(
            policy,
            approvals=request.approvals if request is not None else None,
        )

    @router.post("/policies/{policy_id}/apply")
    async def apply_policy(
        policy_id: UUID,
        request: PromotionApplyRequest,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[PromotionService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
        actor_id: Annotated[str, Depends(actor_resolver)],
    ) -> object:
        await check("apply")
        policy = await current_service.get_policy(current_tenant, policy_id)
        try:
            result = await current_service.apply(
                policy,
                expected_version=request.expected_version,
                actor_id=actor_id,
                reason=request.reason,
                approvals=request.approvals,
            )
        except (PromotionError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        return {"target": result.target, "event": result.event}

    @router.post("/{target_kind}/{target_key}/rollback")
    async def rollback(
        target_kind: PromotionTargetKind,
        target_key: str,
        request: PromotionRollbackRequest,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[PromotionService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
        actor_id: Annotated[str, Depends(actor_resolver)],
    ) -> object:
        await check("apply")
        try:
            result = await current_service.rollback(
                current_tenant,
                target_kind,
                target_key,
                to_revision=request.to_revision,
                expected_version=request.expected_version,
                actor_id=actor_id,
                reason=request.reason,
            )
        except (PromotionError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        return {"target": result.target, "event": result.event}

    @router.post("/{target_kind}/{target_key}/kill-switch")
    async def kill_switch(
        target_kind: PromotionTargetKind,
        target_key: str,
        request: PromotionKillSwitchRequest,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[PromotionService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
        actor_id: Annotated[str, Depends(actor_resolver)],
    ) -> object:
        await check("apply")
        try:
            result = await current_service.kill_switch(
                current_tenant,
                target_kind,
                target_key,
                expected_version=request.expected_version,
                actor_id=actor_id,
                reason=request.reason,
            )
        except (PromotionError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        return {"target": result.target, "event": result.event}

    @router.get("/{target_kind}/{target_key}")
    async def target_state(
        target_kind: PromotionTargetKind,
        target_key: str,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[PromotionService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
    ) -> object:
        await check("view")
        return await current_service.get_target(current_tenant, target_kind, target_key)

    @router.get("/{target_kind}/{target_key}/history")
    async def target_history(
        target_kind: PromotionTargetKind,
        target_key: str,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[PromotionService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
    ) -> object:
        await check("view")
        return await current_service.get_history(current_tenant, target_kind, target_key)

    return router


__all__ = [
    "PromotionApplyRequest",
    "PromotionKillSwitchRequest",
    "PromotionPreviewRequest",
    "PromotionRollbackRequest",
    "build_promotion_router",
]
