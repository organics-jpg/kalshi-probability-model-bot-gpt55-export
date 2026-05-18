#!/usr/bin/env python3
"""Build a sanitized GitHub export for the Kalshi research workspace.

The source workspace is intentionally not a git repository. This script creates
a separate publish tree that keeps code, Research OS, logs, stats, datasets, and
artifacts while excluding obvious secret material and making large text artifacts
GitHub-safe through gzip compression and Git LFS metadata.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import sys
import time
import zipfile
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


EXPORT_MARKER = ".codex_kalshi_github_export"
CHUNK_SIZE = 1024 * 1024

EXCLUDE_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    ".idea",
    ".vscode",
}

SECRET_DIR_NAMES = {
    "secret",
    "secrets",
    ".secrets",
}

BROWSER_PROFILE_MARKERS = {
    "chrome_living_dashboard_profile",
    "chrome_living_dashboard_profile_1280",
    "chrome_living_dashboard_profile_1536b",
    "chrome_living_dashboard_profile_1536c",
    "chrome_reference_art_profile",
}

SECRET_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "cookies",
    "credentials.json",
    "history",
    "login data",
    "service_account.json",
    "service-account.json",
    "web data",
}

SECRET_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".p8",
}

TEXT_SUFFIXES = {
    ".bat",
    ".cmd",
    ".conf",
    ".csv",
    ".css",
    ".html",
    ".ini",
    ".ipynb",
    ".js",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".ndjson",
    ".ps1",
    ".py",
    ".rst",
    ".sql",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}

SECRET_BYTE_PATTERNS: list[tuple[str, re.Pattern[bytes]]] = [
    (
        "private_key_block",
        re.compile(rb"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    ),
    (
        "openai_or_similar_secret_key",
        re.compile(rb"\bsk-[A-Za-z0-9_\-]{24,}\b"),
    ),
    (
        "github_token",
        re.compile(rb"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{30,}\b"),
    ),
    (
        "github_fine_grained_token",
        re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{50,}\b"),
    ),
    (
        "aws_access_key",
        re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    ),
]


@dataclass
class ExportStats:
    copied: int = 0
    compressed: int = 0
    split_artifacts: int = 0
    excluded: int = 0
    lfs_files: int = 0
    original_bytes_included: int = 0
    export_bytes_written: int = 0
    files: list[dict] = field(default_factory=list)
    exclusions: list[dict] = field(default_factory=list)
    large_artifacts: list[dict] = field(default_factory=list)
    lfs_paths: list[str] = field(default_factory=list)


class SecretScanner:
    def __init__(self) -> None:
        self._carry = b""

    def update(self, chunk: bytes) -> str | None:
        haystack = self._carry + chunk
        for reason, pattern in SECRET_BYTE_PATTERNS:
            if pattern.search(haystack):
                return reason
        self._carry = haystack[-4096:]
        return None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel_posix(path: Path) -> str:
    return path.as_posix()


def is_text_like(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def should_exclude_path(rel: Path) -> str | None:
    parts_lower = [part.lower() for part in rel.parts]
    for part in parts_lower[:-1]:
        if part in EXCLUDE_DIR_NAMES:
            return f"excluded directory: {part}"
        if part in SECRET_DIR_NAMES:
            return f"secret directory: {part}"
        if part in BROWSER_PROFILE_MARKERS or ("chrome" in part and "profile" in part):
            return f"browser profile directory: {part}"

    name_lower = rel.name.lower()
    if name_lower in SECRET_FILE_NAMES:
        return f"secret filename: {rel.name}"
    if name_lower.startswith(".env."):
        return f"secret env filename: {rel.name}"
    if rel.suffix.lower() in SECRET_SUFFIXES:
        return f"secret suffix: {rel.suffix}"
    return None


def ensure_clean_dest(dest: Path, clean: bool) -> None:
    if dest.exists():
        marker = dest / EXPORT_MARKER
        if not clean:
            raise SystemExit(
                f"Destination already exists: {dest}\n"
                "Rerun with --clean after confirming it is the export tree."
            )
        if not marker.exists():
            raise SystemExit(
                f"Refusing to clean destination without marker {EXPORT_MARKER}: {dest}"
            )
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / EXPORT_MARKER).write_text(utc_now() + "\n", encoding="utf-8")


def iter_files(source: Path, dest: Path) -> Iterable[Path]:
    source_resolved = source.resolve()
    dest_resolved = dest.resolve()
    for root, dirs, files in os.walk(source):
        root_path = Path(root)
        try:
            root_resolved = root_path.resolve()
        except OSError:
            continue

        if root_resolved == dest_resolved or dest_resolved in root_resolved.parents:
            dirs[:] = []
            continue

        kept_dirs = []
        for dirname in dirs:
            dir_path = root_path / dirname
            try:
                rel = dir_path.relative_to(source_resolved)
            except ValueError:
                continue
            reason = should_exclude_path(rel / "placeholder")
            if reason:
                continue
            kept_dirs.append(dirname)
        dirs[:] = kept_dirs

        for filename in files:
            path = root_path / filename
            try:
                path.relative_to(source_resolved)
            except ValueError:
                continue
            yield path


def clip_preview_line(line: str) -> str:
    clipped = line.rstrip("\n\r")
    if len(clipped) > 500:
        clipped = clipped[:500] + " ... [truncated]"
    return clipped


def read_head_tail(path: Path, lines: int = 20, bytes_to_read: int = 256 * 1024) -> tuple[list[str], list[str]]:
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            head_bytes = handle.read(bytes_to_read)
            handle.seek(max(0, size - bytes_to_read))
            tail_bytes = handle.read(bytes_to_read)
    except OSError:
        return [], []

    head_text = head_bytes.decode("utf-8", errors="replace").splitlines()
    tail_text = tail_bytes.decode("utf-8", errors="replace").splitlines()
    head = [clip_preview_line(line) for line in head_text[:lines]]
    tail = [clip_preview_line(line) for line in tail_text[-lines:]]
    return head, tail


def write_sample(
    sample_root: Path,
    rel: Path,
    original_size: int,
    original_sha256: str,
    line_count: int | None,
    compressed_rel: str,
    source: Path,
) -> str:
    digest = hashlib.sha1(rel_posix(rel).encode("utf-8")).hexdigest()[:16]
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", rel.name)[:90]
    sample_rel = Path("artifact_samples") / f"{digest}_{safe_name}.sample.md"
    sample_path = sample_root / sample_rel
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    head, tail = read_head_tail(source)
    lines = [
        "# Large Artifact Sample",
        "",
        f"- Source path: `{rel_posix(rel)}`",
        f"- Export artifact: `{compressed_rel}`",
        f"- Original bytes: `{original_size}`",
        f"- Original sha256: `{original_sha256}`",
    ]
    if line_count is not None:
        lines.append(f"- Approximate newline count: `{line_count}`")
    lines.extend(["", "## First Lines", ""])
    if head:
        lines.extend([f"    {item}" for item in head])
    else:
        lines.append("_No UTF-8 text preview available._")
    lines.extend(["", "## Last Lines", ""])
    if tail:
        lines.extend([f"    {item}" for item in tail])
    else:
        lines.append("_No UTF-8 text preview available._")
    sample_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel_posix(sample_rel)


def split_large_file(path: Path, chunk_bytes: int) -> list[Path]:
    part_paths: list[Path] = []
    part_index = 0
    with path.open("rb") as src:
        while True:
            chunk = src.read(chunk_bytes)
            if not chunk:
                break
            part_path = path.with_name(f"{path.name}.part{part_index:03d}")
            with part_path.open("wb") as out:
                out.write(chunk)
            part_paths.append(part_path)
            part_index += 1
    path.unlink()
    return part_paths


def scan_zip_for_secret_markers(path: Path) -> str | None:
    try:
        with zipfile.ZipFile(path) as zf:
            for member in zf.infolist():
                member_rel = Path(member.filename)
                reason = should_exclude_path(member_rel)
                if reason:
                    return f"zip member {member.filename}: {reason}"
                if member.file_size > 10 * 1024 * 1024:
                    continue
                if member.is_dir():
                    continue
                scanner = SecretScanner()
                with zf.open(member, "r") as handle:
                    while True:
                        chunk = handle.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        secret_reason = scanner.update(chunk)
                        if secret_reason:
                            return f"zip member {member.filename}: {secret_reason}"
    except zipfile.BadZipFile:
        return None
    except OSError as exc:
        return f"zip scan error: {exc}"
    return None


def copy_or_compress_file(
    source_file: Path,
    rel: Path,
    dest_root: Path,
    stats: ExportStats,
    large_threshold: int,
    lfs_threshold: int,
    split_threshold: int,
    split_chunk: int,
    gzip_compresslevel: int,
) -> None:
    stat = source_file.stat()
    original_size = stat.st_size
    text_like = is_text_like(source_file)
    compress = original_size >= large_threshold and text_like
    dest_rel = Path(rel_posix(rel) + ".gz") if compress else rel
    dest_path = dest_root / dest_rel
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if source_file.suffix.lower() == ".zip":
        zip_reason = scan_zip_for_secret_markers(source_file)
        if zip_reason:
            stats.excluded += 1
            stats.exclusions.append(
                {
                    "path": rel_posix(rel),
                    "reason": zip_reason,
                    "bytes": original_size,
                }
            )
            return

    scanner = SecretScanner()
    hasher = hashlib.sha256()
    written = 0
    newline_count = 0 if text_like else None
    secret_reason: str | None = None
    processed = 0
    last_report = 0
    report_interval = 512 * 1024 * 1024

    try:
        if compress:
            print(
                f"  compressing large artifact {rel_posix(rel)} "
                f"({original_size / (1024 ** 3):.2f} GB raw)",
                flush=True,
            )
            with source_file.open("rb") as src, gzip.open(dest_path, "wb", compresslevel=gzip_compresslevel) as out:
                while True:
                    chunk = src.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    processed += len(chunk)
                    hasher.update(chunk)
                    if newline_count is not None:
                        newline_count += chunk.count(b"\n")
                    secret_reason = scanner.update(chunk)
                    if secret_reason:
                        break
                    out.write(chunk)
                    if processed - last_report >= report_interval:
                        last_report = processed
                        print(
                            f"    {rel_posix(rel)}: {processed / (1024 ** 3):.2f}/"
                            f"{original_size / (1024 ** 3):.2f} GB",
                            flush=True,
                        )
        else:
            with source_file.open("rb") as src, dest_path.open("wb") as out:
                while True:
                    chunk = src.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    processed += len(chunk)
                    hasher.update(chunk)
                    secret_reason = scanner.update(chunk)
                    if secret_reason:
                        break
                    out.write(chunk)
                    written += len(chunk)
                    if original_size >= report_interval and processed - last_report >= report_interval:
                        last_report = processed
                        print(
                            f"    {rel_posix(rel)}: {processed / (1024 ** 3):.2f}/"
                            f"{original_size / (1024 ** 3):.2f} GB",
                            flush=True,
                        )
            shutil.copystat(source_file, dest_path)
    except OSError as exc:
        stats.excluded += 1
        stats.exclusions.append(
            {
                "path": rel_posix(rel),
                "reason": f"read/write error: {exc}",
                "bytes": original_size,
            }
        )
        if dest_path.exists():
            dest_path.unlink()
        return

    if secret_reason:
        stats.excluded += 1
        stats.exclusions.append(
            {
                "path": rel_posix(rel),
                "reason": f"secret pattern: {secret_reason}",
                "bytes": original_size,
            }
        )
        if dest_path.exists():
            dest_path.unlink()
        return

    original_sha256 = hasher.hexdigest()
    output_paths: list[Path]
    if compress and dest_path.stat().st_size > split_threshold:
        output_paths = split_large_file(dest_path, split_chunk)
        stats.split_artifacts += 1
    else:
        output_paths = [dest_path]

    output_rels = [rel_posix(path.relative_to(dest_root)) for path in output_paths]
    output_bytes = sum(path.stat().st_size for path in output_paths)
    stats.original_bytes_included += original_size
    stats.export_bytes_written += output_bytes

    if compress:
        stats.compressed += 1
        sample_rel = write_sample(
            dest_root,
            rel,
            original_size,
            original_sha256,
            newline_count,
            output_rels[0] if len(output_rels) == 1 else " + ".join(output_rels),
            source_file,
        )
        artifact = {
            "source_path": rel_posix(rel),
            "export_paths": output_rels,
            "sample_path": sample_rel,
            "original_bytes": original_size,
            "export_bytes": output_bytes,
            "original_sha256": original_sha256,
            "newline_count": newline_count,
            "compression": "gzip",
            "split": len(output_paths) > 1,
        }
        stats.large_artifacts.append(artifact)
        stats.files.append({**artifact, "mode": "compressed"})
    else:
        stats.copied += 1
        stats.files.append(
            {
                "source_path": rel_posix(rel),
                "export_paths": output_rels,
                "original_bytes": original_size,
                "export_bytes": output_bytes,
                "original_sha256": original_sha256,
                "mode": "copied",
            }
        )

    for out_path in output_paths:
        out_size = out_path.stat().st_size
        if out_size >= lfs_threshold:
            lfs_rel = rel_posix(out_path.relative_to(dest_root))
            stats.lfs_paths.append(lfs_rel)


def write_gitattributes(dest: Path, lfs_paths: list[str]) -> None:
    lines = [
        "# Generated by scripts/build_github_export.py",
        "# Large artifacts are tracked through Git LFS when they exceed the configured threshold.",
    ]
    for path in sorted(set(lfs_paths)):
        lines.append(f"{path} filter=lfs diff=lfs merge=lfs -text")
    (dest / ".gitattributes").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_export_docs(dest: Path, source: Path, stats: ExportStats, started: float) -> None:
    finished_at = utc_now()
    duration = round(time.time() - started, 1)
    manifest = {
        "generated_at": finished_at,
        "source_root": str(source.resolve()),
        "export_root": str(dest.resolve()),
        "policy": {
            "secret_exclusions": {
                "directory_names": sorted(SECRET_DIR_NAMES),
                "file_names": sorted(SECRET_FILE_NAMES),
                "suffixes": sorted(SECRET_SUFFIXES),
                "byte_patterns": [name for name, _ in SECRET_BYTE_PATTERNS],
            },
            "excluded_runtime_dirs": sorted(EXCLUDE_DIR_NAMES),
            "large_text_artifacts": "gzip compressed when over threshold",
            "lfs": "files over threshold are listed in .gitattributes",
        },
        "summary": {
            "copied_files": stats.copied,
            "compressed_files": stats.compressed,
            "split_artifacts": stats.split_artifacts,
            "excluded_files": stats.excluded,
            "lfs_files": len(set(stats.lfs_paths)),
            "original_bytes_included": stats.original_bytes_included,
            "export_bytes_written": stats.export_bytes_written,
            "duration_seconds": duration,
        },
        "large_artifacts": stats.large_artifacts,
        "excluded_files": stats.exclusions,
        "files": stats.files,
    }
    (dest / "EXPORT_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    md = [
        "# Export Manifest",
        "",
        f"- Generated at: `{finished_at}`",
        f"- Source root: `{source.resolve()}`",
        f"- Export root: `{dest.resolve()}`",
        f"- Duration seconds: `{duration}`",
        f"- Copied files: `{stats.copied}`",
        f"- Compressed large text files: `{stats.compressed}`",
        f"- Split artifacts: `{stats.split_artifacts}`",
        f"- Excluded files: `{stats.excluded}`",
        f"- Git LFS paths: `{len(set(stats.lfs_paths))}`",
        f"- Original included bytes: `{stats.original_bytes_included}`",
        f"- Export bytes written: `{stats.export_bytes_written}`",
        "",
        "## Secret Policy",
        "",
        "The export excludes `.env` files, `secrets/` directories, private-key suffixes, and files containing high-confidence secret token/private-key byte patterns. Excluded paths are listed by path and reason only; secret values are never written to this manifest.",
        "",
        "## Large Artifacts",
        "",
        "Large text logs and datasets are gzip-compressed. For each compressed artifact, `artifact_samples/` contains a source path, hash, byte counts, and first/last line samples. Reconstruct raw files with `python scripts/restore_compressed_artifacts.py --manifest EXPORT_MANIFEST.json --dest restored_raw`.",
        "",
    ]
    for artifact in stats.large_artifacts[:200]:
        md.append(
            f"- `{artifact['source_path']}` -> `{', '.join(artifact['export_paths'])}` "
            f"({artifact['original_bytes']} bytes raw, {artifact['export_bytes']} bytes exported)"
        )
    if len(stats.large_artifacts) > 200:
        md.append(f"- ... plus {len(stats.large_artifacts) - 200} more; see `EXPORT_MANIFEST.json`.")
    md.extend(["", "## Exclusions", ""])
    if stats.exclusions:
        for exclusion in stats.exclusions[:300]:
            md.append(f"- `{exclusion['path']}`: {exclusion['reason']} ({exclusion['bytes']} bytes)")
        if len(stats.exclusions) > 300:
            md.append(f"- ... plus {len(stats.exclusions) - 300} more; see `EXPORT_MANIFEST.json`.")
    else:
        md.append("- No files were excluded after policy scanning.")
    (dest / "EXPORT_MANIFEST.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    secret_report = [
        "# Secret Exclusion Report",
        "",
        "No secret values are printed here. This report only records excluded paths and high-level reasons.",
        "",
    ]
    if stats.exclusions:
        for exclusion in stats.exclusions:
            secret_report.append(
                f"- `{exclusion['path']}`: {exclusion['reason']} ({exclusion['bytes']} bytes)"
            )
    else:
        secret_report.append("- No secret-pattern exclusions were triggered.")
    (dest / "SECRET_EXCLUSION_REPORT.md").write_text(
        "\n".join(secret_report) + "\n",
        encoding="utf-8",
    )


RESTORE_SCRIPT = r'''#!/usr/bin/env python3
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
'''


def write_restore_script(dest: Path) -> None:
    scripts = dest / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "restore_compressed_artifacts.py").write_text(RESTORE_SCRIPT, encoding="utf-8")


def build_export(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    dest = Path(args.dest).resolve()
    large_threshold = int(args.large_threshold_mb * 1024 * 1024)
    lfs_threshold = int(args.lfs_threshold_mb * 1024 * 1024)
    split_threshold = int(args.split_threshold_mb * 1024 * 1024)
    split_chunk = int(args.split_chunk_mb * 1024 * 1024)
    ensure_clean_dest(dest, clean=args.clean)
    stats = ExportStats()
    started = time.time()

    files = list(iter_files(source, dest))
    total = len(files)
    print(f"Exporting {total} files from {source} to {dest}", flush=True)
    for index, source_file in enumerate(files, start=1):
        rel = source_file.relative_to(source)
        reason = should_exclude_path(rel)
        if reason:
            size = source_file.stat().st_size
            stats.excluded += 1
            stats.exclusions.append(
                {"path": rel_posix(rel), "reason": reason, "bytes": size}
            )
            continue
        if index == 1 or index % 250 == 0:
            print(
                f"[{index}/{total}] copied={stats.copied} compressed={stats.compressed} "
                f"excluded={stats.excluded} path={rel_posix(rel)}",
                flush=True,
            )
        copy_or_compress_file(
            source_file,
            rel,
            dest,
            stats,
            large_threshold,
            lfs_threshold,
            split_threshold,
            split_chunk,
            args.gzip_compresslevel,
        )

    write_restore_script(dest)
    write_gitattributes(dest, stats.lfs_paths)
    write_export_docs(dest, source, stats, started)
    print(
        f"Done: copied={stats.copied} compressed={stats.compressed} "
        f"excluded={stats.excluded} lfs={len(set(stats.lfs_paths))} "
        f"export_gb={stats.export_bytes_written / (1024 ** 3):.2f}",
        flush=True,
    )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=".", help="Source workspace root")
    parser.add_argument("--dest", required=True, help="Destination export directory")
    parser.add_argument("--clean", action="store_true", help="Clean an existing marked export directory")
    parser.add_argument("--large-threshold-mb", type=float, default=25.0)
    parser.add_argument("--lfs-threshold-mb", type=float, default=50.0)
    parser.add_argument("--split-threshold-mb", type=float, default=1900.0)
    parser.add_argument("--split-chunk-mb", type=float, default=512.0)
    parser.add_argument("--gzip-compresslevel", type=int, default=1)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    return build_export(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
