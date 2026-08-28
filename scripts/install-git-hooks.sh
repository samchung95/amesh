#!/bin/sh
set -eu

repository_root="$(git rev-parse --show-toplevel)"
cd "$repository_root"

if [ ! -f .githooks/pre-push ]; then
  printf '%s\n' 'AMESH hook installer: .githooks/pre-push is missing.' >&2
  exit 1
fi

current_hooks_path="$(git config --local --get core.hooksPath || true)"
if [ -n "$current_hooks_path" ] && [ "$current_hooks_path" != '.githooks' ]; then
  printf '%s\n' \
    "AMESH hook installer: core.hooksPath is already '$current_hooks_path'; refusing to replace it." \
    >&2
  exit 1
fi

git config --local core.hooksPath .githooks

configured_hooks_path="$(git config --local --get core.hooksPath)"
if [ "$configured_hooks_path" != '.githooks' ]; then
  printf '%s\n' 'AMESH hook installer: core.hooksPath verification failed.' >&2
  exit 1
fi

printf '%s\n' \
  'AMESH hook installer: enabled .githooks/pre-push for this clone.' \
  'Ordinary git push commands now run the complete Docker-local gate.'
