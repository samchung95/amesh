"""Inert API composition root with a lazy compatibility application."""

from __future__ import annotations

import importlib
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from copy import copy
from types import ModuleType
from typing import TYPE_CHECKING, Any, cast

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute, request_response
from starlette.applications import Starlette

from amesh import __version__
from amesh.api.compatibility import COMPATIBILITY_OWNERS

if TYPE_CHECKING:
    from amesh.api.dependencies import ApiProviderContainer, ApiProviderFactory

_default_application: FastAPI | None = None


def _build_factory_router(name: str) -> APIRouter:
    from amesh.api.dependencies import (
        get_differential_actor,
        get_differential_authorizer,
        get_differential_executor,
        get_differential_service,
        get_model_engine_account_service,
        get_model_engine_actor,
        get_model_engine_authorizer,
        get_promotion_actor,
        get_promotion_authorizer,
        get_promotion_service,
        require_tenant_context,
    )

    if name == "promotion":
        from amesh.api.promotion import build_promotion_router

        return build_promotion_router(
            get_promotion_service,
            require_tenant_context,
            get_promotion_authorizer,
            get_promotion_actor,
        )
    if name == "model_engines":
        from amesh.api.model_engines import build_model_engine_router

        return build_model_engine_router(
            service_dependency=get_model_engine_account_service,
            tenant_dependency=require_tenant_context,
            authorization_dependency=get_model_engine_authorizer,
            actor_dependency=get_model_engine_actor,
        )
    if name == "differential":
        from amesh.quality.api import build_differential_application_router

        return build_differential_application_router(
            get_differential_service,
            get_differential_executor,
            require_tenant_context,
            get_differential_authorizer,
            get_differential_actor,
        )
    raise ValueError(f"unknown API router factory: {name}")


def _feature_router(module_name: str, attribute: str) -> APIRouter:
    module = importlib.import_module(f"amesh.api.routers.{module_name}")
    return cast(APIRouter, getattr(module, attribute))


def _install_feature_router(application: FastAPI, router: APIRouter) -> None:
    for source_route in router.routes:
        route = copy(source_route)
        if isinstance(route, APIRoute):
            route.dependency_overrides_provider = application
            route.app = request_response(route.get_route_handler())
        application.router.routes.append(route)


def _build_mcp_application(providers: ApiProviderContainer) -> Starlette:
    from amesh.api.dependencies import (
        get_agent_resource_repository,
        get_authorization_service,
        get_credential_service,
        get_repository,
    )
    from amesh.config import get_settings
    from amesh.mcp_server import create_amesh_mcp_application, create_amesh_mcp_server

    with providers.activate():
        settings = get_settings()
        base_url = settings.network_external_base_url or "http://localhost:8000"
        server = create_amesh_mcp_server(
            get_credential_service(),
            get_repository(),
            get_agent_resource_repository(),
            get_authorization_service(),
            base_url=base_url,
        )
    return create_amesh_mcp_application(server, base_url=base_url)


def _install_mcp_routes(application: FastAPI, mcp_application: Starlette) -> None:
    previous_routes = tuple(getattr(application.state, "amesh_mcp_routes", ()))
    insertion_index = next(
        (
            index
            for index, route in enumerate(application.router.routes)
            if any(route is previous_route for previous_route in previous_routes)
        ),
        len(application.router.routes),
    )
    if previous_routes:
        application.router.routes[:] = [
            route
            for route in application.router.routes
            if not any(route is previous_route for previous_route in previous_routes)
        ]
    else:
        for index, route in enumerate(application.router.routes):
            if getattr(route, "name", None) == "web":
                insertion_index = index
                break
    installed_routes = []
    for source_route in mcp_application.routes:
        route = copy(source_route)
        route_app = getattr(route, "app", None)
        if route_app is not None:
            for middleware in reversed(mcp_application.user_middleware):
                route_app = middleware.cls(route_app, *middleware.args, **middleware.kwargs)
            route.__dict__["app"] = route_app
        installed_routes.append(route)
    mcp_routes = tuple(installed_routes)
    application.router.routes[insertion_index:insertion_index] = mcp_routes
    application.state.amesh_mcp_routes = mcp_routes
    application.state.amesh_mcp_routes_installed = True


@asynccontextmanager
async def _application_lifespan(application: FastAPI) -> AsyncIterator[None]:
    provider_factory = cast(
        "ApiProviderFactory",
        application.state.amesh_provider_factory,
    )
    providers = provider_factory()
    application.state.amesh_provider_container = providers
    try:
        mcp_application = _build_mcp_application(providers)
        application.state.amesh_mcp_application = mcp_application
        _install_mcp_routes(application, mcp_application)
        async with mcp_application.router.lifespan_context(mcp_application):
            yield
    finally:
        try:
            await providers.close()
        finally:
            del application.state.amesh_provider_container


def create_application(
    *,
    provider_factory: ApiProviderFactory | None = None,
) -> FastAPI:
    """Build the declarative HTTP application without constructing runtime services."""

    from amesh.api.dependencies import ApiProviderContainer, install_provider_scope
    from amesh.api.http import install_http_handlers
    from amesh.api.routers.manifest import ROUTE_SEQUENCE
    from amesh.frontend import SpaStaticFiles, find_frontend_dist

    application = FastAPI(
        title="AMESH",
        version=__version__,
        description=(
            "Clean-room durable workflow MVP with validated flow management, "
            "execution control, webhook triggers and execution logs."
        ),
        lifespan=_application_lifespan,
    )
    application.state.amesh_provider_factory = provider_factory or ApiProviderContainer
    install_http_handlers(application)
    install_provider_scope(application)
    for kind, module_name, attribute in ROUTE_SEQUENCE:
        if kind == "feature":
            _install_feature_router(application, _feature_router(module_name, attribute))
        else:
            application.include_router(_build_factory_router(module_name))

    frontend_dist = find_frontend_dist()
    if frontend_dist is not None:
        application.mount("/", SpaStaticFiles(directory=frontend_dist, html=True), name="web")
    return application


def get_default_application() -> FastAPI:
    """Return the legacy process-wide ASGI application, creating it on explicit access."""

    global _default_application
    if _default_application is None:
        _default_application = create_application()
    return _default_application


def _compatibility_value(name: str) -> Any:
    if name == "app":
        return get_default_application()
    owner = COMPATIBILITY_OWNERS.get(name)
    if owner is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(importlib.import_module(owner), name)


def _set_compatibility_value(name: str, value: Any) -> bool:
    if name == "app":
        global _default_application
        _default_application = cast(FastAPI, value)
        return True
    owner = COMPATIBILITY_OWNERS.get(name)
    if owner is None:
        return False
    owner_module = importlib.import_module(owner)
    targets = [
        module
        for module_name in set(COMPATIBILITY_OWNERS.values())
        if (module := sys.modules.get(module_name)) is not None and name in vars(module)
    ]
    if owner_module not in targets:
        targets.append(owner_module)
    for target in targets:
        setattr(target, name, value)
    return True


class _CompatibilityApplicationModule(ModuleType):
    """Preserve legacy symbol and monkeypatch behavior without eager feature imports."""

    def __getattr__(self, name: str) -> Any:
        return _compatibility_value(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if not _set_compatibility_value(name, value):
            super().__setattr__(name, value)

    def __dir__(self) -> list[str]:
        return sorted(set(super().__dir__()) | set(COMPATIBILITY_OWNERS) | {"app"})


sys.modules[__name__].__class__ = _CompatibilityApplicationModule
