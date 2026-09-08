from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest
from starlette.exceptions import HTTPException

from amesh.frontend import SpaStaticFiles


def test_spa_static_files_serves_deep_links_but_preserves_api_404(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<main>AMESH control room</main>", encoding="utf-8")
    static = SpaStaticFiles(directory=tmp_path, html=True)

    async def request(path: str, accept: bytes) -> tuple[int, bytes]:
        messages: list[dict[str, Any]] = []
        scope: dict[str, Any] = {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "root_path": "",
            "headers": [(b"accept", accept)],
            "client": ("test", 1),
            "server": ("test", 80),
        }

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        await static(scope, receive, send)
        status = next(
            message["status"] for message in messages if message["type"] == "http.response.start"
        )
        body = b"".join(
            message.get("body", b"")
            for message in messages
            if message["type"] == "http.response.body"
        )
        return status, body

    deep_link = asyncio.run(request("/executions/run-1", b"text/html"))
    assert deep_link == (200, b"<main>AMESH control room</main>")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(request("/api/v1/not-real", b"application/json"))
    assert exc_info.value.status_code == 404
