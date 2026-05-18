"""Observable selection-mix audit for the v28 feature-gate repair branch.

Research-only; no live bot changes or orders.

The size-shrink branch is close to the promotion gates but fails row-count
source quality by a thin margin. This probe asks whether the issue comes from
the observable selection/ranking policy rather than from the physical signal
itself. Source labels are audit-only and are never used for row selection.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    as_float,
    load_or_create_state,
    market,
    net,
    source,
)
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule, raw_edge, rule_name
from probe_v28_feature_gate_coverage_size_shrink import (
    ANCHOR_RULE,
    REPAIR_RULE,
    ask_prob,
    repair_weight,
    row_key,
    summarize_policy,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_observable_selection_mix_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_observable_selection_mix_latest.md"

TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MID = 80.0
TARGET_COVERAGE_MAX = 90.0
POLICY = "repair_low_absd_quarter_else_half"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def recross(row: dict[str, Any]) -> float:
    return fnum(row.get("recross_hazard_score"), 1.0)


def abs_d(row: dict[str, Any]) -> float:
    return fnum(row.get("abs_d_sigma"))


def p_side(row: dict[str, Any]) -> float:
    return fnum(row.get("p_side"))


def score_raw_edge(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (fnum(raw_edge(row), -999.0), abs_d(row), -recross(row), str(row.get("ts_wall") or ""))


def score_absd_then_raw(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (abs_d(row), fnum(raw_edge(row), -999.0), -recross(row), str(row.get("ts_wall") or ""))


def score_low_recross_then_raw(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (-recross(row), fnum(raw_edge(row), -999.0), abs_d(row), str(row.get("ts_wall") or ""))


def score_edge_absd_recross(row: dict[str, Any]) -> tuple[float, float, float, str]:
    composite = fnum(raw_edge(row), -999.0) + 0.05 * abs_d(row) - 0.10 * recross(row)
    return (composite, fnum(raw_edge(row), -999.0), abs_d(row), str(row.get("ts_wall") or ""))


def score_edge_absd_cheap_penalty(row: dict[str, Any]) -> tuple[float, float, float, str]:
    cheap_penalty = max(0.0, 0.50 - ask_prob(row))
    composite = fnum(raw_edge(row), -999.0) + 0.04 * abs_d(row) - 0.08 * recross(row) - 0.06 * cheap_penalty
    return (composite, fnum(raw_edge(row), -999.0), abs_d(row), str(row.get("ts_wall") or ""))


def score_pside_absd_recross(row: dict[str, Any]) -> tuple[float, float, float, str]:
    composite = 0.60 * p_side(row) + 0.06 * abs_d(row) - 0.12 * recross(row)
    return (composite, fnum(raw_edge(row), -999.0), abs_d(row), str(row.get("ts_wall") or ""))


RANKERS: dict[str, Callable[[dict[str, Any]], tuple[Any, ...]]] = {
    "raw_edge": score_raw_edge,
    "absd_then_raw": score_absd_then_raw,
    "low_recross_then_raw": score_low_recross_then_raw,
    "edge_absd_recross": score_edge_absd_recross,
    "edge_absd_cheap_penalty": score_edge_absd_cheap_penalty,
    "pside_absd_recross": score_pside_absd_recross,
}


def selected_by_market(
    rows: list[dict[str, Any]],
    rule: dict[str, Any],
    ranker: Callable[[dict[str, Any]], tuple[Any, ...]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row) and passes_rule(row, rule):
            grouped[market(row)].append(row)
    return [max(items, key=ranker) for items in grouped.values()]


def ceil_for_coverage(denominator: int, pct: float) -> int:
    return int(math.ceil((pct / 100.0) * denominator))


def floor_for_coverage(denominator: int, pct: float) -> int:
    return int(math.floor((pct / 100.0) * denominator))


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def selected_row_view(row: dict[str, Any], anchor_keys: set[tuple[str, str]]) -> dict[str, Any]:
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": net(row),
        "weight": repair_weight(POLICY, row, anchor_keys),
        "raw_edge": raw_edge(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "anchor_row": row_key(row) in anchor_keys,
        "side_won": row.get("side_won"),
    }


def summarize_variant(
    lane: str,
    selection_family: str,
    ranker_name: str,
    rows: list[dict[str, Any]],
    denominator: int,
    anchor_keys: set[tuple[str, str]],
    control_by_market: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    summary = summarize_policy(lane, POLICY, rows, denominator, anchor_keys)
    changed_markets = []
    source_improvements = 0
    source_worsenings = 0
    control_net = 0.0
    variant_net = 0.0
    for row in rows:
        prior = control_by_market.get(market(row))
        if prior is None:
            continue
        control_net += repair_weight(POLICY, prior, anchor_keys) * net(prior)
        variant_net += repair_weight(POLICY, row, anchor_keys) * net(row)
        if row_key(row) == row_key(prior):
            continue
        was_recon = source(prior) != "approved_entry"
        now_recon = source(row) != "approved_entry"
        if was_recon and not now_recon:
            source_improvements += 1
        elif not was_recon and now_recon:
            source_worsenings += 1
        changed_markets.append({
            "market": market(row),
            "from": selected_row_view(prior, anchor_keys),
            "to": selected_row_view(row, anchor_keys),
        })
    summary.update({
        "selection_family": selection_family,
        "ranker": ranker_name,
        "candidate_id": f"{selection_family}_{ranker_name}",
        "source_counts": source_counts(rows),
        "selected_rows": [selected_row_view(row, anchor_keys) for row in rows],
        "changed_market_count_vs_raw_control": len(changed_markets),
        "source_improvements_vs_raw_control": source_improvements,
        "source_worsenings_vs_raw_control": source_worsenings,
        "changed_markets_vs_raw_control": changed_markets[:12],
        "shared_market_weighted_net_delta_vs_raw_control_cents": variant_net - control_net,
    })
    return summary


def anchor_plus_repairs(
    anchor_rows: list[dict[str, Any]],
    repair_pool: list[dict[str, Any]],
    target_entries: int,
    max_entries: int,
    ranker: Callable[[dict[str, Any]], tuple[Any, ...]],
) -> list[dict[str, Any]]:
    selected = list(anchor_rows)
    selected_markets = {market(row) for row in selected}
    candidates = [row for row in repair_pool if market(row) and market(row) not in selected_markets]
    candidates.sort(key=ranker, reverse=True)
    target = min(max_entries, max(target_entries, len(anchor_rows)))
    for row in candidates:
        if len(selected) >= target:
            break
        selected.append(row)
        selected_markets.add(market(row))
    return selected


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Callable[[str], Any]) -> dict[str, Any]:
    rows, _, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    min_entries = ceil_for_coverage(denominator, TARGET_COVERAGE_MIN)
    mid_entries = ceil_for_coverage(denominator, TARGET_COVERAGE_MID)
    max_entries = floor_for_coverage(denominator, TARGET_COVERAGE_MAX)
    anchor_rows = selected_by_market(rows, ANCHOR_RULE, score_raw_edge)
    anchor_keys = {row_key(row) for row in anchor_rows}
    raw_control = selected_by_market(rows, REPAIR_RULE, score_raw_edge)
    control_by_market = {market(row): row for row in raw_control}

    variants = []
    for ranker_name, ranker in RANKERS.items():
        same_market_rows = selected_by_market(rows, REPAIR_RULE, ranker)
        variants.append(summarize_variant(
            label,
            "same_market_repair_rule",
            ranker_name,
            same_market_rows,
            denominator,
            anchor_keys,
            control_by_market,
        ))
        repair_ranked = selected_by_market(rows, REPAIR_RULE, ranker)
        variants.append(summarize_variant(
            label,
            "anchor_plus_min_coverage_repairs",
            ranker_name,
            anchor_plus_repairs(anchor_rows, repair_ranked, min_entries, max_entries, ranker),
            denominator,
            anchor_keys,
            control_by_market,
        ))
        variants.append(summarize_variant(
            label,
            "anchor_plus_80pct_repairs",
            ranker_name,
            anchor_plus_repairs(anchor_rows, repair_ranked, mid_entries, max_entries, ranker),
            denominator,
            anchor_keys,
            control_by_market,
        ))
        variants.append(summarize_variant(
            label,
            "anchor_plus_max90_repairs",
            ranker_name,
            anchor_plus_repairs(anchor_rows, repair_ranked, max_entries, max_entries, ranker),
            denominator,
            anchor_keys,
            control_by_market,
        ))

    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -int(row.get("live_ready") is True),
            -float(row.get("weighted_net_cents") or -999999.0),
            float(row.get("row_reconstructed_share") or 1.0),
            -float(row.get("coverage_pct") or 0.0),
        )
    )
    return {
        "lane": label,
        "future_denominator": denominator,
        "anchor_rule": rule_name(ANCHOR_RULE),
        "repair_rule": rule_name(REPAIR_RULE),
        "policy": POLICY,
        "coverage_entry_targets": {
            "min75": min_entries,
            "mid80": mid_entries,
            "max90": max_entries,
        },
        "anchor_entries": len(anchor_rows),
        "raw_control_entries": len(raw_control),
        "raw_control_source_counts": source_counts(raw_control),
        "top_variants": variants[:24],
        "gate_clear_variants": [row for row in variants if row.get("live_ready")][:24],
        "variant_count": len(variants),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "purpose": "Test observable same-market rankers and anchor-plus-repair mixes for the near-gate feature branch.",
        "lanes": [
            evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
            evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
        ],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Selection variants use observable features only; source labels are audited after selection.",
    ]
    for lane in report.get("lanes") or []:
        clears = lane.get("gate_clear_variants") or []
        best = (lane.get("top_variants") or [{}])[0]
        if clears:
            first = clears[0]
            notes.append(
                f"{lane.get('lane')}: {len(clears)} variant(s) clear count/source/PnL/cushion gates. "
                f"Best clear {first.get('candidate_id')} has {first.get('entries')}/{lane.get('future_denominator')} entries, "
                f"W/L {first.get('wins')}/{first.get('losses')}, weighted net {first.get('weighted_net_cents')}c, "
                f"coverage {first.get('coverage_pct')}%, row recon {first.get('row_reconstructed_share')}."
            )
        else:
            notes.append(
                f"{lane.get('lane')}: no variant clears all gates. Best {best.get('candidate_id')} has "
                f"{best.get('entries')}/{lane.get('future_denominator')} entries, W/L {best.get('wins')}/{best.get('losses')}, "
                f"weighted net {best.get('weighted_net_cents')}c, row recon {best.get('row_reconstructed_share')}, "
                f"blockers {best.get('blockers')}."
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
        "# v28 Feature-Gate Observable Selection-Mix Audit",
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
            f"- Size policy: `{lane.get('policy')}`",
            f"- Anchor/control entries: `{lane.get('anchor_entries')}/{lane.get('raw_control_entries')}`",
            f"- Coverage entry targets: `{lane.get('coverage_entry_targets')}`",
            "",
            "| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | changes | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in lane.get("top_variants") or []:
            lines.append(
                f"| {row.get('candidate_id')} | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))}% | "
                f"{fmt(row.get('weighted_net_cents'))} | {fmt(row.get('row_reconstructed_share'))} | "
                f"{fmt(row.get('exposure_reconstructed_share'))} | {row.get('full_loss_cushion')} | "
                f"{row.get('changed_market_count_vs_raw_control')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_md(build_report())


if __name__ == "__main__":
    main()
