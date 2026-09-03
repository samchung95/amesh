#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from backlog_io import load_epic_catalog

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []

    baseline = load_json(ROOT / "project-baseline.json")
    urs = load_json(ROOT / "requirements" / "urs.json")
    catalog = load_epic_catalog(ROOT)
    backlog = catalog.manifest
    milestones = load_json(ROOT / "backlog" / "milestones.json")
    labels = load_json(ROOT / "backlog" / "labels.json")
    source_provenance = load_json(ROOT / "requirements" / "source-provenance.json")
    compatibility_inventory = load_json(ROOT / "requirements" / "compatibility-inventory.json")

    epic_records: list[dict[str, Any]] = catalog.epics
    functional: list[dict[str, Any]] = urs["functional_requirements"]
    nonfunctional: list[dict[str, Any]] = urs["nonfunctional_requirements"]

    epic_ids = [epic["id"] for epic in epic_records]
    requirement_ids = [item["id"] for item in functional] + [item["id"] for item in nonfunctional]
    milestone_ids = {item["id"] for item in milestones}
    label_names = {item["name"] for item in labels}

    duplicates = [item for item, count in Counter(epic_ids).items() if count > 1]
    if duplicates:
        fail(errors, f"duplicate epic IDs: {duplicates}")

    duplicates = [item for item, count in Counter(requirement_ids).items() if count > 1]
    if duplicates:
        fail(errors, f"duplicate requirement IDs: {duplicates}")

    body_files = [epic["body_file"] for epic in epic_records]
    duplicates = [item for item, count in Counter(body_files).items() if count > 1]
    if duplicates:
        fail(errors, f"duplicate epic body paths: {duplicates}")

    if len(epic_records) != backlog["metadata"]["epic_count"]:
        fail(errors, "epic count does not match backlog metadata")
    active_count = sum(epic.get("state") != "done" for epic in epic_records)
    archived_count = len(epic_records) - active_count
    if active_count != backlog["metadata"].get("active_epic_count"):
        fail(errors, "active epic count does not match backlog metadata")
    if archived_count != backlog["metadata"].get("archived_epic_count"):
        fail(errors, "archived epic count does not match backlog metadata")
    if len(functional) != urs["metadata"]["functional_requirement_count"]:
        fail(errors, "functional requirement count does not match URS metadata")
    if len(nonfunctional) != urs["metadata"]["nonfunctional_requirement_count"]:
        fail(errors, "non-functional requirement count does not match URS metadata")
    if len(requirement_ids) != urs["metadata"]["total_requirement_count"]:
        fail(errors, "total requirement count does not match URS metadata")
    if len(epic_records) != urs["metadata"]["epic_count"]:
        fail(errors, "URS epic count does not match backlog")

    epic_by_id = {epic["id"]: epic for epic in epic_records}
    mapped_functional: set[str] = set()
    mapped_nfr: set[str] = set()

    for epic in epic_records:
        if epic["milestone"] not in milestone_ids:
            fail(errors, f"{epic['id']} references unknown milestone {epic['milestone']}")
        else:
            milestone = next(item for item in milestones if item["id"] == epic["milestone"])
            if epic["wave"] != milestone["wave"]:
                fail(errors, f"{epic['id']} wave differs from milestone {epic['milestone']}")
        if epic["id"] in epic.get("dependencies", []):
            fail(errors, f"{epic['id']} depends on itself")
        for dependency in epic.get("dependencies", []):
            if dependency not in epic_by_id:
                fail(errors, f"{epic['id']} references unknown dependency {dependency}")
        for label in epic.get("labels", []):
            if label not in label_names:
                fail(errors, f"{epic['id']} references undeclared label {label}")

        body_path = ROOT / epic["body_file"]
        if not body_path.is_file():
            fail(errors, f"{epic['id']} body file is missing: {epic['body_file']}")
        elif body_path.read_text(encoding="utf-8") != epic["body"]:
            fail(errors, f"{epic['id']} body file differs from the combined epic catalog")

        for requirement_id in epic["requirement_ids"]:
            mapped_functional.add(requirement_id)
        for requirement_id in epic["nfr_ids"]:
            mapped_nfr.add(requirement_id)

    for requirement in functional:
        epic_id = requirement["epic_id"]
        if epic_id not in epic_by_id:
            fail(errors, f"{requirement['id']} references unknown epic {epic_id}")
            continue
        if requirement["id"] not in epic_by_id[epic_id]["requirement_ids"]:
            fail(errors, f"{requirement['id']} is absent from {epic_id} issue traceability")

    for requirement in nonfunctional:
        if not requirement["epic_ids"]:
            fail(errors, f"{requirement['id']} has no mapped epic")
        for epic_id in requirement["epic_ids"]:
            if epic_id not in epic_by_id:
                fail(errors, f"{requirement['id']} references unknown epic {epic_id}")
            elif requirement["id"] not in epic_by_id[epic_id]["nfr_ids"]:
                fail(errors, f"{requirement['id']} is absent from {epic_id} issue traceability")

    missing_functional = {item["id"] for item in functional} - mapped_functional
    missing_nfr = {item["id"] for item in nonfunctional} - mapped_nfr
    if missing_functional:
        fail(
            errors,
            f"functional requirements not mapped to issue bodies: {sorted(missing_functional)}",
        )
    if missing_nfr:
        fail(
            errors, f"non-functional requirements not mapped to issue bodies: {sorted(missing_nfr)}"
        )

    trace_path = ROOT / "requirements" / "traceability.csv"
    with trace_path.open(newline="", encoding="utf-8") as handle:
        trace_rows = list(csv.DictReader(handle))
    traced_ids = {row["requirement_id"] for row in trace_rows}
    missing_trace = set(requirement_ids) - traced_ids
    if missing_trace:
        fail(errors, f"requirements missing from traceability.csv: {sorted(missing_trace)}")
    extra_trace = traced_ids - set(requirement_ids)
    if extra_trace:
        fail(errors, f"unknown requirements in traceability.csv: {sorted(extra_trace)}")

    expected_trace_pairs = {(item["id"], item["epic_id"]) for item in functional} | {
        (item["id"], epic_id) for item in nonfunctional for epic_id in item["epic_ids"]
    }
    actual_trace_pairs = {(row["requirement_id"], row["epic_id"]) for row in trace_rows}
    if actual_trace_pairs != expected_trace_pairs or len(trace_rows) != len(expected_trace_pairs):
        fail(errors, "traceability.csv does not exactly match canonical requirement-to-epic links")

    urs_csv_path = ROOT / "requirements" / "urs.csv"
    with urs_csv_path.open(newline="", encoding="utf-8") as handle:
        urs_rows = list(csv.DictReader(handle))
    exported_ids = [row["id"] for row in urs_rows]
    if exported_ids != requirement_ids:
        fail(errors, "urs.csv IDs or order differ from canonical requirements")

    issue_path = ROOT / "backlog" / "github-issues.ndjson"
    try:
        issue_records = [
            json.loads(line) for line in issue_path.read_text(encoding="utf-8").splitlines()
        ]
    except json.JSONDecodeError as exc:
        fail(errors, f"github-issues.ndjson is invalid: {exc}")
        issue_records = []
    if len(issue_records) != len(epic_records):
        fail(errors, "github-issues.ndjson issue count differs from the combined epic catalog")
    else:
        for epic, issue in zip(epic_records, issue_records, strict=True):
            expected_issue = {
                "title": f"{epic['id']}: {epic['title']}",
                "body": epic["body"],
                "labels": epic["labels"],
                "milestone": epic["milestone"],
            }
            if issue != expected_issue:
                fail(errors, f"GitHub issue export differs for {epic['id']}")

    parity_path = ROOT / "requirements" / "parity-matrix.csv"
    with parity_path.open(newline="", encoding="utf-8") as handle:
        parity_rows = list(csv.DictReader(handle))
    if {row["epic_id"] for row in parity_rows} != set(epic_ids):
        fail(errors, "parity-matrix.csv does not contain exactly one row per epic")

    expected_target = baseline["parity_target"]
    actual_target = urs["metadata"]["parity_target"]
    if expected_target != actual_target:
        fail(errors, "URS parity target differs from project-baseline.json")
    if source_provenance.get("target") != expected_target:
        fail(errors, "source-provenance target differs from project-baseline.json")
    if compatibility_inventory.get("target") != expected_target:
        fail(errors, "compatibility inventory target differs from project-baseline.json")

    inventory_schema = load_json(ROOT / "schemas" / "compatibility-inventory.schema.json")
    for validation_error in sorted(
        Draft202012Validator(inventory_schema).iter_errors(compatibility_inventory),
        key=lambda item: list(item.absolute_path),
    ):
        location = "/".join(str(part) for part in validation_error.absolute_path) or "root"
        fail(
            errors,
            f"compatibility inventory schema violation at {location}: {validation_error.message}",
        )

    registered_sources = [item.get("id") for item in source_provenance.get("sources", [])]
    duplicate_sources = [item for item, count in Counter(registered_sources).items() if count > 1]
    if duplicate_sources:
        fail(errors, f"duplicate source-provenance IDs: {duplicate_sources}")
    known_sources = set(registered_sources)
    functional_domains = {item["domain"] for item in functional}
    missing_domain_defaults = functional_domains - set(source_provenance.get("domain_defaults", {}))
    if missing_domain_defaults:
        fail(errors, f"source provenance lacks domain defaults: {sorted(missing_domain_defaults)}")

    strict_mode = source_provenance.get("strict_mode", {})
    required_roles = strict_mode.get("required_roles", [])
    if required_roles != ["reference-researcher", "implementer", "reviewer", "verifier"]:
        fail(errors, "strict clean-room role sequence is incomplete or reordered")
    if not strict_mode.get("allowed_handoff_artifacts"):
        fail(errors, "strict clean-room mode has no allowed handoff artifact list")
    if not strict_mode.get("forbidden_handoff_artifacts"):
        fail(errors, "strict clean-room mode has no forbidden handoff artifact list")

    inventory_items = compatibility_inventory.get("items", [])
    inventory_ids = [item.get("requirement_id") for item in inventory_items]
    if inventory_ids != [item["id"] for item in functional]:
        fail(errors, "compatibility inventory IDs or order differ from functional requirements")
    functional_by_id = {item["id"]: item for item in functional}
    for item in inventory_items:
        requirement = functional_by_id.get(item.get("requirement_id"))
        if requirement is None:
            continue
        epic = epic_by_id[requirement["epic_id"]]
        if item.get("epic_id") != epic["id"]:
            fail(errors, f"{requirement['id']} compatibility inventory epic differs")
        if item.get("implementation_status") != requirement["status"]:
            fail(errors, f"{requirement['id']} compatibility status differs from the URS")
        unknown_source_ids = set(item.get("source_ids", [])) - known_sources
        if unknown_source_ids:
            fail(
                errors,
                f"{requirement['id']} uses unknown source IDs: {sorted(unknown_source_ids)}",
            )
        is_intentional = "difference:intentional" in epic.get("labels", [])
        if is_intentional and item.get("disposition") != "intentional-difference":
            fail(errors, f"{requirement['id']} must be an intentional difference")
        if (
            requirement["status"] == "Verified"
            and not is_intentional
            and item.get("disposition") != "verified"
        ):
            fail(errors, f"{requirement['id']} verified status lacks verified disposition")
        if item.get("disposition") == "verified" and not item.get("evidence"):
            fail(errors, f"{requirement['id']} verified disposition lacks evidence")

    if errors:
        print("Backlog validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Backlog valid: "
        f"{len(epic_records)} epics, "
        f"{len(functional)} functional requirements, "
        f"{len(nonfunctional)} non-functional requirements, "
        f"{len(trace_rows)} traceability links."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
