"""Authorized account control-plane routes for subscription-backed model engines.

The composition root supplies manager factories and request dependencies.  The service owns the
small per-binding manager cache so an interactive login process remains attached across requests.
No provider credential or engine home path crosses this module's public response boundary.
"""

import logging
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Annotated, Literal
from urllib.parse import parse_qsl, urlsplit

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from amesh.ports.model_engines import (
    EngineAccountStatus,
    EngineLoginStart,
    ModelEngineAccountManager,
)

LOGGER = logging.getLogger(__name__)


class ModelEngineCatalogEntry(BaseModel):
    """Safe metadata for one account-manager adapter."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    adapter: str = Field(min_length=1, max_length=128)
    revision: str = Field(min_length=1, max_length=64)
    display_name: str = Field(alias="displayName", min_length=1, max_length=255)
    login_modes: tuple[Literal["browser", "device"], ...] = Field(
        alias="loginModes",
        min_length=1,
    )


class ModelEngineCatalog(BaseModel):
    """Versioned projection of supported subscription account adapters."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    version: str = Field(default="1", min_length=1, max_length=32)
    engines: tuple[ModelEngineCatalogEntry, ...]


class ModelEngineAccountStatusResponse(EngineAccountStatus):
    """Namespace binding plus the port's safe account status projection."""

    adapter: str = Field(min_length=1, max_length=128)
    engine_ref: str = Field(alias="engineRef", min_length=1, max_length=512)


class ModelEngineLoginStartResponse(EngineLoginStart):
    """Namespace binding plus the port's safe user-action projection."""

    adapter: str = Field(min_length=1, max_length=128)
    engine_ref: str = Field(alias="engineRef", min_length=1, max_length=512)


class ModelEngineLoginRequest(BaseModel):
    """Select the documented browser or device authorization flow."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    mode: Literal["browser", "device"] = "browser"


class ModelEngineLogoutResponse(BaseModel):
    """Safe acknowledgement for a local account logout command."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    adapter: str = Field(min_length=1, max_length=128)
    engine_ref: str = Field(alias="engineRef", min_length=1, max_length=512)
    status: Literal["logged_out"] = "logged_out"
    action_required: bool = Field(default=False, alias="actionRequired")


class ModelEngineAccountError(RuntimeError):
    """Base class for safe account-operation failures."""


class UnknownModelEngineAdapter(ModelEngineAccountError):
    """No manager is registered for the requested adapter."""


class ModelEngineInvalidRequest(ModelEngineAccountError):
    """The provider rejected an account operation's input or state."""


class ModelEngineUnavailable(ModelEngineAccountError):
    """The account runtime could not be reached or supervised."""


class ModelEngineConflict(ModelEngineAccountError):
    """The account runtime returned a non-transient protocol/state failure."""


ManagerFactory = Callable[[str, str], ModelEngineAccountManager]
AuditDependency = Callable[..., object]
ServiceDependency = Callable[..., object]
TenantDependency = Callable[..., object]
Authorize = Callable[[str], Awaitable[None]]
ActorDependency = Callable[..., object]


SUPPORTED_MODEL_ENGINES: tuple[ModelEngineCatalogEntry, ...] = (
    ModelEngineCatalogEntry(
        adapter="openai-codex-app-server",
        revision="1.0.0",
        displayName="OpenAI Codex App Server",
        loginModes=("browser", "device"),
    ),
    ModelEngineCatalogEntry(
        adapter="github-copilot-cli",
        revision="1.0.0",
        displayName="GitHub Copilot CLI",
        loginModes=("browser", "device"),
    ),
)


class ModelEngineAccountService:
    """Provider-neutral account service with one cached manager per tenant binding."""

    def __init__(
        self,
        manager_factories: Mapping[str, ManagerFactory],
        *,
        audit_repository: object | None = None,
        catalog: Sequence[ModelEngineCatalogEntry] = SUPPORTED_MODEL_ENGINES,
    ) -> None:
        self._manager_factories = dict(manager_factories)
        self._catalog = ModelEngineCatalog(engines=tuple(catalog))
        self._audit_repository = audit_repository
        self._managers: dict[tuple[str, str, str, str], ModelEngineAccountManager] = {}

    def catalog(self) -> ModelEngineCatalog:
        """Return safe metadata without touching an engine process."""

        return self._catalog

    async def status(
        self,
        tenant_id: str,
        *,
        namespace: str,
        adapter: str,
        engine_ref: str,
        actor_id: str,
    ) -> ModelEngineAccountStatusResponse:
        manager = self._manager_for(tenant_id, namespace, adapter, engine_ref)
        try:
            observed = await manager.status(
                tenant_id,
                refresh_token=False,
                include_rate_limits=True,
                include_usage=True,
            )
            account = EngineAccountStatus.model_validate(observed)
            account = account.model_copy(
                update={
                    "rate_limits": _safe_mapping(account.rate_limits),
                    "usage": _safe_mapping(account.usage),
                }
            )
        except Exception as exc:
            await self._audit(
                tenant_id,
                actor_id=actor_id,
                namespace=namespace,
                adapter=adapter,
                engine_ref=engine_ref,
                action="status",
                outcome="ERROR",
            )
            raise _map_adapter_error(exc) from exc
        await self._audit(
            tenant_id,
            actor_id=actor_id,
            namespace=namespace,
            adapter=adapter,
            engine_ref=engine_ref,
            action="status",
            outcome="ACTION_REQUIRED" if account.action_required else "SUCCESS",
        )
        return ModelEngineAccountStatusResponse(
            adapter=adapter,
            engineRef=engine_ref,
            **account.model_dump(mode="python", by_alias=False),
        )

    async def login_start(
        self,
        tenant_id: str,
        *,
        namespace: str,
        adapter: str,
        engine_ref: str,
        mode: str,
        actor_id: str,
    ) -> ModelEngineLoginStartResponse:
        manager = self._manager_for(tenant_id, namespace, adapter, engine_ref)
        try:
            started = await manager.login_start(tenant_id, mode=mode)
            login = EngineLoginStart.model_validate(started)
        except Exception as exc:
            await self._audit(
                tenant_id,
                actor_id=actor_id,
                namespace=namespace,
                adapter=adapter,
                engine_ref=engine_ref,
                action="login_start",
                outcome="ERROR",
            )
            raise _map_adapter_error(exc) from exc
        await self._audit(
            tenant_id,
            actor_id=actor_id,
            namespace=namespace,
            adapter=adapter,
            engine_ref=engine_ref,
            action="login_start",
            outcome="ACTION_REQUIRED" if login.action_required else "SUCCESS",
        )
        login = login.model_copy(
            update={
                "auth_url": _safe_web_url(login.auth_url),
                "verification_url": _safe_web_url(login.verification_url),
            }
        )
        return ModelEngineLoginStartResponse(
            adapter=adapter,
            engineRef=engine_ref,
            **login.model_dump(mode="python", by_alias=False),
        )

    async def logout(
        self,
        tenant_id: str,
        *,
        namespace: str,
        adapter: str,
        engine_ref: str,
        actor_id: str,
    ) -> ModelEngineLogoutResponse:
        manager = self._manager_for(tenant_id, namespace, adapter, engine_ref)
        try:
            await manager.logout(tenant_id)
        except Exception as exc:
            await self._audit(
                tenant_id,
                actor_id=actor_id,
                namespace=namespace,
                adapter=adapter,
                engine_ref=engine_ref,
                action="logout",
                outcome="ERROR",
            )
            raise _map_adapter_error(exc) from exc
        await self._audit(
            tenant_id,
            actor_id=actor_id,
            namespace=namespace,
            adapter=adapter,
            engine_ref=engine_ref,
            action="logout",
            outcome="SUCCESS",
        )
        return ModelEngineLogoutResponse(adapter=adapter, engineRef=engine_ref)

    async def close(self) -> None:
        """Close cached managers when the application lifecycle ends."""

        managers = tuple(self._managers.values())
        self._managers.clear()
        for manager in managers:
            close = getattr(manager, "close", None)
            if callable(close):
                await close()

    def _manager_for(
        self,
        tenant_id: str,
        namespace: str,
        adapter: str,
        engine_ref: str,
    ) -> ModelEngineAccountManager:
        factory = self._manager_factories.get(adapter)
        if factory is None:
            raise UnknownModelEngineAdapter("model engine adapter is not supported")
        key = (tenant_id, namespace, adapter, engine_ref)
        manager = self._managers.get(key)
        if manager is not None:
            return manager
        try:
            manager = factory(namespace, engine_ref)
        except Exception as exc:
            raise ModelEngineUnavailable("model engine account runtime is unavailable") from exc
        self._managers[key] = manager
        return manager

    async def _audit(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        namespace: str,
        adapter: str,
        engine_ref: str,
        action: str,
        outcome: str,
    ) -> None:
        repository = self._audit_repository
        if repository is None:
            return
        record = getattr(repository, "record_model_engine_account_action", None)
        if not callable(record):
            return
        try:
            await record(
                tenant_id,
                actor_id=actor_id,
                namespace=namespace,
                adapter=adapter,
                engine_ref=engine_ref,
                action=action,
                outcome=outcome,
            )
        except Exception:
            LOGGER.exception("model engine account audit write failed")


def _map_adapter_error(error: Exception) -> ModelEngineAccountError:
    if isinstance(error, ModelEngineAccountError):
        return error
    if isinstance(error, ValueError):
        return ModelEngineInvalidRequest("model engine account request is invalid")
    if isinstance(error, (TimeoutError, OSError, ConnectionError)):
        return ModelEngineUnavailable("model engine account runtime is unavailable")
    return ModelEngineConflict("model engine account operation was rejected")


_SENSITIVE_STATUS_KEY_PARTS = (
    "secret",
    "credential",
    "cookie",
    "password",
    "home",
    "path",
    "file",
)


def _safe_mapping(value: Mapping[str, object] | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {
        str(key): safe_value
        for key, raw in value.items()
        if not _is_sensitive_status_key(str(key))
        and (safe_value := _safe_status_value(raw)) is not None
    }


def _is_sensitive_status_key(key: str) -> bool:
    normalized = key.casefold()
    if any(part in normalized for part in _SENSITIVE_STATUS_KEY_PARTS):
        return True
    compact = normalized.replace("_", "").replace("-", "")
    return any(
        marker in compact
        for marker in ("accesstoken", "refreshtoken", "idtoken", "bearertoken", "apitoken")
    )


def _safe_status_value(value: object) -> object | None:
    if isinstance(value, Mapping):
        return _safe_mapping(value)
    if isinstance(value, list):
        return [
            safe_value for item in value if (safe_value := _safe_status_value(item)) is not None
        ]
    if isinstance(value, str):
        normalized = value.casefold()
        if value.startswith(("\\\\", "/")) or (
            len(value) > 2 and value[1] == ":" and value[2] in "\\/"
        ):
            return None
        if any(part in normalized for part in ("refresh_token", "access_token", "client_secret")):
            return None
    return value


def _safe_web_url(value: str | None) -> str | None:
    if value is None:
        return None
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return None
    if any(
        _is_sensitive_status_key(key) for key, _ in parse_qsl(parsed.query, keep_blank_values=True)
    ):
        return None
    return value


async def _default_actor(actor_id: Annotated[str | None, Header(alias="X-Actor-Id")] = None) -> str:
    return actor_id or "api"


def _actor_id(actor: object) -> str:
    if isinstance(actor, str) and actor:
        return actor
    principal_id = getattr(actor, "principal_id", None)
    if principal_id is not None:
        return str(principal_id)
    return "api"


def _raise_account_http_error(error: ModelEngineAccountError) -> None:
    if isinstance(error, UnknownModelEngineAdapter):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="model engine adapter unavailable"
        )
    if isinstance(error, ModelEngineInvalidRequest):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="invalid model engine account request",
        )
    if isinstance(error, ModelEngineUnavailable):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="model engine account runtime unavailable",
        )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="model engine account operation rejected"
    )


def build_model_engine_router(
    *,
    service_dependency: ServiceDependency,
    tenant_dependency: TenantDependency,
    authorization_dependency: Callable[..., object],
    actor_dependency: ActorDependency | None = None,
) -> APIRouter:
    """Build the namespace-scoped account router for application composition."""

    router = APIRouter(
        prefix="/api/v1/namespaces/{namespace}/model-engines",
        tags=["model-engines"],
    )
    actor_resolver = actor_dependency or _default_actor

    @router.get("/catalog", response_model=ModelEngineCatalog)
    async def catalog(
        namespace: str,
        service: Annotated[ModelEngineAccountService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
    ) -> ModelEngineCatalog:
        del namespace
        await check("view")
        return service.catalog()

    @router.get(
        "/{adapter}/{engine_ref}/status",
        response_model=ModelEngineAccountStatusResponse,
    )
    async def account_status(
        namespace: str,
        adapter: str,
        engine_ref: str,
        tenant_id: Annotated[str, Depends(tenant_dependency)],
        service: Annotated[ModelEngineAccountService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
        actor: Annotated[object, Depends(actor_resolver)],
    ) -> ModelEngineAccountStatusResponse:
        await check("view")
        try:
            return await service.status(
                tenant_id,
                namespace=namespace,
                adapter=adapter,
                engine_ref=engine_ref,
                actor_id=_actor_id(actor),
            )
        except ModelEngineAccountError as exc:
            _raise_account_http_error(exc)
        raise AssertionError("unreachable")

    @router.post(
        "/{adapter}/{engine_ref}/login",
        response_model=ModelEngineLoginStartResponse,
    )
    async def account_login_start(
        namespace: str,
        adapter: str,
        engine_ref: str,
        request: ModelEngineLoginRequest,
        tenant_id: Annotated[str, Depends(tenant_dependency)],
        service: Annotated[ModelEngineAccountService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
        actor: Annotated[object, Depends(actor_resolver)],
    ) -> ModelEngineLoginStartResponse:
        await check("manage")
        try:
            return await service.login_start(
                tenant_id,
                namespace=namespace,
                adapter=adapter,
                engine_ref=engine_ref,
                mode=request.mode,
                actor_id=_actor_id(actor),
            )
        except ModelEngineAccountError as exc:
            _raise_account_http_error(exc)
        raise AssertionError("unreachable")

    @router.post(
        "/{adapter}/{engine_ref}/logout",
        response_model=ModelEngineLogoutResponse,
    )
    async def account_logout(
        namespace: str,
        adapter: str,
        engine_ref: str,
        tenant_id: Annotated[str, Depends(tenant_dependency)],
        service: Annotated[ModelEngineAccountService, Depends(service_dependency)],
        check: Annotated[Authorize, Depends(authorization_dependency)],
        actor: Annotated[object, Depends(actor_resolver)],
    ) -> ModelEngineLogoutResponse:
        await check("manage")
        try:
            return await service.logout(
                tenant_id,
                namespace=namespace,
                adapter=adapter,
                engine_ref=engine_ref,
                actor_id=_actor_id(actor),
            )
        except ModelEngineAccountError as exc:
            _raise_account_http_error(exc)
        raise AssertionError("unreachable")

    return router


__all__ = [
    "SUPPORTED_MODEL_ENGINES",
    "ModelEngineAccountService",
    "ModelEngineAccountStatusResponse",
    "ModelEngineCatalog",
    "ModelEngineCatalogEntry",
    "ModelEngineConflict",
    "ModelEngineInvalidRequest",
    "ModelEngineLoginRequest",
    "ModelEngineLoginStartResponse",
    "ModelEngineLogoutResponse",
    "ModelEngineUnavailable",
    "UnknownModelEngineAdapter",
    "build_model_engine_router",
]
