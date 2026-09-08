from __future__ import annotations

import asyncio
import socket
import ssl
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from amesh.config import Settings
from amesh.networking import (
    ForwardedHeaderRejected,
    apply_trusted_forwarded_headers,
    build_network_diagnostics,
    host_matches,
)
from amesh.server import build_uvicorn_config
from amesh.tasks import HttpTaskPolicy
from amesh.tasks.http import validate_http_destination


def _write_certificate_pair(tmp_path: Path, name: str) -> tuple[Path, Path]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(minutes=1))
        .not_valid_after(datetime.now(UTC) + timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    key_file = tmp_path / f"{name}.key"
    cert_file = tmp_path / f"{name}.crt"
    key_file.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    cert_file.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    return key_file, cert_file


def test_direct_tls_builds_modern_mtls_context_and_rotates_mounted_material(
    tmp_path: Path,
) -> None:
    first_key, first_cert = _write_certificate_pair(tmp_path, "first")
    second_key, second_cert = _write_certificate_pair(tmp_path, "second")
    settings = Settings(
        _env_file=None,
        network_inbound_tls_mode="direct",
        network_tls_certificate_file=str(first_cert),
        network_tls_private_key_file=str(first_key),
        network_tls_client_ca_file=str(first_cert),
        network_tls_client_auth="required",
    )

    config = build_uvicorn_config(settings)
    config.load()
    assert config.proxy_headers is False
    assert config.ssl is not None
    assert config.ssl.minimum_version == ssl.TLSVersion.TLSv1_2
    assert config.ssl.verify_mode == ssl.CERT_REQUIRED
    assert all(cipher["protocol"] != "SSLv3" for cipher in config.ssl.get_ciphers())

    rotated = build_uvicorn_config(
        settings.model_copy(
            update={
                "network_tls_certificate_file": str(second_cert),
                "network_tls_private_key_file": str(second_key),
            }
        )
    )
    rotated.load()
    assert rotated.ssl is not None
    assert first_cert.read_bytes() != second_cert.read_bytes()


def test_forwarded_headers_require_a_trusted_socket_peer() -> None:
    untrusted_scope: dict[str, object] = {
        "scheme": "http",
        "client": ("203.0.113.8", 52100),
        "server": ("amesh", 8000),
        "headers": [(b"host", b"amesh:8000")],
    }
    headers = {
        "x-forwarded-proto": "https",
        "x-forwarded-host": "workflows.example.test",
        "x-forwarded-for": "198.51.100.10",
    }
    with pytest.raises(ForwardedHeaderRejected, match="not accepted"):
        apply_trusted_forwarded_headers(untrusted_scope, headers, ("10.0.0.0/8",))

    trusted_scope = {
        **untrusted_scope,
        "client": ("10.1.2.3", 52100),
        "headers": [(b"host", b"amesh:8000")],
    }
    apply_trusted_forwarded_headers(trusted_scope, headers, ("10.0.0.0/8",))
    assert trusted_scope["scheme"] == "https"
    assert trusted_scope["server"] == ("workflows.example.test", 443)
    assert trusted_scope["client"] == ("198.51.100.10", 52100)
    assert trusted_scope["headers"] == [(b"host", b"workflows.example.test")]


def test_http_egress_allowlist_and_private_address_protection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy = HttpTaskPolicy(allowed_hosts=("api.example.test", "192.0.2.0/24"))
    validate_http_destination("https://api.example.test/items", policy, resolve_dns=False)
    with pytest.raises(ValueError, match="egress allowlist"):
        validate_http_destination("https://denied.example.test/items", policy, resolve_dns=False)

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 0))],
    )
    with pytest.raises(ValueError, match="blocked private"):
        validate_http_destination(
            "https://api.example.test/items",
            policy,
            resolve_dns=True,
        )
    assert host_matches("service.corp.example", ("*.corp.example",))
    assert host_matches("10.10.1.2", ("10.10.0.0/16",))


def test_network_diagnostics_redact_proxy_credentials_and_report_dns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key_file, cert_file = _write_certificate_pair(tmp_path, "diagnostic")
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.44", 0))],
    )
    settings = Settings(
        _env_file=None,
        network_inbound_tls_mode="direct",
        network_tls_certificate_file=str(cert_file),
        network_tls_private_key_file=str(key_file),
        network_https_proxy_url="https://proxy-user:proxy-secret@proxy.example.test:8443",
        network_no_proxy=("localhost",),
        network_diagnostic_hosts=("api.example.test",),
        network_topology="split",
        network_private_endpoint=True,
    )

    report = asyncio.run(build_network_diagnostics(settings))
    rendered = report.model_dump_json(by_alias=True)
    assert report.https_proxy_configured
    assert report.topology == "split"
    assert report.certificates[0].status == "READY"
    assert all(item.status == "RESOLVED" for item in report.dns)
    assert "proxy-user" not in rendered
    assert "proxy-secret" not in rendered
