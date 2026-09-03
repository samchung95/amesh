"""Provider- and persistence-neutral error vocabulary."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from amesh.domain.resources import ResourceVersionConflict


class PortError(RuntimeError):
    """Base failure exposed by a port boundary."""


class NotFoundError(PortError, LookupError):
    """A requested resource does not exist within the caller's scope."""

    def __init__(self, resource: str, key: Any, *, message: str | None = None) -> None:
        self.resource = resource
        self.key = key
        super().__init__(message or f"{resource} not found: {key}")


class VersionConflict(PortError):
    """A write used a stale optimistic-concurrency version."""

    def __init__(
        self,
        message: str | None = None,
        *,
        resource: str = "resource",
        expected: int | str | None = None,
        actual: int | str | None = None,
    ) -> None:
        self.resource = resource
        self.expected = expected
        self.actual = actual
        detail = message or f"{resource} version conflict"
        if expected is not None or actual is not None:
            detail = f"{detail} (expected={expected}, actual={actual})"
        super().__init__(detail)


class RepositoryVersionConflict(ResourceVersionConflict, VersionConflict):
    """Bridge resource conflicts through both domain and port error boundaries."""


class WorkflowAppVersionConflict(VersionConflict):
    """A workflow app write used a stale resource version."""


class HumanTaskConflict(VersionConflict):
    """A human-task command conflicts with an existing decision."""


class OperationalControlVersionConflict(VersionConflict):
    """An operational-control write used a stale resource version."""


class LifecycleVersionConflict(VersionConflict):
    """A lifecycle write used a stale resource version."""


class ProviderError(PortError):
    """Provider-neutral failure raised at an external provider boundary."""


class ProviderErrorDiagnostic(Protocol):
    """Sanitized provider failure details safe to expose across an adapter boundary."""

    def as_dict(self) -> Mapping[str, object]: ...


class ProviderDiagnosticError(ProviderError):
    """A provider failure carrying sanitized, adapter-neutral diagnostic details."""

    diagnostic: ProviderErrorDiagnostic


__all__ = [
    "HumanTaskConflict",
    "LifecycleVersionConflict",
    "NotFoundError",
    "OperationalControlVersionConflict",
    "PortError",
    "ProviderDiagnosticError",
    "ProviderError",
    "ProviderErrorDiagnostic",
    "RepositoryVersionConflict",
    "VersionConflict",
    "WorkflowAppVersionConflict",
]
