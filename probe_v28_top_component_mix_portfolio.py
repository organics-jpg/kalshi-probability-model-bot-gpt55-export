"""Top-component mix portfolio for v28 soft-frontier candidates.

Research-only; no live bot changes or orders.

The current leaderboard's top PnL comes from delayed-recheck exit rows, while
the top broad win-rate rows come from the parent soft-frontier midprice entry
lane. This probe composes them on a market/side key:

1. use the best delayed-recheck rescue row when an exit-clock row exists;
2. fill missing parent entry rows with their conservative entry/hold score;
3. stress whether the resulting broad portfolio still beats live without a
   single lucky suppression or a thin source-quality margin.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import best_per_market
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces
from probe_v28_soft_frontier_midprice_boundary_shrink_watch import (
    BROAD_RULE,
    as_float as sf_as_float,
    passes_broad,
    raw_edge as sf_raw_edge,
    recross as sf_recross,
    summarize_weighted,
    weight_quarter_midprice_boundary,
)
from probe_v28_soft_frontier_midprice_delayed_recheck_exit import (
    BOOK_GAP_JSON,
    REDUCE_JSON,
    choose_exit_row,
    delayed_recheck_pass,
    group_exit_rows,
    path_points,
    read_heartbeats,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
RESCUE_JSON = OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_frontier_latest.json"
DELAYED_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json"
MIDPRICE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_top_component_mix_portfolio_latest.json"
OUT_MD = OUT_DIR / "v28_top_component_mix_portfolio_latest.md"
STATE_JSON = OUT_DIR / "v28_top_component_mix_portfolio_state.json"

MAX_RECONSTRUCTED_SHARE = 0.35
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3
STRICT_RECHECK_VARIANT = {"name": "drop15_bid60", "delay_seconds": 60, "bid_floor": 60, "max_drop": 15}
LEGACY_VARIANT_LABELS = {
    "rescue_drop15_exit_clock_rows_only",
    "rescue_drop15_plus_observable_parent_fill_to75",
    "rescue_drop15_plus_all_parent_fill",
}
NEW_RANK_VARIANT_LABELS = {
    "rescue_drop15_plus_absd_parent_fill_to75",
    "rescue_drop15_plus_recross_parent_fill_to75",
    "rescue_drop15_plus_ask_parent_fill_to75",
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


def load_or_create_state() -> dict[str, Any]:
    existing = load_json(STATE_JSON)
    if existing.get("freeze_ts_utc"):
        return ensure_variant_freezes(existing)
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "top_component_mix_portfolio",
        "candidate": "rescue_drop15_plus_all_parent_fill",
        "parent_components": [
            "soft_frontier_midprice_delayed_recheck_rescue_frontier:drop15_bid60",
            "soft_frontier_midprice_boundary_shrink:diagnostic_entry_quarter_midprice_boundary",
        ],
        "note": "Freeze created after diagnostic component mix; only post-birth rows from this timestamp can count as strict evidence.",
    }
    state = ensure_variant_freezes(state)
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def ensure_variant_freezes(state: dict[str, Any]) -> dict[str, Any]:
    freezes = state.get("variant_freeze_ts_utc")
    if not isinstance(freezes, dict):
        freezes = {}
    base_freeze = str(state.get("freeze_ts_utc") or utc_now_iso())
    changed = False
    for label in LEGACY_VARIANT_LABELS:
        if not freezes.get(label):
            freezes[label] = base_freeze
            changed = True
    for label in NEW_RANK_VARIANT_LABELS:
        if not freezes.get(label):
            freezes[label] = utc_now_iso()
            changed = True
    state["variant_freeze_ts_utc"] = freezes
    if changed and state.get("freeze_ts_utc"):
        STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("market") or ""), str(row.get("side") or ""))


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def observed_raw_edge(row: dict[str, Any]) -> float | None:
    return sf_as_float(row.get("raw_edge")) if row.get("raw_edge") is not None else sf_raw_edge(row)


def observed_recross(row: dict[str, Any]) -> float | None:
    return sf_as_float(row.get("recross_hazard_score")) if row.get("recross_hazard_score") is not None else sf_recross(row)


def observed_abs_d(row: dict[str, Any]) -> float | None:
    return sf_as_float(row.get("abs_d_sigma"))


def observed_ask(row: dict[str, Any]) -> float | None:
    return sf_as_float(row.get("ask_prob"))


def live_cents() -> float:
    return 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))


def parent_entry_summary() -> dict[str, Any]:
    delayed = load_json(DELAYED_JSON)
    summary = delayed.get("diagnostic_parent", {}).get("entry_summary")
    if isinstance(summary, dict):
        return summary
    return {}


def denominator_from_parent() -> int:
    summary = parent_entry_summary()
    entries = fnum(summary.get("entries"))
    coverage = fnum(summary.get("coverage_pct"))
    if entries > 0 and coverage > 0:
        return int(round(entries / (coverage / 100.0)))
    for lane in load_json(MIDPRICE_JSON).get("lanes") or []:
        if isinstance(lane, dict) and str(lane.get("lane")) == "diagnostic_entry":
            return int(fnum(lane.get("future_denominator")))
    return 0


def best_rescue_variant() -> dict[str, Any]:
    variants = [row for row in load_json(RESCUE_JSON).get("variants") or [] if isinstance(row, dict)]
    variants.sort(
        key=lambda row: (
            len([b for b in row.get("blockers") or [] if b != "diagnostic_prefreeze"]),
            int(row.get("harmful_suppressed") or 0),
            -fnum(row.get("candidate_net_cents"), -999999.0),
        )
    )
    return variants[0] if variants else {}


def delayed_base_rows() -> list[dict[str, Any]]:
    for lane in load_json(DELAYED_JSON).get("lanes") or []:
        if isinstance(lane, dict) and str(lane.get("lane")) == "diagnostic_prefreeze_context":
            rows = lane.get("rows")
            return [dict(row) for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    return []


def midprice_parent_rows(policy: str = "diagnostic_entry_quarter_midprice_boundary") -> list[dict[str, Any]]:
    payload = load_json(MIDPRICE_JSON)
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict) or str(lane.get("lane")) != "diagnostic_entry":
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict) and str(variant.get("candidate")) == policy:
                summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
                return [dict(row) for row in summary.get("rows") or [] if isinstance(row, dict)]
    return []


def rescue_rows() -> list[dict[str, Any]]:
    variant = best_rescue_variant()
    out = []
    for row in variant.get("scored_rows") or []:
        if not isinstance(row, dict):
            continue
        item = dict(row)
        item["component"] = f"delayed_recheck_rescue:{(variant.get('variant') or {}).get('name')}"
        item["selected_weighted_cents"] = fnum(row.get("frontier_weighted_candidate_cents"))
        item["selected_cents"] = fnum(row.get("frontier_candidate_cents"))
        item["selected_delta_cents"] = fnum(row.get("frontier_weighted_delta_cents"))
        item["selected_suppressed"] = bool(row.get("frontier_suppressed"))
        out.append(item)
    return out


def base_delayed_rows() -> list[dict[str, Any]]:
    out = []
    for row in delayed_base_rows():
        item = dict(row)
        item["component"] = "delayed_recheck_base"
        item["selected_weighted_cents"] = fnum(row.get("weighted_candidate_cents"))
        item["selected_cents"] = fnum(row.get("candidate_cents"))
        item["selected_delta_cents"] = fnum(row.get("weighted_delta_cents"))
        item["selected_suppressed"] = bool(row.get("suppressed"))
        out.append(item)
    return out


def parent_hold_rows() -> list[dict[str, Any]]:
    out = []
    for row in midprice_parent_rows():
        item = dict(row)
        item["component"] = "parent_midprice_hold_fill"
        item["selected_weighted_cents"] = fnum(row.get("weighted_net_cents"))
        item["selected_cents"] = fnum(row.get("raw_net_cents"))
        item["selected_delta_cents"] = 0.0
        item["selected_suppressed"] = False
        out.append(item)
    return out


def compact_strict_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": source(row),
        "side_won": row.get("side_won"),
        "raw_edge": observed_raw_edge(row),
        "recross_hazard_score": observed_recross(row),
        "abs_d_sigma": observed_abs_d(row),
        "ask_prob": observed_ask(row),
        "raw_net_cents": row.get("raw_net_cents"),
        "weighted_net_cents": row.get("weighted_net_cents"),
        "weight": row.get("weight"),
    }


def broad_predicate_report(row: dict[str, Any]) -> dict[str, Any]:
    raw_edge = fnum(observed_raw_edge(row), float("nan"))
    recross = fnum(observed_recross(row), float("nan"))
    abs_d = fnum(observed_abs_d(row), float("nan"))
    ask = fnum(observed_ask(row), float("nan"))
    checks = {
        "raw_edge": math.isfinite(raw_edge) and raw_edge >= fnum(BROAD_RULE.get("raw_edge_min")),
        "recross": math.isfinite(recross) and recross <= fnum(BROAD_RULE.get("recross_max")),
        "abs_d": math.isfinite(abs_d) and abs_d >= fnum(BROAD_RULE.get("abs_d_min")),
        "ask": math.isfinite(ask) and ask >= fnum(BROAD_RULE.get("ask_min")),
    }
    return {
        "checks": checks,
        "pass_count": sum(1 for passed in checks.values() if passed),
        "missing": [name for name, passed in checks.items() if not passed],
    }


def strict_parent_hold_rows(freeze_ts: str) -> tuple[list[dict[str, Any]], int, dict[str, Any]]:
    all_rows, _, denominator = entry_surfaces(freeze_ts)
    broad_rows = [row for row in all_rows if passes_broad(row)]
    selected = best_per_market(broad_rows)
    summary = summarize_weighted(selected, int(denominator or 0), weight_quarter_midprice_boundary)
    out = []
    pending = []
    for row in summary.get("rows") or []:
        if not isinstance(row, dict):
            continue
        if row.get("side_won") is None:
            pending.append(row)
            continue
        item = dict(row)
        item["component"] = "strict_parent_midprice_hold_fill"
        item["selected_weighted_cents"] = fnum(row.get("weighted_net_cents"))
        item["selected_cents"] = fnum(row.get("raw_net_cents"))
        item["selected_delta_cents"] = 0.0
        item["selected_suppressed"] = False
        out.append(item)
    predicate_reports = [(row, broad_predicate_report(row)) for row in all_rows]
    predicate_pass_counts = {
        name: sum(1 for _, report in predicate_reports if report["checks"].get(name))
        for name in ("raw_edge", "recross", "abs_d", "ask")
    }
    predicate_fail_counts = Counter(
        name
        for _, report in predicate_reports
        for name in report.get("missing") or []
    )
    near_misses = sorted(
        predicate_reports,
        key=lambda item: (
            item[1]["pass_count"],
            fnum(observed_raw_edge(item[0]), -999.0),
            fnum(observed_abs_d(item[0]), -999.0),
            fnum(observed_ask(item[0]), -999.0),
            -fnum(observed_recross(item[0]), 999.0),
        ),
        reverse=True,
    )
    diagnostics = {
        "freeze_ts_utc": freeze_ts,
        "broad_rule": dict(BROAD_RULE),
        "future_denominator": int(denominator or 0),
        "future_observation_rows": len(all_rows),
        "broad_pass_rows": len(broad_rows),
        "predicate_pass_counts": predicate_pass_counts,
        "predicate_fail_counts": dict(predicate_fail_counts),
        "near_miss_examples": [
            {
                **compact_strict_row(row),
                "broad_pass_count": report["pass_count"],
                "broad_missing": report["missing"],
            }
            for row, report in near_misses[:10]
        ],
        "selected_parent_rows": int(summary.get("entries") or 0),
        "selected_active_entries": int(summary.get("active_entries") or 0),
        "selected_settled_rows": len(out),
        "selected_pending_rows": len(pending),
        "selected_coverage_pct": summary.get("coverage_pct"),
        "pending_parent_examples": [compact_strict_row(row) for row in pending[:10]],
        "settled_parent_examples": [compact_strict_row(row) for row in out[:10]],
    }
    return out, int(denominator or 0), diagnostics


def strict_rescue_rows(parent_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    book_rows = group_exit_rows(BOOK_GAP_JSON)
    reduce_rows = group_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    all_rows = []
    exit_clock_rows = []
    for parent in parent_rows:
        item = dict(parent)
        exit_row = choose_exit_row(parent, book_rows, reduce_rows, "latest")
        joined = False
        if exit_row is not None and exit_row.get("exit_ts"):
            current_raw = exit_row.get("current_cents")
            hold_raw = exit_row.get("hold_cents") if exit_row.get("hold_cents") is not None else exit_row.get("candidate_cents")
            if current_raw is not None and hold_raw is not None:
                joined = True
                weight = fnum(parent.get("weight"), 1.0)
                current = fnum(current_raw)
                hold = fnum(hold_raw)
                recheck = delayed_recheck_pass(exit_row, path_points(exit_row, heartbeats), STRICT_RECHECK_VARIANT)
                candidate = hold if recheck.get("suppressed") else current
                item.update(
                    {
                        "component": "strict_delayed_recheck_rescue:drop15_bid60",
                        "exit_ts": exit_row.get("exit_ts"),
                        "exit_reason": exit_row.get("exit_reason"),
                        "p_hold": exit_row.get("p_hold"),
                        "fair_drawdown_cents": exit_row.get("fair_drawdown_cents"),
                        "current_cents": current,
                        "hold_cents": hold,
                        "selected_cents": candidate,
                        "selected_weighted_cents": weight * candidate,
                        "selected_delta_cents": weight * (candidate - current),
                        "selected_suppressed": bool(recheck.get("suppressed")),
                        "joined_exit": True,
                        **recheck,
                    }
                )
        if not joined:
            item["joined_exit"] = False
        all_rows.append(item)
        if joined:
            exit_clock_rows.append(dict(item))
    return all_rows, exit_clock_rows


def fill_rank(row: dict[str, Any]) -> tuple[int, float, float, float, float]:
    approved = 1 if source(row) == "approved_entry" else 0
    return (
        approved,
        fnum(row.get("raw_edge")),
        fnum(row.get("abs_d_sigma")),
        fnum(row.get("ask_prob")),
        -fnum(row.get("recross_hazard_score"), 1.0),
    )


def fill_rank_absd_first(row: dict[str, Any]) -> tuple[int, float, float, float, float]:
    approved = 1 if source(row) == "approved_entry" else 0
    return (
        approved,
        fnum(row.get("abs_d_sigma")),
        fnum(row.get("raw_edge")),
        -fnum(row.get("recross_hazard_score"), 1.0),
        fnum(row.get("ask_prob")),
    )


def fill_rank_recross_first(row: dict[str, Any]) -> tuple[int, float, float, float, float]:
    approved = 1 if source(row) == "approved_entry" else 0
    return (
        approved,
        -fnum(row.get("recross_hazard_score"), 1.0),
        fnum(row.get("raw_edge")),
        fnum(row.get("abs_d_sigma")),
        fnum(row.get("ask_prob")),
    )


def fill_rank_ask_first(row: dict[str, Any]) -> tuple[int, float, float, float, float]:
    approved = 1 if source(row) == "approved_entry" else 0
    return (
        approved,
        fnum(row.get("ask_prob")),
        fnum(row.get("raw_edge")),
        fnum(row.get("abs_d_sigma")),
        -fnum(row.get("recross_hazard_score"), 1.0),
    )


def compose(
    primary: list[dict[str, Any]],
    filler: list[dict[str, Any]],
    mode: str,
    target_coverage: float | None = None,
    target_denominator: int | None = None,
) -> list[dict[str, Any]]:
    rows_by_key = {key(row): dict(row) for row in primary}
    candidates = [row for row in filler if key(row) not in rows_by_key]
    if mode == "approved_fill":
        candidates = [row for row in candidates if source(row) == "approved_entry"]
    elif mode == "observable_ranked_fill":
        candidates = sorted(candidates, key=fill_rank, reverse=True)
    elif mode == "observable_absd_ranked_fill":
        candidates = sorted(candidates, key=fill_rank_absd_first, reverse=True)
    elif mode == "observable_recross_ranked_fill":
        candidates = sorted(candidates, key=fill_rank_recross_first, reverse=True)
    elif mode == "observable_ask_ranked_fill":
        candidates = sorted(candidates, key=fill_rank_ask_first, reverse=True)
    elif mode == "all_parent_fill":
        candidates = list(candidates)
    else:
        candidates = []

    if target_coverage is not None:
        denominator = target_denominator if target_denominator is not None else denominator_from_parent()
        required = int(math.ceil(denominator * target_coverage / 100.0)) if denominator else len(primary)
        candidates = candidates[: max(0, required - len(rows_by_key))]

    for row in candidates:
        rows_by_key[key(row)] = dict(row)
    return list(rows_by_key.values())


def summarize(label: str, rows: list[dict[str, Any]], denominator: int, strict_forward: bool = False) -> dict[str, Any]:
    net = sum(fnum(row.get("selected_weighted_cents")) for row in rows)
    counts = Counter(source(row) for row in rows)
    reconstructed = len(rows) - int(counts.get("approved_entry") or 0)
    recon_share = reconstructed / len(rows) if rows else None
    source_gate_row_margin = int(math.floor(MAX_RECONSTRUCTED_SHARE * len(rows))) - reconstructed if rows else None
    coverage = 100.0 * len(rows) / denominator if denominator else None
    live = live_cents()
    wins = sum(1 for row in rows if fnum(row.get("selected_weighted_cents")) > 0)
    losses = sum(1 for row in rows if fnum(row.get("selected_weighted_cents")) < 0)
    suppressed = [row for row in rows if row.get("selected_suppressed")]
    helpful = [row for row in suppressed if fnum(row.get("selected_delta_cents")) > 0]
    harmful = [row for row in suppressed if fnum(row.get("selected_delta_cents")) < 0]
    blockers: list[str] = []
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    if len(rows) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if recon_share is not None and recon_share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    elif source_gate_row_margin is not None and source_gate_row_margin <= 0:
        blockers.append("source_gate_zero_row_margin")
    elif source_gate_row_margin is not None and source_gate_row_margin < 2:
        blockers.append("source_gate_margin_lt_2")
    if net <= 0:
        blockers.append("net_not_positive")
    if int(max(0.0, net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net <= live:
        blockers.append("does_not_beat_refreshed_live_baseline")
    if harmful:
        blockers.append("harmful_suppression_present")

    top = max(rows, key=lambda row: fnum(row.get("selected_weighted_cents")), default={})
    stress_without_top = net - fnum(top.get("selected_weighted_cents")) if top else net
    suppression_delta = sum(fnum(row.get("selected_delta_cents")) for row in suppressed)
    stress_without_suppression = net - suppression_delta
    filler_rows = [row for row in rows if str(row.get("component") or "").startswith("parent_midprice")]
    filler_net = sum(fnum(row.get("selected_weighted_cents")) for row in filler_rows)
    exit_rows = [row for row in rows if str(row.get("component") or "").startswith("delayed_recheck")]
    exit_net = sum(fnum(row.get("selected_weighted_cents")) for row in exit_rows)
    approved_rows = [row for row in rows if source(row) == "approved_entry"]
    reconstructed_rows = [row for row in rows if source(row) != "approved_entry"]

    def bucket_stats(bucket_rows: list[dict[str, Any]]) -> dict[str, Any]:
        bucket_net = sum(fnum(row.get("selected_weighted_cents")) for row in bucket_rows)
        return {
            "rows": len(bucket_rows),
            "net_cents": bucket_net,
            "wins": sum(1 for row in bucket_rows if fnum(row.get("selected_weighted_cents")) > 0),
            "losses": sum(1 for row in bucket_rows if fnum(row.get("selected_weighted_cents")) < 0),
        }

    failure_modes = []
    if not strict_forward:
        failure_modes.append("strict_forward_evidence_missing")
    if recon_share is not None and recon_share > MAX_RECONSTRUCTED_SHARE:
        failure_modes.append("source_quality_error")
    elif source_gate_row_margin is not None and source_gate_row_margin < 2:
        failure_modes.append("source_quality_fragility")
    if int(max(0.0, net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        failure_modes.append("fragility_error")
    if coverage is None or coverage < TARGET_COVERAGE_MIN or coverage > TARGET_COVERAGE_MAX:
        failure_modes.append("coverage_shape_error")
    if harmful:
        failure_modes.append("exit_policy_harmful_suppression")
    if exit_rows and fnum(rows[0].get("selected_weighted_cents")) < 0:
        failure_modes.append("residual_loss_cluster")

    return {
        "label": label,
        "entries": len(rows),
        "settled": len(rows),
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "net_cents": net,
        "delta_vs_live_cents": net - live,
        "source_counts": dict(counts),
        "reconstructed_share": recon_share,
        "source_gate_row_margin": source_gate_row_margin,
        "full_loss_cushion": int(max(0.0, net) // 100.0),
        "suppressed_rows": len(suppressed),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "suppressed_delta_cents": suppression_delta,
        "filler_rows": len(filler_rows),
        "filler_net_cents": filler_net,
        "component_attribution": {
            "exit_rescue": bucket_stats(exit_rows),
            "parent_fill": bucket_stats(filler_rows),
            "approved_entry": bucket_stats(approved_rows),
            "reconstructed_or_rejected": bucket_stats(reconstructed_rows),
        },
        "failure_modes": failure_modes,
        "stress_without_top_row_net_cents": stress_without_top,
        "stress_without_top_row_delta_vs_live_cents": stress_without_top - live,
        "top_row": {
            "market": top.get("market"),
            "side": top.get("side"),
            "source": top.get("source"),
            "component": top.get("component"),
            "selected_weighted_cents": top.get("selected_weighted_cents"),
        } if top else {},
        "stress_without_suppression_net_cents": stress_without_suppression,
        "stress_without_suppression_delta_vs_live_cents": stress_without_suppression - live,
        "component_counts": dict(Counter(str(row.get("component") or "unknown") for row in rows)),
        "blockers": blockers,
        "rows": sorted(rows, key=lambda row: fnum(row.get("selected_weighted_cents"))),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    denominator = denominator_from_parent()
    parent = parent_hold_rows()
    base = base_delayed_rows()
    rescue = rescue_rows()
    diagnostic_variants = [
        summarize("delayed_base_exit_clock_rows_only", base, denominator),
        summarize("rescue_drop15_exit_clock_rows_only", rescue, denominator),
        summarize("rescue_drop15_plus_approved_parent_fill", compose(rescue, parent, "approved_fill"), denominator),
        summarize("rescue_drop15_plus_observable_parent_fill_to75", compose(rescue, parent, "observable_ranked_fill", 75.0), denominator),
        summarize("rescue_drop15_plus_absd_parent_fill_to75", compose(rescue, parent, "observable_absd_ranked_fill", 75.0), denominator),
        summarize("rescue_drop15_plus_recross_parent_fill_to75", compose(rescue, parent, "observable_recross_ranked_fill", 75.0), denominator),
        summarize("rescue_drop15_plus_ask_parent_fill_to75", compose(rescue, parent, "observable_ask_ranked_fill", 75.0), denominator),
        summarize("rescue_drop15_plus_all_parent_fill", compose(rescue, parent, "all_parent_fill"), denominator),
    ]
    variant_freezes = state.get("variant_freeze_ts_utc") if isinstance(state.get("variant_freeze_ts_utc"), dict) else {}
    strict_parent, strict_denominator, strict_forward_diagnostics = strict_parent_hold_rows(str(state["freeze_ts_utc"]))
    strict_all, strict_exit_clock = strict_rescue_rows(strict_parent)
    strict_forward_diagnostics.update(
        {
            "settled_parent_rows_with_exit_clock": len(strict_exit_clock),
            "settled_parent_rows_without_exit_clock": max(0, len(strict_parent) - len(strict_exit_clock)),
            "strict_all_scored_rows": len(strict_all),
        }
    )
    variant_strict_context: dict[str, dict[str, Any]] = {}
    strict_surface_cache: dict[str, tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int, dict[str, Any]]] = {
        str(state["freeze_ts_utc"]): (strict_parent, strict_all, strict_exit_clock, strict_denominator, strict_forward_diagnostics)
    }

    def strict_surface(freeze_ts: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int, dict[str, Any]]:
        cached = strict_surface_cache.get(freeze_ts)
        if cached is not None:
            return cached
        parent_rows, denominator_value, diagnostics = strict_parent_hold_rows(freeze_ts)
        all_rows, exit_rows = strict_rescue_rows(parent_rows)
        diagnostics = dict(diagnostics)
        diagnostics.update(
            {
                "settled_parent_rows_with_exit_clock": len(exit_rows),
                "settled_parent_rows_without_exit_clock": max(0, len(parent_rows) - len(exit_rows)),
                "strict_all_scored_rows": len(all_rows),
            }
        )
        cached = (parent_rows, all_rows, exit_rows, denominator_value, diagnostics)
        strict_surface_cache[freeze_ts] = cached
        return cached

    def strict_variant(label: str, mode: str | None = None, target_coverage: float | None = None, exit_clock_only: bool = False, all_parent: bool = False) -> dict[str, Any]:
        freeze_ts = str(variant_freezes.get(label) or state["freeze_ts_utc"])
        parent_rows, all_rows, exit_rows, denominator_value, diagnostics = strict_surface(freeze_ts)
        if exit_clock_only:
            rows = exit_rows
        elif all_parent:
            rows = all_rows
        else:
            rows = compose(exit_rows, parent_rows, str(mode), target_coverage, denominator_value)
        variant_strict_context[label] = {
            "freeze_ts_utc": freeze_ts,
            "future_denominator": diagnostics.get("future_denominator"),
            "broad_pass_rows": diagnostics.get("broad_pass_rows"),
            "selected_parent_rows": diagnostics.get("selected_parent_rows"),
            "selected_settled_rows": diagnostics.get("selected_settled_rows"),
            "selected_pending_rows": diagnostics.get("selected_pending_rows"),
            "settled_parent_rows_with_exit_clock": len(exit_rows),
            "strict_all_scored_rows": len(all_rows),
        }
        return summarize(f"post_birth_{label}", rows, denominator_value, True)

    strict_variants = [
        strict_variant("rescue_drop15_exit_clock_rows_only", exit_clock_only=True),
        strict_variant("rescue_drop15_plus_observable_parent_fill_to75", "observable_ranked_fill", 75.0),
        strict_variant("rescue_drop15_plus_absd_parent_fill_to75", "observable_absd_ranked_fill", 75.0),
        strict_variant("rescue_drop15_plus_recross_parent_fill_to75", "observable_recross_ranked_fill", 75.0),
        strict_variant("rescue_drop15_plus_ask_parent_fill_to75", "observable_ask_ranked_fill", 75.0),
        strict_variant("rescue_drop15_plus_all_parent_fill", all_parent=True),
    ]
    variants = diagnostic_variants + strict_variants
    variants.sort(
        key=lambda row: (
            len([b for b in row.get("blockers") or [] if b != "diagnostic_prefreeze"]),
            -fnum(row.get("net_cents"), -999999.0),
        )
    )
    best = variants[0] if variants else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "rescue": str(RESCUE_JSON),
            "delayed": str(DELAYED_JSON),
            "midprice": str(MIDPRICE_JSON),
            "live_summary": str(LIVE_SUMMARY_JSON),
        },
        "state": state,
        "parent_entry_summary": parent_entry_summary(),
        "denominator": denominator,
        "strict_denominator": strict_denominator,
        "strict_forward_diagnostics": strict_forward_diagnostics,
        "variant_strict_context": variant_strict_context,
        "best_rescue_variant": (best_rescue_variant().get("variant") or {}).get("name"),
        "diagnostic_variants": diagnostic_variants,
        "strict_variants": strict_variants,
        "variants": variants,
        "interpretation": [
            "Research-only component mix; no live bot changes or orders.",
            (
                f"Best diagnostic mix {best.get('label')} has {best.get('entries')} rows, "
                f"coverage {best.get('coverage_pct')}%, net {best.get('net_cents')}c, "
                f"W/L {best.get('wins')}/{best.get('losses')}, reconstructed share {best.get('reconstructed_share')}, "
                f"blockers {best.get('blockers')}."
            ) if best else "No variants scored.",
            "The key audit is whether exit-clock PnL remains broad after filling parent entry rows that lacked exit-clock rescue rows.",
            f"Portfolio freeze UTC is {state.get('freeze_ts_utc')}; current scored rows are diagnostic parent rows only.",
            (
                "Post-birth strict check: "
                f"{strict_forward_diagnostics.get('selected_parent_rows')} selected parent rows, "
                f"{strict_forward_diagnostics.get('selected_settled_rows')} settled, "
                f"{strict_forward_diagnostics.get('selected_pending_rows')} pending, "
                f"{strict_forward_diagnostics.get('settled_parent_rows_with_exit_clock')} joined to exit-clock rows."
            ),
            "Post-birth variants are the only strict-forward evidence for this portfolio.",
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
        "# v28 Top-Component Mix Portfolio",
        "",
        "Research-only component mix. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Parent denominator: `{report.get('denominator')}`",
        f"- Strict denominator: `{report.get('strict_denominator')}`",
        f"- Best rescue variant: `{report.get('best_rescue_variant')}`",
        f"- Portfolio freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    strict_diag = report.get("strict_forward_diagnostics") or {}
    lines.extend(
        [
            "",
            "## Strict Forward Diagnostics",
            "",
            f"- Future denominator: `{strict_diag.get('future_denominator')}`",
            f"- Future observation rows: `{strict_diag.get('future_observation_rows')}`",
            f"- Broad-pass rows: `{strict_diag.get('broad_pass_rows')}`",
            f"- Predicate pass counts: `{strict_diag.get('predicate_pass_counts')}`",
            f"- Predicate fail counts: `{strict_diag.get('predicate_fail_counts')}`",
            f"- Selected parent rows: `{strict_diag.get('selected_parent_rows')}`",
            f"- Settled selected rows: `{strict_diag.get('selected_settled_rows')}`",
            f"- Pending selected rows: `{strict_diag.get('selected_pending_rows')}`",
            f"- Settled selected rows with exit-clock join: `{strict_diag.get('settled_parent_rows_with_exit_clock')}`",
            f"- Settled selected rows without exit-clock join: `{strict_diag.get('settled_parent_rows_without_exit_clock')}`",
            f"- Strict all scored rows: `{strict_diag.get('strict_all_scored_rows')}`",
        ]
    )
    variant_context = report.get("variant_strict_context") or {}
    if variant_context:
        lines.extend(
            [
                "",
                "### Variant Freeze Clocks",
                "",
                "| variant | freeze UTC | denominator | selected | settled | pending | exit-clock joined |",
                "|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for label, ctx in sorted(variant_context.items()):
            if not isinstance(ctx, dict):
                continue
            lines.append(
                f"| `{label}` | `{ctx.get('freeze_ts_utc')}` | {ctx.get('future_denominator')} | "
                f"{ctx.get('selected_parent_rows')} | {ctx.get('selected_settled_rows')} | "
                f"{ctx.get('selected_pending_rows')} | {ctx.get('settled_parent_rows_with_exit_clock')} |"
            )
    pending = strict_diag.get("pending_parent_examples") or []
    if pending:
        lines.extend(
            [
                "",
                "### Pending Parent Examples",
                "",
                "| market | side | source | raw edge | recross | abs d | ask | weight |",
                "|---|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in pending[:10]:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | "
                f"{fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('weight'))} |"
            )
    near_misses = strict_diag.get("near_miss_examples") or []
    if near_misses:
        lines.extend(
            [
                "",
                "### Strict Near Miss Examples",
                "",
                "| market | side | source | pass | missing | raw edge | recross | abs d | ask |",
                "|---|---|---|---:|---|---:|---:|---:|---:|",
            ]
        )
        for row in near_misses[:10]:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | "
                f"{row.get('broad_pass_count')} | {', '.join(row.get('broad_missing') or [])} | "
                f"{fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} |"
            )
    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| rank | label | entries | W/L | coverage | pnl | delta live | source | src margin | cushion | suppressed H/H | filler rows/net | no-top delta live | no-supp delta live | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate(report.get("variants") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('label')}` | {row.get('entries')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))}% | {fmt(row.get('net_cents'))} | {fmt(row.get('delta_vs_live_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('source_gate_row_margin')} | {row.get('full_loss_cushion')} | "
            f"{row.get('helpful_suppressed')}/{row.get('harmful_suppressed')} | "
            f"{row.get('filler_rows')}/{fmt(row.get('filler_net_cents'))} | "
            f"{fmt(row.get('stress_without_top_row_delta_vs_live_cents'))} | "
            f"{fmt(row.get('stress_without_suppression_delta_vs_live_cents'))} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    best = (report.get("variants") or [{}])[0]
    lines.extend(["", "## Best Variant Attribution", ""])
    best_attr = best.get("component_attribution") if isinstance(best.get("component_attribution"), dict) else {}
    if best_attr:
        lines.extend(
            [
                "| bucket | rows | W/L | net |",
                "|---|---:|---:|---:|",
            ]
        )
        for name in ("exit_rescue", "parent_fill", "approved_entry", "reconstructed_or_rejected"):
            bucket = best_attr.get(name) if isinstance(best_attr.get(name), dict) else {}
            lines.append(
                f"| `{name}` | {bucket.get('rows')} | {bucket.get('wins')}/{bucket.get('losses')} | {fmt(bucket.get('net_cents'))} |"
            )
    lines.extend(
        [
            "",
            f"- Failure modes: `{', '.join(best.get('failure_modes') or [])}`",
            f"- Source counts: `{best.get('source_counts')}`",
            f"- Component counts: `{best.get('component_counts')}`",
        ]
    )
    lines.extend(["", "## Worst Rows By Best Variant", ""])
    lines.extend([
        "| market | side | source | component | weighted c | suppressed | exit reason | p_hold | exit bid | recheck bid | drop |",
        "|---|---|---|---|---:|---|---|---:|---:|---:|---:|",
    ])
    for row in (best.get("rows") or [])[:16]:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {row.get('component')} | "
            f"{fmt(row.get('selected_weighted_cents'))} | {row.get('selected_suppressed')} | "
            f"{row.get('exit_reason')} | {fmt(row.get('p_hold'))} | {fmt(row.get('exit_bid'))} | "
            f"{fmt(row.get('recheck_bid'))} | {fmt(row.get('window_drop_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
