"""Shared construction of the bounded outbound HTTP task policy."""

from __future__ import annotations

from typing import Protocol

from pydantic import SecretStr

from amesh.tasks.http import HttpTaskPolicy


class HttpPolicySettings(Protocol):
    """The settings subset required by core HTTP and agent handlers."""

    network_egress_allowed_hosts: tuple[str, ...]
    core_http_allowed_private_hosts: tuple[str, ...]
    core_http_max_response_bytes: int
    core_http_max_pages: int
    core_http_max_redirects: int
    network_http_proxy_url: SecretStr | None
    network_https_proxy_url: SecretStr | None
    network_no_proxy: tuple[str, ...]
    network_outbound_ca_file: str | None
    network_outbound_client_certificate_file: str | None
    network_outbound_client_key_file: str | None


def _secret_value(value: SecretStr | None) -> str | None:
    return value.get_secret_value() if value is not None else None


def build_http_task_policy(
    settings: HttpPolicySettings,
    *,
    maximum_redirects: int | None = None,
) -> HttpTaskPolicy:
    """Build the common HTTP policy from a settings object or compatible double."""

    return HttpTaskPolicy(
        allowed_hosts=settings.network_egress_allowed_hosts,
        allowed_private_hosts=frozenset(settings.core_http_allowed_private_hosts),
        maximum_response_bytes=settings.core_http_max_response_bytes,
        maximum_pages=settings.core_http_max_pages,
        maximum_redirects=(
            settings.core_http_max_redirects if maximum_redirects is None else maximum_redirects
        ),
        http_proxy_url=_secret_value(settings.network_http_proxy_url),
        https_proxy_url=_secret_value(settings.network_https_proxy_url),
        no_proxy=settings.network_no_proxy,
        ca_file=settings.network_outbound_ca_file,
        client_certificate_file=settings.network_outbound_client_certificate_file,
        client_key_file=settings.network_outbound_client_key_file,
    )


build_http_policy = build_http_task_policy

__all__ = ["HttpPolicySettings", "build_http_policy", "build_http_task_policy"]
