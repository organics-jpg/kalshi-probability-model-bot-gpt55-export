from __future__ import annotations

from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.models import AdapterResult, ProjectNode

from .base import apply_node_overrides, result, safe_load_json


AUDIT_PATH = Path("logs") / "project_os" / "node_audit_latest.json"


def _target_node(outcome: dict[str, Any]) -> ProjectNode | None:
    target_id = str(outcome.get("node_id") or "")
    label = str(outcome.get("label") or target_id.rsplit(":", 1)[-1] or "")
    kind = str(outcome.get("kind") or "unknown")
    family = str(outcome.get("family") or "unclassified")
    if not target_id or not label:
        return None
    metrics = {key: value for key, value in dict(outcome.get("metrics") or {}).items() if value not in (None, "")}
    findings = [str(item) for item in outcome.get("findings") or [] if item]
    tags = ["atlas_node_audited"]
    tags.append("atlas_audit_verified" if not findings else "atlas_audit_needs_attention")
    blockers = [f"atlas_audit:{finding}" for finding in findings]
    return ProjectNode(
        id=target_id,
        kind=kind,
        label=label,
        family=family,
        status=str(outcome.get("status") or "unknown"),
        evidence_level=str(outcome.get("evidence_level") or "metadata_only"),
        metrics=metrics,
        blockers=blockers,
        tags=tags,
        source_adapter="node_audit_adapter",
        confidence="exact",
        summary=f"Atlas node audit: {outcome.get('audit_status') or 'unknown'}; {', '.join(findings) if findings else 'no findings'}.",
    )


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "node_audit_adapter"
    out = result(adapter)
    path = root / AUDIT_PATH
    if not path.exists():
        out.summary = {"audit_file": str(AUDIT_PATH), "available": False}
        return out

    parsed, parse_note = safe_load_json(path, max_bytes=50_000_000)
    payload = parsed if isinstance(parsed, dict) else {}
    outcomes = [item for item in payload.get("outcomes") or [] if isinstance(item, dict)]
    for outcome in outcomes:
        node = _target_node(outcome)
        if node is None:
            continue
        out.nodes.append(apply_node_overrides(node, overrides))
    counts = payload.get("counts") if isinstance(payload.get("counts"), dict) else {}
    out.summary = {
        "audit_file": str(AUDIT_PATH),
        "available": True,
        "nodes_audited": len(out.nodes),
        "node_update_mode": "direct_node_updates_only",
        "audit_statuses": counts.get("audit_statuses", {}),
        "findings": counts.get("findings", {}),
        "parse_note": parse_note,
    }
    return out
