from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from typing import Any, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .identity import NaturalId, validate_namespace, validate_natural_id


class BlueprintCatalogSource(StrEnum):
    BUILTIN = "BUILTIN"
    ORGANIZATION = "ORGANIZATION"
    COMMUNITY = "COMMUNITY"


class BlueprintParameterKind(StrEnum):
    STRING = "STRING"
    NAMESPACE = "NAMESPACE"
    FLOW_ID = "FLOW_ID"


class BlueprintParameter(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: NaturalId
    title: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=500)
    kind: BlueprintParameterKind
    required: bool = True
    default: str | None = Field(default=None, max_length=500)


class BlueprintProvenance(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    publisher: str
    location: str
    revision: str
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class BlueprintSummary(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    blueprint_id: NaturalId = Field(alias="blueprintId")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    source: BlueprintCatalogSource
    title: str
    summary: str
    tags: tuple[str, ...]
    parameters: tuple[BlueprintParameter, ...]
    documentation: str
    license: str
    provenance: BlueprintProvenance
    local_only: bool = Field(alias="localOnly")


class BlueprintDefinition(BlueprintSummary):
    template: str


class BlueprintInstantiationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    parameters: dict[str, str] = Field(default_factory=dict, max_length=32)


_PLACEHOLDER = re.compile(r"\$\{([A-Za-z0-9_-]+)\}")


def list_blueprints(
    *,
    query: str | None = None,
    source: BlueprintCatalogSource | None = None,
) -> tuple[BlueprintSummary, ...]:
    normalized = (query or "").strip().casefold()
    selected: list[BlueprintSummary] = []
    for blueprint in _BLUEPRINTS:
        if source is not None and blueprint.source is not source:
            continue
        haystack = " ".join(
            (
                blueprint.blueprint_id,
                blueprint.title,
                blueprint.summary,
                blueprint.documentation,
                *blueprint.tags,
            )
        ).casefold()
        if normalized and normalized not in haystack:
            continue
        selected.append(
            BlueprintSummary.model_validate(
                blueprint.model_dump(by_alias=True, exclude={"template"})
            )
        )
    return tuple(selected)


def get_blueprint(blueprint_id: str, version: str) -> BlueprintDefinition:
    for blueprint in _BLUEPRINTS:
        if blueprint.blueprint_id == blueprint_id and blueprint.version == version:
            return blueprint
    raise LookupError("blueprint version not found")


def instantiate_blueprint(
    blueprint: BlueprintDefinition,
    request: BlueprintInstantiationRequest,
) -> dict[str, Any]:
    declared = {parameter.name: parameter for parameter in blueprint.parameters}
    unknown = sorted(set(request.parameters) - set(declared))
    if unknown:
        raise ValueError(f"unknown blueprint parameters: {', '.join(unknown)}")
    values: dict[str, str] = {}
    for name, parameter in declared.items():
        value = request.parameters.get(name, parameter.default)
        if value is None or (parameter.required and not value.strip()):
            raise ValueError(f"blueprint parameter {name!r} is required")
        normalized = value.strip()
        if len(normalized) > 500:
            raise ValueError(f"blueprint parameter {name!r} exceeds 500 characters")
        if parameter.kind is BlueprintParameterKind.NAMESPACE:
            validate_namespace(normalized)
        elif parameter.kind is BlueprintParameterKind.FLOW_ID:
            validate_natural_id(normalized)
        values[name] = normalized
    document = yaml.safe_load(blueprint.template)
    if not isinstance(document, dict):
        raise ValueError("blueprint template must produce a flow object")
    return cast(dict[str, Any], _substitute(document, values))


def _substitute(value: Any, parameters: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: _substitute(item, parameters) for key, item in value.items()}
    if isinstance(value, list):
        return [_substitute(item, parameters) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in parameters:
            raise ValueError(f"blueprint template references undeclared parameter {name!r}")
        return parameters[name]

    return _PLACEHOLDER.sub(replace, value)


def _definition(
    *,
    blueprint_id: str,
    version: str,
    source: BlueprintCatalogSource,
    title: str,
    summary: str,
    tags: tuple[str, ...],
    parameters: tuple[BlueprintParameter, ...],
    documentation: str,
    license_name: str,
    publisher: str,
    location: str,
    revision: str,
    document: dict[str, Any],
) -> BlueprintDefinition:
    template = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
    digest_payload = json.dumps(
        {
            "blueprintId": blueprint_id,
            "version": version,
            "source": source.value,
            "parameters": [item.model_dump(mode="json") for item in parameters],
            "template": template,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return BlueprintDefinition(
        blueprintId=blueprint_id,
        version=version,
        source=source,
        title=title,
        summary=summary,
        tags=tags,
        parameters=parameters,
        documentation=documentation,
        license=license_name,
        provenance=BlueprintProvenance(
            publisher=publisher,
            location=location,
            revision=revision,
            digest=f"sha256:{hashlib.sha256(digest_payload).hexdigest()}",
        ),
        localOnly=True,
        template=template,
    )


_BASE_PARAMETERS = (
    BlueprintParameter(
        name="namespace",
        title="Namespace",
        description="Draft namespace in dotted AMESH form.",
        kind=BlueprintParameterKind.NAMESPACE,
        default="examples.getting_started",
    ),
    BlueprintParameter(
        name="flow_id",
        title="Flow ID",
        description="Natural identifier for the unsaved draft.",
        kind=BlueprintParameterKind.FLOW_ID,
        default="hello_blueprint",
    ),
)


_BLUEPRINTS = (
    _definition(
        blueprint_id="hello-world",
        version="1.0.0",
        source=BlueprintCatalogSource.BUILTIN,
        title="Hello, workflow",
        summary="A local log-and-return flow with one optional input.",
        tags=("getting-started", "local", "core"),
        parameters=(
            *_BASE_PARAMETERS,
            BlueprintParameter(
                name="greeting",
                title="Greeting",
                description="Text emitted before the supplied name.",
                kind=BlueprintParameterKind.STRING,
                default="Hello",
            ),
        ),
        documentation="Start here. The draft uses only deterministic core tasks and runs in Compose.",
        license_name="Apache-2.0",
        publisher="AMESH project",
        location="repository://amesh/examples/hello-world.yaml",
        revision="0.2.0",
        document={
            "apiVersion": "amesh.flow/v1",
            "id": "${flow_id}",
            "namespace": "${namespace}",
            "description": "Created from the built-in hello-world blueprint.",
            "labels": {"blueprint": "hello-world", "environment": "local"},
            "inputs": [{"id": "name", "type": "STRING", "required": False, "default": "World"}],
            "tasks": [
                {"id": "greet", "type": "core.log", "message": "${greeting} {{ inputs.name }}"},
                {
                    "id": "done",
                    "type": "core.return",
                    "dependsOn": ["greet"],
                    "value": {"message": "${greeting} {{ inputs.name }}"},
                },
            ],
            "outputs": {"message": "{{ outputs.done.value.message }}"},
        },
    ),
    _definition(
        blueprint_id="organization-readiness",
        version="1.0.0",
        source=BlueprintCatalogSource.ORGANIZATION,
        title="Organization readiness marker",
        summary="A policy-neutral local marker for an organization onboarding namespace.",
        tags=("organization", "readiness", "local"),
        parameters=_BASE_PARAMETERS,
        documentation="An organization catalog example. Replace its return payload before production use.",
        license_name="Apache-2.0",
        publisher="Example organization catalog",
        location="organization://default/platform-blueprints",
        revision="1",
        document={
            "apiVersion": "amesh.flow/v1",
            "id": "${flow_id}",
            "namespace": "${namespace}",
            "description": "Organization catalog readiness draft.",
            "labels": {"blueprint": "organization-readiness", "environment": "local"},
            "tasks": [
                {
                    "id": "ready",
                    "type": "core.return",
                    "value": {"ready": True, "source": "organization"},
                }
            ],
        },
    ),
    _definition(
        blueprint_id="community-batch",
        version="1.0.0",
        source=BlueprintCatalogSource.COMMUNITY,
        title="Community batch loop",
        summary="A bounded foreach example that returns each local sample value.",
        tags=("community", "loop", "foreach", "local"),
        parameters=_BASE_PARAMETERS,
        documentation="A reviewed community-style sample with bounded concurrency and iteration limits.",
        license_name="MIT",
        publisher="AMESH community examples",
        location="community://amesh/examples/loops",
        revision="2026-08-23",
        document={
            "apiVersion": "amesh.flow/v1",
            "id": "${flow_id}",
            "namespace": "${namespace}",
            "description": "Community catalog bounded batch draft.",
            "labels": {"blueprint": "community-batch", "environment": "local"},
            "tasks": [
                {
                    "id": "items",
                    "type": "core.foreach",
                    "items": ["alpha", "beta", "gamma"],
                    "maxConcurrency": 2,
                    "maxIterations": 3,
                    "maxTaskRuns": 3,
                    "tasks": [
                        {
                            "id": "return_item",
                            "type": "core.return",
                            "value": "{{ iteration.value }}",
                        }
                    ],
                }
            ],
        },
    ),
)
