"""Mix/match audit for top v28 candidate families.

Research-only. This tests whether the current top PnL and top win-rate lanes
are mechanically compatible as an entry/exit stack or as a dual strategy.
It writes diagnostic evidence only; it does not alter live bot behavior.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
EXIT_REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
EXIT_BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_V2_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json"
EXIT_BOOK_GAP_LOSS_GUARD_V3_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json"
EXIT_BOOK_GAP_VALUE_ONLY_JSON = OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json"
EXIT_VALUE_REDUCE_DEPTH_COMPOSITE_JSON = OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json"
EXIT_OBSERVABLE_LOSS_CONTROL_JSON = OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json"
EXIT_OBSERVABLE_LOSS_CONTROL_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_observable_loss_control_opportunity_latest.json"
EXIT_MIDBAND_REDUCE_RESCUE_JSON = OUT_DIR / "v28_frozen_exit_midband_reduce_rescue_watch_latest.json"
EXIT_YES_REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.json"
EXIT_GEOMETRY_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_latest.json"
FEATURE_GATE_LEDGER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_row_ledger_latest.json"
FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON = OUT_DIR / "v28_frozen_feature_gate_soft_frontier_exit_stack_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json"
RMT_JSON = OUT_DIR / "v28_rmt_forgetting_entry_bakeoff_latest.json"
SIDECAR_JSON = OUT_DIR / "v28_sidecar_live_test_watch_latest.json"
OUT_JSON = OUT_DIR / "v28_top_candidate_mix_match_latest.json"
OUT_MD = OUT_DIR / "v28_top_candidate_mix_match_latest.md"

FORGETTING_GATES = {
    "rmt_forgetting_entry_bakeoff",
    "path_rmt_forward_gate",
    "boundary_memory_fv",
    "phi_forgetting_fv",
    "reward_memory_fv",
}

CATASTROPHIC_FV_GATES = {
    "boundary_memory_fv",
    "phi_forgetting_fv",
    "reward_memory_fv",
}


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


def row_net(row: dict[str, Any], *fields: str) -> float:
    for field in fields:
        value = as_float(row.get(field))
        if value is not None:
            return value
    return 0.0


def exit_key(row: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (row.get("market"), row.get("side"), row.get("entry_ts"))


def market_side_key(row: dict[str, Any]) -> tuple[Any, Any]:
    return (row.get("market"), row.get("side"))


def summarize_rows(rows: list[dict[str, Any]], net_field: str) -> dict[str, Any]:
    nets = [row_net(row, net_field, "candidate_net_cents", "candidate_cents") for row in rows]
    return {
        "rows": len(rows),
        "net_cents": sum(nets),
        "wins": sum(1 for value in nets if value > 0),
        "losses": sum(1 for value in nets if value < 0),
        "flat": sum(1 for value in nets if value == 0),
    }


def top_tracker_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [
        row for row in rows
        if row.get("has_settled_pnl") and as_float(row.get("net_cents_after_entry_fee")) is not None
    ]
    by_pnl = sorted(settled, key=lambda row: as_float(row.get("net_cents_after_entry_fee")) or -999999.0, reverse=True)
    by_win = sorted(
        [
            row for row in settled
            if as_float(row.get("settled")) and as_float(row.get("wins")) is not None and as_float(row.get("losses")) is not None
            and (as_float(row.get("settled")) or 0.0) >= 10
        ],
        key=lambda row: (
            (as_float(row.get("wins")) or 0.0) / max((as_float(row.get("wins")) or 0.0) + (as_float(row.get("losses")) or 0.0), 1.0),
            as_float(row.get("net_cents_after_entry_fee")) or -999999.0,
        ),
        reverse=True,
    )
    return {
        "top_pnl": by_pnl[:12],
        "top_win_rate_min10": by_win[:12],
    }


def tracker_family_top(rows: list[dict[str, Any]], gates: set[str], limit: int = 12) -> list[dict[str, Any]]:
    family_rows = [
        row for row in rows
        if row.get("gate") in gates
        and row.get("has_settled_pnl")
        and as_float(row.get("net_cents_after_entry_fee")) is not None
    ]
    return sorted(
        family_rows,
        key=lambda row: (
            as_float(row.get("net_cents_after_entry_fee")) or -999999.0,
            as_float(row.get("settled")) or 0.0,
        ),
        reverse=True,
    )[:limit]


def exit_policy_mix() -> dict[str, Any]:
    reduce_rows = load_json(EXIT_REDUCE_JSON).get("rows") or []
    book_rows = load_json(EXIT_BOOK_GAP_JSON).get("rows") or []
    loss_guard = load_json(EXIT_BOOK_GAP_LOSS_GUARD_JSON)
    loss_guard_v2 = load_json(EXIT_BOOK_GAP_LOSS_GUARD_V2_JSON)
    loss_guard_v3 = load_json(EXIT_BOOK_GAP_LOSS_GUARD_V3_JSON)
    value_only = load_json(EXIT_BOOK_GAP_VALUE_ONLY_JSON)
    value_reduce_depth = load_json(EXIT_VALUE_REDUCE_DEPTH_COMPOSITE_JSON)
    observable_loss_control = load_json(EXIT_OBSERVABLE_LOSS_CONTROL_JSON)
    observable_loss_control_opportunity = load_json(EXIT_OBSERVABLE_LOSS_CONTROL_OPPORTUNITY_JSON)
    midband_reduce_rescue = load_json(EXIT_MIDBAND_REDUCE_RESCUE_JSON)
    yes_rows = load_json(EXIT_YES_REDUCE_JSON).get("rows") or []
    geometry_rows = load_json(EXIT_GEOMETRY_JSON).get("rows") or []
    policies = {
        "reduce": {exit_key(row): row for row in reduce_rows},
        "book_gap": {exit_key(row): row for row in book_rows},
        "yes_reduce": {exit_key(row): row for row in yes_rows},
        "geometry": {exit_key(row): row for row in geometry_rows},
    }
    common_reduce_book = sorted(set(policies["reduce"]) & set(policies["book_gap"]))
    reduce_only = sorted(set(policies["reduce"]) - set(policies["book_gap"]))
    book_else_reduce_rows = [policies["book_gap"][key] for key in common_reduce_book] + [
        policies["reduce"][key] for key in reduce_only
    ]
    pairwise = []
    for left, right in (("reduce", "book_gap"), ("reduce", "yes_reduce"), ("reduce", "geometry"), ("book_gap", "geometry")):
        common = sorted(set(policies[left]) & set(policies[right]))
        pairwise.append({
            "left": left,
            "right": right,
            "common_rows": len(common),
            "left_net_cents": sum(row_net(policies[left][key], "candidate_cents", "candidate_net_cents") for key in common),
            "right_net_cents": sum(row_net(policies[right][key], "candidate_cents", "candidate_net_cents") for key in common),
            "current_net_cents": sum(row_net(policies[left][key], "current_cents", "current_net_cents") for key in common),
        })
    observable_lanes = observable_loss_control.get("lanes") or []
    observable_diag = next((lane for lane in observable_lanes if lane.get("lane") == "diagnostic_from_reduce_freeze"), {})
    observable_post = next((lane for lane in observable_lanes if lane.get("lane") == "post_observable_birth"), {})
    observable_diag_best = (observable_diag.get("variants") or [{}])[0]
    observable_post_best = (observable_post.get("variants") or [{}])[0]
    observable_opportunity_rules = observable_loss_control_opportunity.get("rules") or []
    return {
        "policy_counts": {name: len(rows) for name, rows in policies.items()},
        "reduce": summarize_rows(list(policies["reduce"].values()), "candidate_cents"),
        "book_gap": summarize_rows(list(policies["book_gap"].values()), "candidate_cents"),
        "yes_reduce": summarize_rows(list(policies["yes_reduce"].values()), "candidate_cents"),
        "geometry": summarize_rows(list(policies["geometry"].values()), "candidate_cents"),
        "book_gap_loss_guard": {
            "forward": loss_guard.get("summary") or {},
            "discovery_all_exit_rows": loss_guard.get("discovery_summary_existing_exit_sample") or {},
            "discovery_comparable_book_gap_freeze": loss_guard.get("discovery_summary_comparable_book_gap_freeze_sample") or {},
            "freeze": loss_guard.get("freeze") or {},
            "blockers": loss_guard.get("blockers") or [],
        },
        "book_gap_loss_guard_v2": {
            "forward": loss_guard_v2.get("summary") or {},
            "discovery_all_exit_rows": loss_guard_v2.get("discovery_summary_existing_exit_sample") or {},
            "discovery_comparable_book_gap_freeze": loss_guard_v2.get("discovery_summary_comparable_book_gap_freeze_sample") or {},
            "freeze": loss_guard_v2.get("freeze") or {},
            "blockers": loss_guard_v2.get("blockers") or [],
        },
        "book_gap_loss_guard_v3": {
            "forward": loss_guard_v3.get("summary") or {},
            "discovery_all_exit_rows": loss_guard_v3.get("discovery_summary_existing_exit_sample") or {},
            "discovery_comparable_book_gap_freeze": loss_guard_v3.get("discovery_summary_comparable_book_gap_freeze_sample") or {},
            "freeze": loss_guard_v3.get("freeze") or {},
            "blockers": loss_guard_v3.get("blockers") or [],
        },
        "book_gap_value_only": {
            "forward": value_only.get("summary") or {},
            "diagnostic": next(
                (
                    lane for lane in value_only.get("lanes") or []
                    if lane.get("lane") == "diagnostic_from_book_gap_freeze"
                ),
                {},
            ),
            "freeze": value_only.get("freeze") or {},
            "blockers": value_only.get("blockers") or [],
        },
        "value_reduce_depth_composite": {
            "forward": value_reduce_depth.get("summary") or {},
            "diagnostic": next(
                (
                    lane for lane in value_reduce_depth.get("lanes") or []
                    if lane.get("lane") == "diagnostic_from_exit_freezes"
                ),
                {},
            ),
            "freeze": value_reduce_depth.get("freeze") or {},
            "blockers": value_reduce_depth.get("blockers") or [],
        },
        "observable_loss_control": {
            "freeze_ts_utc": (observable_loss_control.get("state") or {}).get("freeze_ts_utc"),
            "diagnostic": observable_diag_best,
            "post_birth": observable_post_best,
            "opportunity": observable_opportunity_rules[0] if observable_opportunity_rules else {},
        },
        "midband_reduce_rescue": {
            "freeze_ts_utc": (midband_reduce_rescue.get("state") or {}).get("freeze_ts_utc"),
            "diagnostic_best": (midband_reduce_rescue.get("diagnostic") or [{}])[0],
            "post_birth_best": (midband_reduce_rescue.get("post_birth") or [{}])[0],
            "diagnostic_rows": midband_reduce_rescue.get("diagnostic_rows"),
            "post_birth_rows": midband_reduce_rescue.get("post_birth_rows"),
        },
        "book_gap_else_reduce": {
            **summarize_rows(book_else_reduce_rows, "candidate_cents"),
            "common_book_gap_rows": len(common_reduce_book),
            "reduce_only_rows": len(reduce_only),
            "current_net_cents": (
                sum(row_net(policies["book_gap"][key], "current_cents", "current_net_cents") for key in common_reduce_book)
                + sum(row_net(policies["reduce"][key], "current_cents", "current_net_cents") for key in reduce_only)
            ),
            "status": "diagnostic_composite_needs_fresh_freeze",
        },
        "pairwise_common_windows": pairwise,
    }


def feature_gate_exit_overlap() -> list[dict[str, Any]]:
    ledger = load_json(FEATURE_GATE_LEDGER_JSON)
    reduce_rows = load_json(EXIT_REDUCE_JSON).get("rows") or []
    book_rows = load_json(EXIT_BOOK_GAP_JSON).get("rows") or []
    exits_by_market_side: dict[tuple[Any, Any], list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for row in reduce_rows:
        exits_by_market_side[market_side_key(row)].append(("reduce", row))
    for row in book_rows:
        exits_by_market_side[market_side_key(row)].append(("book_gap", row))

    out: list[dict[str, Any]] = []
    for lane in ledger.get("lanes") or []:
        lane_name = lane.get("lane")
        if lane_name not in {"post_feature_freeze_entry", "post_feature_freeze_bridge"}:
            continue
        for rule in lane.get("rules") or []:
            selected = rule.get("selected_rows") or []
            joined: list[tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]] = []
            ambiguous = 0
            for selected_row in selected:
                candidates = [item for item in exits_by_market_side.get(market_side_key(selected_row), []) if item[1].get("entry_ts")]
                entry_ts_set = {item[1].get("entry_ts") for item in candidates}
                if len(entry_ts_set) > 1:
                    ambiguous += 1
                    continue
                if candidates:
                    joined.append((selected_row, candidates))
            approved = sum(1 for row in selected if row.get("source") == "approved_entry")
            entry_net = sum(row_net(row, "net_cents") for row in selected)
            joined_entry_net = sum(row_net(row, "net_cents") for row, _ in joined)
            reduce_net = 0.0
            book_net = 0.0
            for _, exit_candidates in joined:
                reduce_net += next((row_net(row, "candidate_cents") for name, row in exit_candidates if name == "reduce"), 0.0)
                book_net += next((row_net(row, "candidate_cents") for name, row in exit_candidates if name == "book_gap"), 0.0)
            out.append({
                "lane": lane_name,
                "rule": rule.get("rule"),
                "selected": len(selected),
                "approved_rows": approved,
                "reconstructed_share": 1.0 - (approved / len(selected)) if selected else None,
                "entry_net_cents": entry_net,
                "joined_unambiguous_rows": len(joined),
                "ambiguous_market_side_rows": ambiguous,
                "joined_entry_net_cents": joined_entry_net,
                "joined_reduce_exit_net_cents": reduce_net,
                "joined_book_gap_exit_net_cents": book_net,
                "status": "overlap_probe_only",
            })
    return out


def rmt_feature_overlap() -> dict[str, Any]:
    rmt = load_json(RMT_JSON)
    rmt_rows = [row for row in rmt.get("rows") or [] if row.get("policy") == "rmt_repetition_forget_p58_edge2"]
    ledger = load_json(FEATURE_GATE_LEDGER_JSON)
    feature_rows: list[dict[str, Any]] = []
    for lane in ledger.get("lanes") or []:
        if lane.get("lane") != "post_feature_freeze_entry":
            continue
        for rule in lane.get("rules") or []:
            if rule.get("rule") == "raw05_recross60_abs085":
                feature_rows = rule.get("selected_rows") or []
                break
    rmt_by_key = {market_side_key(row): row for row in rmt_rows}
    feature_by_key = {market_side_key(row): row for row in feature_rows}
    overlap = sorted(set(rmt_by_key) & set(feature_by_key))
    return {
        "rmt_policy": "rmt_repetition_forget_p58_edge2",
        "rmt_rows": len(rmt_rows),
        "feature_gate_rows": len(feature_rows),
        "overlap_market_side_rows": len(overlap),
        "overlap_net_cents_rmt": sum(row_net(rmt_by_key[key], "net_gross_cents_after_entry_fee") for key in overlap),
        "overlap_net_cents_feature_gate": sum(row_net(feature_by_key[key], "net_cents") for key in overlap),
        "status": "poor_overlap_dual_lane_not_stack",
    }


def compact_candidate(row: dict[str, Any]) -> dict[str, Any]:
    wins = as_float(row.get("wins")) or 0.0
    losses = as_float(row.get("losses")) or 0.0
    denom = wins + losses
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "win_rate": wins / denom if denom else None,
        "coverage_pct": row.get("coverage_pct"),
        "net_cents": row.get("net_cents_after_entry_fee"),
        "simulated_share": row.get("simulated_share"),
        "blockers": row.get("blockers") or [],
    }


def best_stack_variant(payload: dict[str, Any]) -> dict[str, Any]:
    variants = [
        variant
        for lane in payload.get("lanes") or []
        for variant in (lane.get("variants") or [])
        if isinstance(variant, dict)
    ]
    if not variants:
        return {}
    return sorted(
        variants,
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("joined_exit_candidate_cents") or -999999.0),
            -float((row.get("entry_summary") or {}).get("net_cents") or -999999.0),
        ),
    )[0]


def best_midprice_exit_stack_variant(payload: dict[str, Any]) -> dict[str, Any]:
    variants = [row for row in payload.get("variants") or [] if isinstance(row, dict)]
    if not variants:
        return {}
    return sorted(
        variants,
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("weighted_joined_exit_candidate_cents") or -999999.0),
            -float((row.get("entry_summary") or {}).get("net_cents") or -999999.0),
        ),
    )[0]


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    tracker_rows = tracker.get("rows") or []
    top = top_tracker_rows(tracker.get("rows") or [])
    exit_mix = exit_policy_mix()
    feature_overlap = feature_gate_exit_overlap()
    soft_frontier_exit_stack = load_json(FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON)
    soft_frontier_exit_stack_best = best_stack_variant(soft_frontier_exit_stack)
    midprice_boundary_shrink = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON)
    midprice_boundary_variants = [
        variant
        for lane in midprice_boundary_shrink.get("lanes") or []
        for variant in (lane.get("variants") or [])
        if isinstance(variant, dict)
    ]
    midprice_boundary_best = sorted(
        midprice_boundary_variants,
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
        ),
    )[0] if midprice_boundary_variants else {}
    midprice_boundary_exit_stack = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON)
    midprice_boundary_exit_stack_best = best_midprice_exit_stack_variant(midprice_boundary_exit_stack)
    rmt_overlap = rmt_feature_overlap()
    sidecar = load_json(SIDECAR_JSON)
    forgetting_top = [compact_candidate(row) for row in tracker_family_top(tracker_rows, FORGETTING_GATES, limit=20)]
    catastrophic_forgetting_fv = [
        compact_candidate(row)
        for row in tracker_family_top(tracker_rows, CATASTROPHIC_FV_GATES, limit=20)
    ]
    recommended = [
        {
            "name": "dual_exit_book_gap_else_reduce",
            "type": "exit_policy_composite",
            "why": "Book-gap suppression dominates plain reduce-suppression on the common exit window; reduce-only rows add positive net on the wider reduce ledger.",
            "evidence": exit_mix["book_gap_else_reduce"],
            "blockers": ["needs_fresh_freeze", "exit_loss_control_signature_not_resolved", "live_ready_false"],
        },
        {
            "name": "value_only_book_gap_exit",
            "type": "exit_policy_refinement",
            "why": "The top book-gap lane's catastrophic cost comes from probability_reduce holds; suppressing only value-over-hold exits keeps soft-exit winner recovery while removing suppressed losers on the diagnostic book-gap window.",
            "evidence": exit_mix["book_gap_value_only"],
            "blockers": ["new_freeze_settled_lt_30", "needs_post_freeze_forward_rows", "live_ready_false"],
        },
        {
            "name": "value_v2_reduce_depth384_composite",
            "type": "exit_policy_composite",
            "why": "The strongest mixed exit idea separates rich-book value exits from shallow-depth probability-reduce exits; the safer frozen primary uses v2 value guards plus p_hold>=0.75/depth<=384 reduce suppression.",
            "evidence": exit_mix["value_reduce_depth_composite"],
            "blockers": ["new_freeze_settled_lt_30", "suppressed_decisions_lt_30", "needs_post_freeze_forward_rows", "live_ready_false"],
        },
        {
            "name": "observable_reduce_loss_control_gate",
            "type": "exit_policy_refinement",
            "why": "The newest observable gate combines shallow-entry-depth and very-short-duration reduce churn; it recovers diagnostic clipped winners without observed loss-control cost, but strict post-birth rows have not produced eligible probability_reduce exits yet.",
            "evidence": exit_mix["observable_loss_control"],
            "blockers": ["settled_lt_30", "suppressed_decisions_lt_30", "no_post_birth_probability_reduce_rows", "live_ready_false"],
        },
        {
            "name": "midband_reduce_rescue",
            "type": "exit_policy_refinement",
            "why": "The latest reduce-harm classifier says high p_hold rich exits can be dangerous to suppress, while lower p_hold 0.60-0.75 probability-reduce clips recovered winners in diagnostic rows without observed suppression harm.",
            "evidence": exit_mix["midband_reduce_rescue"],
            "blockers": ["new_freeze_no_post_birth_rows", "suppressed_decisions_lt_30", "needs_post_freeze_forward_rows", "live_ready_false"],
        },
        {
            "name": "loss_guarded_book_gap_exit",
            "type": "exit_policy_refinement",
            "why": "The loss-guard keeps most book-gap upside while shrinking suppressed full-loss cost; on the comparable book-gap freeze window it improves current v28 by +473c with 0c observed suppressed-loss cost.",
            "evidence": exit_mix["book_gap_loss_guard"],
            "blockers": ["new_freeze_settled_lt_30", "needs_post_freeze_forward_rows", "live_ready_false"],
        },
        {
            "name": "loss_guarded_book_gap_exit_v2",
            "type": "exit_policy_refinement",
            "why": "The stricter loss-guard v2 gives up some comparable-window upside, but removes the observed suppressed-loss cost on the broader diagnostic exit sample by refusing high-p_hold holds when the book gap is negative and fair drawdown is deep.",
            "evidence": exit_mix["book_gap_loss_guard_v2"],
            "blockers": ["new_freeze_settled_lt_30", "suppressed_decisions_lt_30", "needs_post_freeze_forward_rows", "live_ready_false"],
        },
        {
            "name": "loss_guarded_book_gap_exit_v3_extreme_p",
            "type": "exit_policy_refinement",
            "why": "V3 keeps v2's rich-exit/negative-gap protection but tests whether extreme p_hold>=0.95 value exits recover clipped winners without reopening the lower-confidence 80-90c rich-exit failure.",
            "evidence": exit_mix["book_gap_loss_guard_v3"],
            "blockers": ["new_freeze_settled_lt_30", "needs_post_freeze_forward_rows", "live_ready_false"],
        },
        {
            "name": "clean_feature_gate_with_book_gap_exit_watch",
            "type": "entry_plus_exit_watch",
            "why": "The clean ask65 feature-gate row has zero reconstructed share and the joined approved subset improves under book-gap exit handling, but sample and coverage are too small.",
            "evidence": sorted(
                feature_overlap,
                key=lambda row: (row.get("joined_book_gap_exit_net_cents") or -999999.0, row.get("entry_net_cents") or -999999.0),
                reverse=True,
            )[:3],
            "blockers": ["settled_lt_30", "coverage_too_low_for_ask65", "row_join_is_partial", "live_ready_false"],
        },
        {
            "name": "soft_frontier_feature_gate_with_guarded_exit_stack",
            "type": "entry_plus_exit_watch",
            "why": "The soft-frontier rule is the broadest clean observable feature gate that meets target coverage diagnostically; this new frozen stack tests it with book-gap and loss-guarded exits from its own timestamp.",
            "evidence": {
                "freeze": soft_frontier_exit_stack.get("freeze") or {},
                "exit_rows_available": soft_frontier_exit_stack.get("exit_rows_available") or {},
                "best_variant": soft_frontier_exit_stack_best,
            },
            "blockers": ["new_freeze_no_joined_rows", "settled_lt_30", "live_ready_false"],
        },
        {
            "name": "soft_frontier_midprice_boundary_shrink",
            "type": "entry_size_overlay_watch",
            "why": "The strongest new mix from the broad soft-frontier branch shrinks only near-boundary mid-price rows, preserving selected-market coverage while reducing the repeated -133c diagnostic loss pocket to -33c at quarter size.",
            "evidence": {
                "freeze": midprice_boundary_shrink.get("state") or {},
                "best_variant": midprice_boundary_best,
            },
            "blockers": ["new_freeze_settled_lt_30", "strict_forward_rows_zero", "source_share_still_high_on_post_feature_window", "live_ready_false"],
        },
        {
            "name": "soft_frontier_midprice_boundary_with_book_gap_exit",
            "type": "entry_size_overlay_plus_exit_watch",
            "why": "The weighted overlap audit combines the top broad-entry shrink with guarded exits; diagnostic matched book-gap rows beat the live baseline, but the combination is newly frozen and strict overlap is not mature.",
            "evidence": {
                "freeze": midprice_boundary_exit_stack.get("freeze") or {},
                "best_variant": midprice_boundary_exit_stack_best,
            },
            "blockers": ["entry_lane_not_strict_combo_forward", "strict_combo_joined_rows_lt_30", "live_ready_false"],
        },
        {
            "name": "rmt_p58_edge2_as_narrow_sidecar_only",
            "type": "dual_strategy_sidecar",
            "why": "RMT p58 edge2 has the highest current win rate among >=10-settled lanes, but it is tiny, mostly reconstructed, and barely overlaps the boundary-clock feature gate.",
            "evidence": rmt_overlap,
            "blockers": ["diagnostic_only", "coverage_too_low", "simulated_share_gt_35pct", "poor_stack_overlap"],
        },
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "top_pnl": [compact_candidate(row) for row in top["top_pnl"]],
        "top_win_rate_min10": [compact_candidate(row) for row in top["top_win_rate_min10"]],
        "exit_policy_mix": exit_mix,
        "feature_gate_exit_overlap": feature_overlap,
        "feature_gate_soft_frontier_exit_stack": {
            "freeze": soft_frontier_exit_stack.get("freeze") or {},
            "exit_rows_available": soft_frontier_exit_stack.get("exit_rows_available") or {},
            "best_variant": soft_frontier_exit_stack_best,
        },
        "soft_frontier_midprice_boundary_shrink": {
            "freeze": midprice_boundary_shrink.get("state") or {},
            "best_variant": midprice_boundary_best,
        },
        "soft_frontier_midprice_boundary_exit_stack": {
            "freeze": midprice_boundary_exit_stack.get("freeze") or {},
            "best_variant": midprice_boundary_exit_stack_best,
        },
        "rmt_feature_overlap": rmt_overlap,
        "forgetting_family_top": forgetting_top,
        "catastrophic_forgetting_fv": catastrophic_forgetting_fv,
        "sidecar_live_test": {
            "counts": sidecar.get("counts") or {},
            "closest_positive": (sidecar.get("closest_positive") or [{}])[0],
            "top_net": (sidecar.get("top_net") or [{}])[0],
        },
        "recommended_research_candidates": recommended,
        "promotion_status": "none_live_ready",
    }


def money(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number * 100.0:.1f}%" if number <= 1.0 else f"{number:.1f}%"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Top Candidate Mix/Match Audit",
        "",
        "Research-only diagnostic. No live trading logic changed.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Promotion status: `{report['promotion_status']}`",
        "",
        "## Top PnL Candidates",
        "",
        "| rank | gate | policy | settled | W/L | net | coverage | sim share |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(report["top_pnl"][:10], start=1):
        lines.append(
            f"| {idx} | `{row['gate']}` | `{row['policy']}` | {row['settled']} | "
            f"{row['wins']}/{row['losses']} | {money(row['net_cents'])} | {pct(row['coverage_pct'])} | {pct(row['simulated_share'])} |"
        )
    lines.extend([
        "",
        "## Top Winning Candidates",
        "",
        "| rank | gate | policy | settled | W/L | win rate | net | coverage | sim share |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report["top_win_rate_min10"][:10], start=1):
        lines.append(
            f"| {idx} | `{row['gate']}` | `{row['policy']}` | {row['settled']} | "
            f"{row['wins']}/{row['losses']} | {pct(row['win_rate'])} | {money(row['net_cents'])} | "
            f"{pct(row['coverage_pct'])} | {pct(row['simulated_share'])} |"
        )
    exit_mix = report["exit_policy_mix"]
    sidecar_counts = report["sidecar_live_test"]["counts"]
    sidecar_closest = report["sidecar_live_test"]["closest_positive"]
    combo = exit_mix["book_gap_else_reduce"]
    value_only_diag = ((exit_mix["book_gap_value_only"].get("diagnostic") or {}).get("variants") or [{}])[0]
    value_only_diag_summary = value_only_diag.get("summary") or {}
    value_only_forward = exit_mix["book_gap_value_only"].get("forward") or {}
    value_reduce_diag = ((exit_mix["value_reduce_depth_composite"].get("diagnostic") or {}).get("variants") or [{}])[0]
    value_reduce_diag_summary = value_reduce_diag.get("summary") or {}
    value_reduce_forward = exit_mix["value_reduce_depth_composite"].get("forward") or {}
    observable = exit_mix["observable_loss_control"]
    observable_diag_summary = (observable.get("diagnostic") or {}).get("summary") or {}
    observable_post_summary = (observable.get("post_birth") or {}).get("summary") or {}
    observable_opportunity = observable.get("opportunity") or {}
    midband = exit_mix["midband_reduce_rescue"]
    midband_diag = midband.get("diagnostic_best") or {}
    midband_post = midband.get("post_birth_best") or {}
    midprice = report.get("soft_frontier_midprice_boundary_shrink") or {}
    midprice_best = midprice.get("best_variant") or {}
    midprice_summary = midprice_best.get("summary") or {}
    midprice_exit = report.get("soft_frontier_midprice_boundary_exit_stack") or {}
    midprice_exit_best = midprice_exit.get("best_variant") or {}
    midprice_exit_summary = midprice_exit_best.get("entry_summary") or {}
    lines.extend([
        "",
        "## Mix/Match Findings",
        "",
        f"- `book_gap_else_reduce`: {combo['rows']} rows, W/L {combo['wins']}/{combo['losses']}, net {money(combo['net_cents'])}, current-comparable net {money(combo['current_net_cents'])}.",
        f"- Common reduce/book window: {exit_mix['pairwise_common_windows'][0]['common_rows']} rows; reduce net {money(exit_mix['pairwise_common_windows'][0]['left_net_cents'])}, book-gap net {money(exit_mix['pairwise_common_windows'][0]['right_net_cents'])}.",
        f"- `value_only_book_gap_exit` diagnostic book-gap window: {value_only_diag_summary.get('settled')} rows, W/L {value_only_diag_summary.get('candidate_wins')}/{value_only_diag_summary.get('candidate_losses')}, net {money(value_only_diag_summary.get('candidate_gross_cents'))}, suppressed W/L {value_only_diag_summary.get('suppressed_winners')}/{value_only_diag_summary.get('suppressed_losers')}, loss cost {money(value_only_diag_summary.get('loss_control_cost_cents'))}.",
        f"- `value_only_book_gap_exit` strict post-freeze window: {value_only_forward.get('settled')} rows, W/L {value_only_forward.get('candidate_wins')}/{value_only_forward.get('candidate_losses')}, net {money(value_only_forward.get('candidate_gross_cents'))}, blockers {exit_mix['book_gap_value_only'].get('blockers')}.",
        f"- `value_v2_reduce_depth384_composite` diagnostic exit-freeze window: rule {value_reduce_diag.get('rule')}, {value_reduce_diag_summary.get('settled')} rows, W/L {value_reduce_diag_summary.get('candidate_wins')}/{value_reduce_diag_summary.get('candidate_losses')}, net {money(value_reduce_diag_summary.get('candidate_gross_cents'))}, delta {money(value_reduce_diag_summary.get('delta_vs_current_cents'))}, suppressed value/reduce {value_reduce_diag_summary.get('value_suppressed')}/{value_reduce_diag_summary.get('reduce_suppressed')}, suppressed W/L {value_reduce_diag_summary.get('suppressed_winners')}/{value_reduce_diag_summary.get('suppressed_losers')}, loss cost {money(value_reduce_diag_summary.get('loss_control_cost_cents'))}.",
        f"- `value_v2_reduce_depth384_composite` strict post-freeze window: {value_reduce_forward.get('settled')} rows, W/L {value_reduce_forward.get('candidate_wins')}/{value_reduce_forward.get('candidate_losses')}, net {money(value_reduce_forward.get('candidate_gross_cents'))}, blockers {exit_mix['value_reduce_depth_composite'].get('blockers')}.",
        f"- `observable_reduce_loss_control_gate` diagnostic reduce-freeze window: {observable_diag_summary.get('settled')} rows, W/L {observable_diag_summary.get('candidate_wins')}/{observable_diag_summary.get('candidate_losses')}, delta {money(observable_diag_summary.get('delta_vs_current_cents'))}, suppressed W/L {observable_diag_summary.get('suppressed_winners')}/{observable_diag_summary.get('suppressed_losers')}, loss cost {money(observable_diag_summary.get('loss_control_cost_cents'))}.",
        f"- `observable_reduce_loss_control_gate` strict post-birth window: {observable_post_summary.get('settled')} rows, delta {money(observable_post_summary.get('delta_vs_current_cents'))}, would-suppress rows {observable_opportunity.get('would_suppress_rows')}, fail reasons {observable_opportunity.get('fail_reason_counts')}.",
        f"- `midband_reduce_rescue` diagnostic window: {midband_diag.get('rows')} rows, suppressed {midband_diag.get('suppressed')}, delta {money(midband_diag.get('delta_vs_current_cents'))}, loss-count reduction {midband_diag.get('loss_count_reduction')}, helpful/harmful {midband_diag.get('helpful_suppressions')}/{midband_diag.get('harmful_suppressions')}; strict post-birth rows {midband_post.get('rows')} with blockers {midband_post.get('blockers')}.",
        f"- `soft_frontier_midprice_boundary_shrink` best diagnostic/watch row: {midprice_best.get('candidate')} has {midprice_summary.get('settled')} settled, W/L {midprice_summary.get('wins')}/{midprice_summary.get('losses')}, coverage {pct(midprice_summary.get('coverage_pct'))}, net {money(midprice_summary.get('net_cents'))}, delta {money(midprice_summary.get('delta_vs_unweighted_cents'))}, band rows {midprice_summary.get('midprice_boundary_rows')} raw/weighted {money(midprice_summary.get('midprice_boundary_raw_net_cents'))}/{money(midprice_summary.get('midprice_boundary_weighted_net_cents'))}, blockers {midprice_best.get('blockers')}.",
        f"- `soft_frontier_midprice_boundary_with_book_gap_exit` best overlap: {midprice_exit_best.get('candidate')} has entry settled {midprice_exit_summary.get('settled')}, joined exits {midprice_exit_best.get('joined_exit_rows')}, weighted exit net {money(midprice_exit_best.get('weighted_joined_exit_candidate_cents'))}, weighted delta {money(midprice_exit_best.get('weighted_joined_exit_delta_cents'))}, blockers {midprice_exit_best.get('blockers')}.",
        f"- `loss_guarded_book_gap_exit` comparable book-gap window: {exit_mix['book_gap_loss_guard']['discovery_comparable_book_gap_freeze'].get('settled')} rows, W/L {exit_mix['book_gap_loss_guard']['discovery_comparable_book_gap_freeze'].get('candidate_wins')}/{exit_mix['book_gap_loss_guard']['discovery_comparable_book_gap_freeze'].get('candidate_losses')}, net {money(exit_mix['book_gap_loss_guard']['discovery_comparable_book_gap_freeze'].get('candidate_gross_cents'))}, loss cost {money(exit_mix['book_gap_loss_guard']['discovery_comparable_book_gap_freeze'].get('loss_control_cost_cents'))}.",
        f"- `loss_guarded_book_gap_exit` all-exit discovery window: {exit_mix['book_gap_loss_guard']['discovery_all_exit_rows'].get('settled')} rows, W/L {exit_mix['book_gap_loss_guard']['discovery_all_exit_rows'].get('candidate_wins')}/{exit_mix['book_gap_loss_guard']['discovery_all_exit_rows'].get('candidate_losses')}, net {money(exit_mix['book_gap_loss_guard']['discovery_all_exit_rows'].get('candidate_gross_cents'))}, loss cost {money(exit_mix['book_gap_loss_guard']['discovery_all_exit_rows'].get('loss_control_cost_cents'))}.",
        f"- `loss_guarded_book_gap_exit_v2` comparable book-gap window: {exit_mix['book_gap_loss_guard_v2']['discovery_comparable_book_gap_freeze'].get('settled')} rows, W/L {exit_mix['book_gap_loss_guard_v2']['discovery_comparable_book_gap_freeze'].get('candidate_wins')}/{exit_mix['book_gap_loss_guard_v2']['discovery_comparable_book_gap_freeze'].get('candidate_losses')}, net {money(exit_mix['book_gap_loss_guard_v2']['discovery_comparable_book_gap_freeze'].get('candidate_gross_cents'))}, loss cost {money(exit_mix['book_gap_loss_guard_v2']['discovery_comparable_book_gap_freeze'].get('loss_control_cost_cents'))}.",
        f"- `loss_guarded_book_gap_exit_v2` all-exit discovery window: {exit_mix['book_gap_loss_guard_v2']['discovery_all_exit_rows'].get('settled')} rows, W/L {exit_mix['book_gap_loss_guard_v2']['discovery_all_exit_rows'].get('candidate_wins')}/{exit_mix['book_gap_loss_guard_v2']['discovery_all_exit_rows'].get('candidate_losses')}, net {money(exit_mix['book_gap_loss_guard_v2']['discovery_all_exit_rows'].get('candidate_gross_cents'))}, loss cost {money(exit_mix['book_gap_loss_guard_v2']['discovery_all_exit_rows'].get('loss_control_cost_cents'))}.",
        f"- `loss_guarded_book_gap_exit_v3_extreme_p` strict post-freeze window: {exit_mix['book_gap_loss_guard_v3']['forward'].get('settled')} rows, W/L {exit_mix['book_gap_loss_guard_v3']['forward'].get('candidate_wins')}/{exit_mix['book_gap_loss_guard_v3']['forward'].get('candidate_losses')}, net {money(exit_mix['book_gap_loss_guard_v3']['forward'].get('candidate_gross_cents'))}, blockers {exit_mix['book_gap_loss_guard_v3'].get('blockers')}.",
        f"- `loss_guarded_book_gap_exit_v3_extreme_p` all-exit diagnostic window: {exit_mix['book_gap_loss_guard_v3']['discovery_all_exit_rows'].get('settled')} rows, W/L {exit_mix['book_gap_loss_guard_v3']['discovery_all_exit_rows'].get('candidate_wins')}/{exit_mix['book_gap_loss_guard_v3']['discovery_all_exit_rows'].get('candidate_losses')}, net {money(exit_mix['book_gap_loss_guard_v3']['discovery_all_exit_rows'].get('candidate_gross_cents'))}, loss cost {money(exit_mix['book_gap_loss_guard_v3']['discovery_all_exit_rows'].get('loss_control_cost_cents'))}.",
        "- The exit-policy family is still the strongest mix/match direction, but every new variant needs clean post-freeze rows before promotion.",
        "",
        "## Feature-Gate Exit Overlap",
        "",
        "| lane | rule | selected | approved | entry net | joined rows | joined entry net | joined reduce exit | joined book-gap exit | ambiguous |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in sorted(
        report["feature_gate_exit_overlap"],
        key=lambda item: (item.get("joined_book_gap_exit_net_cents") or -999999.0, item.get("entry_net_cents") or -999999.0),
        reverse=True,
    )[:8]:
        lines.append(
            f"| `{row['lane']}` | `{row['rule']}` | {row['selected']} | {row['approved_rows']} | "
            f"{money(row['entry_net_cents'])} | {row['joined_unambiguous_rows']} | {money(row['joined_entry_net_cents'])} | "
            f"{money(row['joined_reduce_exit_net_cents'])} | {money(row['joined_book_gap_exit_net_cents'])} | {row['ambiguous_market_side_rows']} |"
        )
    lines.extend([
        "",
        "## Forgetting / Memory Family",
        "",
        "| rank | gate | policy | settled | W/L | win rate | net | coverage | sim share | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report["forgetting_family_top"][:20], start=1):
        lines.append(
            f"| {idx} | `{row['gate']}` | `{row['policy']}` | {row['settled']} | "
            f"{row['wins']}/{row['losses']} | {pct(row['win_rate'])} | {money(row['net_cents'])} | "
            f"{pct(row['coverage_pct'])} | {pct(row['simulated_share'])} | {', '.join(row['blockers'])} |"
        )
    lines.extend([
        "",
        "## Catastrophic Forgetting FV Overlays",
        "",
        "These are the explicit boundary/phi/reward-memory FV overlays. They are shown separately so negative catastrophic-forgetting rows do not disappear below RMT sidecar rows.",
        "",
        "| rank | gate | policy | settled | W/L | net | coverage | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report["catastrophic_forgetting_fv"][:20], start=1):
        lines.append(
            f"| {idx} | `{row['gate']}` | `{row['policy']}` | {row['settled']} | "
            f"{row['wins']}/{row['losses']} | {money(row['net_cents'])} | "
            f"{pct(row['coverage_pct'])} | {', '.join(row['blockers'])} |"
        )
    lines.extend([
        "",
        "## Sidecar Readiness",
        "",
        f"- Sidecar-ready rows: `{sidecar_counts.get('sidecar_ready_rows')}` out of `{sidecar_counts.get('candidate_rows')}` candidate rows.",
        f"- Closest positive sidecar: `{sidecar_closest.get('gate')} / {sidecar_closest.get('policy')}` with {sidecar_closest.get('settled')} settled, net {money(sidecar_closest.get('net_cents'))}, cushion {sidecar_closest.get('full_loss_cushion')}, missing gates {sidecar_closest.get('missing_gates')}.",
    ])
    lines.extend([
        "",
        "## Recommended Research Tracks",
        "",
    ])
    for item in report["recommended_research_candidates"]:
        blockers = ", ".join(item["blockers"])
        lines.append(f"- `{item['name']}`: {item['why']} Blockers: {blockers}.")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- Top PnL is currently an exit-policy story, not an entry-gate story.",
        "- Top win rate is mostly narrow and/or source-quality blocked, so it should be a sidecar/watch lane rather than the main broad strategy.",
        "- The cleanest mature freeze is the stricter v2 loss-guard; V3 is the newest extreme-probability branch and has to earn post-freeze rows from its own timestamp.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
