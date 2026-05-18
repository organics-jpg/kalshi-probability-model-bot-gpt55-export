"""Delayed-recheck exit overlay for the strict feature-gate size-shrink lane.

Research-only; no live bot changes or orders.

The closest strict broad-ish lane now clears sample, coverage, positive net,
and cushion, but remains below the refreshed live baseline and fails row-count
source quality. This probe asks whether the newer delayed-recheck exit repair
improves that strict lane without touching entry selection or using source
labels in the rule.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state as load_feature_gate_state
from probe_v28_boundary_clock_feature_gate_candidate import market, net, source
from probe_v28_feature_gate_coverage_size_shrink import (
    ANCHOR_RULE,
    REPAIR_RULE,
    repair_weight,
    row_key,
    selected,
)
from probe_v28_feature_gate_exit_bid_path_risk import parse_utc, to_eastern_naive
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces
from probe_v28_post_exit_path import btc15m_close_time_from_ticker, held_bid, read_heartbeats


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_exit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_exit_latest.md"
STATE_JSON = OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_exit_state.json"

POLICY = "repair_low_absd_quarter_else_half"
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECON_SHARE = 0.35
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3

RECHECK_VARIANTS = [
    {"name": "base_no_exit_overlay", "delay_seconds": None, "bid_floor": None, "max_drop": None},
    {"name": "delay60_bid60_drop10", "delay_seconds": 60, "bid_floor": 60, "max_drop": 10},
    {"name": "delay60_bid60_drop11", "delay_seconds": 60, "bid_floor": 60, "max_drop": 11},
    {"name": "delay60_bid65_drop10", "delay_seconds": 60, "bid_floor": 65, "max_drop": 10},
    {"name": "delay120_bid60_drop10", "delay_seconds": 120, "bid_floor": 60, "max_drop": 10},
]


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


def load_or_create_exit_state() -> dict[str, Any]:
    existing = load_json(STATE_JSON)
    if existing:
        return existing
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_size_shrink_delayed_recheck_exit",
        "parent_policy": POLICY,
        "note": "Freeze created after diagnostic delayed-recheck overlay discovery; post-birth rows are the only strict-forward evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "")


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def grouped_exit_rows(path: Path) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in load_json(path).get("rows") or []:
        if isinstance(row, dict) and market(row) and side(row):
            grouped[(market(row), side(row))].append(row)
    floor = datetime.min.replace(tzinfo=timezone.utc)
    for key in grouped:
        grouped[key].sort(key=lambda row: parse_ts(row.get("exit_ts") or row.get("entry_ts")) or floor)
    return grouped


def latest(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return rows[-1] if rows else None


def choose_exit_row(
    entry: dict[str, Any],
    book_rows: dict[tuple[str, str], list[dict[str, Any]]],
    reduce_rows: dict[tuple[str, str], list[dict[str, Any]]],
) -> dict[str, Any] | None:
    key = (market(entry), side(entry))
    candidates = [row for row in [latest(book_rows.get(key) or []), latest(reduce_rows.get(key) or [])] if row is not None]
    floor = datetime.min.replace(tzinfo=timezone.utc)
    candidates.sort(key=lambda row: parse_ts(row.get("exit_ts") or row.get("entry_ts")) or floor)
    return candidates[-1] if candidates else None


def path_points(row: dict[str, Any], heartbeats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    exit_ts = to_eastern_naive(parse_utc(row.get("exit_ts")))
    close_ts = to_eastern_naive(btc15m_close_time_from_ticker(market(row)))
    points = [
        {**hb, "held_bid": held_bid(hb, side(row))}
        for hb in heartbeats
        if hb["market"] == market(row)
        and exit_ts is not None
        and hb["ts"] >= exit_ts
        and (close_ts is None or hb["ts"] < close_ts)
    ]
    points.sort(key=lambda item: item["ts"])
    return points


def delayed_recheck(exit_row: dict[str, Any], points: list[dict[str, Any]], variant: dict[str, Any]) -> dict[str, Any]:
    if variant.get("delay_seconds") is None:
        return {
            "suppressed": False,
            "exit_bid": None,
            "recheck_bid": None,
            "min_window_bid": None,
            "window_drop_cents": None,
            "recheck_missing": False,
        }
    exit_ts = to_eastern_naive(parse_utc(exit_row.get("exit_ts")))
    if exit_ts is None or not points:
        return {
            "suppressed": False,
            "exit_bid": None,
            "recheck_bid": None,
            "min_window_bid": None,
            "window_drop_cents": None,
            "recheck_missing": True,
        }
    exit_bid = fnum(points[0].get("held_bid"), None)
    recheck_ts = exit_ts + timedelta(seconds=int(variant["delay_seconds"]))
    recheck = next((point for point in points if point["ts"] >= recheck_ts), None)
    window = [point for point in points if point["ts"] <= recheck_ts]
    recheck_bid = None if recheck is None else fnum(recheck.get("held_bid"), None)
    min_window_bid = min([fnum(point.get("held_bid")) for point in window], default=None)
    drop = None if min_window_bid is None or exit_bid is None else exit_bid - min_window_bid
    suppress = (
        recheck_bid is not None
        and recheck_bid >= float(variant["bid_floor"])
        and drop is not None
        and drop <= float(variant["max_drop"])
    )
    return {
        "suppressed": suppress,
        "exit_bid": exit_bid,
        "recheck_bid": recheck_bid,
        "min_window_bid": min_window_bid,
        "window_drop_cents": drop,
        "recheck_missing": recheck is None,
    }


def build_entries(freeze_ts: str) -> tuple[list[dict[str, Any]], set[tuple[str, str]], int]:
    rows, _, denominator_raw = entry_surfaces(freeze_ts)
    anchor_rows = selected(rows, ANCHOR_RULE)
    repair_rows = selected(rows, REPAIR_RULE)
    return repair_rows, {row_key(row) for row in anchor_rows}, int(denominator_raw or 0)


def source_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    counts = Counter(source(row) for row in rows)
    return (len(rows) - int(counts.get("approved_entry") or 0)) / len(rows)


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
            "exit_bid": None,
            "recheck_bid": None,
            "min_window_bid": None,
            "window_drop_cents": None,
            "recheck_missing": False,
        }
        if exit_row is not None and exit_row.get("exit_ts"):
            cur = exit_row.get("current_cents")
            held = exit_row.get("hold_cents") if exit_row.get("hold_cents") is not None else exit_row.get("candidate_cents")
            if cur is not None and held is not None:
                joined = True
                current = fnum(cur)
                hold = fnum(held)
                recheck = delayed_recheck(exit_row, path_points(exit_row, heartbeats), variant)
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
            "weighted_entry_hold_cents": weight * entry_hold,
            "weighted_current_exit_cents": weight * current,
            "weighted_candidate_cents": weight * candidate,
            "weighted_delta_vs_current_exit_cents": weight * (candidate - current),
            "weighted_delta_vs_entry_hold_cents": weight * (candidate - entry_hold),
            "exit_ts": None if exit_row is None else exit_row.get("exit_ts"),
            "exit_reason": None if exit_row is None else exit_row.get("exit_reason"),
            **recheck,
        })
    candidate_net = sum(row["weighted_candidate_cents"] for row in scored)
    current_net = sum(row["weighted_current_exit_cents"] for row in scored)
    entry_hold_net = sum(row["weighted_entry_hold_cents"] for row in scored)
    suppressed = [row for row in scored if row.get("suppressed")]
    coverage = 100.0 * len(entries) / denominator if denominator else 0.0
    recon = source_share(entries)
    blockers = []
    if len(entries) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if recon is not None and recon > MAX_RECON_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    if candidate_net <= 0:
        blockers.append("weighted_net_not_positive")
    if int(max(0.0, candidate_net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if candidate_net <= live_cents:
        blockers.append("does_not_beat_refreshed_live_baseline")
    if not strict_forward:
        blockers.extend(["diagnostic_prefreeze", "exit_overlay_not_independently_frozen"])
    return {
        "lane": lane_label,
        "strict_forward": strict_forward,
        "variant": variant,
        "entries": len(entries),
        "settled": len(entries),
        "wins": sum(1 for row in scored if row["weighted_candidate_cents"] > 0),
        "losses": sum(1 for row in scored if row["weighted_candidate_cents"] < 0),
        "coverage_pct": coverage,
        "source_counts": dict(Counter(source(row) for row in entries)),
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
        "full_loss_cushion": int(max(0.0, candidate_net) // 100.0),
        "blockers": blockers,
        "worst_rows": sorted(scored, key=lambda row: row["weighted_candidate_cents"])[:12],
        "scored_rows": scored,
    }


def evaluate_lane(
    lane_label: str,
    strict_forward: bool,
    entries: list[dict[str, Any]],
    anchor_keys: set[tuple[str, str]],
    denominator: int,
    book_rows: dict[tuple[str, str], list[dict[str, Any]]],
    reduce_rows: dict[tuple[str, str], list[dict[str, Any]]],
    heartbeats: list[dict[str, Any]],
    live_cents: float,
) -> dict[str, Any]:
    variants = [
        evaluate_variant(
            variant,
            entries,
            anchor_keys,
            denominator,
            book_rows,
            reduce_rows,
            heartbeats,
            live_cents,
            lane_label,
            strict_forward,
        )
        for variant in RECHECK_VARIANTS
    ]
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("candidate_net_cents") or -999999.0),
            -float(row.get("delta_vs_current_exit_cents") or -999999.0),
        )
    )
    return {
        "lane": lane_label,
        "strict_forward": strict_forward,
        "denominator": denominator,
        "entry_rows": len(entries),
        "variants": variants,
        "best": variants[0] if variants else {},
    }


def build_report() -> dict[str, Any]:
    feature_state = load_feature_gate_state()
    exit_state = load_or_create_exit_state()
    diagnostic_entries, diagnostic_anchor_keys, diagnostic_denominator = build_entries(str(feature_state["freeze_ts_utc"]))
    post_entries, post_anchor_keys, post_denominator = build_entries(str(exit_state["freeze_ts_utc"]))
    book_rows = grouped_exit_rows(BOOK_GAP_JSON)
    reduce_rows = grouped_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    live_cents = 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))
    diagnostic_lane = evaluate_lane(
        "diagnostic_prefreeze_context",
        False,
        diagnostic_entries,
        diagnostic_anchor_keys,
        diagnostic_denominator,
        book_rows,
        reduce_rows,
        heartbeats,
        live_cents,
    )
    post_lane = evaluate_lane(
        "post_delayed_recheck_overlay_birth",
        True,
        post_entries,
        post_anchor_keys,
        post_denominator,
        book_rows,
        reduce_rows,
        heartbeats,
        live_cents,
    )
    best = diagnostic_lane.get("best") or {}
    post_best = post_lane.get("best") or {}
    return {
        "generated_at_utc": utc_now_iso(),
        "policy": POLICY,
        "feature_gate_freeze_ts_utc": feature_state.get("freeze_ts_utc"),
        "state": exit_state,
        "live_baseline_cents": live_cents,
        "lanes": [diagnostic_lane, post_lane],
        "variants": diagnostic_lane.get("variants") or [],
        "interpretation": [
            "Research-only delayed-recheck exit overlay; no live bot changes or orders.",
            (
                f"Diagnostic best variant {((best.get('variant') or {}).get('name'))} has "
                f"net {best.get('candidate_net_cents')}c, delta vs current exits "
                f"{best.get('delta_vs_current_exit_cents')}c, W/L {best.get('wins')}/{best.get('losses')}, "
                f"suppressed {best.get('suppressed_rows')}, blockers {best.get('blockers')}."
            ) if best else "No variants scored.",
            (
                f"Post-overlay-birth best variant {((post_best.get('variant') or {}).get('name'))} has "
                f"{post_best.get('settled')} settled rows and net {post_best.get('candidate_net_cents')}c; "
                f"only this post-birth lane can become live-test evidence."
            ) if post_best else "No post-overlay-birth variants scored.",
            "This does not solve source quality; it only tests whether the current strict branch has an exit-policy repair path.",
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
        "# v28 Feature-Gate Size-Shrink Delayed-Recheck Exit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Policy: `{report.get('policy')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Overlay freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
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
            "| lane | strict forward | denominator | entries | best variant | W/L | coverage | source | candidate | delta live | blockers |",
            "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        best = lane.get("best") or {}
        variant = best.get("variant") or {}
        lines.append(
            f"| `{lane.get('lane')}` | {lane.get('strict_forward')} | {lane.get('denominator')} | "
            f"{lane.get('entry_rows')} | `{variant.get('name')}` | {best.get('wins')}/{best.get('losses')} | "
            f"{fmt(best.get('coverage_pct'))}% | {fmt(best.get('reconstructed_share'))} | "
            f"{fmt(best.get('candidate_net_cents'))} | {fmt(best.get('delta_vs_live_cents'))} | "
            f"{', '.join(best.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Diagnostic Variants",
            "",
            "| rank | variant | W/L | coverage | source | entry hold | current exit | candidate | delta current | delta live | joined | suppressed | H/H | cushion | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, item in enumerate(report.get("variants") or [], start=1):
        variant = item.get("variant") or {}
        lines.append(
            f"| {idx} | `{variant.get('name')}` | {item.get('wins')}/{item.get('losses')} | "
            f"{fmt(item.get('coverage_pct'))}% | {fmt(item.get('reconstructed_share'))} | "
            f"{fmt(item.get('entry_hold_net_cents'))} | {fmt(item.get('current_exit_net_cents'))} | "
            f"{fmt(item.get('candidate_net_cents'))} | {fmt(item.get('delta_vs_current_exit_cents'))} | "
            f"{fmt(item.get('delta_vs_live_cents'))} | {item.get('joined_exit_rows')} | "
            f"{item.get('suppressed_rows')} | {item.get('helpful_suppressed')}/{item.get('harmful_suppressed')} | "
            f"{item.get('full_loss_cushion')} | {', '.join(item.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Worst Rows For Best Variant",
            "",
            "| market | side | source | reason | current | hold | candidate | weight | weighted | exit bid | recheck bid | drop |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    best_rows = ((report.get("variants") or [{}])[0].get("worst_rows") or []) if report.get("variants") else []
    for row in best_rows:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('current_exit_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('candidate_cents'))} | {fmt(row.get('weight'))} | "
            f"{fmt(row.get('weighted_candidate_cents'))} | {fmt(row.get('exit_bid'))} | "
            f"{fmt(row.get('recheck_bid'))} | {fmt(row.get('window_drop_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
