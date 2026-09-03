"""Cohesive platform API definitions extracted from the composition root."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi import Path as PathParameter
from pydantic import ValidationError

from amesh import __version__
from amesh.admission_policy import policy_input_from_flow
from amesh.api.dependencies import (
    ActorDependency,
    AdmissionPolicyRepositoryDependency,
    AdmissionPolicyServiceDependency,
    AuthorizationServiceDependency,
    ConfigurationManagerDependency,
    FeatureFlagRepositoryDependency,
    IsolatedPluginRuntimeDependency,
    PluginCatalogDependency,
    PluginPolicyRepositoryDependency,
    PluginPolicyServiceDependency,
    SelfHostedPluginRegistryDependency,
    SettingsDependency,
    TenantDependency,
    TrustedPluginRuntimeDependency,
    authorize_request,
)
from amesh.api.models import (
    ConfigurationDiagnosticBundle,
    FeatureFlagUpsertRequest,
)
from amesh.authorization import AuthorizationService
from amesh.config import (
    ConfigurationLoadError,
    ConfigurationSnapshot,
    NonReloadableConfigurationChanged,
)
from amesh.domain import (
    ActorContext,
    AdministrationApplyRequest,
    AdministrationApprovalError,
    AdministrationAuditEntry,
    AdministrationControl,
    AdministrationControlDraft,
    AdministrationControlKey,
    AdministrationImpactPreview,
    EffectivePluginPolicy,
    FeatureFlag,
    FeatureFlagDecision,
    FeatureFlagScope,
    PermissionAction,
    PluginPolicyDecision,
    PluginPolicyImpactPreview,
    PluginPolicyRule,
    PluginPolicyRuleCreate,
    PluginPolicyScope,
    PluginPolicyStage,
    PluginQuarantine,
    PluginQuarantineCreate,
    PolicyDecision,
    PolicyDocument,
    PolicyEvaluationRequest,
    PolicyFixture,
    PolicyFixtureResult,
    PolicyRevision,
    PolicyScope,
    PolicyStage,
    administration_control_flag,
    administration_controls,
    issue_administration_preview,
    verify_administration_approval,
)
from amesh.dsl import (
    FlowDefinition,
    FlowDocumentError,
    validate_flow_document,
)
from amesh.observability import (
    configure_observability,
    diagnostic_metric_samples,
    recent_redacted_logs,
)
from amesh.plugin_sdk import (
    PluginCatalogSnapshot,
    PluginRegistryIndex,
    PluginRegistryPackage,
    PluginRegistryPublishRequest,
    PluginRegistryYankRequest,
)
from amesh.plugins import (
    IsolatedPluginRuntimeSnapshot,
    PluginPolicyDenied,
    TrustedPluginRuntimeSnapshot,
)
from amesh.ports import (
    FeatureFlagVersionConflict,
)

router_1 = APIRouter()


router_2 = APIRouter()


router_3 = APIRouter()


@router_1.get(
    "/api/v1/plugins",
    response_model=PluginCatalogSnapshot,
    tags=["plugins"],
)
async def list_plugins(
    catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginCatalogSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return catalog.snapshot


@router_1.get(
    "/api/v1/plugin-policy/effective",
    response_model=EffectivePluginPolicy,
    tags=["plugins"],
)
async def get_effective_plugin_policy(
    service: PluginPolicyServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> EffectivePluginPolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await service.effective_policy(tenant_id, namespace=namespace)


@router_1.get(
    "/api/v1/plugin-policy/decisions",
    response_model=tuple[PluginPolicyDecision, ...],
    tags=["plugins"],
)
async def list_plugin_policy_decisions(
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> tuple[PluginPolicyDecision, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_decisions(tenant_id, limit=limit)


@router_1.post(
    "/api/v1/plugin-policy/evaluate",
    response_model=PluginPolicyDecision,
    tags=["plugins"],
)
async def evaluate_flow_plugin_policy(
    request: Request,
    service: PluginPolicyServiceDependency,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    stage: PluginPolicyStage = PluginPolicyStage.VALIDATION,
) -> PluginPolicyDecision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=(
            PermissionAction.MANAGE
            if stage is PluginPolicyStage.ADMINISTRATION
            else PermissionAction.VIEW
        ),
        tenant_id=tenant_id,
    )
    try:
        result = validate_flow_document(
            await request.body(),
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if not result.valid or result.canonical is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[issue.model_dump(mode="json", by_alias=True) for issue in result.issues],
        )
    flow = FlowDefinition.model_validate(result.canonical)
    return await service.evaluate_flow(
        flow,
        tenant_id=tenant_id,
        stage=stage,
        actor_id=str(actor.principal_id),
    )


@router_2.get(
    "/api/v1/policies",
    response_model=tuple[PolicyRevision, ...],
    tags=["policies"],
)
async def list_admission_policies(
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: str = "default",
) -> tuple[PolicyRevision, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.effective_revisions(tenant_id, namespace=namespace)


@router_2.post(
    "/api/v1/policies",
    response_model=PolicyRevision,
    status_code=status.HTTP_201_CREATED,
    tags=["policies"],
)
async def create_admission_policy(
    request: PolicyDocument,
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PolicyRevision:
    await _authorize_admission_policy_change(
        request,
        actor,
        authorization_service,
        tenant_id,
    )
    return await repository.save_revision(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@router_2.post(
    "/api/v1/policies/evaluate",
    response_model=PolicyDecision,
    tags=["policies"],
)
async def evaluate_admission_policies(
    request: PolicyEvaluationRequest,
    service: AdmissionPolicyServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PolicyDecision:
    namespace = request.input.namespace.id
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    evaluated_input = request.input.model_copy(
        update={
            "actor": request.input.actor.model_copy(
                update={
                    "principal_id": str(actor.principal_id),
                    "principal_type": actor.principal_type.value,
                    "display": actor.display,
                }
            ),
            "tenant": request.input.tenant.model_copy(update={"id": tenant_id}),
        }
    )
    return await service.evaluate(request.model_copy(update={"input": evaluated_input}))


@router_2.post(
    "/api/v1/policies/flows/validate",
    response_model=PolicyDecision,
    tags=["policies"],
)
async def validate_flow_admission_policy(
    request: Request,
    service: AdmissionPolicyServiceDependency,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PolicyDecision:
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB policy-validation limit",
        )
    try:
        result = validate_flow_document(
            body,
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if not result.valid or result.canonical is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[issue.model_dump(mode="json", by_alias=True) for issue in result.issues],
        )
    flow = FlowDefinition.model_validate(result.canonical)
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=flow.namespace,
    )
    return await service.evaluate(
        PolicyEvaluationRequest(
            stage=PolicyStage.VALIDATE,
            input=policy_input_from_flow(
                flow,
                tenant_id=tenant_id,
                actor=actor,
            ),
        )
    )


@router_2.get(
    "/api/v1/policies/decisions",
    response_model=tuple[PolicyDecision, ...],
    tags=["policies"],
)
async def list_admission_policy_decisions(
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> tuple[PolicyDecision, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_decisions(tenant_id, limit=limit)


@router_2.get(
    "/api/v1/policies/{policy_key}",
    response_model=PolicyRevision,
    tags=["policies"],
)
async def get_admission_policy(
    policy_key: str,
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> PolicyRevision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await repository.get_revision(
            tenant_id,
            policy_key,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_2.put(
    "/api/v1/policies/{policy_key}",
    response_model=PolicyRevision,
    tags=["policies"],
)
async def update_admission_policy(
    policy_key: str,
    request: PolicyDocument,
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PolicyRevision:
    if policy_key != request.policy_key:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="policy key does not match request document",
        )
    await _authorize_admission_policy_change(
        request,
        actor,
        authorization_service,
        tenant_id,
    )
    return await repository.save_revision(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@router_2.post(
    "/api/v1/policies/{policy_key}/test",
    response_model=PolicyFixtureResult,
    tags=["policies"],
)
async def test_admission_policy(
    policy_key: str,
    request: PolicyFixture,
    service: AdmissionPolicyServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> PolicyFixtureResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=request.request.input.namespace.id,
    )
    try:
        return await service.test_fixture(
            tenant_id,
            policy_key,
            request,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_2.post(
    "/api/v1/plugin-policy/rules",
    response_model=PluginPolicyRule,
    status_code=status.HTTP_201_CREATED,
    tags=["plugins"],
)
async def create_plugin_policy_rule(
    request: PluginPolicyRuleCreate,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginPolicyRule:
    await _authorize_plugin_policy_change(
        request.scope,
        request.namespace,
        actor,
        authorization_service,
        tenant_id,
    )
    return await repository.create_rule(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@router_2.put(
    "/api/v1/plugin-policy/rules/{rule_id}",
    response_model=PluginPolicyRule,
    tags=["plugins"],
)
async def update_plugin_policy_rule(
    rule_id: UUID,
    request: PluginPolicyRuleCreate,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginPolicyRule:
    await _authorize_plugin_policy_change(
        request.scope,
        request.namespace,
        actor,
        authorization_service,
        tenant_id,
    )
    try:
        return await repository.update_rule(
            tenant_id,
            rule_id,
            request,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_2.get(
    "/api/v1/plugin-policy/rules/{rule_id}",
    response_model=PluginPolicyRule,
    tags=["plugins"],
)
async def get_plugin_policy_rule(
    rule_id: UUID,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginPolicyRule:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await repository.get_rule(tenant_id, rule_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_2.delete(
    "/api/v1/plugin-policy/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["plugins"],
)
async def delete_plugin_policy_rule(
    rule_id: UUID,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    try:
        await repository.delete_rule(
            tenant_id,
            rule_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_2.post(
    "/api/v1/plugin-policy/quarantines/preview",
    response_model=PluginPolicyImpactPreview,
    tags=["plugins"],
)
async def preview_plugin_quarantine(
    request: PluginQuarantineCreate,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginPolicyImpactPreview:
    await _authorize_plugin_policy_change(
        request.scope,
        request.namespace,
        actor,
        authorization_service,
        tenant_id,
    )
    return await repository.impact_preview(tenant_id, request)


@router_2.post(
    "/api/v1/plugin-policy/quarantines",
    response_model=PluginQuarantine,
    status_code=status.HTTP_201_CREATED,
    tags=["plugins"],
)
async def quarantine_plugin_version(
    request: PluginQuarantineCreate,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginQuarantine:
    await _authorize_plugin_policy_change(
        request.scope,
        request.namespace,
        actor,
        authorization_service,
        tenant_id,
    )
    try:
        return await repository.create_quarantine(
            tenant_id,
            request,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_2.post(
    "/api/v1/plugin-policy/quarantines/{quarantine_id}/release",
    response_model=PluginQuarantine,
    tags=["plugins"],
)
async def release_plugin_quarantine(
    quarantine_id: UUID,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    reason: Annotated[str, Query(min_length=1, max_length=2048)],
) -> PluginQuarantine:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    try:
        return await repository.release_quarantine(
            tenant_id,
            quarantine_id,
            actor_id=str(actor.principal_id),
            reason=reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_2.get(
    "/api/v1/plugins/trusted-runtime",
    response_model=TrustedPluginRuntimeSnapshot,
    tags=["plugins"],
)
async def trusted_plugin_runtime_status(
    runtime: TrustedPluginRuntimeDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> TrustedPluginRuntimeSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    await runtime.ensure_started()
    return runtime.snapshot()


@router_2.get(
    "/api/v1/plugins/isolated-runtime",
    response_model=IsolatedPluginRuntimeSnapshot,
    tags=["plugins"],
)
async def isolated_plugin_runtime_status(
    runtime: IsolatedPluginRuntimeDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> IsolatedPluginRuntimeSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    await runtime.ensure_configured()
    return runtime.snapshot()


@router_2.post(
    "/api/v1/plugins/refresh",
    response_model=PluginCatalogSnapshot,
    tags=["plugins"],
)
async def refresh_plugins(
    catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginCatalogSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    return await asyncio.to_thread(catalog.refresh)


@router_2.post(
    "/api/v1/plugins/install",
    response_model=PluginCatalogSnapshot,
    tags=["plugins"],
)
async def install_plugin_bundle(
    request: Request,
    catalog: PluginCatalogDependency,
    policy: PluginPolicyServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    content_digest: Annotated[
        str,
        Query(alias="contentDigest", pattern=r"^sha256:[0-9a-f]{64}$"),
    ],
) -> PluginCatalogSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    content = await request.body()
    if len(content) > 64 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="plugin bundle exceeds the 64 MiB installation limit",
        )
    try:
        manifest = catalog.inspect_offline_bundle_bytes(
            content,
            expected_digest=content_digest,
        )
        await policy.enforce_manifest_administration(
            manifest,
            content_digest,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
        catalog.install_offline_bundle_bytes(content, expected_digest=content_digest)
    except PluginPolicyDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return catalog.snapshot


@router_2.get(
    "/api/v1/plugin-registry/index",
    response_model=PluginRegistryIndex,
    tags=["plugins"],
)
async def get_plugin_registry_index(
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryIndex:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return registry.snapshot()


@router_2.post(
    "/api/v1/plugin-registry/packages",
    response_model=PluginRegistryPackage,
    tags=["plugins"],
)
async def publish_plugin_registry_package(
    request: PluginRegistryPublishRequest,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryPackage:
    del tenant_id
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    try:
        return registry.publish_request(request)
    except (OSError, ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router_2.get(
    "/api/v1/plugin-registry/packages/{name}/{version}",
    response_model=PluginRegistryPackage,
    tags=["plugins"],
)
async def get_plugin_registry_package(
    name: str,
    version: str,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryPackage:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return registry.release(name, version)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_2.post(
    "/api/v1/plugin-registry/packages/{name}/{version}/yank",
    response_model=PluginRegistryPackage,
    tags=["plugins"],
)
async def yank_plugin_registry_package(
    name: str,
    version: str,
    request: PluginRegistryYankRequest,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryPackage:
    del tenant_id
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    try:
        return registry.yank(name, version, reason=request.reason)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_2.get(
    "/api/v1/plugin-registry/blobs/{digest}",
    response_class=Response,
    tags=["plugins"],
)
async def download_plugin_registry_bundle(
    digest: Annotated[str, PathParameter(pattern=r"^[0-9a-f]{64}$")],
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        content = registry.download(f"sha256:{digest}")
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(content=content, media_type="application/vnd.amesh.plugin+zip")


@router_2.get(
    "/api/v1/plugin-registry/offline-export",
    response_class=Response,
    tags=["plugins"],
)
async def export_plugin_registry(
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return Response(
        content=registry.export_offline(),
        media_type="application/vnd.amesh.plugin-registry+zip",
        headers={"Content-Disposition": 'attachment; filename="amesh-plugin-registry.zip"'},
    )


@router_2.post(
    "/api/v1/plugin-registry/offline-import",
    response_model=PluginRegistryIndex,
    tags=["plugins"],
)
async def import_plugin_registry(
    request: Request,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryIndex:
    del tenant_id
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    content = await request.body()
    if len(content) > 256 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="offline plugin registry bundle exceeds 256 MiB",
        )
    try:
        return registry.import_offline(content)
    except (OSError, ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router_2.get(
    "/api/v1/configuration",
    response_model=ConfigurationSnapshot,
    tags=["configuration"],
)
async def get_effective_configuration(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    configuration: ConfigurationManagerDependency,
) -> ConfigurationSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="configuration",
        action=PermissionAction.VIEW,
    )
    return configuration.snapshot()


@router_2.post(
    "/api/v1/configuration/reload",
    response_model=ConfigurationSnapshot,
    tags=["configuration"],
)
async def reload_configuration(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    configuration: ConfigurationManagerDependency,
    feature_flags: FeatureFlagRepositoryDependency,
) -> ConfigurationSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="configuration",
        action=PermissionAction.MANAGE,
    )
    before = configuration.snapshot()
    try:
        after = configuration.reload()
    except NonReloadableConfigurationChanged as exc:
        await feature_flags.audit_configuration_reload(
            actor_id=str(actor.principal_id),
            outcome="REJECTED",
            changed_fields=exc.fields,
            reason="restart-required setting changed",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ConfigurationLoadError as exc:
        await feature_flags.audit_configuration_reload(
            actor_id=str(actor.principal_id),
            outcome="REJECTED",
            changed_fields=(),
            reason="candidate configuration failed validation",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    before_entries = {entry.name: entry for entry in before.entries}
    changed = tuple(
        entry.name
        for entry in after.entries
        if before_entries[entry.name].value != entry.value
        or before_entries[entry.name].source != entry.source
    )
    configure_observability(configuration.settings)
    await feature_flags.audit_configuration_reload(
        actor_id=str(actor.principal_id),
        outcome="SUCCESS",
        changed_fields=changed,
        reason="reload accepted",
    )
    return after


@router_2.get(
    "/api/v1/configuration/diagnostics",
    response_model=ConfigurationDiagnosticBundle,
    tags=["configuration"],
)
async def get_configuration_diagnostics(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    configuration: ConfigurationManagerDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> ConfigurationDiagnosticBundle:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        namespace=namespace,
        resource_type="configuration",
        action=PermissionAction.VIEW,
    )
    recent_errors = tuple(
        entry
        for entry in recent_redacted_logs(limit=50, tenant_id=tenant_id)
        if entry.get("level") in {"ERROR", "CRITICAL"}
    )
    return ConfigurationDiagnosticBundle(
        generatedAt=datetime.now(UTC),
        tenantId=tenant_id,
        namespace=namespace,
        configuration=configuration.snapshot(),
        featureFlags=await feature_flags.list_for_context(tenant_id, namespace=namespace),
        componentHealth={configuration.settings.service_role: "AVAILABLE"},
        versionMatrix={"amesh": __version__},
        recentErrors=recent_errors,
        selectedMetrics=diagnostic_metric_samples(),
    )


@router_3.get(
    "/api/v1/feature-flags",
    response_model=tuple[FeatureFlag, ...],
    tags=["configuration"],
)
async def list_feature_flags(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> tuple[FeatureFlag, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        namespace=namespace,
        resource_type="feature_flag",
        action=PermissionAction.VIEW,
    )
    return await feature_flags.list_for_context(tenant_id, namespace=namespace)


@router_3.get(
    "/api/v1/feature-flags/{key}/evaluate",
    response_model=FeatureFlagDecision,
    tags=["configuration"],
)
async def evaluate_feature_flag(
    key: str,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
    default: bool = False,
) -> FeatureFlagDecision:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        namespace=namespace,
        resource_type="feature_flag",
        action=PermissionAction.VIEW,
    )
    return await feature_flags.evaluate(
        key,
        tenant_id,
        namespace=namespace,
        default=default,
    )


@router_3.put(
    "/api/v1/feature-flags/{key}",
    response_model=FeatureFlag,
    tags=["configuration"],
)
async def put_feature_flag(
    key: str,
    request: FeatureFlagUpsertRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
) -> FeatureFlag:
    if key.startswith("admin-"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="reserved administration controls require the guarded administration API",
        )
    if request.scope is FeatureFlagScope.INSTANCE:
        if request.tenant_id is not None or request.namespace is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="instance feature flag cannot declare tenant or namespace",
            )
        scope_tenant = None
        scope_namespace = None
    else:
        if request.tenant_id is not None and request.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant unavailable")
        scope_tenant = tenant_id
        scope_namespace = request.namespace
        if request.scope is FeatureFlagScope.TENANT and scope_namespace is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="tenant feature flag cannot declare namespace",
            )
        if request.scope is FeatureFlagScope.NAMESPACE and scope_namespace is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="namespace feature flag requires namespace",
            )
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=scope_tenant,
        namespace=scope_namespace,
        resource_type="feature_flag",
        action=PermissionAction.MANAGE,
    )
    flag = FeatureFlag(
        key=key,
        scope=request.scope,
        enabled=request.enabled,
        tenant_id=scope_tenant,
        namespace=scope_namespace,
        description=request.description,
        updated_by=str(actor.principal_id),
    )
    try:
        return await feature_flags.upsert(
            flag,
            actor_id=str(actor.principal_id),
            expected_version=request.expected_version,
        )
    except FeatureFlagVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="feature flag version changed",
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tenant unavailable"
        ) from exc


@router_3.get(
    "/api/v1/admin/controls",
    response_model=tuple[AdministrationControl, ...],
    tags=["administration"],
)
async def list_administration_controls(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
) -> tuple[AdministrationControl, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="configuration",
        action=PermissionAction.VIEW,
    )
    return administration_controls(await feature_flags.list_for_context(tenant_id))


@router_3.post(
    "/api/v1/admin/controls/preview",
    response_model=AdministrationImpactPreview,
    tags=["administration"],
)
async def preview_administration_control(
    draft: AdministrationControlDraft,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
) -> AdministrationImpactPreview:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="configuration",
        action=PermissionAction.MANAGE,
    )
    return issue_administration_preview(
        draft,
        actor_id=str(actor.principal_id),
        tenant_id=tenant_id,
        signing_key=settings.amesh_token_pepper.get_secret_value(),
    )


@router_3.put(
    "/api/v1/admin/controls/{key}",
    response_model=AdministrationControl,
    tags=["administration"],
)
async def apply_administration_control(
    key: AdministrationControlKey,
    request: AdministrationApplyRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
) -> AdministrationControl:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="configuration",
        action=PermissionAction.MANAGE,
    )
    actor_id = str(actor.principal_id)
    try:
        if request.draft.key is not key:
            raise AdministrationApprovalError("administration control path does not match draft")
        verify_administration_approval(
            request,
            actor_id=actor_id,
            tenant_id=tenant_id,
            signing_key=settings.amesh_token_pepper.get_secret_value(),
        )
    except AdministrationApprovalError as exc:
        await feature_flags.audit_administration_action(
            tenant_id,
            actor_id=actor_id,
            action="administration-control.apply",
            resource_id=key.value,
            outcome="REJECTED",
            reason=str(exc),
            evidence={"enabled": request.draft.enabled, "value": request.draft.value},
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    flag = administration_control_flag(request.draft, tenant_id=tenant_id, actor_id=actor_id)
    try:
        persisted = await feature_flags.upsert(
            flag,
            actor_id=actor_id,
            expected_version=request.draft.expected_version,
            administration_audit={
                "action": "administration-control.apply",
                "resourceId": key.value,
                "reason": request.draft.reason,
                "evidence": {"enabled": request.draft.enabled, "value": request.draft.value},
            },
        )
    except FeatureFlagVersionConflict as exc:
        await feature_flags.audit_administration_action(
            tenant_id,
            actor_id=actor_id,
            action="administration-control.apply",
            resource_id=key.value,
            outcome="REJECTED",
            reason="administration control version changed",
            evidence={"expectedVersion": request.draft.expected_version},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="administration control version changed",
        ) from exc
    return next(control for control in administration_controls((persisted,)) if control.key is key)


@router_3.get(
    "/api/v1/admin/audit",
    response_model=tuple[AdministrationAuditEntry, ...],
    tags=["administration"],
)
async def list_administration_audit(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> tuple[AdministrationAuditEntry, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="audit",
        action=PermissionAction.VIEW,
    )
    return await feature_flags.list_administration_audit(tenant_id, limit=limit)


async def _authorize_plugin_policy_change(
    scope: PluginPolicyScope,
    namespace: str | None,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> None:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
        tenant_id=None if scope is PluginPolicyScope.INSTANCE else tenant_id,
        namespace=namespace,
    )


async def _authorize_admission_policy_change(
    document: PolicyDocument,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> None:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
        tenant_id=None if document.scope is PolicyScope.INSTANCE else tenant_id,
        namespace=document.namespace,
    )
