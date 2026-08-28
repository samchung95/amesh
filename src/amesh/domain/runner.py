from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RunnerId(StrEnum):
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"


class RunnerNetworkAccess(StrEnum):
    INHERIT = "inherit"
    NONE = "none"
    RESTRICTED = "restricted"


class RunnerNetworkPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    access: RunnerNetworkAccess = RunnerNetworkAccess.INHERIT
    allowed_egress: tuple[str, ...] = Field(default=(), alias="allowedEgress")

    @model_validator(mode="after")
    def validate_allowed_egress(self) -> RunnerNetworkPolicy:
        if self.access is not RunnerNetworkAccess.RESTRICTED and self.allowed_egress:
            raise ValueError("allowedEgress requires restricted network access")
        return self


class RunnerSecurityPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    privileged: bool = False
    read_only_root_filesystem: bool = Field(default=False, alias="readOnlyRootFilesystem")
    run_as_user: int | None = Field(default=None, alias="runAsUser", ge=0)
    capability_add: tuple[str, ...] = Field(default=(), alias="capabilityAdd")
    capability_drop: tuple[str, ...] = Field(default=("ALL",), alias="capabilityDrop")
    no_new_privileges: bool = Field(default=True, alias="noNewPrivileges")

    @property
    def is_default(self) -> bool:
        return (
            not self.privileged
            and not self.read_only_root_filesystem
            and self.run_as_user is None
            and not self.capability_add
            and self.capability_drop == ("ALL",)
            and self.no_new_privileges
        )


class LocalProcessRunnerExtension(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    type: Literal[RunnerId.LOCAL]
    inherit_host_environment: bool = Field(default=False, alias="inheritHostEnvironment")
    allowed_host_environment: tuple[str, ...] = Field(default=(), alias="allowedHostEnvironment")
    shell: bool = False


class LocalProcessResourceLimits(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    cpu_seconds: int | None = Field(default=None, alias="cpuSeconds", ge=1)
    memory_bytes: int | None = Field(default=None, alias="memoryBytes", ge=1)
    file_size_bytes: int | None = Field(default=None, alias="fileSizeBytes", ge=1)
    open_files: int | None = Field(default=None, alias="openFiles", ge=1)
    processes: int | None = Field(default=None, ge=1)


class DockerImagePullPolicy(StrEnum):
    NEVER = "NEVER"
    IF_NOT_PRESENT = "IF_NOT_PRESENT"
    ALWAYS = "ALWAYS"


class DockerContainerRunnerExtension(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    type: Literal[RunnerId.DOCKER]
    pull_policy: DockerImagePullPolicy = Field(
        default=DockerImagePullPolicy.IF_NOT_PRESENT,
        alias="pullPolicy",
    )
    platform: str | None = Field(default=None, min_length=1, max_length=128)
    runtime: str | None = Field(default=None, min_length=1, max_length=128)
    registry_username_variable: str | None = Field(
        default=None,
        alias="registryUsernameVariable",
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    )
    registry_password_variable: str | None = Field(
        default=None,
        alias="registryPasswordVariable",
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    )

    @model_validator(mode="after")
    def validate_registry_credentials(self) -> DockerContainerRunnerExtension:
        if (self.registry_username_variable is None) != (self.registry_password_variable is None):
            raise ValueError(
                "registryUsernameVariable and registryPasswordVariable must be configured together"
            )
        return self


class DockerContainerResourceLimits(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    cpus: float | None = Field(default=None, gt=0)
    memory_bytes: int | None = Field(default=None, alias="memoryBytes", ge=4 * 1024 * 1024)
    processes: int | None = Field(default=None, ge=1)
    open_files: int | None = Field(default=None, alias="openFiles", ge=1)


class DockerImagePolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    allowed_registries: tuple[str, ...] = Field(
        default=("docker.io",),
        alias="allowedRegistries",
        min_length=1,
    )
    allow_tags: bool = Field(default=False, alias="allowTags")
    require_signature: bool = Field(default=False, alias="requireSignature")
    require_vulnerability_scan: bool = Field(
        default=False,
        alias="requireVulnerabilityScan",
    )


class KubernetesJobRunnerExtension(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    type: Literal[RunnerId.KUBERNETES]
    service_account_name: str | None = Field(
        default=None,
        alias="serviceAccountName",
        min_length=1,
        max_length=253,
    )
    labels: dict[str, str] = Field(default_factory=dict)
    node_selector: dict[str, str] = Field(default_factory=dict, alias="nodeSelector")
    runtime_class_name: str | None = Field(
        default=None,
        alias="runtimeClassName",
        min_length=1,
        max_length=253,
    )

    @field_validator("labels")
    @classmethod
    def protect_owner_labels(cls, value: dict[str, str]) -> dict[str, str]:
        protected = {
            key for key in value if key == "app.kubernetes.io/name" or key.startswith("amesh.io/")
        }
        if protected:
            raise ValueError(f"runner labels are platform-owned: {', '.join(sorted(protected))}")
        return value


class KubernetesJobTemplate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    image_pull_secrets: tuple[str, ...] = Field(default=(), alias="imagePullSecrets")
    priority_class_name: str | None = Field(default=None, alias="priorityClassName")
    scheduler_name: str | None = Field(default=None, alias="schedulerName")
    tolerations: tuple[dict[str, object], ...] = ()
    affinity: dict[str, object] = Field(default_factory=dict)
    backoff_limit: int = Field(default=1, alias="backoffLimit", ge=0, le=100)
    ttl_seconds_after_finished: int | None = Field(
        default=None,
        alias="ttlSecondsAfterFinished",
        ge=0,
    )
    transfer_image: str = Field(
        default="busybox:1.37.0",
        alias="transferImage",
        min_length=1,
    )

    @field_validator("labels")
    @classmethod
    def protect_owner_labels(cls, value: dict[str, str]) -> dict[str, str]:
        return KubernetesJobRunnerExtension.protect_owner_labels(value)


class KubernetesRunnerProfile(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(
        min_length=1,
        max_length=63,
        pattern=r"^[A-Za-z0-9]([A-Za-z0-9_.-]*[A-Za-z0-9])?$",
    )
    namespace_prefix: str = Field(default="", alias="namespacePrefix", max_length=255)
    worker_group: str | None = Field(
        default=None,
        alias="workerGroup",
        min_length=1,
        max_length=128,
    )
    context: str | None = Field(default=None, min_length=1, max_length=253)
    namespace: str = Field(default="amesh-tasks", min_length=1, max_length=63)
    service_account_name: str | None = Field(
        default=None,
        alias="serviceAccountName",
        min_length=1,
        max_length=253,
    )
    node_selector: dict[str, str] = Field(default_factory=dict, alias="nodeSelector")
    runtime_class_name: str | None = Field(
        default=None,
        alias="runtimeClassName",
        min_length=1,
        max_length=253,
    )
    workload_identity: bool = Field(default=False, alias="workloadIdentity")
    template: KubernetesJobTemplate = Field(default_factory=KubernetesJobTemplate)

    @model_validator(mode="after")
    def validate_workload_identity(self) -> KubernetesRunnerProfile:
        if self.workload_identity and self.service_account_name is None:
            raise ValueError("workloadIdentity requires serviceAccountName")
        return self

    def matches(self, namespace: str, worker_group: str | None) -> bool:
        namespace_match = not self.namespace_prefix or (
            namespace == self.namespace_prefix or namespace.startswith(f"{self.namespace_prefix}.")
        )
        worker_match = self.worker_group is None or self.worker_group == worker_group
        return namespace_match and worker_match


class KubernetesRunnerProfileSet:
    def __init__(self, profiles: tuple[KubernetesRunnerProfile, ...]) -> None:
        if not profiles:
            raise ValueError("at least one Kubernetes runner profile is required")
        names = [item.name for item in profiles]
        if len(names) != len(set(names)):
            raise ValueError("Kubernetes runner profile names must be unique")
        scopes = [(item.namespace_prefix, item.worker_group) for item in profiles]
        if len(scopes) != len(set(scopes)):
            raise ValueError("Kubernetes runner profile scopes must be unique")
        self._profiles = profiles

    @property
    def profiles(self) -> tuple[KubernetesRunnerProfile, ...]:
        return self._profiles

    def select(self, namespace: str, worker_group: str | None) -> KubernetesRunnerProfile:
        matching = [item for item in self._profiles if item.matches(namespace, worker_group)]
        matching.sort(
            key=lambda item: (
                item.worker_group is not None,
                len(item.namespace_prefix.split(".")) if item.namespace_prefix else 0,
            ),
            reverse=True,
        )
        if not matching:
            raise RunnerPolicyViolation(
                f"no Kubernetes runner profile matches namespace {namespace!r} "
                f"and worker group {worker_group or '*'}"
            )
        return matching[0]


RunnerExtension = Annotated[
    LocalProcessRunnerExtension | DockerContainerRunnerExtension | KubernetesJobRunnerExtension,
    Field(discriminator="type"),
]


class RunnerPolicyViolation(ValueError):
    """Raised when runner selection is prohibited or unavailable."""


class RunnerPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    namespace_prefix: str = Field(default="", alias="namespacePrefix", max_length=255)
    worker_group: str | None = Field(
        default=None, alias="workerGroup", min_length=1, max_length=128
    )
    default_runner: RunnerId | None = Field(default=None, alias="defaultRunner")
    allowed_runners: tuple[RunnerId, ...] = Field(
        default=(RunnerId.LOCAL, RunnerId.DOCKER, RunnerId.KUBERNETES),
        alias="allowedRunners",
        min_length=1,
    )

    @field_validator("allowed_runners")
    @classmethod
    def validate_allowed_runners(cls, value: tuple[RunnerId, ...]) -> tuple[RunnerId, ...]:
        if len(value) != len(set(value)):
            raise ValueError("allowedRunners must be unique")
        return value

    @model_validator(mode="after")
    def validate_default_runner(self) -> RunnerPolicy:
        if self.default_runner is not None and self.default_runner not in self.allowed_runners:
            raise ValueError("defaultRunner must be present in allowedRunners")
        return self

    def matches(self, namespace: str, worker_group: str | None) -> bool:
        namespace_match = not self.namespace_prefix or (
            namespace == self.namespace_prefix or namespace.startswith(f"{self.namespace_prefix}.")
        )
        worker_match = self.worker_group is None or self.worker_group == worker_group
        return namespace_match and worker_match


class RunnerPolicySet:
    def __init__(self, policies: tuple[RunnerPolicy, ...] = ()) -> None:
        scopes = [(item.namespace_prefix, item.worker_group) for item in policies]
        if len(scopes) != len(set(scopes)):
            raise ValueError("runner policy scopes must be unique")
        self._policies = policies

    def select(
        self,
        *,
        namespace: str,
        worker_group: str | None,
        requested: RunnerId | None,
        fallback: RunnerId,
        available: set[RunnerId] | frozenset[RunnerId],
    ) -> RunnerId:
        matching = [item for item in self._policies if item.matches(namespace, worker_group)]
        matching.sort(
            key=lambda item: (
                item.worker_group is not None,
                len(item.namespace_prefix.split(".")) if item.namespace_prefix else 0,
            ),
            reverse=True,
        )
        policy = matching[0] if matching else RunnerPolicy()
        selected = requested or policy.default_runner or fallback
        if selected not in policy.allowed_runners:
            scope = policy.namespace_prefix or "*"
            group = policy.worker_group or "*"
            raise RunnerPolicyViolation(
                f"runner {selected.value!r} is prohibited for namespace {scope!r} "
                f"and worker group {group!r}"
            )
        if selected not in available:
            raise RunnerPolicyViolation(f"runner {selected.value!r} is not available")
        return selected
