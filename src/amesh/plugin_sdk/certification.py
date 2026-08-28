from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from semantic_version import SimpleSpec, Version  # type: ignore[import-untyped]

from amesh import __version__

from .manifest import PLUGIN_PROTOCOL_VERSION, PluginManifest
from .schema import plugin_catalog, validate_configuration

CERTIFICATION_REPORT_VERSION: Literal["amesh.plugin-certification/v1"] = (
    "amesh.plugin-certification/v1"
)
REFERENCE_FIXTURES = (
    "retries",
    "cancellation",
    "large-files",
    "secret-redaction",
    "worker-restart",
)
_MANIFEST_NAMES = ("amesh-plugin.json", "amesh-plugin.yaml", "amesh-plugin.yml")


class PluginQualityLevel(StrEnum):
    UNVERIFIED = "unverified"
    COMMUNITY = "community"
    VERIFIED = "verified"
    CERTIFIED = "certified"


class CertificationCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: Literal["manifest", "schema", "contract", "security", "license", "compatibility"]
    passed: bool
    summary: str
    evidence: tuple[str, ...] = ()


class CompatibilityResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    platform_version: str = Field(alias="platformVersion")
    compatible: bool
    declared_range: str = Field(alias="declaredRange")


class PublicCiEvidence(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    source_commit: str = Field(alias="sourceCommit", pattern=r"^[0-9a-f]{40,64}$")
    run_url: str = Field(alias="runUrl", min_length=9, max_length=2048)
    workflow: str = Field(min_length=1, max_length=255)

    @field_validator("run_url")
    @classmethod
    def require_public_https_url(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("public CI runUrl must use HTTPS")
        return value


class CertificationFixture(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.plugin-fixture/v1"] = Field(
        default="amesh.plugin-fixture/v1",
        alias="schemaVersion",
    )
    name: Literal[
        "retries",
        "cancellation",
        "large-files",
        "secret-redaction",
        "worker-restart",
    ]
    entry_point: str = Field(alias="entryPoint", min_length=1, max_length=255)
    assertion: str = Field(min_length=1, max_length=4096)
    evidence_file: str = Field(alias="evidenceFile", min_length=1, max_length=4096)

    @field_validator("evidence_file")
    @classmethod
    def require_safe_evidence_path(cls, value: str) -> str:
        _safe_relative_path(value)
        return value


class CertificationReport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: Literal["amesh.plugin-certification/v1"] = Field(
        default=CERTIFICATION_REPORT_VERSION,
        alias="schemaVersion",
    )
    plugin: str
    version: str
    input_digest: str = Field(alias="inputDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    quality_level: PluginQualityLevel = Field(alias="qualityLevel")
    checks: tuple[CertificationCheck, ...]
    compatibility: tuple[CompatibilityResult, ...]
    fixtures: tuple[str, ...]
    public_ci: PublicCiEvidence | None = Field(default=None, alias="publicCi")

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def quality_level_criteria() -> dict[PluginQualityLevel, tuple[str, ...]]:
    return {
        PluginQualityLevel.COMMUNITY: (
            "A valid versioned manifest and Draft 2020-12 schemas",
            "A repository license file matching the declared package license",
        ),
        PluginQualityLevel.VERIFIED: (
            "All community criteria",
            "Manifest, schema, contract, security, license and compatibility checks pass",
            "All five reference resilience and redaction fixtures are present with evidence",
        ),
        PluginQualityLevel.CERTIFIED: (
            "All verified criteria",
            "A public HTTPS CI run and immutable source commit reproduce the report",
        ),
    }


def certify_plugin(
    root: Path,
    *,
    platform_versions: tuple[str, ...] = (),
) -> CertificationReport:
    package = root.resolve()
    manifest_path = _manifest_path(package)
    manifest = _load_manifest(manifest_path)
    versions = platform_versions or _compatibility_versions(package) or (__version__,)
    compatibility = _compatibility(manifest, versions)
    fixtures, fixture_errors, fixture_paths = _load_fixtures(package, manifest)
    license_files = tuple(
        path
        for path in sorted(package.glob("LICENSE*"))
        if path.is_file() and not path.is_symlink()
    )
    security_errors = _security_errors(manifest)
    checks = (
        CertificationCheck(
            category="manifest",
            passed=True,
            summary=f"{manifest.name} {manifest.version} uses {manifest.schema_version}",
            evidence=(manifest_path.relative_to(package).as_posix(),),
        ),
        CertificationCheck(
            category="schema",
            passed=True,
            summary=f"{len(manifest.entry_points)} entry-point schema set(s) are valid",
            evidence=tuple(entry.name for entry in manifest.entry_points),
        ),
        CertificationCheck(
            category="contract",
            passed=not fixture_errors,
            summary=(
                "all reference fixtures and evidence files are present"
                if not fixture_errors
                else "; ".join(fixture_errors)
            ),
            evidence=tuple(item.name for item in fixtures),
        ),
        CertificationCheck(
            category="security",
            passed=not security_errors,
            summary=(
                "capabilities, targets and secret examples are deny-first"
                if not security_errors
                else "; ".join(security_errors)
            ),
        ),
        CertificationCheck(
            category="license",
            passed=bool(license_files),
            summary=(
                f"declared {manifest.license}; repository license is present"
                if license_files
                else f"declared {manifest.license}; repository license file is missing"
            ),
            evidence=tuple(path.name for path in license_files),
        ),
        CertificationCheck(
            category="compatibility",
            passed=all(item.compatible for item in compatibility),
            summary=(
                "all tracked platform releases satisfy the declared range and protocol"
                if all(item.compatible for item in compatibility)
                else "one or more tracked platform releases are incompatible"
            ),
            evidence=tuple(item.platform_version for item in compatibility),
        ),
    )
    public_ci, evidence_path = _public_ci_evidence(package)
    quality = _quality_level(checks, public_ci)
    digest_paths = (manifest_path, *license_files, *fixture_paths)
    compatibility_path = package / "certification" / "compatibility.json"
    if compatibility_path.is_file():
        digest_paths = (*digest_paths, compatibility_path)
    if evidence_path is not None:
        digest_paths = (*digest_paths, evidence_path)
    return CertificationReport(
        plugin=manifest.name,
        version=manifest.version,
        inputDigest=_input_digest(package, digest_paths),
        qualityLevel=quality,
        checks=checks,
        compatibility=compatibility,
        fixtures=tuple(item.name for item in fixtures),
        publicCi=public_ci,
    )


def generate_plugin_documentation(root: Path, output_directory: Path) -> tuple[Path, Path]:
    package = root.resolve()
    manifest = _load_manifest(_manifest_path(package))
    output_directory.mkdir(parents=True, exist_ok=True)
    documentation_path = output_directory / "plugin-reference.md"
    sample_path = output_directory / "sample-config.yaml"
    lines = [
        f"# {manifest.name} {manifest.version}",
        "",
        manifest.description or f"Plugin maintained by {manifest.vendor}.",
        "",
        f"- Vendor: {manifest.vendor}",
        f"- License: {manifest.license}",
        f"- Platform: `{manifest.compatibility.platform_version}`",
        f"- Protocols: {', '.join(f'`{item}`' for item in manifest.compatibility.protocol_versions)}",
        "",
        "## Entry points",
        "",
    ]
    samples: list[dict[str, Any]] = []
    for entry in manifest.entry_points:
        lines.extend(
            [
                f"### {entry.documentation.title}",
                "",
                entry.documentation.description,
                "",
                f"- Resource type: `{entry.resolved_resource_type}`",
                f"- Extension: `{entry.type.value}`",
                f"- Transport: `{entry.transport.value}`",
                "",
            ]
        )
        example = (
            dict(entry.documentation.examples[0])
            if entry.documentation.examples
            else _sample_from_schema(entry.configuration_schema)
        )
        samples.append({"type": entry.resolved_resource_type, **example})
        lines.extend(["```yaml", yaml.safe_dump(example, sort_keys=False).rstrip(), "```", ""])
    documentation_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    sample_path.write_text(
        yaml.safe_dump({"entryPoints": samples}, sort_keys=False), encoding="utf-8"
    )
    return documentation_path, sample_path


def sandbox_configuration(
    root: Path,
    entry_point: str,
    configuration: dict[str, Any],
) -> dict[str, Any]:
    manifest = _load_manifest(_manifest_path(root.resolve()))
    entry = next((item for item in manifest.entry_points if item.name == entry_point), None)
    if entry is None:
        raise ValueError(f"plugin entry point is not declared: {entry_point}")
    errors = validate_configuration(entry, configuration)
    return {
        "plugin": manifest.name,
        "version": manifest.version,
        "entryPoint": entry.name,
        "valid": not errors,
        "errors": [item.model_dump(mode="json", by_alias=True) for item in errors],
        "catalog": next(
            item for item in plugin_catalog(manifest)["entryPoints"] if item["name"] == entry.name
        ),
    }


def scaffold_plugin(root: Path, *, name: str) -> tuple[Path, ...]:
    target = root.resolve()
    if target.exists() and any(target.iterdir()):
        raise ValueError("plugin scaffold target must be absent or empty")
    target.mkdir(parents=True, exist_ok=True)
    entry_type = f"{name}.echo"
    files = {
        "amesh-plugin.yaml": _starter_manifest(name, entry_type),
        "plugin.py": _starter_plugin(),
        "pyproject.toml": _starter_pyproject(name),
        "LICENSE": "MIT License\n\nReplace this starter text with the complete license before publishing.\n",
        "README.md": _starter_readme(name),
        "sample.yaml": "message: hello\n",
        "certification/compatibility.json": json.dumps(
            {"platformVersions": [__version__]}, indent=2
        )
        + "\n",
    }
    for fixture_name in REFERENCE_FIXTURES:
        files[f"certification/fixtures/{fixture_name}.json"] = (
            json.dumps(
                {
                    "schemaVersion": "amesh.plugin-fixture/v1",
                    "name": fixture_name,
                    "entryPoint": "task.echo",
                    "assertion": _fixture_assertion(fixture_name),
                    "evidenceFile": f"certification/evidence/{fixture_name}.json",
                },
                indent=2,
            )
            + "\n"
        )
        files[f"certification/evidence/{fixture_name}.json"] = (
            json.dumps({"status": "pending"}, indent=2) + "\n"
        )
    created: list[Path] = []
    for relative, content in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created.append(path)
    return tuple(created)


def _manifest_path(root: Path) -> Path:
    manifests = [root / name for name in _MANIFEST_NAMES if (root / name).is_file()]
    if len(manifests) != 1:
        raise ValueError("plugin root must contain exactly one amesh-plugin manifest")
    return manifests[0]


def _load_manifest(path: Path) -> PluginManifest:
    content = path.read_text(encoding="utf-8")
    payload: object = json.loads(content) if path.suffix == ".json" else yaml.safe_load(content)
    return PluginManifest.model_validate(payload)


def _compatibility_versions(root: Path) -> tuple[str, ...]:
    path = root / "certification" / "compatibility.json"
    if not path.is_file():
        return ()
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload.get("platformVersions") if isinstance(payload, dict) else None
    if (
        not isinstance(values, list)
        or not values
        or not all(isinstance(item, str) for item in values)
    ):
        raise ValueError("certification compatibility matrix requires platformVersions")
    if len(values) != len(set(values)):
        raise ValueError("certification platformVersions must be unique")
    return tuple(values)


def _compatibility(
    manifest: PluginManifest,
    platform_versions: tuple[str, ...],
) -> tuple[CompatibilityResult, ...]:
    try:
        specification = SimpleSpec(manifest.compatibility.platform_version)
    except ValueError:
        specification = None
    protocol_compatible = PLUGIN_PROTOCOL_VERSION in manifest.compatibility.protocol_versions
    results = []
    for platform_version in platform_versions:
        try:
            compatible = (
                specification is not None
                and specification.match(Version(platform_version))
                and protocol_compatible
            )
        except ValueError:
            compatible = False
        results.append(
            CompatibilityResult(
                platformVersion=platform_version,
                compatible=compatible,
                declaredRange=manifest.compatibility.platform_version,
            )
        )
    return tuple(results)


def _load_fixtures(
    root: Path,
    manifest: PluginManifest,
) -> tuple[tuple[CertificationFixture, ...], tuple[str, ...], tuple[Path, ...]]:
    directory = root / "certification" / "fixtures"
    entries = {item.name for item in manifest.entry_points}
    fixtures: list[CertificationFixture] = []
    errors: list[str] = []
    paths: list[Path] = []
    for name in REFERENCE_FIXTURES:
        path = directory / f"{name}.json"
        if not path.is_file():
            errors.append(f"missing fixture {name}")
            continue
        paths.append(path)
        try:
            fixture = CertificationFixture.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValidationError) as exc:
            errors.append(f"invalid fixture {name}: {type(exc).__name__}")
            continue
        if fixture.name != name:
            errors.append(f"fixture file {name} declares {fixture.name}")
            continue
        if fixture.entry_point not in entries:
            errors.append(f"fixture {name} references unknown entry point")
            continue
        evidence = root / fixture.evidence_file
        if not evidence.is_file() or evidence.is_symlink():
            errors.append(f"fixture {name} evidence is missing")
            continue
        try:
            evidence_payload = json.loads(evidence.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"fixture {name} evidence is invalid JSON")
            continue
        if not isinstance(evidence_payload, dict) or evidence_payload.get("status") != "passed":
            errors.append(f"fixture {name} evidence has not passed")
            continue
        paths.append(evidence)
        fixtures.append(fixture)
    return tuple(fixtures), tuple(errors), tuple(paths)


def _security_errors(manifest: PluginManifest) -> tuple[str, ...]:
    errors: list[str] = []
    if any(value == "*" or "*" in value for value in manifest.capabilities.allowed_egress):
        errors.append("network egress cannot use wildcards")
    for entry in manifest.entry_points:
        target = PurePosixPath(entry.target.replace("\\", "/"))
        if target.is_absolute() or ".." in target.parts:
            errors.append(f"entry point {entry.name} target escapes the package")
        properties = entry.configuration_schema.get("properties", {})
        if not isinstance(properties, dict):
            continue
        secret_properties = {
            name
            for name, schema in properties.items()
            if isinstance(schema, dict)
            and (schema.get("writeOnly") is True or schema.get("format") == "password")
        }
        for example in entry.documentation.examples:
            for name in secret_properties.intersection(example):
                value = example[name]
                if not isinstance(value, str) or not value.startswith("secret://"):
                    errors.append(
                        f"entry point {entry.name} example exposes secret property {name}"
                    )
    return tuple(errors)


def _public_ci_evidence(root: Path) -> tuple[PublicCiEvidence | None, Path | None]:
    path = root / "certification" / "evidence.json"
    if not path.is_file():
        return None, None
    return PublicCiEvidence.model_validate_json(path.read_text(encoding="utf-8")), path


def _quality_level(
    checks: tuple[CertificationCheck, ...],
    public_ci: PublicCiEvidence | None,
) -> PluginQualityLevel:
    passed = {item.category for item in checks if item.passed}
    if not {"manifest", "schema", "license"}.issubset(passed):
        return PluginQualityLevel.UNVERIFIED
    if not {item.category for item in checks}.issubset(passed):
        return PluginQualityLevel.COMMUNITY
    return PluginQualityLevel.CERTIFIED if public_ci is not None else PluginQualityLevel.VERIFIED


def _input_digest(root: Path, paths: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        relative = path.resolve().relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return "sha256:" + digest.hexdigest()


def _sample_from_schema(schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return {}
    return {
        name: _sample_value(value) for name, value in properties.items() if isinstance(value, dict)
    }


def _sample_value(schema: dict[str, Any]) -> Any:
    if schema.get("writeOnly") is True or schema.get("format") == "password":
        return "secret://replace-me"
    if "default" in schema:
        return schema["default"]
    if isinstance(schema.get("enum"), list) and schema["enum"]:
        return schema["enum"][0]
    schema_type = schema.get("type")
    return {
        "boolean": False,
        "integer": 0,
        "number": 0,
        "array": [],
        "object": {},
    }.get(schema_type if isinstance(schema_type, str) else "", "replace-me")


def _safe_relative_path(value: str) -> None:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("path must be a safe package-relative path")


def _starter_manifest(name: str, resource_type: str) -> str:
    if not re.fullmatch(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$", name):
        raise ValueError("plugin name must be a lowercase dotted identifier")
    return f"""schemaVersion: amesh.plugin/v1
name: {name}
version: 0.1.0
vendor: Replace me
license: MIT
description: Starter AMESH task plugin.
compatibility:
  platformVersion: \">=0.2.0,<0.3.0\"
  protocolVersions: [amesh.plugin.rpc/v1]
entryPoints:
  - name: task.echo
    resourceType: {resource_type}
    type: task
    transport: stdio
    target: plugin.py
    configurationSchema:
      $schema: https://json-schema.org/draft/2020-12/schema
      type: object
      properties:
        message: {{type: string, title: Message}}
      required: [message]
      additionalProperties: false
    outputSchema: {{type: object}}
    documentation:
      title: Echo
      description: Return one message.
      category: Examples
      propertyOrder: [message]
      examples: [{{message: hello}}]
capabilities:
  networkAccess: none
  filesystemAccess: none
"""


def _starter_plugin() -> str:
    return """from __future__ import annotations

import asyncio
from pathlib import Path

import yaml

from amesh.plugin_sdk import PluginManifest, PluginOperation, PluginResponse, serve_stdio_plugin


async def echo(request, capabilities):
    del capabilities
    return PluginResponse(
        invocationId=request.session.invocation_id,
        output={"message": request.configuration["message"]},
    )


manifest = PluginManifest.model_validate(
    yaml.safe_load(Path(__file__).with_name("amesh-plugin.yaml").read_text(encoding="utf-8"))
)

if __name__ == "__main__":
    asyncio.run(serve_stdio_plugin(manifest, {("task.echo", PluginOperation.EXECUTE): echo}))
"""


def _starter_pyproject(name: str) -> str:
    distribution = name.replace(".", "-")
    return f"""[project]
name = "{distribution}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["amesh>=0.2.0,<0.3.0", "PyYAML>=6,<7"]

[dependency-groups]
dev = ["pytest>=8,<9"]
"""


def _starter_readme(name: str) -> str:
    return f"""# {name}

Install dependencies with `uv sync`, validate configuration with
`uv run amesh plugins sandbox . task.echo --configuration sample.yaml`, and run all checks with
`uv run amesh plugins certify .`.
"""


def _fixture_assertion(name: str) -> str:
    return {
        "retries": "Retryable failures converge without duplicate committed output.",
        "cancellation": "Cancellation reaches the plugin and terminates bounded work.",
        "large-files": "Large files remain streamed and within the declared memory budget.",
        "secret-redaction": "Secret values never appear in outputs, logs, metrics or errors.",
        "worker-restart": "A restarted worker resumes or safely retries the in-flight invocation.",
    }[name]
