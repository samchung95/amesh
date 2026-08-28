from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol

from docker.client import DockerClient
from docker.errors import ImageNotFound
from docker.models.images import Image

from amesh.ports import (
    DockerContainerRunnerExtension,
    DockerImagePolicy,
    DockerImagePullPolicy,
    RunnerId,
    UnsupportedRunnerRequest,
)


@dataclass(frozen=True)
class ImagePolicyDecision:
    requested: str
    resolved: str
    registry: str
    signature_verified: bool
    vulnerability_policy_passed: bool


class ImagePolicyVerifier(Protocol):
    async def verify_signature(self, image: str) -> None: ...

    async def verify_vulnerabilities(self, image: str) -> None: ...


class CommandImagePolicyVerifier:
    """Runs configured argv-only verification commands against one immutable image."""

    def __init__(
        self,
        *,
        signature_command: tuple[str, ...] = (),
        vulnerability_command: tuple[str, ...] = (),
    ) -> None:
        self._signature_command = signature_command
        self._vulnerability_command = vulnerability_command

    async def verify_signature(self, image: str) -> None:
        await _run_verifier(self._signature_command, image, "signature")

    async def verify_vulnerabilities(self, image: str) -> None:
        await _run_verifier(self._vulnerability_command, image, "vulnerability")


async def resolve_and_verify_image(
    client: DockerClient,
    requested: str,
    extension: DockerContainerRunnerExtension,
    policy: DockerImagePolicy,
    verifier: ImagePolicyVerifier,
    *,
    auth_config: dict[str, str] | None,
) -> ImagePolicyDecision:
    registry = image_registry(requested)
    if registry not in policy.allowed_registries:
        raise UnsupportedRunnerRequest(
            RunnerId.DOCKER,
            (f"image registry {registry!r} is not allowed",),
        )
    is_digest = "@sha256:" in requested
    if not is_digest and not policy.allow_tags:
        raise UnsupportedRunnerRequest(
            RunnerId.DOCKER,
            ("image tags require docker_image_policy.allowTags=true",),
        )

    image = await _obtain_image(client, requested, extension, auth_config=auth_config)
    resolved = _resolved_digest(image, requested)
    if resolved is None:
        raise UnsupportedRunnerRequest(
            RunnerId.DOCKER,
            (f"image {requested!r} did not resolve to an immutable repository digest",),
        )
    signature_verified = False
    vulnerability_policy_passed = False
    if policy.require_signature:
        await verifier.verify_signature(resolved)
        signature_verified = True
    if policy.require_vulnerability_scan:
        await verifier.verify_vulnerabilities(resolved)
        vulnerability_policy_passed = True
    return ImagePolicyDecision(
        requested=requested,
        resolved=resolved,
        registry=registry,
        signature_verified=signature_verified,
        vulnerability_policy_passed=vulnerability_policy_passed,
    )


def image_registry(reference: str) -> str:
    name = reference.split("@", 1)[0]
    if "/" not in name:
        return "docker.io"
    first = name.split("/", 1)[0]
    if "." in first or ":" in first or first == "localhost":
        return "docker.io" if first == "index.docker.io" else first
    return "docker.io"


async def _obtain_image(
    client: DockerClient,
    requested: str,
    extension: DockerContainerRunnerExtension,
    *,
    auth_config: dict[str, str] | None,
) -> Image:
    if extension.pull_policy is DockerImagePullPolicy.ALWAYS:
        return await asyncio.to_thread(
            client.images.pull,
            requested,
            auth_config=auth_config,
            platform=extension.platform,
        )
    try:
        return await asyncio.to_thread(client.images.get, requested)
    except ImageNotFound:
        if extension.pull_policy is DockerImagePullPolicy.NEVER:
            raise UnsupportedRunnerRequest(
                RunnerId.DOCKER,
                (f"image {requested!r} is absent and pullPolicy is NEVER",),
            ) from None
        return await asyncio.to_thread(
            client.images.pull,
            requested,
            auth_config=auth_config,
            platform=extension.platform,
        )


def _resolved_digest(image: Image, requested: str) -> str | None:
    if "@sha256:" in requested:
        return requested
    repository = requested.rsplit(":", 1)[0] if ":" in requested.rsplit("/", 1)[-1] else requested
    digests = image.attrs.get("RepoDigests") or []
    for digest in digests:
        if isinstance(digest, str) and digest.split("@", 1)[0] == repository:
            return digest
    return next((item for item in digests if isinstance(item, str)), None)


async def _run_verifier(command: tuple[str, ...], image: str, kind: str) -> None:
    if not command:
        raise UnsupportedRunnerRequest(
            RunnerId.DOCKER,
            (f"{kind} verification is required but no verifier command is configured",),
        )
    if not any("{image}" in item for item in command):
        raise UnsupportedRunnerRequest(
            RunnerId.DOCKER,
            (f"{kind} verifier command must contain the {{image}} placeholder",),
        )
    argv = tuple(item.replace("{image}", image) for item in command)
    process = await asyncio.create_subprocess_exec(
        *argv,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        message = stderr.decode(errors="replace").strip()
        detail = f": {message[:512]}" if message else ""
        raise UnsupportedRunnerRequest(
            RunnerId.DOCKER,
            (f"{kind} verification rejected {image!r}{detail}",),
        )
