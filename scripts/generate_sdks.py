#!/usr/bin/env python3
"""Generate the published AMESH API clients from the checked-in OpenAPI contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "docs" / "api" / "openapi.json"
SDK_ROOT = ROOT / "sdks" / "api"
TEMPLATE_ROOT = ROOT / "scripts" / "sdk_templates"
GENERATOR_IMAGE = (
    "openapitools/openapi-generator-cli@"
    "sha256:5bf3dc75f764c584da8e3344c51b2f3f1e74703461d46a035b5ac1d31515cc88"
)
GO_FORMATTER_IMAGE = (
    "golang@sha256:60deed95d3888cc5e4d9ff8a10c54e5edc008c6ae3fba6187be6fb592e19e8c0"
)


@dataclass(frozen=True)
class Target:
    name: str
    generator: str
    package: str
    properties: tuple[str, ...]
    arguments: tuple[str, ...] = ()


TARGETS = (
    Target(
        "python",
        "python",
        "amesh-client",
        (
            "packageName=amesh_client",
            "projectName=amesh-client",
            "packageVersion=0.2.0",
            "hideGenerationTimestamp=true",
        ),
    ),
    Target(
        "typescript",
        "typescript-fetch",
        "@amesh/client",
        (
            "npmName=@amesh/client",
            "npmVersion=0.2.0",
            "supportsES6=true",
            "hideGenerationTimestamp=true",
        ),
    ),
    Target(
        "java",
        "java",
        "io.amesh:amesh-client",
        (
            "library=native",
            "groupId=io.amesh",
            "artifactId=amesh-client",
            "artifactVersion=0.2.0",
            "apiPackage=io.amesh.client.api",
            "modelPackage=io.amesh.client.model",
            "hideGenerationTimestamp=true",
        ),
    ),
    Target(
        "go",
        "go",
        "github.com/amesh/amesh-client-go",
        (
            "packageName=ameshclient",
            "packageVersion=0.2.0",
            "moduleName=github.com/amesh/amesh-client-go",
            "isGoSubmodule=false",
            "enumClassPrefix=true",
            "hideGenerationTimestamp=true",
        ),
    ),
)


def _safe_replace_directory(path: Path, allowed_parent: Path) -> None:
    resolved = path.resolve()
    parent = allowed_parent.resolve()
    if resolved == parent or not resolved.is_relative_to(parent):
        raise RuntimeError(f"refusing to replace SDK path outside {parent}: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def _container_path(path: Path) -> str:
    return "/local/" + path.resolve().relative_to(ROOT).as_posix()


def _run_generator(target: Target, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{ROOT}:/local",
        GENERATOR_IMAGE,
        "generate",
        "-i",
        "/local/docs/api/openapi.json",
        "-g",
        target.generator,
        "-o",
        _container_path(destination),
        "--additional-properties",
        ",".join((*target.properties, "licenseName=AGPL-3.0-only")),
        "--global-property",
        "apiDocs=true,modelDocs=false,apiTests=false,modelTests=false",
        "--git-user-id",
        "amesh",
        "--git-repo-id",
        f"amesh-client-{target.name}",
        *target.arguments,
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"{target.name} SDK generation failed\n{completed.stdout}\n{completed.stderr}"
        )
    print(f"generated {target.name} SDK")


def _write_pagination_helpers(root: Path) -> None:
    python_helper = root / "python" / "amesh_client" / "pagination.py"
    python_helper.write_text(
        """from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, TypeVar

T = TypeVar(\"T\")
PageLoader = Callable[[str | None], dict[str, Any]]


def iterate_pages(load: PageLoader) -> Iterator[Any]:
    cursor: str | None = None
    while True:
        page = load(cursor)
        yield from page.get(\"items\", [])
        cursor = page.get(\"nextCursor\")
        if not cursor:
            return
""",
        encoding="utf-8",
    )

    typescript_helper = root / "typescript" / "src" / "pagination.ts"
    typescript_helper.write_text(
        """export interface Page<T> { items: T[]; nextCursor?: string | null }

export async function collectPages<T>(
  load: (cursor?: string) => Promise<Page<T>>,
): Promise<T[]> {
  const items: T[] = [];
  let cursor: string | undefined;
  do {
    const page = await load(cursor);
    items.push(...page.items);
    cursor = page.nextCursor ?? undefined;
  } while (cursor);
  return items;
}
""",
        encoding="utf-8",
    )
    typescript_index = root / "typescript" / "src" / "index.ts"
    with typescript_index.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("export * from './pagination';\n")

    java_helper = root / "java" / "src" / "main" / "java" / "io" / "amesh" / "client"
    java_helper.mkdir(parents=True, exist_ok=True)
    (java_helper / "Pagination.java").write_text(
        """package io.amesh.client;

import java.util.ArrayList;
import java.util.List;

public final class Pagination {
    private Pagination() {}

    public static final class Page<T> {
        private final List<T> items;
        private final String nextCursor;

        public Page(List<T> items, String nextCursor) {
            this.items = List.copyOf(items);
            this.nextCursor = nextCursor;
        }

        public List<T> items() { return items; }
        public String nextCursor() { return nextCursor; }
    }

    @FunctionalInterface
    public interface Loader<T> {
        Page<T> load(String cursor) throws Exception;
    }

    public static <T> List<T> collect(Loader<T> loader) throws Exception {
        List<T> items = new ArrayList<>();
        String cursor = null;
        do {
            Page<T> page = loader.load(cursor);
            items.addAll(page.items());
            cursor = page.nextCursor();
        } while (cursor != null && !cursor.isEmpty());
        return List.copyOf(items);
    }
}
""",
        encoding="utf-8",
    )

    (root / "go" / "pagination.go").write_text(
        """package ameshclient

import \"context\"

type Page[T any] struct {
\tItems      []T
\tNextCursor string
}

type PageLoader[T any] func(context.Context, string) (Page[T], error)

func CollectPages[T any](ctx context.Context, load PageLoader[T]) ([]T, error) {
\tvar all []T
\tvar cursor string
\tfor {
\t\tpage, err := load(ctx, cursor)
\t\tif err != nil {
\t\t\treturn nil, err
\t\t}
\t\tall = append(all, page.Items...)
\t\tcursor = page.NextCursor
\t\tif cursor == \"\" {
\t\t\treturn all, nil
\t\t}
\t}
}
""",
        encoding="utf-8",
    )


def _write_execution_helpers(root: Path) -> None:
    targets = {
        TEMPLATE_ROOT / "python" / "execution.py": (
            root / "python" / "amesh_client" / "execution.py"
        ),
        TEMPLATE_ROOT / "typescript" / "execution.ts": (
            root / "typescript" / "src" / "execution.ts"
        ),
        TEMPLATE_ROOT / "java" / "AmeshExecutionClient.java": (
            root
            / "java"
            / "src"
            / "main"
            / "java"
            / "io"
            / "amesh"
            / "client"
            / "AmeshExecutionClient.java"
        ),
        TEMPLATE_ROOT / "java" / "AnyOf.java": (
            root
            / "java"
            / "src"
            / "main"
            / "java"
            / "io"
            / "amesh"
            / "client"
            / "model"
            / "AnyOf.java"
        ),
        TEMPLATE_ROOT / "go" / "execution_client.go": root / "go" / "execution_client.go",
        TEMPLATE_ROOT / "go" / "any_of.go": root / "go" / "any_of.go",
        TEMPLATE_ROOT / "go" / "execution_client_test.go": (
            root / "go" / "execution_client_test.go"
        ),
    }
    for source, destination in targets.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    python_init = root / "python" / "amesh_client" / "__init__.py"
    with python_init.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(
            "from amesh_client.execution import (\n"
            "    AmeshError as AmeshError,\n"
            "    AsyncExecutionClient as AsyncExecutionClient,\n"
            "    ExecutionClient as ExecutionClient,\n"
            "    RetryPolicy as RetryPolicy,\n"
            "    verify_webhook as verify_webhook,\n"
            ")\n"
        )
    typescript_index = root / "typescript" / "src" / "index.ts"
    with typescript_index.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("export * from './execution';\n")


def _repair_typescript_generator_gaps(root: Path) -> None:
    """Keep the pinned generator's unconstrained FormField.default model compilable."""
    form_field = root / "typescript" / "src" / "models" / "FormField.ts"
    content = form_field.read_text(encoding="utf-8")
    replacements = {
        "_default?:  | null;": "_default?: unknown | null;",
        "FromJSON(json['default'])": "json['default']",
        "ToJSON(value['_default'])": "value['_default']",
    }
    for old, new in replacements.items():
        if old not in content:
            raise RuntimeError(f"generated TypeScript FormField marker changed: {old}")
        content = content.replace(old, new, 1)
    form_field.write_text(content, encoding="utf-8")

    for name in ("tsconfig.json", "tsconfig.esm.json"):
        path = root / "typescript" / name
        document = json.loads(path.read_text(encoding="utf-8"))
        compiler = document.setdefault("compilerOptions", {})
        compiler["target"] = "es2018"
        compiler["lib"] = ["ES2018", "DOM", "DOM.Iterable"]
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def _repair_and_format_go_generator_gaps(root: Path) -> None:
    """Repair pinned-generator union defaults, then format generated Go deterministically."""

    tolerance = root / "go" / "model_tolerance.go"
    content = tolerance.read_text(encoding="utf-8")
    replacements = {
        "var absolute Absolute = 0": ('var absolute Absolute = Absolute{String: PtrString("0")}'),
        "var relative Relative = 0": ('var relative Relative = Relative{String: PtrString("0")}'),
    }
    for old, new in replacements.items():
        if content.count(old) != 2:
            raise RuntimeError(f"generated Go Tolerance marker changed: {old}")
        content = content.replace(old, new)
    tolerance.write_text(content, encoding="utf-8")

    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{ROOT}:/local",
        "-w",
        _container_path(root / "go"),
        GO_FORMATTER_IMAGE,
        "sh",
        "-c",
        "find . -type f -name '*.go' -print0 | xargs -0 gofmt -w",
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Go SDK formatting failed\n{completed.stdout}\n{completed.stderr}")


def _write_license_metadata(root: Path) -> None:
    for target in TARGETS:
        shutil.copy2(ROOT / "LICENSE", root / target.name / "LICENSE")
    python_project = root / "python" / "pyproject.toml"
    content = python_project.read_text(encoding="utf-8")
    marker = 'description = "AMESH"\n'
    if marker not in content:
        raise RuntimeError("generated Python package metadata changed unexpectedly")
    python_project.write_text(
        content.replace(marker, marker + 'license = {file = "LICENSE"}\n', 1),
        encoding="utf-8",
    )


def _remove_generated_github_actions(root: Path) -> None:
    """Keep published SDK trees free of executable GitHub Actions workflows."""
    for target in TARGETS:
        target_root = root / target.name
        workflow_root = target_root / ".github" / "workflows"
        if workflow_root.exists():
            shutil.rmtree(workflow_root)
        github_root = workflow_root.parent
        if github_root.exists() and not any(github_root.iterdir()):
            github_root.rmdir()

        generator_files = target_root / ".openapi-generator" / "FILES"
        if generator_files.exists():
            retained = [
                line
                for line in generator_files.read_text(encoding="utf-8").splitlines()
                if not line.startswith(".github/workflows/")
            ]
            generator_files.write_text("\n".join(retained) + "\n", encoding="utf-8")


def _write_manifest(root: Path) -> None:
    contract = json.loads(OPENAPI.read_text(encoding="utf-8"))
    manifest = {
        "schemaVersion": 1,
        "apiVersion": contract["info"]["version"],
        "compatibleApiVersions": ">=0.2.0,<0.3.0",
        "openapiSha256": hashlib.sha256(OPENAPI.read_bytes()).hexdigest(),
        "generatorImage": GENERATOR_IMAGE,
        "goFormatterImage": GO_FORMATTER_IMAGE,
        "clients": [
            {
                "language": target.name,
                "package": target.package,
                "path": target.name,
                "paginationHelper": True,
                "executionClient": True,
            }
            for target in TARGETS
        ],
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / "README.md").write_text(
        """# AMESH API clients

These typed Python, TypeScript, Java and Go clients are generated from
`docs/api/openapi.json` with the pinned OpenAPI Generator image recorded in `manifest.json`.
Each package is versioned with AMESH 0.2.0 and declares compatibility with the 0.2 API line.

Regenerate or verify all clients from the repository root:

```console
uv run python scripts/generate_sdks.py
uv run python scripts/generate_sdks.py --check
```

Configure generated clients with `Authorization: Bearer <token>` and `X-Amesh-Tenant`. Each package
includes a hand-written execution client for bounded retries, idempotent launch, terminal waiting,
cancellation, logs, artifact download, NDJSON streaming and webhook signature verification. The
language-specific `pagination` helper repeatedly calls a cursor-aware page loader until `nextCursor`
is empty. Generated models and APIs should not be edited directly; execution helpers are maintained
under `scripts/sdk_templates` and copied during generation.
""",
        encoding="utf-8",
    )


def _remove_missing_markdown_links(root: Path) -> None:
    """Remove links to model docs omitted by the apiDocs-only generation profile."""

    markdown_link = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")

    for path in sorted(root.rglob("*.md")):
        content = path.read_text(encoding="utf-8")

        def replace_link(match: re.Match[str], parent: Path = path.parent) -> str:
            label, target = match.groups()
            if target.startswith(("#", "/", "http://", "https://", "mailto:")):
                return match.group(0)
            document_target = target.split("#", 1)[0]
            if not document_target.lower().endswith(".md"):
                return match.group(0)
            if (parent / document_target).exists():
                return match.group(0)
            return label

        normalized = markdown_link.sub(replace_link, content)
        if normalized != content:
            path.write_text(normalized, encoding="utf-8")


def _normalize_generated_text(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lines = [line.rstrip() for line in content.splitlines()]
        while lines and not lines[-1]:
            lines.pop()
        normalized = "\n".join(lines)
        if normalized:
            normalized += "\n"
        path.write_text(normalized, encoding="utf-8", newline="\n")


def generate(root: Path, *, allowed_parent: Path) -> None:
    _safe_replace_directory(root, allowed_parent)
    for target in TARGETS:
        _run_generator(target, root / target.name)
    _remove_generated_github_actions(root)
    _write_license_metadata(root)
    _write_pagination_helpers(root)
    _write_execution_helpers(root)
    _repair_typescript_generator_gaps(root)
    _repair_and_format_go_generator_gaps(root)
    _write_manifest(root)
    _remove_missing_markdown_links(root)
    _normalize_generated_text(root)


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        SDK_ROOT.parent.mkdir(parents=True, exist_ok=True)
        generate(SDK_ROOT, allowed_parent=SDK_ROOT.parent)
        print(f"generated {len(TARGETS)} SDKs in {SDK_ROOT}")
        return 0
    build_root = ROOT / "build"
    build_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sdk-check-", dir=build_root) as temporary:
        candidate = Path(temporary) / "api"
        generate(candidate, allowed_parent=Path(temporary))
        expected = _tree_hashes(SDK_ROOT)
        actual = _tree_hashes(candidate)
    if expected != actual:
        missing = sorted(set(expected) - set(actual))
        added = sorted(set(actual) - set(expected))
        changed = sorted(
            key for key in expected.keys() & actual.keys() if expected[key] != actual[key]
        )
        raise RuntimeError(
            "generated SDKs are stale: "
            f"missing={missing[:5]}, added={added[:5]}, changed={changed[:5]}"
        )
    print(f"generated SDKs are current ({len(expected)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
