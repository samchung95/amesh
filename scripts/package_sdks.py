#!/usr/bin/env python3
"""Create deterministic release archives for the generated API clients."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SDK_ROOT = ROOT / "sdks" / "api"
FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def deterministic_zip(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            info = ZipInfo(path.relative_to(source).as_posix(), FIXED_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def package_sdks(output_dir: Path) -> tuple[Path, ...]:
    manifest = json.loads((SDK_ROOT / "manifest.json").read_text(encoding="utf-8"))
    version = str(manifest["apiVersion"])
    archives: list[Path] = []
    for client in manifest["clients"]:
        language = str(client["language"])
        archive = output_dir / f"amesh-client-{language}-{version}.zip"
        deterministic_zip(SDK_ROOT / str(client["path"]), archive)
        archives.append(archive)
    checksums = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in archives
    )
    checksum_path = output_dir / "amesh-clients.sha256"
    checksum_path.write_text(checksums, encoding="utf-8", newline="\n")
    return (*archives, checksum_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "sdk")
    args = parser.parse_args()
    created = package_sdks(args.output_dir)
    print(f"packaged {len(created) - 1} SDKs and checksums in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
