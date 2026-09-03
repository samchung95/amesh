"""Cohesive dependencies API definitions extracted from the composition root."""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
import secrets
from collections.abc import Awaitable, Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path
from threading import RLock
from typing import Annotated, NamedTuple, NoReturn, cast
from urllib.parse import parse_qs
from uuid import UUID

from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.types import ASGIApp, Receive, Scope, Send

from amesh.adapters.agent_session_registry import (
    AGENT_SESSION_HARNESS_REGISTRY,
)
from amesh.adapters.codex_app_server import CodexAccountManager, CodexAppServerConfig
from amesh.adapters.copilot_cli import CopilotAccountManager, CopilotCliConfig
from amesh.adapters.postgres import (
    PostgresAdmissionPolicyRepository,
    PostgresAgentMemoryRepository,
    PostgresAgentPrimitiveRepository,
    PostgresAgentResourceRepository,
    PostgresAgentSessionFleetRepository,
    PostgresAgentSessionPolicyRepository,
    PostgresAgentSessionRepository,
    PostgresAuditRepository,
    PostgresAuthenticationRepository,
    PostgresAuthorizationRepository,
    PostgresBackfillRepository,
    PostgresCheckRepository,
    PostgresCredentialRepository,
    PostgresDashboardRepository,
    PostgresEvidenceBundleRepository,
    PostgresExecutionRepository,
    PostgresFeatureFlagRepository,
    PostgresFederationRepository,
    PostgresFlowTestRepository,
    PostgresHumanTaskRepository,
    PostgresMetadataRepository,
    PostgresOperationalControlRepository,
    PostgresPluginPolicyRepository,
    PostgresPromotionRepository,
    PostgresRealtimeRepository,
    PostgresReconciliationRepository,
    PostgresRetentionRepository,
    PostgresSearchRepository,
    PostgresServiceRegistryRepository,
    PostgresSharedResourceRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
    PostgresTransferRepository,
    PostgresTriggerRuntimeRepository,
    PostgresUpgradeRepository,
    PostgresWorkerRepository,
)
from amesh.admission_policy import AdmissionPolicyService
from amesh.api.model_engines import (
    ModelEngineAccountService,
)
from amesh.api.models import (
    ScimGroupResource,
    ScimMember,
    ScimPatchRequest,
    ScimResourceMeta,
    ScimUserResource,
)
from amesh.application import (
    build_authentication_service,
)
from amesh.audit import AuditArtifactService
from amesh.authentication import (
    AuthenticationService,
    InvalidAuthentication,
    InvalidCsrf,
)
from amesh.authorization import AuthorizationDenied, AuthorizationService
from amesh.backfills import BackfillService
from amesh.config import (
    ConfigurationManager,
    ScimProviderConfig,
    Settings,
    get_configuration_manager,
    get_settings,
)
from amesh.credentials import CredentialService, InvalidCredential
from amesh.database import create_database_engine
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    IssuedBrowserSession,
    OperationalBoundary,
    PermissionAction,
    PolicyDecision,
    PolicyStage,
    PrincipalType,
    ScimResourceRecord,
    ServiceRole,
    TenantSlug,
)
from amesh.dsl import (
    FlowDefinition,
    TaskDefinition,
)
from amesh.evidence_bundle import (
    FilesystemEvidenceObjectStore,
)
from amesh.federation import (
    IdentityFederationService,
)
from amesh.human_tasks import HumanTaskService
from amesh.model_continuations import (
    configured_trigger_payload_protector,
)
from amesh.observability import (
    instrument_database,
)
from amesh.plugin_sdk import (
    PluginCatalogManager,
    PluginResolver,
)
from amesh.plugins import (
    IsolatedPluginRuntime,
    PluginPolicyService,
    SelfHostedPluginRegistry,
    TrustedPluginRuntime,
    build_isolated_runtime,
    build_plugin_catalog,
    build_trusted_runtime,
)
from amesh.ports import (
    AdmissionPolicyRepository,
    AgentMemoryRepository,
    AgentPrimitiveRepository,
    AgentResourceRepository,
    AgentSessionFleetRepository,
    AgentSessionPolicyRepository,
    AgentSessionRepository,
    AuditRepository,
    AuditStore,
    AuthenticationRepository,
    AuthorizationRepository,
    BackfillRepository,
    CheckRepository,
    CredentialRateLimitExceeded,
    CredentialRepository,
    DifferentialShadowRepository,
    EvidenceBundleRepository,
    ExecutionRepository,
    FeatureFlagRepository,
    FederationRepository,
    FlowTestRepository,
    HumanTaskRepository,
    MetadataRepository,
    OperationalControlRepository,
    PluginPolicyRepository,
    PromotionRepository,
    RealtimeRepository,
    SearchRepository,
    ServiceRegistryRepository,
    SharedResourceRepository,
    TaskCacheRepository,
    TenantQuotaExceeded,
    TenantRepository,
    TransferRepository,
    TriggerRuntimeRepository,
    WorkerRepository,
)
from amesh.ports.dashboard_repository import (
    DashboardRepository,
)
from amesh.ports.retention_repository import RetentionRepository
from amesh.ports.upgrade_repository import UpgradeRepository
from amesh.profile_transfer import (
    ProfileTransferService,
)
from amesh.promotion import PromotionService
from amesh.quality import (
    ConfigurationPin,
    DurableDifferentialService,
    PostgresDifferentialShadowRepository,
    RunObservation,
    ShadowRunContext,
)
from amesh.reconciliation import ReconciliationService
from amesh.retention import RetentionService
from amesh.storage.factory import build_object_store
from amesh.tenancy import TenantService
from amesh.upgrade import UpgradeService
from amesh.workflow.shared_resources import (
    NamespaceResourceService,
)

_MISSING_PROVIDER = object()


class ProviderCacheInfo(NamedTuple):
    hits: int
    misses: int
    maxsize: int | None
    currsize: int


class ApiProviderContainer:
    """Own lazily built API providers for one application instance."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._values: dict[Callable[[], object], object] = {}
        self._hits: dict[Callable[[], object], int] = {}
        self._misses: dict[Callable[[], object], int] = {}
        self._closing = False
        self._closed = False

    def resolve[ProviderValue](
        self,
        factory: Callable[[], ProviderValue],
    ) -> ProviderValue:
        with self._lock:
            if self._closing or self._closed:
                raise RuntimeError("API provider container is closed")
            cached = self._values.get(factory, _MISSING_PROVIDER)
            if cached is not _MISSING_PROVIDER:
                self._hits[factory] = self._hits.get(factory, 0) + 1
                return cast(ProviderValue, cached)
            self._misses[factory] = self._misses.get(factory, 0) + 1
            token = _ACTIVE_PROVIDER_CONTAINER.set(self)
            try:
                value = factory()
            finally:
                _ACTIVE_PROVIDER_CONTAINER.reset(token)
            self._values[factory] = value
            return value

    def set(self, provider: Callable[[], object], value: object) -> None:
        """Seed an explicit provider value for composition and integration tests."""

        with self._lock:
            if self._closing or self._closed:
                raise RuntimeError("API provider container is closed")
            self._values[_provider_factory(provider)] = value

    def provider_cache_info(self, provider: Callable[[], object]) -> ProviderCacheInfo:
        factory = _provider_factory(provider)
        with self._lock:
            return ProviderCacheInfo(
                hits=self._hits.get(factory, 0),
                misses=self._misses.get(factory, 0),
                maxsize=None,
                currsize=int(factory in self._values),
            )

    def clear(self, provider: Callable[[], object]) -> None:
        factory = _provider_factory(provider)
        with self._lock:
            self._values.pop(factory, None)
            self._hits.pop(factory, None)
            self._misses.pop(factory, None)

    @contextmanager
    def activate(self) -> Iterator[None]:
        token = _ACTIVE_PROVIDER_CONTAINER.set(self)
        try:
            yield
        finally:
            _ACTIVE_PROVIDER_CONTAINER.reset(token)

    async def close(self) -> None:
        """Close only runtime resources materialized by this application."""

        closed: set[int] = set()
        failures: list[BaseException] = []
        with self._lock:
            if self._closing or self._closed:
                return
            self._closing = True
            values = self._values
            self._values = {}
            self._hits = {}
            self._misses = {}
        try:
            for provider, method_name in (
                (get_model_engine_account_service, "close"),
                (get_isolated_plugin_runtime, "stop"),
                (get_trusted_plugin_runtime, "stop"),
                (read_database_engine, "dispose"),
                (database_engine, "dispose"),
            ):
                resource = values.get(_provider_factory(provider), _MISSING_PROVIDER)
                if resource is _MISSING_PROVIDER or id(resource) in closed:
                    continue
                closed.add(id(resource))
                try:
                    await getattr(resource, method_name)()
                except BaseException as exc:
                    failures.append(exc)
        finally:
            with self._lock:
                self._closing = False
                self._closed = True
        if len(failures) == 1:
            raise failures[0]
        if failures:
            raise BaseExceptionGroup("API provider cleanup failed", failures)


ApiProviderFactory = Callable[[], ApiProviderContainer]


_ACTIVE_PROVIDER_CONTAINER: ContextVar[ApiProviderContainer | None] = ContextVar(
    "amesh_api_provider_container",
    default=None,
)
_DEFAULT_PROVIDER_CONTAINER: ApiProviderContainer | None = None


def _provider_factory(provider: Callable[[], object]) -> Callable[[], object]:
    return cast(
        Callable[[], object],
        getattr(provider, "__amesh_provider_factory__", provider),
    )


def _default_provider_container() -> ApiProviderContainer:
    global _DEFAULT_PROVIDER_CONTAINER
    if _DEFAULT_PROVIDER_CONTAINER is None:
        _DEFAULT_PROVIDER_CONTAINER = ApiProviderContainer()
    return _DEFAULT_PROVIDER_CONTAINER


def provider[ProviderValue](
    factory: Callable[[], ProviderValue],
) -> Callable[[], ProviderValue]:
    """Expose a stable dependency callable backed by the active application container."""

    @wraps(factory)
    def resolve() -> ProviderValue:
        container = _ACTIVE_PROVIDER_CONTAINER.get() or _default_provider_container()
        return container.resolve(factory)

    def cache_info() -> ProviderCacheInfo:
        if _DEFAULT_PROVIDER_CONTAINER is None:
            return ProviderCacheInfo(hits=0, misses=0, maxsize=None, currsize=0)
        return _DEFAULT_PROVIDER_CONTAINER.provider_cache_info(resolve)

    def cache_clear() -> None:
        if _DEFAULT_PROVIDER_CONTAINER is None:
            return
        _DEFAULT_PROVIDER_CONTAINER.clear(resolve)

    resolve.__dict__.update(
        {
            "__amesh_provider_factory__": factory,
            "cache_info": cache_info,
            "cache_clear": cache_clear,
            "cache_parameters": lambda: {"maxsize": None, "typed": False},
        }
    )
    return resolve


class ApiProviderScopeMiddleware:
    """Keep one provider scope active through the complete ASGI request lifecycle."""

    def __init__(self, application: ASGIApp) -> None:
        self._application = application

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in {"http", "websocket"}:
            await self._application(scope, receive, send)
            return
        owner = cast(FastAPI, scope["app"])
        container: ApiProviderContainer | None = getattr(
            owner.state,
            "amesh_provider_container",
            None,
        )
        if container is None:
            request_owned = True
            container = owner.state.amesh_provider_factory()
        else:
            request_owned = False
        try:
            with container.activate():
                await self._application(scope, receive, send)
        finally:
            if request_owned:
                await container.close()


def install_provider_scope(application: FastAPI) -> None:
    """Resolve stable dependency callables from the active application's container."""

    application.add_middleware(ApiProviderScopeMiddleware)


@provider
def database_engine() -> AsyncEngine:
    settings = get_settings()
    return instrument_database(
        create_database_engine(settings),
        slow_query_seconds=settings.database_slow_query_seconds,
    )


@provider
def read_database_engine() -> AsyncEngine:
    settings = get_settings()
    return instrument_database(
        create_database_engine(settings, read_replica=True),
        slow_query_seconds=settings.database_slow_query_seconds,
    )


@provider
def get_plugin_catalog_manager() -> PluginCatalogManager:
    return build_plugin_catalog(get_settings())


PluginCatalogDependency = Annotated[
    PluginCatalogManager,
    Depends(get_plugin_catalog_manager),
]


@provider
def get_plugin_policy_repository() -> PluginPolicyRepository:
    return PostgresPluginPolicyRepository(database_engine())


PluginPolicyRepositoryDependency = Annotated[
    PluginPolicyRepository,
    Depends(get_plugin_policy_repository),
]


@provider
def get_plugin_policy_service() -> PluginPolicyService:
    settings = get_settings()
    return PluginPolicyService(
        get_plugin_policy_repository(),
        get_plugin_catalog_manager(),
        default_allow=settings.plugin_trust_mode == "development",
    )


PluginPolicyServiceDependency = Annotated[
    PluginPolicyService,
    Depends(get_plugin_policy_service),
]


@provider
def get_admission_policy_repository() -> AdmissionPolicyRepository:
    return PostgresAdmissionPolicyRepository(database_engine())


AdmissionPolicyRepositoryDependency = Annotated[
    AdmissionPolicyRepository,
    Depends(get_admission_policy_repository),
]


@provider
def get_admission_policy_service() -> AdmissionPolicyService:
    return AdmissionPolicyService(get_admission_policy_repository())


AdmissionPolicyServiceDependency = Annotated[
    AdmissionPolicyService,
    Depends(get_admission_policy_service),
]


async def _enforce_repository_admission_policy(
    flow: FlowDefinition,
    tenant_id: str,
    stage: PolicyStage,
    actor_id: str,
    inputs: dict[str, object] | None,
    task: TaskDefinition | None,
    execution_id: UUID | None,
    task_run_id: UUID | None,
) -> PolicyDecision:
    return await get_admission_policy_service().enforce_flow(
        flow,
        tenant_id,
        stage,
        actor_id,
        inputs=inputs,
        task=task,
        execution_id=execution_id,
        task_run_id=task_run_id,
    )


@provider
def get_self_hosted_plugin_registry() -> SelfHostedPluginRegistry:
    settings = get_settings()
    trusted_keys = {
        key_id: secret.get_secret_value().encode("utf-8")
        for key_id, secret in settings.plugin_registry_verification_keys.items()
    }
    return SelfHostedPluginRegistry(
        settings.plugin_registry_root,
        key_id=settings.plugin_registry_signing_key_id,
        signing_key=settings.plugin_registry_signing_key.get_secret_value().encode("utf-8"),
        trusted_keys=trusted_keys,
    )


SelfHostedPluginRegistryDependency = Annotated[
    SelfHostedPluginRegistry,
    Depends(get_self_hosted_plugin_registry),
]


@provider
def get_trusted_plugin_runtime() -> TrustedPluginRuntime:
    return build_trusted_runtime(get_settings(), get_plugin_catalog_manager())


TrustedPluginRuntimeDependency = Annotated[
    TrustedPluginRuntime,
    Depends(get_trusted_plugin_runtime),
]


@provider
def get_isolated_plugin_runtime() -> IsolatedPluginRuntime:
    return build_isolated_runtime(get_settings(), get_plugin_catalog_manager())


IsolatedPluginRuntimeDependency = Annotated[
    IsolatedPluginRuntime,
    Depends(get_isolated_plugin_runtime),
]


@provider
def get_repository() -> ExecutionRepository:
    catalog = get_plugin_catalog_manager()
    return PostgresExecutionRepository(
        database_engine(),
        plugin_resolution_provider=lambda flow: (
            PluginResolver(catalog.snapshot).resolve_flow(flow).revision_payload()
        ),
        plugin_policy_enforcer=get_plugin_policy_service().enforce_flow,
        admission_policy_enforcer=_enforce_repository_admission_policy,
    )


RepositoryDependency = Annotated[
    ExecutionRepository,
    Depends(get_repository),
]


@provider
def get_flow_test_repository() -> FlowTestRepository:
    return PostgresFlowTestRepository(database_engine())


FlowTestRepositoryDependency = Annotated[
    FlowTestRepository,
    Depends(get_flow_test_repository),
]


@provider
def get_task_cache_repository() -> TaskCacheRepository:
    return PostgresTaskCacheRepository(database_engine())


TaskCacheRepositoryDependency = Annotated[
    TaskCacheRepository,
    Depends(get_task_cache_repository),
]


@provider
def get_retention_repository() -> RetentionRepository:
    return PostgresRetentionRepository(database_engine())


@provider
def get_retention_service() -> RetentionService:
    return RetentionService(
        get_retention_repository(),
        build_object_store(get_settings()),
    )


RetentionRepositoryDependency = Annotated[
    RetentionRepository,
    Depends(get_retention_repository),
]


RetentionServiceDependency = Annotated[
    RetentionService,
    Depends(get_retention_service),
]


@provider
def get_trigger_runtime_repository() -> TriggerRuntimeRepository:
    settings = get_settings()
    return PostgresTriggerRuntimeRepository(
        database_engine(),
        configured_trigger_payload_protector(
            primary_key_id=settings.model_continuation_key_id,
            primary_key=settings.model_continuation_encryption_key,
            previous_key_id=settings.model_continuation_previous_key_id,
            previous_key=settings.model_continuation_previous_encryption_key,
        ),
    )


TriggerRuntimeRepositoryDependency = Annotated[
    TriggerRuntimeRepository,
    Depends(get_trigger_runtime_repository),
]


@provider
def get_check_repository() -> CheckRepository:
    return PostgresCheckRepository(database_engine())


CheckRepositoryDependency = Annotated[
    CheckRepository,
    Depends(get_check_repository),
]


@provider
def get_metadata_repository() -> MetadataRepository:
    return PostgresMetadataRepository(database_engine())


MetadataRepositoryDependency = Annotated[
    MetadataRepository,
    Depends(get_metadata_repository),
]


@provider
def get_evidence_bundle_repository() -> EvidenceBundleRepository:
    object_root = os.getenv("AMESH_EVIDENCE_OBJECT_ROOT")
    object_store = FilesystemEvidenceObjectStore(object_root) if object_root else None
    return PostgresEvidenceBundleRepository(database_engine(), object_store=object_store)


EvidenceBundleRepositoryDependency = Annotated[
    EvidenceBundleRepository,
    Depends(get_evidence_bundle_repository),
]


@provider
def get_promotion_repository() -> PromotionRepository:
    return PostgresPromotionRepository(database_engine())


@provider
def get_promotion_service() -> PromotionService:
    return PromotionService(get_promotion_repository())


async def get_promotion_authorizer(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Callable[[str], Awaitable[None]]:
    async def authorize_release(action: str) -> None:
        selected_action = (
            PermissionAction.VIEW if action in {"view", "preview"} else PermissionAction.MANAGE
        )
        await authorize_request(
            authorization_service,
            actor,
            resource_type="release",
            action=selected_action,
            tenant_id=tenant_id,
        )

    return authorize_release


async def get_promotion_actor(actor: ActorDependency) -> str:
    return str(actor.principal_id)


async def get_model_engine_authorizer(
    namespace: str,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Callable[[str], Awaitable[None]]:
    async def authorize_model_engine(action: str) -> None:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="agent_connection",
            action=(PermissionAction.VIEW if action == "view" else PermissionAction.MANAGE),
            tenant_id=tenant_id,
            namespace=namespace,
        )

    return authorize_model_engine


async def get_model_engine_actor(actor: ActorDependency) -> str:
    return str(actor.principal_id)


@provider
def get_differential_repository() -> DifferentialShadowRepository:
    return PostgresDifferentialShadowRepository(database_engine())


@provider
def get_differential_service() -> DurableDifferentialService:
    return DurableDifferentialService(get_differential_repository())


def get_differential_executor() -> Callable[
    [ConfigurationPin, object, ShadowRunContext], RunObservation
]:
    """Return the neutral baseline executor used until a domain adapter is supplied."""

    def execute(
        configuration: ConfigurationPin,
        inputs: object,
        context: ShadowRunContext,
    ) -> RunObservation:
        del configuration, context
        return RunObservation(output=inputs)

    return execute


async def get_differential_authorizer(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Callable[[str], Awaitable[None]]:
    async def authorize_differential(action: str) -> None:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=(PermissionAction.EXECUTE if action == "execute" else PermissionAction.VIEW),
            tenant_id=tenant_id,
        )

    return authorize_differential


async def get_differential_actor(actor: ActorDependency) -> str:
    return str(actor.principal_id)


@provider
def get_dashboard_repository() -> DashboardRepository:
    return PostgresDashboardRepository(database_engine())


DashboardRepositoryDependency = Annotated[
    DashboardRepository,
    Depends(get_dashboard_repository),
]


@provider
def get_search_repository() -> SearchRepository:
    return PostgresSearchRepository(database_engine())


SearchRepositoryDependency = Annotated[
    SearchRepository,
    Depends(get_search_repository),
]


@provider
def get_realtime_repository() -> RealtimeRepository:
    return PostgresRealtimeRepository(database_engine())


RealtimeRepositoryDependency = Annotated[
    RealtimeRepository,
    Depends(get_realtime_repository),
]


@provider
def get_agent_primitive_repository() -> AgentPrimitiveRepository:
    return PostgresAgentPrimitiveRepository(database_engine())


AgentPrimitiveRepositoryDependency = Annotated[
    AgentPrimitiveRepository,
    Depends(get_agent_primitive_repository),
]


@provider
def get_agent_resource_repository() -> AgentResourceRepository:
    return PostgresAgentResourceRepository(database_engine())


AgentResourceRepositoryDependency = Annotated[
    AgentResourceRepository,
    Depends(get_agent_resource_repository),
]


@provider
def get_transfer_repository() -> TransferRepository:
    compatible_harnesses = {
        (
            metadata["adapter"],
            metadata["adapterVersion"],
            metadata["protocol"],
        )
        for metadata in AGENT_SESSION_HARNESS_REGISTRY.values()
    }
    return PostgresTransferRepository(
        database_engine(),
        object_store=build_object_store(get_settings()),
        compatible_harnesses=compatible_harnesses,
    )


TransferRepositoryDependency = Annotated[
    TransferRepository,
    Depends(get_transfer_repository),
]


@provider
def get_profile_transfer_service() -> ProfileTransferService:
    return ProfileTransferService(
        get_agent_resource_repository(),
        get_agent_primitive_repository(),
        get_transfer_repository(),
    )


ProfileTransferServiceDependency = Annotated[
    ProfileTransferService,
    Depends(get_profile_transfer_service),
]


@provider
def get_agent_memory_repository() -> AgentMemoryRepository:
    return PostgresAgentMemoryRepository(database_engine())


AgentMemoryRepositoryDependency = Annotated[
    AgentMemoryRepository,
    Depends(get_agent_memory_repository),
]


@provider
def get_agent_session_repository() -> AgentSessionRepository:
    return PostgresAgentSessionRepository(database_engine())


AgentSessionRepositoryDependency = Annotated[
    AgentSessionRepository,
    Depends(get_agent_session_repository),
]


@provider
def get_agent_session_policy_repository() -> AgentSessionPolicyRepository:
    return PostgresAgentSessionPolicyRepository(database_engine())


AgentSessionPolicyRepositoryDependency = Annotated[
    AgentSessionPolicyRepository,
    Depends(get_agent_session_policy_repository),
]


@provider
def get_agent_session_fleet_repository() -> AgentSessionFleetRepository:
    return PostgresAgentSessionFleetRepository(database_engine())


AgentSessionFleetRepositoryDependency = Annotated[
    AgentSessionFleetRepository,
    Depends(get_agent_session_fleet_repository),
]


@provider
def get_shared_resource_repository() -> SharedResourceRepository:
    return PostgresSharedResourceRepository(database_engine())


SharedResourceRepositoryDependency = Annotated[
    SharedResourceRepository,
    Depends(get_shared_resource_repository),
]


@provider
def get_human_task_repository() -> HumanTaskRepository:
    return PostgresHumanTaskRepository(database_engine())


HumanTaskRepositoryDependency = Annotated[
    HumanTaskRepository,
    Depends(get_human_task_repository),
]


@provider
def get_operational_control_repository() -> OperationalControlRepository:
    return PostgresOperationalControlRepository(database_engine())


OperationalControlRepositoryDependency = Annotated[
    OperationalControlRepository,
    Depends(get_operational_control_repository),
]


@provider
def get_human_task_service() -> HumanTaskService:
    return HumanTaskService(
        get_human_task_repository(),
        get_repository(),
        token_pepper=get_settings().amesh_token_pepper.get_secret_value(),
    )


HumanTaskServiceDependency = Annotated[
    HumanTaskService,
    Depends(get_human_task_service),
]


@provider
def get_namespace_resource_service() -> NamespaceResourceService:
    return NamespaceResourceService(
        get_shared_resource_repository(),
        build_object_store(get_settings()),
    )


NamespaceResourceServiceDependency = Annotated[
    NamespaceResourceService,
    Depends(get_namespace_resource_service),
]


@provider
def get_replica_repository() -> ExecutionRepository:
    return PostgresExecutionRepository(read_database_engine())


def get_read_repository(
    primary: RepositoryDependency,
) -> ExecutionRepository:
    if get_settings().database_read_replica_url is None:
        return primary
    return get_replica_repository()


ReadRepositoryDependency = Annotated[
    ExecutionRepository,
    Depends(get_read_repository),
]


@provider
def get_backfill_repository() -> BackfillRepository:
    return PostgresBackfillRepository(database_engine())


BackfillRepositoryDependency = Annotated[
    BackfillRepository,
    Depends(get_backfill_repository),
]


@provider
def get_backfill_service() -> BackfillService:
    return BackfillService(
        get_repository(),
        get_backfill_repository(),
        get_operational_control_repository(),
    )


BackfillServiceDependency = Annotated[
    BackfillService,
    Depends(get_backfill_service),
]


SettingsDependency = Annotated[Settings, Depends(get_settings)]


ConfigurationManagerDependency = Annotated[
    ConfigurationManager,
    Depends(get_configuration_manager),
]


@provider
def get_authorization_repository() -> AuthorizationRepository:
    return PostgresAuthorizationRepository(database_engine())


@provider
def get_audit_repository() -> AuditStore:
    return PostgresAuditRepository(database_engine())


@provider
def get_model_engine_account_service() -> ModelEngineAccountService:
    settings = get_settings()
    state_root = Path(settings.model_engine_state_root)
    codex_config = CodexAppServerConfig(
        command=settings.model_engine_codex_command,
        state_root=state_root,
        frame_limit_bytes=settings.model_engine_max_frame_bytes,
        timeout_seconds=settings.model_engine_timeout_seconds,
        cancel_grace_seconds=settings.model_engine_cancel_grace_seconds,
        environment=settings.model_engine_environment,
    )
    copilot_config = CopilotCliConfig(
        command=settings.model_engine_copilot_command,
        state_root=state_root,
        frame_limit_bytes=settings.model_engine_max_frame_bytes,
        timeout_seconds=settings.model_engine_timeout_seconds,
        cancel_grace_seconds=settings.model_engine_cancel_grace_seconds,
        allow_plaintext_token_storage=settings.model_engine_copilot_allow_plaintext_token_storage,
        environment=settings.model_engine_environment,
    )
    return ModelEngineAccountService(
        {
            "openai-codex-app-server": lambda namespace, engine_ref: CodexAccountManager(
                codex_config,
                namespace=namespace,
                engine_ref=engine_ref,
            ),
            "github-copilot-cli": lambda namespace, engine_ref: CopilotAccountManager(
                copilot_config,
                namespace=namespace,
                engine_ref=engine_ref,
            ),
        },
        audit_repository=get_audit_repository(),
    )


@provider
def get_audit_artifact_service() -> AuditArtifactService:
    settings = get_settings()
    return AuditArtifactService(
        get_audit_repository(),
        signing_key=settings.webhook_signing_key.get_secret_value(),
        object_store=build_object_store(settings),
    )


@provider
def get_authorization_service() -> AuthorizationService:
    return AuthorizationService(
        get_authorization_repository(),
        decision_audit=get_audit_repository(),
    )


AuthorizationServiceDependency = Annotated[
    AuthorizationService,
    Depends(get_authorization_service),
]


AuthorizationRepositoryDependency = Annotated[
    AuthorizationRepository,
    Depends(get_authorization_repository),
]


AuditRepositoryDependency = Annotated[AuditRepository, Depends(get_audit_repository)]


AuditArtifactServiceDependency = Annotated[
    AuditArtifactService,
    Depends(get_audit_artifact_service),
]


@provider
def get_credential_repository() -> CredentialRepository:
    return PostgresCredentialRepository(database_engine())


@provider
def get_credential_service() -> CredentialService:
    settings = get_settings()
    return CredentialService(
        get_credential_repository(),
        token_pepper=settings.amesh_token_pepper,
        previous_token_pepper=settings.amesh_previous_token_pepper,
    )


CredentialServiceDependency = Annotated[CredentialService, Depends(get_credential_service)]


@provider
def get_authentication_repository() -> AuthenticationRepository:
    return PostgresAuthenticationRepository(database_engine())


@provider
def get_federation_repository() -> FederationRepository:
    return PostgresFederationRepository(
        database_engine(),
        token_pepper=get_settings().amesh_token_pepper,
    )


@provider
def get_authentication_service() -> AuthenticationService:
    settings = get_settings()
    return build_authentication_service(
        settings,
        get_authentication_repository(),
        federation_repository=get_federation_repository(),
    )


AuthenticationServiceDependency = Annotated[
    AuthenticationService,
    Depends(get_authentication_service),
]


@provider
def get_federation_service() -> IdentityFederationService:
    settings = get_settings()
    return IdentityFederationService(
        get_federation_repository(),
        get_authentication_service(),
        settings.identity_providers,
    )


FederationServiceDependency = Annotated[
    IdentityFederationService,
    Depends(get_federation_service),
]


async def authenticate_scim_provider(
    settings: SettingsDependency,
    authorization: Annotated[str | None, Header()] = None,
) -> ScimProviderConfig:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="SCIM bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    supplied = authorization[7:]
    unavailable = False
    for provider in settings.scim_providers:
        try:
            configured = Path(provider.token_file).read_text(encoding="utf-8").strip()
        except OSError:
            unavailable = True
            continue
        if configured and secrets.compare_digest(supplied, configured):
            return provider
    if unavailable and settings.scim_providers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SCIM provider credential is unavailable",
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid SCIM bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )


ScimProviderDependency = Annotated[ScimProviderConfig, Depends(authenticate_scim_provider)]


FederationRepositoryDependency = Annotated[
    FederationRepository,
    Depends(get_federation_repository),
]


@provider
def get_tenant_repository() -> TenantRepository:
    return PostgresTenantRepository(database_engine())


@provider
def get_tenant_service() -> TenantService:
    return TenantService(get_tenant_repository())


TenantServiceDependency = Annotated[TenantService, Depends(get_tenant_service)]


@provider
def get_feature_flag_repository() -> FeatureFlagRepository:
    return PostgresFeatureFlagRepository(database_engine())


FeatureFlagRepositoryDependency = Annotated[
    FeatureFlagRepository,
    Depends(get_feature_flag_repository),
]


@provider
def get_worker_repository() -> WorkerRepository:
    return PostgresWorkerRepository(database_engine())


WorkerRepositoryDependency = Annotated[
    WorkerRepository,
    Depends(get_worker_repository),
]


@provider
def get_reconciliation_service() -> ReconciliationService:
    return ReconciliationService(PostgresReconciliationRepository(database_engine()))


ReconciliationServiceDependency = Annotated[
    ReconciliationService,
    Depends(get_reconciliation_service),
]


@provider
def get_service_registry_repository() -> ServiceRegistryRepository:
    settings = get_settings()
    return PostgresServiceRegistryRepository(
        database_engine(),
        stale_after_seconds=settings.service_stale_after_seconds,
    )


ServiceRegistryRepositoryDependency = Annotated[
    ServiceRegistryRepository,
    Depends(get_service_registry_repository),
]


@provider
def get_upgrade_repository() -> UpgradeRepository:
    return PostgresUpgradeRepository(database_engine())


@provider
def get_upgrade_service() -> UpgradeService:
    return UpgradeService(
        get_upgrade_repository(),
        get_service_registry_repository(),
        get_plugin_catalog_manager(),
        build_object_store(get_settings()),
    )


UpgradeRepositoryDependency = Annotated[
    UpgradeRepository,
    Depends(get_upgrade_repository),
]


UpgradeServiceDependency = Annotated[
    UpgradeService,
    Depends(get_upgrade_service),
]


_TENANT_SLUG_ADAPTER = TypeAdapter(TenantSlug)


_BOOTSTRAP_PRINCIPAL_ID = UUID("00000000-0000-7000-8000-000000000001")


async def authenticate_bearer_actor(
    settings: SettingsDependency,
    credential_service: CredentialService | None,
    authorization: str | None,
) -> ActorContext:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="valid bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expected = f"Bearer {settings.amesh_admin_token.get_secret_value()}"
    if (
        settings.app_env == "development"
        and settings.auth_mode == "development"
        and authorization is not None
        and secrets.compare_digest(authorization, expected)
    ):
        return ActorContext(
            principal_id=_BOOTSTRAP_PRINCIPAL_ID,
            principal_type=PrincipalType.SYSTEM,
            display="development-bootstrap-admin",
            bootstrap_admin=True,
        )
    if credential_service is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="valid bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await credential_service.authenticate_bearer(authorization)
    except CredentialRateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="credential rate limit exceeded",
            headers={"Retry-After": "60"},
        ) from exc
    except InvalidCredential as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="valid bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def authenticate_actor(
    request: Request,
    response: Response,
    settings: SettingsDependency,
    credential_service: CredentialServiceDependency,
    authentication_service: AuthenticationServiceDependency,
    authorization: Annotated[str | None, Header()] = None,
    csrf_header: Annotated[str | None, Header(alias="X-Amesh-CSRF")] = None,
) -> ActorContext:
    if authorization is not None:
        return await authenticate_bearer_actor(settings, credential_service, authorization)
    session_cookie = request.cookies.get(_session_cookie_name(settings))
    if session_cookie is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    require_csrf = request.method not in {"GET", "HEAD", "OPTIONS", "TRACE"}
    try:
        authenticated = await authentication_service.authenticate_session(
            session_cookie,
            csrf_cookie=request.cookies.get(_csrf_cookie_name(settings)),
            csrf_header=csrf_header,
            require_csrf=require_csrf,
        )
    except InvalidCsrf as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        ) from exc
    except InvalidAuthentication as exc:
        _clear_session_cookies(response, settings)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if authenticated.rotated_token is not None:
        remaining = max(
            0,
            int((authenticated.absolute_expires_at - datetime.now(UTC)).total_seconds()),
        )
        _set_session_cookie(
            response,
            settings,
            authenticated.rotated_token.get_secret_value(),
            max_age=remaining,
        )
    request.state.browser_session_id = authenticated.session_id
    return authenticated.actor


def _session_cookie_name(settings: Settings) -> str:
    return "amesh_session" if settings.app_env == "development" else "__Host-amesh_session"


def _csrf_cookie_name(settings: Settings) -> str:
    return "amesh_csrf" if settings.app_env == "development" else "__Host-amesh_csrf"


def _set_session_cookie(
    response: Response,
    settings: Settings,
    value: str,
    *,
    max_age: int,
) -> None:
    response.set_cookie(
        _session_cookie_name(settings),
        value,
        max_age=max_age,
        path="/",
        secure=settings.app_env != "development",
        httponly=True,
        samesite="lax",
    )


def _set_authentication_cookies(
    response: Response,
    settings: Settings,
    *,
    session_token: str,
    csrf_token: str,
    max_age: int,
) -> None:
    _set_session_cookie(response, settings, session_token, max_age=max_age)
    response.set_cookie(
        _csrf_cookie_name(settings),
        csrf_token,
        max_age=max_age,
        path="/",
        secure=settings.app_env != "development",
        httponly=False,
        samesite="lax",
    )


def _clear_session_cookies(response: Response, settings: Settings) -> None:
    secure = settings.app_env != "development"
    response.delete_cookie(
        _session_cookie_name(settings),
        path="/",
        secure=secure,
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        _csrf_cookie_name(settings),
        path="/",
        secure=secure,
        httponly=False,
        samesite="lax",
    )


def _set_issued_session_cookies(
    response: Response,
    settings: Settings,
    issued: IssuedBrowserSession,
) -> None:
    max_age = max(
        0,
        int((issued.absolute_expires_at - datetime.now(UTC)).total_seconds()),
    )
    _set_authentication_cookies(
        response,
        settings,
        session_token=issued.session_token.get_secret_value(),
        csrf_token=issued.csrf_token.get_secret_value(),
        max_age=max_age,
    )


def _urlencoded_form(body: bytes) -> dict[str, str]:
    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="form payload must be UTF-8") from exc
    return {key: values[-1] for key, values in parse_qs(decoded, keep_blank_values=True).items()}


def _saml_request_data(
    request: Request,
    *,
    post_data: dict[str, str] | None = None,
) -> dict[str, object]:
    port = request.url.port or (443 if request.url.scheme == "https" else 80)
    return {
        "https": "on" if request.url.scheme == "https" else "off",
        "http_host": request.url.hostname or "localhost",
        "server_port": str(port),
        "script_name": request.url.path,
        "get_data": dict(request.query_params),
        "post_data": post_data or {},
        "query_string": request.url.query,
    }


def _scim_filter_value(filter_value: str | None, attribute: str) -> str | None:
    if filter_value is None:
        return None
    matched = re.fullmatch(
        rf'\s*{re.escape(attribute)}\s+eq\s+"([^"]+)"\s*',
        filter_value,
        flags=re.IGNORECASE,
    )
    if matched is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'SCIM filter must use {attribute} eq "value"',
        )
    return matched.group(1)


def _scim_principal_handle(value: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", value.strip().lower()).strip("-_")
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"scim-{(slug or 'resource')[:80]}-{digest}"


def _scim_meta(record: ScimResourceRecord) -> ScimResourceMeta:
    plural = "Users" if record.resource_type == "User" else "Groups"
    return ScimResourceMeta(
        resourceType=record.resource_type,
        created=record.created_at,
        lastModified=record.updated_at,
        version=f'W/"{record.version}"',
        location=f"/scim/v2/{plural}/{record.principal_id}",
    )


def _scim_user_resource(record: ScimResourceRecord) -> ScimUserResource:
    return ScimUserResource(
        id=record.principal_id,
        externalId=record.external_id,
        userName=record.resource_name,
        displayName=record.display_name,
        active=record.enabled,
        meta=_scim_meta(record),
    )


def _scim_group_resource(record: ScimResourceRecord) -> ScimGroupResource:
    return ScimGroupResource(
        id=record.principal_id,
        externalId=record.external_id,
        displayName=record.display_name,
        members=tuple(ScimMember(value=member_id) for member_id in record.member_ids),
        meta=_scim_meta(record),
    )


def _scim_user_patch(payload: ScimPatchRequest) -> tuple[str | None, bool | None]:
    display_name: str | None = None
    active: bool | None = None
    for operation in payload.operations:
        if operation.op.lower() not in {"add", "replace"}:
            raise ValueError("SCIM users support add or replace for active and displayName")
        if operation.path is None and isinstance(operation.value, dict):
            if "displayName" in operation.value:
                display_name = str(operation.value["displayName"])
            if "active" in operation.value:
                active = bool(operation.value["active"])
        elif operation.path and operation.path.lower() == "displayname":
            display_name = str(operation.value)
        elif operation.path and operation.path.lower() == "active":
            if not isinstance(operation.value, bool):
                raise ValueError("SCIM active patch value must be boolean")
            active = operation.value
        else:
            raise ValueError("unsupported SCIM user patch path")
    return display_name, active


def _scim_member_values(value: object) -> set[UUID]:
    items = value if isinstance(value, list) else [value]
    members: set[UUID] = set()
    for item in items:
        if not isinstance(item, dict) or "value" not in item:
            raise ValueError("SCIM member values must contain a value UUID")
        members.add(UUID(str(item["value"])))
    return members


def _scim_group_patch(
    payload: ScimPatchRequest,
    current_members: tuple[UUID, ...],
) -> tuple[str | None, tuple[UUID, ...] | None]:
    display_name: str | None = None
    members = set(current_members)
    members_changed = False
    for operation in payload.operations:
        op = operation.op.lower()
        path = operation.path or ""
        if not path and isinstance(operation.value, dict):
            if "displayName" in operation.value:
                display_name = str(operation.value["displayName"])
            if "members" in operation.value:
                members = _scim_member_values(operation.value["members"])
                members_changed = True
            continue
        if path.lower() == "displayname" and op in {"add", "replace"}:
            display_name = str(operation.value)
        elif path.lower() == "members" and op in {"add", "replace"}:
            incoming = _scim_member_values(operation.value)
            members = incoming if op == "replace" else members | incoming
            members_changed = True
        elif op == "remove":
            matched = re.fullmatch(
                r'members\[value\s+eq\s+"([0-9a-fA-F-]{36})"\]',
                path,
                flags=re.IGNORECASE,
            )
            if matched is None:
                raise ValueError('SCIM member removal requires members[value eq "uuid"]')
            members.discard(UUID(matched.group(1)))
            members_changed = True
        else:
            raise ValueError("unsupported SCIM group patch operation")
    ordered = tuple(sorted(members, key=str)) if members_changed else None
    return display_name, ordered


ActorDependency = Annotated[ActorContext, Depends(authenticate_actor)]


class _TenantRequestContext(str):
    """Tenant slug carrying the request-local, deferred API quota charge."""

    _tenant_service: TenantService
    _quota_charge_lock: asyncio.Lock
    _quota_charged: bool

    def __new__(cls, value: str, tenant_service: TenantService) -> _TenantRequestContext:
        context = super().__new__(cls, value)
        context._tenant_service = tenant_service
        context._quota_charge_lock = asyncio.Lock()
        context._quota_charged = False
        return context

    async def charge_api_request(self) -> None:
        async with self._quota_charge_lock:
            if self._quota_charged:
                return
            await self._tenant_service.consume_api_request(str(self))
            self._quota_charged = True


def _request_control_boundaries(request: Request) -> tuple[OperationalBoundary, ...]:
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return ()
    path = request.url.path
    if path.startswith("/api/v1/operational-controls"):
        return ()
    boundaries = [OperationalBoundary.API_WRITES]
    authoring_roots = (
        "/api/v1/flows",
        "/api/v1/apps",
        "/api/v1/dashboards",
        "/api/v1/plugin-policy",
        "/api/v1/plugin-registry",
        "/api/v1/namespaces",
    )
    if path.startswith(authoring_roots):
        boundaries.append(OperationalBoundary.AUTHORING)
    return tuple(boundaries)


async def _enforce_request_controls(
    repository: OperationalControlRepository,
    request: Request,
    *,
    tenant_id: str,
) -> None:
    for boundary in _request_control_boundaries(request):
        decision = await repository.evaluate(
            boundary,
            tenant_id=tenant_id,
            namespace=request.path_params.get("namespace"),
            flow_id=request.path_params.get("flow_id"),
            component_id="webserver:api",
            component_role=ServiceRole.WEBSERVER.value,
        )
        if decision.blocked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail={
                    "message": f"{boundary.value.lower()} blocked by operational control",
                    "boundary": boundary.value,
                    "controlIds": [str(control.control_id) for control in decision.controls],
                },
            )


async def require_tenant_context(
    request: Request,
    settings: SettingsDependency,
    tenant_service: TenantServiceDependency,
    operational_controls: OperationalControlRepositoryDependency,
    tenant_header: Annotated[str | None, Header(alias="X-Amesh-Tenant")] = None,
) -> str:
    if tenant_header is None:
        if settings.tenancy_mode != "single":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Amesh-Tenant header required",
            )
        tenant_header = settings.single_tenant_slug
    try:
        tenant_slug = _TENANT_SLUG_ADAPTER.validate_python(tenant_header)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tenant unavailable",
        ) from None
    tenant_context = _TenantRequestContext(tenant_slug, tenant_service)
    await _enforce_request_controls(
        operational_controls,
        request,
        tenant_id=tenant_context,
    )
    return tenant_context


TenantDependency = Annotated[str, Depends(require_tenant_context)]


async def _charge_authorized_tenant_request(tenant_id: str | None) -> None:
    if not isinstance(tenant_id, _TenantRequestContext):
        return
    try:
        await tenant_id.charge_api_request()
    except TenantQuotaExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="tenant API request quota exceeded",
            headers={"Retry-After": "60"},
        ) from exc


async def authorize_request(
    service: AuthorizationService,
    actor: ActorContext,
    *,
    resource_type: str,
    action: PermissionAction,
    tenant_id: str | None = None,
    namespace: str | None = None,
) -> AuthorizationDecision:
    try:
        decision = await service.require(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant_id,
                namespace=namespace,
                resource_type=resource_type,
                action=action,
            )
        )
    except AuthorizationDenied as exc:
        if tenant_id is not None and not exc.decision.matched_role_names:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="tenant unavailable",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized",
        ) from exc
    await _charge_authorized_tenant_request(tenant_id)
    return decision


_AGENT_SESSION_LEGACY_FALLBACK_REASONS = frozenset({"NO_MATCHING_GRANT", "CREDENTIAL_SCOPE_DENY"})


def _raise_authorization_http_error(
    decision: AuthorizationDecision,
    *,
    tenant_id: str | None,
) -> NoReturn:
    if tenant_id is not None and not decision.matched_role_names:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tenant unavailable",
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="not authorized",
    )


async def authorize_agent_session_request(
    service: AuthorizationService,
    actor: ActorContext,
    *,
    action: PermissionAction,
    legacy_actions: tuple[PermissionAction, ...],
    tenant_id: str,
    namespace: str | None = None,
) -> AuthorizationDecision:
    """Authorize the session product boundary with a temporary execution-RBAC fallback."""

    decision = await service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=namespace,
            resource_type="agent_session",
            action=action,
        )
    )
    if decision.allowed:
        await _charge_authorized_tenant_request(tenant_id)
        return decision
    if decision.reason_code not in _AGENT_SESSION_LEGACY_FALLBACK_REASONS:
        _raise_authorization_http_error(decision, tenant_id=tenant_id)

    fallback_decision = decision
    for legacy_action in legacy_actions:
        fallback_decision = await service.decide(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant_id,
                namespace=namespace,
                resource_type="execution",
                action=legacy_action,
            )
        )
        if not fallback_decision.allowed:
            _raise_authorization_http_error(fallback_decision, tenant_id=tenant_id)
    await _charge_authorized_tenant_request(tenant_id)
    return fallback_decision


async def _agent_session_fleet_access_allowed(
    service: AuthorizationService,
    actor: ActorContext,
    *,
    tenant_id: str,
) -> bool:
    """Check optional fleet visibility without overriding an explicit session deny."""

    decision = await service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            resource_type="agent_session",
            action=PermissionAction.LIST,
        )
    )
    if decision.allowed:
        return True
    if decision.reason_code not in _AGENT_SESSION_LEGACY_FALLBACK_REASONS:
        return False
    legacy = await service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            resource_type="execution",
            action=PermissionAction.MANAGE,
        )
    )
    return legacy.allowed
