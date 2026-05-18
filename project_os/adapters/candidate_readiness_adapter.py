from __future__ import annotations

from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, file_size, result, safe_load_json


def _status(value: Any) -> str:
    text = str(value or "blocked")
    allowed = {"strong_candidate", "worth_watching", "needs_more_proof", "blocked", "rejected", "active", "diagnostic_only", "unknown"}
    return text if text in allowed else "blocked"


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "candidate_readiness_adapter"
    out = result(adapter)
    path = root / "logs" / "project_os" / "candidate_readiness_reevaluation_latest.json"
    parsed, note = safe_load_json(path, max_bytes=10_000_000) if path.exists() else ({}, "")
    payload = parsed if isinstance(parsed, dict) else {}
    if note or not payload:
        out.summary = {"present": False}
        return out

    count = 0
    for row in payload.get("candidates") or []:
        if not isinstance(row, dict) or not row.get("node_id"):
            continue
        metrics = row.get("metrics_update") if isinstance(row.get("metrics_update"), dict) else {}
        blockers = row.get("blockers") if isinstance(row.get("blockers"), list) else []
        node = ProjectNode(
            id=str(row["node_id"]),
            kind="candidate",
            label=str(row.get("label") or row["node_id"]),
            family=str(row.get("family") or "unclassified"),
            status=_status(row.get("status_update")),
            evidence_level=str(row.get("evidence_level") or "metadata_only"),
            path=str(path),
            updated_at_utc=path_mtime_iso(path),
            size_bytes=file_size(path),
            metrics=metrics,
            blockers=[str(blocker) for blocker in blockers],
            next_action=str(row.get("next_action") or ""),
            tags=["candidate_readiness_reviewed", str(row.get("readiness_level") or "readiness_unknown")],
            source_adapter=adapter,
            confidence="exact",
            summary=f"Latest same-rubric readiness review: {row.get('readiness_level', 'unknown')} (score {row.get('readiness_score', 'n/a')}).",
        )
        out.nodes.append(apply_node_overrides(node, overrides))
        count += 1
    out.summary = {
        "present": True,
        "candidate_updates": count,
        "schema": payload.get("schema"),
        "generated_at_utc": payload.get("generated_at_utc"),
    }
    return out
