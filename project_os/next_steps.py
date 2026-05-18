from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from project_os.models import ProjectNode, ProjectRegistry, utc_now_iso
from project_os.patterns import family_gap_rows, normalized_metric_snapshot
from project_os.registry import REGISTRY_DIR, LATEST_NAME, load_registry


OUTCOME_JSON = Path("logs") / "project_os" / "next_step_outcomes_latest.json"
OUTCOME_MD = Path("logs") / "project_os" / "next_step_outcomes_latest.md"


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value in (None, ""):
        return []
    return [part.strip() for part in str(value).replace(";", ",").split(",") if part.strip()]


def _source_paths(node: ProjectNode) -> list[str]:
    metrics = node.metrics or {}
    paths: list[str] = []
    for key in ("rv_forward_audit_path", "paired_slice_report_path"):
        if metrics.get(key):
            paths.append(str(metrics[key]))
    source_key = str(metrics.get("net_pnl_source_key") or "")
    if ".json" in source_key:
        paths.append(source_key.split(".json", 1)[0] + ".json")
    if node.path:
        paths.append(str(node.path))
    return list(dict.fromkeys(paths))


def _short_gates(gates: list[str], limit: int = 4) -> str:
    cleaned = [gate.replace("linked_oos_gate_failed:", "").replace("rv_forward_gate_failed:", "") for gate in gates]
    return ", ".join(cleaned[:limit]) if cleaned else "proof gap"


def _candidate_next_action(node: ProjectNode, gates: list[str], pnl_7d: float | None) -> str:
    label = node.label
    gate_text = _short_gates(gates)
    gate_set = {gate.replace("linked_oos_gate_failed:", "").replace("rv_forward_gate_failed:", "") for gate in gates}
    if label == "RV600NEAR001":
        return "Keep frozen diagnostic, not promotable; positive P&L is too thin/concentrated and still fails sample, breadth, and matched-v28 gates."
    if label == "RV600REV001":
        return "Archive or park this revision unless a newly predeclared RV600 mechanism changes the trade set; current forward economics are negative."
    if label == "RESIDLOCK001":
        return "Archive residual-blend-as-is; fresh locked OOS failed hard, so do not collect more rows without a new predeclared blocker mechanism."
    if label.startswith("PSLICELOCK"):
        if pnl_7d is not None and pnl_7d <= 0:
            return "Block or archive this slice unless redesigned; current local OOS is negative or underpowered after fees."
        return "Repair slice calibration and positive-market-share gates before collecting more rows."
    if pnl_7d is not None and pnl_7d <= 0:
        return f"Archive or redesign this candidate; local OOS/forward evidence is nonpositive and failed {gate_text}."
    if gate_set == {"beats_brownian_probability"}:
        return "Keep as near-miss only; require Brownian-probability improvement before any more collection."
    if "enough_markets" in gate_set:
        return "Block for insufficient markets plus benchmark failures; collect fresh locked OOS only after the mechanism changes."
    if gate_set:
        return f"Do not rerun unchanged; redesign the candidate to address {gate_text} before more rows."
    return "Find or collect linked forward/OOS proof before ranking this candidate further."


def _candidate_outcome(node: ProjectNode) -> dict[str, Any]:
    snapshot = normalized_metric_snapshot(node)
    metrics = node.metrics or {}
    gates = _as_list(metrics.get("linked_oos_failed_gates")) + _as_list(metrics.get("rv_forward_failed_gates"))
    has_local_gate_report = bool(gates or metrics.get("linked_oos_all_passed") is not None or metrics.get("rv_forward_audit_available"))
    completion_status = "completed" if has_local_gate_report else "pending"
    pnl_7d = snapshot.get("pnl_7d_value")
    status = node.status
    if gates:
        status = "blocked"
    outcome = "local_gate_review_completed" if has_local_gate_report else "requires_future_forward_shadow_or_report_link"
    if pnl_7d is not None and float(pnl_7d) <= 0 and has_local_gate_report:
        outcome = "local_gate_review_completed_negative_or_nonpositive"
    if node.label.startswith("PSLICELOCK") and has_local_gate_report:
        outcome = "local_slice_oos_review_completed"
    next_action = _candidate_next_action(node, gates, float(pnl_7d) if pnl_7d is not None else None)
    blockers = [f"next_step:{gate}" for gate in gates]
    if completion_status == "pending":
        blockers = ["next_step:missing_linked_forward_or_oos_report"]
    return {
        "node_id": node.id,
        "kind": node.kind,
        "label": node.label,
        "family": node.family,
        "status": status,
        "evidence_level": node.evidence_level,
        "completion_status": completion_status,
        "outcome": outcome,
        "next_action": next_action,
        "blockers": blockers,
        "source_paths": _source_paths(node),
        "evidence_summary": f"P&L/7d {snapshot.get('pnl_7d_display') or 'n/a'}; source {snapshot.get('pnl_display') or 'n/a'}; gates {', '.join(gates) if gates else 'none'}",
        "metrics": {
            "next_step_pnl_7d_display": snapshot.get("pnl_7d_display"),
            "next_step_source_pnl_display": snapshot.get("pnl_display"),
            "next_step_window": snapshot.get("pnl_window_display"),
            "next_step_failed_gates": gates,
            "next_step_review_source": "registry_and_linked_local_artifacts",
        },
    }


def _family_kind(family: str, row: Mapping[str, Any]) -> str:
    candidates = int(row.get("Candidates") or 0)
    stats = int(row.get("Stats") or 0)
    reports = int(row.get("Reports") or 0)
    forward = int(row.get("Forward Evidence") or 0)
    live = int(row.get("Live Evidence") or 0)
    if family in {"v28_successor", "rv600"} and candidates:
        return "blocked_candidate_family"
    if family in {"dashboard_ui", "infrastructure", "research_os"}:
        return "support_tooling"
    if stats or live:
        return "baseline_or_live_reference"
    if reports or forward:
        return "diagnostic_or_unowned_evidence"
    return "archive_or_unscoped"


def _family_next_action(family: str, family_kind: str, flags: list[str]) -> str:
    if family == "v28_successor":
        return "Freeze sibling runs; classify OOS gate failures, then only test a pre-registered variant with a changed blocker mechanism and stats reconciliation."
    if family == "rv600":
        return "Stop sibling variants until the changed assumption is explicit; repair breadth, average entries, root/market positivity, and matched-v28 comparison before more collection."
    if family_kind == "baseline_or_live_reference":
        return "Keep as baseline/stat reference unless one artifact is explicitly wrapped as a frozen candidate with forward validation criteria."
    if family_kind == "support_tooling":
        return "Keep out of strategy ranking; link only as provenance, dashboard, or infrastructure support."
    if family_kind == "diagnostic_or_unowned_evidence":
        return "Either freeze the strongest artifact as a named candidate with forward gates, or archive the family as diagnostic/support evidence."
    if "NO_CANDIDATE" in flags:
        return "Do not score as a strategy family until a named candidate and evidence chain exist."
    return "No candidate-family action is currently required beyond classification hygiene."


def _family_outcomes(registry: ProjectRegistry) -> list[dict[str, Any]]:
    gaps = {str(row.get("Family") or ""): row for row in family_gap_rows(registry)}
    outcomes: list[dict[str, Any]] = []
    families = sorted((node for node in registry.nodes if node.kind == "family"), key=lambda node: node.family)
    for node in families:
        row = gaps.get(node.family, {})
        flags = [] if row.get("Gap Flags") in (None, "", "NONE") else _as_list(row.get("Gap Flags"))
        family_kind = _family_kind(node.family, row)
        status = "blocked" if family_kind == "blocked_candidate_family" else "diagnostic_only" if family_kind in {"diagnostic_or_unowned_evidence", "archive_or_unscoped"} else node.status
        blockers = [f"family_next_step:{flag}" for flag in flags]
        outcomes.append(
            {
                "node_id": node.id,
                "kind": "family",
                "label": node.label,
                "family": node.family,
                "status": status,
                "evidence_level": node.evidence_level,
                "completion_status": "completed",
                "outcome": family_kind,
                "next_action": _family_next_action(node.family, family_kind, flags),
                "blockers": blockers,
                "source_paths": ["logs/project_os/registry_latest.json", "logs/project_os/research_os_v2_patterns_latest.json"],
                "evidence_summary": (
                    f"{row.get('Candidates', 0)} candidates; {row.get('Reports', 0)} reports; "
                    f"{row.get('Stats', 0)} stats; {row.get('Forward Evidence', 0)} forward; "
                    f"{row.get('Live Evidence', 0)} live; flags {row.get('Gap Flags', 'NONE')}"
                ),
                "metrics": {
                    "family_next_step_kind": family_kind,
                    "family_next_step_flags": flags,
                    "family_next_step_review_source": "family_gap_rows",
                },
            }
        )
    return outcomes


def build_next_step_outcomes(registry: ProjectRegistry) -> dict[str, Any]:
    candidates = sorted([node for node in registry.nodes if node.kind == "candidate"], key=lambda node: (node.family, node.label))
    outcomes = [_candidate_outcome(node) for node in candidates]
    outcomes.extend(_family_outcomes(registry))
    counts: dict[str, int] = {}
    for outcome in outcomes:
        key = str(outcome.get("completion_status") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return {
        "schema": "research_os_next_step_outcomes_v1",
        "generated_at_utc": utc_now_iso(),
        "registry_generated_at_utc": registry.generated_at_utc,
        "research_only": True,
        "summary": "Candidate and family atlas next steps were reviewed against local linked evidence; no live bot, order, threshold, secret, or state changes were made.",
        "counts": counts,
        "outcomes": outcomes,
    }


def render_next_step_markdown(payload: Mapping[str, Any]) -> str:
    outcomes = list(payload.get("outcomes") or [])
    lines = [
        "# Research OS Next-Step Outcomes",
        "",
        f"- generated_at_utc: {payload.get('generated_at_utc')}",
        f"- registry_generated_at_utc: {payload.get('registry_generated_at_utc')}",
        f"- research_only: {payload.get('research_only')}",
        "",
        "Scope: local atlas/evidence review only. No live bot, order, threshold, secret, or state change is implied.",
        "",
        "| Node | Kind | Family | Status | Completion | Outcome | Next Action |",
        "|---|---|---|---|---|---|---|",
    ]
    for outcome in outcomes:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(outcome.get("label")),
                    _md(outcome.get("kind")),
                    _md(outcome.get("family")),
                    _md(outcome.get("status")),
                    _md(outcome.get("completion_status")),
                    _md(outcome.get("outcome")),
                    _md(outcome.get("next_action")),
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_next_step_outcomes(root: Path, registry_path: Path | None = None) -> tuple[Path, Path, dict[str, Any]]:
    registry = load_registry(registry_path or root / REGISTRY_DIR / LATEST_NAME)
    payload = build_next_step_outcomes(registry)
    json_path = root / OUTCOME_JSON
    md_path = root / OUTCOME_MD
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_next_step_markdown(payload), encoding="utf-8")
    return json_path, md_path, payload


def _md(value: Any) -> str:
    return str(value if value is not None else "").replace("\n", " ").replace("\r", " ").replace("|", "\\|")


__all__ = [
    "OUTCOME_JSON",
    "OUTCOME_MD",
    "build_next_step_outcomes",
    "render_next_step_markdown",
    "write_next_step_outcomes",
]
