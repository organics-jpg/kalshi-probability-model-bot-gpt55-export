"""High raw/book-gap notional shrink diagnostic for feature-gate rows.

Research-only; no live bot changes or orders.

This probe does not freeze a new candidate. It reads the already-refreshed
boundary-clock feature-gate report and asks whether the high-gap mechanism seen
in approved-entry valve forensics is better represented as a continuous
notional penalty than as a hard veto. Source labels are audit-only.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_GATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_high_gap_shrink_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_high_gap_shrink_diagnostic_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
MAX_WEIGHTED_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

POLICIES = [
    "no_shrink_control",
    "gap30_mild_75",
    "gap30_half",
    "gap30_quarter",
    "gap30_linear_floor25",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def live_net_cents() -> float | None:
    summary = load_json(LIVE_SUMMARY_JSON)
    dollars = as_float(summary.get("net_pnl_total_dollars"))
    return None if dollars is None else round(dollars * 100.0, 6)


def raw_gap(row: dict[str, Any]) -> float:
    return as_float(row.get("raw_edge")) or 0.0


def net_cents(row: dict[str, Any]) -> float:
    return as_float(row.get("net_cents")) or 0.0


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def is_settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def row_weight(policy: str, row: dict[str, Any]) -> float:
    gap = raw_gap(row)
    if policy == "no_shrink_control" or gap < 0.30:
        return 1.0
    if policy == "gap30_mild_75":
        return 0.75
    if policy == "gap30_half":
        return 0.50
    if policy == "gap30_quarter":
        return 0.25
    if policy == "gap30_linear_floor25":
        # Start shrinking at 30pp raw/book gap and reach the 25% floor by 60pp.
        return max(0.25, 1.0 - 2.5 * (gap - 0.30))
    return 1.0


def compact_row(row: dict[str, Any], policy: str) -> dict[str, Any]:
    weight = row_weight(policy, row)
    return {
        "market": row.get("market"),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net_cents(row),
        "raw_gap": raw_gap(row),
        "ask_prob": as_float(row.get("ask_prob")),
        "recross_hazard_score": as_float(row.get("recross_hazard_score")),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "weight": weight,
        "weighted_net_cents": net_cents(row) * weight if is_settled(row) else None,
    }


def summarize_policy(policy: str, rows: list[dict[str, Any]], denominator: int, live_cents: float | None) -> dict[str, Any]:
    entries = len(rows)
    settled = [row for row in rows if is_settled(row)]
    high_gap = [row for row in rows if raw_gap(row) >= 0.30]
    weighted_net = 0.0
    exposure = 0.0
    rejected_exposure = 0.0
    rejected_rows = 0
    high_gap_weighted_net = 0.0
    high_gap_unweighted_net = 0.0
    high_gap_winner_cost = 0.0
    high_gap_loser_saved = 0.0
    for row in rows:
        weight = row_weight(policy, row)
        row_net = net_cents(row)
        exposure += weight
        if source(row) != "approved_entry":
            rejected_rows += 1
            rejected_exposure += weight
        if not is_settled(row):
            continue
        weighted_net += weight * row_net
        if raw_gap(row) >= 0.30:
            high_gap_unweighted_net += row_net
            high_gap_weighted_net += weight * row_net
            removed = (1.0 - weight) * row_net
            if row_net > 0:
                high_gap_winner_cost += removed
            elif row_net < 0:
                high_gap_loser_saved += -removed
    row_share = rejected_rows / entries if entries else 0.0
    exposure_share = rejected_exposure / exposure if exposure else 0.0
    coverage = 100.0 * entries / denominator if denominator else 0.0
    delta_vs_control = None
    delta_vs_live = None if live_cents is None else weighted_net - live_cents
    blockers: list[str] = []
    if len(settled) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage < MIN_COVERAGE:
        blockers.append("coverage_too_low")
    if coverage > MAX_COVERAGE:
        blockers.append("coverage_above_90pct")
    if weighted_net <= 0:
        blockers.append("weighted_net_not_positive")
    if row_share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    if exposure_share > MAX_WEIGHTED_RECONSTRUCTED_SHARE:
        blockers.append("weighted_reconstructed_share_gt_35pct")
    cushion = int(max(0.0, weighted_net) // 100.0)
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("weighted_full_loss_cushion_lt_3")
    if delta_vs_live is None or delta_vs_live <= 0:
        blockers.append("does_not_beat_refreshed_live_baseline")
    blockers.append("diagnostic_not_independently_frozen_candidate")

    return {
        "policy": policy,
        "entries": entries,
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": coverage,
        "weighted_net_cents": weighted_net,
        "delta_vs_control_cents": delta_vs_control,
        "delta_vs_live_cents": delta_vs_live,
        "row_reconstructed_share": row_share,
        "weighted_reconstructed_share": exposure_share,
        "notional_exposure_rows": exposure,
        "full_loss_cushion": cushion,
        "high_gap_rows": len(high_gap),
        "high_gap_settled": sum(1 for row in high_gap if is_settled(row)),
        "high_gap_wins": sum(1 for row in high_gap if row.get("side_won") is True),
        "high_gap_losses": sum(1 for row in high_gap if row.get("side_won") is False),
        "high_gap_unweighted_net_cents": high_gap_unweighted_net,
        "high_gap_weighted_net_cents": high_gap_weighted_net,
        "high_gap_winner_cost_cents": high_gap_winner_cost,
        "high_gap_loser_saved_cents": high_gap_loser_saved,
        "source_counts": dict(Counter(source(row) for row in rows)),
        "high_gap_source_counts": dict(Counter(source(row) for row in high_gap)),
        "blockers": blockers,
        "worst_rows": sorted([compact_row(row, policy) for row in rows], key=lambda item: item.get("weighted_net_cents") or 0.0)[:8],
        "high_gap_rows_detail": [compact_row(row, policy) for row in high_gap[:20]],
    }


def evaluate_variant(lane: dict[str, Any], variant: dict[str, Any], live_cents: float | None) -> dict[str, Any]:
    rows = list(variant.get("rows") or [])
    denominator = int(lane.get("future_denominator") or 0)
    policies = [summarize_policy(policy, rows, denominator, live_cents) for policy in POLICIES]
    control_net = next((row.get("weighted_net_cents") for row in policies if row.get("policy") == "no_shrink_control"), 0.0)
    for row in policies:
        row["delta_vs_control_cents"] = (as_float(row.get("weighted_net_cents")) or 0.0) - (as_float(control_net) or 0.0)
    policies.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("weighted_net_cents") or -999999.0),
            -float(row.get("delta_vs_control_cents") or -999999.0),
        )
    )
    return {
        "lane": lane.get("lane"),
        "candidate": variant.get("candidate"),
        "future_denominator": denominator,
        "base_summary": variant.get("candidate_summary") or {},
        "base_reconstructed_share": variant.get("reconstructed_share"),
        "policies": policies,
    }


def build_report() -> dict[str, Any]:
    feature = load_json(FEATURE_GATE_JSON)
    live_cents = live_net_cents()
    lanes = []
    for lane in feature.get("lanes") or []:
        variants = lane.get("variants") or []
        if not variants:
            continue
        best = variants[0]
        # Also keep the broad raw03 lane when it is not the top row because it
        # is the coverage-repair pressure point.
        wanted = [best]
        for variant in variants:
            if str(variant.get("candidate") or "").endswith("raw03_recross70_abs075") and variant not in wanted:
                wanted.append(variant)
        for variant in wanted:
            lanes.append(evaluate_variant(lane, variant, live_cents))
    return {
        "input_report": str(FEATURE_GATE_JSON),
        "live_net_cents": live_cents,
        "lanes": lanes,
        "promotion_ready_rows": [],
        "interpretation": interpretation(lanes, live_cents),
    }


def interpretation(lanes: list[dict[str, Any]], live_cents: float | None) -> list[str]:
    notes = [
        "This is a diagnostic notional-shrink replay on existing feature-gate rows, not a new frozen candidate.",
        f"Live baseline used for naive comparison is {live_cents}c.",
    ]
    best_delta = None
    for lane in lanes:
        policy = (lane.get("policies") or [{}])[0]
        delta = as_float(policy.get("delta_vs_control_cents"))
        if best_delta is None or (delta is not None and delta > as_float(best_delta.get("delta_vs_control_cents"))):
            best_delta = {
                "lane": lane.get("lane"),
                "candidate": lane.get("candidate"),
                "policy": policy.get("policy"),
                "delta_vs_control_cents": delta,
                "weighted_net_cents": policy.get("weighted_net_cents"),
                "blockers": policy.get("blockers"),
            }
    if best_delta:
        notes.append(
            f"Best shrink delta is {best_delta['policy']} on {best_delta['candidate']}: "
            f"{best_delta['delta_vs_control_cents']}c versus control, weighted net "
            f"{best_delta['weighted_net_cents']}c, blockers {best_delta['blockers']}."
        )
    notes.append(
        "Rows with large positive raw/book gaps include tail winners, so any useful repair must track winner cost explicitly."
    )
    return notes


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate High-Gap Shrink Diagnostic",
        "",
        "Research-only diagnostic; no live bot changes or orders.",
        "",
        f"- Input report: `{report.get('input_report')}`",
        f"- Live baseline net: `{fmt(report.get('live_net_cents'))}c`",
        f"- Evaluated lane/variant rows: `{len(report.get('lanes') or [])}`",
        "- Promotion-ready rows: `0`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')} / {lane.get('candidate')}",
            "",
            f"- Future denominator: `{lane.get('future_denominator')}`",
            f"- Base reconstructed share: `{fmt(lane.get('base_reconstructed_share'))}`",
            "",
            "| rank | policy | settled | W/L | coverage | weighted net | delta vs control | delta vs live | row recon | weighted recon | high-gap W/L/net | winner cost | loser saved | cushion | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(lane.get("policies") or [], start=1):
            lines.append(
                f"| {idx} | `{row.get('policy')}` | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
                f"{fmt(row.get('weighted_net_cents'))} | {fmt(row.get('delta_vs_control_cents'))} | "
                f"{fmt(row.get('delta_vs_live_cents'))} | {fmt(row.get('row_reconstructed_share'))} | "
                f"{fmt(row.get('weighted_reconstructed_share'))} | "
                f"{row.get('high_gap_wins')}/{row.get('high_gap_losses')}/{fmt(row.get('high_gap_unweighted_net_cents'))} | "
                f"{fmt(row.get('high_gap_winner_cost_cents'))} | {fmt(row.get('high_gap_loser_saved_cents'))} | "
                f"{row.get('full_loss_cushion')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
        best = (lane.get("policies") or [{}])[0]
        lines.extend([
            "",
            "### High-Gap Rows For Best Policy",
            "",
            "| market | source | side | won | net c | gap | weight | weighted c | ask | recross | abs d |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in best.get("high_gap_rows_detail") or []:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('source')}` | `{row.get('side')}` | "
                f"{row.get('side_won')} | {fmt(row.get('net_cents'))} | {fmt(row.get('raw_gap'))} | "
                f"{fmt(row.get('weight'))} | {fmt(row.get('weighted_net_cents'))} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
