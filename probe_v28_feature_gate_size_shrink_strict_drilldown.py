"""Strict-forward drilldown for the closest feature-gate size-shrink lane.

Research-only; no live bot changes or orders.

The strict runway report says the closest broad-ish lane is the feature-gate
coverage repair with reduced notional on lower-abs-distance repair rows. This
probe classifies its current failures and source-quality runway at row level.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state, market, net, source
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule, raw_edge
from probe_v28_feature_gate_coverage_size_shrink import (
    ANCHOR_RULE,
    REPAIR_RULE,
    abs_d,
    ask_prob,
    classify,
    recross,
    repair_weight,
    row_key,
    selected,
)
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_size_shrink_strict_drilldown_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_size_shrink_strict_drilldown_latest.md"

POLICY = "repair_low_absd_quarter_else_half"
MAX_RECON_SHARE = 0.35
TARGET_COVERAGE_MIN = 0.75
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"


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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def is_settled(row: dict[str, Any]) -> bool:
    return isinstance(row.get("side_won"), bool)


def is_reconstructed(row: dict[str, Any]) -> bool:
    return source(row) != "approved_entry"


def failure_tags(row: dict[str, Any], anchor_keys: set[tuple[str, str]]) -> list[str]:
    tags: list[str] = []
    if row_key(row) in anchor_keys:
        tags.append("anchor_loss")
    else:
        tags.append("coverage_repair_loss")
    if is_reconstructed(row):
        tags.append("source_quality_error")
    if abs_d(row) < 0.75:
        tags.append("weak_boundary_distance")
    if recross(row) > 0.25:
        tags.append("moderate_recross_risk")
    if ask_prob(row) < 0.50:
        tags.append("cheap_or_midcheap_touch")
    if fnum(raw_edge(row)) < 0.08:
        tags.append("thin_raw_edge")
    if abs_d(row) >= 1.25 and fnum(raw_edge(row)) >= 0.15:
        tags.append("fv_or_market_regime_error")
    return tags


def row_view(row: dict[str, Any], anchor_keys: set[tuple[str, str]]) -> dict[str, Any]:
    weight = repair_weight(POLICY, row, anchor_keys)
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": net(row),
        "weight": weight,
        "weighted_net_cents": weight * net(row),
        "raw_edge": raw_edge(row),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "p_side": row.get("p_side"),
        "class": classify(row, anchor_keys),
        "failure_tags": failure_tags(row, anchor_keys) if net(row) < 0 else [],
    }


def clean_rows_needed_for_source(reconstructed: int, entries: int) -> int:
    if entries <= 0 or reconstructed / entries <= MAX_RECON_SHARE:
        return 0
    return int(math.ceil(reconstructed / MAX_RECON_SHARE - entries))


def clean_wins_needed_for_live(net_cents: float, live_cents: float) -> int:
    return int(max(0, math.ceil((live_cents - net_cents) / 100.0)))


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    rows, _, denominator_raw = entry_surfaces(freeze_ts)
    denominator = int(denominator_raw or 0)
    anchor_rows = selected(rows, ANCHOR_RULE)
    repair_rows = selected(rows, REPAIR_RULE)
    anchor_keys = {row_key(row) for row in anchor_rows}
    selected_rows = [row for row in repair_rows if repair_weight(POLICY, row, anchor_keys) > 0]
    selected_markets = {market(row) for row in selected_rows}

    settled_rows = [row for row in selected_rows if is_settled(row)]
    loss_rows = [row for row in settled_rows if net(row) < 0]
    win_rows = [row for row in settled_rows if net(row) > 0]
    reconstructed_rows = [row for row in selected_rows if is_reconstructed(row)]
    weighted_net = sum(repair_weight(POLICY, row, anchor_keys) * net(row) for row in settled_rows)
    live_cents = 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))
    omitted_settled = [
        row for row in rows
        if market(row) and market(row) not in selected_markets and is_settled(row)
    ]
    omitted_positive_approved = [row for row in omitted_settled if source(row) == "approved_entry" and net(row) > 0]
    omitted_positive_reconstructed = [row for row in omitted_settled if source(row) != "approved_entry" and net(row) > 0]
    loss_tag_counts = Counter(tag for row in loss_rows for tag in failure_tags(row, anchor_keys))
    class_counts = Counter(classify(row, anchor_keys) for row in selected_rows)
    class_weighted_net: Counter[str] = Counter()
    for row in settled_rows:
        class_weighted_net[classify(row, anchor_keys)] += repair_weight(POLICY, row, anchor_keys) * net(row)

    entries = len(selected_rows)
    reconstructed = len(reconstructed_rows)
    coverage = entries / denominator if denominator else 0.0
    blockers = []
    if coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if reconstructed / entries > MAX_RECON_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    if weighted_net < 300.0:
        blockers.append("full_loss_cushion_lt_3")
    if weighted_net <= live_cents:
        blockers.append("does_not_beat_refreshed_live_baseline")

    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "policy": POLICY,
        "denominator": denominator,
        "entries": entries,
        "settled": len(settled_rows),
        "wins": len(win_rows),
        "losses": len(loss_rows),
        "coverage_pct": 100.0 * coverage,
        "weighted_net_cents": weighted_net,
        "live_baseline_cents": live_cents,
        "delta_vs_live_cents": weighted_net - live_cents,
        "source_counts": dict(Counter(source(row) for row in selected_rows)),
        "reconstructed_share": reconstructed / entries if entries else None,
        "exposure_reconstructed_share": (
            sum(repair_weight(POLICY, row, anchor_keys) for row in reconstructed_rows)
            / sum(repair_weight(POLICY, row, anchor_keys) for row in selected_rows)
        ) if selected_rows else None,
        "clean_rows_needed_for_source": clean_rows_needed_for_source(reconstructed, entries),
        "clean_full_wins_needed_for_live": clean_wins_needed_for_live(weighted_net, live_cents),
        "blockers": blockers,
        "class_counts": dict(class_counts),
        "class_weighted_net_cents": dict(class_weighted_net),
        "loss_tag_counts": dict(loss_tag_counts),
        "loss_rows": [row_view(row, anchor_keys) for row in sorted(loss_rows, key=lambda item: repair_weight(POLICY, item, anchor_keys) * net(item))],
        "omitted_positive_approved_count": len(omitted_positive_approved),
        "omitted_positive_approved_net_cents": sum(net(row) for row in omitted_positive_approved),
        "omitted_positive_reconstructed_count": len(omitted_positive_reconstructed),
        "omitted_positive_reconstructed_net_cents": sum(net(row) for row in omitted_positive_reconstructed),
        "top_omitted_positive_rows": [
            row_view(row, anchor_keys)
            for row in sorted(omitted_settled, key=lambda item: net(item), reverse=True)[:20]
            if net(row) > 0
        ],
        "interpretation": [
            "Research-only strict-forward drilldown; no live bot changes or orders.",
            "The closest strict broad-ish lane clears settled count, net-positive, and three-full-loss cushion, but the latest denominator drift leaves it below the 75% coverage floor; it also still fails row-count source quality and refreshed live-baseline comparison.",
            "The current omitted positive pool is reconstructed-only, so source repair probably requires genuinely new clean approved future rows rather than an observable reshuffle of current rows.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Size-Shrink Strict Drilldown",
        "",
        "Research-only strict-forward drilldown. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Policy: `{report.get('policy')}`",
        f"- Entries/denominator: `{report.get('entries')}/{report.get('denominator')}`",
        f"- Settled W/L: `{report.get('wins')}/{report.get('losses')}`",
        f"- Coverage: `{fmt(report.get('coverage_pct'))}%`",
        f"- Weighted net: `{fmt(report.get('weighted_net_cents'))}c`",
        f"- Live baseline delta: `{fmt(report.get('delta_vs_live_cents'))}c`",
        f"- Source counts: `{report.get('source_counts')}`",
        f"- Reconstructed share: `{fmt(report.get('reconstructed_share'))}`",
        f"- Exposure reconstructed share: `{fmt(report.get('exposure_reconstructed_share'))}`",
        f"- Clean rows needed for source: `{report.get('clean_rows_needed_for_source')}`",
        f"- Clean full wins needed for live: `{report.get('clean_full_wins_needed_for_live')}`",
        f"- Blockers: `{report.get('blockers')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Loss Classes",
            "",
            f"- Loss tag counts: `{report.get('loss_tag_counts')}`",
            f"- Class weighted net: `{report.get('class_weighted_net_cents')}`",
            "",
            "| market | side | source | net | weight | weighted | class | tags | raw edge | abs d | recross | ask |",
            "|---|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("loss_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('weight'))} | {fmt(row.get('weighted_net_cents'))} | "
            f"{row.get('class')} | {row.get('failure_tags')} | {fmt(row.get('raw_edge'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {fmt(row.get('ask_prob'))} |"
        )
    lines.extend(
        [
            "",
            "## Omitted Positive Pool",
            "",
            f"- Omitted positive approved rows: `{report.get('omitted_positive_approved_count')}` / `{fmt(report.get('omitted_positive_approved_net_cents'))}c`",
            f"- Omitted positive reconstructed rows: `{report.get('omitted_positive_reconstructed_count')}` / `{fmt(report.get('omitted_positive_reconstructed_net_cents'))}c`",
            "",
            "| market | side | source | net | raw edge | abs d | recross | ask |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("top_omitted_positive_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('raw_edge'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {fmt(row.get('ask_prob'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
