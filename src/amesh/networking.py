from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import socket
import ssl
from collections.abc import Mapping, MutableMapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field

from amesh.config import Settings


class ForwardedHeaderRejected(ValueError):
    """Raised when an untrusted peer attempts to influence the external request origin."""


class CertificateDiagnostic(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    purpose: str
    configured: bool
    status: Literal["NOT_CONFIGURED", "READY", "MISSING", "INVALID"]
    fingerprint: str | None = None
    modified_at: datetime | None = Field(default=None, alias="modifiedAt")
    detail: str


class DnsDiagnostic(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    host: str
    status: Literal["RESOLVED", "FAILED"]
    addresses: tuple[str, ...] = ()
    detail: str


class ConnectionDiagnostic(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    scheme: str
    host: str
    port: int | None = None
    proxy: Literal["HTTP", "HTTPS", "BYPASSED", "DIRECT"]


class NetworkDiagnosticBundle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: int = Field(default=1, alias="schemaVersion")
    generated_at: datetime = Field(alias="generatedAt")
    inbound_tls_mode: str = Field(alias="inboundTlsMode")
    minimum_tls_version: str = Field(alias="minimumTlsVersion")
    client_authentication: str = Field(alias="clientAuthentication")
    topology: str
    private_endpoint: bool = Field(alias="privateEndpoint")
    external_base_url: str | None = Field(default=None, alias="externalBaseUrl")
    trusted_proxy_ranges: tuple[str, ...] = Field(alias="trustedProxyRanges")
    http_proxy_configured: bool = Field(alias="httpProxyConfigured")
    https_proxy_configured: bool = Field(alias="httpsProxyConfigured")
    no_proxy: tuple[str, ...] = Field(alias="noProxy")
    egress_allowed_hosts: tuple[str, ...] = Field(alias="egressAllowedHosts")
    allowed_private_hosts: tuple[str, ...] = Field(alias="allowedPrivateHosts")
    connections: tuple[ConnectionDiagnostic, ...]
    certificates: tuple[CertificateDiagnostic, ...]
    dns: tuple[DnsDiagnostic, ...]


def apply_trusted_forwarded_headers(
    scope: MutableMapping[str, Any],
    headers: Mapping[str, str],
    trusted_proxy_ranges: Sequence[str],
) -> None:
    """Validate and apply external-origin headers using the original socket peer."""

    normalized = {key.lower(): value.strip() for key, value in headers.items()}
    forwarded_names = {
        "forwarded",
        "x-forwarded-for",
        "x-forwarded-host",
        "x-forwarded-port",
        "x-forwarded-proto",
    }
    if not forwarded_names.intersection(normalized):
        return
    client = scope.get("client")
    peer = client[0] if isinstance(client, tuple | list) and client else None
    if not isinstance(peer, str) or not _address_in_ranges(peer, trusted_proxy_ranges):
        raise ForwardedHeaderRejected("forwarded headers are not accepted from this peer")

    standard = _parse_forwarded(normalized.get("forwarded"))
    proto = standard.get("proto") or _first_value(normalized.get("x-forwarded-proto"))
    host = standard.get("host") or _first_value(normalized.get("x-forwarded-host"))
    forwarded_for = standard.get("for") or _first_value(normalized.get("x-forwarded-for"))
    port = _first_value(normalized.get("x-forwarded-port"))

    if proto is not None:
        if proto not in {"http", "https"}:
            raise ForwardedHeaderRejected("forwarded protocol must be http or https")
        scope["scheme"] = proto
    if host is not None:
        parsed = urlsplit(f"//{host}")
        if (
            parsed.hostname is None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
        ):
            raise ForwardedHeaderRejected("forwarded host is invalid")
        selected_port = parsed.port
        if port is not None:
            try:
                selected_port = int(port)
            except ValueError as exc:
                raise ForwardedHeaderRejected("forwarded port is invalid") from exc
            if not 0 < selected_port <= 65535:
                raise ForwardedHeaderRejected("forwarded port is invalid")
        default_port = 443 if scope.get("scheme") == "https" else 80
        scope["server"] = (parsed.hostname, selected_port or default_port)
        encoded_host = host.encode("latin-1")
        scope["headers"] = [
            (name, encoded_host if name.lower() == b"host" else value)
            for name, value in scope.get("headers", [])
        ]
    if forwarded_for is not None:
        parsed_for = _forwarded_address(forwarded_for)
        client_port = client[1] if isinstance(client, tuple | list) and len(client) > 1 else 0
        scope["client"] = (parsed_for, client_port)


def outbound_http_client(
    url: str,
    *,
    http_proxy_url: str | None,
    https_proxy_url: str | None,
    no_proxy: Sequence[str],
    ca_file: str | None,
    client_certificate_file: str | None,
    client_key_file: str | None,
) -> httpx.AsyncClient:
    parsed = urlsplit(url)
    hostname = parsed.hostname or ""
    proxy: str | None = None
    if not host_matches(hostname, no_proxy):
        proxy = https_proxy_url if parsed.scheme == "https" else http_proxy_url
    verify: bool | ssl.SSLContext = True
    if ca_file is not None:
        verify = ssl.create_default_context(cafile=ca_file)
        verify.minimum_version = ssl.TLSVersion.TLSv1_2
    certificate: tuple[str, str] | None = None
    if client_certificate_file is not None and client_key_file is not None:
        certificate = (client_certificate_file, client_key_file)
    return httpx.AsyncClient(
        proxy=proxy,
        verify=verify,
        cert=certificate,
        follow_redirects=False,
        trust_env=False,
    )


def host_matches(hostname: str, patterns: Sequence[str]) -> bool:
    normalized = hostname.rstrip(".").lower()
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        address = None
    for raw_pattern in patterns:
        pattern = raw_pattern.strip().lower()
        if pattern == "*":
            return True
        if not pattern:
            continue
        candidate = pattern.rsplit(":", 1)[0] if pattern.count(":") == 1 else pattern
        if candidate.startswith("*."):
            suffix = candidate[1:]
            if normalized.endswith(suffix) and normalized != suffix[1:]:
                return True
            continue
        if candidate.startswith(".") and (
            normalized == candidate[1:] or normalized.endswith(candidate)
        ):
            return True
        if normalized == candidate:
            return True
        if address is not None:
            try:
                if address in ipaddress.ip_network(candidate, strict=False):
                    return True
            except ValueError:
                continue
    return False


async def build_network_diagnostics(settings: Settings) -> NetworkDiagnosticBundle:
    connections = _connection_diagnostics(settings)
    hosts = tuple(
        dict.fromkeys([*settings.network_diagnostic_hosts, *(item.host for item in connections)])
    )
    dns = await asyncio.gather(*(_resolve_host(host) for host in hosts))
    certificates = _certificate_diagnostics(settings)
    return NetworkDiagnosticBundle(
        generatedAt=datetime.now(UTC),
        inboundTlsMode=settings.network_inbound_tls_mode,
        minimumTlsVersion=settings.network_tls_minimum_version,
        clientAuthentication=settings.network_tls_client_auth,
        topology=settings.network_topology,
        privateEndpoint=settings.network_private_endpoint,
        externalBaseUrl=settings.network_external_base_url,
        trustedProxyRanges=settings.network_trusted_proxy_ranges,
        httpProxyConfigured=settings.network_http_proxy_url is not None,
        httpsProxyConfigured=settings.network_https_proxy_url is not None,
        noProxy=settings.network_no_proxy,
        egressAllowedHosts=settings.network_egress_allowed_hosts,
        allowedPrivateHosts=settings.core_http_allowed_private_hosts,
        connections=connections,
        certificates=certificates,
        dns=tuple(dns),
    )


def _parse_forwarded(value: str | None) -> dict[str, str]:
    if value is None:
        return {}
    selected: dict[str, str] = {}
    for item in value.split(",", 1)[0].split(";"):
        key, separator, raw_value = item.strip().partition("=")
        if not separator or key.lower() not in {"for", "host", "proto"}:
            continue
        candidate = (
            raw_value.strip().strip('"').lower()
            if key.lower() == "proto"
            else raw_value.strip().strip('"')
        )
        if not candidate or any(character in candidate for character in "\r\n"):
            raise ForwardedHeaderRejected("forwarded header is invalid")
        selected[key.lower()] = candidate
    return selected


def _first_value(value: str | None) -> str | None:
    if value is None:
        return None
    selected = value.split(",", 1)[0].strip()
    if not selected or any(character in selected for character in "\r\n"):
        raise ForwardedHeaderRejected("forwarded header is invalid")
    return selected


def _forwarded_address(value: str) -> str:
    selected = value.strip().strip('"')
    if selected.startswith("["):
        closing = selected.find("]")
        if closing == -1:
            raise ForwardedHeaderRejected("forwarded client address is invalid")
        candidate = selected[1:closing]
    else:
        candidate = selected.rsplit(":", 1)[0] if selected.count(":") == 1 else selected
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError as exc:
        raise ForwardedHeaderRejected("forwarded client address is invalid") from exc


def _address_in_ranges(address: str, ranges: Sequence[str]) -> bool:
    try:
        selected = ipaddress.ip_address(address)
    except ValueError:
        return False
    return any(selected in ipaddress.ip_network(value, strict=False) for value in ranges)


def _connection_diagnostics(settings: Settings) -> tuple[ConnectionDiagnostic, ...]:
    candidates: list[tuple[str, str]] = [
        ("postgresql", settings.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)),
        ("object-storage", settings.object_storage_endpoint),
    ]
    if settings.otel_exporter_otlp_endpoint is not None:
        candidates.append(("telemetry", settings.otel_exporter_otlp_endpoint))
    candidates.extend(
        (f"plugin-registry-{index}", value)
        for index, value in enumerate(settings.plugin_registries, start=1)
        if urlsplit(value).scheme in {"http", "https"}
    )
    result: list[ConnectionDiagnostic] = []
    for name, value in candidates:
        parsed = urlsplit(value)
        if parsed.hostname is None:
            continue
        proxy: Literal["HTTP", "HTTPS", "BYPASSED", "DIRECT"]
        if host_matches(parsed.hostname, settings.network_no_proxy):
            proxy = "BYPASSED"
        elif parsed.scheme == "https" and settings.network_https_proxy_url is not None:
            proxy = "HTTPS"
        elif parsed.scheme == "http" and settings.network_http_proxy_url is not None:
            proxy = "HTTP"
        else:
            proxy = "DIRECT"
        result.append(
            ConnectionDiagnostic(
                name=name,
                scheme=parsed.scheme,
                host=parsed.hostname,
                port=parsed.port,
                proxy=proxy,
            )
        )
    return tuple(result)


def _certificate_diagnostics(settings: Settings) -> tuple[CertificateDiagnostic, ...]:
    paths = (
        ("inbound-server", settings.network_tls_certificate_file),
        ("inbound-client-ca", settings.network_tls_client_ca_file),
        ("outbound-ca", settings.network_outbound_ca_file),
        ("outbound-client", settings.network_outbound_client_certificate_file),
    )
    diagnostics = [_certificate_file(purpose, path) for purpose, path in paths]
    if (
        settings.network_tls_certificate_file is not None
        and settings.network_tls_private_key_file is not None
    ):
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(
                settings.network_tls_certificate_file,
                settings.network_tls_private_key_file,
            )
        except (OSError, ssl.SSLError) as exc:
            diagnostics[0] = diagnostics[0].model_copy(
                update={
                    "status": "INVALID",
                    "detail": f"certificate/key validation failed: {type(exc).__name__}",
                }
            )
    return tuple(diagnostics)


def _certificate_file(purpose: str, value: str | None) -> CertificateDiagnostic:
    if value is None:
        return CertificateDiagnostic(
            purpose=purpose,
            configured=False,
            status="NOT_CONFIGURED",
            detail="not configured",
        )
    path = Path(value)
    try:
        payload = path.read_bytes()
        stat = path.stat()
    except OSError as exc:
        return CertificateDiagnostic(
            purpose=purpose,
            configured=True,
            status="MISSING",
            detail=f"certificate material is unavailable: {type(exc).__name__}",
        )
    if b"-----BEGIN CERTIFICATE-----" not in payload:
        return CertificateDiagnostic(
            purpose=purpose,
            configured=True,
            status="INVALID",
            detail="file does not contain a PEM certificate",
        )
    return CertificateDiagnostic(
        purpose=purpose,
        configured=True,
        status="READY",
        fingerprint=hashlib.sha256(payload).hexdigest(),
        modifiedAt=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
        detail="PEM certificate is readable",
    )


async def _resolve_host(host: str) -> DnsDiagnostic:
    def resolve() -> tuple[str, ...]:
        return tuple(
            sorted(
                {str(ipaddress.ip_address(item[4][0])) for item in socket.getaddrinfo(host, None)}
            )
        )

    try:
        addresses = await asyncio.wait_for(asyncio.to_thread(resolve), timeout=3)
    except (OSError, TimeoutError, ValueError) as exc:
        return DnsDiagnostic(
            host=host,
            status="FAILED",
            detail=f"resolution failed: {type(exc).__name__}",
        )
    return DnsDiagnostic(
        host=host,
        status="RESOLVED",
        addresses=addresses,
        detail=f"resolved {len(addresses)} address(es)",
    )
