from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.family import infer_family, slugify
from project_os.models import AdapterResult, ProjectEdge, ProjectNode, path_mtime_iso


JSON_PARSE_LIMIT_BYTES = 2_000_000
PREVIEW_LIMIT_CHARS = 8_000


def result(name: str) -> AdapterResult:
    return AdapterResult(name=name)


def node_id(kind: str, family: str, label: str) -> str:
    return f"{kind}:{family or 'unclassified'}:{slugify(label)}"


def family_node(family: str, adapter: str) -> ProjectNode:
    return ProjectNode(
        id=f"family:{family}",
        kind="family",
        label=family.replace("_", " ").title(),
        family=family,
        status="unknown",
        evidence_level="metadata_only",
        source_adapter=adapter,
        confidence="exact",
        summary=f"Strategy or artifact family: {family}",
    )


def contains_family_edge(family: str, node: ProjectNode, reason: str = "family grouping") -> ProjectEdge:
    return ProjectEdge(
        source=f"family:{family}",
        target=node.id,
        relation="contains",
        evidence_level=node.evidence_level,
        confidence=node.confidence,
        reason=reason,
    )


def safe_read_text(path: Path, limit: int = PREVIEW_LIMIT_CHARS) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return text[:limit]


def safe_load_json(path: Path, max_bytes: int = JSON_PARSE_LIMIT_BYTES) -> tuple[dict[str, Any] | list[Any] | None, str]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        return None, f"stat failed: {exc}"
    if size > max_bytes:
        return None, f"json too large for full parse ({size:,} bytes)"
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore") or "{}"), ""
    except Exception as exc:
        return None, f"malformed json: {exc}"


def folder_stats(path: Path) -> dict[str, Any]:
    total = 0
    count = 0
    newest = 0.0
    newest_path = ""
    for dirpath, _dirnames, filenames in os.walk(path, topdown=True):
        for filename in filenames:
            full = Path(dirpath) / filename
            try:
                stat = full.stat()
            except OSError:
                continue
            count += 1
            total += int(stat.st_size)
            if stat.st_mtime > newest:
                newest = stat.st_mtime
                newest_path = str(full)
    updated = path_mtime_iso(Path(newest_path)) if newest_path else path_mtime_iso(path)
    return {"files": count, "size_bytes": total, "updated_at_utc": updated, "newest_path": newest_path}


def health_issue(adapter: str, family: str, label: str, summary: str, path: Path | None = None) -> ProjectNode:
    issue_id = node_id("health_issue", family or "unclassified", f"{adapter}:{label}")
    return ProjectNode(
        id=issue_id,
        kind="health_issue",
        label=label,
        family=family or "unclassified",
        status="health_issue",
        evidence_level="metadata_only",
        path=str(path) if path else None,
        updated_at_utc=path_mtime_iso(path) if path else None,
        summary=summary,
        source_adapter=adapter,
        confidence="exact",
    )


def apply_node_overrides(node: ProjectNode, overrides: Overrides) -> ProjectNode:
    node.family = overrides.family_for(node.family, node.label)
    if node.id in overrides.status_overrides:
        node.status = overrides.status_overrides[node.id]
    for key, value in overrides.node_overrides(node.id).items():
        if hasattr(node, key):
            setattr(node, key, value)
    if node.id in set(overrides.pinned) and "pinned" not in node.tags:
        node.tags.append("pinned")
    return node


def infer_family_from_path(path: Path, *extra: Any) -> str:
    return infer_family(path.name, path.parent.name, str(path), *extra)


def file_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None
