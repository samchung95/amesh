from __future__ import annotations

import asyncio
import hashlib
import json
import multiprocessing
import queue
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf import __version__ as PYPDF_VERSION

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskHandler
from amesh.plugin_sdk import (
    DocumentArtifactRef,
    DocumentChunk,
    DocumentExtractionLimits,
    DocumentExtractRequest,
    DocumentExtractResult,
    DocumentPage,
    ExtractorProvenance,
)
from amesh.workflow.working_directory import WorkingDirectoryManager

_DEFAULT_TIMEOUT_SECONDS = 30.0
_MAX_RESULT_BYTES = 100 * 1024 * 1024
_CORE_EXTRACTOR_DIGEST = (
    "sha256:" + hashlib.sha256(b"amesh.core.document.extract@0.2.0").hexdigest()
)
_PYPDF_WHEEL_DIGEST = "sha256:63fec31c4092ae50b6729beedcb469055b60d20c834bde1c402df241f371f644"


class DocumentExtractionError(ValueError):
    """Stable user-facing failure from the reference document extractor."""

    def __init__(self, message: str, code: str = "document.extract.failed") -> None:
        super().__init__(message)
        self.code = code


def core_document_extract_handler(workspace_manager: WorkingDirectoryManager) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        extra = task.configuration.handler_view()
        source_name = _source_name(extra.get("source"))
        try:
            artifact = DocumentArtifactRef.model_validate(extra.get("artifact"))
        except Exception as exc:
            raise DocumentExtractionError(
                "document task requires a valid public artifact reference",
                "document.extract.artifact",
            ) from exc
        if artifact.tenant_id != context.tenant_id:
            raise DocumentExtractionError(
                "document artifact belongs to another tenant",
                "document.extract.tenant_isolation",
            )
        if artifact.namespace != context.namespace:
            raise DocumentExtractionError(
                "document artifact belongs to another namespace",
                "document.extract.namespace_isolation",
            )
        source_uri = context.files.get(source_name)
        reference = context.file_references.get(source_name)
        if source_uri is None or reference is None:
            raise DocumentExtractionError(
                f"document source {source_name!r} requires an exact input artifact reference",
                "document.extract.source_missing",
            )
        if reference.uri != source_uri:
            raise DocumentExtractionError(
                "document source reference does not match the selected object",
                "document.extract.source_mismatch",
            )
        if artifact.size_bytes != reference.size_bytes:
            raise DocumentExtractionError(
                "document artifact size does not match the selected object",
                "document.extract.artifact_mismatch",
            )
        if artifact.checksum_sha256 != reference.checksum_sha256:
            raise DocumentExtractionError(
                "document artifact checksum does not match the selected object",
                "document.extract.artifact_mismatch",
            )
        media_type = _media_type(artifact.media_type)
        if media_type != "application/pdf":
            raise DocumentExtractionError(
                f"unsupported document media type {media_type!r}",
                "document.extract.media_type",
            )
        limits_payload = extra.get("limits", {})
        if not isinstance(limits_payload, dict):
            raise DocumentExtractionError("limits must be an object", "document.extract.limits")
        try:
            limits = DocumentExtractionLimits.model_validate(limits_payload)
        except Exception as exc:
            raise DocumentExtractionError(
                "document extraction limits are invalid",
                "document.extract.limits",
            ) from exc
        if reference.size_bytes > limits.max_bytes:
            raise DocumentExtractionError(
                f"document exceeds maxBytes ({limits.max_bytes})",
                "document.extract.size_limit",
            )
        request = DocumentExtractRequest(artifact=artifact, source=source_name, limits=limits)
        workspace = await workspace_manager.prepare(
            tenant_id=context.tenant_id,
            execution_id=str(context.execution_id),
            task_run_id=str(context.task_run_id),
            attempt_id=str(context.attempt_id),
            scope_id=context.workspace_scope_id,
            input_files={source_name: source_uri},
            file_references={source_name: reference},
            quota_bytes=context.workspace_quota_bytes or task.workspace_quota_bytes,
        )
        try:
            source_path = workspace.path.joinpath(*Path(source_name).parts)
            if not source_path.is_file():
                raise DocumentExtractionError(
                    "document source was not materialized",
                    "document.extract.source_missing",
                )
            result = await _extract_with_limit(
                source_path,
                request.limits,
                timeout_seconds=task.timeout_seconds
                or request.limits.wall_time_seconds
                or _DEFAULT_TIMEOUT_SECONDS,
            )
            typed = DocumentExtractResult(
                source=request.artifact,
                extractor=ExtractorProvenance(
                    plugin="amesh.core.document.extract",
                    pluginVersion="0.2.0",
                    pluginContentDigest=_CORE_EXTRACTOR_DIGEST,
                    parser="pypdf",
                    parserVersion=PYPDF_VERSION,
                    parserContentDigest=_PYPDF_WHEEL_DIGEST,
                ),
                metadata=result["metadata"],
                pages=tuple(DocumentPage.model_validate(item) for item in result["pages"]),
                chunks=tuple(DocumentChunk.model_validate(item) for item in result["chunks"]),
                text=result["text"],
                tokenCount=result["tokenCount"],
            )
            output_path = workspace.path / "document-result.json"
            serialized = json.dumps(
                typed.model_dump(mode="json", by_alias=True), sort_keys=True, ensure_ascii=False
            )
            output_bytes = len(serialized.encode("utf-8"))
            if output_bytes > min(
                _MAX_RESULT_BYTES, task.contract.resource_limits.max_output_bytes
            ):
                raise DocumentExtractionError(
                    "document result exceeds maxOutputBytes",
                    "document.extract.output_limit",
                )
            await asyncio.to_thread(output_path.write_text, serialized, encoding="utf-8")
            collected = await workspace_manager.collect(
                workspace,
                tenant_id=context.tenant_id,
                execution_id=str(context.execution_id),
                task_run_id=str(context.task_run_id),
                attempt=context.attempt,
                patterns=("document-result.json",),
                manifest_path=None,
                quota_bytes=context.workspace_quota_bytes or task.workspace_quota_bytes,
            )
            return TaskCompletion(
                output=typed.model_dump(mode="json", by_alias=True),
                artifacts=collected.artifacts,
            )
        finally:
            if not workspace.shared:
                await asyncio.to_thread(workspace_manager.cleanup, workspace.path)

    return run


async def _extract_with_limit(
    path: Path,
    limits: DocumentExtractionLimits,
    *,
    timeout_seconds: float,
) -> dict[str, Any]:
    context = multiprocessing.get_context("spawn")
    result_queue: multiprocessing.Queue[dict[str, Any]] = context.Queue(maxsize=1)
    process = context.Process(
        target=_extract_worker, args=(str(path), limits.model_dump(), result_queue)
    )
    process.start()
    result: dict[str, Any] | None = None
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    try:
        while result is None:
            try:
                result = result_queue.get_nowait()
                break
            except queue.Empty:
                if not process.is_alive():
                    process.join(timeout=1)
                    try:
                        result = result_queue.get_nowait()
                    except queue.Empty:
                        raise DocumentExtractionError(
                            "document parser exited without a result",
                            "document.extract.parser",
                        ) from None
                    break
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    process.terminate()
                    process.join(timeout=1)
                    raise DocumentExtractionError(
                        "document extractor timed out",
                        "document.extract.timeout",
                    ) from None
                await asyncio.sleep(min(0.01, remaining))
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=1)
        result_queue.close()
        result_queue.join_thread()
    if not result.get("ok"):
        raise DocumentExtractionError(
            str(result.get("message", "document parser failed")),
            str(result.get("code", "document.extract.parser")),
        )
    payload = result.get("result")
    if not isinstance(payload, dict):
        raise DocumentExtractionError(
            "document parser returned no result", "document.extract.parser"
        )
    return payload


def _extract_worker(
    path: str,
    limits_payload: dict[str, Any],
    result_queue: multiprocessing.Queue[dict[str, Any]],
) -> None:
    try:
        limits = DocumentExtractionLimits.model_validate(limits_payload)
        result_queue.put({"ok": True, "result": _extract_pdf(Path(path), limits)})
    except Exception as exc:
        result_queue.put(
            {
                "ok": False,
                "code": _parser_error_code(exc),
                "message": _safe_parser_message(exc),
            }
        )


def _extract_pdf(path: Path, limits: DocumentExtractionLimits) -> dict[str, Any]:
    with path.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            raise DocumentExtractionError(
                "document is not a PDF",
                "document.extract.unsupported",
            )
    reader = PdfReader(str(path), strict=True)
    if reader.is_encrypted:
        raise DocumentExtractionError(
            "encrypted PDFs are not supported",
            "document.extract.encrypted",
        )
    if len(reader.pages) > limits.max_pages:
        raise DocumentExtractionError(
            f"document exceeds maxPages ({limits.max_pages})",
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
        if total_tokens > limits.max_tokens:
            raise DocumentExtractionError(
                f"document exceeds maxTokens ({limits.max_tokens})",
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
        chunks.extend(_page_chunks(page_number, text, limits))
    return {
        "metadata": metadata,
        "pages": pages,
        "chunks": chunks,
        "text": "\n".join(page_texts),
        "tokenCount": total_tokens,
    }


def _page_chunks(
    page_number: int, text: str, limits: DocumentExtractionLimits
) -> list[dict[str, Any]]:
    tokens = _tokens(text)
    if not tokens:
        return []
    step = limits.chunk_tokens - limits.chunk_overlap_tokens
    if step <= 0:
        raise DocumentExtractionError(
            "chunkOverlapTokens must be smaller than chunkTokens", "document.extract.limits"
        )
    chunks: list[dict[str, Any]] = []
    for chunk_number, start in enumerate(range(0, len(tokens), step), start=1):
        selected = tokens[start : start + limits.chunk_tokens]
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


def _source_name(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        raise DocumentExtractionError(
            "source must be a relative POSIX input file path", "document.extract.source"
        )
    path = Path(value)
    if not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise DocumentExtractionError(
            "source must be a relative POSIX input file path", "document.extract.source"
        )
    return value


def _media_type(value: object) -> str:
    if value is None:
        return "application/pdf"
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise DocumentExtractionError(
            "mediaType must be a trimmed value", "document.extract.media_type"
        )
    return value.casefold()


def _parser_error_code(exc: BaseException) -> str:
    if isinstance(exc, DocumentExtractionError):
        return exc.code
    return "document.extract.parser"


def _safe_parser_message(exc: BaseException) -> str:
    if isinstance(exc, DocumentExtractionError):
        return str(exc)
    return f"PDF parser failed: {type(exc).__name__}"
