from __future__ import annotations

from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, contains_family_edge, file_size, result, safe_load_json


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _safe_int(value: Any) -> int | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _candidate_node(row: dict[str, Any], path: Path) -> ProjectNode | None:
    node_id = str(row.get("node_id") or "").strip()
    if not node_id:
        return None
    launch_status = str(row.get("launch_status") or "unknown").strip().lower()
    active = launch_status in {"running", "started", "active"}
    mode = str(row.get("mode") or "unknown")
    metrics = {
        "live_test_active": active and mode == "live_order",
        "live_shadow_active": active and mode == "live_shadow",
        "live_test_mode": mode,
        "live_test_launch_status": launch_status,
        "live_test_pid": _safe_int(row.get("pid")),
        "live_test_position_size": _safe_int(row.get("position_size")),
        "live_test_no_max_drawdown": _safe_bool(row.get("no_max_drawdown")),
        "live_test_strategy_tag": row.get("strategy_tag"),
        "live_test_bot_storage_tag": row.get("bot_storage_tag"),
        "live_test_started_at_utc": row.get("started_at_utc"),
        "live_test_status_path": str(path),
    }
    metrics = {key: value for key, value in metrics.items() if value not in (None, "")}
    tags = ["live_testing_status", mode]
    if active:
        tags.append("active_live_testing" if mode == "live_order" else "active_live_shadow")
    return ProjectNode(
        id=node_id,
        kind="candidate",
        label=str(row.get("label") or row.get("candidate_id") or node_id),
        family=str(row.get("family") or "v28_successor"),
        status="active" if active else "worth_watching",
        evidence_level="live_forward" if mode == "live_order" else "forward_shadow",
        path=str(path),
        updated_at_utc=path_mtime_iso(path),
        size_bytes=file_size(path),
        metrics=metrics,
        blockers=[],
        next_action=str(row.get("next_action") or "Monitor live/shadow evidence and refresh the atlas after each collection cycle."),
        tags=tags,
        source_adapter="live_testing_status_adapter",
        confidence="exact",
        summary=str(row.get("summary") or f"{mode} status: {launch_status}"),
    )


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "live_testing_status_adapter"
    out = result(adapter)
    path = root / "logs" / "project_os" / "live_testing_status_latest.json"
    parsed, note = safe_load_json(path, max_bytes=2_000_000) if path.exists() else ({}, "")
    payload = parsed if isinstance(parsed, dict) else {}
    if note or not payload:
        out.summary = {"present": False}
        return out

    count = 0
    for row in [*(payload.get("live_tests") or []), *(payload.get("shadow_tests") or [])]:
        if not isinstance(row, dict):
            continue
        node = _candidate_node(row, path)
        if node is None:
            continue
        node = apply_node_overrides(node, overrides)
        out.nodes.append(node)
        out.edges.append(contains_family_edge(node.family, node, "live testing status"))
        count += 1
    out.summary = {
        "present": True,
        "status_rows": count,
        "generated_at_utc": payload.get("generated_at_utc"),
        "schema": payload.get("schema"),
    }
    return out
