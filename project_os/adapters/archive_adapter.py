from __future__ import annotations

from pathlib import Path

from project_os.curation import Overrides
from project_os.family import infer_family
from project_os.models import AdapterResult, ProjectNode

from .base import apply_node_overrides, contains_family_edge, family_node, folder_stats, node_id, result


ARCHIVE_DIRS = ("trial_archives", "handoff_gpt55_v28_live_context_20260501")


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "archive_adapter"
    out = result(adapter)
    count = 0
    for name in ARCHIVE_DIRS:
        archive_path = root / name
        if not archive_path.exists():
            continue
        count += 1
        stats = folder_stats(archive_path) if archive_path.is_dir() else {"files": 1, "size_bytes": archive_path.stat().st_size, "updated_at_utc": None}
        family = infer_family(name)
        node = ProjectNode(
            id=node_id("archive", family, name),
            kind="archive",
            label=name,
            family=family,
            status="archived",
            evidence_level="metadata_only",
            path=str(archive_path),
            updated_at_utc=stats.get("updated_at_utc"),
            size_bytes=stats.get("size_bytes"),
            metrics={"files": stats.get("files", 0), "size_mb": round(float(stats.get("size_bytes", 0)) / 1_048_576, 2)},
            tags=["archive"],
            source_adapter=adapter,
            confidence="exact",
            summary=f"Archive/handoff artifact with {stats.get('files', 0):,} files.",
        )
        out.nodes.extend([family_node(family, adapter), apply_node_overrides(node, overrides)])
        out.edges.append(contains_family_edge(family, node, "archive grouped by inferred family"))
    out.summary = {"archives": count}
    return out
