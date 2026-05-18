"""Dual-clock delayed recheck rescue for feature-gate size-shrink branch.

Research-only; no live bot changes or orders.

Fast and late collapse/rebound repairs catch different false-collapse exits.
This probe tests an observable union policy:

- high-bid delayed recheck protects clipped winners after 60s;
- fast collapse rebound rescues shallow false collapses after 60s;
- late collapse rebound rescues deep false collapses after 90s.

All parent rows are diagnostic. The union has its own freeze timestamp, and
only rows after that timestamp can be considered strict evidence.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state as load_feature_gate_state
from probe_v28_boundary_clock_feature_gate_candidate import market, net, source
from probe_v28_feature_gate_coverage_size_shrink import repair_weight
from probe_v28_feature_gate_size_shrink_delayed_recheck_rescue import (
    BOOK_GAP_JSON,
    LIVE_SUMMARY_JSON,
    REDUCE_JSON,
    build_entries,
    choose_exit_row,
    fnum,
    grouped_exit_rows,
    load_json,
    path_points,
    read_heartbeats,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_dual_clock_recheck_rescue_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_dual_clock_recheck_rescue_latest.md"
STATE_JSON = OUT_DIR / "v28_feature_gate_dual_clock_recheck_rescue_state.json"

POLICY = "repair_low_absd_quarter_else_half"

CONDITIONS = {
    "high60": {
        "delay_seconds": 60,
        "kind": "high",
        "bid_floor": 60,
        "max_drop": 10,
    },
    "fast_collapse60": {
        "delay_seconds": 60,
        "kind": "collapse",
        "exit_bid_max": 45,
        "recheck_bid_floor": 40,
        "rebound_min": 10,
        "max_drop": 15,
    },
    "late_collapse90": {
        "delay_seconds": 90,
        "kind": "collapse",
        "exit_bid_max": 25,
        "recheck_bid_floor": 25,
        "rebound_min": 8,
        "max_drop": 15,
    },
}

VARIANTS = [
    {"name": "base_no_exit_overlay", "conditions": []},
    {"name": "high60_only", "conditions": ["high60"]},
    {"name": "fast_collapse60_only", "conditions": ["fast_collapse60"]},
    {"name": "late_collapse90_only", "conditions": ["late_collapse90"]},
    {"name": "high60_or_fast_collapse60", "conditions": ["high60", "fast_collapse60"]},
    {"name": "high60_or_late_collapse90", "conditions": ["high60", "late_collapse90"]},
    {"name": "high60_or_fast_collapse60_or_late_collapse90", "conditions": ["high60", "fast_collapse60", "late_collapse90"]},
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    existing = load_json(STATE_JSON)
    if existing:
        return existing
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_dual_clock_recheck_rescue",
        "parent_policy": POLICY,
        "note": "Freeze created after diagnostic fast+late collapse union discovery; post-birth rows are the only strict-forward evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "")


def condition_result(exit_row: dict[str, Any], points: list[dict[str, Any]], condition_name: str) -> dict[str, Any]:
    condition = CONDITIONS[condition_name]
    if not points:
        return {
            "suppressed": False,
            "condition": condition_name,
            "exit_bid": None,
            "recheck_bid": None,
            "min_window_bid": None,
            "window_drop_cents": None,
            "rebound_cents": None,
            "post_recheck_min_bid": None,
            "post_recheck_adverse_cents": None,
        }
    exit_ts = points[0]["ts"]
    exit_bid = fnum(points[0].get("held_bid"), None)
    recheck_ts = exit_ts + timedelta(seconds=int(condition["delay_seconds"]))
    recheck = next((point for point in points if point["ts"] >= recheck_ts), None)
    recheck_bid = None if recheck is None else fnum(recheck.get("held_bid"), None)
    window = [point for point in points if point["ts"] <= recheck_ts]
    min_window_bid = min([fnum(point.get("held_bid"), 0.0) or 0.0 for point in window], default=None)
    drop = None if min_window_bid is None or exit_bid is None else exit_bid - min_window_bid
    rebound = None if recheck_bid is None or exit_bid is None else recheck_bid - exit_bid
    post = [point for point in points if point["ts"] >= recheck_ts]
    post_min = min([fnum(point.get("held_bid"), 0.0) or 0.0 for point in post], default=None)
    adverse = None if post_min is None or recheck_bid is None else recheck_bid - post_min
    reason = str(exit_row.get("exit_reason") or "")
    if condition["kind"] == "high":
        suppressed = (
            recheck_bid is not None
            and recheck_bid >= float(condition["bid_floor"])
            and drop is not None
            and drop <= float(condition["max_drop"])
        )
    else:
        suppressed = (
            "collapse" in reason
            and exit_bid is not None
            and exit_bid <= float(condition["exit_bid_max"])
            and recheck_bid is not None
            and recheck_bid >= float(condition["recheck_bid_floor"])
            and rebound is not None
            and rebound >= float(condition["rebound_min"])
            and drop is not None
            and drop <= float(condition["max_drop"])
        )
    return {
        "suppressed": suppressed,
        "condition": condition_name,
        "exit_bid": exit_bid,
        "recheck_bid": recheck_bid,
        "min_window_bid": min_window_bid,
        "window_drop_cents": drop,
        "rebound_cents": rebound,
        "post_recheck_min_bid": post_min,
        "post_recheck_adverse_cents": adverse,
    }


def recheck_union(exit_row: dict[str, Any], points: list[dict[str, Any]], condition_names: list[str]) -> dict[str, Any]:
    results = [condition_result(exit_row, points, name) for name in condition_names]
    suppressed_results = [row for row in results if row.get("suppressed")]
    if not suppressed_results:
        base = results[0] if results else {}
        return {
            "suppressed": False,
            "suppression_rule": None,
            "condition_results": results,
            "exit_bid": base.get("exit_bid"),
            "recheck_bid": base.get("recheck_bid"),
            "window_drop_cents": base.get("window_drop_cents"),
            "rebound_cents": base.get("rebound_cents"),
            "post_recheck_adverse_cents": base.get("post_recheck_adverse_cents"),
        }
    best = max(suppressed_results, key=lambda row: (fnum(row.get("recheck_bid"), 0.0) or 0.0, -(fnum(row.get("post_recheck_adverse_cents"), 0.0) or 0.0)))
    return {
        "suppressed": True,
        "suppression_rule": best.get("condition"),
        "condition_results": results,
        "exit_bid": best.get("exit_bid"),
        "recheck_bid": best.get("recheck_bid"),
        "window_drop_cents": best.get("window_drop_cents"),
        "rebound_cents": best.get("rebound_cents"),
        "post_recheck_adverse_cents": best.get("post_recheck_adverse_cents"),
    }


def evaluate_variant(
    variant: dict[str, Any],
    entries: list[dict[str, Any]],
    anchor_keys: set[tuple[str, str]],
    denominator: int,
    book_rows: dict[tuple[str, str], list[dict[str, Any]]],
    reduce_rows: dict[tuple[str, str], list[dict[str, Any]]],
    heartbeats: list[dict[str, Any]],
    live_cents: float,
    lane_label: str,
    strict_forward: bool,
) -> dict[str, Any]:
    scored = []
    for entry in entries:
        weight = repair_weight(POLICY, entry, anchor_keys)
        entry_hold = net(entry)
        exit_row = choose_exit_row(entry, book_rows, reduce_rows)
        current = entry_hold
        hold = entry_hold
        joined = False
        recheck = {
            "suppressed": False,
            "suppression_rule": None,
            "exit_bid": None,
            "recheck_bid": None,
            "window_drop_cents": None,
            "rebound_cents": None,
            "post_recheck_adverse_cents": None,
        }
        if exit_row is not None and exit_row.get("exit_ts"):
            cur = exit_row.get("current_cents")
            held = exit_row.get("hold_cents") if exit_row.get("hold_cents") is not None else exit_row.get("candidate_cents")
            if cur is not None and held is not None:
                joined = True
                current = float(fnum(cur) or 0.0)
                hold = float(fnum(held) or 0.0)
                recheck = recheck_union(exit_row, path_points(exit_row, heartbeats), list(variant.get("conditions") or []))
        candidate = hold if recheck["suppressed"] else current
        scored.append({
            "market": market(entry),
            "side": side(entry),
            "source": source(entry),
            "weight": weight,
            "entry_hold_cents": entry_hold,
            "joined_exit": joined,
            "current_exit_cents": current,
            "hold_cents": hold,
            "candidate_cents": candidate,
            "weighted_candidate_cents": weight * candidate,
            "weighted_current_exit_cents": weight * current,
            "weighted_entry_hold_cents": weight * entry_hold,
            "weighted_delta_vs_current_exit_cents": weight * (candidate - current),
            "exit_reason": None if exit_row is None else exit_row.get("exit_reason"),
            **recheck,
        })
    candidate_net = sum(row["weighted_candidate_cents"] for row in scored)
    current_net = sum(row["weighted_current_exit_cents"] for row in scored)
    entry_hold_net = sum(row["weighted_entry_hold_cents"] for row in scored)
    suppressed = [row for row in scored if row.get("suppressed")]
    counts = Counter(source(row) for row in entries)
    recon = (len(entries) - int(counts.get("approved_entry") or 0)) / len(entries) if entries else None
    coverage = 100.0 * len(entries) / denominator if denominator else 0.0
    blockers = []
    if len(entries) < 30:
        blockers.append("settled_lt_30")
    if coverage < 75.0:
        blockers.append("coverage_too_low")
    if coverage > 90.0:
        blockers.append("coverage_too_high")
    if recon is not None and recon > 0.35:
        blockers.append("row_reconstructed_share_gt_35pct")
    if candidate_net <= 0:
        blockers.append("weighted_net_not_positive")
    if int(max(0.0, candidate_net) // 100.0) < 3:
        blockers.append("full_loss_cushion_lt_3")
    if candidate_net <= live_cents:
        blockers.append("does_not_beat_refreshed_live_baseline")
    if any(row.get("suppressed") and row["weighted_delta_vs_current_exit_cents"] < 0 for row in scored):
        blockers.append("harmful_suppression_present")
    if any(row.get("suppressed") and fnum(row.get("post_recheck_adverse_cents"), 0.0) >= 25.0 for row in scored):
        blockers.append("post_recheck_adverse_ge_25c")
    if not strict_forward:
        blockers.extend(["diagnostic_prefreeze", "dual_clock_rescue_not_independently_frozen"])
    return {
        "lane": lane_label,
        "strict_forward": strict_forward,
        "variant": variant,
        "entries": len(entries),
        "settled": len(entries),
        "wins": sum(1 for row in scored if row["weighted_candidate_cents"] > 0),
        "losses": sum(1 for row in scored if row["weighted_candidate_cents"] < 0),
        "coverage_pct": coverage,
        "source_counts": dict(counts),
        "reconstructed_share": recon,
        "entry_hold_net_cents": entry_hold_net,
        "current_exit_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_current_exit_cents": candidate_net - current_net,
        "delta_vs_entry_hold_cents": candidate_net - entry_hold_net,
        "delta_vs_live_cents": candidate_net - live_cents,
        "joined_exit_rows": sum(1 for row in scored if row.get("joined_exit")),
        "suppressed_rows": len(suppressed),
        "helpful_suppressed": sum(1 for row in suppressed if row["weighted_delta_vs_current_exit_cents"] > 0),
        "harmful_suppressed": sum(1 for row in suppressed if row["weighted_delta_vs_current_exit_cents"] < 0),
        "suppressed_delta_cents": sum(row["weighted_delta_vs_current_exit_cents"] for row in suppressed),
        "suppression_rule_counts": dict(Counter(row.get("suppression_rule") for row in suppressed)),
        "suppressed_post_recheck_adverse_ge_10": sum(1 for row in suppressed if fnum(row.get("post_recheck_adverse_cents"), 0.0) >= 10.0),
        "suppressed_post_recheck_adverse_ge_25": sum(1 for row in suppressed if fnum(row.get("post_recheck_adverse_cents"), 0.0) >= 25.0),
        "worst_suppressed_post_recheck_adverse_cents": max([fnum(row.get("post_recheck_adverse_cents"), 0.0) or 0.0 for row in suppressed], default=0.0),
        "full_loss_cushion": int(max(0.0, candidate_net) // 100.0),
        "blockers": blockers,
        "suppressed_rows_detail": suppressed,
        "worst_rows": sorted(scored, key=lambda row: row["weighted_candidate_cents"])[:12],
    }


def evaluate_lane(label: str, strict_forward: bool, freeze_ts: str) -> dict[str, Any]:
    entries, anchor_keys, denominator = build_entries(freeze_ts)
    book_rows = grouped_exit_rows(BOOK_GAP_JSON)
    reduce_rows = grouped_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    live_cents = 100.0 * float(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars") or 0.0)
    variants = [
        evaluate_variant(variant, entries, anchor_keys, denominator, book_rows, reduce_rows, heartbeats, live_cents, label, strict_forward)
        for variant in VARIANTS
    ]
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("candidate_net_cents") or -999999.0),
            -float(row.get("delta_vs_current_exit_cents") or -999999.0),
        )
    )
    return {
        "lane": label,
        "strict_forward": strict_forward,
        "freeze_ts_utc": freeze_ts,
        "denominator": denominator,
        "entry_rows": len(entries),
        "variants": variants,
        "best": variants[0] if variants else {},
    }


def build_report() -> dict[str, Any]:
    feature_state = load_feature_gate_state()
    state = load_or_create_state()
    diagnostic = evaluate_lane("diagnostic_prefreeze_context", False, str(feature_state["freeze_ts_utc"]))
    post = evaluate_lane("post_dual_clock_rescue_birth", True, str(state["freeze_ts_utc"]))
    best = diagnostic.get("best") or {}
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_state.get("freeze_ts_utc"),
        "state": state,
        "policy": POLICY,
        "conditions": CONDITIONS,
        "lanes": [diagnostic, post],
        "variants": diagnostic.get("variants") or [],
        "interpretation": [
            "Research-only dual-clock delayed recheck rescue; no live bot changes or orders.",
            (
                f"Diagnostic best {((best.get('variant') or {}).get('name'))} has net {best.get('candidate_net_cents')}c, "
                f"delta vs current exits {best.get('delta_vs_current_exit_cents')}c, W/L {best.get('wins')}/{best.get('losses')}, "
                f"suppressed {best.get('suppressed_rows')}, blockers {best.get('blockers')}."
            ) if best else "No diagnostic variants scored.",
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
        "# v28 Feature-Gate Dual-Clock Recheck Rescue",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Dual-clock freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Variants",
        "",
        "| rank | variant | W/L | coverage | source | candidate | delta current | delta live | suppressed | H/H | rules | adverse >=10/25 | worst adverse | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("variants") or [], start=1):
        variant = row.get("variant") or {}
        lines.append(
            f"| {idx} | `{variant.get('name')}` | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))}% | {fmt(row.get('reconstructed_share'))} | "
            f"{fmt(row.get('candidate_net_cents'))} | {fmt(row.get('delta_vs_current_exit_cents'))} | "
            f"{fmt(row.get('delta_vs_live_cents'))} | {row.get('suppressed_rows')} | "
            f"{row.get('helpful_suppressed')}/{row.get('harmful_suppressed')} | {row.get('suppression_rule_counts')} | "
            f"{row.get('suppressed_post_recheck_adverse_ge_10')}/{row.get('suppressed_post_recheck_adverse_ge_25')} | "
            f"{fmt(row.get('worst_suppressed_post_recheck_adverse_cents'))} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    lines.extend([
        "",
        "## Suppressed Rows For Best Variant",
        "",
        "| market | side | source | reason | current | hold | delta | rule | exit bid | recheck bid | rebound | adverse |",
        "|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|",
    ])
    best_rows = ((report.get("variants") or [{}])[0].get("suppressed_rows_detail") or []) if report.get("variants") else []
    for row in best_rows:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('current_exit_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('weighted_delta_vs_current_exit_cents'))} | {row.get('suppression_rule')} | "
            f"{fmt(row.get('exit_bid'))} | {fmt(row.get('recheck_bid'))} | {fmt(row.get('rebound_cents'))} | "
            f"{fmt(row.get('post_recheck_adverse_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
