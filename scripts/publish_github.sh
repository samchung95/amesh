#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OWNER="${GITHUB_OWNER:-samchung95}"
REPO="${GITHUB_REPO:-amesh}"
VISIBILITY="${GITHUB_VISIBILITY:-private}"
FULL="$OWNER/$REPO"

case "$VISIBILITY" in
  private|public|internal) ;;
  *) echo "GITHUB_VISIBILITY must be private, public, or internal" >&2; exit 2 ;;
esac

command -v gh >/dev/null || { echo "GitHub CLI (gh) is required." >&2; exit 2; }
gh auth status

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing to publish a dirty worktree. Review and commit changes first." >&2
  git status --short
  exit 2
fi

if [[ "${CONFIRM_PUBLISH:-}" != "$FULL" ]]; then
  cat >&2 <<EOF
Publication guard not satisfied.
Review repository, name, license, visibility and clean-room policy, then run:

  export CONFIRM_PUBLISH="$FULL"
  export GITHUB_OWNER="$OWNER"
  export GITHUB_REPO="$REPO"
  export GITHUB_VISIBILITY="$VISIBILITY"
  bash scripts/publish_github.sh
EOF
  exit 2
fi

if gh repo view "$FULL" >/dev/null 2>&1; then
  echo "Repository $FULL already exists; it will not be recreated."
else
  gh repo create "$FULL" "--$VISIBILITY" \
    --description "AMESH: fully open-source durable workflow and agent-mesh orchestration" \
    --source . \
    --remote origin
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/$FULL.git"
fi

git push --set-upstream origin main
echo "Published $FULL."
