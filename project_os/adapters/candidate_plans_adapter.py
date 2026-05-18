from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.family import evidence_from_name, infer_family
from project_os.models import AdapterResult, ProjectNode, ProjectEdge, path_mtime_iso

from .base import apply_node_overrides, contains_family_edge, family_node, file_size, health_issue, node_id, result, safe_load_json, safe_read_text


ID_PATTERN = re.compile(r"(?<![A-Za-z0-9])(?:RV600[A-Z0-9]+|PSLICELOCK\d+|GAUSS\d+LOCK\d+|RESIDLOCK\d+|CONSENSUSLOCK\d+|RVTERMLOCK\d+)(?![A-Za-z0-9])")


def _candidate_id(path: Path, payload: dict[str, Any], preview: str) -> str:
    for key in ("candidate_id", "plan_id", "policy_id", "lock_id", "variant_id"):
        val = payload.get(key)
        if val:
            return str(val)
    match = ID_PATTERN.search(path.name + " " + preview)
    return match.group(0) if match else path.stem


def _actual_pnl_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    rationale = payload.get("rationale")
    diagnostics = rationale.get("prior_diagnostic_metrics") if isinstance(rationale, dict) else None
    if not isinstance(diagnostics, dict):
        return {}

    selected_pnl = diagnostics.get("selected_pnl_cents")
    metrics: dict[str, Any] = {}
    if selected_pnl is not None:
        metrics.update(
            {
                "net_pnl": selected_pnl,
                "net_pnl_source_key": "rationale.prior_diagnostic_metrics.selected_pnl_cents",
                "net_pnl_unit_hint": "cents",
                "pnl_provenance": "prior_diagnostic_metrics_from_locked_plan",
                "pnl_status": "normalized_from_locked_plan_prior_diagnostic",
            }
        )
    if diagnostics.get("positive_market_rate") is not None:
        metrics["win_rate"] = diagnostics.get("positive_market_rate")
        metrics["win_rate_source_key"] = "rationale.prior_diagnostic_metrics.positive_market_rate"
    if diagnostics.get("distinct_markets") is not None:
        metrics["markets"] = diagnostics.get("distinct_markets")
        metrics["markets_source_key"] = "rationale.prior_diagnostic_metrics.distinct_markets"
    if diagnostics.get("avg_pnl_per_entry_cents") is not None:
        metrics["avg_pnl_per_entry_cents"] = diagnostics.get("avg_pnl_per_entry_cents")
        metrics["avg_pnl_per_entry_cents_source_key"] = "rationale.prior_diagnostic_metrics.avg_pnl_per_entry_cents"
        metrics["avg_pnl_per_entry_cents_unit_hint"] = "cents"
    return metrics


def _nested(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _rank_oos_report(path: Path) -> int:
    name = path.name.lower()
    if any(token in name for token in ("passive", "replay", "diagnostic", "probability", "selection", "failure", "same_sample")):
        return 0
    if "oos_locked" in name or "locked_oos" in name:
        return 3
    if "locked" in name:
        return 1
    return 0


def _linked_oos_metrics(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    artifact_root = payload.get("artifact_root")
    if not artifact_root:
        return {}
    reports_root = root / str(artifact_root) / "reports"
    if not reports_root.exists():
        return {}

    candidates: list[tuple[int, Path, dict[str, Any]]] = []
    for report_path in reports_root.glob("*.json"):
        rank = _rank_oos_report(report_path)
        if not rank:
            continue
        parsed, _parse_note = safe_load_json(report_path, max_bytes=5_000_000)
        if isinstance(parsed, dict):
            candidates.append((rank, report_path, parsed))
    for _rank, report_path, report in sorted(candidates, key=lambda item: (item[0], item[1].name), reverse=True):
        metric_specs = (
            ("selected_variant.total_counterfactual_pnl_cents", "selected_variant.selected_count", "selected_variant.win_rate"),
            ("consensus_total_counterfactual_pnl_cents", "consensus_selected_count", "consensus_win_rate"),
            ("side_safe_total_counterfactual_pnl_cents", "side_safe_selected_count", "side_safe_win_rate"),
            ("total_counterfactual_pnl_cents", "selected_count", "win_rate"),
        )
        for pnl_path, entries_path, win_rate_path in metric_specs:
            pnl = _nested(report, pnl_path)
            if pnl is None:
                continue
            metrics: dict[str, Any] = {
                "net_pnl": pnl,
                "net_pnl_source_key": f"{report_path.relative_to(root)}:{pnl_path}",
                "net_pnl_unit_hint": "cents",
                "pnl_provenance": "linked_oos_report",
                "pnl_status": "normalized_from_linked_oos_report",
                "pnl_source_label": report_path.name,
            }
            gate_results = report.get("gate_results")
            if isinstance(gate_results, dict):
                failed_gates = sorted(
                    str(key)
                    for key, value in gate_results.items()
                    if value is False and str(key) != "all_passed"
                )
                metrics["linked_oos_all_passed"] = bool(gate_results.get("all_passed"))
                metrics["linked_oos_failed_gates"] = failed_gates
                if report.get("evaluation_scope") == "locked_oos_shadow" or gate_results.get("locked_oos_scope") is True:
                    metrics["linked_oos_evidence_level"] = "forward_shadow"
            entries = _nested(report, entries_path)
            markets = report.get("market_count")
            win_rate = _nested(report, win_rate_path)
            if entries is not None:
                metrics["entries"] = entries
                metrics["entries_source_key"] = f"{report_path.relative_to(root)}:{entries_path}"
            if markets is not None:
                metrics["markets"] = markets
                metrics["markets_source_key"] = f"{report_path.relative_to(root)}:market_count"
            if win_rate is not None:
                metrics["win_rate"] = win_rate
                metrics["win_rate_source_key"] = f"{report_path.relative_to(root)}:{win_rate_path}"
            return metrics
    return {}


def _paired_sidecar_slice_oos_metrics(root: Path, candidate_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not candidate_id.startswith("PSLICELOCK"):
        return {}
    report_path = root / "logs" / "particle_research" / "reports" / f"paired_sidecar_slice_oos_{candidate_id}_latest.json"
    parsed, _parse_note = safe_load_json(report_path, max_bytes=5_000_000) if report_path.exists() else ({}, "")
    report = parsed if isinstance(parsed, dict) else {}
    if not report:
        return {}
    selected = report.get("selected_metrics")
    selected = selected if isinstance(selected, dict) else {}
    pnl = selected.get("selected_pnl_cents")
    if pnl is None:
        return {}
    markets = selected.get("markets") or report.get("slice_markets") or report.get("fresh_markets")
    positive_markets = selected.get("positive_selected_market_count")
    win_rate = None
    try:
        if positive_markets is not None and markets:
            win_rate = float(positive_markets) / float(markets)
    except (TypeError, ValueError, ZeroDivisionError):
        win_rate = None
    metrics: dict[str, Any] = {
        "net_pnl": pnl,
        "net_pnl_source_key": f"{report_path.relative_to(root)}:selected_metrics.selected_pnl_cents",
        "net_pnl_unit_hint": "cents",
        "pnl_provenance": "paired_sidecar_slice_oos_report",
        "pnl_status": "normalized_from_paired_sidecar_slice_oos_report",
        "pnl_source_label": report_path.name,
        "entries": selected.get("selected_count"),
        "entries_source_key": f"{report_path.relative_to(root)}:selected_metrics.selected_count",
        "markets": markets,
        "markets_source_key": f"{report_path.relative_to(root)}:selected_metrics.markets",
        "win_rate": win_rate,
        "paired_slice_report_path": str(report_path.relative_to(root)),
        "paired_slice_evaluation_scope": report.get("evaluation_scope") or payload.get("evaluation_scope"),
    }
    gate_results = report.get("gate_results")
    if isinstance(gate_results, dict):
        failed_gates = sorted(
            str(key)
            for key, value in gate_results.items()
            if value is False and str(key) != "all_passed"
        )
        metrics["linked_oos_all_passed"] = bool(gate_results.get("all_passed"))
        metrics["linked_oos_failed_gates"] = failed_gates
        if gate_results.get("locked_forward_scope") is True or report.get("evaluation_scope") == "locked_forward_shadow":
            metrics["linked_oos_evidence_level"] = "forward_shadow"
    return {key: value for key, value in metrics.items() if value not in (None, "")}


def _linked_oos_blockers(metrics: dict[str, Any]) -> list[str]:
    failed = metrics.get("linked_oos_failed_gates")
    if not isinstance(failed, list):
        return []
    return [f"linked_oos_gate_failed:{gate}" for gate in failed[:12]]


def _rv600_forward_audit_metrics(root: Path, candidate_id: str) -> dict[str, Any]:
    audit_path = root / "logs" / "project_os" / f"rv_positive_candidate_forward_audit_{candidate_id}.json"
    parsed, _parse_note = safe_load_json(audit_path, max_bytes=5_000_000) if audit_path.exists() else ({}, "")
    audit = parsed if isinstance(parsed, dict) else {}
    if not audit:
        return {}
    primary = audit.get("primary_summary")
    primary = primary if isinstance(primary, dict) else {}
    sample = audit.get("sample_gates")
    sample = sample if isinstance(sample, dict) else {}
    rejection = str(primary.get("rejection_reason") or "")
    failed = [f"sample_{key}" for key, value in sample.items() if value is False]
    failed.extend(part.strip() for part in re.split(r"[;,]", rejection) if part.strip())
    metrics: dict[str, Any] = {
        "rv_forward_audit_available": True,
        "rv_forward_audit_path": str(audit_path.relative_to(root)),
        "rv_forward_decision": audit.get("decision"),
        "rv_forward_failed_gates": list(dict.fromkeys(failed))[:20],
        "rv_forward_root_count": audit.get("root_count"),
        "rv_forward_calendar_day_count": audit.get("calendar_day_count"),
        "rv_forward_weekend_day_count": audit.get("weekend_day_count"),
        "rv_forward_selected_pnl_cents": primary.get("selected_pnl_cents"),
        "rv_forward_accepted_entries": primary.get("accepted_entries"),
        "rv_forward_distinct_markets": primary.get("distinct_markets"),
        "rv_forward_avg_pnl_per_entry_cents": primary.get("avg_pnl_per_entry_cents"),
        "rv_forward_positive_root_rate": primary.get("positive_root_rate"),
        "rv_forward_positive_market_rate": primary.get("positive_market_rate"),
        "rv_forward_matched_v28_delta_cents": primary.get("matched_v28_delta_cents"),
    }
    return {key: value for key, value in metrics.items() if value not in (None, "")}


def _rv600_forward_blockers(metrics: dict[str, Any]) -> list[str]:
    failed = metrics.get("rv_forward_failed_gates")
    if not isinstance(failed, list):
        return []
    return [f"rv_forward_gate_failed:{gate}" for gate in failed[:12]]


def _status_for_candidate(metrics: dict[str, Any], blockers: list[str]) -> str:
    if blockers:
        return "blocked"
    if metrics.get("linked_oos_all_passed") is True:
        return "worth_watching"
    return "needs_more_proof"


def _next_action_for_candidate(metrics: dict[str, Any], blockers: list[str]) -> str:
    if blockers:
        if metrics.get("rv_forward_audit_available"):
            return "Forward audit refreshed; keep frozen diagnostic until sample, breadth, and matched-v28 gates clear."
        return "Inspect linked OOS failed gates; change blocker mechanism before collecting more rows."
    if metrics.get("linked_oos_all_passed") is True:
        return "Run a separate locked holdout audit before any live consideration."
    return "Collect more forward/shadow rows"


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "candidate_plans_adapter"
    out = result(adapter)
    plans_root = root / "logs" / "particle_research" / "locked_oos_plans"
    if not plans_root.exists():
        out.issues.append(health_issue(adapter, "unclassified", "locked plans missing", "locked_oos_plans folder does not exist", plans_root))
        return out

    count = 0
    for plan_path in sorted(plans_root.glob("*.json"), key=lambda p: p.name.lower()):
        count += 1
        parsed, parse_note = safe_load_json(plan_path)
        payload = parsed if isinstance(parsed, dict) else {}
        md_path = plan_path.with_suffix(".md")
        preview = safe_read_text(md_path if md_path.exists() else plan_path)
        if parse_note and not payload:
            out.issues.append(health_issue(adapter, infer_family(plan_path.name), f"bad locked plan: {plan_path.name}", parse_note, plan_path))
        candidate_id = _candidate_id(plan_path, payload, preview)
        family = infer_family(plan_path.name, candidate_id, preview, payload.get("family"), payload.get("variant"))
        metrics = {
            "frozen": bool(payload),
            "params": len(payload.get("params", {}) or {}) if isinstance(payload.get("params"), dict) else None,
        }
        metrics = {k: v for k, v in metrics.items() if v is not None}
        actual_pnl_metrics = _actual_pnl_metrics(payload)
        linked_oos_metrics = _linked_oos_metrics(root, payload)
        if not linked_oos_metrics:
            linked_oos_metrics = _paired_sidecar_slice_oos_metrics(root, candidate_id, payload)
        rv_forward_metrics = _rv600_forward_audit_metrics(root, candidate_id)
        if actual_pnl_metrics:
            metrics.update(actual_pnl_metrics)
        if linked_oos_metrics:
            metrics.update(linked_oos_metrics)
        if rv_forward_metrics:
            metrics.update(rv_forward_metrics)
        if not linked_oos_metrics and not rv_forward_metrics:
            metrics.setdefault("pnl_status", "no_actual_pnl_in_locked_plan")
            metrics.setdefault("pnl_missing_reason", "locked plan stores gates/thresholds but no realized or diagnostic P&L metric")
        blockers = [*_linked_oos_blockers(metrics), *_rv600_forward_blockers(metrics)]
        evidence = evidence_from_name(plan_path.name)
        if metrics.get("linked_oos_evidence_level") == "forward_shadow" or metrics.get("rv_forward_audit_available"):
            evidence = "forward_shadow"
        node = ProjectNode(
            id=node_id("candidate", family, candidate_id),
            kind="candidate",
            label=candidate_id,
            family=family,
            status=_status_for_candidate(metrics, blockers),
            evidence_level=evidence,
            path=str(plan_path),
            updated_at_utc=path_mtime_iso(plan_path),
            size_bytes=file_size(plan_path),
            metrics=metrics,
            blockers=blockers,
            next_action=_next_action_for_candidate(metrics, blockers),
            tags=["candidate", "locked_plan"],
            source_adapter=adapter,
            confidence="exact" if candidate_id != plan_path.stem else "inferred",
            summary=(preview.splitlines()[0] if preview.strip() else f"Locked candidate plan {plan_path.name}")[:500],
            raw_preview=preview[:2000],
        )
        plan_node = ProjectNode(
            id=node_id("artifact", family, plan_path.stem),
            kind="artifact",
            label=plan_path.stem,
            family=family,
            status="active",
            evidence_level="metadata_only",
            path=str(plan_path),
            updated_at_utc=path_mtime_iso(plan_path),
            size_bytes=file_size(plan_path),
            tags=["locked_plan", "json"],
            source_adapter=adapter,
            confidence="exact",
            summary=f"Locked plan artifact for {candidate_id}.",
            raw_preview=preview[:1200],
        )
        out.nodes.extend([family_node(family, adapter), apply_node_overrides(node, overrides), apply_node_overrides(plan_node, overrides)])
        out.edges.append(contains_family_edge(family, node, "locked plan grouped by family"))
        out.edges.append(contains_family_edge(family, plan_node, "locked plan artifact grouped by family"))
        out.edges.append(ProjectEdge(source=plan_node.id, target=node.id, relation="documents", evidence_level="metadata_only", confidence="exact", reason="locked plan defines candidate"))

    out.summary = {"locked_plans": count}
    return out
