from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RunnerId(StrEnum):
    LOCAL = "local"
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

    @property
    def is_default(self) -> bool:
        return (
            not self.privileged and not self.read_only_root_filesystem and self.run_as_user is None
        )


class LocalProcessRunnerExtension(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    type: Literal[RunnerId.LOCAL]
    inherit_host_environment: bool = Field(default=False, alias="inheritHostEnvironment")
    allowed_host_environment: tuple[str, ...] = Field(default=(), alias="allowedHostEnvironment")


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

    @field_validator("labels")
    @classmethod
    def protect_owner_labels(cls, value: dict[str, str]) -> dict[str, str]:
        protected = {
            key for key in value if key == "app.kubernetes.io/name" or key.startswith("amesh.io/")
        }
        if protected:
            raise ValueError(f"runner labels are platform-owned: {', '.join(sorted(protected))}")
        return value


RunnerExtension = Annotated[
    LocalProcessRunnerExtension | KubernetesJobRunnerExtension,
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
        default=(RunnerId.LOCAL, RunnerId.KUBERNETES),
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
