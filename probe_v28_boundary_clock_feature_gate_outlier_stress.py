"""Outlier/source fragility stress for boundary-clock feature-gate frontier.

Research-only; no live bot changes or orders.

The feature-gate frontier can look positive while still depending on one
reconstructed or cheap-tail row. This probe measures top-win concentration,
source split PnL, leave-one-out damage, and full-loss cushion for the current
observable frontier rule.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import (
    OUT_JSON as FRONTIER_JSON,
    passes_rule,
)
from probe_v28_boundary_clock_feature_gate_frontier_mechanism import (
    compact_row,
    mechanism_tags,
)
from probe_v28_boundary_clock_feature_gate_candidate import best_per_market, load_or_create_state, market, net, source
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_outlier_stress_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_outlier_stress_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
FULL_LOSS_CENTS = 100.0
MIN_FULL_LOSS_CUSHION_CENTS = 300.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def frontier_rule(frontier: dict[str, Any], lane_name: str) -> dict[str, Any]:
    lane = next((row for row in frontier.get("lanes") or [] if row.get("lane") == lane_name), {})
    best = (lane.get("pareto_frontier") or [{}])[0]
    params = best.get("rule_params") or {}
    return {
        "rule": best.get("rule"),
        "rule_params": params,
        "summary": best.get("summary") or {},
        "reconstructed_share": best.get("reconstructed_share"),
        "frontier_blockers": best.get("blockers") or [],
    }


def selected_rows(rows: list[dict[str, Any]], rule: dict[str, Any]) -> list[dict[str, Any]]:
    return best_per_market([row for row in rows if passes_rule(row, rule)])


def source_split(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[source(row)].append(row)
    out: dict[str, Any] = {}
    for label, group in sorted(groups.items()):
        wins = sum(1 for row in group if row.get("side_won") is True)
        losses = sum(1 for row in group if row.get("side_won") is False)
        row_net = sum(net(row) for row in group)
        out[label] = {
            "rows": len(group),
            "wins": wins,
            "losses": losses,
            "net_cents": row_net,
            "avg_net_cents": None if not group else row_net / len(group),
        }
    return out


def blockers(settled: int, coverage_pct: float, reconstructed_share: float, net_cents: float) -> list[str]:
    out: list[str] = []
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage_pct < MIN_COVERAGE:
        out.append("coverage_too_low")
    if reconstructed_share > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if net_cents <= 0.0:
        out.append("net_not_positive")
    if net_cents < MIN_FULL_LOSS_CUSHION_CENTS:
        out.append("full_loss_cushion_lt_3")
    return out


def summarize_lane(label: str, surfaces_fn: Any, freeze_ts: str, frontier: dict[str, Any]) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    rule = frontier_rule(frontier, label)
    params = rule.get("rule_params") or {}
    selected = selected_rows(rows, params)
    settled = [row for row in selected if row.get("side_won") is not None]
    row_nets = [net(row) for row in selected]
    settled_nets = [net(row) for row in settled]
    selected_count = len(selected)
    denominator = int(denominator or 0)
    coverage_pct = (100.0 * selected_count / denominator) if denominator else 0.0
    total_net = sum(row_nets)
    reconstructed_count = sum(1 for row in selected if source(row) != "approved_entry")
    reconstructed_share = reconstructed_count / selected_count if selected_count else 0.0
    wins = sum(1 for row in selected if row.get("side_won") is True)
    losses = sum(1 for row in selected if row.get("side_won") is False)
    sorted_by_net = sorted(selected, key=lambda row: net(row), reverse=True)
    top_win = sorted_by_net[0] if sorted_by_net else {}
    worst_loss = sorted(selected, key=lambda row: net(row))[0] if selected else {}
    top_win_net = net(top_win) if top_win else 0.0
    leave_one_out_nets = [total_net - net(row) for row in selected]
    leave_one_out_min = min(leave_one_out_nets) if leave_one_out_nets else None
    approved_rows = [row for row in selected if source(row) == "approved_entry"]
    reconstructed_rows = [row for row in selected if source(row) != "approved_entry"]
    tag_counts = Counter(tag for row in selected for tag in mechanism_tags(row))
    stress_blockers = blockers(len(settled), coverage_pct, reconstructed_share, total_net)
    if selected and top_win_net / max(abs(total_net), 1.0) >= 0.50:
        stress_blockers.append("top_win_concentration_ge_50pct_net")
    if reconstructed_rows and sum(net(row) for row in approved_rows) <= 0.0:
        stress_blockers.append("approved_source_net_not_positive")
    return {
        "lane": label,
        "frontier_rule": rule.get("rule"),
        "rule_params": params,
        "future_denominator": denominator,
        "entries": selected_count,
        "settled": len(settled),
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage_pct,
        "net_cents": total_net,
        "avg_settled_net_cents": None if not settled_nets else sum(settled_nets) / len(settled_nets),
        "reconstructed_share": reconstructed_share,
        "source_counts": dict(Counter(source(row) for row in selected)),
        "source_split": source_split(selected),
        "approved_only_net_cents": sum(net(row) for row in approved_rows),
        "reconstructed_only_net_cents": sum(net(row) for row in reconstructed_rows),
        "top_win_net_cents": top_win_net,
        "top_win_net_share": None if total_net == 0.0 else top_win_net / abs(total_net),
        "net_without_top_win_cents": total_net - top_win_net,
        "worst_loss_net_cents": net(worst_loss) if worst_loss else None,
        "leave_one_out_min_net_cents": leave_one_out_min,
        "net_after_one_full_loss_cents": total_net - FULL_LOSS_CENTS,
        "net_after_three_full_losses_cents": total_net - MIN_FULL_LOSS_CUSHION_CENTS,
        "max_full_losses_positive": int(max(0.0, total_net) // FULL_LOSS_CENTS),
        "mechanism_tag_counts": dict(tag_counts),
        "stress_blockers": stress_blockers,
        "top_win_row": compact_row(top_win, params) if top_win else {},
        "worst_loss_row": compact_row(worst_loss, params) if worst_loss else {},
    }


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is an outlier/source stress audit of the current observable frontier; it is not promotion evidence.",
    ]
    for lane in report.get("lanes") or []:
        notes.append(
            f"{lane.get('lane')}: {lane.get('frontier_rule')} has {lane.get('settled')} settled, "
            f"coverage {lane.get('coverage_pct')}%, net {lane.get('net_cents')}c, recon share "
            f"{lane.get('reconstructed_share')}; top win {lane.get('top_win_net_cents')}c leaves "
            f"{lane.get('net_without_top_win_cents')}c without it, approved-only net "
            f"{lane.get('approved_only_net_cents')}c, reconstructed-only net "
            f"{lane.get('reconstructed_only_net_cents')}c, blockers {lane.get('stress_blockers')}."
        )
    return notes


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    frontier = load_json(FRONTIER_JSON)
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        summarize_lane("post_feature_freeze_entry", entry_surfaces, freeze_ts, frontier),
        summarize_lane("post_feature_freeze_bridge", bridge_surfaces, freeze_ts, frontier),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": freeze_ts,
        "frontier_generated_at_utc": frontier.get("generated_at_utc"),
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Outlier Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Frontier generated UTC: `{report.get('frontier_generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Lanes",
        "",
        "| lane | rule | selected/den | settled | W/L | coverage | net c | recon | approved net | reconstructed net | top win | net ex top | one full loss | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        lines.append(
            f"| {lane.get('lane')} | {lane.get('frontier_rule')} | {lane.get('entries')}/{lane.get('future_denominator')} | "
            f"{lane.get('settled')} | {lane.get('wins')}/{lane.get('losses')} | {fmt(lane.get('coverage_pct'))} | "
            f"{fmt(lane.get('net_cents'))} | {fmt(lane.get('reconstructed_share'))} | "
            f"{fmt(lane.get('approved_only_net_cents'))} | {fmt(lane.get('reconstructed_only_net_cents'))} | "
            f"{fmt(lane.get('top_win_net_cents'))} | {fmt(lane.get('net_without_top_win_cents'))} | "
            f"{fmt(lane.get('net_after_one_full_loss_cents'))} | {', '.join(lane.get('stress_blockers') or []) or 'none'} |"
        )
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')} Details", ""])
        lines.append(f"- Source split: `{lane.get('source_split')}`")
        lines.append(f"- Mechanism tags: `{lane.get('mechanism_tag_counts')}`")
        lines.append(f"- Top win row: `{lane.get('top_win_row')}`")
        lines.append(f"- Worst loss row: `{lane.get('worst_loss_row')}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
