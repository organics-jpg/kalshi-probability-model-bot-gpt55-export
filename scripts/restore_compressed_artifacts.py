#!/usr/bin/env python3
"""Restore compressed artifacts from EXPORT_MANIFEST.json."""

from __future__ import annotations

import argparse
import gzip
import json
import shutil
from pathlib import Path


def restore(manifest_path: Path, dest: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent
    dest.mkdir(parents=True, exist_ok=True)
    for artifact in manifest.get("large_artifacts", []):
        source_rel = Path(artifact["source_path"])
        out_path = dest / source_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        export_paths = [root / rel for rel in artifact["export_paths"]]
        if artifact.get("split"):
            tmp_gz = out_path.with_suffix(out_path.suffix + ".gz")
            with tmp_gz.open("wb") as combined:
                for part in export_paths:
                    with part.open("rb") as handle:
                        shutil.copyfileobj(handle, combined)
            gz_path = tmp_gz
        else:
            gz_path = export_paths[0]
        with gzip.open(gz_path, "rb") as src, out_path.open("wb") as out:
            shutil.copyfileobj(src, out)
        if artifact.get("split"):
            tmp_gz.unlink()
        print(f"restored {artifact['source_path']} -> {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="EXPORT_MANIFEST.json")
    parser.add_argument("--dest", default="restored_raw")
    args = parser.parse_args()
    restore(Path(args.manifest), Path(args.dest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
