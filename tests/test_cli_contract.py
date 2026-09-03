from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any, ClassVar

import httpx

from amesh.cli import (
    EXIT_CONFIRMATION_REQUIRED,
    EXIT_DIFFERENCE,
    EXIT_SUCCESS,
    build_parser,
    command_markdown,
    main,
    shell_completion,
)
from amesh.dsl import validate_flow_document


class MemoryCredentialStore:
    values: ClassVar[dict[str, str]] = {}

    def get(self, profile: str) -> str | None:
        return self.values.get(profile)

    def set(self, profile: str, token: str) -> None:
        self.values[profile] = token

    def delete(self, profile: str) -> None:
        self.values.pop(profile, None)


class ProfileClient:
    def __init__(self, **kwargs: Any) -> None:
        assert kwargs["base_url"] == "https://ci.amesh.test"
        assert kwargs["headers"] == {
            "authorization": "Bearer stored-ci-token",
            "x-amesh-tenant": "ci-tenant",
        }

    def __enter__(self) -> ProfileClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        del kwargs
        assert path == "/api/v1/flows"
        return httpx.Response(
            200,
            request=httpx.Request("GET", path),
            json=[{"namespace": "examples", "flow_id": "hello"}],
        )


def test_urs_f_0414_0415_0419_0420_profiles_secure_tokens_and_output_modes(
    monkeypatch: Any,
    capsys: Any,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    MemoryCredentialStore.values.clear()
    monkeypatch.setattr("amesh.cli.KeyringCredentialStore", MemoryCredentialStore)
    assert (
        main(
            [
                "--config-path",
                str(config_path),
                "config",
                "set",
                "ci",
                "--api-url",
                "https://ci.amesh.test",
                "--tenant",
                "ci-tenant",
            ]
        )
        == EXIT_SUCCESS
    )
    assert main(["--config-path", str(config_path), "config", "use", "ci"]) == EXIT_SUCCESS
    capsys.readouterr()

    monkeypatch.setattr(sys, "stdin", io.StringIO("stored-ci-token\n"))
    assert (
        main(["--config-path", str(config_path), "auth", "token", "store", "--stdin"])
        == EXIT_SUCCESS
    )
    assert "stored-ci-token" not in config_path.read_text(encoding="utf-8")
    assert "stored-ci-token" not in capsys.readouterr().out

    monkeypatch.setattr(httpx, "Client", ProfileClient)
    assert main(["--config-path", str(config_path), "--output", "human", "flows"]) == EXIT_SUCCESS
    assert "hello" in capsys.readouterr().out
    assert main(["--config-path", str(config_path), "--output", "quiet", "flows"]) == EXIT_SUCCESS
    assert capsys.readouterr().out == ""

    MemoryCredentialStore.values.clear()
    monkeypatch.setenv("AMESH_SERVICE_ACCOUNT_TOKEN", "stored-ci-token")
    assert main(["--config-path", str(config_path), "--output", "quiet", "flows"]) == EXIT_SUCCESS
    assert capsys.readouterr().out == ""


class DeclarativeClient:
    remote_document: ClassVar[dict[str, Any]]
    applied: ClassVar[bytes | None] = None
    deleted: ClassVar[list[str]] = []
    calls: ClassVar[list[tuple[str, str]]] = []

    def __init__(self, **kwargs: Any) -> None:
        del kwargs

    def __enter__(self) -> DeclarativeClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        del kwargs
        self.calls.append(("GET", path))
        if path == "/api/v1/configuration":
            return httpx.Response(200, request=httpx.Request("GET", path), json={"version": 1})
        return httpx.Response(
            200,
            request=httpx.Request("GET", path),
            json={
                "namespace": "examples.cli",
                "flowId": "declarative",
                "revision": 1,
                "semanticHash": "a" * 64,
                "document": self.remote_document,
            },
        )

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        self.calls.append(("PUT", path))
        type(self).applied = kwargs["content"]
        return httpx.Response(200, request=httpx.Request("PUT", path), json={"revision": 2})

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        del kwargs
        self.calls.append(("POST", path))
        return httpx.Response(200, request=httpx.Request("POST", path), json={"version": 2})

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        del kwargs
        self.deleted.append(path)
        return httpx.Response(204, request=httpx.Request("DELETE", path))


def _flow(value: str) -> str:
    return f"""id: declarative
namespace: examples.cli
tasks:
  - id: done
    type: core.return
    value: {value}
"""


def test_urs_f_0414_0416_declarative_stdin_diff_export_delete_and_admin(
    monkeypatch: Any,
    capsys: Any,
    tmp_path: Path,
) -> None:
    DeclarativeClient.calls.clear()
    DeclarativeClient.deleted.clear()
    remote = validate_flow_document(_flow("before").encode())
    assert remote.canonical is not None
    DeclarativeClient.remote_document = remote.canonical
    monkeypatch.setattr(httpx, "Client", DeclarativeClient)

    monkeypatch.setattr(sys, "stdin", io.StringIO(_flow("after")))
    assert main(["--token", "test", "flow", "apply", "-"]) == EXIT_SUCCESS
    assert DeclarativeClient.applied == _flow("after").encode()

    local = tmp_path / "flow.yaml"
    local.write_text(_flow("after"), encoding="utf-8")
    assert main(["--token", "test", "flow", "diff", str(local)]) == EXIT_DIFFERENCE
    assert '"changed": true' in capsys.readouterr().out

    exported = tmp_path / "exported.yaml"
    assert (
        main(
            [
                "--token",
                "test",
                "flow",
                "export",
                "examples.cli",
                "declarative",
                str(exported),
            ]
        )
        == EXIT_SUCCESS
    )
    assert "value: before" in exported.read_text(encoding="utf-8")

    preview = main(["--token", "test", "flow", "delete", "examples.cli", "declarative", "1"])
    assert preview == EXIT_CONFIRMATION_REQUIRED
    assert DeclarativeClient.deleted == []
    assert (
        main(
            [
                "--token",
                "test",
                "flow",
                "delete",
                "examples.cli",
                "declarative",
                "1",
                "--force",
            ]
        )
        == EXIT_SUCCESS
    )
    assert DeclarativeClient.deleted == ["/api/v1/flows/examples.cli/declarative/revisions/1"]
    assert main(["--token", "test", "admin", "configuration", "show"]) == EXIT_SUCCESS
    assert ("GET", "/api/v1/configuration") in DeclarativeClient.calls

    deleted_before_preview = list(DeclarativeClient.deleted)
    assert (
        main(["--token", "test", "admin", "tenants", "delete", "tenant-a"])
        == EXIT_CONFIRMATION_REQUIRED
    )
    assert DeclarativeClient.deleted == deleted_before_preview
    assert (
        main(
            [
                "--token",
                "test",
                "admin",
                "tenants",
                "delete",
                "tenant-a",
                "--force",
            ]
        )
        == EXIT_SUCCESS
    )
    assert DeclarativeClient.deleted[-1] == "/api/v1/admin/tenants/tenant-a"


def test_urs_f_0421_completion_and_docs_are_generated_from_parser() -> None:
    parser = build_parser()
    parsed = parser.parse_args(
        [
            "--output",
            "quiet",
            "plugins",
            "certify",
            "plugin",
            "--output",
            "report.json",
        ]
    )
    assert parsed.output_mode == "quiet"
    assert parsed.output == Path("report.json")
    for shell in ("bash", "zsh", "fish", "powershell"):
        generated = shell_completion(parser, shell)
        assert "flow" in generated
        assert "admin" in generated
    documentation = command_markdown(parser)
    assert documentation == command_markdown(parser)
    assert "`amesh flow diff`" in documentation
    assert "`amesh auth token store`" in documentation
