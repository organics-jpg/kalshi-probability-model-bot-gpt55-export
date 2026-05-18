"""Stress audit for the boundary-clock feature-gate continuous penalty.

Research-only; no live bot changes or orders.

This is a derived audit over the continuous-penalty report. It measures source
split, top-win concentration, one/three full-loss sensitivity, and the clean-row
runway needed before the post-birth lane can clear promotion-style gates.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PENALTY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_stress_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_stress_latest.md"

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


def as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def net(row: dict[str, Any]) -> float:
    return float(row.get("net_cents") or 0.0)


def source(row: dict[str, Any]) -> str:
    label = str(row.get("source") or "")
    return label or "unknown"


def source_split(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[source(row)].append(row)
    out: dict[str, Any] = {}
    for label, group in sorted(groups.items()):
        row_net = sum(net(row) for row in group)
        out[label] = {
            "rows": len(group),
            "wins": sum(1 for row in group if row.get("side_won") is True),
            "losses": sum(1 for row in group if row.get("side_won") is False),
            "net_cents": row_net,
            "avg_net_cents": None if not group else row_net / len(group),
        }
    return out


def needed_for_coverage(entries: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    needed = 0
    while needed <= 1000:
        if 100.0 * (entries + needed) / (denominator + needed) >= MIN_COVERAGE:
            return needed
        needed += 1
    return needed


def needed_for_source_gate(reconstructed_count: int, selected_count: int) -> int:
    needed = 0
    while needed <= 1000:
        denom = selected_count + needed
        share = reconstructed_count / denom if denom else 0.0
        if share <= MAX_RECONSTRUCTED_SHARE:
            return needed
        needed += 1
    return needed


def blockers(
    settled: int,
    coverage_pct: float,
    reconstructed_share: float,
    net_cents: float,
    top_win_net: float,
) -> list[str]:
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
    if net_cents > 0.0 and top_win_net / max(abs(net_cents), 1.0) >= 0.50:
        out.append("top_win_concentration_ge_50pct_net")
    return out


def stress_variant(lane: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    summary = variant.get("candidate_summary") or {}
    rows = list(variant.get("rows") or [])
    entries = int(as_float(summary.get("entries")) or len(rows))
    settled = int(as_float(summary.get("settled")) or 0)
    denominator = int(as_float(lane.get("future_denominator")) or 0)
    coverage_pct = float(as_float(summary.get("coverage_pct")) or 0.0)
    net_cents = float(as_float(summary.get("net_cents")) or sum(net(row) for row in rows))
    reconstructed_count = sum(1 for row in rows if source(row) != "approved_entry")
    reconstructed_share = reconstructed_count / entries if entries else 0.0
    approved_rows = [row for row in rows if source(row) == "approved_entry"]
    reconstructed_rows = [row for row in rows if source(row) != "approved_entry"]
    sorted_by_net = sorted(rows, key=net, reverse=True)
    top_win = sorted_by_net[0] if sorted_by_net else {}
    worst_loss = min(rows, key=net) if rows else {}
    top_win_net = net(top_win) if top_win else 0.0
    source_rows_needed = needed_for_source_gate(reconstructed_count, entries)
    coverage_rows_needed = needed_for_coverage(entries, denominator)
    sample_rows_needed = max(0, MIN_SETTLED - settled)
    net_needed = max(0.0, MIN_FULL_LOSS_CUSHION_CENTS - net_cents)
    clean_rows_needed = max(source_rows_needed, coverage_rows_needed, sample_rows_needed)
    return {
        "lane": lane.get("lane"),
        "candidate": variant.get("candidate"),
        "future_denominator": denominator,
        "entries": entries,
        "settled": settled,
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "coverage_pct": coverage_pct,
        "net_cents": net_cents,
        "avg_net_cents": summary.get("avg_net_cents"),
        "source_counts": variant.get("source_counts") or dict(Counter(source(row) for row in rows)),
        "source_split": source_split(rows),
        "reconstructed_share": reconstructed_share,
        "approved_only_net_cents": sum(net(row) for row in approved_rows),
        "reconstructed_only_net_cents": sum(net(row) for row in reconstructed_rows),
        "top_win_net_cents": top_win_net,
        "top_win_net_share": None if net_cents == 0.0 else top_win_net / abs(net_cents),
        "net_without_top_win_cents": net_cents - top_win_net,
        "worst_loss_net_cents": net(worst_loss) if worst_loss else None,
        "net_after_one_full_loss_cents": net_cents - FULL_LOSS_CENTS,
        "net_after_three_full_losses_cents": net_cents - MIN_FULL_LOSS_CUSHION_CENTS,
        "max_full_losses_positive": int(max(0.0, net_cents) // FULL_LOSS_CENTS),
        "clean_rows_needed_for_coverage_gate": coverage_rows_needed,
        "clean_rows_needed_for_source_gate": source_rows_needed,
        "settled_rows_needed_for_sample_gate": sample_rows_needed,
        "net_cents_needed_for_cushion3": net_needed,
        "future_clean_selected_needed_for_all_count_gates": clean_rows_needed,
        "stress_blockers": blockers(settled, coverage_pct, reconstructed_share, net_cents, top_win_net),
        "top_win_row": top_win,
        "worst_loss_row": worst_loss,
    }


def stress_lane(lane: dict[str, Any]) -> dict[str, Any] | None:
    variants = lane.get("variants") or []
    if not variants:
        return None
    variant_stresses = [stress_variant(lane, variant) for variant in variants]
    best_by_gate = dict(variant_stresses[0])
    top_pnl = max(variant_stresses, key=lambda row: float(row.get("net_cents") or -999999.0))
    best_by_gate["variant_stresses"] = variant_stresses
    best_by_gate["top_pnl_candidate"] = top_pnl.get("candidate")
    best_by_gate["top_pnl_net_cents"] = top_pnl.get("net_cents")
    best_by_gate["top_pnl_coverage_pct"] = top_pnl.get("coverage_pct")
    best_by_gate["top_pnl_reconstructed_share"] = top_pnl.get("reconstructed_share")
    best_by_gate["top_pnl_stress_blockers"] = top_pnl.get("stress_blockers")
    return best_by_gate


def build_report() -> dict[str, Any]:
    penalty = load_json(PENALTY_JSON)
    lanes = []
    for lane in penalty.get("lanes") or []:
        stressed = stress_lane(lane)
        if stressed:
            lanes.append(stressed)
    report = {
        "generated_at_utc": utc_now_iso(),
        "penalty_generated_at_utc": penalty.get("generated_at_utc"),
        "penalty_freeze_ts_utc": (penalty.get("state") or {}).get("freeze_ts_utc"),
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a source/runway/outlier stress audit of the continuous cheap-side penalty; it is not promotion evidence.",
    ]
    for lane in report.get("lanes") or []:
        notes.append(
            f"{lane.get('lane')}: {lane.get('candidate')} has {lane.get('settled')} settled, "
            f"coverage {lane.get('coverage_pct')}%, net {lane.get('net_cents')}c, recon share "
            f"{lane.get('reconstructed_share')}; needs {lane.get('future_clean_selected_needed_for_all_count_gates')} "
            f"clean selected rows for count gates and {lane.get('net_cents_needed_for_cushion3')}c for cushion, "
            f"top win {lane.get('top_win_net_cents')}c leaves {lane.get('net_without_top_win_cents')}c without it, "
            f"top-PnL variant {lane.get('top_pnl_candidate')} nets {lane.get('top_pnl_net_cents')}c, "
            f"blockers {lane.get('stress_blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Continuous Penalty Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Penalty report generated UTC: `{report.get('penalty_generated_at_utc')}`",
        f"- Penalty freeze UTC: `{report.get('penalty_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Lanes",
        "",
        "| lane | candidate | selected/den | settled | W/L | coverage | net c | recon | approved net | recon net | top win | net ex top | clean rows needed | cushion c needed | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        lines.append(
            f"| {lane.get('lane')} | {lane.get('candidate')} | {lane.get('entries')}/{lane.get('future_denominator')} | "
            f"{lane.get('settled')} | {lane.get('wins')}/{lane.get('losses')} | {fmt(lane.get('coverage_pct'))} | "
            f"{fmt(lane.get('net_cents'))} | {fmt(lane.get('reconstructed_share'))} | "
            f"{fmt(lane.get('approved_only_net_cents'))} | {fmt(lane.get('reconstructed_only_net_cents'))} | "
            f"{fmt(lane.get('top_win_net_cents'))} | {fmt(lane.get('net_without_top_win_cents'))} | "
            f"{lane.get('future_clean_selected_needed_for_all_count_gates')} | "
            f"{fmt(lane.get('net_cents_needed_for_cushion3'))} | "
            f"{', '.join(lane.get('stress_blockers') or []) or 'none'} |"
        )
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')} Details", ""])
        lines.append(f"- Source split: `{lane.get('source_split')}`")
        lines.append(f"- Top win row: `{lane.get('top_win_row')}`")
        lines.append(f"- Worst loss row: `{lane.get('worst_loss_row')}`")
        lines.extend([
            "",
            "### Variant Stress",
            "",
            "| candidate | selected/den | coverage | net c | recon | clean rows needed | cushion c needed | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ])
        for variant in lane.get("variant_stresses") or []:
            lines.append(
                f"| {variant.get('candidate')} | {variant.get('entries')}/{variant.get('future_denominator')} | "
                f"{fmt(variant.get('coverage_pct'))} | {fmt(variant.get('net_cents'))} | "
                f"{fmt(variant.get('reconstructed_share'))} | "
                f"{variant.get('future_clean_selected_needed_for_all_count_gates')} | "
                f"{fmt(variant.get('net_cents_needed_for_cushion3'))} | "
                f"{', '.join(variant.get('stress_blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
