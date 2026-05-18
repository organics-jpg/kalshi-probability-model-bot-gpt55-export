from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from project_os.models import ProjectNode, ProjectRegistry, utc_now_iso
from project_os.patterns import normalized_metric_snapshot
from project_os.registry import REGISTRY_DIR, LATEST_NAME, load_registry


DEFAULT_OUTPUT_JSON = Path("logs") / "project_os" / "rv_positive_candidate_forward_validation_latest.json"
DEFAULT_OUTPUT_MD = Path("logs") / "project_os" / "rv_positive_candidate_forward_validation_latest.md"


@dataclass(frozen=True)
class Gate:
    gate: str
    status: str
    value: Any = None
    threshold: str = ""
    source: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "status": self.status,
            "value": self.value,
            "threshold": self.threshold,
            "source": self.source,
            "note": self.note,
        }


def build_rv_positive_validation(root: Path, registry_path: Path | None = None) -> dict[str, Any]:
    """Build a research-only validation payload for positive-PnL RV candidates."""
    root = root.resolve()
    registry = load_registry(registry_path or root / REGISTRY_DIR / LATEST_NAME)
    candidates = positive_rv_candidate_nodes(registry)
    rows = [_candidate_result(root, node) for node in candidates]
    return {
        "schema_version": "research-os-rv-positive-forward-validation-v1",
        "generated_utc": utc_now_iso(),
        "research_only": True,
        "scope": "Positive-PnL RV candidates from the current Research OS registry; no live bot, order, scorer, threshold, secret, live state, or 8501 dashboard changes.",
        "registry_generated_at_utc": registry.generated_at_utc,
        "registry_path": str(registry_path or root / REGISTRY_DIR / LATEST_NAME),
        "positive_rv_candidate_count": len(rows),
        "candidate_ids": [row["candidate_id"] for row in rows],
        "overall_decision": _overall_decision(rows),
        "candidate_results": rows,
    }


def write_rv_positive_validation(
    root: Path,
    *,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
    registry_path: Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    payload = build_rv_positive_validation(root, registry_path=registry_path)
    json_out = root / output_json if not output_json.is_absolute() else output_json
    md_out = root / output_md if not output_md.is_absolute() else output_md
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out.write_text(render_rv_positive_validation_markdown(payload), encoding="utf-8")
    return json_out, md_out, payload


def positive_rv_candidate_nodes(registry: ProjectRegistry) -> list[ProjectNode]:
    rows: list[tuple[float, str, ProjectNode]] = []
    for node in registry.nodes:
        if node.kind != "candidate":
            continue
        if not _is_rv_like(node):
            continue
        snapshot = normalized_metric_snapshot(node)
        pnl_value = snapshot.get("pnl_7d_value")
        if pnl_value is None:
            pnl_value = snapshot.get("pnl_value")
        if pnl_value is None or float(pnl_value) <= 0:
            continue
        rows.append((float(pnl_value), node.label, node))
    return [node for _pnl, _label, node in sorted(rows, key=lambda item: (-item[0], item[1]))]


def render_rv_positive_validation_markdown(payload: Mapping[str, Any]) -> str:
    rows = list(payload.get("candidate_results") or [])
    lines = [
        "# RV Positive Candidate Forward Validation",
        "",
        f"- generated_utc: {payload.get('generated_utc')}",
        f"- research_only: {payload.get('research_only')}",
        f"- registry_generated_at_utc: {payload.get('registry_generated_at_utc')}",
        f"- positive_rv_candidate_count: {payload.get('positive_rv_candidate_count')}",
        f"- overall_decision: `{payload.get('overall_decision')}`",
        "",
        "Scope: reads registry, locked-plan, and OOS/shadow artifacts only. This report does not change live bot logic, order logic, scorer behavior, thresholds, secrets, live trading state, or the 8501 dashboard.",
        "",
        "## Candidate Summary",
        "",
        "| Candidate | Family | Registry P&L/7d | Source P&L | Window | Forward/OOS P&L | Entries | Markets | Verdict | Blocking Gates |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_md(row.get('candidate_id'))}`",
                    _md(row.get("family")),
                    _md(row.get("registry_pnl_7d_display")),
                    _md(row.get("registry_pnl_display")),
                    _md(row.get("registry_pnl_window_display")),
                    _md(_format_cents(row.get("forward_or_oos_pnl_cents"))),
                    _md(row.get("forward_or_oos_entries")),
                    _md(row.get("forward_or_oos_markets")),
                    f"`{_md(row.get('verdict'))}`",
                    _md(", ".join(row.get("blocking_gates") or []) or "none"),
                ]
            )
            + " |"
        )
    lines.append("")
    for row in rows:
        lines.extend(
            [
                f"## {row.get('candidate_id')}",
                "",
                f"- family: `{_md(row.get('family'))}`",
                f"- source_path: `{_md(row.get('source_path'))}`",
                f"- validation_source: `{_md(row.get('validation_source'))}`",
                f"- verdict: `{_md(row.get('verdict'))}`",
                f"- recommendation: {_md(row.get('recommendation'))}",
                "",
                "| Gate | Status | Value | Threshold | Source |",
                "|---|---|---|---|---|",
            ]
        )
        for gate in row.get("gates") or []:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{_md(gate.get('gate'))}`",
                        f"`{_md(gate.get('status'))}`",
                        _md(_display_value(gate.get("value"))),
                        _md(gate.get("threshold")),
                        _md(gate.get("source")),
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _candidate_result(root: Path, node: ProjectNode) -> dict[str, Any]:
    snapshot = normalized_metric_snapshot(node)
    source_path = _node_path(root, node.path)
    if node.family == "rv600" and source_path and source_path.exists():
        return _rv600_locked_plan_result(root, node, source_path, snapshot)
    return _linked_oos_result(root, node, source_path, snapshot)


def _rv600_locked_plan_result(
    root: Path,
    node: ProjectNode,
    plan_path: Path,
    snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    plan = _load_json(plan_path)
    plan_id = str(plan.get("plan_id") or node.label)
    audit_path = root / "logs" / "project_os" / f"rv_positive_candidate_forward_audit_{plan_id}.json"
    audit = _load_json(audit_path)
    gates: list[Gate] = [
        Gate(
            "registry_pnl_positive",
            "pass",
            snapshot.get("pnl_7d_display") or snapshot.get("pnl_display"),
            "> 0",
            "Research OS registry normalized 7-day metric",
            "This only qualifies the candidate for the validation sweep.",
        )
    ]
    prior = ((plan.get("rationale") or {}).get("prior_diagnostic_metrics") or {}) if plan else {}
    gates.extend(_prior_diagnostic_gates(prior))

    primary = audit.get("primary_summary") or {}
    summary_rows = list(audit.get("summary_rows") or [])
    if not audit:
        gates.append(Gate("forward_audit_available", "missing", None, "required", str(audit_path)))
        verdict = "needs_forward_audit"
        recommendation = "Run the locked-plan forward audit before interpreting the frozen plan."
        forward_pnl = None
        forward_entries = None
        forward_markets = None
    else:
        gates.extend(_rv600_forward_gates(plan, audit, primary, summary_rows))
        verdict = _verdict_for_gates(gates)
        recommendation = _rv600_recommendation(plan_id, primary, gates)
        forward_pnl = _num(primary.get("selected_pnl_cents"))
        forward_entries = _int_or_none(primary.get("accepted_entries"))
        forward_markets = _int_or_none(primary.get("distinct_markets"))

    gate_dicts = [gate.to_dict() for gate in gates]
    return {
        "candidate_id": node.label,
        "node_id": node.id,
        "family": node.family,
        "registry_status": node.status,
        "registry_evidence_level": node.evidence_level,
        "registry_pnl_display": snapshot.get("pnl_display"),
        "registry_pnl_value_dollars": snapshot.get("pnl_value"),
        "registry_pnl_7d_display": snapshot.get("pnl_7d_display"),
        "registry_pnl_7d_value_dollars": snapshot.get("pnl_7d_value"),
        "registry_pnl_window_display": snapshot.get("pnl_window_display"),
        "registry_pnl_observed_window_days": snapshot.get("pnl_observed_window_days"),
        "registry_pnl_standardization_status": snapshot.get("pnl_standardization_status"),
        "registry_pnl_confidence": snapshot.get("pnl_confidence"),
        "source_path": _rel(root, plan_path),
        "validation_source": _rel(root, audit_path),
        "validation_kind": "rv600_locked_plan_forward_audit",
        "forward_or_oos_pnl_cents": forward_pnl,
        "forward_or_oos_entries": forward_entries,
        "forward_or_oos_markets": forward_markets,
        "verdict": verdict,
        "recommendation": recommendation,
        "blocking_gates": _blocking_gate_names(gate_dicts),
        "gates": gate_dicts,
        "primary_summary": primary,
        "sample_gates": audit.get("sample_gates") or {},
    }


def _linked_oos_result(
    root: Path,
    node: ProjectNode,
    source_path: Path | None,
    snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    source_report = _source_report_from_metric(root, node)
    report = _load_json(source_report) if source_report else {}
    gates: list[Gate] = [
        Gate(
            "registry_pnl_positive",
            "pass",
            snapshot.get("pnl_7d_display") or snapshot.get("pnl_display"),
            "> 0",
            "Research OS registry normalized 7-day metric",
            "This only qualifies the candidate for the validation sweep.",
        )
    ]
    selected = report.get("selected_variant") or {}
    gate_results = report.get("gate_results") or {}
    if not report:
        gates.append(Gate("linked_oos_report_available", "missing", None, "required", str(source_report or "")))
        verdict = "needs_linked_oos_report"
        recommendation = "Repair the linked report before interpreting this positive P&L."
    else:
        gates.extend(_terminal_oos_gates(report, gate_results, selected))
        verdict = _verdict_for_gates(gates, terminal=True)
        recommendation = _terminal_recommendation(node.label, gate_results)

    gate_dicts = [gate.to_dict() for gate in gates]
    return {
        "candidate_id": node.label,
        "node_id": node.id,
        "family": node.family,
        "registry_status": node.status,
        "registry_evidence_level": node.evidence_level,
        "registry_pnl_display": snapshot.get("pnl_display"),
        "registry_pnl_value_dollars": snapshot.get("pnl_value"),
        "registry_pnl_7d_display": snapshot.get("pnl_7d_display"),
        "registry_pnl_7d_value_dollars": snapshot.get("pnl_7d_value"),
        "registry_pnl_window_display": snapshot.get("pnl_window_display"),
        "registry_pnl_observed_window_days": snapshot.get("pnl_observed_window_days"),
        "registry_pnl_standardization_status": snapshot.get("pnl_standardization_status"),
        "registry_pnl_confidence": snapshot.get("pnl_confidence"),
        "source_path": _rel(root, source_path) if source_path else "",
        "validation_source": _rel(root, source_report) if source_report else "",
        "validation_kind": "linked_oos_report",
        "forward_or_oos_pnl_cents": _num(selected.get("total_counterfactual_pnl_cents")),
        "forward_or_oos_entries": _int_or_none(selected.get("selected_count")),
        "forward_or_oos_markets": _int_or_none(report.get("market_count")),
        "verdict": verdict,
        "recommendation": recommendation,
        "blocking_gates": _blocking_gate_names(gate_dicts),
        "gates": gate_dicts,
        "selected_variant": selected,
        "gate_results": gate_results,
    }


def _prior_diagnostic_gates(metrics: Mapping[str, Any]) -> list[Gate]:
    if not metrics:
        return [Gate("prior_diagnostic_metrics_available", "missing", None, "required for frozen-plan context")]
    return [
        Gate("prior_selected_pnl_positive", _pass_fail(_num(metrics.get("selected_pnl_cents")), lambda value: value > 0), _num(metrics.get("selected_pnl_cents")), "> 0c", "locked plan prior diagnostic"),
        Gate("prior_avg_entry_at_least_10c", _pass_fail(_num(metrics.get("avg_pnl_per_entry_cents")), lambda value: value >= 10.0), _num(metrics.get("avg_pnl_per_entry_cents")), ">= 10c", "locked plan prior diagnostic"),
        Gate("prior_positive_roots_at_least_60pct", _pass_fail(_num(metrics.get("positive_root_rate")), lambda value: value >= 0.60), _num(metrics.get("positive_root_rate")), ">= 0.60", "locked plan prior diagnostic"),
        Gate("prior_positive_markets_at_least_60pct", _pass_fail(_num(metrics.get("positive_market_rate")), lambda value: value >= 0.60), _num(metrics.get("positive_market_rate")), ">= 0.60", "locked plan prior diagnostic"),
        Gate("prior_concentration_at_most_25pct", _pass_fail(_num(metrics.get("max_single_market_pnl_share")), lambda value: value <= 0.25), _num(metrics.get("max_single_market_pnl_share")), "<= 0.25", "locked plan prior diagnostic"),
        Gate("prior_last_window_positive", _pass_fail(_num(metrics.get("last_window_pnl_cents")), lambda value: value > 0), _num(metrics.get("last_window_pnl_cents")), "> 0c", "locked plan prior diagnostic"),
    ]


def _rv600_forward_gates(
    plan: Mapping[str, Any],
    audit: Mapping[str, Any],
    primary: Mapping[str, Any],
    summary_rows: Iterable[Mapping[str, Any]],
) -> list[Gate]:
    target = dict(plan.get("forward_gates") or {})
    candidate = dict(plan.get("candidate") or {})
    required_modes = set(candidate.get("required_accounting_modes") or [])
    seen_modes = {str(row.get("accounting_mode")) for row in summary_rows if row.get("accounting_mode")}
    sample = dict(audit.get("sample_gates") or {})
    rejection = str(primary.get("rejection_reason") or "")
    gates = [
        Gate("forward_audit_available", "pass", audit.get("decision"), "report exists", str(audit.get("plan_json") or "")),
        Gate("forward_entries_at_least_target", _bool_status(sample.get("accepted_entries")), primary.get("accepted_entries"), f">= {target.get('target_accepted_entries', 100)}", "locked-plan forward audit"),
        Gate("forward_markets_at_least_target", _bool_status(sample.get("distinct_markets")), primary.get("distinct_markets"), f">= {target.get('target_distinct_markets', 40)}", "locked-plan forward audit"),
        Gate("forward_calendar_days_at_least_target", _bool_status(sample.get("calendar_days")), audit.get("calendar_day_count"), f">= {target.get('target_calendar_days', 10)}", "locked-plan forward audit"),
        Gate("forward_weekend_sessions_at_least_target", _bool_status(sample.get("weekend_sessions")), audit.get("weekend_day_count"), f">= {target.get('target_weekend_sessions', 2)}", "locked-plan forward audit"),
        Gate("forward_selected_pnl_positive", _pass_fail(_num(primary.get("selected_pnl_cents")), lambda value: value > 0), _num(primary.get("selected_pnl_cents")), "> 0c", "locked-plan forward audit"),
        Gate("forward_avg_entry_at_least_10c", _pass_fail(_num(primary.get("avg_pnl_per_entry_cents")), lambda value: value >= float(target.get("avg_pnl_per_entry_cents_min") or 10.0)), _num(primary.get("avg_pnl_per_entry_cents")), f">= {target.get('avg_pnl_per_entry_cents_min', 10.0)}c", "locked-plan forward audit"),
        Gate("forward_positive_roots_at_least_60pct", _pass_fail(_num(primary.get("positive_root_rate")), lambda value: value >= float(target.get("positive_root_rate_min") or 0.60)), _num(primary.get("positive_root_rate")), f">= {target.get('positive_root_rate_min', 0.60)}", "locked-plan forward audit"),
        Gate("forward_positive_markets_at_least_60pct", _pass_fail(_num(primary.get("positive_market_rate")), lambda value: value >= float(target.get("positive_market_rate_min") or 0.60)), _num(primary.get("positive_market_rate")), f">= {target.get('positive_market_rate_min', 0.60)}", "locked-plan forward audit"),
        Gate("forward_concentration_at_most_25pct", _pass_fail(_num(primary.get("max_single_market_pnl_share")), lambda value: value <= float(target.get("max_single_market_pnl_share_max") or 0.25)), _num(primary.get("max_single_market_pnl_share")), f"<= {target.get('max_single_market_pnl_share_max', 0.25)}", "locked-plan forward audit"),
        Gate("forward_last_window_positive", _pass_fail(_num(primary.get("last_window_pnl_cents")), lambda value: value > 0), _num(primary.get("last_window_pnl_cents")), "> 0c", "locked-plan forward audit"),
        Gate("forward_no_fill_penalty_positive", _pass_fail(_num(primary.get("no_fill_penalty_pnl_cents")), lambda value: value > 0), _num(primary.get("no_fill_penalty_pnl_cents")), "> 0c", "locked-plan forward audit"),
        Gate("forward_repeated_entry_gate_pass", _bool_status(primary.get("repeated_entry_gate_pass")), primary.get("repeated_entry_gate_pass"), "true", "locked-plan forward audit"),
        Gate("matched_v28_beaten_by_20pct", "fail" if "does_not_beat_matched_v28_by_20pct" in rejection else "pass", {"selected_pnl_cents": primary.get("selected_pnl_cents"), "matched_v28_control_pnl_cents": primary.get("matched_v28_control_pnl_cents"), "matched_v28_delta_cents": primary.get("matched_v28_delta_cents")}, "selected >= matched v28 + 20%", "locked-plan forward audit"),
        Gate("all_required_accounting_modes_present", "pass" if required_modes and required_modes.issubset(seen_modes) else "missing", sorted(seen_modes), ", ".join(sorted(required_modes)), "locked-plan forward audit"),
        Gate("forward_gate_bundle_clean", "pass" if not rejection else "fail", rejection or "clean", "no rejection reasons", "locked-plan forward audit"),
    ]
    return gates


def _terminal_oos_gates(
    report: Mapping[str, Any],
    gate_results: Mapping[str, Any],
    selected: Mapping[str, Any],
) -> list[Gate]:
    gate_config = dict(report.get("gate_config") or {})
    named = [
        ("locked_oos_scope", "true", "OOS report"),
        ("enough_candidates", f">= {gate_config.get('min_candidate_count', 'configured')}", "OOS report"),
        ("enough_markets", f">= {gate_config.get('min_market_count', 'configured')}", "OOS report"),
        ("enough_selected", f">= {gate_config.get('min_selected_count', 'configured')}", "OOS report"),
        ("positive_total_pnl", "> 0c", "OOS report"),
        ("positive_avg_pnl", f">= {gate_config.get('min_avg_pnl_per_selected_cents', 0)}c", "OOS report"),
        ("beats_static_particle_pnl", "true", "OOS report"),
        ("beats_current_calibrated_pnl", "true", "OOS report"),
        ("beats_current_probability", "true", "OOS report"),
        ("beats_market_probability", "true", "OOS report"),
        ("beats_brownian_probability", "true", "OOS report"),
        ("positive_ev_rank", "true", "OOS report"),
        ("positive_top_ev_bucket", "> 0c", "OOS report"),
    ]
    values = {
        "positive_total_pnl": selected.get("total_counterfactual_pnl_cents"),
        "positive_avg_pnl": selected.get("avg_counterfactual_pnl_cents_per_selected"),
        "enough_candidates": report.get("candidate_count"),
        "enough_markets": report.get("market_count"),
        "enough_selected": selected.get("selected_count"),
        "positive_ev_rank": selected.get("ev_rank_correlation_sign"),
        "positive_top_ev_bucket": selected.get("top_ev_bucket_pnl_cents"),
    }
    gates = [
        Gate(name, _bool_status(gate_results.get(name)), values.get(name, gate_results.get(name)), threshold, source)
        for name, threshold, source in named
    ]
    gates.append(Gate("all_terminal_oos_gates_passed", _bool_status(gate_results.get("all_passed")), gate_results.get("all_passed"), "true", "OOS report"))
    return gates


def _verdict_for_gates(gates: Iterable[Gate], *, terminal: bool = False) -> str:
    gate_list = list(gates)
    failures = {gate.gate for gate in gate_list if gate.status == "fail"}
    missing = {gate.gate for gate in gate_list if gate.status == "missing"}
    if missing and not failures:
        return "needs_source_fields"
    if terminal:
        return "forward_validated" if not failures and not missing else "blocked_oos_robustness_failed"
    sample_failures = {
        "forward_entries_at_least_target",
        "forward_markets_at_least_target",
        "forward_calendar_days_at_least_target",
        "forward_weekend_sessions_at_least_target",
    } & failures
    performance_failures = failures - sample_failures - {"prior_avg_entry_at_least_10c"}
    if sample_failures and performance_failures:
        return "blocked_forward_failed_and_underpowered"
    if sample_failures:
        return "needs_more_forward_shadow"
    if performance_failures:
        return "blocked_forward_failed"
    return "forward_validated"


def _rv600_recommendation(plan_id: str, primary: Mapping[str, Any], gates: Iterable[Gate]) -> str:
    failures = _blocking_gate_names([gate.to_dict() for gate in gates])
    selected = _num(primary.get("selected_pnl_cents"))
    if selected is not None and selected <= 0:
        return f"Do not promote {plan_id}; post-freeze forward P&L is nonpositive and robustness gates are not close enough to rescue it."
    if failures:
        return f"Keep {plan_id} frozen as diagnostic-only; positive P&L is not enough until breadth, matched-v28, concentration, and sample gates clear together."
    return f"{plan_id} is forward-validated under the current narrow gates; next step would be a separate, pre-registered holdout audit."


def _terminal_recommendation(candidate_id: str, gate_results: Mapping[str, Any]) -> str:
    if gate_results.get("all_passed") is True:
        return f"{candidate_id} passes its linked OOS gate bundle; validate in a separate locked follow-up before any live consideration."
    return f"Do not promote {candidate_id}; headline P&L is positive, but the linked OOS robustness gates still fail."


def _overall_decision(rows: Iterable[Mapping[str, Any]]) -> str:
    verdicts = {str(row.get("verdict") or "") for row in rows}
    if not rows:
        return "no_positive_rv_candidates_found"
    if verdicts == {"forward_validated"}:
        return "all_positive_rv_candidates_forward_validated"
    return "positive_pnl_candidates_remain_blocked_or_underpowered"


def _blocking_gate_names(gates: Iterable[Mapping[str, Any]]) -> list[str]:
    return [
        str(gate.get("gate"))
        for gate in gates
        if gate.get("status") in {"fail", "missing"} and str(gate.get("gate")) != "registry_pnl_positive"
    ]


def _source_report_from_metric(root: Path, node: ProjectNode) -> Path | None:
    source_key = str((node.metrics or {}).get("net_pnl_source_key") or "")
    if not source_key or ".json" not in source_key:
        return None
    path_text = source_key.split(".json", 1)[0] + ".json"
    path = Path(path_text)
    return path if path.is_absolute() else root / path


def _is_rv_like(node: ProjectNode) -> bool:
    label = str(node.label or "").upper()
    text = " ".join([node.id, node.family, node.label, node.summary, node.path or ""]).upper()
    return node.family == "rv600" or label.startswith("RV") or "RVTERM" in text or "RV_" in text


def _node_path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def _load_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}


def _pass_fail(value: float | None, predicate) -> str:
    if value is None:
        return "missing"
    return "pass" if predicate(value) else "fail"


def _bool_status(value: Any) -> str:
    if value is None:
        return "missing"
    return "pass" if bool(value) else "fail"


def _num(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    numeric = _num(value)
    return int(numeric) if numeric is not None else None


def _rel(root: Path, path: Path | str | None) -> str:
    if not path:
        return ""
    path_obj = Path(path)
    try:
        return str(path_obj.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path_obj)


def _format_cents(value: Any) -> str:
    numeric = _num(value)
    if numeric is None:
        return "n/a"
    return f"{numeric:.2f}c"


def _display_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, dict):
        return "; ".join(f"{key}={_display_value(item)}" for key, item in value.items())
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _md(value: Any) -> str:
    return str(value if value is not None else "").replace("\n", " ").replace("\r", " ").replace("|", "\\|")


__all__ = [
    "DEFAULT_OUTPUT_JSON",
    "DEFAULT_OUTPUT_MD",
    "build_rv_positive_validation",
    "positive_rv_candidate_nodes",
    "render_rv_positive_validation_markdown",
    "write_rv_positive_validation",
]
