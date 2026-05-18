from __future__ import annotations

from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, contains_family_edge, file_size, result, safe_load_json


OUTCOME_PATH = Path("logs") / "project_os" / "next_step_outcomes_latest.json"


def _summary_text(outcome: dict[str, Any]) -> str:
    pieces = [
        str(outcome.get("outcome") or ""),
        str(outcome.get("evidence_summary") or ""),
        str(outcome.get("completion_status") or ""),
    ]
    return " ".join(piece for piece in pieces if piece).strip()[:500]


def _target_node(outcome: dict[str, Any], path: Path) -> ProjectNode | None:
    target_id = str(outcome.get("node_id") or "")
    label = str(outcome.get("label") or target_id.rsplit(":", 1)[-1] or "")
    kind = str(outcome.get("kind") or "unknown")
    family = str(outcome.get("family") or "unclassified")
    if not target_id or not label:
        return None
    metrics = dict(outcome.get("metrics") or {})
    metrics.update(
        {
            "next_step_reviewed": True,
            "next_step_completion_status": outcome.get("completion_status"),
            "next_step_outcome": outcome.get("outcome"),
            "next_step_source_paths": "; ".join(str(item) for item in outcome.get("source_paths") or []),
        }
    )
    blockers = [str(item) for item in outcome.get("blockers") or [] if item]
    tags = ["next_step_reviewed", f"next_step_{outcome.get('completion_status') or 'reviewed'}"]
    return ProjectNode(
        id=target_id,
        kind=kind,
        label=label,
        family=family,
        status=str(outcome.get("status") or "unknown"),
        evidence_level=str(outcome.get("evidence_level") or "metadata_only"),
        path=str(path),
        updated_at_utc=path_mtime_iso(path),
        size_bytes=file_size(path),
        metrics={key: value for key, value in metrics.items() if value not in (None, "")},
        blockers=blockers,
        next_action=str(outcome.get("next_action") or ""),
        tags=tags,
        source_adapter="next_step_outcomes_adapter",
        confidence="exact",
        summary=_summary_text(outcome),
    )


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "next_step_outcomes_adapter"
    out = result(adapter)
    path = root / OUTCOME_PATH
    if not path.exists():
        out.summary = {"outcome_file": str(OUTCOME_PATH), "available": False}
        return out

    parsed, parse_note = safe_load_json(path, max_bytes=10_000_000)
    payload = parsed if isinstance(parsed, dict) else {}
    outcomes = [item for item in payload.get("outcomes") or [] if isinstance(item, dict)]
    target_nodes: list[ProjectNode] = []
    for outcome in outcomes:
        node = _target_node(outcome, path)
        if not node:
            continue
        node = apply_node_overrides(node, overrides)
        target_nodes.append(node)
        out.nodes.append(node)
        out.edges.append(contains_family_edge(node.family, node, "next-step outcome target"))

    out.summary = {
        "outcome_file": str(OUTCOME_PATH),
        "available": True,
        "outcomes": len(outcomes),
        "candidate_outcomes": sum(1 for node in target_nodes if node.kind == "candidate"),
        "family_outcomes": sum(1 for node in target_nodes if node.kind == "family"),
        "completed": sum(1 for item in outcomes if item.get("completion_status") == "completed"),
        "blocked": sum(1 for item in outcomes if item.get("completion_status") == "blocked"),
        "pending": sum(1 for item in outcomes if item.get("completion_status") == "pending"),
        "parse_note": parse_note,
        "node_update_mode": "direct_node_updates_only",
    }
    return out
