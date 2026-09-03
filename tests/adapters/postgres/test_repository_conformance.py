from __future__ import annotations

import pytest

from amesh.adapters.postgres import (
    PostgresAdmissionPolicyRepository,
    PostgresAdmissionRepository,
    PostgresAgentMemoryRepository,
    PostgresAgentPrimitiveRepository,
    PostgresAgentProgressSink,
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
    PostgresDurableTransport,
    PostgresEvidenceBundleRepository,
    PostgresExecutionControlRepository,
    PostgresExecutionLifecycleRepository,
    PostgresExecutionRepository,
    PostgresFeatureFlagRepository,
    PostgresFederationRepository,
    PostgresFlowRegistryRepository,
    PostgresFlowTestRepository,
    PostgresHumanTaskRepository,
    PostgresMetadataRepository,
    PostgresOperationalControlRepository,
    PostgresOperationsRepository,
    PostgresPluginPolicyRepository,
    PostgresPromotionRepository,
    PostgresRealtimeRepository,
    PostgresReconciliationRepository,
    PostgresRetentionRepository,
    PostgresSchedulerRepository,
    PostgresSearchRepository,
    PostgresServiceRegistryRepository,
    PostgresSharedResourceRepository,
    PostgresTaskCacheRepository,
    PostgresTaskRunRepository,
    PostgresTenantRepository,
    PostgresToolInvocationJournal,
    PostgresTransferRepository,
    PostgresTriggerRuntimeRepository,
    PostgresUpgradeRepository,
    PostgresWorkerRepository,
)
from amesh.domain import ResourceVersionConflict
from amesh.model_providers import (
    ModelProfileConflict,
    ProviderCallAmbiguous,
    ProviderCallTimeout,
    ProviderNegotiationError,
    ProviderRevisionConflict,
    RetryableProviderError,
)
from amesh.ports import (
    AdmissionPolicyRepository,
    AdmissionRepository,
    AgentMemoryRepository,
    AgentPrimitiveRepository,
    AgentProgressSink,
    AgentResourceRepository,
    AgentSessionFleetRepository,
    AgentSessionPolicyRepository,
    AgentSessionRepository,
    AuditRepository,
    AuthenticationRepository,
    AuthorizationDecisionAuditSink,
    AuthorizationRepository,
    BackfillRepository,
    CheckRepository,
    CredentialRepository,
    DashboardRepository,
    DifferentialShadowRepository,
    DurableTransport,
    EvidenceBundleRepository,
    ExecutionControlRepository,
    ExecutionLifecycleRepository,
    ExecutionRepository,
    FeatureFlagRepository,
    FederationRepository,
    FlowRegistryRepository,
    FlowTestRepository,
    HumanTaskRepository,
    MetadataRepository,
    OperationalControlRepository,
    OperationsRepository,
    PluginPolicyRepository,
    PromotionRepository,
    RealtimeRepository,
    ReconciliationRepository,
    RetentionRepository,
    SchedulerRepository,
    SearchProjector,
    SearchRepository,
    ServiceRegistryRepository,
    SharedResourceRepository,
    TaskCacheRepository,
    TaskRunRepository,
    TenantRepository,
    ToolInvocationJournal,
    TransferRepository,
    TriggerRuntimeRepository,
    UpgradeRepository,
    WorkerRepository,
)
from amesh.ports.errors import (
    NotFoundError,
    ProviderError,
    RepositoryVersionConflict,
    VersionConflict,
)
from amesh.quality.repository import PostgresDifferentialShadowRepository


@pytest.mark.parametrize(
    ("adapter", "ports"),
    (
        (PostgresAdmissionPolicyRepository, (AdmissionPolicyRepository,)),
        (PostgresAdmissionRepository, (AdmissionRepository,)),
        (PostgresAgentMemoryRepository, (AgentMemoryRepository,)),
        (PostgresAgentPrimitiveRepository, (AgentPrimitiveRepository,)),
        (PostgresAgentProgressSink, (AgentProgressSink,)),
        (PostgresAgentResourceRepository, (AgentResourceRepository,)),
        (PostgresAgentSessionFleetRepository, (AgentSessionFleetRepository,)),
        (PostgresAgentSessionPolicyRepository, (AgentSessionPolicyRepository,)),
        (PostgresAgentSessionRepository, (AgentSessionRepository,)),
        (
            PostgresAuditRepository,
            (AuditRepository, AuthorizationDecisionAuditSink),
        ),
        (PostgresAuthenticationRepository, (AuthenticationRepository,)),
        (PostgresAuthorizationRepository, (AuthorizationRepository,)),
        (PostgresBackfillRepository, (BackfillRepository,)),
        (PostgresCheckRepository, (CheckRepository,)),
        (PostgresCredentialRepository, (CredentialRepository,)),
        (PostgresDashboardRepository, (DashboardRepository,)),
        (PostgresDifferentialShadowRepository, (DifferentialShadowRepository,)),
        (PostgresDurableTransport, (DurableTransport,)),
        (PostgresEvidenceBundleRepository, (EvidenceBundleRepository,)),
        (PostgresExecutionControlRepository, (ExecutionControlRepository,)),
        (PostgresExecutionLifecycleRepository, (ExecutionLifecycleRepository,)),
        (PostgresExecutionRepository, (ExecutionRepository,)),
        (PostgresFeatureFlagRepository, (FeatureFlagRepository,)),
        (PostgresFederationRepository, (FederationRepository,)),
        (PostgresFlowTestRepository, (FlowTestRepository,)),
        (PostgresFlowRegistryRepository, (FlowRegistryRepository,)),
        (PostgresHumanTaskRepository, (HumanTaskRepository,)),
        (PostgresMetadataRepository, (MetadataRepository,)),
        (PostgresOperationalControlRepository, (OperationalControlRepository,)),
        (PostgresOperationsRepository, (OperationsRepository,)),
        (PostgresPluginPolicyRepository, (PluginPolicyRepository,)),
        (PostgresPromotionRepository, (PromotionRepository,)),
        (PostgresRealtimeRepository, (RealtimeRepository,)),
        (PostgresReconciliationRepository, (ReconciliationRepository,)),
        (PostgresRetentionRepository, (RetentionRepository,)),
        (PostgresSchedulerRepository, (SchedulerRepository,)),
        (PostgresSearchRepository, (SearchRepository, SearchProjector)),
        (PostgresServiceRegistryRepository, (ServiceRegistryRepository,)),
        (PostgresSharedResourceRepository, (SharedResourceRepository,)),
        (PostgresTaskCacheRepository, (TaskCacheRepository,)),
        (PostgresTaskRunRepository, (TaskRunRepository,)),
        (PostgresTenantRepository, (TenantRepository,)),
        (PostgresToolInvocationJournal, (ToolInvocationJournal,)),
        (PostgresTransferRepository, (TransferRepository,)),
        (PostgresTriggerRuntimeRepository, (TriggerRuntimeRepository,)),
        (PostgresUpgradeRepository, (UpgradeRepository,)),
        (PostgresWorkerRepository, (WorkerRepository,)),
    ),
)
def test_postgres_adapter_explicitly_implements_checked_ports(
    adapter: type[object], ports: tuple[type[object], ...]
) -> None:
    assert all(port in adapter.__mro__ for port in ports)


@pytest.mark.parametrize(
    ("error", "boundary"),
    (
        (ProviderNegotiationError, ProviderError),
        (ProviderCallTimeout, ProviderError),
        (RetryableProviderError, ProviderError),
        (ProviderCallAmbiguous, ProviderError),
        (ProviderRevisionConflict, VersionConflict),
        (ModelProfileConflict, VersionConflict),
    ),
)
def test_cross_layer_errors_use_shared_port_vocabulary(
    error: type[BaseException], boundary: type[BaseException]
) -> None:
    assert issubclass(error, boundary)


def test_not_found_error_preserves_legacy_lookup_boundary() -> None:
    error = NotFoundError("flow", "orders")

    assert isinstance(error, LookupError)
    assert error.resource == "flow"
    assert error.key == "orders"


def test_not_found_error_can_preserve_an_existing_public_message() -> None:
    error = NotFoundError("flow", "orders", message="flow orders does not exist")

    assert str(error) == "flow orders does not exist"


def test_repository_version_conflict_bridges_domain_and_port_boundaries() -> None:
    error = RepositoryVersionConflict("flow orders changed")

    assert isinstance(error, ResourceVersionConflict)
    assert isinstance(error, VersionConflict)
    assert str(error) == "flow orders changed"
