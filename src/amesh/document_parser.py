"""PDF parsing that runs in the isolated document-extractor child interpreter.

The parent starts this file as a script with ``python -I -S``. Isolated mode
ignores ``PYTHON*`` variables, the user site and the script directory, and
``-S`` skips ``site`` so no ``.pth`` hook (coverage, profilers, editable-install
finders) runs before parsing untrusted input. The parent passes the directories
that hold pypdf in the request. The wall-time budget therefore measures parsing
rather than platform start-up. This module must import only the standard
library and, lazily, pypdf.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


class DocumentExtractionError(ValueError):
    """Stable user-facing failure from the reference document extractor."""

    def __init__(self, message: str, code: str = "document.extract.failed") -> None:
        super().__init__(message)
        self.code = code


def run_request(request: str) -> dict[str, Any]:
    try:
        payload = json.loads(request)
        # Append so parent site-packages never shadow the standard library.
        sys.path.extend(entry for entry in payload.get("importPaths", ()) if entry not in sys.path)
        return {
            "ok": True,
            "result": extract_pdf(Path(payload["path"]), **payload["limits"]),
        }
    except Exception as exc:
        return {
            "ok": False,
            "code": _parser_error_code(exc),
            "message": _safe_parser_message(exc),
        }


def main(argv: list[str]) -> int:
    result_stream = sys.stdout.buffer
    # Keep stray library prints from corrupting the JSON result channel.
    sys.stdout = sys.stderr
    result = run_request(argv[1] if len(argv) == 2 else "")
    result_stream.write(json.dumps(result).encode("ascii"))
    result_stream.flush()
    return 0


def extract_pdf(
    path: Path,
    *,
    max_pages: int,
    max_tokens: int,
    chunk_tokens: int,
    chunk_overlap_tokens: int,
) -> dict[str, Any]:
    with path.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            raise DocumentExtractionError(
                "document is not a PDF",
                "document.extract.unsupported",
            )
    from pypdf import PdfReader

    reader = PdfReader(str(path), strict=True)
    if reader.is_encrypted:
        raise DocumentExtractionError(
            "encrypted PDFs are not supported",
            "document.extract.encrypted",
        )
    if len(reader.pages) > max_pages:
        raise DocumentExtractionError(
            f"document exceeds maxPages ({max_pages})",
            "document.extract.page_limit",
        )
    metadata = {
        str(key).lstrip("/"): _metadata_value(value)
        for key, value in (reader.metadata or {}).items()
        if value is not None
    }
    pages: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    page_texts: list[str] = []
    total_tokens = 0
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        page_texts.append(text)
        tokens = _tokens(text)
        total_tokens += len(tokens)
        if total_tokens > max_tokens:
            raise DocumentExtractionError(
                f"document exceeds maxTokens ({max_tokens})",
                "document.extract.token_limit",
            )
        pages.append(
            {
                "pageNumber": page_number,
                "text": text,
                "tokenCount": len(tokens),
                "sourceLocator": {
                    "pageNumber": page_number,
                    "startOffset": 0,
                    "endOffset": len(text),
                },
            }
        )
        chunks.extend(_page_chunks(page_number, text, chunk_tokens, chunk_overlap_tokens))
    return {
        "metadata": metadata,
        "pages": pages,
        "chunks": chunks,
        "text": "\n".join(page_texts),
        "tokenCount": total_tokens,
    }


def _page_chunks(
    page_number: int, text: str, chunk_tokens: int, chunk_overlap_tokens: int
) -> list[dict[str, Any]]:
    tokens = _tokens(text)
    if not tokens:
        return []
    step = chunk_tokens - chunk_overlap_tokens
    if step <= 0:
        raise DocumentExtractionError(
            "chunkOverlapTokens must be smaller than chunkTokens", "document.extract.limits"
        )
    chunks: list[dict[str, Any]] = []
    for chunk_number, start in enumerate(range(0, len(tokens), step), start=1):
        selected = tokens[start : start + chunk_tokens]
        if not selected:
            break
        first_start = selected[0][1]
        last_end = selected[-1][2]
        chunks.append(
            {
                "id": f"page-{page_number}-chunk-{chunk_number}",
                "text": text[first_start:last_end],
                "tokenCount": len(selected),
                "sourceLocators": [
                    {
                        "pageNumber": page_number,
                        "startOffset": first_start,
                        "endOffset": last_end,
                    }
                ],
            }
        )
    return chunks


def _tokens(text: str) -> list[tuple[str, int, int]]:
    return [(match.group(), match.start(), match.end()) for match in re.finditer(r"\S+", text)]


def _metadata_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _parser_error_code(exc: BaseException) -> str:
    if isinstance(exc, DocumentExtractionError):
        return exc.code
    return "document.extract.parser"


def _safe_parser_message(exc: BaseException) -> str:
    if isinstance(exc, DocumentExtractionError):
        return str(exc)
    return f"PDF parser failed: {type(exc).__name__}"


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
