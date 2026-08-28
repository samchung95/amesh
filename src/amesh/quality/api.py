"""Optional FastAPI transport for the generic differential quality service.

The application composition root supplies authorization and the configuration adapter. Keeping the
router factory here prevents quality contracts from importing AMESH's tenant or service registry
implementation.
"""

import inspect
from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Path, status

from .differential import (
    ComparisonReport,
    DifferentialService,
    DifferentialSpec,
    Executor,
    ShadowExecutionError,
)
from .durable import DurableDifferentialService
from .repository import DifferentialConflictError, DifferentialRunBusyError

Authorize = Callable[[str, str, str], Awaitable[None] | None]
ApplicationAuthorize = Callable[[str], Awaitable[None]]
Dependency = Callable[..., object]


def build_differential_router(
    service: DifferentialService,
    executor: Executor,
    *,
    authorize: Authorize,
) -> APIRouter:
    """Build authenticated, tenant-scoped differential operations for app composition."""

    router = APIRouter(
        prefix="/api/v1/namespaces/{namespace}/differentials",
        tags=["quality"],
    )

    async def check_access(tenant_id: str, namespace: str, action: str) -> None:
        try:
            result = authorize(tenant_id, namespace, action)
            if inspect.isawaitable(result):
                await result
        except PermissionError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="not authorized",
            ) from exc

    @router.post("", response_model=ComparisonReport)
    async def run_differential(
        namespace: Annotated[str, Path(min_length=1, max_length=255)],
        spec: DifferentialSpec,
        tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")],
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    ) -> ComparisonReport:
        if spec.tenant_id != tenant_id or spec.namespace != namespace:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="differential tenant and namespace must match request context",
            )
        if idempotency_key is not None and idempotency_key != spec.idempotency_key:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Idempotency-Key does not match idempotencyKey body field",
            )
        await check_access(tenant_id, namespace, "execute")
        try:
            return service.run(spec, executor)
        except (ShadowExecutionError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

    @router.get("/{idempotency_key}", response_model=ComparisonReport)
    async def get_differential(
        namespace: Annotated[str, Path(min_length=1, max_length=255)],
        idempotency_key: Annotated[str, Path(min_length=1, max_length=512)],
        tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")],
    ) -> ComparisonReport:
        await check_access(tenant_id, namespace, "view")
        try:
            return service.get(tenant_id, namespace, idempotency_key)
        except LookupError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="differential report unavailable",
            ) from exc

    return router


def build_differential_application_router(
    service_dependency: Dependency,
    executor_dependency: Dependency,
    tenant_dependency: Dependency,
    authorization_dependency: Dependency,
    actor_dependency: Dependency,
) -> APIRouter:
    """Build differential routes using AMESH's FastAPI dependency composition.

    The direct callback factory above remains available to embedders.  This variant lets the
    application resolve tenant, authorization, service, and executor dependencies consistently
    with its other transport factories while keeping the executor provider-neutral.
    """

    router = APIRouter(
        prefix="/api/v1/namespaces/{namespace}/differentials",
        tags=["quality"],
    )

    @router.post("", response_model=ComparisonReport)
    async def run_differential(
        namespace: Annotated[str, Path(min_length=1, max_length=255)],
        spec: DifferentialSpec,
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[DurableDifferentialService, Depends(service_dependency)],
        current_executor: Annotated[Executor, Depends(executor_dependency)],
        check: Annotated[ApplicationAuthorize, Depends(authorization_dependency)],
        current_actor: Annotated[str, Depends(actor_dependency)],
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    ) -> ComparisonReport:
        if spec.tenant_id != current_tenant or spec.namespace != namespace:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="differential tenant and namespace must match request context",
            )
        if idempotency_key is not None and idempotency_key != spec.idempotency_key:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Idempotency-Key does not match idempotencyKey body field",
            )
        await check("execute")
        try:
            return await current_service.run(spec, current_executor, actor_id=current_actor)
        except (
            DifferentialConflictError,
            DifferentialRunBusyError,
            ShadowExecutionError,
            ValueError,
        ) as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

    @router.get("/{idempotency_key}", response_model=ComparisonReport)
    async def get_differential(
        namespace: Annotated[str, Path(min_length=1, max_length=255)],
        idempotency_key: Annotated[str, Path(min_length=1, max_length=512)],
        current_tenant: Annotated[str, Depends(tenant_dependency)],
        current_service: Annotated[DurableDifferentialService, Depends(service_dependency)],
        check: Annotated[ApplicationAuthorize, Depends(authorization_dependency)],
    ) -> ComparisonReport:
        await check("view")
        try:
            return await current_service.get(current_tenant, namespace, idempotency_key)
        except LookupError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="differential report unavailable",
            ) from exc

    return router
