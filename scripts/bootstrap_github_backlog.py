#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        list(args),
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout if capture else ""


def gh_json(*args: str) -> Any:
    output = run("gh", *args, capture=True)
    return json.loads(output or "null")


def resolve_repo(explicit: str | None) -> str:
    if explicit:
        return explicit
    environment = os.getenv("GITHUB_REPOSITORY")
    if environment:
        return environment
    data = gh_json("repo", "view", "--json", "nameWithOwner")
    return str(data["nameWithOwner"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="owner/name; defaults to current gh repository")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="create at most N missing issues")
    args = parser.parse_args()

    repo = resolve_repo(args.repo)
    backlog = json.loads((ROOT / "backlog" / "epics.json").read_text(encoding="utf-8"))
    labels = json.loads((ROOT / "backlog" / "labels.json").read_text(encoding="utf-8"))
    milestones = json.loads((ROOT / "backlog" / "milestones.json").read_text(encoding="utf-8"))

    print(f"Target repository: {repo}")
    if args.dry_run:
        print(f"Would upsert {len(labels)} labels, {len(milestones)} milestones and {len(backlog['epics'])} epic issues.")
        return 0

    run("gh", "auth", "status")

    for label in labels:
        run(
            "gh", "label", "create", label["name"],
            "--repo", repo,
            "--color", label["color"],
            "--description", label["description"],
            "--force",
        )

    existing_milestones = gh_json(
        "api", f"repos/{repo}/milestones?state=all&per_page=100",
    )
    milestone_by_title = {item["title"]: item for item in existing_milestones}
    for milestone in milestones:
        title = f"{milestone['id']} — {milestone['title']}"
        if title not in milestone_by_title:
            created = gh_json(
                "api", "--method", "POST", f"repos/{repo}/milestones",
                "-f", f"title={title}",
                "-f", f"description={milestone['exit']}",
            )
            milestone_by_title[title] = created

    existing_issues = gh_json(
        "issue", "list", "--repo", repo, "--state", "all",
        "--limit", "1000", "--json", "number,title",
    )
    existing_titles = {item["title"] for item in existing_issues}

    created_count = 0
    for epic in backlog["epics"]:
        title = f"{epic['id']}: {epic['title']}"
        if title in existing_titles:
            print(f"exists: {title}")
            continue
        if args.limit and created_count >= args.limit:
            break
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            handle.write(epic["body"])
            body_file = handle.name
        try:
            command = [
                "gh", "issue", "create",
                "--repo", repo,
                "--title", title,
                "--body-file", body_file,
                "--milestone", f"{epic['milestone']} — {next(m['title'] for m in milestones if m['id'] == epic['milestone'])}",
            ]
            for label in epic["labels"]:
                command.extend(["--label", label])
            run(*command)
            created_count += 1
        finally:
            Path(body_file).unlink(missing_ok=True)

    print(f"Created {created_count} issues; existing issues were left unchanged.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"GitHub command failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
