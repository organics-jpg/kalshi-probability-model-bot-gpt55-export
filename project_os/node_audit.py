from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from project_os.models import ProjectNode, ProjectRegistry, utc_now_iso
from project_os.registry import REGISTRY_DIR, LATEST_NAME, load_registry


AUDIT_JSON = Path("logs") / "project_os" / "node_audit_latest.json"
AUDIT_MD = Path("logs") / "project_os" / "node_audit_latest.md"
DECISION_KINDS = {"candidate", "report", "stats"}


def _resolve(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def _mtime_iso(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except OSError:
        return None


def _file_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size) if path.is_file() else None
    except OSError:
        return None


def _path_status(root: Path, node: ProjectNode) -> tuple[str, str, str | None, int | None]:
    path = _resolve(root, node.path)
    if path is None:
        return "missing_path_field", "", None, None
    try:
        exists = path.exists()
    except OSError:
        return "path_error", str(path), None, None
    if not exists:
        return "missing_source_path", str(path), None, None
    if path.is_dir():
        return "directory_exists", str(path), _mtime_iso(path), None
    return "file_exists", str(path), _mtime_iso(path), _file_size(path)


def _metric_bool(metrics: Mapping[str, Any], key: str) -> bool:
    value = metrics.get(key)
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes"}


def _node_findings(node: ProjectNode, path_status: str) -> list[str]:
    metrics = node.metrics or {}
    findings: list[str] = []
    if path_status in {"missing_path_field", "missing_source_path", "path_error"}:
        findings.append(path_status)
    if node.kind == "candidate":
        if metrics.get("pnl_7d_basis") != "7d":
            findings.append("candidate_missing_7d_pnl_basis")
        if not _metric_bool(metrics, "next_step_reviewed"):
            findings.append("candidate_missing_direct_next_step_review")
        if node.status == "blocked" and not node.blockers:
            findings.append("blocked_candidate_missing_blocker")
    if node.kind == "family":
        if not _metric_bool(metrics, "next_step_reviewed"):
            findings.append("family_missing_direct_next_step_review")
        if not metrics.get("family_next_step_kind"):
            findings.append("family_missing_next_step_kind")
    if node.kind in DECISION_KINDS and not (metrics.get("pnl_status") or any("pnl" in str(key).lower() for key in metrics)):
        findings.append("decision_node_missing_pnl_status")
    if node.kind == "secret" and (node.raw_preview or not node.sensitive):
        findings.append("secret_node_preview_or_sensitive_flag_issue")
    if node.kind not in {"family", "secret"} and not node.summary:
        findings.append("missing_summary")
    return sorted(dict.fromkeys(findings))


def _node_outcome(root: Path, registry: ProjectRegistry, node: ProjectNode, generated_at: str) -> dict[str, Any]:
    path_status, resolved_path, source_mtime, source_size = _path_status(root, node)
    findings = _node_findings(node, path_status)
    status = "needs_attention" if findings else "verified"
    return {
        "node_id": node.id,
        "kind": node.kind,
        "label": node.label,
        "family": node.family,
        "status": node.status,
        "evidence_level": node.evidence_level,
        "audit_status": status,
        "findings": findings,
        "metrics": {
            "atlas_node_reviewed": True,
            "atlas_node_reviewed_at_utc": generated_at,
            "atlas_registry_snapshot_utc": registry.generated_at_utc,
            "atlas_node_audit_status": status,
            "atlas_source_path_status": path_status,
            "atlas_resolved_path": resolved_path,
            "atlas_source_mtime_utc": source_mtime,
            "atlas_source_size_bytes": source_size,
            "atlas_audit_findings": findings,
            "atlas_audit_finding_count": len(findings),
        },
    }


def build_node_audit(root: Path, registry: ProjectRegistry) -> dict[str, Any]:
    generated_at = utc_now_iso()
    outcomes = [_node_outcome(root, registry, node, generated_at) for node in registry.nodes]
    status_counts: dict[str, int] = {}
    finding_counts: dict[str, int] = {}
    for outcome in outcomes:
        status = str(outcome.get("audit_status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        for finding in outcome.get("findings") or []:
            finding_counts[str(finding)] = finding_counts.get(str(finding), 0) + 1
    return {
        "schema": "research_os_node_audit_v1",
        "generated_at_utc": generated_at,
        "registry_generated_at_utc": registry.generated_at_utc,
        "research_only": True,
        "node_update_mode": "direct_node_updates_only",
        "summary": "Every atlas node was checked for source path existence, basic metadata freshness, candidate/family next-step annotations, PnL basis, and secret preview hygiene.",
        "counts": {
            "nodes": len(outcomes),
            "audit_statuses": status_counts,
            "findings": finding_counts,
        },
        "outcomes": outcomes,
    }


def render_node_audit_markdown(payload: Mapping[str, Any]) -> str:
    counts = payload.get("counts") if isinstance(payload.get("counts"), Mapping) else {}
    statuses = counts.get("audit_statuses") if isinstance(counts.get("audit_statuses"), Mapping) else {}
    findings = counts.get("findings") if isinstance(counts.get("findings"), Mapping) else {}
    lines = [
        "# Research OS Node Audit",
        "",
        f"- generated_at_utc: {payload.get('generated_at_utc')}",
        f"- registry_generated_at_utc: {payload.get('registry_generated_at_utc')}",
        f"- research_only: {payload.get('research_only')}",
        f"- node_update_mode: {payload.get('node_update_mode')}",
        f"- nodes: {counts.get('nodes')}",
        f"- audit_statuses: {_pairs(statuses)}",
        f"- findings: {_pairs(findings)}",
        "",
        "Scope: direct per-node verification metadata only; this file should not create an atlas summary node.",
        "",
        "| Node | Kind | Family | Audit | Findings |",
        "|---|---|---|---|---|",
    ]
    for outcome in payload.get("outcomes") or []:
        if outcome.get("audit_status") == "verified":
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(outcome.get("label")),
                    _md(outcome.get("kind")),
                    _md(outcome.get("family")),
                    _md(outcome.get("audit_status")),
                    _md(", ".join(outcome.get("findings") or [])),
                ]
            )
            + " |"
        )
    if lines[-1] == "|---|---|---|---|---|":
        lines.append("| all nodes | all | all | verified | none |")
    return "\n".join(lines).rstrip() + "\n"


def write_node_audit(root: Path, registry_path: Path | None = None) -> tuple[Path, Path, dict[str, Any]]:
    registry = load_registry(registry_path or root / REGISTRY_DIR / LATEST_NAME)
    payload = build_node_audit(root.resolve(), registry)
    json_path = root / AUDIT_JSON
    md_path = root / AUDIT_MD
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_node_audit_markdown(payload), encoding="utf-8")
    return json_path, md_path, payload


def _pairs(payload: Mapping[str, Any]) -> str:
    if not payload:
        return "none"
    return ", ".join(f"{key}={payload[key]}" for key in sorted(payload))


def _md(value: Any) -> str:
    return str(value if value is not None else "").replace("\n", " ").replace("\r", " ").replace("|", "\\|")


__all__ = [
    "AUDIT_JSON",
    "AUDIT_MD",
    "build_node_audit",
    "render_node_audit_markdown",
    "write_node_audit",
]
