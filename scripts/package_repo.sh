#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="${PACKAGE_NAME:-amesh}"
OUT_DIR="${OUT_DIR:-$(dirname "$ROOT")}"
ZIP="$OUT_DIR/$NAME.zip"
TAR="$OUT_DIR/$NAME.tar.gz"
CHECKSUMS="$OUT_DIR/$NAME.sha256"
BUNDLE="$OUT_DIR/$NAME.bundle"

python "$ROOT/scripts/validate_backlog.py"
python "$ROOT/scripts/check_clean_room.py"
uvx --from 'reuse[charset-normalizer]==6.2.0' reuse lint

rm -f "$ZIP" "$TAR" "$BUNDLE" "$CHECKSUMS"

python - "$ROOT" "$ZIP" "$TAR" <<'PY'
from __future__ import annotations

import os
import sys
import tarfile
import zipfile
from pathlib import Path

root = Path(sys.argv[1])
zip_path = Path(sys.argv[2])
tar_path = Path(sys.argv[3])
excluded_parts = {
    ".agent-hotel",
    ".artifacts",
    ".claude",
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "node_modules",
}
excluded_names = {".env", ".coverage"}

files = [
    path for path in root.rglob("*")
    if path.is_file()
    and not excluded_parts.intersection(path.relative_to(root).parts)
    and path.name not in excluded_names
]
files.sort(key=lambda item: item.as_posix())

with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files:
        archive.write(path, Path(root.name) / path.relative_to(root))

with tarfile.open(tar_path, "w:gz", compresslevel=9) as archive:
    for path in files:
        info = archive.gettarinfo(str(path), arcname=str(Path(root.name) / path.relative_to(root)))
        info.mtime = 0
        with path.open("rb") as handle:
            archive.addfile(info, handle)
PY

if [[ -d "$ROOT/.git" ]] && [[ -z "$(git -C "$ROOT" status --porcelain)" ]]; then
  git -C "$ROOT" bundle create "$BUNDLE" --all
elif [[ -d "$ROOT/.git" ]]; then
  echo "Skipping Git bundle because the working tree has uncommitted changes." >&2
fi

(
  cd "$OUT_DIR"
  if [[ -f "$BUNDLE" ]]; then
    sha256sum "$(basename "$ZIP")" "$(basename "$TAR")" "$(basename "$BUNDLE")" > "$CHECKSUMS"
  else
    sha256sum "$(basename "$ZIP")" "$(basename "$TAR")" > "$CHECKSUMS"
  fi
)

printf 'Created:\n%s\n%s\n' "$ZIP" "$TAR"
if [[ -f "$BUNDLE" ]]; then printf '%s\n' "$BUNDLE"; fi
printf '%s\n' "$CHECKSUMS"
