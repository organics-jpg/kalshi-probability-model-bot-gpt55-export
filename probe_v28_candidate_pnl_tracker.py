"""Current PnL/W-L tracker for v28 candidate lanes.

This is a reporting-only aggregation. It reads the existing readiness and
leaderboard artifacts, reconciles candidates by gate/policy, and writes a
single answer to "what are we tracking against live BTC 15m markets?"
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
LEADERBOARD_JSON = OUT_DIR / "v28_frozen_candidate_leaderboard_latest.json"
WATCHLIST_MD = OUT_DIR / "v28_candidate_watchlist_latest.md"
OUT_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
OUT_MD = OUT_DIR / "v28_candidate_pnl_tracker_latest.md"
FEATURE_GATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
FEATURE_GATE_BOOK_GAP_EXIT_STACK_JSON = OUT_DIR / "v28_frozen_feature_gate_book_gap_exit_stack_latest.json"
FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON = OUT_DIR / "v28_frozen_feature_gate_soft_frontier_exit_stack_latest.json"
FEATURE_GATE_CONTINUOUS_PENALTY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.json"
FEATURE_GATE_SOFT_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_watch_latest.json"
FEATURE_GATE_CLEAN_BROAD_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_clean_broad_frontier_watch_latest.json"
FEATURE_GATE_CHEAP_TAIL_QUARANTINE_JSON = OUT_DIR / "v28_feature_gate_cheap_tail_quarantine_latest.json"
FEATURE_GATE_CHEAP_TAIL_SHRINK_WATCH_JSON = OUT_DIR / "v28_frozen_feature_gate_cheap_tail_shrink_watch_latest.json"
FEATURE_GATE_CORE_EXPANSION_MIX_JSON = OUT_DIR / "v28_feature_gate_core_expansion_mix_latest.json"
FEATURE_GATE_COVERAGE_SIZE_SHRINK_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.json"
FEATURE_GATE_MIDDLE_DISTANCE_CORE_JSON = OUT_DIR / "v28_feature_gate_middle_distance_core_watch_latest.json"
FEATURE_GATE_MIDDLE_CORE_EXIT_GUARD_JSON = OUT_DIR / "v28_feature_gate_middle_core_exit_guard_watch_latest.json"
FEATURE_GATE_OBSERVABLE_SELECTION_MIX_JSON = OUT_DIR / "v28_feature_gate_observable_selection_mix_latest.json"
FEATURE_GATE_SIZE_SHRINK_EXIT_OVERLAY_JSON = OUT_DIR / "v28_feature_gate_size_shrink_exit_overlay_latest.json"
FEATURE_GATE_SIZE_SHRINK_DELAYED_RECHECK_EXIT_JSON = OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_exit_latest.json"
FEATURE_GATE_SIZE_SHRINK_DELAYED_RECHECK_RESCUE_JSON = OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_rescue_latest.json"
FEATURE_GATE_SOURCE_CONFIRMATION_REPLACEMENT_JSON = OUT_DIR / "v28_feature_gate_source_confirmation_replacement_latest.json"
FEATURE_GATE_LATE_COLLAPSE_RECHECK_RESCUE_JSON = OUT_DIR / "v28_feature_gate_late_collapse_recheck_rescue_latest.json"
FEATURE_GATE_DUAL_CLOCK_RECHECK_RESCUE_JSON = OUT_DIR / "v28_feature_gate_dual_clock_recheck_rescue_latest.json"
FEATURE_GATE_CONFIRMED_DUAL_CLOCK_FILL_JSON = OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_latest.json"
FEATURE_GATE_SOURCE_QUALITY_PROXY_JSON = OUT_DIR / "v28_feature_gate_source_quality_proxy_latest.json"
FEATURE_GATE_SOURCE_PROXY_COVERAGE_REPAIR_JSON = OUT_DIR / "v28_feature_gate_source_proxy_coverage_repair_latest.json"
TARGET_CLUSTER_SOURCE_AWARE_JSON = OUT_DIR / "v28_target_cluster_penalty_source_aware_watch_latest.json"
TARGET_CLUSTER_OBSERVABLE_STABILITY_JSON = OUT_DIR / "v28_target_cluster_penalty_observable_stability_proxy_latest.json"
EXIT_REDUCE_REFINEMENT_JSON = OUT_DIR / "v28_frozen_exit_reduce_loss_control_refinement_latest.json"
EXIT_REDUCE_DEPTH_GATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json"
EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_JSON = OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json"
EXIT_REDUCE_DRIFT_GUARD_JSON = OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_latest.json"
EXIT_SHALLOW_DRAWDOWN_JSON = OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_latest.json"
EXIT_SHALLOW_DURATION_JSON = OUT_DIR / "v28_frozen_exit_shallow_duration_watch_latest.json"
EXIT_MIDBAND_REDUCE_RESCUE_JSON = OUT_DIR / "v28_frozen_exit_midband_reduce_rescue_watch_latest.json"
EXIT_CLIP_SEPARATOR_WATCH_JSON = OUT_DIR / "v28_frozen_exit_clip_separator_watch_latest.json"
MATCHED_UNCHANGED_LOSS_GUARD_WATCH_JSON = OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_latest.json"
RMT_FORGETTING_ENTRY_JSON = OUT_DIR / "v28_rmt_forgetting_entry_bakeoff_latest.json"
PATH_RMT_FORWARD_GATE_JSON = OUT_DIR / "v28_path_rmt_forward_gate_latest.json"
BOUNDARY_MEMORY_FV_JSON = OUT_DIR / "v28_boundary_memory_fv_candidates_latest.json"
PHI_FORGETTING_FV_JSON = OUT_DIR / "v28_phi_forgetting_fv_candidates_latest.json"
REWARD_MEMORY_FV_JSON = OUT_DIR / "v28_reward_memory_fv_candidates_latest.json"
FALSE_CONVICTION_FAMILY_JSON = OUT_DIR / "v28_false_conviction_family_scorecard_latest.json"
BOUNDARY_CLOCK_SOURCE_STRESS_JSON = OUT_DIR / "v28_boundary_clock_source_stress_latest.json"
COLLAPSE_REENTRY_JSON = OUT_DIR / "v28_live_collapse_reentry_registry_latest.json"
SOFT_FRONTIER_SIZE_SHRINK_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
MIDPRICE_SOURCE_DILUTION_JSON = OUT_DIR / "v28_midprice_source_dilution_watch_latest.json"
P50_BOOK_EDGE_NO_SIDE_SHRINK_JSON = OUT_DIR / "v28_frozen_p50_book_edge_no_side_shrink_watch_latest.json"
FEATURE_GATE_VALUE_EXIT_WATCH_JSON = OUT_DIR / "v28_frozen_feature_gate_value_exit_watch_latest.json"
VALUE_EXIT_FEATURE_SIDE_GUARD_JSON = OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_CLIP_EXIT_STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_clip_exit_stack_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_stack_latest.json"
SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_GUARD_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_guard_refinement_latest.json"
FEATURE_GATE_EXIT_BID_SUPPRESSION_WATCH_JSON = OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_latest.json"
FEATURE_GATE_EXIT_BID_DELAYED_RECHECK_JSON = OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_latest.json"
EXIT_COMMON_CLOCK_RESIDUAL_CHILD_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_latest.json"
SOFT_FRONTIER_MIDPRICE_DELAYED_RECHECK_EXIT_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json"
SOFT_FRONTIER_MIDPRICE_DELAYED_RECHECK_RESCUE_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_rescue_latest.json"
TOP_COMPONENT_MIX_PORTFOLIO_JSON = OUT_DIR / "v28_top_component_mix_portfolio_latest.json"
TOP_COMPONENT_FALSE_NEGATIVE_RESCUE_JSON = OUT_DIR / "v28_top_component_false_negative_rescue_child_latest.json"
TOP_COMPONENT_PARENT_FILL_REPAIR_JSON = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json"
TOP_COMPONENT_OBSERVABLE_QUARANTINE_JSON = OUT_DIR / "v28_top_component_observable_quarantine_child_latest.json"
DUAL_LANE_OVERLAP_PORTFOLIO_JSON = OUT_DIR / "v28_dual_lane_overlap_portfolio_latest.json"
DUAL_LANE_OWN_FREEZE_WATCH_JSON = OUT_DIR / "v28_dual_lane_own_freeze_watch_latest.json"
SUPPLEMENTAL_SUMMARY_SOURCES = [
    (
        "weak_reversal_residual_fv_shrink",
        OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_latest.json",
        "weak_summary",
        ("freeze", "variant"),
    ),
    (
        "weak_reversal_residual_repair",
        OUT_DIR / "v28_frozen_weak_reversal_residual_repair_latest.json",
        "candidate_summary",
        ("policy",),
    ),
    (
        "no_mid_edge_fv",
        OUT_DIR / "v28_frozen_no_mid_edge_fv_latest.json",
        "target_summary",
        ("freeze", "variant"),
    ),
    (
        "boundary_energy_fv_entry",
        OUT_DIR / "v28_frozen_boundary_energy_fv_entry_latest.json",
        "candidate_summary",
        ("freeze", "candidate"),
    ),
    (
        "early_no_boundary_fv_entry",
        OUT_DIR / "v28_frozen_early_no_boundary_fv_entry_latest.json",
        "candidate_summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_reduce_suppression",
        OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_reduce_yes_suppression",
        OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_book_gap_suppression",
        OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_book_gap_loss_guard",
        OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_book_gap_loss_guard_v2",
        OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_book_gap_loss_guard_v3",
        OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_book_gap_value_only",
        OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_value_reduce_depth_composite",
        OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_reduce_geometry_suppression",
        OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "exit_reduce_geometry_relaxed_watch",
        OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "dual_exit_book_gap_else_reduce",
        OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.json",
        "summary",
        ("freeze", "candidate"),
    ),
    (
        "approved_entry_book_raw_blend_fv",
        OUT_DIR / "v28_frozen_approved_entry_book_raw_blend_latest.json",
        "candidate_summary",
        ("freeze", "primary_candidate"),
    ),
]


TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0


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


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(number)


def key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("gate") or ""), str(row.get("policy") or ""))


def has_settled_pnl(row: dict[str, Any]) -> bool:
    settled = as_float(row.get("settled")) or 0.0
    return settled > 0 and as_float(row.get("net_cents_after_entry_fee")) is not None


def in_target_coverage(row: dict[str, Any]) -> bool:
    coverage = as_float(row.get("coverage_pct"))
    return (
        coverage is not None
        and TARGET_COVERAGE_MIN <= coverage <= TARGET_COVERAGE_MAX
    )


def simulated_share(row: dict[str, Any]) -> float | None:
    share = as_float(row.get("simulated_share"))
    if share is not None:
        return share
    approved = as_float(row.get("approved_entry_count"))
    rejected = as_float(row.get("added_reject_count"))
    if approved is None or rejected is None:
        return None
    total = approved + rejected
    if total <= 0:
        return None
    return rejected / total


def merge_rows(
    readiness_rows: list[dict[str, Any]],
    leaderboard_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    readiness_by_key = {key(row): row for row in readiness_rows}
    leaderboard_by_key = {key(row): row for row in leaderboard_rows}
    merged: list[dict[str, Any]] = []

    for row_key in sorted(set(readiness_by_key) | set(leaderboard_by_key)):
        ready = readiness_by_key.get(row_key, {})
        leader = leaderboard_by_key.get(row_key, {})
        # The frozen leaderboard is the authoritative source for settled
        # forward PnL/W-L when it has the lane. Readiness contributes gate
        # state, but can lag the dedicated frozen scorecards on performance.
        row = {**ready, **leader}

        # The readiness artifact is the broadest source for current PnL, while
        # the leaderboard often has W/L fields. Preserve leaderboard W/L when
        # readiness does not carry them.
        for field in ("wins", "losses"):
            if row.get(field) is None and leader.get(field) is not None:
                row[field] = leader.get(field)

        row["candidate_key"] = f"{row_key[0]}::{row_key[1]}"
        row["source_readiness"] = row_key in readiness_by_key
        row["source_leaderboard"] = row_key in leaderboard_by_key
        row["target_coverage"] = in_target_coverage(row)
        row["has_settled_pnl"] = has_settled_pnl(row)
        row["simulated_share"] = simulated_share(row)
        merged.append(row)
    return merged


def nested_get(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = payload
    for part in path:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def supplemental_summary_map() -> dict[tuple[str, str], dict[str, Any]]:
    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    for gate, path, summary_key, policy_path in SUPPLEMENTAL_SUMMARY_SOURCES:
        payload = load_json(path)
        summary = payload.get(summary_key)
        if not isinstance(summary, dict):
            continue
        policy = nested_get(payload, policy_path)
        if not policy:
            continue
        summaries[(gate, str(policy))] = summary
    return summaries


def supplemental_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for gate, path, summary_key, policy_path in SUPPLEMENTAL_SUMMARY_SOURCES:
        payload = load_json(path)
        summary = payload.get(summary_key)
        if not isinstance(summary, dict):
            continue
        policy = nested_get(payload, policy_path)
        if not policy:
            continue
        row = {
            "gate": gate,
            "policy": str(policy),
            "live_ready": bool(payload.get("candidate_live_ready")),
            "blockers": payload.get("blockers") or [],
            "candidate_key": f"{gate}::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_supplemental_summary": True,
        }
        apply_supplemental_summary(row, summary)
        rows.append(row)
    return rows


def first_present(payload: dict[str, Any], *fields: str) -> Any:
    for field in fields:
        value = payload.get(field)
        if value is not None:
            return value
    return None


def apply_supplemental_summary(row: dict[str, Any], summary: dict[str, Any]) -> None:
    net_cents = first_present(
        summary,
        "net_cents_after_entry_fee",
        "net_cents",
        "candidate_net_cents",
        "candidate_gross_cents",
    )
    field_updates = {
        "entries": first_present(summary, "entries", "rows"),
        "settled": first_present(summary, "settled", "rows"),
        "wins": first_present(summary, "wins", "candidate_wins"),
        "losses": first_present(summary, "losses", "candidate_losses"),
        "net_cents_after_entry_fee": net_cents,
        "avg_net_cents": summary.get("avg_net_cents"),
        "delta_vs_current_cents": summary.get("delta_vs_current_cents"),
        "suppressed_exits": summary.get("suppressed_exits"),
        "winner_clip_recovered_cents": summary.get("winner_clip_recovered_cents"),
        "loss_control_cost_cents": summary.get("loss_control_cost_cents"),
        "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
    }
    for field, value in field_updates.items():
        if value is not None:
            row[field] = value
    if row.get("full_loss_cushion_estimate") is None:
        net_number = as_float(net_cents)
        if net_number is not None and net_number > 0.0:
            row["full_loss_cushion_estimate"] = int(net_number // 100.0)
    row["target_coverage"] = in_target_coverage(row)
    row["has_settled_pnl"] = has_settled_pnl(row)
    row["simulated_share"] = simulated_share(row)


def feature_gate_forward_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if not lane_name.startswith("post_feature_freeze_"):
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("candidate_summary")
            if not isinstance(summary, dict):
                continue
            source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
            row = {
                "gate": "boundary_clock_feature_gate_candidate",
                "policy": variant.get("candidate") or lane_name,
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "avg_net_cents": summary.get("avg_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": source_counts.get("rejected_actionable"),
                "simulated_share": variant.get("reconstructed_share"),
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "full_loss_cushion_estimate": variant.get("full_loss_cushion_estimate"),
                "candidate_key": f"boundary_clock_feature_gate_candidate::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def feature_gate_book_gap_exit_stack_rows(
    path: Path = FEATURE_GATE_BOOK_GAP_EXIT_STACK_JSON,
    gate: str = "feature_gate_book_gap_exit_stack",
    source_flag: str = "source_feature_gate_book_gap_exit_stack",
) -> list[dict[str, Any]]:
    payload = load_json(path)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("entry_summary")
            if not isinstance(summary, dict):
                continue
            joined_rows = variant.get("joined_rows") if isinstance(variant.get("joined_rows"), list) else []
            source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
            row = {
                "gate": gate,
                "policy": variant.get("candidate") or f"{lane_name}_{variant.get('rule')}",
                "entries": summary.get("entries"),
                "settled": variant.get("joined_exit_rows"),
                "wins": sum(1 for item in joined_rows if (as_float(item.get("exit_candidate_cents")) or 0.0) >= 0.0),
                "losses": sum(1 for item in joined_rows if (as_float(item.get("exit_candidate_cents")) or 0.0) < 0.0),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents_after_entry_fee": variant.get("joined_exit_candidate_cents"),
                "entry_settled": summary.get("settled"),
                "entry_net_cents": summary.get("net_cents"),
                "joined_exit_delta_cents": variant.get("joined_exit_delta_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
                "simulated_share": variant.get("reconstructed_share"),
                "live_ready": bool(variant.get("live_ready")),
                "blockers": variant.get("blockers") or [],
                "candidate_key": f"{gate}::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                source_flag: True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def collapse_reentry_registry_rows() -> list[dict[str, Any]]:
    payload = load_json(COLLAPSE_REENTRY_JSON)
    rows: list[dict[str, Any]] = []

    def blockers_for(settled: Any, net_cents: Any, extra: list[str] | None = None) -> list[str]:
        blockers = list(extra or [])
        settled_i = as_int(settled) or 0
        net_f = as_float(net_cents)
        if settled_i < 30:
            blockers.append("settled_lt_30")
        if net_f is None or net_f <= 0.0:
            blockers.append("net_not_positive")
        blockers.append("state_registry_watch_only")
        return blockers

    summary = payload.get("future_summary")
    if isinstance(summary, dict):
        actual = {
            "gate": "collapse_reentry_registry",
            "policy": "all_post_collapse_reentries_actual",
            "entries": summary.get("rows"),
            "settled": summary.get("closed"),
            "wins": summary.get("wins"),
            "losses": summary.get("losses"),
            "coverage_pct": None,
            "net_cents_after_entry_fee": summary.get("gross_cents"),
            "skip_delta_cents": summary.get("skip_delta_cents"),
            "open_rows": summary.get("open"),
            "live_ready": False,
            "blockers": blockers_for(summary.get("closed"), summary.get("gross_cents")),
            "candidate_key": "collapse_reentry_registry::all_post_collapse_reentries_actual",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_collapse_reentry_registry": True,
        }
        actual["target_coverage"] = in_target_coverage(actual)
        actual["has_settled_pnl"] = has_settled_pnl(actual)
        rows.append(actual)

        skip_all = {
            "gate": "collapse_reentry_registry",
            "policy": "skip_all_post_collapse_reentries",
            "entries": summary.get("rows"),
            "settled": summary.get("closed"),
            "wins": summary.get("losses"),
            "losses": summary.get("wins"),
            "coverage_pct": None,
            "net_cents_after_entry_fee": summary.get("skip_delta_cents"),
            "underlying_gross_cents": summary.get("gross_cents"),
            "open_rows": summary.get("open"),
            "live_ready": False,
            "blockers": blockers_for(
                summary.get("closed"),
                summary.get("skip_delta_cents"),
                ["would_skip_all_reentries"],
            ),
            "candidate_key": "collapse_reentry_registry::skip_all_post_collapse_reentries",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_collapse_reentry_registry": True,
        }
        skip_all["target_coverage"] = in_target_coverage(skip_all)
        skip_all["has_settled_pnl"] = has_settled_pnl(skip_all)
        rows.append(skip_all)

    for rollup in payload.get("future_tag_rollups") or []:
        if not isinstance(rollup, dict):
            continue
        tag = str(rollup.get("tag") or "unknown")
        policy = f"skip_reentry_tag_{tag}"
        row = {
            "gate": "collapse_reentry_registry",
            "policy": policy,
            "entries": rollup.get("rows"),
            "settled": rollup.get("closed"),
            "wins": rollup.get("losses"),
            "losses": rollup.get("wins"),
            "coverage_pct": None,
            "net_cents_after_entry_fee": rollup.get("skip_delta_cents"),
            "underlying_gross_cents": rollup.get("gross_cents"),
            "tag": tag,
            "live_ready": False,
            "blockers": blockers_for(
                rollup.get("closed"),
                rollup.get("skip_delta_cents"),
                [f"would_skip_tag:{tag}"],
            ),
            "candidate_key": f"collapse_reentry_registry::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_collapse_reentry_registry": True,
        }
        row["target_coverage"] = in_target_coverage(row)
        row["has_settled_pnl"] = has_settled_pnl(row)
        rows.append(row)
    return rows


def soft_frontier_size_shrink_rows() -> list[dict[str, Any]]:
    payload = load_json(SOFT_FRONTIER_SIZE_SHRINK_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        strict_forward = bool(lane.get("strict_forward"))
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("summary")
            if not isinstance(summary, dict):
                continue
            row = {
                "gate": "soft_frontier_size_shrink_portfolio",
                "policy": variant.get("candidate") or f"{lane_name}_{variant.get('weight_policy')}",
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "active_coverage_pct": summary.get("active_coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "raw_unweighted_net_cents": summary.get("raw_unweighted_net_cents"),
                "delta_vs_unweighted_cents": summary.get("delta_vs_unweighted_cents"),
                "avg_weight": summary.get("avg_weight"),
                "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
                "approved_entry_count": (variant.get("source_counts") or {}).get("approved_entry"),
                "added_reject_count": (
                    sum((variant.get("source_counts") or {}).values())
                    - int((variant.get("source_counts") or {}).get("approved_entry") or 0)
                ) if isinstance(variant.get("source_counts"), dict) else None,
                "simulated_share": variant.get("reconstructed_share"),
                "live_ready": bool(variant.get("live_ready")),
                "blockers": variant.get("blockers") or [],
                "strict_forward": strict_forward,
                "candidate_key": f"soft_frontier_size_shrink_portfolio::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_soft_frontier_size_shrink": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def soft_frontier_midprice_boundary_shrink_rows() -> list[dict[str, Any]]:
    payload = load_json(SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        strict_forward = bool(lane.get("strict_forward"))
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("summary")
            if not isinstance(summary, dict):
                continue
            source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
            approved = int(source_counts.get("approved_entry") or 0)
            total = sum(int(value or 0) for value in source_counts.values())
            row = {
                "gate": "soft_frontier_midprice_boundary_shrink",
                "policy": variant.get("candidate") or f"{lane_name}_{variant.get('weight_policy')}",
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "active_coverage_pct": summary.get("active_coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "raw_unweighted_net_cents": summary.get("raw_unweighted_net_cents"),
                "delta_vs_unweighted_cents": summary.get("delta_vs_unweighted_cents"),
                "midprice_boundary_rows": summary.get("midprice_boundary_rows"),
                "midprice_boundary_raw_net_cents": summary.get("midprice_boundary_raw_net_cents"),
                "midprice_boundary_weighted_net_cents": summary.get("midprice_boundary_weighted_net_cents"),
                "avg_weight": summary.get("avg_weight"),
                "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
                "approved_entry_count": approved if total else None,
                "added_reject_count": (total - approved) if total else None,
                "simulated_share": variant.get("reconstructed_share"),
                "live_ready": bool(variant.get("live_ready")),
                "blockers": variant.get("blockers") or [],
                "strict_forward": strict_forward,
                "candidate_key": f"soft_frontier_midprice_boundary_shrink::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_soft_frontier_midprice_boundary_shrink": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def midprice_source_dilution_rows() -> list[dict[str, Any]]:
    payload = load_json(MIDPRICE_SOURCE_DILUTION_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        strict_forward = bool(lane.get("strict_forward"))
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
            approved = int(source_counts.get("approved_entry") or 0)
            total = sum(int(value or 0) for value in source_counts.values())
            policy = f"{lane_name}_{variant.get('filter')}"
            row = {
                "gate": "midprice_source_dilution_watch",
                "policy": policy,
                "entries": variant.get("entries"),
                "settled": variant.get("settled"),
                "wins": variant.get("wins"),
                "losses": variant.get("losses"),
                "coverage_pct": variant.get("coverage_pct"),
                "net_cents_after_entry_fee": variant.get("net_cents"),
                "dropped_entries": variant.get("dropped_entries"),
                "dropped_net_cents": variant.get("dropped_net_cents"),
                "approved_entry_count": approved if total else None,
                "added_reject_count": (total - approved) if total else None,
                "simulated_share": variant.get("reconstructed_share"),
                "full_loss_cushion_estimate": variant.get("full_loss_cushion"),
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "strict_forward": strict_forward,
                "candidate_key": f"midprice_source_dilution_watch::{policy}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_midprice_source_dilution": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def p50_book_edge_no_side_shrink_rows() -> list[dict[str, Any]]:
    payload = load_json(P50_BOOK_EDGE_NO_SIDE_SHRINK_JSON)
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return []
    freeze = payload.get("freeze") if isinstance(payload.get("freeze"), dict) else {}
    row = {
        "gate": "p50_book_edge_no_side_shrink_watch",
        "policy": freeze.get("candidate") or "p50_book_plus_05_edge_nonnegative_quarter_no_side",
        "entries": summary.get("entries"),
        "settled": summary.get("settled"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents_after_entry_fee": summary.get("weighted_gross_cents"),
        "simulated_share": summary.get("weighted_rejected_actionable_share"),
        "approved_entry_count": summary.get("approved_entry_count"),
        "added_reject_count": summary.get("rejected_actionable_count"),
        "full_loss_cushion": summary.get("full_loss_cushion"),
        "live_ready": bool(payload.get("candidate_live_ready")),
        "blockers": payload.get("blockers") or [],
        "strict_forward": True,
        "candidate_key": "p50_book_edge_no_side_shrink_watch::p50_book_plus_05_edge_nonnegative_quarter_no_side",
        "source_readiness": False,
        "source_leaderboard": False,
        "source_p50_book_edge_no_side_shrink_watch": True,
    }
    return [finalise_report_row(row)]


def feature_gate_value_exit_watch_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_VALUE_EXIT_WATCH_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("label") or "")
        strict_forward = bool(lane.get("strict_forward"))
        for item in lane.get("variants") or []:
            if not isinstance(item, dict):
                continue
            policy = str(item.get("variant") or "")
            if not policy:
                continue
            row = {
                "gate": "frozen_feature_gate_value_exit_watch",
                "policy": f"{lane_name}_{policy}",
                "entries": item.get("settled"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": None,
                "net_cents_after_entry_fee": item.get("candidate_net_cents"),
                "avg_net_cents": None,
                "approved_entry_count": None,
                "added_reject_count": None,
                "simulated_share": None,
                "live_ready": False,
                "blockers": item.get("blockers") or [],
                "strict_forward": strict_forward,
                "full_loss_cushion_estimate": item.get("full_loss_cushion_estimate"),
                "candidate_key": f"frozen_feature_gate_value_exit_watch::{lane_name}::{policy}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_value_exit_watch": True,
            }
            rows.append(finalise_report_row(row))
    return rows


def value_exit_feature_side_guard_rows() -> list[dict[str, Any]]:
    payload = load_json(VALUE_EXIT_FEATURE_SIDE_GUARD_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("label") or "")
        summary = lane.get("summary") if isinstance(lane.get("summary"), dict) else {}
        if not summary:
            continue
        row = {
            "gate": "frozen_value_exit_feature_side_guard",
            "policy": f"{lane_name}_value_only_gap15_or_p75_feature_gate_same_side",
            "entries": summary.get("rows"),
            "settled": summary.get("rows"),
            "wins": summary.get("feature_side_guard_wins"),
            "losses": summary.get("feature_side_guard_losses"),
            "coverage_pct": None,
            "net_cents_after_entry_fee": summary.get("feature_side_guard_net_cents"),
            "avg_net_cents": None,
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "live_ready": False,
            "blockers": summary.get("blockers") or [],
            "strict_forward": bool(lane.get("strict_forward")),
            "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
            "candidate_key": f"frozen_value_exit_feature_side_guard::{lane_name}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_value_exit_feature_side_guard": True,
        }
        rows.append(finalise_report_row(row))
    return rows


def soft_frontier_midprice_boundary_exit_stack_rows(
    path: Path = SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON,
    gate: str = "soft_frontier_midprice_boundary_exit_stack",
    source_flag: str = "source_soft_frontier_midprice_boundary_exit_stack",
) -> list[dict[str, Any]]:
    payload = load_json(path)
    rows: list[dict[str, Any]] = []
    for variant in payload.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        summary = variant.get("entry_summary")
        if not isinstance(summary, dict):
            continue
        joined_rows = variant.get("joined_rows") if isinstance(variant.get("joined_rows"), list) else []
        source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
        row = {
            "gate": gate,
            "policy": variant.get("candidate") or variant.get("policy"),
            "entries": summary.get("entries"),
            "settled": variant.get("joined_exit_rows"),
            "wins": sum(1 for item in joined_rows if (as_float(item.get("weighted_exit_candidate_cents")) or as_float(item.get("weighted_candidate_cents")) or 0.0) >= 0.0),
            "losses": sum(1 for item in joined_rows if (as_float(item.get("weighted_exit_candidate_cents")) or as_float(item.get("weighted_candidate_cents")) or 0.0) < 0.0),
            "coverage_pct": summary.get("coverage_pct"),
            "net_cents_after_entry_fee": variant.get("weighted_joined_exit_candidate_cents", variant.get("weighted_candidate_cents")),
            "entry_settled": summary.get("settled"),
            "entry_net_cents": summary.get("net_cents"),
            "joined_exit_delta_cents": variant.get("weighted_joined_exit_delta_cents", variant.get("weighted_delta_cents")),
            "approved_entry_count": source_counts.get("approved_entry"),
            "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
            "simulated_share": variant.get("reconstructed_share"),
            "live_ready": bool(variant.get("live_ready")),
            "blockers": variant.get("blockers") or [],
            "strict_forward": variant.get("strict_forward"),
            "candidate_key": f"{gate}::{variant.get('candidate') or variant.get('policy')}",
            "source_readiness": False,
            "source_leaderboard": False,
            source_flag: True,
        }
        row["target_coverage"] = in_target_coverage(row)
        row["has_settled_pnl"] = has_settled_pnl(row)
        rows.append(row)
    return rows


def feature_gate_continuous_penalty_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_CONTINUOUS_PENALTY_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if not lane_name.startswith("post_penalty_birth_"):
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("candidate_summary")
            if not isinstance(summary, dict):
                continue
            source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
            row = {
                "gate": "boundary_clock_feature_gate_continuous_penalty",
                "policy": variant.get("candidate") or lane_name,
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "avg_net_cents": summary.get("avg_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": source_counts.get("rejected_actionable"),
                "simulated_share": variant.get("reconstructed_share"),
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "strict_forward": True,
                "full_loss_cushion_estimate": variant.get("full_loss_cushion_estimate"),
                "candidate_key": f"boundary_clock_feature_gate_continuous_penalty::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_continuous_penalty": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def feature_gate_soft_frontier_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_SOFT_FRONTIER_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if not lane_name.startswith("post_soft_frontier_birth_"):
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("candidate_summary")
            if not isinstance(summary, dict):
                continue
            source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
            row = {
                "gate": "boundary_clock_feature_gate_soft_frontier",
                "policy": variant.get("candidate") or lane_name,
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "avg_net_cents": summary.get("avg_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": source_counts.get("rejected_actionable"),
                "simulated_share": variant.get("reconstructed_share"),
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "full_loss_cushion_estimate": variant.get("full_loss_cushion_estimate"),
                "candidate_key": f"boundary_clock_feature_gate_soft_frontier::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_soft_frontier": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def feature_gate_clean_broad_frontier_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_CLEAN_BROAD_FRONTIER_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if not lane_name.startswith("post_clean_broad_freeze_"):
            continue
        summary = lane.get("candidate_summary")
        if not isinstance(summary, dict):
            continue
        source_counts = lane.get("source_counts") if isinstance(lane.get("source_counts"), dict) else {}
        row = {
            "gate": "boundary_clock_feature_gate_clean_broad_frontier",
            "policy": lane.get("candidate") or lane_name,
            "entries": summary.get("entries"),
            "settled": summary.get("settled"),
            "wins": summary.get("wins"),
            "losses": summary.get("losses"),
            "coverage_pct": summary.get("coverage_pct"),
            "net_cents_after_entry_fee": summary.get("net_cents"),
            "avg_net_cents": summary.get("avg_net_cents"),
            "approved_entry_count": source_counts.get("approved_entry"),
            "added_reject_count": source_counts.get("rejected_actionable"),
            "simulated_share": lane.get("reconstructed_share"),
            "live_ready": False,
            "blockers": lane.get("blockers") or [],
            "full_loss_cushion_estimate": lane.get("full_loss_cushion_estimate"),
            "candidate_key": f"boundary_clock_feature_gate_clean_broad_frontier::{lane.get('candidate') or lane_name}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_feature_gate_clean_broad_frontier": True,
        }
        row["target_coverage"] = in_target_coverage(row)
        row["has_settled_pnl"] = has_settled_pnl(row)
        out.append(row)
    return out


def feature_gate_cheap_tail_quarantine_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_CHEAP_TAIL_QUARANTINE_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if not lane_name.startswith("post_quarantine_freeze_"):
            continue
        for group_name, group_gate in [
            ("core_rules", "feature_gate_quarantine_core"),
            ("tail_rules", "feature_gate_quarantine_tail"),
        ]:
            for variant in lane.get(group_name) or []:
                if not isinstance(variant, dict):
                    continue
                summary = variant.get("summary")
                if not isinstance(summary, dict):
                    continue
                source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
                row = {
                    "gate": group_gate,
                    "policy": f"{lane_name}_{variant.get('label')}",
                    "entries": summary.get("entries"),
                    "settled": summary.get("settled"),
                    "wins": summary.get("wins"),
                    "losses": summary.get("losses"),
                    "coverage_pct": summary.get("coverage_pct"),
                    "net_cents_after_entry_fee": summary.get("net_cents"),
                    "avg_net_cents": summary.get("avg_net_cents"),
                    "approved_entry_count": source_counts.get("approved_entry"),
                    "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
                    "simulated_share": variant.get("reconstructed_share"),
                    "top_win_cents": variant.get("top_win_cents"),
                    "net_without_top_win_cents": variant.get("net_without_top_win_cents"),
                    "full_loss_cushion_estimate": variant.get("full_loss_cushion_estimate"),
                    "live_ready": bool(variant.get("ready")),
                    "blockers": variant.get("blockers") or [],
                    "candidate_key": f"{group_gate}::{lane_name}_{variant.get('label')}",
                    "source_readiness": False,
                    "source_leaderboard": False,
                    "source_feature_gate_cheap_tail_quarantine": True,
                }
                row["target_coverage"] = in_target_coverage(row)
                row["has_settled_pnl"] = has_settled_pnl(row)
                out.append(row)
    return out


def feature_gate_cheap_tail_shrink_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_CHEAP_TAIL_SHRINK_WATCH_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for policy in lane.get("policies") or []:
            if not isinstance(policy, dict):
                continue
            source_counts = policy.get("source_counts") if isinstance(policy.get("source_counts"), dict) else {}
            approved = int(source_counts.get("approved_entry") or 0)
            total = sum(int(value or 0) for value in source_counts.values())
            row = {
                "gate": "feature_gate_cheap_tail_shrink",
                "policy": f"{lane_name}_{policy.get('policy')}",
                "entries": policy.get("entries"),
                "settled": policy.get("settled"),
                "wins": policy.get("wins"),
                "losses": policy.get("losses"),
                "coverage_pct": policy.get("coverage_pct"),
                "net_cents_after_entry_fee": policy.get("weighted_net_cents"),
                "total_notional_weight": policy.get("total_notional_weight"),
                "weighted_reconstructed_share": policy.get("weighted_reconstructed_share"),
                "cheap_rows": policy.get("cheap_rows"),
                "cheap_net_cents": policy.get("cheap_net_cents"),
                "full_loss_cushion_estimate": policy.get("full_loss_cushion_estimate"),
                "approved_entry_count": approved if total else None,
                "added_reject_count": (total - approved) if total else None,
                "simulated_share": policy.get("row_reconstructed_share"),
                "live_ready": False,
                "blockers": policy.get("blockers") or [],
                "strict_forward": True,
                "candidate_key": f"feature_gate_cheap_tail_shrink::{lane_name}_{policy.get('policy')}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_cheap_tail_shrink": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def feature_gate_core_expansion_mix_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_CORE_EXPANSION_MIX_JSON)
    rows: list[dict[str, Any]] = []
    for mix in payload.get("rows") or []:
        if not isinstance(mix, dict):
            continue
        policy = mix.get("policy")
        if not policy:
            continue
        row = {
            "gate": "feature_gate_core_expansion_mix",
            "policy": str(policy),
            "entries": mix.get("entries"),
            "settled": mix.get("settled"),
            "wins": mix.get("wins"),
            "losses": mix.get("losses"),
            "coverage_pct": mix.get("coverage_pct"),
            "net_cents_after_entry_fee": mix.get("weighted_net_cents"),
            "avg_net_cents": mix.get("avg_weighted_net_cents"),
            "simulated_share": mix.get("row_source_share"),
            "row_source_share": mix.get("row_source_share"),
            "exposure_source_share": mix.get("exposure_source_share"),
            "full_loss_cushion_estimate": mix.get("full_loss_cushion"),
            "live_ready": bool(mix.get("live_ready")),
            "blockers": mix.get("blockers") or [],
            "strict_forward": True,
            "candidate_key": f"feature_gate_core_expansion_mix::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_feature_gate_core_expansion_mix": True,
        }
        row["target_coverage"] = in_target_coverage(row)
        row["has_settled_pnl"] = has_settled_pnl(row)
        rows.append(row)
    return rows


def feature_gate_coverage_size_shrink_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_COVERAGE_SIZE_SHRINK_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for item in lane.get("rows") or []:
            if not isinstance(item, dict):
                continue
            policy = item.get("policy")
            if not policy:
                continue
            row = {
                "gate": "feature_gate_coverage_size_shrink",
                "policy": f"{lane_name}_{policy}",
                "entries": item.get("entries"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": item.get("coverage_pct"),
                "net_cents_after_entry_fee": item.get("weighted_net_cents"),
                "avg_net_cents": item.get("avg_weighted_net_cents"),
                "simulated_share": item.get("row_reconstructed_share"),
                "row_source_share": item.get("row_reconstructed_share"),
                "exposure_source_share": item.get("exposure_reconstructed_share"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion"),
                "live_ready": bool(item.get("live_ready")),
                "blockers": item.get("blockers") or [],
                "strict_forward": True,
                "candidate_key": f"feature_gate_coverage_size_shrink::{lane_name}::{policy}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_coverage_size_shrink": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def feature_gate_middle_distance_core_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_MIDDLE_DISTANCE_CORE_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        strict_forward = lane_name.startswith("post_middle_core_freeze")
        for item in lane.get("rules") or []:
            if not isinstance(item, dict):
                continue
            summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
            source_counts = item.get("source_counts") if isinstance(item.get("source_counts"), dict) else {}
            row = {
                "gate": "feature_gate_middle_distance_core_watch",
                "policy": f"{lane_name}_{item.get('rule')}",
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "avg_net_cents": summary.get("avg_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (
                    sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)
                ) if source_counts else None,
                "simulated_share": item.get("reconstructed_share"),
                "row_source_share": item.get("reconstructed_share"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion_estimate"),
                "top_win_cents": item.get("top_win_cents"),
                "net_without_top_win_cents": item.get("net_without_top_win_cents"),
                "live_ready": bool(item.get("live_ready")),
                "blockers": item.get("blockers") or [],
                "strict_forward": strict_forward,
                "candidate_key": f"feature_gate_middle_distance_core_watch::{lane_name}::{item.get('rule')}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_middle_distance_core_watch": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def feature_gate_middle_core_exit_guard_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_MIDDLE_CORE_EXIT_GUARD_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for item in lane.get("variants") or []:
            if not isinstance(item, dict):
                continue
            row = {
                "gate": "feature_gate_middle_core_exit_guard_watch",
                "policy": f"{lane_name}_{item.get('variant')}",
                "entries": item.get("entries"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": item.get("coverage_pct"),
                "net_cents_after_entry_fee": item.get("candidate_net_cents"),
                "avg_net_cents": None,
                "simulated_share": item.get("source_share"),
                "row_source_share": item.get("source_share"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion"),
                "entry_hold_net_cents": item.get("entry_hold_net_cents"),
                "current_exit_net_cents": item.get("current_exit_net_cents"),
                "delta_vs_current_exit_cents": item.get("delta_vs_current_exit_cents"),
                "joined_exit_rows": item.get("joined_exit_rows"),
                "suppressed_rows": item.get("suppressed_rows"),
                "live_ready": bool(item.get("live_ready")),
                "blockers": item.get("blockers") or [],
                "strict_forward": bool(item.get("strict_forward")),
                "candidate_key": f"feature_gate_middle_core_exit_guard_watch::{lane_name}::{item.get('variant')}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_middle_core_exit_guard_watch": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def feature_gate_observable_selection_mix_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_OBSERVABLE_SELECTION_MIX_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for item in lane.get("top_variants") or []:
            if not isinstance(item, dict):
                continue
            source_counts = item.get("source_counts") if isinstance(item.get("source_counts"), dict) else {}
            row = {
                "gate": "feature_gate_observable_selection_mix",
                "policy": f"{lane_name}_{item.get('candidate_id')}",
                "entries": item.get("entries"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": item.get("coverage_pct"),
                "net_cents_after_entry_fee": item.get("weighted_net_cents"),
                "avg_net_cents": item.get("avg_weighted_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
                "simulated_share": item.get("row_reconstructed_share"),
                "row_source_share": item.get("row_reconstructed_share"),
                "exposure_source_share": item.get("exposure_reconstructed_share"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion"),
                "live_ready": bool(item.get("live_ready")),
                "blockers": item.get("blockers") or [],
                "strict_forward": True,
                "candidate_key": f"feature_gate_observable_selection_mix::{lane_name}::{item.get('candidate_id')}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_observable_selection_mix": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def feature_gate_size_shrink_exit_overlay_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_SIZE_SHRINK_EXIT_OVERLAY_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for item in lane.get("variants") or []:
            if not isinstance(item, dict):
                continue
            source_counts = item.get("source_counts") if isinstance(item.get("source_counts"), dict) else {}
            row = {
                "gate": "feature_gate_size_shrink_exit_overlay",
                "policy": f"{lane_name}_{item.get('policy')}",
                "entries": item.get("entries"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": item.get("coverage_pct"),
                "net_cents_after_entry_fee": item.get("weighted_candidate_net_cents"),
                "avg_net_cents": None,
                "entry_net_cents": item.get("weighted_entry_hold_net_cents"),
                "joined_exit_delta_cents": item.get("delta_vs_current_exit_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
                "simulated_share": item.get("row_reconstructed_share"),
                "row_source_share": item.get("row_reconstructed_share"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion"),
                "live_ready": bool(item.get("live_ready")),
                "blockers": item.get("blockers") or [],
                "strict_forward": True,
                "candidate_key": f"feature_gate_size_shrink_exit_overlay::{lane_name}::{item.get('policy')}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_size_shrink_exit_overlay": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def feature_gate_size_shrink_delayed_recheck_exit_rows() -> list[dict[str, Any]]:
    return feature_gate_size_shrink_delayed_recheck_rows(
        FEATURE_GATE_SIZE_SHRINK_DELAYED_RECHECK_EXIT_JSON,
        "feature_gate_size_shrink_delayed_recheck_exit",
        "source_feature_gate_size_shrink_delayed_recheck_exit",
    )


def feature_gate_size_shrink_delayed_recheck_rescue_rows() -> list[dict[str, Any]]:
    return feature_gate_size_shrink_delayed_recheck_rows(
        FEATURE_GATE_SIZE_SHRINK_DELAYED_RECHECK_RESCUE_JSON,
        "feature_gate_size_shrink_delayed_recheck_rescue",
        "source_feature_gate_size_shrink_delayed_recheck_rescue",
    )


def feature_gate_late_collapse_recheck_rescue_rows() -> list[dict[str, Any]]:
    return feature_gate_size_shrink_delayed_recheck_rows(
        FEATURE_GATE_LATE_COLLAPSE_RECHECK_RESCUE_JSON,
        "feature_gate_late_collapse_recheck_rescue",
        "source_feature_gate_late_collapse_recheck_rescue",
    )


def feature_gate_dual_clock_recheck_rescue_rows() -> list[dict[str, Any]]:
    return feature_gate_size_shrink_delayed_recheck_rows(
        FEATURE_GATE_DUAL_CLOCK_RECHECK_RESCUE_JSON,
        "feature_gate_dual_clock_recheck_rescue",
        "source_feature_gate_dual_clock_recheck_rescue",
    )


def feature_gate_confirmed_dual_clock_fill_rows() -> list[dict[str, Any]]:
    return feature_gate_size_shrink_delayed_recheck_rows(
        FEATURE_GATE_CONFIRMED_DUAL_CLOCK_FILL_JSON,
        "feature_gate_confirmed_dual_clock_fill",
        "source_feature_gate_confirmed_dual_clock_fill",
    )


def feature_gate_size_shrink_delayed_recheck_rows(path: Path, gate: str, source_flag: str) -> list[dict[str, Any]]:
    payload = load_json(path)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        strict_forward = bool(lane.get("strict_forward"))
        for item in lane.get("variants") or []:
            if not isinstance(item, dict):
                continue
            variant = item.get("variant") if isinstance(item.get("variant"), dict) else {}
            source_counts = item.get("source_counts") if isinstance(item.get("source_counts"), dict) else {}
            row = {
                "gate": gate,
                "policy": f"{lane_name}_{variant.get('name')}",
                "entries": item.get("entries"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": item.get("coverage_pct"),
                "net_cents_after_entry_fee": item.get("candidate_net_cents"),
                "avg_net_cents": None,
                "entry_net_cents": item.get("entry_hold_net_cents"),
                "current_exit_net_cents": item.get("current_exit_net_cents"),
                "delta_vs_current_cents": item.get("delta_vs_current_exit_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
                "simulated_share": item.get("reconstructed_share"),
                "row_source_share": item.get("reconstructed_share"),
                "suppressed_exits": item.get("suppressed_rows"),
                "suppressed_delta_cents": item.get("suppressed_delta_cents"),
                "helpful_suppressions": item.get("helpful_suppressed"),
                "harmful_suppressions": item.get("harmful_suppressed"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion"),
                "live_ready": False,
                "blockers": item.get("blockers") or [],
                "strict_forward": strict_forward,
                "candidate_key": f"{gate}::{lane_name}::{variant.get('name')}",
                "source_readiness": False,
                "source_leaderboard": False,
                source_flag: True,
            }
            rows.append(finalise_report_row(row))
    return rows


def feature_gate_source_confirmation_replacement_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_SOURCE_CONFIRMATION_REPLACEMENT_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        repl = lane.get("replacement_entry_summary") if isinstance(lane.get("replacement_entry_summary"), dict) else {}
        best = lane.get("replacement_rescue_best") if isinstance(lane.get("replacement_rescue_best"), dict) else {}
        if not best:
            continue
        source_counts = repl.get("source_counts") if isinstance(repl.get("source_counts"), dict) else {}
        variant = best.get("variant") if isinstance(best.get("variant"), dict) else {}
        row = {
            "gate": "feature_gate_source_confirmation_replacement",
            "policy": f"{lane_name}_{variant.get('name')}",
            "entries": repl.get("entries"),
            "settled": repl.get("settled"),
            "wins": best.get("wins"),
            "losses": best.get("losses"),
            "coverage_pct": repl.get("coverage_pct"),
            "net_cents_after_entry_fee": best.get("candidate_net_cents_conservative_entry_adjusted"),
            "avg_net_cents": None,
            "entry_net_cents": repl.get("weighted_entry_hold_net_cents"),
            "approved_entry_count": source_counts.get("approved_entry"),
            "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
            "simulated_share": repl.get("reconstructed_share"),
            "row_source_share": repl.get("reconstructed_share"),
            "suppressed_exits": best.get("suppressed_rows"),
            "suppressed_delta_cents": best.get("suppressed_delta_cents"),
            "helpful_suppressions": best.get("helpful_suppressed"),
            "harmful_suppressions": best.get("harmful_suppressed"),
            "full_loss_cushion_estimate": int(max(0.0, float(best.get("candidate_net_cents_conservative_entry_adjusted") or 0.0)) // 100.0),
            "live_ready": False,
            "blockers": best.get("blockers") or [],
            "strict_forward": bool(lane.get("strict_forward")),
            "candidate_key": f"feature_gate_source_confirmation_replacement::{lane_name}::{variant.get('name')}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_feature_gate_source_confirmation_replacement": True,
        }
        rows.append(finalise_report_row(row))
    return rows


def feature_gate_source_quality_proxy_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_SOURCE_QUALITY_PROXY_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        strict_forward = bool(lane.get("strict_forward"))
        variants = lane.get("top_variants") or []
        if strict_forward:
            variants = lane.get("watch_variants") or variants
        for item in variants:
            if not isinstance(item, dict):
                continue
            source_counts = item.get("source_counts") if isinstance(item.get("source_counts"), dict) else {}
            row = {
                "gate": "feature_gate_source_quality_proxy",
                "policy": f"{lane_name}_{item.get('candidate_id')}",
                "entries": item.get("entries"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": item.get("coverage_pct"),
                "net_cents_after_entry_fee": item.get("weighted_net_cents"),
                "avg_net_cents": item.get("avg_weighted_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
                "simulated_share": item.get("row_reconstructed_share"),
                "row_source_share": item.get("row_reconstructed_share"),
                "exposure_source_share": item.get("exposure_reconstructed_share"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion"),
                "live_ready": bool(item.get("live_ready")),
                "blockers": item.get("blockers") or [],
                "strict_forward": strict_forward,
                "candidate_key": f"feature_gate_source_quality_proxy::{lane_name}::{item.get('candidate_id')}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_source_quality_proxy": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def feature_gate_source_proxy_coverage_repair_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_SOURCE_PROXY_COVERAGE_REPAIR_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        strict_forward = bool(lane.get("strict_forward"))
        for item in lane.get("top_variants") or []:
            if not isinstance(item, dict):
                continue
            source_counts = item.get("source_counts") if isinstance(item.get("source_counts"), dict) else {}
            row = {
                "gate": "feature_gate_source_proxy_coverage_repair",
                "policy": f"{lane_name}_{item.get('candidate_id')}",
                "entries": item.get("entries"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": item.get("coverage_pct"),
                "net_cents_after_entry_fee": item.get("weighted_net_cents"),
                "avg_net_cents": item.get("avg_weighted_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (sum(source_counts.values()) - int(source_counts.get("approved_entry") or 0)) if source_counts else None,
                "simulated_share": item.get("row_reconstructed_share"),
                "row_source_share": item.get("row_reconstructed_share"),
                "exposure_source_share": item.get("exposure_reconstructed_share"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion"),
                "live_ready": bool(item.get("live_ready")),
                "blockers": item.get("blockers") or [],
                "strict_forward": strict_forward,
                "candidate_key": f"feature_gate_source_proxy_coverage_repair::{lane_name}::{item.get('candidate_id')}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_feature_gate_source_proxy_coverage_repair": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            rows.append(row)
    return rows


def target_cluster_source_aware_rows() -> list[dict[str, Any]]:
    payload = load_json(TARGET_CLUSTER_SOURCE_AWARE_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if lane_name != "post_source_aware_birth":
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("candidate_summary")
            if not isinstance(summary, dict):
                continue
            source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
            approved = int(source_counts.get("approved_entry") or 0)
            total = sum(int(value or 0) for value in source_counts.values())
            row = {
                "gate": "target_cluster_penalty_source_aware",
                "policy": variant.get("candidate") or lane_name,
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "avg_net_cents": summary.get("avg_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (total - approved) if total else None,
                "simulated_share": variant.get("reconstructed_share"),
                "full_loss_cushion_estimate": variant.get("full_loss_cushion_estimate"),
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "candidate_key": f"target_cluster_penalty_source_aware::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_target_cluster_penalty_source_aware": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def target_cluster_observable_stability_rows() -> list[dict[str, Any]]:
    payload = load_json(TARGET_CLUSTER_OBSERVABLE_STABILITY_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if lane_name != "post_observable_proxy_birth":
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("candidate_summary")
            if not isinstance(summary, dict):
                continue
            source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
            approved = int(source_counts.get("approved_entry") or 0)
            total = sum(int(value or 0) for value in source_counts.values())
            row = {
                "gate": "target_cluster_penalty_observable_stability",
                "policy": variant.get("candidate") or lane_name,
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "avg_net_cents": summary.get("avg_net_cents"),
                "approved_entry_count": source_counts.get("approved_entry"),
                "added_reject_count": (total - approved) if total else None,
                "simulated_share": variant.get("reconstructed_share"),
                "full_loss_cushion_estimate": variant.get("full_loss_cushion_estimate"),
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "candidate_key": f"target_cluster_penalty_observable_stability::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_target_cluster_penalty_observable_stability": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def exit_reduce_refinement_rows() -> list[dict[str, Any]]:
    payload = load_json(EXIT_REDUCE_REFINEMENT_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if lane_name != "post_refinement_birth":
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("summary")
            if not isinstance(summary, dict):
                continue
            row = {
                "gate": "exit_reduce_loss_control_refinement",
                "policy": variant.get("candidate") or lane_name,
                "entries": summary.get("settled"),
                "settled": summary.get("settled"),
                "wins": summary.get("candidate_wins"),
                "losses": summary.get("candidate_losses"),
                "coverage_pct": None,
                "net_cents_after_entry_fee": summary.get("candidate_gross_cents"),
                "avg_net_cents": None,
                "approved_entry_count": None,
                "added_reject_count": None,
                "simulated_share": None,
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
                "candidate_key": f"exit_reduce_loss_control_refinement::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_exit_reduce_refinement": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def exit_reduce_depth_gate_rows() -> list[dict[str, Any]]:
    payload = load_json(EXIT_REDUCE_DEPTH_GATE_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if lane_name != "post_depth_gate_birth":
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("summary")
            if not isinstance(summary, dict):
                continue
            row = {
                "gate": "exit_reduce_depth_gate",
                "policy": variant.get("candidate") or lane_name,
                "entries": summary.get("settled"),
                "settled": summary.get("settled"),
                "wins": summary.get("candidate_wins"),
                "losses": summary.get("candidate_losses"),
                "coverage_pct": None,
                "net_cents_after_entry_fee": summary.get("candidate_gross_cents"),
                "avg_net_cents": None,
                "approved_entry_count": None,
                "added_reject_count": None,
                "simulated_share": None,
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
                "candidate_key": f"exit_reduce_depth_gate::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_exit_reduce_depth_gate": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def exit_reduce_observable_loss_control_rows() -> list[dict[str, Any]]:
    payload = load_json(EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_JSON)
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if lane_name != "post_observable_birth":
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("summary")
            if not isinstance(summary, dict):
                continue
            row = {
                "gate": "exit_reduce_observable_loss_control",
                "policy": variant.get("candidate") or lane_name,
                "entries": summary.get("settled"),
                "settled": summary.get("settled"),
                "wins": summary.get("candidate_wins"),
                "losses": summary.get("candidate_losses"),
                "coverage_pct": None,
                "net_cents_after_entry_fee": summary.get("candidate_gross_cents"),
                "avg_net_cents": None,
                "approved_entry_count": None,
                "added_reject_count": None,
                "simulated_share": None,
                "live_ready": False,
                "blockers": variant.get("blockers") or [],
                "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
                "candidate_key": f"exit_reduce_observable_loss_control::{variant.get('candidate') or lane_name}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_exit_reduce_observable_loss_control": True,
            }
            row["target_coverage"] = in_target_coverage(row)
            row["has_settled_pnl"] = has_settled_pnl(row)
            out.append(row)
    return out


def feature_gate_exit_bid_suppression_watch_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_EXIT_BID_SUPPRESSION_WATCH_JSON)
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if lane_name != "post_exit_bid_birth":
            continue
        summary = lane.get("summary")
        if not isinstance(summary, dict):
            continue
        policy = state.get("candidate") or lane_name
        row = {
            "gate": "feature_gate_exit_bid_suppression_watch",
            "policy": policy,
            "entries": summary.get("settled"),
            "settled": summary.get("settled"),
            "wins": summary.get("candidate_wins"),
            "losses": summary.get("candidate_losses"),
            "coverage_pct": None,
            "net_cents_after_entry_fee": summary.get("candidate_net_cents"),
            "avg_net_cents": None,
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "delta_vs_current_cents": summary.get("delta_vs_live_cents"),
            "suppressed_exits": summary.get("suppressed_exits"),
            "suppressed_delta_cents": summary.get("delta_vs_live_cents"),
            "helpful_suppressions": summary.get("suppressed_helpful"),
            "harmful_suppressions": summary.get("suppressed_harmful"),
            "loss_control_cost_cents": summary.get("loss_control_cost_cents"),
            "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
            "live_ready": False,
            "blockers": summary.get("blockers") or [],
            "candidate_key": f"feature_gate_exit_bid_suppression_watch::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_feature_gate_exit_bid_suppression_watch": True,
        }
        out.append(finalise_report_row(row))
    return out


def feature_gate_exit_bid_delayed_recheck_rows() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_GATE_EXIT_BID_DELAYED_RECHECK_JSON)
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if lane_name != "post_delayed_recheck_birth":
            continue
        summary = lane.get("summary")
        if not isinstance(summary, dict):
            continue
        policy = state.get("candidate") or lane_name
        row = {
            "gate": "feature_gate_exit_bid_delayed_recheck",
            "policy": policy,
            "entries": summary.get("rows"),
            "settled": summary.get("rows"),
            "wins": summary.get("candidate_wins"),
            "losses": summary.get("candidate_losses"),
            "coverage_pct": None,
            "net_cents_after_entry_fee": summary.get("candidate_net_cents"),
            "avg_net_cents": None,
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "delta_vs_current_cents": summary.get("delta_vs_live_cents"),
            "suppressed_exits": summary.get("suppressed"),
            "suppressed_delta_cents": summary.get("delta_vs_live_cents"),
            "helpful_suppressions": summary.get("helpful_suppressed"),
            "harmful_suppressions": summary.get("harmful_suppressed"),
            "loss_control_cost_cents": summary.get("loss_cost_cents"),
            "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
            "live_ready": False,
            "blockers": summary.get("blockers") or [],
            "strict_forward": bool(summary.get("strict_forward")),
            "candidate_key": f"feature_gate_exit_bid_delayed_recheck::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_feature_gate_exit_bid_delayed_recheck": True,
        }
        out.append(finalise_report_row(row))
    return out


def soft_frontier_midprice_delayed_recheck_exit_rows() -> list[dict[str, Any]]:
    payload = load_json(SOFT_FRONTIER_MIDPRICE_DELAYED_RECHECK_EXIT_JSON)
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    parent = payload.get("diagnostic_parent") if isinstance(payload.get("diagnostic_parent"), dict) else {}
    entry_summary = parent.get("entry_summary") if isinstance(parent.get("entry_summary"), dict) else {}
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        summary = lane.get("summary") if isinstance(lane.get("summary"), dict) else {}
        if not summary:
            continue
        source_counts = summary.get("source_counts") if isinstance(summary.get("source_counts"), dict) else {}
        total = sum(int(value or 0) for value in source_counts.values()) if source_counts else 0
        approved = int(source_counts.get("approved_entry") or 0) if source_counts else None
        policy = (
            f"{lane_name}_{state.get('entry_policy')}_"
            f"{state.get('exit_source')}_{state.get('recheck_policy')}"
        )
        row = {
            "gate": "soft_frontier_midprice_delayed_recheck_exit",
            "policy": policy,
            "entries": summary.get("rows"),
            "settled": summary.get("rows"),
            "wins": summary.get("candidate_wins"),
            "losses": summary.get("candidate_losses"),
            "coverage_pct": entry_summary.get("coverage_pct") if lane_name == "diagnostic_prefreeze_context" else None,
            "net_cents_after_entry_fee": summary.get("weighted_candidate_cents"),
            "avg_net_cents": None,
            "approved_entry_count": approved,
            "added_reject_count": (total - approved) if source_counts and approved is not None else None,
            "simulated_share": summary.get("reconstructed_share"),
            "delta_vs_current_cents": summary.get("weighted_delta_cents"),
            "suppressed_exits": summary.get("suppressed"),
            "helpful_suppressed": summary.get("helpful_suppressed"),
            "harmful_suppressed": summary.get("harmful_suppressed"),
            "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
            "live_ready": False,
            "strict_forward": bool(summary.get("strict_forward")),
            "blockers": summary.get("blockers") or [],
            "candidate_key": f"soft_frontier_midprice_delayed_recheck_exit::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_soft_frontier_midprice_delayed_recheck_exit": True,
        }
        out.append(finalise_report_row(row))
    return out


def soft_frontier_midprice_delayed_recheck_rescue_rows() -> list[dict[str, Any]]:
    payload = load_json(SOFT_FRONTIER_MIDPRICE_DELAYED_RECHECK_RESCUE_JSON)
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    parent = payload.get("diagnostic_parent") if isinstance(payload.get("diagnostic_parent"), dict) else {}
    entry_summary = parent.get("entry_summary") if isinstance(parent.get("entry_summary"), dict) else {}
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        summary = lane.get("summary") if isinstance(lane.get("summary"), dict) else {}
        if not summary:
            continue
        source_counts = summary.get("source_counts") if isinstance(summary.get("source_counts"), dict) else {}
        total = sum(int(value or 0) for value in source_counts.values()) if source_counts else 0
        approved = int(source_counts.get("approved_entry") or 0) if source_counts else None
        policy = (
            f"{lane_name}_{state.get('entry_policy')}_"
            f"{state.get('exit_source')}_{state.get('recheck_policy')}"
        )
        row = {
            "gate": "soft_frontier_midprice_delayed_recheck_rescue",
            "policy": policy,
            "entries": summary.get("rows"),
            "settled": summary.get("rows"),
            "wins": summary.get("candidate_wins"),
            "losses": summary.get("candidate_losses"),
            "coverage_pct": entry_summary.get("coverage_pct") if lane_name == "diagnostic_prefreeze_context" else None,
            "net_cents_after_entry_fee": summary.get("weighted_candidate_cents"),
            "avg_net_cents": None,
            "approved_entry_count": approved,
            "added_reject_count": (total - approved) if source_counts and approved is not None else None,
            "simulated_share": summary.get("reconstructed_share"),
            "delta_vs_current_cents": summary.get("weighted_delta_cents"),
            "suppressed_exits": summary.get("suppressed"),
            "helpful_suppressed": summary.get("helpful_suppressed"),
            "harmful_suppressed": summary.get("harmful_suppressed"),
            "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
            "live_ready": False,
            "strict_forward": bool(summary.get("strict_forward")),
            "blockers": summary.get("blockers") or [],
            "candidate_key": f"soft_frontier_midprice_delayed_recheck_rescue::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_soft_frontier_midprice_delayed_recheck_rescue": True,
        }
        out.append(finalise_report_row(row))
    return out


def top_component_mix_portfolio_rows() -> list[dict[str, Any]]:
    payload = load_json(TOP_COMPONENT_MIX_PORTFOLIO_JSON)
    out: list[dict[str, Any]] = []
    for item in payload.get("variants") or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "")
        if not label:
            continue
        source_counts = item.get("source_counts") if isinstance(item.get("source_counts"), dict) else {}
        total = sum(int(value or 0) for value in source_counts.values()) if source_counts else 0
        approved = int(source_counts.get("approved_entry") or 0) if source_counts else None
        row = {
            "gate": "top_component_mix_portfolio",
            "policy": label,
            "entries": item.get("entries"),
            "settled": item.get("settled"),
            "wins": item.get("wins"),
            "losses": item.get("losses"),
            "coverage_pct": item.get("coverage_pct"),
            "net_cents_after_entry_fee": item.get("net_cents"),
            "delta_vs_live_cents": item.get("delta_vs_live_cents"),
            "approved_entry_count": approved,
            "added_reject_count": (total - approved) if source_counts and approved is not None else None,
            "simulated_share": item.get("reconstructed_share"),
            "suppressed_exits": item.get("suppressed_rows"),
            "helpful_suppressed": item.get("helpful_suppressed"),
            "harmful_suppressed": item.get("harmful_suppressed"),
            "filler_rows": item.get("filler_rows"),
            "filler_net_cents": item.get("filler_net_cents"),
            "full_loss_cushion_estimate": item.get("full_loss_cushion"),
            "stress_without_top_row_delta_vs_live_cents": item.get("stress_without_top_row_delta_vs_live_cents"),
            "stress_without_suppression_delta_vs_live_cents": item.get("stress_without_suppression_delta_vs_live_cents"),
            "live_ready": False,
            "strict_forward": False,
            "blockers": item.get("blockers") or [],
            "candidate_key": f"top_component_mix_portfolio::{label}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_top_component_mix_portfolio": True,
        }
        out.append(finalise_report_row(row))
    return out


def top_component_false_negative_rescue_rows() -> list[dict[str, Any]]:
    payload = load_json(TOP_COMPONENT_FALSE_NEGATIVE_RESCUE_JSON)
    out: list[dict[str, Any]] = []
    for item in payload.get("variants") or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "")
        if not label:
            continue
        row = {
            "gate": "top_component_false_negative_rescue_child",
            "policy": label,
            "entries": item.get("entries"),
            "settled": item.get("settled"),
            "wins": item.get("wins"),
            "losses": item.get("losses"),
            "coverage_pct": item.get("coverage_pct"),
            "net_cents_after_entry_fee": item.get("net_cents"),
            "delta_vs_live_cents": item.get("delta_vs_live_cents"),
            "delta_vs_parent_cents": item.get("delta_vs_parent_cents"),
            "simulated_share": item.get("reconstructed_share"),
            "suppressed_exits": item.get("rescued_rows"),
            "helpful_suppressed": item.get("helpful_rescues"),
            "harmful_suppressed": item.get("harmful_rescues"),
            "suppressed_delta_cents": item.get("delta_vs_parent_cents"),
            "full_loss_cushion_estimate": item.get("full_loss_cushion"),
            "live_ready": False,
            "strict_forward": bool(item.get("strict_forward")),
            "blockers": item.get("blockers") or [],
            "candidate_key": f"top_component_false_negative_rescue_child::{label}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_top_component_false_negative_rescue_child": True,
        }
        out.append(finalise_report_row(row))
    return out


def top_component_parent_fill_repair_rows() -> list[dict[str, Any]]:
    payload = load_json(TOP_COMPONENT_PARENT_FILL_REPAIR_JSON)
    out: list[dict[str, Any]] = []
    for item in payload.get("variants") or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "")
        if not label:
            continue
        row = {
            "gate": "top_component_parent_fill_repair_child",
            "policy": label,
            "entries": item.get("entries"),
            "settled": item.get("settled"),
            "wins": item.get("wins"),
            "losses": item.get("losses"),
            "coverage_pct": item.get("coverage_pct"),
            "net_cents_after_entry_fee": item.get("net_cents"),
            "delta_vs_live_cents": item.get("delta_vs_live_cents"),
            "simulated_share": item.get("reconstructed_share"),
            "suppressed_exits": item.get("exit_child_rescues"),
            "helpful_suppressed": item.get("exit_child_rescues"),
            "harmful_suppressed": 0,
            "suppressed_delta_cents": item.get("exit_child_delta_cents"),
            "parent_fill_rows": item.get("parent_fill_rows"),
            "parent_fill_net_cents": item.get("parent_fill_net_cents"),
            "shrunk_parent_fill_rows": item.get("shrunk_parent_fill_rows"),
            "parent_fill_shrink_delta_cents": item.get("parent_fill_shrink_delta_cents"),
            "full_loss_cushion_estimate": item.get("full_loss_cushion"),
            "live_ready": False,
            "strict_forward": bool(item.get("strict_forward")),
            "blockers": item.get("blockers") or [],
            "candidate_key": f"top_component_parent_fill_repair_child::{label}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_top_component_parent_fill_repair_child": True,
        }
        out.append(finalise_report_row(row))
    return out


def top_component_observable_quarantine_rows() -> list[dict[str, Any]]:
    payload = load_json(TOP_COMPONENT_OBSERVABLE_QUARANTINE_JSON)
    out: list[dict[str, Any]] = []
    for section, gate, strict_forward, diagnostic_context in (
        ("diagnostic", "top_component_observable_quarantine_child", False, True),
        ("autopsy_context", "top_component_observable_quarantine_autopsy_context", False, True),
        ("strict", "top_component_observable_quarantine_child", True, False),
    ):
        for item in payload.get(section) or []:
            if not isinstance(item, dict):
                continue
            label = str(item.get("label") or "")
            if not label:
                continue
            row = {
                "gate": gate,
                "policy": label,
                "entries": item.get("entries"),
                "settled": item.get("settled"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "coverage_pct": item.get("coverage_pct"),
                "net_cents_after_entry_fee": item.get("net_cents"),
                "delta_vs_live_cents": item.get("delta_vs_live_cents"),
                "simulated_share": item.get("reconstructed_share"),
                "full_loss_cushion_estimate": item.get("full_loss_cushion"),
                "affected_rows": item.get("affected_rows"),
                "affected_delta_cents": item.get("affected_delta_cents"),
                "zeroed_rows": item.get("zeroed_rows"),
                "live_ready": False,
                "strict_forward": bool(strict_forward),
                "diagnostic_context": bool(diagnostic_context),
                "blockers": item.get("blockers") or [],
                "candidate_key": f"{gate}::{label}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_top_component_observable_quarantine_child": True,
            }
            out.append(finalise_report_row(row))
    return out


def dual_lane_overlap_portfolio_rows() -> list[dict[str, Any]]:
    payload = load_json(DUAL_LANE_OVERLAP_PORTFOLIO_JSON)
    out: list[dict[str, Any]] = []
    for section, gate, summary_key in (
        ("top_portfolios", "dual_lane_overlap_union", "union"),
        ("top_strict_post_portfolios", "dual_lane_overlap_union", "union"),
        ("top_confirmations", "dual_lane_confirmation_filter", "confirmed"),
        ("top_strict_confirmations", "dual_lane_confirmation_filter", "confirmed"),
    ):
        for item in payload.get(section) or []:
            if not isinstance(item, dict):
                continue
            primary = item.get("primary") if isinstance(item.get("primary"), dict) else {}
            sidecar = item.get("sidecar") if isinstance(item.get("sidecar"), dict) else {}
            summary = item.get(summary_key) if isinstance(item.get(summary_key), dict) else {}
            policy = (
                f"{primary.get('source')}:{primary.get('policy')} + "
                f"{sidecar.get('policy')}"
            )
            if not policy.strip():
                continue
            blockers = list(item.get("blockers") or [])
            if "needs_own_frozen_forward_birth" not in blockers:
                blockers.append("needs_own_frozen_forward_birth")
            row = {
                "gate": gate,
                "policy": policy,
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents_after_entry_fee": summary.get("net_cents"),
                "avg_net_cents": summary.get("avg_net_cents"),
                "simulated_share": summary.get("reconstructed_share"),
                "full_loss_cushion_estimate": summary.get("full_loss_cushion"),
                "sidecar_add_entries": item.get("sidecar_add_entries"),
                "sidecar_add_net_cents": item.get("sidecar_add_net_cents"),
                "shared_markets": item.get("shared_markets"),
                "same_side_net_cents": (item.get("same_side") or {}).get("net_cents")
                if isinstance(item.get("same_side"), dict)
                else None,
                "omitted_primary_net_cents": (item.get("omitted_primary") or {}).get("net_cents")
                if isinstance(item.get("omitted_primary"), dict)
                else None,
                "live_ready": False,
                "strict_forward": False,
                "blockers": blockers,
                "candidate_key": f"{gate}::{section}::{policy}",
                "source_readiness": False,
                "source_leaderboard": False,
                "source_dual_lane_overlap_portfolio": True,
            }
            out.append(finalise_report_row(row))
    return out


def dual_lane_own_freeze_watch_rows() -> list[dict[str, Any]]:
    payload = load_json(DUAL_LANE_OWN_FREEZE_WATCH_JSON)
    out: list[dict[str, Any]] = []
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    for item in payload.get("unions") or []:
        if not isinstance(item, dict):
            continue
        primary = item.get("primary") if isinstance(item.get("primary"), dict) else {}
        sidecar = item.get("sidecar") if isinstance(item.get("sidecar"), dict) else {}
        summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
        policy = (
            f"{primary.get('source')}:{primary.get('policy')} + "
            f"{sidecar.get('policy')}"
        )
        if not policy.strip():
            continue
        row = {
            "gate": "dual_lane_own_freeze_watch",
            "policy": policy,
            "entries": summary.get("entries"),
            "settled": summary.get("settled"),
            "wins": summary.get("wins"),
            "losses": summary.get("losses"),
            "coverage_pct": summary.get("coverage_pct"),
            "net_cents_after_entry_fee": summary.get("net_cents"),
            "avg_net_cents": summary.get("avg_net_cents"),
            "simulated_share": summary.get("reconstructed_share"),
            "full_loss_cushion_estimate": summary.get("full_loss_cushion"),
            "source_counts": summary.get("source_counts"),
            "freeze_ts_utc": state.get("freeze_ts_utc"),
            "sidecar_add_entries": item.get("sidecar_add_entries"),
            "sidecar_add_net_cents": item.get("sidecar_add_net_cents"),
            "shared_markets": item.get("shared_markets"),
            "live_ready": bool(item.get("live_ready")),
            "strict_forward": bool(item.get("strict_forward")),
            "blockers": item.get("blockers") or [],
            "candidate_key": f"dual_lane_own_freeze_watch::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_dual_lane_own_freeze_watch": True,
        }
        out.append(finalise_report_row(row))
    return out


def exit_common_clock_residual_child_rows() -> list[dict[str, Any]]:
    payload = load_json(EXIT_COMMON_CLOCK_RESIDUAL_CHILD_JSON)
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        if lane.get("label") != "post_child_birth":
            continue
        policy = state.get("candidate") or "parent_loss_guard_plus_residual_exit70_79"
        row = {
            "gate": "exit_common_clock_residual_child_watch",
            "policy": policy,
            "entries": lane.get("settled"),
            "settled": lane.get("settled"),
            "wins": lane.get("candidate_wins"),
            "losses": lane.get("candidate_losses"),
            "coverage_pct": None,
            "net_cents_after_entry_fee": lane.get("candidate_net_cents"),
            "avg_net_cents": None,
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "delta_vs_current_cents": lane.get("delta_vs_current_cents"),
            "suppressed_exits": lane.get("child_suppressed"),
            "suppressed_delta_cents": lane.get("child_delta_vs_parent_cents"),
            "helpful_suppressions": lane.get("child_helpful"),
            "harmful_suppressions": lane.get("child_harmful"),
            "loss_control_cost_cents": lane.get("child_loss_control_cost_cents"),
            "full_loss_cushion_estimate": lane.get("full_loss_cushion_estimate"),
            "live_ready": False,
            "blockers": lane.get("blockers") or [],
            "strict_forward": True,
            "candidate_key": f"exit_common_clock_residual_child_watch::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_exit_common_clock_residual_child_watch": True,
        }
        out.append(finalise_report_row(row))
    return out


def finalise_report_row(row: dict[str, Any]) -> dict[str, Any]:
    row["target_coverage"] = in_target_coverage(row)
    row["has_settled_pnl"] = has_settled_pnl(row)
    row["simulated_share"] = simulated_share(row)
    return row


def parse_wl(value: Any) -> tuple[int | None, int | None]:
    if not value:
        return (None, None)
    text = str(value)
    if "/" not in text:
        return (None, None)
    left, right = text.split("/", 1)
    try:
        return (int(float(left)), int(float(right)))
    except ValueError:
        return (None, None)


def exit_variant_rows(
    payload: dict[str, Any],
    gate: str,
    collection_key: str,
    source_flag: str,
    diagnostic_prefix: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in payload.get(collection_key) or []:
        if not isinstance(item, dict):
            continue
        policy = str(item.get("policy") or item.get("candidate") or "")
        if not policy:
            continue
        label = policy if policy.startswith(f"{diagnostic_prefix}_") else f"{diagnostic_prefix}_{policy}"
        wins, losses = parse_wl(item.get("candidate_wl"))
        rows_value = first_present(item, "settled", "rows")
        row = {
            "gate": gate,
            "policy": label,
            "entries": rows_value,
            "settled": rows_value,
            "wins": first_present(item, "candidate_wins", "wins") if wins is None else wins,
            "losses": first_present(item, "candidate_losses", "losses") if losses is None else losses,
            "coverage_pct": None,
            "net_cents_after_entry_fee": first_present(
                item,
                "candidate_net_cents",
                "candidate_cents",
                "candidate_gross_cents",
            ),
            "delta_vs_current_cents": item.get("delta_vs_current_cents"),
            "suppressed_exits": item.get("suppressed"),
            "suppressed_delta_cents": first_present(item, "suppressed_delta_cents", "delta_vs_current_cents"),
            "helpful_suppressions": first_present(item, "suppressed_helpful", "helpful_suppressions"),
            "harmful_suppressions": first_present(item, "suppressed_harmful", "harmful_suppressions"),
            "loss_control_cost_cents": item.get("loss_control_cost_cents"),
            "full_loss_cushion_estimate": first_present(item, "full_loss_cushion_estimate", "full_loss_cushion"),
            "live_ready": False,
            "blockers": item.get("blockers") or [],
            "candidate_key": f"{gate}::{label}",
            "source_readiness": False,
            "source_leaderboard": False,
            source_flag: True,
        }
        out.append(finalise_report_row(row))
    return out


def exit_reduce_drift_guard_rows() -> list[dict[str, Any]]:
    payload = load_json(EXIT_REDUCE_DRIFT_GUARD_JSON)
    rows = exit_variant_rows(
        payload,
        "exit_reduce_drift_guard",
        "diagnostic_since_base_freeze",
        "source_exit_reduce_drift_guard",
        "diagnostic",
    )
    rows.extend(
        exit_variant_rows(
            payload,
            "exit_reduce_drift_guard",
            "post_drift_guard_birth",
            "source_exit_reduce_drift_guard",
            "post_birth",
        )
    )
    return rows


def exit_single_summary_rows(payload: dict[str, Any], gate: str, source_flag: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, prefix in [("best_diagnostic", "diagnostic"), ("best_strict_forward", "post_birth")]:
        item = payload.get(key)
        if not isinstance(item, dict):
            continue
        state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
        policy = str(item.get("policy") or state.get("candidate") or key)
        if not policy:
            continue
        label = policy if policy.startswith(f"{prefix}_") else f"{prefix}_{policy}"
        row = {
            "gate": gate,
            "policy": label,
            "entries": item.get("settled"),
            "settled": item.get("settled"),
            "wins": item.get("candidate_wins"),
            "losses": item.get("candidate_losses"),
            "coverage_pct": None,
            "net_cents_after_entry_fee": first_present(item, "candidate_gross_cents", "candidate_cents"),
            "delta_vs_current_cents": item.get("delta_vs_current_cents"),
            "suppressed_exits": first_present(item, "suppressed_exits", "suppressed"),
            "helpful_suppressions": item.get("suppressed_helpful"),
            "harmful_suppressions": item.get("suppressed_harmful"),
            "loss_control_cost_cents": item.get("loss_control_cost_cents"),
            "full_loss_cushion_estimate": first_present(item, "full_loss_cushion_estimate", "full_loss_cushion"),
            "live_ready": False,
            "blockers": item.get("blockers") or [],
            "strict_forward": bool(item.get("strict_forward")),
            "candidate_key": f"{gate}::{label}",
            "source_readiness": False,
            "source_leaderboard": False,
            source_flag: True,
        }
        rows.append(finalise_report_row(row))
    return rows


def exit_shallow_drawdown_rows() -> list[dict[str, Any]]:
    return exit_single_summary_rows(
        load_json(EXIT_SHALLOW_DRAWDOWN_JSON),
        "exit_shallow_drawdown",
        "source_exit_shallow_drawdown",
    )


def exit_shallow_duration_rows() -> list[dict[str, Any]]:
    return exit_single_summary_rows(
        load_json(EXIT_SHALLOW_DURATION_JSON),
        "exit_shallow_duration_lte52",
        "source_exit_shallow_duration",
    )


def exit_midband_reduce_rescue_rows() -> list[dict[str, Any]]:
    payload = load_json(EXIT_MIDBAND_REDUCE_RESCUE_JSON)
    rows = exit_variant_rows(
        payload,
        "exit_midband_reduce_rescue",
        "diagnostic",
        "source_exit_midband_reduce_rescue",
        "diagnostic",
    )
    rows.extend(
        exit_variant_rows(
            payload,
            "exit_midband_reduce_rescue",
            "post_birth",
            "source_exit_midband_reduce_rescue",
            "post_birth",
        )
    )
    return rows


def exit_clip_separator_watch_rows() -> list[dict[str, Any]]:
    payload = load_json(EXIT_CLIP_SEPARATOR_WATCH_JSON)
    summary = payload.get("candidate_summary")
    if not isinstance(summary, dict):
        return []
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    policy = str(state.get("candidate") or "fair_drawdown_lte10_p_hold_ge060_exit_clip_separator")
    row = {
        "gate": "exit_clip_separator_watch",
        "policy": policy,
        "entries": payload.get("post_freeze_matched_unchanged_rows"),
        "settled": payload.get("post_freeze_matched_unchanged_rows"),
        "wins": summary.get("helpful_rows"),
        "losses": summary.get("harmful_rows"),
        "coverage_pct": None,
        "net_cents_after_entry_fee": summary.get("known_hold_delta_cents"),
        "known_rows": summary.get("known_rows"),
        "unknown_rows": summary.get("unknown_rows"),
        "selected_rows": summary.get("rows"),
        "precision_on_known": summary.get("precision_on_known"),
        "live_ready": bool(payload.get("candidate_live_ready")),
        "blockers": summary.get("blockers") or [],
        "candidate_key": f"exit_clip_separator_watch::{policy}",
        "source_readiness": False,
        "source_leaderboard": False,
        "source_exit_clip_separator_watch": True,
    }
    return [finalise_report_row(row)]


def matched_unchanged_loss_guard_watch_rows() -> list[dict[str, Any]]:
    payload = load_json(MATCHED_UNCHANGED_LOSS_GUARD_WATCH_JSON)
    summary = payload.get("post_freeze_summary")
    if not isinstance(summary, dict):
        return []
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    policy = "guarded_matched_unchanged_loss_hold_watch"
    row = {
        "gate": "matched_unchanged_loss_guard_watch",
        "policy": policy,
        "entries": summary.get("rows"),
        "settled": summary.get("rows"),
        "wins": summary.get("helpful_rows"),
        "losses": summary.get("harmful_rows"),
        "coverage_pct": None,
        "net_cents_after_entry_fee": summary.get("candidate_net_cents"),
        "current_net_cents": summary.get("current_net_cents"),
        "delta_vs_current_cents": summary.get("delta_vs_current_cents"),
        "selected_rows": summary.get("selected_rows"),
        "suppressed_exits": summary.get("selected_rows"),
        "loss_count_reduction": summary.get("loss_count_reduction"),
        "full_loss_cushion_estimate": summary.get("full_loss_cushion"),
        "live_ready": False,
        "blockers": summary.get("blockers") or [],
        "candidate_key": f"matched_unchanged_loss_guard_watch::{policy}",
        "strict_forward": True,
        "source_readiness": False,
        "source_leaderboard": False,
        "source_matched_unchanged_loss_guard_watch": True,
        "freeze_ts_utc": state.get("freeze_ts_utc"),
    }
    return [finalise_report_row(row)]


def rmt_forgetting_entry_rows() -> list[dict[str, Any]]:
    payload = load_json(RMT_FORGETTING_ENTRY_JSON)
    rows: list[dict[str, Any]] = []
    for item in payload.get("ranked_by_pnl") or []:
        if not isinstance(item, dict):
            continue
        policy = str(item.get("policy") or "")
        if "rmt_" not in policy and "book_ask_prior" not in policy:
            continue
        row = {
            "gate": "rmt_forgetting_entry_bakeoff",
            "policy": policy,
            "entries": item.get("entries"),
            "settled": item.get("settled"),
            "wins": item.get("wins"),
            "losses": item.get("losses"),
            "coverage_pct": item.get("coverage_pct"),
            "net_cents_after_entry_fee": first_present(
                item,
                "net_cents_after_entry_fee",
                "net_gross_cents_after_entry_fee",
                "net_cents",
            ),
            "avg_net_cents": item.get("avg_net_gross_cents_after_entry_fee"),
            "approved_entry_count": item.get("approved_entry_count"),
            "added_reject_count": item.get("added_reject_count"),
            "live_ready": False,
            "blockers": ["diagnostic_bakeoff", "not_fresh_forward_gate"],
            "candidate_key": f"rmt_forgetting_entry_bakeoff::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_rmt_forgetting_entry_bakeoff": True,
        }
        rows.append(finalise_report_row(row))
    return rows


def path_rmt_forward_gate_rows() -> list[dict[str, Any]]:
    payload = load_json(PATH_RMT_FORWARD_GATE_JSON)
    rows: list[dict[str, Any]] = []
    for item in payload.get("summaries") or []:
        if not isinstance(item, dict):
            continue
        policy = str(item.get("policy") or "")
        if "rmt" not in policy:
            continue
        blockers = item.get("blockers") or []
        if not blockers:
            blockers = []
            share = as_float(item.get("simulated_share"))
            coverage = as_float(item.get("coverage_pct"))
            net = as_float(item.get("net_cents_after_entry_fee"))
            brier_delta = as_float(item.get("brier_delta_vs_base"))
            logloss_delta = as_float(item.get("logloss_delta_vs_base"))
            if share is not None and share > 0.35:
                blockers.append("simulated_share_gt_0.35")
            if coverage is not None and coverage < TARGET_COVERAGE_MIN:
                blockers.append("coverage_too_low")
            if coverage is not None and coverage > TARGET_COVERAGE_MAX:
                blockers.append("coverage_too_high")
            if net is None or net <= 0:
                blockers.append("net_not_positive")
            if brier_delta is not None and brier_delta >= 0:
                blockers.append("brier_delta_not_negative")
            if logloss_delta is not None and logloss_delta >= 0:
                blockers.append("logloss_delta_not_negative")
        row = {
            "gate": "path_rmt_forward_gate",
            "policy": policy,
            "entries": item.get("entries"),
            "settled": item.get("settled"),
            "wins": item.get("wins"),
            "losses": item.get("losses"),
            "coverage_pct": item.get("coverage_pct"),
            "net_cents_after_entry_fee": item.get("net_cents_after_entry_fee"),
            "avg_net_cents": None,
            "approved_entry_count": item.get("approved_entry_count"),
            "added_reject_count": item.get("added_reject_count"),
            "simulated_share": item.get("simulated_share"),
            "live_ready": bool(item.get("promotable")),
            "blockers": blockers,
            "candidate_key": f"path_rmt_forward_gate::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_path_rmt_forward_gate": True,
        }
        rows.append(finalise_report_row(row))
    return rows


def forgetting_fv_rows(path: Path, gate: str, source_flag: str) -> list[dict[str, Any]]:
    payload = load_json(path)
    rows: list[dict[str, Any]] = []
    for item in payload.get("forward") or []:
        if not isinstance(item, dict):
            continue
        policy = str(item.get("overlay") or "")
        if not policy or policy == "raw_probability":
            continue
        row = {
            "gate": gate,
            "policy": policy,
            "entries": item.get("entries"),
            "settled": item.get("settled"),
            "wins": item.get("wins"),
            "losses": item.get("losses"),
            "coverage_pct": item.get("coverage_pct"),
            "net_cents_after_entry_fee": item.get("net_cents_after_entry_fee"),
            "avg_net_cents": None,
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": None,
            "live_ready": False,
            "blockers": item.get("blockers") or [],
            "candidate_key": f"{gate}::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            source_flag: True,
        }
        rows.append(finalise_report_row(row))
    return rows


def false_conviction_family_rows() -> list[dict[str, Any]]:
    payload = load_json(FALSE_CONVICTION_FAMILY_JSON)
    rows: list[dict[str, Any]] = []
    for item in payload.get("rows") or []:
        if not isinstance(item, dict):
            continue
        policy = str(item.get("candidate") or item.get("name") or "")
        if not policy:
            continue
        row = {
            "gate": "false_conviction_family_scorecard",
            "policy": policy,
            "entries": item.get("entries"),
            "settled": item.get("settled"),
            "wins": item.get("wins"),
            "losses": item.get("losses"),
            "coverage_pct": item.get("coverage_pct"),
            "net_cents_after_entry_fee": item.get("net_cents"),
            "avg_net_cents": None,
            "approved_entry_count": None,
            "added_reject_count": None,
            "simulated_share": item.get("reconstructed_share"),
            "live_ready": bool(item.get("pass") or item.get("integrity_pass")),
            "blockers": item.get("blockers") or [],
            "full_loss_cushion_estimate": first_present(
                item,
                "loss_cushion",
                "full_loss_cushion",
            ),
            "candidate_key": f"false_conviction_family_scorecard::{policy}",
            "source_readiness": False,
            "source_leaderboard": False,
            "source_false_conviction_family_scorecard": True,
        }
        rows.append(finalise_report_row(row))
    return rows


def boundary_clock_source_stress_map() -> dict[str, dict[str, Any]]:
    payload = load_json(BOUNDARY_CLOCK_SOURCE_STRESS_JSON)
    out: dict[str, dict[str, Any]] = {}
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if not lane_name:
            continue
        source_counts = lane.get("source_counts") if isinstance(lane.get("source_counts"), dict) else {}
        out[lane_name] = {
            "approved_entry_count": source_counts.get("approved_entry"),
            "added_reject_count": source_counts.get("rejected_actionable"),
            "simulated_share": lane.get("reconstructed_share"),
            "full_loss_cushion_estimate": lane.get("full_loss_cushion_estimate"),
            "source_clean_rows_needed": lane.get("future_clean_rows_for_sample_source_gate"),
            "source_stress_blockers": lane.get("blockers") or [],
            "source_boundary_clock_source_stress": True,
        }
    return out


def count_where(rows: list[dict[str, Any]], predicate) -> int:
    return sum(1 for row in rows if predicate(row))


def top_rows(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    scored = [row for row in rows if has_settled_pnl(row)]
    return sorted(
        scored,
        key=lambda row: (
            as_float(row.get("net_cents_after_entry_fee")) or -999999.0,
            as_float(row.get("settled")) or 0.0,
        ),
        reverse=True,
    )[:limit]


def has_approved_evidence(row: dict[str, Any]) -> bool:
    return (as_int(row.get("approved_entry_count")) or 0) > 0


def build_report() -> dict[str, Any]:
    readiness = load_json(READINESS_JSON)
    leaderboard = load_json(LEADERBOARD_JSON)
    readiness_rows = list(readiness.get("candidates") or [])
    leaderboard_rows = list(leaderboard.get("ranked") or [])
    merged = merge_rows(readiness_rows, leaderboard_rows)
    feature_rows = feature_gate_forward_rows()
    feature_book_gap_stack_rows = feature_gate_book_gap_exit_stack_rows()
    feature_soft_frontier_exit_stack_rows = feature_gate_book_gap_exit_stack_rows(
        FEATURE_GATE_SOFT_FRONTIER_EXIT_STACK_JSON,
        "feature_gate_soft_frontier_exit_stack",
        "source_feature_gate_soft_frontier_exit_stack",
    )
    continuous_penalty_rows = feature_gate_continuous_penalty_rows()
    soft_frontier_rows = feature_gate_soft_frontier_rows()
    clean_broad_frontier_rows = feature_gate_clean_broad_frontier_rows()
    cheap_tail_quarantine_rows = feature_gate_cheap_tail_quarantine_rows()
    cheap_tail_shrink_rows = feature_gate_cheap_tail_shrink_rows()
    core_expansion_mix_rows = feature_gate_core_expansion_mix_rows()
    coverage_size_shrink_rows = feature_gate_coverage_size_shrink_rows()
    middle_distance_core_rows = feature_gate_middle_distance_core_rows()
    middle_core_exit_guard_rows = feature_gate_middle_core_exit_guard_rows()
    observable_selection_mix_rows = feature_gate_observable_selection_mix_rows()
    size_shrink_exit_overlay_rows = feature_gate_size_shrink_exit_overlay_rows()
    size_shrink_delayed_recheck_exit_rows = feature_gate_size_shrink_delayed_recheck_exit_rows()
    size_shrink_delayed_recheck_rescue_rows = feature_gate_size_shrink_delayed_recheck_rescue_rows()
    source_confirmation_replacement_rows = feature_gate_source_confirmation_replacement_rows()
    late_collapse_recheck_rescue_rows = feature_gate_late_collapse_recheck_rescue_rows()
    dual_clock_recheck_rescue_rows = feature_gate_dual_clock_recheck_rescue_rows()
    confirmed_dual_clock_fill_rows = feature_gate_confirmed_dual_clock_fill_rows()
    source_quality_proxy_rows = feature_gate_source_quality_proxy_rows()
    source_proxy_coverage_repair_rows = feature_gate_source_proxy_coverage_repair_rows()
    cluster_source_aware_rows = target_cluster_source_aware_rows()
    cluster_observable_stability_rows = target_cluster_observable_stability_rows()
    exit_reduce_refinement = exit_reduce_refinement_rows()
    exit_reduce_depth_gate = exit_reduce_depth_gate_rows()
    exit_reduce_observable_loss_control = exit_reduce_observable_loss_control_rows()
    exit_reduce_drift_guard = exit_reduce_drift_guard_rows()
    exit_shallow_drawdown = exit_shallow_drawdown_rows()
    exit_shallow_duration = exit_shallow_duration_rows()
    exit_midband_reduce_rescue = exit_midband_reduce_rescue_rows()
    exit_clip_separator_watch = exit_clip_separator_watch_rows()
    matched_unchanged_loss_guard_watch = matched_unchanged_loss_guard_watch_rows()
    rmt_forgetting_rows = rmt_forgetting_entry_rows()
    path_rmt_rows = path_rmt_forward_gate_rows()
    boundary_memory_rows = forgetting_fv_rows(
        BOUNDARY_MEMORY_FV_JSON,
        "boundary_memory_fv",
        "source_boundary_memory_fv",
    )
    phi_forgetting_rows = forgetting_fv_rows(
        PHI_FORGETTING_FV_JSON,
        "phi_forgetting_fv",
        "source_phi_forgetting_fv",
    )
    reward_memory_rows = forgetting_fv_rows(
        REWARD_MEMORY_FV_JSON,
        "reward_memory_fv",
        "source_reward_memory_fv",
    )
    false_conviction_rows = false_conviction_family_rows()
    collapse_reentry_rows = collapse_reentry_registry_rows()
    soft_frontier_size_shrink_rows_ = soft_frontier_size_shrink_rows()
    soft_frontier_midprice_boundary_shrink_rows_ = soft_frontier_midprice_boundary_shrink_rows()
    midprice_source_dilution_rows_ = midprice_source_dilution_rows()
    p50_book_edge_no_side_shrink_rows_ = p50_book_edge_no_side_shrink_rows()
    soft_frontier_midprice_boundary_exit_stack_rows_ = soft_frontier_midprice_boundary_exit_stack_rows()
    soft_frontier_midprice_boundary_clip_exit_stack_rows_ = soft_frontier_midprice_boundary_exit_stack_rows(
        SOFT_FRONTIER_MIDPRICE_BOUNDARY_CLIP_EXIT_STACK_JSON,
        "soft_frontier_midprice_boundary_clip_exit_stack",
        "source_soft_frontier_midprice_boundary_clip_exit_stack",
    )
    soft_frontier_midprice_boundary_dual_exit_stack_rows_ = soft_frontier_midprice_boundary_exit_stack_rows(
        SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_STACK_JSON,
        "soft_frontier_midprice_boundary_dual_exit_stack",
        "source_soft_frontier_midprice_boundary_dual_exit_stack",
    )
    soft_frontier_midprice_boundary_dual_exit_guard_rows_ = soft_frontier_midprice_boundary_exit_stack_rows(
        SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_GUARD_JSON,
        "soft_frontier_midprice_boundary_dual_exit_guard",
        "source_soft_frontier_midprice_boundary_dual_exit_guard",
    )
    feature_gate_exit_bid_suppression_watch_rows_ = feature_gate_exit_bid_suppression_watch_rows()
    feature_gate_exit_bid_delayed_recheck_rows_ = feature_gate_exit_bid_delayed_recheck_rows()
    exit_common_clock_residual_child_rows_ = exit_common_clock_residual_child_rows()
    soft_frontier_midprice_delayed_recheck_exit_rows_ = soft_frontier_midprice_delayed_recheck_exit_rows()
    soft_frontier_midprice_delayed_recheck_rescue_rows_ = soft_frontier_midprice_delayed_recheck_rescue_rows()
    top_component_mix_portfolio_rows_ = top_component_mix_portfolio_rows()
    top_component_false_negative_rescue_rows_ = top_component_false_negative_rescue_rows()
    top_component_parent_fill_repair_rows_ = top_component_parent_fill_repair_rows()
    top_component_observable_quarantine_rows_ = top_component_observable_quarantine_rows()
    dual_lane_overlap_portfolio_rows_ = dual_lane_overlap_portfolio_rows()
    dual_lane_own_freeze_watch_rows_ = dual_lane_own_freeze_watch_rows()
    feature_gate_value_exit_watch_rows_ = feature_gate_value_exit_watch_rows()
    value_exit_feature_side_guard_rows_ = value_exit_feature_side_guard_rows()
    existing_keys = {key(row) for row in merged}
    supplemental_only_rows = supplemental_rows()
    for row in (
        feature_rows
        + feature_book_gap_stack_rows
        + feature_soft_frontier_exit_stack_rows
        + continuous_penalty_rows
        + soft_frontier_rows
        + clean_broad_frontier_rows
        + cheap_tail_quarantine_rows
        + cheap_tail_shrink_rows
        + core_expansion_mix_rows
        + coverage_size_shrink_rows
        + middle_distance_core_rows
        + middle_core_exit_guard_rows
        + observable_selection_mix_rows
        + size_shrink_exit_overlay_rows
        + size_shrink_delayed_recheck_exit_rows
        + size_shrink_delayed_recheck_rescue_rows
        + source_confirmation_replacement_rows
        + late_collapse_recheck_rescue_rows
        + dual_clock_recheck_rescue_rows
        + confirmed_dual_clock_fill_rows
        + source_quality_proxy_rows
        + source_proxy_coverage_repair_rows
        + cluster_source_aware_rows
        + cluster_observable_stability_rows
        + exit_reduce_refinement
        + exit_reduce_depth_gate
        + exit_reduce_observable_loss_control
        + exit_reduce_drift_guard
        + exit_shallow_drawdown
        + exit_shallow_duration
        + exit_midband_reduce_rescue
        + exit_clip_separator_watch
        + matched_unchanged_loss_guard_watch
        + rmt_forgetting_rows
        + path_rmt_rows
        + boundary_memory_rows
        + phi_forgetting_rows
        + reward_memory_rows
        + false_conviction_rows
        + collapse_reentry_rows
        + soft_frontier_size_shrink_rows_
        + soft_frontier_midprice_boundary_shrink_rows_
        + midprice_source_dilution_rows_
        + p50_book_edge_no_side_shrink_rows_
        + soft_frontier_midprice_boundary_exit_stack_rows_
        + soft_frontier_midprice_boundary_clip_exit_stack_rows_
        + soft_frontier_midprice_boundary_dual_exit_stack_rows_
        + soft_frontier_midprice_boundary_dual_exit_guard_rows_
        + feature_gate_exit_bid_suppression_watch_rows_
        + feature_gate_exit_bid_delayed_recheck_rows_
        + exit_common_clock_residual_child_rows_
        + soft_frontier_midprice_delayed_recheck_exit_rows_
        + soft_frontier_midprice_delayed_recheck_rescue_rows_
        + top_component_mix_portfolio_rows_
        + top_component_false_negative_rescue_rows_
        + top_component_parent_fill_repair_rows_
        + top_component_observable_quarantine_rows_
        + dual_lane_overlap_portfolio_rows_
        + dual_lane_own_freeze_watch_rows_
        + feature_gate_value_exit_watch_rows_
        + value_exit_feature_side_guard_rows_
        + supplemental_only_rows
    ):
        if key(row) not in existing_keys:
            merged.append(row)
            existing_keys.add(key(row))
    supplemental_by_key = supplemental_summary_map()

    for row in merged:
        summary = supplemental_by_key.get(key(row))
        if not summary:
            continue
        apply_supplemental_summary(row, summary)

    boundary_clock_stress = boundary_clock_source_stress_map()
    for row in merged:
        stress = boundary_clock_stress.get(str(row.get("gate") or ""))
        if not stress:
            continue
        for field, value in stress.items():
            if value is not None:
                row[field] = value
        stress_blockers = stress.get("source_stress_blockers") or []
        if stress_blockers:
            existing = list(row.get("blockers") or [])
            for blocker in stress_blockers:
                tagged = f"source_stress:{blocker}"
                if tagged not in existing:
                    existing.append(tagged)
            row["blockers"] = existing

    positive_rows = [
        row for row in merged
        if has_settled_pnl(row) and (as_float(row.get("net_cents_after_entry_fee")) or 0.0) > 0.0
    ]
    target_positive_rows = [row for row in positive_rows if in_target_coverage(row)]
    wl_rows = [
        row for row in merged
        if row.get("wins") is not None and row.get("losses") is not None
    ]
    actual_evidence_rows = [row for row in merged if has_approved_evidence(row)]
    high_sim_rows = [
        row for row in merged
        if (share := simulated_share(row)) is not None and share > 0.35
    ]

    summary = {
        "readiness_candidates": len(readiness_rows),
        "leaderboard_candidates": len(leaderboard_rows),
        "unique_candidates": len(merged),
        "feature_gate_forward_candidates": len(feature_rows),
        "feature_gate_book_gap_exit_stack_candidates": len(feature_book_gap_stack_rows),
        "feature_gate_soft_frontier_exit_stack_candidates": len(feature_soft_frontier_exit_stack_rows),
        "feature_gate_continuous_penalty_forward_candidates": len(continuous_penalty_rows),
        "feature_gate_soft_frontier_forward_candidates": len(soft_frontier_rows),
        "feature_gate_clean_broad_frontier_forward_candidates": len(clean_broad_frontier_rows),
        "feature_gate_cheap_tail_quarantine_forward_candidates": len(cheap_tail_quarantine_rows),
        "feature_gate_cheap_tail_shrink_forward_candidates": len(cheap_tail_shrink_rows),
        "feature_gate_core_expansion_mix_candidates": len(core_expansion_mix_rows),
        "feature_gate_coverage_size_shrink_candidates": len(coverage_size_shrink_rows),
        "feature_gate_middle_distance_core_candidates": len(middle_distance_core_rows),
        "feature_gate_middle_core_exit_guard_candidates": len(middle_core_exit_guard_rows),
        "feature_gate_observable_selection_mix_candidates": len(observable_selection_mix_rows),
        "feature_gate_size_shrink_exit_overlay_candidates": len(size_shrink_exit_overlay_rows),
        "feature_gate_size_shrink_delayed_recheck_exit_candidates": len(size_shrink_delayed_recheck_exit_rows),
        "feature_gate_size_shrink_delayed_recheck_rescue_candidates": len(size_shrink_delayed_recheck_rescue_rows),
        "feature_gate_source_confirmation_replacement_candidates": len(source_confirmation_replacement_rows),
        "feature_gate_late_collapse_recheck_rescue_candidates": len(late_collapse_recheck_rescue_rows),
        "feature_gate_dual_clock_recheck_rescue_candidates": len(dual_clock_recheck_rescue_rows),
        "feature_gate_confirmed_dual_clock_fill_candidates": len(confirmed_dual_clock_fill_rows),
        "feature_gate_source_quality_proxy_candidates": len(source_quality_proxy_rows),
        "feature_gate_source_proxy_coverage_repair_candidates": len(source_proxy_coverage_repair_rows),
        "target_cluster_source_aware_forward_candidates": len(cluster_source_aware_rows),
        "target_cluster_observable_stability_forward_candidates": len(cluster_observable_stability_rows),
        "exit_reduce_refinement_forward_candidates": len(exit_reduce_refinement),
        "exit_reduce_depth_gate_forward_candidates": len(exit_reduce_depth_gate),
        "exit_reduce_observable_loss_control_forward_candidates": len(exit_reduce_observable_loss_control),
        "exit_reduce_drift_guard_candidates": len(exit_reduce_drift_guard),
        "exit_shallow_drawdown_candidates": len(exit_shallow_drawdown),
        "exit_shallow_duration_candidates": len(exit_shallow_duration),
        "exit_midband_reduce_rescue_candidates": len(exit_midband_reduce_rescue),
        "exit_clip_separator_watch_candidates": len(exit_clip_separator_watch),
        "matched_unchanged_loss_guard_watch_candidates": len(matched_unchanged_loss_guard_watch),
        "rmt_forgetting_entry_candidates": len(rmt_forgetting_rows),
        "path_rmt_forward_gate_candidates": len(path_rmt_rows),
        "boundary_memory_fv_candidates": len(boundary_memory_rows),
        "phi_forgetting_fv_candidates": len(phi_forgetting_rows),
        "reward_memory_fv_candidates": len(reward_memory_rows),
        "false_conviction_family_candidates": len(false_conviction_rows),
        "collapse_reentry_registry_candidates": len(collapse_reentry_rows),
        "soft_frontier_size_shrink_candidates": len(soft_frontier_size_shrink_rows_),
        "soft_frontier_midprice_boundary_shrink_candidates": len(soft_frontier_midprice_boundary_shrink_rows_),
        "midprice_source_dilution_candidates": len(midprice_source_dilution_rows_),
        "p50_book_edge_no_side_shrink_candidates": len(p50_book_edge_no_side_shrink_rows_),
        "soft_frontier_midprice_boundary_exit_stack_candidates": len(soft_frontier_midprice_boundary_exit_stack_rows_),
        "soft_frontier_midprice_boundary_clip_exit_stack_candidates": len(soft_frontier_midprice_boundary_clip_exit_stack_rows_),
        "soft_frontier_midprice_boundary_dual_exit_stack_candidates": len(soft_frontier_midprice_boundary_dual_exit_stack_rows_),
        "soft_frontier_midprice_boundary_dual_exit_guard_candidates": len(soft_frontier_midprice_boundary_dual_exit_guard_rows_),
        "feature_gate_exit_bid_suppression_watch_candidates": len(feature_gate_exit_bid_suppression_watch_rows_),
        "feature_gate_exit_bid_delayed_recheck_candidates": len(feature_gate_exit_bid_delayed_recheck_rows_),
        "exit_common_clock_residual_child_candidates": len(exit_common_clock_residual_child_rows_),
        "soft_frontier_midprice_delayed_recheck_exit_candidates": len(soft_frontier_midprice_delayed_recheck_exit_rows_),
        "soft_frontier_midprice_delayed_recheck_rescue_candidates": len(soft_frontier_midprice_delayed_recheck_rescue_rows_),
        "top_component_mix_portfolio_candidates": len(top_component_mix_portfolio_rows_),
        "top_component_false_negative_rescue_candidates": len(top_component_false_negative_rescue_rows_),
        "top_component_parent_fill_repair_candidates": len(top_component_parent_fill_repair_rows_),
        "top_component_observable_quarantine_candidates": len(top_component_observable_quarantine_rows_),
        "dual_lane_overlap_portfolio_candidates": len(dual_lane_overlap_portfolio_rows_),
        "dual_lane_own_freeze_watch_candidates": len(dual_lane_own_freeze_watch_rows_),
        "feature_gate_value_exit_watch_candidates": len(feature_gate_value_exit_watch_rows_),
        "value_exit_feature_side_guard_candidates": len(value_exit_feature_side_guard_rows_),
        "with_settled_pnl": count_where(merged, has_settled_pnl),
        "with_wins_losses": len(wl_rows),
        "positive_pnl": len(positive_rows),
        "target_coverage": count_where(merged, in_target_coverage),
        "target_coverage_positive_pnl": len(target_positive_rows),
        "live_ready": count_where(merged, lambda row: bool(row.get("live_ready"))),
        "actual_approved_evidence": len(actual_evidence_rows),
        "high_simulated_share": len(high_sim_rows),
        "control_entries": readiness.get("control_entries"),
        "control_gross_cents": readiness.get("control_gross_cents"),
        "control_risk_stop": readiness.get("control_risk_stop"),
        "watchlist_present": WATCHLIST_MD.exists(),
        "target_coverage_min": TARGET_COVERAGE_MIN,
        "target_coverage_max": TARGET_COVERAGE_MAX,
    }

    return {
        "summary": summary,
        "top_positive": top_rows(positive_rows),
        "top_target_positive": top_rows(target_positive_rows),
        "top_approved_evidence": top_rows(actual_evidence_rows),
        "top_positive_approved_evidence": top_rows([
            row for row in positive_rows if has_approved_evidence(row)
        ]),
        "rows": merged,
        "sources": {
            "readiness": str(READINESS_JSON),
            "leaderboard": str(LEADERBOARD_JSON),
            "watchlist": str(WATCHLIST_MD),
            "feature_gate": str(FEATURE_GATE_JSON),
            "feature_gate_continuous_penalty": str(FEATURE_GATE_CONTINUOUS_PENALTY_JSON),
            "feature_gate_soft_frontier": str(FEATURE_GATE_SOFT_FRONTIER_JSON),
            "feature_gate_clean_broad_frontier": str(FEATURE_GATE_CLEAN_BROAD_FRONTIER_JSON),
            "feature_gate_cheap_tail_shrink": str(FEATURE_GATE_CHEAP_TAIL_SHRINK_WATCH_JSON),
            "feature_gate_core_expansion_mix": str(FEATURE_GATE_CORE_EXPANSION_MIX_JSON),
            "feature_gate_coverage_size_shrink": str(FEATURE_GATE_COVERAGE_SIZE_SHRINK_JSON),
            "feature_gate_middle_distance_core": str(FEATURE_GATE_MIDDLE_DISTANCE_CORE_JSON),
            "feature_gate_middle_core_exit_guard": str(FEATURE_GATE_MIDDLE_CORE_EXIT_GUARD_JSON),
            "feature_gate_observable_selection_mix": str(FEATURE_GATE_OBSERVABLE_SELECTION_MIX_JSON),
            "feature_gate_size_shrink_exit_overlay": str(FEATURE_GATE_SIZE_SHRINK_EXIT_OVERLAY_JSON),
            "feature_gate_size_shrink_delayed_recheck_exit": str(FEATURE_GATE_SIZE_SHRINK_DELAYED_RECHECK_EXIT_JSON),
            "feature_gate_size_shrink_delayed_recheck_rescue": str(FEATURE_GATE_SIZE_SHRINK_DELAYED_RECHECK_RESCUE_JSON),
            "feature_gate_source_confirmation_replacement": str(FEATURE_GATE_SOURCE_CONFIRMATION_REPLACEMENT_JSON),
            "feature_gate_late_collapse_recheck_rescue": str(FEATURE_GATE_LATE_COLLAPSE_RECHECK_RESCUE_JSON),
            "feature_gate_dual_clock_recheck_rescue": str(FEATURE_GATE_DUAL_CLOCK_RECHECK_RESCUE_JSON),
            "feature_gate_confirmed_dual_clock_fill": str(FEATURE_GATE_CONFIRMED_DUAL_CLOCK_FILL_JSON),
            "feature_gate_source_quality_proxy": str(FEATURE_GATE_SOURCE_QUALITY_PROXY_JSON),
            "feature_gate_source_proxy_coverage_repair": str(FEATURE_GATE_SOURCE_PROXY_COVERAGE_REPAIR_JSON),
            "target_cluster_source_aware": str(TARGET_CLUSTER_SOURCE_AWARE_JSON),
            "target_cluster_observable_stability": str(TARGET_CLUSTER_OBSERVABLE_STABILITY_JSON),
            "exit_reduce_refinement": str(EXIT_REDUCE_REFINEMENT_JSON),
            "exit_reduce_depth_gate": str(EXIT_REDUCE_DEPTH_GATE_JSON),
            "exit_reduce_observable_loss_control": str(EXIT_REDUCE_OBSERVABLE_LOSS_CONTROL_JSON),
            "exit_reduce_drift_guard": str(EXIT_REDUCE_DRIFT_GUARD_JSON),
            "exit_shallow_drawdown": str(EXIT_SHALLOW_DRAWDOWN_JSON),
            "exit_shallow_duration": str(EXIT_SHALLOW_DURATION_JSON),
            "exit_midband_reduce_rescue": str(EXIT_MIDBAND_REDUCE_RESCUE_JSON),
            "exit_clip_separator_watch": str(EXIT_CLIP_SEPARATOR_WATCH_JSON),
            "rmt_forgetting_entry_bakeoff": str(RMT_FORGETTING_ENTRY_JSON),
            "path_rmt_forward_gate": str(PATH_RMT_FORWARD_GATE_JSON),
            "boundary_memory_fv": str(BOUNDARY_MEMORY_FV_JSON),
            "phi_forgetting_fv": str(PHI_FORGETTING_FV_JSON),
            "reward_memory_fv": str(REWARD_MEMORY_FV_JSON),
            "false_conviction_family_scorecard": str(FALSE_CONVICTION_FAMILY_JSON),
            "boundary_clock_source_stress": str(BOUNDARY_CLOCK_SOURCE_STRESS_JSON),
            "collapse_reentry_registry": str(COLLAPSE_REENTRY_JSON),
            "soft_frontier_size_shrink": str(SOFT_FRONTIER_SIZE_SHRINK_JSON),
            "soft_frontier_midprice_boundary_shrink": str(SOFT_FRONTIER_MIDPRICE_BOUNDARY_SHRINK_JSON),
            "midprice_source_dilution": str(MIDPRICE_SOURCE_DILUTION_JSON),
            "p50_book_edge_no_side_shrink": str(P50_BOOK_EDGE_NO_SIDE_SHRINK_JSON),
            "soft_frontier_midprice_boundary_exit_stack": str(SOFT_FRONTIER_MIDPRICE_BOUNDARY_EXIT_STACK_JSON),
            "soft_frontier_midprice_boundary_clip_exit_stack": str(SOFT_FRONTIER_MIDPRICE_BOUNDARY_CLIP_EXIT_STACK_JSON),
            "soft_frontier_midprice_boundary_dual_exit_stack": str(SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_STACK_JSON),
            "soft_frontier_midprice_boundary_dual_exit_guard": str(SOFT_FRONTIER_MIDPRICE_BOUNDARY_DUAL_EXIT_GUARD_JSON),
            "feature_gate_exit_bid_suppression_watch": str(FEATURE_GATE_EXIT_BID_SUPPRESSION_WATCH_JSON),
            "feature_gate_exit_bid_delayed_recheck": str(FEATURE_GATE_EXIT_BID_DELAYED_RECHECK_JSON),
            "exit_common_clock_residual_child": str(EXIT_COMMON_CLOCK_RESIDUAL_CHILD_JSON),
            "soft_frontier_midprice_delayed_recheck_exit": str(SOFT_FRONTIER_MIDPRICE_DELAYED_RECHECK_EXIT_JSON),
            "soft_frontier_midprice_delayed_recheck_rescue": str(SOFT_FRONTIER_MIDPRICE_DELAYED_RECHECK_RESCUE_JSON),
            "top_component_mix_portfolio": str(TOP_COMPONENT_MIX_PORTFOLIO_JSON),
            "top_component_false_negative_rescue": str(TOP_COMPONENT_FALSE_NEGATIVE_RESCUE_JSON),
            "top_component_parent_fill_repair": str(TOP_COMPONENT_PARENT_FILL_REPAIR_JSON),
            "top_component_observable_quarantine": str(TOP_COMPONENT_OBSERVABLE_QUARANTINE_JSON),
            "dual_lane_own_freeze_watch": str(DUAL_LANE_OWN_FREEZE_WATCH_JSON),
            "feature_gate_value_exit_watch": str(FEATURE_GATE_VALUE_EXIT_WATCH_JSON),
            "value_exit_feature_side_guard": str(VALUE_EXIT_FEATURE_SIDE_GUARD_JSON),
            "supplemental_summary_count": len(supplemental_only_rows),
        },
    }


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    dollars = number / 100.0
    return f"{number:.0f}c (${dollars:.2f})"


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.2f}%"


def fmt_share(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number * 100.0:.1f}%"


def write_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "| gate | policy | entries | settled | W/L | coverage | net | sim share | live ready |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in rows:
        wins = row.get("wins")
        losses = row.get("losses")
        wl = f"{wins}/{losses}" if wins is not None and losses is not None else "n/a"
        lines.append(
            f"| `{row.get('gate')}` | `{row.get('policy')}` | "
            f"{row.get('entries')} | {row.get('settled')} | {wl} | "
            f"{fmt_pct(row.get('coverage_pct'))} | {fmt_cents(row.get('net_cents_after_entry_fee'))} | "
            f"{fmt_share(row.get('simulated_share'))} | {row.get('live_ready')} |"
        )


def write_md(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Candidate PnL Tracker",
        "",
        "Reporting-only consolidation of current v28 candidate lanes against live-market forward evidence.",
        "",
        "## Counts",
        "",
        f"- Readiness candidates: `{summary['readiness_candidates']}`",
        f"- Frozen leaderboard candidates: `{summary['leaderboard_candidates']}`",
        f"- Unique gate/policy lanes after reconciliation: `{summary['unique_candidates']}`",
        f"- Boundary-clock feature-gate forward lanes: `{summary['feature_gate_forward_candidates']}`",
        f"- Feature-gate + book-gap exit stack forward lanes: `{summary['feature_gate_book_gap_exit_stack_candidates']}`",
        f"- Feature-gate soft-frontier + exit stack forward lanes: `{summary['feature_gate_soft_frontier_exit_stack_candidates']}`",
        f"- Boundary-clock continuous-penalty forward lanes: `{summary['feature_gate_continuous_penalty_forward_candidates']}`",
        f"- Boundary-clock soft-frontier forward lanes: `{summary['feature_gate_soft_frontier_forward_candidates']}`",
        f"- Boundary-clock clean-broad frontier forward lanes: `{summary['feature_gate_clean_broad_frontier_forward_candidates']}`",
        f"- Feature-gate cheap-tail quarantine forward lanes: `{summary['feature_gate_cheap_tail_quarantine_forward_candidates']}`",
        f"- Feature-gate cheap-tail shrink forward lanes: `{summary['feature_gate_cheap_tail_shrink_forward_candidates']}`",
        f"- Feature-gate core/expansion mix lanes: `{summary['feature_gate_core_expansion_mix_candidates']}`",
        f"- Feature-gate coverage size-shrink lanes: `{summary['feature_gate_coverage_size_shrink_candidates']}`",
        f"- Feature-gate middle-distance core lanes: `{summary['feature_gate_middle_distance_core_candidates']}`",
        f"- Feature-gate middle-core exit-guard lanes: `{summary['feature_gate_middle_core_exit_guard_candidates']}`",
        f"- Feature-gate observable selection-mix lanes: `{summary['feature_gate_observable_selection_mix_candidates']}`",
        f"- Feature-gate size-shrink exit-overlay lanes: `{summary['feature_gate_size_shrink_exit_overlay_candidates']}`",
        f"- Feature-gate size-shrink delayed-recheck exit lanes: `{summary['feature_gate_size_shrink_delayed_recheck_exit_candidates']}`",
        f"- Feature-gate size-shrink delayed-recheck rescue lanes: `{summary['feature_gate_size_shrink_delayed_recheck_rescue_candidates']}`",
        f"- Feature-gate source-confirmation replacement lanes: `{summary['feature_gate_source_confirmation_replacement_candidates']}`",
        f"- Feature-gate late-collapse recheck rescue lanes: `{summary['feature_gate_late_collapse_recheck_rescue_candidates']}`",
        f"- Feature-gate dual-clock recheck rescue lanes: `{summary['feature_gate_dual_clock_recheck_rescue_candidates']}`",
        f"- Feature-gate confirmed dual-clock fill lanes: `{summary['feature_gate_confirmed_dual_clock_fill_candidates']}`",
        f"- Feature-gate source-quality proxy lanes: `{summary['feature_gate_source_quality_proxy_candidates']}`",
        f"- Feature-gate source-proxy coverage-repair lanes: `{summary['feature_gate_source_proxy_coverage_repair_candidates']}`",
        f"- Target cluster source-aware forward lanes: `{summary['target_cluster_source_aware_forward_candidates']}`",
        f"- Target cluster observable-stability forward lanes: `{summary['target_cluster_observable_stability_forward_candidates']}`",
        f"- Exit reduce loss-control refinement forward lanes: `{summary['exit_reduce_refinement_forward_candidates']}`",
        f"- Exit reduce entry-depth gate forward lanes: `{summary['exit_reduce_depth_gate_forward_candidates']}`",
        f"- Exit reduce observable loss-control forward lanes: `{summary['exit_reduce_observable_loss_control_forward_candidates']}`",
        f"- Exit reduce drift-guard lanes: `{summary['exit_reduce_drift_guard_candidates']}`",
        f"- Exit shallow-drawdown lanes: `{summary['exit_shallow_drawdown_candidates']}`",
        f"- Exit shallow-duration lanes: `{summary['exit_shallow_duration_candidates']}`",
        f"- Exit clip-separator watch lanes: `{summary['exit_clip_separator_watch_candidates']}`",
        f"- Matched-unchanged loss guard watch lanes: `{summary['matched_unchanged_loss_guard_watch_candidates']}`",
        f"- RMT forgetting entry lanes: `{summary['rmt_forgetting_entry_candidates']}`",
        f"- Path/RMT fresh-gate lanes: `{summary['path_rmt_forward_gate_candidates']}`",
        f"- Boundary-memory FV lanes: `{summary['boundary_memory_fv_candidates']}`",
        f"- Phi-forgetting FV lanes: `{summary['phi_forgetting_fv_candidates']}`",
        f"- Reward-memory FV lanes: `{summary['reward_memory_fv_candidates']}`",
        f"- False-conviction family scorecard lanes: `{summary['false_conviction_family_candidates']}`",
        f"- Collapse/reentry registry lanes: `{summary['collapse_reentry_registry_candidates']}`",
        f"- Soft-frontier size-shrink portfolio lanes: `{summary['soft_frontier_size_shrink_candidates']}`",
        f"- Soft-frontier mid-price boundary shrink lanes: `{summary['soft_frontier_midprice_boundary_shrink_candidates']}`",
        f"- Mid-price source-dilution watch lanes: `{summary['midprice_source_dilution_candidates']}`",
        f"- p50 book-edge NO-side shrink watch lanes: `{summary['p50_book_edge_no_side_shrink_candidates']}`",
        f"- Soft-frontier mid-price boundary exit-stack lanes: `{summary['soft_frontier_midprice_boundary_exit_stack_candidates']}`",
        f"- Soft-frontier mid-price boundary clip-exit stack lanes: `{summary['soft_frontier_midprice_boundary_clip_exit_stack_candidates']}`",
        f"- Soft-frontier mid-price boundary dual-exit stack lanes: `{summary['soft_frontier_midprice_boundary_dual_exit_stack_candidates']}`",
        f"- Soft-frontier mid-price boundary dual-exit guard lanes: `{summary['soft_frontier_midprice_boundary_dual_exit_guard_candidates']}`",
        f"- Feature-gate exit-bid suppression watch lanes: `{summary['feature_gate_exit_bid_suppression_watch_candidates']}`",
        f"- Feature-gate exit-bid delayed-recheck lanes: `{summary['feature_gate_exit_bid_delayed_recheck_candidates']}`",
        f"- Exit common-clock residual child lanes: `{summary['exit_common_clock_residual_child_candidates']}`",
        f"- Soft-frontier mid-price delayed-recheck exit lanes: `{summary['soft_frontier_midprice_delayed_recheck_exit_candidates']}`",
        f"- Soft-frontier mid-price delayed-recheck rescue lanes: `{summary['soft_frontier_midprice_delayed_recheck_rescue_candidates']}`",
        f"- Top-component mix portfolio lanes: `{summary['top_component_mix_portfolio_candidates']}`",
        f"- Top-component false-negative rescue lanes: `{summary['top_component_false_negative_rescue_candidates']}`",
        f"- Top-component parent-fill repair lanes: `{summary['top_component_parent_fill_repair_candidates']}`",
        f"- Top-component observable quarantine lanes: `{summary['top_component_observable_quarantine_candidates']}`",
        f"- Dual-lane own-freeze watch lanes: `{summary['dual_lane_own_freeze_watch_candidates']}`",
        f"- Feature-gate value-exit watch lanes: `{summary['feature_gate_value_exit_watch_candidates']}`",
        f"- Value-exit feature-side guard lanes: `{summary['value_exit_feature_side_guard_candidates']}`",
        f"- Lanes with settled PnL: `{summary['with_settled_pnl']}`",
        f"- Lanes with explicit W/L fields: `{summary['with_wins_losses']}`",
        f"- Positive PnL lanes: `{summary['positive_pnl']}`",
        f"- Target coverage lanes ({TARGET_COVERAGE_MIN:.0f}-{TARGET_COVERAGE_MAX:.0f}%): `{summary['target_coverage']}`",
        f"- Target coverage and positive PnL lanes: `{summary['target_coverage_positive_pnl']}`",
        f"- Live-ready lanes: `{summary['live_ready']}`",
        f"- Lanes with some approved-entry evidence: `{summary['actual_approved_evidence']}`",
        f"- Lanes over 35% simulated/rejected share: `{summary['high_simulated_share']}`",
        "",
        "## Control",
        "",
        f"- Current v28 control entries: `{summary['control_entries']}`",
        f"- Current v28 control gross PnL: `{fmt_cents(summary['control_gross_cents'])}`",
        f"- Current v28 risk stop active: `{summary['control_risk_stop']}`",
        "",
        "## Top Target-Coverage Positive Lanes",
        "",
    ]
    if report["top_target_positive"]:
        write_table(lines, report["top_target_positive"])
    else:
        lines.append("- None right now.")
    lines.extend([
        "",
        "## Top Positive Lanes",
        "",
    ])
    if report["top_positive"]:
        write_table(lines, report["top_positive"])
    else:
        lines.append("- None right now.")
    lines.extend([
        "",
        "## Top Positive Lanes With Approved-Entry Evidence",
        "",
    ])
    if report["top_positive_approved_evidence"]:
        write_table(lines, report["top_positive_approved_evidence"])
    else:
        lines.append("- None right now.")
    lines.extend([
        "",
        "## Top Approved-Entry Evidence Lanes",
        "",
    ])
    if report["top_approved_evidence"]:
        write_table(lines, report["top_approved_evidence"])
    else:
        lines.append("- None right now.")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- The readiness artifact is the widest current count; the frozen leaderboard carries W/L for fewer lanes.",
        "- `live_ready=false` means the lane is still shadow/research-only even when its PnL is positive.",
        "- High simulated/rejected share means the lane is mostly reconstructed opportunity evidence, not actual approved live entries.",
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
