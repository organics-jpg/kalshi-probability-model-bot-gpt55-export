"""Size-shrink audit for feature-gate coverage repair rows.

Research-only; no live bot changes or orders.

The prior coverage-repair audit showed that simple observable relaxations buy
coverage by adding lower-abs-distance, source-fragile rows. This probe keeps the
near-promotion anchor at full notional and tests reduced notional on the extra
coverage rows selected by the nearest observable repair rule.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    as_float,
    best_per_market,
    blockers,
    load_or_create_state,
    market,
    net,
    reconstructed_share,
    source,
)
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule, rule_name
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.md"

TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECON_SHARE = 0.35
MIN_SETTLED = 30
MIN_CUSHION = 3

ANCHOR_RULE = {
    "raw_edge_min": 0.05,
    "recross_max": 0.60,
    "abs_d_min": 0.85,
    "ask_min": None,
}

REPAIR_RULE = {
    "raw_edge_min": 0.03,
    "recross_max": 0.50,
    "abs_d_min": 0.50,
    "ask_min": 0.35,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("market") or ""), str(row.get("side") or "")


def is_settled(row: dict[str, Any]) -> bool:
    return isinstance(row.get("side_won"), bool)


def is_reconstructed(row: dict[str, Any]) -> bool:
    return source(row) != "approved_entry"


def ask_prob(row: dict[str, Any]) -> float:
    return fnum(row.get("ask_prob"))


def abs_d(row: dict[str, Any]) -> float:
    return fnum(row.get("abs_d_sigma"))


def recross(row: dict[str, Any]) -> float:
    return fnum(row.get("recross_hazard_score"), 1.0)


def classify(row: dict[str, Any], anchor_keys: set[tuple[str, str]]) -> str:
    if row_key(row) in anchor_keys:
        return "anchor"
    tags: list[str] = ["coverage_repair"]
    if abs_d(row) < 0.85:
        tags.append("lower_abs_d")
    if recross(row) > 0.30:
        tags.append("recross_risk")
    if ask_prob(row) < 0.50:
        tags.append("mid_cheap")
    if is_reconstructed(row):
        tags.append("source_fragile")
    return "+".join(tags)


def selected(rows: list[dict[str, Any]], rule: dict[str, Any]) -> list[dict[str, Any]]:
    return best_per_market([row for row in rows if passes_rule(row, rule)])


def repair_weight(policy: str, row: dict[str, Any], anchor_keys: set[tuple[str, str]]) -> float:
    if row_key(row) in anchor_keys:
        return 1.0
    row_abs = abs_d(row)
    row_recross = recross(row)
    row_ask = ask_prob(row)

    if policy == "repair_full_control":
        return 1.0
    if policy == "repair_half":
        return 0.5
    if policy == "repair_quarter":
        return 0.25
    if policy == "repair_eighth":
        return 0.125
    if policy == "repair_absd_linear":
        return max(0.10, min(0.75, row_abs / 0.85))
    if policy == "repair_absd_squared":
        return max(0.05, min(0.75, (row_abs / 0.85) ** 2))
    if policy == "repair_absd_recross_scaled":
        recross_scale = 0.5 if row_recross > 0.30 else 1.0
        return max(0.05, min(0.75, (row_abs / 0.85) ** 2 * recross_scale))
    if policy == "repair_midcheap_quarter_else_half":
        return 0.25 if row_ask < 0.50 else 0.5
    if policy == "repair_low_absd_quarter_else_half":
        return 0.25 if row_abs < 0.75 else 0.5
    if policy == "repair_low_absd_recross_eighth_else_half":
        return 0.125 if row_abs < 0.75 and row_recross > 0.30 else 0.5
    return 0.0


def summarize_policy(
    lane: str,
    policy: str,
    rows: list[dict[str, Any]],
    denominator: int,
    anchor_keys: set[tuple[str, str]],
) -> dict[str, Any]:
    entries = 0
    settled = 0
    wins = 0
    losses = 0
    weighted_net = 0.0
    weight_sum = 0.0
    source_weight = 0.0
    row_source_count = 0
    class_counts: Counter[str] = Counter()
    class_weight: Counter[str] = Counter()
    class_net: Counter[str] = Counter()
    worst_rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []

    for row in rows:
        weight = repair_weight(policy, row, anchor_keys)
        if weight <= 0:
            continue
        entries += 1
        weight_sum += weight
        cls = classify(row, anchor_keys)
        class_counts[cls] += 1
        class_weight[cls] += weight
        if is_reconstructed(row):
            row_source_count += 1
            source_weight += weight
        selected_row = {
            "market": market(row),
            "side": row.get("side"),
            "source": source(row),
            "approved": not is_reconstructed(row),
            "settled": is_settled(row),
            "raw_net_cents": net(row) if is_settled(row) else None,
            "weight": weight,
            "weighted_net_cents": weight * net(row) if is_settled(row) else None,
            "is_anchor": row_key(row) in anchor_keys,
            "ask_prob": row.get("ask_prob"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
        }
        selected_rows.append(selected_row)
        if is_settled(row):
            row_net = net(row)
            settled += 1
            weighted_net += weight * row_net
            class_net[cls] += weight * row_net
            if row_net > 0:
                wins += 1
            elif row_net < 0:
                losses += 1
            if row_net < 0:
                worst_rows.append({
                    "market": market(row),
                    "side": row.get("side"),
                    "source": source(row),
                    "net_cents": row_net,
                    "weight": weight,
                    "weighted_net_cents": row_net * weight,
                    "ask_prob": row.get("ask_prob"),
                    "abs_d_sigma": row.get("abs_d_sigma"),
                    "recross_hazard_score": row.get("recross_hazard_score"),
                    "class": cls,
                })

    coverage = 100.0 * entries / denominator if denominator else 0.0
    row_recon_share = row_source_count / entries if entries else 0.0
    exposure_recon_share = source_weight / weight_sum if weight_sum else 0.0
    cushion = int(max(0.0, weighted_net) // 100.0)
    required_entries = math.ceil(TARGET_COVERAGE_MIN * denominator / 100.0)
    clean_rows_needed = 0
    while entries + clean_rows_needed > 0 and (
        row_source_count / (entries + clean_rows_needed)
    ) > MAX_RECON_SHARE:
        clean_rows_needed += 1

    row_blockers: list[str] = []
    if settled < MIN_SETTLED:
        row_blockers.append("settled_lt_30")
    if coverage < TARGET_COVERAGE_MIN:
        row_blockers.append("coverage_too_low")
    if coverage > TARGET_COVERAGE_MAX:
        row_blockers.append("coverage_too_high")
    if row_recon_share > MAX_RECON_SHARE:
        row_blockers.append("row_reconstructed_share_gt_35pct")
    if exposure_recon_share > MAX_RECON_SHARE:
        row_blockers.append("exposure_reconstructed_share_gt_35pct")
    if weighted_net <= 0:
        row_blockers.append("weighted_net_not_positive")
    if cushion < MIN_CUSHION:
        row_blockers.append("weighted_full_loss_cushion_lt_3")

    return {
        "lane": lane,
        "policy": policy,
        "entries": entries,
        "settled": settled,
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "weighted_net_cents": weighted_net,
        "avg_weighted_net_cents": weighted_net / settled if settled else 0.0,
        "row_reconstructed_share": row_recon_share,
        "exposure_reconstructed_share": exposure_recon_share,
        "full_loss_cushion": cushion,
        "coverage_entries_needed": max(0, required_entries - entries),
        "clean_rows_needed_for_source": clean_rows_needed,
        "net_cents_needed_for_cushion3": max(0.0, 300.0 - weighted_net),
        "blockers": row_blockers,
        "live_ready": not row_blockers,
        "class_counts": dict(class_counts),
        "class_weight": dict(class_weight),
        "class_weighted_net_cents": dict(class_net),
        "selected_rows": selected_rows,
        "worst_rows": sorted(worst_rows, key=lambda item: item["weighted_net_cents"])[:8],
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Callable[[str], Any]) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    denominator = int(denominator or 0)
    anchor_rows = selected(rows, ANCHOR_RULE)
    repair_rows = selected(rows, REPAIR_RULE)
    anchor_keys = {row_key(row) for row in anchor_rows}
    policies = [
        "repair_full_control",
        "repair_half",
        "repair_quarter",
        "repair_eighth",
        "repair_absd_linear",
        "repair_absd_squared",
        "repair_absd_recross_scaled",
        "repair_midcheap_quarter_else_half",
        "repair_low_absd_quarter_else_half",
        "repair_low_absd_recross_eighth_else_half",
    ]
    summaries = [summarize_policy(label, policy, repair_rows, denominator, anchor_keys) for policy in policies]
    summaries.sort(
        key=lambda row: (
            len(row["blockers"]),
            row["clean_rows_needed_for_source"],
            row["net_cents_needed_for_cushion3"],
            -float(row["weighted_net_cents"]),
        )
    )
    return {
        "lane": label,
        "future_denominator": denominator,
        "anchor_rule": rule_name(ANCHOR_RULE),
        "repair_rule": rule_name(REPAIR_RULE),
        "anchor_entries": len(anchor_rows),
        "repair_entries": len(repair_rows),
        "added_entries": len([row for row in repair_rows if row_key(row) not in anchor_keys]),
        "rows": summaries,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "purpose": "Test reduced notional on coverage-repair rows while keeping the raw05 anchor full size.",
        "lanes": [
            evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
            evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
        ],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a size/portfolio audit only; row-count source gates still matter for promotion.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("rows") or [{}])[0]
        notes.append(
            f"{lane.get('lane')}: best policy {best.get('policy')} has "
            f"{best.get('entries')}/{lane.get('future_denominator')} entries, "
            f"{best.get('settled')} settled, W/L {best.get('wins')}/{best.get('losses')}, "
            f"weighted net {best.get('weighted_net_cents')}c, row/exposure recon "
            f"{best.get('row_reconstructed_share')}/{best.get('exposure_reconstructed_share')}, "
            f"cushion {best.get('full_loss_cushion')}, blockers {best.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Coverage Size-Shrink Audit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Anchor rule: `{lane.get('anchor_rule')}`",
            f"- Repair rule: `{lane.get('repair_rule')}`",
            f"- Anchor/repair/added entries: `{lane.get('anchor_entries')}/{lane.get('repair_entries')}/{lane.get('added_entries')}`",
            "",
            "| policy | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | needs | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ])
        for row in lane.get("rows") or []:
            needs = (
                f"cov {row.get('coverage_entries_needed')}, "
                f"clean {row.get('clean_rows_needed_for_source')}, "
                f"cushion {fmt(row.get('net_cents_needed_for_cushion3'))}c"
            )
            lines.append(
                f"| {row.get('policy')} | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))}% | "
                f"{fmt(row.get('weighted_net_cents'))} | {fmt(row.get('row_reconstructed_share'))} | "
                f"{fmt(row.get('exposure_reconstructed_share'))} | {row.get('full_loss_cushion')} | "
                f"{needs} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_md(build_report())


if __name__ == "__main__":
    main()
