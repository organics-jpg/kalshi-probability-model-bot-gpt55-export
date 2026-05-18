"""Dashboard for frozen v28 exit-policy watch lanes.

Research-only; no live bot changes or orders.

This consolidates the exit/state branch so a zero-delta watch is not mistaken
for a failed rule when it simply has not seen suppressible post-freeze exits.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
OUT_MD = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.md"

SOURCES = {
    "book_gap": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "book_gap_loss_guard": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "book_gap_loss_guard_opportunity": OUT_DIR / "v28_exit_book_gap_loss_guard_opportunity_latest.json",
    "book_gap_loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
    "book_gap_loss_guard_v2_opportunity": OUT_DIR / "v28_exit_book_gap_loss_guard_v2_opportunity_latest.json",
    "book_gap_loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
    "book_gap_value_only": OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json",
    "value_reduce_depth": OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json",
    "reduce_depth_gate": OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json",
    "reduce_depth_runway": OUT_DIR / "v28_exit_reduce_depth_gate_runway_latest.json",
    "reduce_depth_opportunity": OUT_DIR / "v28_exit_reduce_depth_gate_opportunity_latest.json",
    "reduce_refinement": OUT_DIR / "v28_frozen_exit_reduce_loss_control_refinement_latest.json",
    "reduce_observable_loss_control": OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "reduce_geometry": OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_latest.json",
    "reduce_geometry_relaxed": OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.json",
    "reduce_drift_guard": OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_latest.json",
    "midband_reduce_rescue": OUT_DIR / "v28_frozen_exit_midband_reduce_rescue_watch_latest.json",
    "exit_clip_separator": OUT_DIR / "v28_frozen_exit_clip_separator_watch_latest.json",
    "matched_unchanged_loss_guard": OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_latest.json",
    "shallow_drawdown": OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_latest.json",
    "shallow_duration": OUT_DIR / "v28_frozen_exit_shallow_duration_watch_latest.json",
    "dual_exit": OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.json",
    "common_clock": OUT_DIR / "v28_exit_policy_common_clock_watch_latest.json",
    "common_clock_residual_child": OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_latest.json",
    "common_clock_residual_child_book_gap_guard": OUT_DIR / "v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_latest.json",
    "soft_frontier_midprice_delayed_recheck": OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json",
    "soft_frontier_midprice_delayed_recheck_rescue": OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_rescue_latest.json",
    "feature_gate_value_exit": OUT_DIR / "v28_frozen_feature_gate_value_exit_watch_latest.json",
    "feature_gate_exit_bid": OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_latest.json",
    "feature_gate_exit_bid_delayed_recheck": OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_latest.json",
    "value_exit_feature_side_guard": OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.json",
}


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
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def first_variant(payload: dict[str, Any], lane_name: str) -> dict[str, Any]:
    for lane in payload.get("lanes") or []:
        if isinstance(lane, dict) and lane.get("lane") == lane_name:
            variants = lane.get("variants")
            return variants[0] if isinstance(variants, list) and variants else {}
    return {}


def classify(summary: dict[str, Any], blockers: list[str], opportunity: dict[str, Any] | None = None) -> str:
    settled = int(as_float(summary.get("settled")) or as_float(summary.get("rows")) or 0)
    suppressed = int(as_float(summary.get("suppressed_exits")) or as_float(summary.get("suppressed")) or 0)
    delta = float(
        as_float(summary.get("delta_vs_current_cents"))
        or as_float(summary.get("delta_vs_live_cents"))
        or as_float(summary.get("feature_side_guard_delta_cents"))
        or as_float(summary.get("delta_vs_current"))
        or 0.0
    )
    candidate_net = (
        as_float(summary.get("candidate_gross_cents"))
        if summary.get("candidate_gross_cents") is not None
        else as_float(summary.get("candidate_net_cents"))
        if summary.get("candidate_net_cents") is not None
        else as_float(summary.get("feature_side_guard_net_cents"))
        if summary.get("feature_side_guard_net_cents") is not None
        else as_float(summary.get("net_cents"))
    )
    loss_cost = float(as_float(summary.get("loss_control_cost_cents")) or 0.0)
    if settled == 0:
        return "waiting_no_post_freeze_rows"
    if opportunity is not None:
        total_rows = int(as_float(opportunity.get("total_rows")) or as_float(opportunity.get("post_birth_rows")) or 0)
        reduce_rows = int(as_float(opportunity.get("probability_reduce_rows")) or 0)
        soft_rows = int(as_float(opportunity.get("soft_exit_rows")) or 0)
        would_suppress = int(as_float(opportunity.get("would_suppress_rows")) or 0)
        if total_rows > 0 and reduce_rows == 0 and soft_rows == 0 and would_suppress == 0:
            return "waiting_no_suppressible_exit_type"
        if total_rows > 0 and would_suppress == 0:
            return "waiting_rule_has_not_fired"
    if loss_cost < 0 or "suppressed_loss_control_cost_negative" in blockers:
        return "blocked_loss_control_cost"
    if "net_not_positive" in blockers or (candidate_net is not None and candidate_net <= 0.0):
        return "blocked_net_not_positive"
    if suppressed == 0:
        return "waiting_no_suppressed_exits"
    if delta > 0 and settled >= 30:
        return "forward_positive_under_review"
    if delta > 0:
        return "positive_but_under_sample"
    return "not_positive_or_under_sample"


def lane_row(name: str, candidate: str, summary: dict[str, Any], blockers: list[str], freeze_ts: Any, opportunity: dict[str, Any] | None = None) -> dict[str, Any]:
    current_net = (
        as_float(summary.get("current_gross_cents"))
        if summary.get("current_gross_cents") is not None
        else as_float(summary.get("current_net_cents"))
        if summary.get("current_net_cents") is not None
        else as_float(summary.get("baseline_live_net_cents"))
        if summary.get("baseline_live_net_cents") is not None
        else as_float(summary.get("live_selected_net_cents"))
    )
    candidate_net = (
        as_float(summary.get("candidate_gross_cents"))
        if summary.get("candidate_gross_cents") is not None
        else as_float(summary.get("candidate_net_cents"))
        if summary.get("candidate_net_cents") is not None
        else as_float(summary.get("feature_side_guard_net_cents"))
        if summary.get("feature_side_guard_net_cents") is not None
        else as_float(summary.get("net_cents"))
    )
    delta = (
        as_float(summary.get("delta_vs_current_cents"))
        if summary.get("delta_vs_current_cents") is not None
        else as_float(summary.get("delta_vs_live_cents"))
        if summary.get("delta_vs_live_cents") is not None
        else as_float(summary.get("feature_side_guard_delta_cents"))
    )
    return {
        "lane": name,
        "candidate": candidate,
        "freeze_ts_utc": freeze_ts,
        "settled": int(as_float(summary.get("settled")) or as_float(summary.get("rows")) or 0),
        "rows": int(as_float(summary.get("rows")) or 0),
        "suppressed_exits": int(as_float(summary.get("suppressed_exits")) or as_float(summary.get("suppressed")) or 0),
        "current_net_cents": float(current_net or 0.0),
        "candidate_net_cents": float(candidate_net or 0.0),
        "delta_vs_current_cents": float(delta or 0.0),
        "winner_recovery_cents": float(as_float(summary.get("winner_clip_recovered_cents")) or as_float(summary.get("winner_recovery_cents")) or 0.0),
        "loss_control_cost_cents": float(as_float(summary.get("loss_control_cost_cents")) or 0.0),
        "full_loss_cushion": int(as_float(summary.get("full_loss_cushion_estimate")) or 0),
        "opportunity": opportunity or {},
        "blockers": blockers,
        "status": classify(summary, blockers, opportunity),
    }


def common_clock_summary(strict_window: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(summary)
    row_count = int(as_float(strict_window.get("row_count")) or 0)
    settled = int(as_float(normalized.get("settled")) or as_float(normalized.get("rows")) or 0)
    if row_count > settled:
        normalized["settled"] = row_count
        normalized["rows"] = row_count
    return normalized


def exit_summary(item: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(item)
    if "candidate_cents" in normalized and "candidate_net_cents" not in normalized:
        normalized["candidate_net_cents"] = normalized.get("candidate_cents")
    if "current_cents" in normalized and "current_net_cents" not in normalized:
        normalized["current_net_cents"] = normalized.get("current_cents")
    if "full_loss_cushion" in normalized and "full_loss_cushion_estimate" not in normalized:
        normalized["full_loss_cushion_estimate"] = normalized.get("full_loss_cushion")
    if "suppressed" in normalized and "suppressed_exits" not in normalized:
        normalized["suppressed_exits"] = normalized.get("suppressed")
    if "harmful_delta_cents" in normalized and "loss_control_cost_cents" not in normalized:
        normalized["loss_control_cost_cents"] = normalized.get("harmful_delta_cents")
    return normalized


def build_report() -> dict[str, Any]:
    data = {name: load_json(path) for name, path in SOURCES.items()}
    rows: list[dict[str, Any]] = []

    book_gap = data["book_gap"]
    rows.append(lane_row(
        "book_gap_suppression",
        (book_gap.get("freeze") or {}).get("candidate") or "suppress_soft_gap15_or_p_hold75",
        book_gap.get("summary") or {},
        list(book_gap.get("blockers") or []),
        (book_gap.get("freeze") or {}).get("freeze_ts_utc"),
    ))

    loss_guard = data["book_gap_loss_guard"]
    loss_guard_opp = data["book_gap_loss_guard_opportunity"]
    rows.append(lane_row(
        "book_gap_loss_guard",
        (loss_guard.get("freeze") or {}).get("candidate") or "book_gap_loss_guard",
        loss_guard.get("summary") or {},
        list(loss_guard.get("blockers") or []),
        (loss_guard.get("freeze") or {}).get("freeze_ts_utc"),
        {
            "total_rows": loss_guard_opp.get("total_rows"),
            "soft_exit_rows": loss_guard_opp.get("soft_exit_rows"),
            "would_suppress_rows": loss_guard_opp.get("would_suppress_rows"),
            "fail_reason_counts": loss_guard_opp.get("fail_reason_counts"),
        },
    ))

    loss_guard_v2 = data["book_gap_loss_guard_v2"]
    loss_guard_v2_opp = data["book_gap_loss_guard_v2_opportunity"]
    rows.append(lane_row(
        "book_gap_loss_guard_v2",
        (loss_guard_v2.get("freeze") or {}).get("candidate") or "book_gap_loss_guard_v2",
        loss_guard_v2.get("summary") or {},
        list(loss_guard_v2.get("blockers") or []),
        (loss_guard_v2.get("freeze") or {}).get("freeze_ts_utc"),
        {
            "total_rows": loss_guard_v2_opp.get("total_rows"),
            "soft_exit_rows": loss_guard_v2_opp.get("soft_exit_rows"),
            "value_over_hold_rows": loss_guard_v2_opp.get("value_over_hold_rows"),
            "probability_reduce_rows": loss_guard_v2_opp.get("probability_reduce_rows"),
            "would_suppress_rows": loss_guard_v2_opp.get("would_suppress_rows"),
            "fail_reason_counts": loss_guard_v2_opp.get("fail_reason_counts"),
        },
    ))

    loss_guard_v3 = data["book_gap_loss_guard_v3"]
    rows.append(lane_row(
        "book_gap_loss_guard_v3",
        (loss_guard_v3.get("freeze") or {}).get("candidate") or "book_gap_loss_guard_v3",
        loss_guard_v3.get("summary") or {},
        list(loss_guard_v3.get("blockers") or []),
        (loss_guard_v3.get("freeze") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_existing_exit_sample": loss_guard_v3.get("discovery_summary_existing_exit_sample") or {},
            "diagnostic_comparable_book_gap_sample": loss_guard_v3.get("discovery_summary_comparable_book_gap_freeze_sample") or {},
        },
    ))

    book_gap_value = data["book_gap_value_only"]
    rows.append(lane_row(
        "book_gap_value_only",
        (book_gap_value.get("freeze") or {}).get("candidate") or (book_gap_value.get("summary") or {}).get("variant") or "value_only_gap15_or_p75",
        book_gap_value.get("summary") or {},
        list(book_gap_value.get("blockers") or []),
        (book_gap_value.get("freeze") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_best": (first_variant(book_gap_value, "diagnostic_from_book_gap_freeze").get("summary") or {}),
        },
    ))

    value_reduce = data["value_reduce_depth"]
    rows.append(lane_row(
        "value_reduce_depth_composite",
        (value_reduce.get("freeze") or {}).get("candidate") or "value_v2_reduce_depth384",
        value_reduce.get("summary") or {},
        list(value_reduce.get("blockers") or []),
        (value_reduce.get("freeze") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_best": (first_variant(value_reduce, "diagnostic_from_exit_freezes").get("summary") or {}),
        },
    ))

    depth = data["reduce_depth_gate"]
    depth_post = first_variant(depth, "post_depth_gate_birth")
    depth_summary = depth_post.get("summary") or {}
    depth_opp = data["reduce_depth_opportunity"]
    depth_opp_rules = depth_opp.get("rules") or []
    depth_opp_first = depth_opp_rules[0] if depth_opp_rules else {}
    rows.append(lane_row(
        "reduce_depth_gate",
        depth_post.get("candidate") or "post_depth_gate_birth",
        depth_summary,
        list(depth_post.get("blockers") or []),
        (depth.get("state") or {}).get("freeze_ts_utc"),
        {
            "post_birth_rows": depth_opp.get("post_birth_rows"),
            "probability_reduce_rows": depth_opp_first.get("probability_reduce_rows"),
            "would_suppress_rows": depth_opp_first.get("would_suppress_rows"),
            "fail_reason_counts": depth_opp_first.get("fail_reason_counts"),
            "runway": data["reduce_depth_runway"].get("post_birth_best") or {},
        },
    ))

    refinement = data["reduce_refinement"]
    refinement_post = first_variant(refinement, "post_refinement_birth")
    rows.append(lane_row(
        "reduce_loss_control_refinement",
        refinement_post.get("candidate") or "post_refinement_birth",
        refinement_post.get("summary") or {},
        list(refinement_post.get("blockers") or []),
        (refinement.get("state") or {}).get("freeze_ts_utc"),
    ))

    observable = data["reduce_observable_loss_control"]
    observable_post = first_variant(observable, "post_observable_birth")
    observable_diag = first_variant(observable, "diagnostic_from_reduce_freeze")
    rows.append(lane_row(
        "reduce_observable_loss_control",
        observable_post.get("candidate") or "post_observable_birth_reduce_suppress_p75_entry_stc_lte_596",
        observable_post.get("summary") or {},
        list(observable_post.get("blockers") or []),
        (observable.get("state") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_best": observable_diag.get("summary") or {},
        },
    ))

    geometry = data["reduce_geometry"]
    rows.append(lane_row(
        "reduce_side_geometry",
        (geometry.get("freeze") or {}).get("candidate") or "side_geometry_suppress_reduce_p_hold_ge_075",
        geometry.get("summary") or {},
        list(geometry.get("blockers") or []),
        (geometry.get("freeze") or {}).get("freeze_ts_utc"),
    ))

    geometry_relaxed = data["reduce_geometry_relaxed"]
    rows.append(lane_row(
        "reduce_geometry_relaxed",
        (geometry_relaxed.get("summary") or {}).get("policy") or (geometry_relaxed.get("freeze") or {}).get("candidate") or "side_geometry_or_no_deep_loss20_suppress_reduce_p_hold_ge_075",
        geometry_relaxed.get("summary") or {},
        list(geometry_relaxed.get("blockers") or []),
        (geometry_relaxed.get("freeze") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_best": (geometry_relaxed.get("diagnostic") or {}).get("best") or {},
        },
    ))

    drift = data["reduce_drift_guard"]
    drift_state = drift.get("state") if isinstance(drift.get("state"), dict) else {}
    drift_post_policy = str(drift.get("best_post_birth_policy") or "")
    drift_post = next(
        (item for item in drift.get("post_drift_guard_birth") or [] if item.get("policy") == drift_post_policy),
        (drift.get("post_drift_guard_birth") or [{}])[0] if drift.get("post_drift_guard_birth") else {},
    )
    drift_diag_policy = str(drift.get("best_diagnostic_policy") or "")
    drift_diag = next(
        (item for item in drift.get("diagnostic_since_base_freeze") or [] if item.get("policy") == drift_diag_policy),
        {},
    )
    rows.append(lane_row(
        "exit_reduce_drift_guard",
        drift_post.get("policy") or drift_post_policy or drift_state.get("candidate") or "two_regime_drift_guard",
        exit_summary(drift_post),
        list(drift_post.get("blockers") or []),
        drift_state.get("freeze_ts_utc"),
        {
            "diagnostic_policy": drift_diag.get("policy"),
            "diagnostic_settled": drift_diag.get("settled", drift_diag.get("rows")),
            "diagnostic_delta_cents": drift_diag.get("delta_vs_current_cents"),
            "diagnostic_suppressed": drift_diag.get("suppressed"),
            "diagnostic_helpful_harmful": f"{drift_diag.get('suppressed_helpful')}/{drift_diag.get('suppressed_harmful')}",
        },
    ))

    midband = data["midband_reduce_rescue"]
    midband_post = (midband.get("post_birth") or [{}])[0]
    midband_diag = (midband.get("diagnostic") or [{}])[0]
    rows.append(lane_row(
        "midband_reduce_rescue",
        midband_post.get("candidate") or "midband_p60_75_exit50_75_asklt80",
        exit_summary(midband_post),
        list(midband_post.get("blockers") or []),
        (midband.get("state") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_best": midband_diag,
        },
    ))

    clip = data["exit_clip_separator"]
    clip_state = clip.get("state") if isinstance(clip.get("state"), dict) else {}
    clip_summary = dict(clip.get("candidate_summary") or {})
    clip_summary["settled"] = clip.get("post_freeze_matched_unchanged_rows")
    clip_summary["suppressed_exits"] = clip_summary.get("rows")
    clip_summary["candidate_net_cents"] = clip_summary.get("known_hold_delta_cents")
    clip_summary["delta_vs_current_cents"] = clip_summary.get("known_hold_delta_cents")
    rows.append(lane_row(
        "exit_clip_separator_watch",
        clip_state.get("candidate") or "fair_drawdown_lte10_p_hold_ge060_exit_clip_separator",
        clip_summary,
        list(clip_summary.get("blockers") or []),
        clip_state.get("freeze_ts_utc"),
        {
            "post_freeze_matched_unchanged_rows": clip.get("post_freeze_matched_unchanged_rows"),
            "total_rows": clip.get("post_freeze_matched_unchanged_rows"),
            "soft_exit_rows": clip.get("post_freeze_matched_unchanged_rows"),
            "would_suppress_rows": clip_summary.get("rows"),
            "missed_known_helpful_rows": clip.get("missed_known_helpful_rows"),
            "physics": clip_state.get("physics"),
        },
    ))

    matched_guard = data["matched_unchanged_loss_guard"]
    matched_state = matched_guard.get("state") if isinstance(matched_guard.get("state"), dict) else {}
    matched_post = matched_guard.get("post_freeze_summary") if isinstance(matched_guard.get("post_freeze_summary"), dict) else {}
    matched_diag = matched_guard.get("diagnostic_summary") if isinstance(matched_guard.get("diagnostic_summary"), dict) else {}
    rows.append(lane_row(
        "matched_unchanged_loss_guard_watch",
        "guarded_matched_unchanged_loss_hold_watch",
        exit_summary(matched_post),
        list(matched_post.get("blockers") or []),
        matched_state.get("freeze_ts_utc"),
        {
            "diagnostic_selected": matched_diag.get("selected_rows"),
            "diagnostic_helpful_harmful": f"{matched_diag.get('helpful_rows')}/{matched_diag.get('harmful_rows')}",
            "diagnostic_delta_cents": matched_diag.get("selected_hold_delta_cents"),
            "total_rows": matched_post.get("rows"),
            "soft_exit_rows": matched_post.get("rows"),
            "would_suppress_rows": matched_post.get("selected_rows"),
            "physics": "Guarded rich-ish near-boundary exit holds test whether selected exits are clipped winners rather than FV/entry failures.",
        },
    ))

    shallow = data["shallow_drawdown"]
    shallow_state = shallow.get("state") if isinstance(shallow.get("state"), dict) else {}
    shallow_post = shallow.get("best_strict_forward") if isinstance(shallow.get("best_strict_forward"), dict) else {}
    shallow_diag = shallow.get("best_diagnostic") if isinstance(shallow.get("best_diagnostic"), dict) else {}
    rows.append(lane_row(
        "exit_shallow_drawdown",
        shallow_post.get("policy") or shallow_state.get("candidate") or "shallow_drawdown_reduce_or_collapse_lte5",
        exit_summary(shallow_post),
        list(shallow_post.get("blockers") or []),
        shallow_state.get("freeze_ts_utc"),
        {
            "diagnostic_policy": shallow_diag.get("policy"),
            "diagnostic_settled": shallow_diag.get("settled"),
            "diagnostic_delta_cents": shallow_diag.get("delta_vs_current_cents"),
            "diagnostic_suppressed": shallow_diag.get("suppressed_exits"),
            "diagnostic_helpful_harmful": f"{shallow_diag.get('suppressed_helpful')}/{shallow_diag.get('suppressed_harmful')}",
            "diagnostic_loss_control_cost_cents": shallow_diag.get("loss_control_cost_cents"),
        },
    ))

    duration = data["shallow_duration"]
    duration_state = duration.get("state") if isinstance(duration.get("state"), dict) else {}
    duration_post = duration.get("best_strict_forward") if isinstance(duration.get("best_strict_forward"), dict) else {}
    duration_diag = duration.get("best_diagnostic") if isinstance(duration.get("best_diagnostic"), dict) else {}
    rows.append(lane_row(
        "exit_shallow_duration_lte52",
        duration_post.get("policy") or duration_state.get("candidate") or "shallow_drawdown_duration_lte52_reduce_or_collapse",
        exit_summary(duration_post),
        list(duration_post.get("blockers") or []),
        duration_state.get("freeze_ts_utc"),
        {
            "diagnostic_policy": duration_diag.get("policy") or duration_state.get("candidate"),
            "diagnostic_settled": duration_diag.get("settled"),
            "diagnostic_delta_cents": duration_diag.get("delta_vs_current_cents"),
            "diagnostic_suppressed": duration_diag.get("suppressed_exits"),
            "diagnostic_helpful_harmful": f"{duration_diag.get('suppressed_helpful')}/{duration_diag.get('suppressed_harmful')}",
            "diagnostic_loss_control_cost_cents": duration_diag.get("loss_control_cost_cents"),
        },
    ))

    dual = data["dual_exit"]
    rows.append(lane_row(
        "dual_exit_book_gap_else_reduce",
        (dual.get("freeze") or {}).get("candidate") or "dual_exit_book_gap_else_reduce",
        dual.get("summary") or {},
        list(dual.get("blockers") or []),
        (dual.get("freeze") or {}).get("freeze_ts_utc"),
        {"source_counts": dual.get("source_counts")},
    ))

    common = data["common_clock"]
    common_windows = [row for row in common.get("windows") or [] if isinstance(row, dict)]
    strict_names = [
        "new_exit_mix_common_forward_v1",
        "new_exit_mix_common_forward_v2",
        "new_exit_mix_common_forward_v3",
    ]
    strict_forward_windows = common.get("strict_forward_windows") or {}
    for strict_name in strict_names:
        strict = next((row for row in common_windows if row.get("window") == strict_name), {})
        if not strict:
            continue
        strict_best = common_clock_summary(strict, (strict.get("summaries") or [{}])[0])
        rows.append(lane_row(
            f"common_clock_{strict_name.replace('new_exit_mix_common_forward', 'strict_forward')}",
            strict_best.get("policy") or "current_v28_exit",
            strict_best,
            list(strict_best.get("blockers") or []),
            strict_forward_windows.get(strict_name) or common.get("strict_forward_window") or strict.get("freeze_ts_utc"),
        ))

    residual_child = data["common_clock_residual_child"]
    residual_state = residual_child.get("state") if isinstance(residual_child.get("state"), dict) else {}
    residual_post = next(
        (lane for lane in residual_child.get("lanes") or [] if lane.get("label") == "post_child_birth"),
        {},
    )
    residual_v2 = next(
        (lane for lane in residual_child.get("lanes") or [] if lane.get("label") == "diagnostic_v2_common_clock_context"),
        {},
    )
    residual_v3 = next(
        (lane for lane in residual_child.get("lanes") or [] if lane.get("label") == "diagnostic_v3_common_clock_context"),
        {},
    )
    residual_summary = dict(residual_post)
    residual_summary["suppressed_exits"] = residual_post.get("child_suppressed")
    residual_summary["loss_control_cost_cents"] = residual_post.get("child_loss_control_cost_cents")
    rows.append(lane_row(
        "common_clock_residual_child_exit70_79",
        residual_state.get("candidate") or "parent_loss_guard_plus_residual_exit70_79",
        residual_summary,
        list(residual_post.get("blockers") or []),
        residual_state.get("freeze_ts_utc"),
        {
            "diagnostic_v2_settled": residual_v2.get("settled"),
            "diagnostic_v2_child_helpful_harmful": f"{residual_v2.get('child_helpful')}/{residual_v2.get('child_harmful')}",
            "diagnostic_v2_child_delta_cents": residual_v2.get("child_delta_vs_parent_cents"),
            "diagnostic_v3_settled": residual_v3.get("settled"),
            "diagnostic_v3_child_helpful_harmful": f"{residual_v3.get('child_helpful')}/{residual_v3.get('child_harmful')}",
            "diagnostic_v3_child_delta_cents": residual_v3.get("child_delta_vs_parent_cents"),
        },
    ))

    residual_guard = data["common_clock_residual_child_book_gap_guard"]
    residual_guard_state = residual_guard.get("state") if isinstance(residual_guard.get("state"), dict) else {}
    residual_guard_post = next(
        (lane for lane in residual_guard.get("lanes") or [] if lane.get("lane") == "post_book_gap_guard_birth"),
        {},
    )
    residual_guard_v2 = next(
        (lane for lane in residual_guard.get("lanes") or [] if lane.get("lane") == "diagnostic_v2_common_clock_context"),
        {},
    )
    residual_guard_v3 = next(
        (lane for lane in residual_guard.get("lanes") or [] if lane.get("lane") == "diagnostic_v3_common_clock_context"),
        {},
    )
    residual_guard_summary = dict(residual_guard_post)
    residual_guard_summary["suppressed_exits"] = residual_guard_post.get("child_suppressed")
    residual_guard_summary["loss_control_cost_cents"] = residual_guard_post.get("child_loss_control_cost_cents")
    rows.append(lane_row(
        "common_clock_residual_child_book_gap_guard",
        residual_guard_state.get("candidate") or "residual_exit70_79_book_gap_le_neg_0_5pp",
        residual_guard_summary,
        list(residual_guard_post.get("blockers") or []),
        residual_guard_state.get("freeze_ts_utc"),
        {
            "diagnostic_v2_settled": residual_guard_v2.get("settled"),
            "diagnostic_v2_child_helpful_harmful": f"{residual_guard_v2.get('child_helpful')}/{residual_guard_v2.get('child_harmful')}",
            "diagnostic_v2_child_delta_cents": residual_guard_v2.get("child_delta_vs_parent_cents"),
            "diagnostic_v3_settled": residual_guard_v3.get("settled"),
            "diagnostic_v3_child_helpful_harmful": f"{residual_guard_v3.get('child_helpful')}/{residual_guard_v3.get('child_harmful')}",
            "diagnostic_v3_child_delta_cents": residual_guard_v3.get("child_delta_vs_parent_cents"),
            "physics": residual_guard_state.get("physics"),
        },
    ))

    soft_delay = data["soft_frontier_midprice_delayed_recheck"]
    soft_delay_state = soft_delay.get("state") if isinstance(soft_delay.get("state"), dict) else {}
    soft_delay_post_lane = next(
        (lane for lane in soft_delay.get("lanes") or [] if lane.get("lane") == "post_delayed_recheck_birth"),
        {},
    )
    soft_delay_diag_lane = next(
        (lane for lane in soft_delay.get("lanes") or [] if lane.get("lane") == "diagnostic_prefreeze_context"),
        {},
    )
    soft_delay_post = dict(soft_delay_post_lane.get("summary") or {})
    soft_delay_diag = soft_delay_diag_lane.get("summary") or {}
    soft_delay_post["settled"] = soft_delay_post.get("rows")
    soft_delay_post["suppressed_exits"] = soft_delay_post.get("suppressed")
    soft_delay_post["current_net_cents"] = soft_delay_post.get("weighted_current_cents")
    soft_delay_post["candidate_net_cents"] = soft_delay_post.get("weighted_candidate_cents")
    soft_delay_post["delta_vs_current_cents"] = soft_delay_post.get("weighted_delta_cents")
    soft_delay_post["loss_control_cost_cents"] = 0.0
    rows.append(lane_row(
        "soft_frontier_midprice_delayed_recheck_exit",
        (
            f"{soft_delay_state.get('entry_policy')}_{soft_delay_state.get('exit_source')}_"
            f"{soft_delay_state.get('recheck_policy')}"
        ),
        soft_delay_post,
        list(soft_delay_post.get("blockers") or []),
        soft_delay_state.get("freeze_ts_utc"),
        {
            "diagnostic_settled": soft_delay_diag.get("rows"),
            "diagnostic_helpful_harmful": (
                f"{soft_delay_diag.get('helpful_suppressed')}/"
                f"{soft_delay_diag.get('harmful_suppressed')}"
            ),
            "diagnostic_delta_cents": soft_delay_diag.get("weighted_delta_cents"),
            "diagnostic_reconstructed_share": soft_delay_diag.get("reconstructed_share"),
            "rule": soft_delay_state.get("rule"),
        },
    ))

    soft_rescue = data["soft_frontier_midprice_delayed_recheck_rescue"]
    soft_rescue_state = soft_rescue.get("state") if isinstance(soft_rescue.get("state"), dict) else {}
    soft_rescue_post_lane = next(
        (lane for lane in soft_rescue.get("lanes") or [] if lane.get("lane") == "post_clean_rescue_birth"),
        {},
    )
    soft_rescue_diag_lane = next(
        (lane for lane in soft_rescue.get("lanes") or [] if lane.get("lane") == "diagnostic_prefreeze_context"),
        {},
    )
    soft_rescue_post = dict(soft_rescue_post_lane.get("summary") or {})
    soft_rescue_diag = soft_rescue_diag_lane.get("summary") or {}
    soft_rescue_post["settled"] = soft_rescue_post.get("rows")
    soft_rescue_post["suppressed_exits"] = soft_rescue_post.get("suppressed")
    soft_rescue_post["current_net_cents"] = soft_rescue_post.get("weighted_current_cents")
    soft_rescue_post["candidate_net_cents"] = soft_rescue_post.get("weighted_candidate_cents")
    soft_rescue_post["delta_vs_current_cents"] = soft_rescue_post.get("weighted_delta_cents")
    soft_rescue_post["loss_control_cost_cents"] = 0.0
    rows.append(lane_row(
        "soft_frontier_midprice_delayed_recheck_rescue",
        (
            f"{soft_rescue_state.get('entry_policy')}_{soft_rescue_state.get('exit_source')}_"
            f"{soft_rescue_state.get('recheck_policy')}"
        ),
        soft_rescue_post,
        list(soft_rescue_post.get("blockers") or []),
        soft_rescue_state.get("freeze_ts_utc"),
        {
            "diagnostic_settled": soft_rescue_diag.get("rows"),
            "diagnostic_helpful_harmful": (
                f"{soft_rescue_diag.get('helpful_suppressed')}/"
                f"{soft_rescue_diag.get('harmful_suppressed')}"
            ),
            "diagnostic_delta_cents": soft_rescue_diag.get("weighted_delta_cents"),
            "diagnostic_reconstructed_share": soft_rescue_diag.get("reconstructed_share"),
            "rule": soft_rescue_state.get("rule"),
        },
    ))

    feature_value = data["feature_gate_value_exit"]
    feature_value_post = next(
        (lane for lane in feature_value.get("lanes") or [] if lane.get("label") == "post_value_exit_birth"),
        {},
    )
    feature_value_best = (feature_value_post.get("variants") or [{}])[0]
    feature_value_diag = next(
        (lane for lane in feature_value.get("lanes") or [] if lane.get("label") == "diagnostic_prefreeze_context"),
        {},
    )
    feature_value_diag_best = (feature_value_diag.get("variants") or [{}])[0]
    rows.append(lane_row(
        "feature_gate_value_exit",
        feature_value_best.get("variant") or (feature_value.get("state") or {}).get("primary_candidate") or "suppress_value_over_hold",
        feature_value_best,
        list(feature_value_best.get("blockers") or []),
        (feature_value.get("state") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_settled": feature_value_diag_best.get("settled"),
            "diagnostic_delta_vs_live_cents": feature_value_diag_best.get("delta_vs_live_cents"),
            "diagnostic_suppressed": feature_value_diag_best.get("suppressed"),
            "diagnostic_suppressed_wl": (
                f"{feature_value_diag_best.get('suppressed_winners')}/"
                f"{feature_value_diag_best.get('suppressed_losers')}"
            ),
        },
    ))

    exit_bid = data["feature_gate_exit_bid"]
    exit_bid_post = next(
        (lane for lane in exit_bid.get("lanes") or [] if lane.get("lane") == "post_exit_bid_birth"),
        {},
    ).get("summary") or {}
    exit_bid_diag = next(
        (lane for lane in exit_bid.get("lanes") or [] if lane.get("lane") == "diagnostic_feature_gate_exit_bid"),
        {},
    ).get("summary") or {}
    rows.append(lane_row(
        "feature_gate_exit_bid_suppression",
        (exit_bid.get("state") or {}).get("candidate") or "feature_gate_exit_bid_min_ge_60_suppress",
        exit_bid_post,
        list(exit_bid_post.get("blockers") or []),
        (exit_bid.get("state") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_settled": exit_bid_diag.get("settled"),
            "diagnostic_delta_vs_live_cents": exit_bid_diag.get("delta_vs_live_cents"),
            "diagnostic_suppressed": exit_bid_diag.get("suppressed_exits"),
            "diagnostic_suppressed_wl": (
                f"{exit_bid_diag.get('suppressed_helpful')}/"
                f"{exit_bid_diag.get('suppressed_harmful')}"
            ),
        },
    ))

    delayed = data["feature_gate_exit_bid_delayed_recheck"]
    delayed_post = next(
        (lane for lane in delayed.get("lanes") or [] if lane.get("lane") == "post_delayed_recheck_birth"),
        {},
    ).get("summary") or {}
    delayed_diag = next(
        (lane for lane in delayed.get("lanes") or [] if lane.get("lane") == "diagnostic_prefreeze_context"),
        {},
    ).get("summary") or {}
    rows.append(lane_row(
        "feature_gate_exit_bid_delayed_recheck",
        (delayed.get("state") or {}).get("candidate") or "delay60_bid_ge60_drop_lte10",
        delayed_post,
        list(delayed_post.get("blockers") or []),
        (delayed.get("state") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_settled": delayed_diag.get("rows"),
            "diagnostic_delta_vs_live_cents": delayed_diag.get("delta_vs_live_cents"),
            "diagnostic_suppressed": delayed_diag.get("suppressed"),
            "diagnostic_suppressed_wl": (
                f"{delayed_diag.get('helpful_suppressed')}/"
                f"{delayed_diag.get('harmful_suppressed')}"
            ),
            "rule": (delayed.get("state") or {}).get("rule"),
        },
    ))

    side_guard = data["value_exit_feature_side_guard"]
    side_guard_post = next(
        (lane for lane in side_guard.get("lanes") or [] if lane.get("label") == "post_feature_side_guard_birth"),
        {},
    ).get("summary") or {}
    side_guard_diag = next(
        (lane for lane in side_guard.get("lanes") or [] if lane.get("label") in {"diagnostic_prefreeze_context", "diagnostic_from_value_freeze"}),
        {},
    ).get("summary") or {}
    rows.append(lane_row(
        "value_exit_feature_side_guard",
        (side_guard.get("state") or {}).get("primary_candidate") or "value_exit_feature_side_guard",
        side_guard_post,
        list(side_guard_post.get("blockers") or []),
        (side_guard.get("state") or {}).get("freeze_ts_utc"),
        {
            "diagnostic_settled": side_guard_diag.get("settled", side_guard_diag.get("rows")),
            "diagnostic_delta_vs_current_cents": side_guard_diag.get(
                "delta_vs_current_cents",
                side_guard_diag.get("feature_side_guard_delta_cents"),
            ),
            "diagnostic_delta_vs_value_only_cents": side_guard_diag.get(
                "delta_vs_value_only_cents",
                side_guard_diag.get("feature_side_guard_delta_vs_value_only_cents"),
            ),
            "diagnostic_suppressed": side_guard_diag.get("suppressed_exits", side_guard_diag.get("suppressed")),
            "diagnostic_suppressed_wl": (
                f"{side_guard_diag.get('suppressed_winners')}/"
                f"{side_guard_diag.get('suppressed_losers')}"
            ),
        },
    ))

    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status"))
        status_counts[status] = status_counts.get(status, 0) + 1
    report = {
        "generated_at_utc": utc_now_iso(),
        "rows": rows,
        "status_counts": dict(sorted(status_counts.items())),
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    rows = report.get("rows") or []
    active = [row for row in rows if row.get("status") in {"forward_positive_under_review", "positive_but_under_sample"}]
    waiting = [row for row in rows if str(row.get("status", "")).startswith("waiting")]
    blocked = [row for row in rows if str(row.get("status", "")).startswith("blocked")]
    return [
        "This dashboard is a research-only status rollup; it is not a promotion gate by itself.",
        f"Positive active exit watches: {[row.get('lane') for row in active]}.",
        f"Waiting/no-op exit watches: {[row.get('lane') for row in waiting]}.",
        f"Blocked exit watches: {[row.get('lane') for row in blocked]}.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Policy Watch Dashboard",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Status counts: `{report.get('status_counts')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Lanes",
            "",
            "| lane | status | settled | suppressed | current c | candidate c | delta c | recovery c | loss cost c | cushion | blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('lane')} | {row.get('status')} | {row.get('settled')} | "
            f"{row.get('suppressed_exits')} | {fmt(row.get('current_net_cents'))} | "
            f"{fmt(row.get('candidate_net_cents'))} | {fmt(row.get('delta_vs_current_cents'))} | "
            f"{fmt(row.get('winner_recovery_cents'))} | {fmt(row.get('loss_control_cost_cents'))} | "
            f"{row.get('full_loss_cushion')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Opportunity Notes", ""])
    for row in report.get("rows") or []:
        opp = row.get("opportunity") or {}
        if opp:
            lines.append(f"- `{row.get('lane')}`: `{opp}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
