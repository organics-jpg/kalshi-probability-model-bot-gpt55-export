from __future__ import annotations

from pathlib import Path

from project_os.curation import Overrides
from project_os.family import infer_family
from project_os.models import AdapterResult, ProjectNode

from .base import apply_node_overrides, contains_family_edge, family_node, folder_stats, health_issue, node_id, result


LARGE_LOG_FOLDER_BYTES = 500 * 1024 * 1024


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "logs_adapter"
    out = result(adapter)
    logs_root = root / "logs"
    if not logs_root.exists():
        out.issues.append(health_issue(adapter, "unclassified", "logs folder missing", "logs/ does not exist", logs_root))
        return out

    folder_count = 0
    for child in sorted((p for p in logs_root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        if child.name == "project_os":
            continue
        folder_count += 1
        stats = folder_stats(child)
        size_bytes = int(stats.get("size_bytes", 0) or 0)
        size_mb = round(float(size_bytes) / 1_048_576, 2)
        size_gb = round(float(size_bytes) / 1_073_741_824, 2)
        is_large_folder = size_bytes >= LARGE_LOG_FOLDER_BYTES
        family = infer_family(child.name, stats.get("newest_path"))
        bot_log = child / "bot.log"
        events = child / "execution_events.ndjson"
        monitor = child / "hourly_monitor.log"
        status = "active" if child.name.startswith("live_") else "diagnostic_only"
        if "archive" in child.name.lower() or "chrome" in child.name.lower():
            status = "archived"
        tags = ["logs"]
        if bot_log.exists():
            tags.append("bot_log")
        if events.exists():
            tags.append("execution_events")
        if monitor.exists():
            tags.append("monitor")
        if is_large_folder:
            tags.extend(["large_folder", "metadata_only_large"])
        summary = f"Log folder with {stats.get('files', 0):,} files. bot.log={bot_log.exists()}, execution_events.ndjson={events.exists()}, hourly_monitor.log={monitor.exists()}."
        if is_large_folder:
            summary += f" Large folder ({size_gb} GB); Research OS indexes metadata only."
        node = ProjectNode(
            id=node_id("log", family, child.name),
            kind="log",
            label=child.name,
            family=family,
            status=status,
            evidence_level="live_stats" if child.name.startswith("live_") else "diagnostic",
            path=str(child),
            updated_at_utc=stats.get("updated_at_utc"),
            size_bytes=stats.get("size_bytes"),
            metrics={"files": stats.get("files", 0), "size_mb": size_mb, "size_gb": size_gb, "large_folder": is_large_folder},
            tags=tags,
            source_adapter=adapter,
            confidence="inferred",
            summary=summary,
            next_action="Use metadata and latest-file pointers only; archive or trim logs outside Research OS when disk cleanup is intended." if is_large_folder else "",
        )
        out.nodes.extend([family_node(family, adapter), apply_node_overrides(node, overrides)])
        out.edges.append(contains_family_edge(family, node, "log folder grouped by inferred family"))

    out.summary = {"log_folders": folder_count}
    return out
