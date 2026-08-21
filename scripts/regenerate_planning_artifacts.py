#!/usr/bin/env python3
"""Regenerate human-readable planning and traceability artifacts from canonical JSON.

Canonical inputs:
- project-baseline.json
- backlog/milestones.json
- backlog/epics.json
- requirements/urs.json

The script is intentionally deterministic. Run it after any requirement or epic change and
check the generated files into the same pull request.
"""

from __future__ import annotations

import csv
import io
import json
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> Any:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def write_text(relative_path: str, value: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not value.endswith("\n"):
        value += "\n"
    path.write_text(value, encoding="utf-8", newline="\n")


def csv_text(fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({name: row.get(name, "") for name in fieldnames})
    return buffer.getvalue()


def milestone_lookup(milestones: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in milestones}


def sorted_epics(epics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(epics, key=lambda item: (item["wave"], item["id"]))


def parity_scope(epic: dict[str, Any], existing: dict[str, dict[str, str]]) -> tuple[str, str]:
    prior = existing.get(epic["id"])
    if prior:
        return prior["parity_scope"], prior["compatibility_level"]
    labels = set(epic.get("labels", []))
    if "difference:intentional" in labels:
        return "AMESH differentiator; not a Kestra-parity claim", "Intentional difference"
    if "parity:open-enterprise" in labels:
        return (
            "Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation",
            "P0 capability",
        )
    if "parity:compatibility" in labels:
        return (
            "Kestra v1.3.30 public behavior and architecture parity baseline",
            "P1 selected configuration",
        )
    return "Kestra v1.3.30 public behavior and architecture parity baseline", "P0 capability"


def render_urs(
    baseline: dict[str, Any],
    urs: dict[str, Any],
    milestones: list[dict[str, Any]],
    epics: list[dict[str, Any]],
) -> str:
    meta = urs["metadata"]
    target = meta["parity_target"]
    functional = urs["functional_requirements"]
    nonfunctional = urs["nonfunctional_requirements"]
    funcs_by_epic: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in functional:
        funcs_by_epic[item["epic_id"]].append(item)
    epics_by_milestone: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for epic in sorted_epics(epics):
        epics_by_milestone[epic["milestone"]].append(epic)

    lines = [
        "# User Requirements Specification (URS)",
        "",
        f"**Product:** {meta['product']} — {meta.get('product_expansion', 'Agent Mesh')}",
        f"**Baseline:** {target['product']} {target['version']} / `{target['commit']}`",
        f"**Status:** {meta['status']}",
        f"**Generated:** {meta['generated_on']}",
        f"**Functional requirements:** {meta['functional_requirement_count']}",
        f"**Non-functional requirements:** {meta['nonfunctional_requirement_count']}",
        f"**Total:** {meta['total_requirement_count']}",
        "",
        "## 1. Purpose",
        "",
        "This URS defines the observable outcomes, quality attributes and verification expectations for AMESH: a clean-room, fully open-source, Kestra-compatible durable workflow and agent orchestration platform. It is an implementation baseline, not a claim that all requirements already exist.",
        "",
        "## 2. Requirement language",
        "",
        "- **Shall** is mandatory for the selected release scope.",
        "- **Must/Should/Could** are MoSCoW priorities.",
        "- **Verified** requires linked evidence; code completion alone is not verification.",
        "- Compatibility is version-pinned and may be claimed only for surfaces with passing differential evidence.",
        "",
        "## 3. Binding product decisions",
        "",
        f"- Product name: **{baseline['product']} ({baseline['product_expansion']})**.",
        f"- Licence grant: **{baseline['license']}**.",
        "- Implementation model: strict clean room based on public specifications, observable behavior and independently authored tests.",
        "- Scope: Kestra OSS parity, independently implemented advanced capabilities, and AMESH-specific agent-mesh differentiation in one open distribution.",
        "- Compatibility surfaces: Kestra YAML, Pebble expressions, REST API, CLI, execution semantics and documented import/export formats.",
        "- Reference persistence and durable internal transport: PostgreSQL only; LISTEN/NOTIFY is an optimization, never delivery truth.",
        "- Production durable control plane: Python 3.12 asyncio (ADR-016); the checked-in foundation is the production engine seed.",
        "- Web client: React and TypeScript.",
        "- First runners: local process, Docker/OCI and Kubernetes.",
        "- Production reference: on-premises Kubernetes/Helm with external PostgreSQL and S3-compatible object storage; Docker Compose is the development profile.",
        "- Plugin direction: isolated language-neutral runtime with Java, Python and TypeScript SDKs; migration tools preferred over unchanged JAR loading.",
        "- Priority users: AI workflow developers, software engineers and platform engineers.",
        "- Accepted first integrations: HTTP/REST, webhooks, Git, GitHub, PostgreSQL, S3/MinIO, Docker/OCI, Kubernetes, OpenAI-compatible model APIs and MCP.",
        "- Scale profile M: 100,000 executions/day, 1,000 active task runs, 50 task starts/second and 10 million retained execution records.",
        "- Availability and recovery: 99.9% monthly control-plane target; v1 RPO <= 48 hours and RTO <= 8 hours.",
        "- Migration: full side-by-side resources, identity/governance, historical executions, logs, artifacts and audit evidence.",
        "- Compliance: SOC 2 and ISO/IEC 27001 readiness without a certification claim.",
        "- Engineering authority: independent agent quorum for normal merges; named human approval for defined high-risk changes and stable releases.",
        "",
        "All foundational product decisions required to begin M0 are accepted. The decision record is maintained in [`docs/product/decision-register.md`](../docs/product/decision-register.md); [`DECISIONS_NEEDED.md`](../DECISIONS_NEEDED.md) records whether any new product-owner blocker exists.",
        "",
        "## 4. Functional requirements",
        "",
    ]

    for milestone in milestones:
        lines.extend(
            [
                f"### {milestone['id']} — {milestone['title']}",
                "",
                f"Exit condition: {milestone['exit']}",
                "",
            ]
        )
        for epic in epics_by_milestone[milestone["id"]]:
            lines.extend(
                [
                    f"#### {epic['id']} — {epic['title']}",
                    "",
                    epic["goal"],
                    "",
                ]
            )
            for requirement in sorted(funcs_by_epic[epic["id"]], key=lambda item: item["id"]):
                lines.extend(
                    [
                        f"**{requirement['id']} — {requirement['priority']}**",
                        "",
                        requirement["statement"],
                        "",
                        f"_Verification:_ {requirement['verification']}.",
                        f"_Source scope:_ {requirement['source_scope']}.",
                        "",
                    ]
                )

    lines.extend(["## 5. Non-functional requirements", ""])
    nfr_by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for nfr in nonfunctional:
        nfr_by_category[nfr["category"]].append(nfr)
    for category in sorted(nfr_by_category):
        lines.extend([f"### {category.replace('-', ' ').title()}", ""])
        for nfr in sorted(nfr_by_category[category], key=lambda item: item["id"]):
            mapped = ", ".join(f"`{epic_id}`" for epic_id in nfr["epic_ids"])
            lines.extend(
                [
                    f"**{nfr['id']} — {nfr['priority']} — {nfr['title']}**",
                    "",
                    nfr["statement"],
                    "",
                    f"_Target:_ {nfr['target']}",
                    f"_Verification:_ {nfr['verification']}",
                    f"_Mapped epics:_ {mapped}.",
                    "",
                ]
            )

    lines.extend(
        [
            "## 6. Traceability and evidence",
            "",
            "- `requirements/urs.json` is the canonical machine-readable requirement set.",
            "- `requirements/traceability.csv` maps every functional and non-functional requirement to one or more epics.",
            "- `requirements/parity-matrix.csv` records the parity or intentional-difference scope of every epic.",
            "- `backlog/epics.json` and `backlog/epics/*.md` contain implementation issue bodies and definitions of done.",
            "- Requirement status remains **Proposed** until the approved evidence model is satisfied.",
            "",
            "## 7. Change control",
            "",
            "Any change to a Must requirement, compatibility promise, quality target, architecture invariant or licensing decision requires an ADR or product-owner decision, regenerated planning artifacts and updated traceability in the same change set.",
        ]
    )
    return "\n".join(lines)


def render_epic_body(
    epic: dict[str, Any],
    milestone: dict[str, Any],
    functional_by_id: dict[str, dict[str, Any]],
    nfr_by_id: dict[str, dict[str, Any]],
) -> str:
    functional = [functional_by_id[item] for item in epic["requirement_ids"]]
    nonfunctional = [nfr_by_id[item] for item in epic["nfr_ids"]]
    source_scope = (
        functional[0]["source_scope"]
        if functional
        else "AMESH quality and architecture requirement"
    )
    verification = []
    for requirement in functional:
        value = requirement["verification"].rstrip(".")
        if value not in verification:
            verification.append(value)
    for requirement in nonfunctional:
        value = requirement["verification"].rstrip(".")
        if value not in verification:
            verification.append(value)

    lines = [
        f"# {epic['id']} — {epic['title']}",
        "",
        f"- **Milestone:** {milestone['id']} — {milestone['title']}",
        f"- **Priority:** {epic['priority']}",
        f"- **Domain:** `{epic['domain']}`",
        f"- **Primary persona:** {epic['persona']}",
        f"- **Parity scope:** {source_scope}",
        "",
        "## Outcome",
        "",
        epic["goal"],
        "",
        "## In scope",
        "",
    ]
    for requirement in functional:
        lines.append(f"- [ ] **{requirement['id']}** — {requirement['statement']}")
    if not functional:
        lines.append("- [ ] No functional requirement is currently mapped.")

    if epic.get("mvp_progress"):
        lines.extend(["", "## MVP implementation progress", ""])
        lines.extend(f"- {item}" for item in epic["mvp_progress"])

    if epic.get("non_goals"):
        lines.extend(["", "## Explicit non-goals", ""])
        lines.extend(f"- {item}" for item in epic["non_goals"])

    lines.extend(["", "## Non-functional requirements", ""])
    for requirement in nonfunctional:
        lines.append(
            f"- [ ] **{requirement['id']}** — {requirement['statement']} "
            f"Target: {requirement['target']}"
        )
    if not nonfunctional:
        lines.append(
            "- [ ] No epic-specific NFR is mapped yet; general security, maintainability "
            "and test gates still apply."
        )

    lines.extend(["", "## Dependencies", ""])
    if epic.get("dependencies"):
        lines.extend(f"- {item}" for item in epic["dependencies"])
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Architecture impact",
            "",
            f"- Primary bounded area: `{epic['domain']}`.",
            "- Public contracts introduced or changed must be versioned and documented.",
            "- Durable state changes must use the command/event/outbox model.",
            "- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.",
            "",
            "## Verification plan",
            "",
        ]
    )
    if verification:
        lines.extend(f"- {item}." for item in verification)
    else:
        lines.append("- Requirement-specific verification to be defined before implementation.")
    lines.extend(
        [
            "- Add requirement-to-test evidence links before changing any requirement to Verified.",
            "- Add failure, duplicate, restart and authorization scenarios where applicable.",
            "",
            "## Definition of done",
            "",
            "- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.",
            "- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.",
            "- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.",
            "- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.",
            "- [ ] Documentation, examples, migration notes and operational runbooks are updated.",
            "- [ ] Performance and recovery budgets are measured when this epic is on a critical path.",
            "- [ ] `python scripts/validate_backlog.py` passes.",
            "",
            "## Risks and unknowns",
            "",
        ]
    )
    risks = list(epic.get("risks", []))
    if not risks:
        risks = [
            "Compatibility is version-pinned; gaps must remain explicit and release-scoped.",
            "Qualification claims are valid only for the published profile, topology, configuration and evidence set.",
        ]
    lines.extend(f"- {item}" for item in risks)

    functional_ids = ", ".join(epic["requirement_ids"]) or "none"
    nfr_ids = ", ".join(epic["nfr_ids"]) or "none specifically mapped"
    lines.extend(
        [
            "",
            "## Traceability",
            "",
            f"- Functional requirements: {functional_ids}",
            f"- Non-functional requirements: {nfr_ids}",
            f"- Source scope: {source_scope}",
        ]
    )
    return "\n".join(line.rstrip() for line in lines) + "\n"


def main() -> int:
    baseline = load_json("project-baseline.json")
    milestones: list[dict[str, Any]] = load_json("backlog/milestones.json")
    backlog = load_json("backlog/epics.json")
    urs = load_json("requirements/urs.json")
    epics: list[dict[str, Any]] = sorted_epics(backlog["epics"])
    functional: list[dict[str, Any]] = sorted(
        urs["functional_requirements"], key=lambda item: item["id"]
    )
    nonfunctional: list[dict[str, Any]] = sorted(
        urs["nonfunctional_requirements"], key=lambda item: item["id"]
    )
    epic_by_id = {epic["id"]: epic for epic in epics}
    milestone_by_id = milestone_lookup(milestones)
    functional_by_id = {item["id"]: item for item in functional}
    nfr_by_id = {item["id"]: item for item in nonfunctional}

    # Issue bodies are generated from canonical requirement records so prose cannot drift.
    for epic in epics:
        body = render_epic_body(
            epic,
            milestone_by_id[epic["milestone"]],
            functional_by_id,
            nfr_by_id,
        )
        epic["body"] = body
        write_text(epic["body_file"], body)
    backlog["epics"] = epics
    write_text("backlog/epics.json", json.dumps(backlog, indent=2, ensure_ascii=False))

    write_text("requirements/URS.md", render_urs(baseline, urs, milestones, epics))

    urs_rows: list[dict[str, Any]] = []
    for item in functional:
        urs_rows.append(
            {
                "id": item["id"],
                "type": "Functional",
                "priority": item["priority"],
                "status": item["status"],
                "milestone": item["milestone"],
                "wave": item["wave"],
                "epic_ids": item["epic_id"],
                "domain": item["domain"],
                "persona": item["persona"],
                "statement": item["statement"],
                "verification": item["verification"],
                "source_scope": item["source_scope"],
            }
        )
    for item in nonfunctional:
        urs_rows.append(
            {
                "id": item["id"],
                "type": "Non-functional",
                "priority": item["priority"],
                "status": item["status"],
                "milestone": "",
                "wave": "",
                "epic_ids": ";".join(item["epic_ids"]),
                "domain": item["category"],
                "persona": "All users and operators",
                "statement": f"{item['statement']} Target: {item['target']}",
                "verification": item["verification"],
                "source_scope": "AMESH quality attribute",
            }
        )
    write_text(
        "requirements/urs.csv",
        csv_text(
            [
                "id",
                "type",
                "priority",
                "status",
                "milestone",
                "wave",
                "epic_ids",
                "domain",
                "persona",
                "statement",
                "verification",
                "source_scope",
            ],
            urs_rows,
        ),
    )

    trace_rows: list[dict[str, Any]] = []
    for item in functional:
        epic = epic_by_id[item["epic_id"]]
        trace_rows.append(
            {
                "requirement_id": item["id"],
                "requirement_type": "Functional",
                "priority": item["priority"],
                "epic_id": epic["id"],
                "epic_title": epic["title"],
                "milestone": epic["milestone"],
                "wave": epic["wave"],
                "verification": item["verification"],
                "status": item["status"],
            }
        )
    for item in nonfunctional:
        for epic_id in item["epic_ids"]:
            epic = epic_by_id[epic_id]
            trace_rows.append(
                {
                    "requirement_id": item["id"],
                    "requirement_type": "Non-functional",
                    "priority": item["priority"],
                    "epic_id": epic["id"],
                    "epic_title": epic["title"],
                    "milestone": epic["milestone"],
                    "wave": epic["wave"],
                    "verification": item["verification"],
                    "status": item["status"],
                }
            )
    trace_rows.sort(key=lambda row: (row["requirement_id"], row["epic_id"]))
    write_text(
        "requirements/traceability.csv",
        csv_text(
            [
                "requirement_id",
                "requirement_type",
                "priority",
                "epic_id",
                "epic_title",
                "milestone",
                "wave",
                "verification",
                "status",
            ],
            trace_rows,
        ),
    )

    existing_parity: dict[str, dict[str, str]] = {}
    parity_path = ROOT / "requirements/parity-matrix.csv"
    if parity_path.exists():
        with parity_path.open(newline="", encoding="utf-8") as handle:
            existing_parity = {row["epic_id"]: row for row in csv.DictReader(handle)}
    parity_rows: list[dict[str, Any]] = []
    for epic in epics:
        scope, compatibility = parity_scope(epic, existing_parity)
        parity_rows.append(
            {
                "epic_id": epic["id"],
                "capability_area": epic["title"],
                "milestone": epic["milestone"],
                "parity_scope": scope,
                "compatibility_level": compatibility,
                "status": existing_parity.get(epic["id"], {}).get("status", "Planned"),
                "requirement_count": len(epic["requirement_ids"]) + len(epic["nfr_ids"]),
                "evidence": existing_parity.get(epic["id"], {}).get("evidence", ""),
            }
        )
    write_text(
        "requirements/parity-matrix.csv",
        csv_text(
            [
                "epic_id",
                "capability_area",
                "milestone",
                "parity_scope",
                "compatibility_level",
                "status",
                "requirement_count",
                "evidence",
            ],
            parity_rows,
        ),
    )

    backlog_lines = [
        "# Epic backlog",
        "",
        f"This backlog contains {len(epics)} epics and is generated from `backlog/epics.json`.",
        "",
        "| Epic | Milestone | Domain | Requirements | Goal |",
        "|---|---|---|---:|---|",
    ]
    for epic in epics:
        relative_body = Path(epic["body_file"]).relative_to("backlog").as_posix()
        count = len(epic["requirement_ids"]) + len(epic["nfr_ids"])
        goal = epic["goal"].replace("|", "\\|").replace("\n", " ")
        backlog_lines.append(
            f"| [{epic['id']}]({relative_body}) | {epic['milestone']} | {epic['domain']} | {count} | {goal} |"
        )
    write_text("backlog/README.md", "\n".join(backlog_lines))

    issue_lines = []
    for epic in epics:
        issue_lines.append(
            json.dumps(
                {
                    "title": f"{epic['id']}: {epic['title']}",
                    "body": epic["body"],
                    "labels": epic["labels"],
                    "milestone": epic["milestone"],
                },
                ensure_ascii=False,
                sort_keys=False,
            )
        )
    write_text("backlog/github-issues.ndjson", "\n".join(issue_lines))

    roadmap_lines = [
        "# Roadmap",
        "",
        "The roadmap is dependency-oriented rather than calendar-based. AI engineering capacity is elastic, but milestone exits are evidence gates rather than staffing or calendar promises.",
        "",
    ]
    epics_by_milestone: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for epic in epics:
        epics_by_milestone[epic["milestone"]].append(epic)
    for milestone in milestones:
        grouped = epics_by_milestone[milestone["id"]]
        roadmap_lines.extend(
            [
                f"## {milestone['id']} — {milestone['title']}",
                "",
                f"**Exit condition:** {milestone['exit']}",
                "",
                f"**Epic count:** {len(grouped)}",
                "",
            ]
        )
        for epic in grouped:
            roadmap_lines.append(f"- `{epic['id']}` {epic['title']}")
        roadmap_lines.append("")
    write_text("docs/product/roadmap.md", "\n".join(roadmap_lines))

    print(
        "Regenerated planning artifacts: "
        f"{len(epics)} epics, {len(functional)} functional requirements, "
        f"{len(nonfunctional)} non-functional requirements, {len(trace_rows)} trace links."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
