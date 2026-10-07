"""Shared construction of the authentication service used by app and CLI roots."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from pydantic import SecretStr

from amesh.authentication import AuthenticationService
from amesh.ports.authentication_repository import AuthenticationRepository


class AuthenticationSettings(Protocol):
    """The settings subset needed to configure ``AuthenticationService``."""

    @property
    def amesh_token_pepper(self) -> SecretStr: ...

    @property
    def auth_policy(self) -> str: ...

    @property
    def auth_session_idle_seconds(self) -> int: ...

    @property
    def auth_session_absolute_seconds(self) -> int: ...

    @property
    def auth_session_rotation_seconds(self) -> int: ...

    @property
    def auth_session_overlap_seconds(self) -> int: ...

    @property
    def auth_login_rate_limit_per_minute(self) -> int: ...

    @property
    def auth_login_max_failures(self) -> int: ...

    @property
    def auth_login_lock_seconds(self) -> int: ...


AuthenticationServiceFactory = Callable[..., AuthenticationService]


def build_authentication_service(
    settings: AuthenticationSettings,
    repository: AuthenticationRepository,
    *,
    service_factory: AuthenticationServiceFactory = AuthenticationService,
) -> AuthenticationService:
    """Build the shared authentication service from injected repositories and factories."""

    return service_factory(
        repository,
        token_pepper=settings.amesh_token_pepper,
        policy=settings.auth_policy,
        session_idle_seconds=settings.auth_session_idle_seconds,
        session_absolute_seconds=settings.auth_session_absolute_seconds,
        session_rotation_seconds=settings.auth_session_rotation_seconds,
        session_overlap_seconds=settings.auth_session_overlap_seconds,
        login_rate_limit_per_minute=settings.auth_login_rate_limit_per_minute,
        login_max_failures=settings.auth_login_max_failures,
        login_lock_seconds=settings.auth_login_lock_seconds,
    )


__all__ = ["AuthenticationSettings", "build_authentication_service"]
