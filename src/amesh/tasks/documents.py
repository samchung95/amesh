from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from pypdf import __version__ as PYPDF_VERSION

from amesh import document_parser
from amesh.document_parser import DocumentExtractionError
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

__all__ = ["DocumentExtractionError", "core_document_extract_handler"]


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
    request = json.dumps(
        {
            "path": str(path),
            "limits": {
                "max_pages": limits.max_pages,
                "max_tokens": limits.max_tokens,
                "chunk_tokens": limits.chunk_tokens,
                "chunk_overlap_tokens": limits.chunk_overlap_tokens,
            },
        }
    )
    process = subprocess.Popen(
        [*parser_command(), request],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
    )
    try:
        output, _ = await asyncio.wait_for(
            asyncio.to_thread(process.communicate), timeout=timeout_seconds
        )
    except TimeoutError:
        raise DocumentExtractionError(
            "document extractor timed out",
            "document.extract.timeout",
        ) from None
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    try:
        result = json.loads(output) if output else None
    except ValueError:
        result = None
    if not isinstance(result, dict):
        raise DocumentExtractionError(
            "document parser exited without a result",
            "document.extract.parser",
        )
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


def parser_command() -> tuple[str, ...]:
    """Fresh-interpreter command for the parser child.

    Running the file as a script with ``-P`` avoids multiprocessing's re-import of
    the parent's ``python -m`` main module and keeps ``src/amesh`` off
    ``sys.path``, where ``amesh/platform`` would shadow the standard library.
    """
    return (sys.executable, "-P", str(Path(document_parser.__file__).resolve()))


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
