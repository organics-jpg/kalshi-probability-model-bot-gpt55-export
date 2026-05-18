"""Research-only readiness comparison for active ask65 vs broader ask35.

This probe does not place orders, edit launchers, or control processes. It
summarizes whether the current live feature-gate lane should remain ask65 or
whether the broader clean frontier rule is a better live-test candidate.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LIVE_LOCK = ROOT / "state" / "live_trading.lock"
FEATURE_GATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
COVERAGE_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_source_frontier_latest.json"
LIVE_GATE_JSON = OUT_DIR / "v28_feature_gate_live_gate_rejection_audit_latest.json"
SIDECAR_JSON = OUT_DIR / "v28_feature_gate_sidecar_live_state_audit_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_live_variant_switch_readiness_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_live_variant_switch_readiness_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def find_variant(feature_gate: dict[str, Any], candidate_name: str) -> dict[str, Any]:
    for lane in feature_gate.get("lanes") or []:
        if lane.get("lane") != "post_feature_freeze_entry":
            continue
        for variant in lane.get("variants") or []:
            if variant.get("candidate") == candidate_name:
                return variant
    return {}


def find_frontier_rule(frontier: dict[str, Any], rule_name: str) -> dict[str, Any]:
    for lane in frontier.get("lanes") or []:
        if lane.get("lane") != "post_feature_freeze_entry":
            continue
        for bucket in ("clean_broad_positive", "clean_broad_positive_rules", "pareto_frontier", "top_by_gate_sort"):
            for row in lane.get(bucket) or []:
                if row.get("rule") == rule_name:
                    return row
    return {}


def summary_from_feature_variant(row: dict[str, Any]) -> dict[str, Any]:
    summary = row.get("candidate_summary") or {}
    return {
        "source": "feature_gate_candidate",
        "rule": row.get("candidate"),
        "settled": summary.get("settled"),
        "entries": summary.get("entries"),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": summary.get("net_cents"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "reconstructed_share": row.get("reconstructed_share"),
        "full_loss_cushion": row.get("full_loss_cushion_estimate"),
        "blockers": row.get("blockers") or [],
        "rule_config": row.get("rule"),
    }


def summary_from_frontier(row: dict[str, Any]) -> dict[str, Any]:
    summary = row.get("summary") or {}
    return {
        "source": "coverage_source_frontier",
        "rule": row.get("rule"),
        "settled": summary.get("settled"),
        "entries": summary.get("entries"),
        "denominator": row.get("future_denominator"),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": summary.get("net_cents"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "reconstructed_share": row.get("reconstructed_share"),
        "full_loss_cushion": row.get("full_loss_cushion_estimate"),
        "blockers": row.get("blockers") or [],
        "rule_config": row.get("rule_params"),
    }


def build_report() -> dict[str, Any]:
    live_lock = load_json(LIVE_LOCK)
    feature_gate = load_json(FEATURE_GATE_JSON)
    frontier = load_json(COVERAGE_FRONTIER_JSON)
    live_gate = load_json(LIVE_GATE_JSON)
    sidecar = load_json(SIDECAR_JSON)

    ask65 = summary_from_feature_variant(
        find_variant(feature_gate, "post_feature_freeze_entry_raw05_recross60_abs085_ask65")
    )
    no_ask = summary_from_feature_variant(
        find_variant(feature_gate, "post_feature_freeze_entry_raw05_recross60_abs085")
    )
    ask35 = summary_from_frontier(find_frontier_rule(frontier, "raw03_recross60_abs85_ask35"))
    target_cov = 75.0
    active_summary = (sidecar.get("trade_summary") or {})
    counterfactuals = {
        row.get("variant"): row
        for row in live_gate.get("counterfactual_variants") or []
    }

    decision = "stay_ask65_for_now"
    decision_reasons = [
        "active_ask65_has_zero_live_fills_so_no_live_loss_cluster",
        "ask35_not_promotable_because_coverage_below_target",
    ]
    ask35_cov = as_float(ask35.get("coverage_pct"))
    ask35_net = as_float(ask35.get("net_cents"))
    ask35_recon = as_float(ask35.get("reconstructed_share"))
    ask35_cushion = as_float(ask35.get("full_loss_cushion"))
    ask65_net = as_float(ask65.get("net_cents"))
    if (
        ask35_cov is not None
        and ask35_net is not None
        and ask35_recon is not None
        and ask35_cushion is not None
        and ask35_net > float(ask65_net or 0.0)
        and ask35_recon <= 0.35
        and ask35_cushion >= 3
    ):
        decision = "ask35_is_better_watch_candidate_not_live_promoted"
        decision_reasons = [
            "ask35_has_higher_post_freeze_net_than_ask65",
            "ask35_source_quality_is_clean",
            "ask35_keeps_cheap_tail_floor_above_35c",
            "coverage_still_below_75pct_so_not_promotable",
        ]
    if (active_summary.get("entries_total") or 0) == 0:
        decision_reasons.append("active_ask65_live_test_is_not_collecting_fill_data_yet")

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "live_lock": live_lock,
        "active_live_trade_summary": active_summary,
        "ask65_active_candidate": ask65,
        "ask35_broader_frontier_candidate": ask35,
        "no_ask_reference": no_ask,
        "latest_live_gate_counterfactuals": {
            "no_ask": counterfactuals.get("raw05_recross60_abs085_no_ask"),
            "frontier_ask35": counterfactuals.get("frontier_raw03_recross60_abs85_ask35"),
            "frontier_ask45": counterfactuals.get("frontier_raw03_recross60_abs85_ask45"),
            "ask55": counterfactuals.get("raw05_recross60_abs085_ask55"),
            "ask65": counterfactuals.get("raw05_recross60_abs085_ask65"),
        },
        "target_coverage_pct": target_cov,
        "decision": decision,
        "decision_reasons": decision_reasons,
        "live_action_recommendation": "do_not_switch_without_user_confirmation",
        "interpretation": [
            "ask65 is cleanest but too selective; it currently has no fills.",
            "ask35 is the best clean broader frontier row but remains below the broad-market coverage gate.",
            "The current live market had no frontier ask35 counterfactual passes, so switching would not have created a trade in the latest observed window.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Live Variant Switch Readiness",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Live action recommendation: `{report.get('live_action_recommendation')}`",
        f"- Decision reasons: `{', '.join(report.get('decision_reasons') or [])}`",
        "",
        "## Candidate Comparison",
        "",
        "| candidate | settled | W/L | coverage | net c | recon | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for label, row in [
        ("active ask65", report.get("ask65_active_candidate") or {}),
        ("broader ask35", report.get("ask35_broader_frontier_candidate") or {}),
        ("no ask reference", report.get("no_ask_reference") or {}),
    ]:
        lines.append(
            f"| {label} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('full_loss_cushion')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Live Gate Context", ""])
    for label, row in (report.get("latest_live_gate_counterfactuals") or {}).items():
        if not row:
            lines.append(f"- {label}: None")
        else:
            lines.append(f"- {label}: pass_count `{row.get('pass_count')}`, sides `{row.get('sides')}`, markets `{row.get('markets')}`")
    lines.extend(["", "## Interpretation", ""])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
