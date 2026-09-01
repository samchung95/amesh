#!/usr/bin/env python3
"""Run the versioned agent-session harness kit and emit a canonical JSON report."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from amesh.adapters.agent_session_harness import (  # noqa: E402
    _PI_ADAPTER_VERSION,
    _PI_WORKER_PROTOCOL,
)
from amesh.quality.agent_harness_conformance import (  # noqa: E402
    HarnessCaseStatus,
    HarnessConformanceCase,
    HarnessConformanceCaseResult,
    HarnessConformanceManifest,
    HarnessConformanceReport,
    HarnessDependencyProvenance,
    HarnessPackageProvenance,
    HarnessRuntimeVersions,
    canonical_report_json,
    dependency_license,
    manifest_digest,
    sha256_file,
)

DEFAULT_MANIFEST = ROOT / "schemas" / "agent-harness-conformance-manifest-v1.json"
DEFAULT_LOCK_FILE = ROOT / "harnesses" / "pi" / "package-lock.json"
DEFAULT_WORKER_FILE = ROOT / "harnesses" / "pi" / "src" / "worker.mjs"
DEFAULT_ADAPTER = "pi-agent-core"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_FILE)
    parser.add_argument("--adapter", choices=("pi",), default="pi")
    parser.add_argument("--worker-file", type=Path, default=DEFAULT_WORKER_FILE)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def _amesh_version() -> str:
    try:
        return importlib.metadata.version("amesh")
    except importlib.metadata.PackageNotFoundError:
        with (ROOT / "pyproject.toml").open("rb") as handle:
            return str(tomllib.load(handle)["project"]["version"])


def _node_version() -> str:
    try:
        completed = subprocess.run(
            ["node", "--version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return "unavailable"
    version = completed.stdout.strip()
    return version if completed.returncode == 0 and version else "unavailable"


def _lock_provenance(path: Path) -> HarnessPackageProvenance:
    lock_bytes = path.read_bytes()
    document = json.loads(lock_bytes)
    dependencies: list[HarnessDependencyProvenance] = []
    for package_path, package in document.get("packages", {}).items():
        if not package_path or not package_path.startswith("node_modules/"):
            continue
        if not isinstance(package, dict) or not package.get("version"):
            continue
        package_name = package_path.rsplit("node_modules/", 1)[-1]
        dependencies.append(
            HarnessDependencyProvenance(
                package=package_name,
                version=str(package["version"]),
                license=dependency_license(package.get("license")),
                integrity=str(package["integrity"]) if package.get("integrity") else None,
                resolved=str(package["resolved"]) if package.get("resolved") else None,
            )
        )
    dependencies.sort(key=lambda item: (item.package, item.version, item.integrity or ""))
    return HarnessPackageProvenance(
        lockFile=path.relative_to(ROOT).as_posix(),
        lockSha256=sha256_file(path),
        dependencies=tuple(dependencies),
    )


def _relative_file(value: str | None) -> str | None:
    if value is None:
        return None
    candidate = Path(value)
    if not candidate.is_absolute():
        return candidate.as_posix()
    try:
        return candidate.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return candidate.as_posix()


def _junit_results(path: Path) -> dict[str, HarnessCaseStatus]:
    root = ElementTree.parse(path).getroot()
    results: dict[str, HarnessCaseStatus] = {}
    for testcase in root.iter("testcase"):
        file_name = _relative_file(testcase.attrib.get("file"))
        name = testcase.attrib.get("name", "")
        node_id = f"{file_name}::{name}" if file_name else name
        if testcase.find("error") is not None:
            status = HarnessCaseStatus.ERROR
        elif testcase.find("failure") is not None:
            status = HarnessCaseStatus.FAILED
        elif testcase.find("skipped") is not None:
            status = HarnessCaseStatus.SKIPPED
        else:
            status = HarnessCaseStatus.PASSED
        results[node_id] = status
    return results


def _status_for_case(
    case: HarnessConformanceCase, results: dict[str, HarnessCaseStatus]
) -> HarnessCaseStatus:
    direct = results.get(case.pytest_node_id)
    if direct is not None:
        return direct
    # pytest can omit its file attribute in some junit-family versions. The manifest
    # node IDs are still unambiguous, so match the final function name as a fallback.
    test_name = case.pytest_node_id.rsplit("::", 1)[-1]
    matches = [
        status for node_id, status in results.items() if node_id.rsplit("::", 1)[-1] == test_name
    ]
    return matches[0] if len(matches) == 1 else HarnessCaseStatus.MISSING


def run(manifest: HarnessConformanceManifest, args: argparse.Namespace) -> HarnessConformanceReport:
    with tempfile.TemporaryDirectory(prefix="amesh-harness-conformance-") as directory:
        junit_path = Path(directory) / "junit.xml"
        command = [
            sys.executable,
            "-m",
            "pytest",
            "--junitxml",
            str(junit_path),
            *[case.pytest_node_id for case in manifest.cases],
        ]
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        results = _junit_results(junit_path) if junit_path.exists() else {}
    case_results = tuple(
        HarnessConformanceCaseResult(
            caseId=case.case_id,
            surface=case.surface,
            pytestNodeId=case.pytest_node_id,
            status=_status_for_case(case, results)
            if completed.returncode == 0
            else (
                _status_for_case(case, results)
                if case.pytest_node_id in results
                else HarnessCaseStatus.ERROR
            ),
        )
        for case in manifest.cases
    )
    passed = sum(item.status is HarnessCaseStatus.PASSED for item in case_results)
    skipped = sum(item.status is HarnessCaseStatus.SKIPPED for item in case_results)
    failed = len(case_results) - passed - skipped
    return HarnessConformanceReport(
        kitVersion=manifest.kit_version,
        portVersion="amesh.agent-session-harness/v2",
        manifestDigest=manifest_digest(manifest),
        adapter=DEFAULT_ADAPTER,
        adapterVersion=_PI_ADAPTER_VERSION,
        workerProtocol=_PI_WORKER_PROTOCOL,
        workerFile=args.worker_file.relative_to(ROOT).as_posix(),
        workerSha256=sha256_file(args.worker_file),
        ameshVersion=_amesh_version(),
        runtime=HarnessRuntimeVersions(python=platform.python_version(), node=_node_version()),
        packageProvenance=_lock_provenance(args.lock_file),
        cases=case_results,
        passed=passed,
        failed=failed,
        skipped=skipped,
        overall="passed" if failed == 0 and skipped == 0 else "failed",
    ).with_digest()


def main() -> int:
    args = _parse_args()
    manifest = HarnessConformanceManifest.model_validate_json(
        args.manifest.read_text(encoding="utf-8")
    )
    report = run(manifest, args)
    encoded = canonical_report_json(report)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded + b"\n")
    sys.stdout.write(encoded.decode("utf-8") + "\n")
    return 0 if report.overall == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
