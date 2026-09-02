from __future__ import annotations

from amesh.domain.plugin_policy import (
    EffectivePluginPolicy,
    PluginPolicyDecision,
    PluginPolicyStage,
    PluginPolicySubject,
    evaluate_plugin_policy,
)
from amesh.dsl import FlowDefinition
from amesh.plugin_sdk import (
    PLUGIN_RESOLUTION_VERSION,
    PluginCatalogManager,
    PluginManifest,
    PluginResolution,
    PluginResolver,
)
from amesh.ports import PluginPolicyRepository


class PluginPolicyDenied(ValueError):
    def __init__(self, decision: PluginPolicyDecision) -> None:
        self.decision = decision
        denied = ", ".join(
            f"{item.subject.package}@{item.subject.version} ({item.reason_code})"
            for item in decision.subjects
            if not item.allowed
        )
        super().__init__(f"plugin policy denied {decision.stage.value.lower()}: {denied}")


class PluginResolutionQuarantined(ValueError):
    """Raised once an incompatible legacy resolution has disabled its owning flow."""


class PluginPolicyService:
    def __init__(
        self,
        repository: PluginPolicyRepository,
        catalog: PluginCatalogManager,
        *,
        default_allow: bool = False,
    ) -> None:
        self._repository = repository
        self._catalog = catalog
        self._default_allow = default_allow

    async def effective_policy(
        self,
        tenant_id: str,
        *,
        namespace: str | None,
    ) -> EffectivePluginPolicy:
        return await self._repository.effective_policy(
            tenant_id,
            namespace=namespace,
            default_allow=self._default_allow,
        )

    async def evaluate_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        stage: PluginPolicyStage,
        actor_id: str,
        enforce: bool = False,
    ) -> PluginPolicyDecision:
        resolution_payload = None
        if stage is PluginPolicyStage.EXECUTION:
            resolution_payload = await self._repository.frozen_resolution(
                tenant_id,
                flow.namespace,
                flow.id,
                flow.revision,
            )
        if resolution_payload is None:
            resolution_payload = (
                PluginResolver(self._catalog.snapshot).resolve_flow(flow).revision_payload()
            )
        elif resolution_payload.get("schemaVersion") != PLUGIN_RESOLUTION_VERSION:
            try:
                replacement = (
                    PluginResolver(self._catalog.snapshot).resolve_flow(flow).revision_payload()
                )
            except Exception as exc:
                reason = f"{type(exc).__name__}: {exc}"
                await self._repository.quarantine_legacy_resolution(
                    tenant_id,
                    flow.namespace,
                    flow.id,
                    flow.revision,
                    expected=resolution_payload,
                    actor_id=actor_id,
                    reason=reason,
                )
                raise PluginResolutionQuarantined(
                    f"flow {flow.namespace}/{flow.id} revision {flow.revision} was disabled "
                    "because its legacy plugin resolution cannot be upgraded"
                ) from exc
            resolution_payload = await self._repository.migrate_legacy_resolution(
                tenant_id,
                flow.namespace,
                flow.id,
                flow.revision,
                expected=resolution_payload,
                replacement=replacement,
                actor_id=actor_id,
            )
        subjects = self.subjects_from_resolution(resolution_payload)
        effective = await self.effective_policy(tenant_id, namespace=flow.namespace)
        decision = evaluate_plugin_policy(
            subjects,
            effective.rules,
            effective.quarantines,
            tenant_id=tenant_id,
            namespace=flow.namespace,
            stage=stage,
            default_allow=self._default_allow,
            flow_id=flow.id,
            flow_revision=flow.revision,
        )
        await self._repository.record_decision(decision, actor_id=actor_id)
        if enforce and not decision.allowed:
            raise PluginPolicyDenied(decision)
        return decision

    async def preview_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        stage: PluginPolicyStage,
        resolution_payload: dict[str, object] | None = None,
    ) -> PluginPolicyDecision:
        """Evaluate policy without recording a decision or mutating runtime state."""

        resolved = resolution_payload or (
            PluginResolver(self._catalog.snapshot).resolve_flow(flow).revision_payload()
        )
        if resolved.get("schemaVersion") != PLUGIN_RESOLUTION_VERSION:
            resolved = PluginResolver(self._catalog.snapshot).resolve_flow(flow).revision_payload()
        effective = await self.effective_policy(tenant_id, namespace=flow.namespace)
        return evaluate_plugin_policy(
            self.subjects_from_resolution(resolved),
            effective.rules,
            effective.quarantines,
            tenant_id=tenant_id,
            namespace=flow.namespace,
            stage=stage,
            default_allow=self._default_allow,
            flow_id=flow.id,
            flow_revision=flow.revision,
        )

    async def enforce_flow(
        self,
        flow: FlowDefinition,
        tenant_id: str,
        stage: PluginPolicyStage,
        actor_id: str,
    ) -> None:
        await self.evaluate_flow(
            flow,
            tenant_id=tenant_id,
            stage=stage,
            actor_id=actor_id,
            enforce=True,
        )

    async def evaluate_subjects(
        self,
        subjects: tuple[PluginPolicySubject, ...],
        *,
        tenant_id: str,
        namespace: str,
        stage: PluginPolicyStage,
        actor_id: str,
        enforce: bool = False,
    ) -> PluginPolicyDecision:
        effective = await self.effective_policy(
            tenant_id,
            namespace=namespace or None,
        )
        decision = evaluate_plugin_policy(
            subjects,
            effective.rules,
            effective.quarantines,
            tenant_id=tenant_id,
            namespace=namespace,
            stage=stage,
            default_allow=self._default_allow,
        )
        await self._repository.record_decision(decision, actor_id=actor_id)
        if enforce and not decision.allowed:
            raise PluginPolicyDenied(decision)
        return decision

    async def enforce_manifest_administration(
        self,
        manifest: PluginManifest,
        content_digest: str,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> None:
        subject = _manifest_subject(manifest, content_digest)
        await self.evaluate_subjects(
            (subject,),
            tenant_id=tenant_id,
            namespace="__instance__",
            stage=PluginPolicyStage.ADMINISTRATION,
            actor_id=actor_id,
            enforce=True,
        )

    def subjects_from_resolution(
        self,
        payload: dict[str, object],
    ) -> tuple[PluginPolicySubject, ...]:
        resolution = PluginResolution.model_validate(payload)
        catalog_by_identity = {
            record.identity: record
            for record in self._catalog.snapshot.packages
            if record.identity is not None
        }
        types_by_package: dict[str, set[str]] = {}
        for resource in resolution.resources:
            types_by_package.setdefault(resource.package, set()).add(
                f"{resource.kind.value}:{resource.type}"
            )
        subjects: list[PluginPolicySubject] = []
        for package in resolution.packages:
            record = catalog_by_identity.get((package.name, package.version))
            manifest = record.manifest if record is not None else None
            capabilities: set[str] = set()
            if manifest is not None:
                capabilities.update(manifest.capabilities.required)
                capabilities.add(f"network:{manifest.capabilities.network_access.value}")
                capabilities.add(f"filesystem:{manifest.capabilities.filesystem_access.value}")
                capabilities.update(
                    f"egress:{value}" for value in manifest.capabilities.allowed_egress
                )
                capabilities.update(
                    f"secret:{value}" for value in manifest.capabilities.secret_scopes
                )
            subjects.append(
                PluginPolicySubject(
                    package=package.name,
                    version=package.version,
                    vendor=manifest.vendor if manifest is not None else "unknown",
                    pluginTypes=tuple(sorted(types_by_package.get(package.name, ()))),
                    capabilities=tuple(sorted(capabilities)),
                    contentDigest=package.content_digest,
                )
            )
        return tuple(subjects)


def _manifest_subject(manifest: PluginManifest, content_digest: str) -> PluginPolicySubject:
    capabilities = set(manifest.capabilities.required)
    capabilities.add(f"network:{manifest.capabilities.network_access.value}")
    capabilities.add(f"filesystem:{manifest.capabilities.filesystem_access.value}")
    capabilities.update(f"egress:{value}" for value in manifest.capabilities.allowed_egress)
    capabilities.update(f"secret:{value}" for value in manifest.capabilities.secret_scopes)
    return PluginPolicySubject(
        package=manifest.name,
        version=manifest.version,
        vendor=manifest.vendor,
        pluginTypes=tuple(
            sorted(
                f"{entry.type.value}:{entry.resolved_resource_type}"
                for entry in manifest.entry_points
            )
        ),
        capabilities=tuple(sorted(capabilities)),
        contentDigest=content_digest,
    )
