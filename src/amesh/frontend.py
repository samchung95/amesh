from __future__ import annotations

from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, Response
from starlette.staticfiles import StaticFiles


def find_frontend_dist() -> Path | None:
    candidates = (
        Path(__file__).with_name("web"),
        Path(__file__).resolve().parents[2] / "frontend" / "dist",
    )
    return next(
        (candidate for candidate in candidates if (candidate / "index.html").is_file()), None
    )


class SpaStaticFiles(StaticFiles):
    """Serve immutable frontend assets and HTML deep links without masking API 404s."""

    async def get_response(self, path: str, scope: MutableMapping[str, Any]) -> Response:
        try:
            response = await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code != 404:
                raise
            response = None
        accepts_html = "text/html" in Headers(scope=scope).get("accept", "")
        if response is not None or scope["method"] not in {"GET", "HEAD"} or not accepts_html:
            if response is None:
                raise HTTPException(status_code=404)
            return response
        if self.directory is None:
            raise RuntimeError("SPA static directory is not configured")
        return FileResponse(Path(self.directory) / "index.html")
