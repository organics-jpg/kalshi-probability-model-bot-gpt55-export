"""Middle-distance observable core watch for v28 feature-gate rows.

Research-only; no live bot changes or orders.

The size-shrink source slice showed the low-abs-distance repair tail is the
fragile part of the near-gate branch, while the middle-distance bucket looked
clean and strongly positive. This probe freezes that observable mechanism as a
watch lane so future rows can test whether it is real or just a small-window
artifact.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    STATE_JSON as FEATURE_STATE_JSON,
    as_float,
    best_per_market,
    load_json,
    market,
    net,
    recross,
    reconstructed_share,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_feature_gate_middle_distance_core_watch_state.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_middle_distance_core_watch_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_middle_distance_core_watch_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
TARGET_COVERAGE_MIN = 75.0
MARKET_INTERVAL_MINUTES = 15

RULES = {
    "middle_core_raw03_recross50_abs075_125_ask35": {
        "raw_min": 0.03,
        "recross_max": 0.50,
        "abs_min": 0.75,
        "abs_max": 1.25,
        "ask_min": 0.35,
    },
    "middle_core_raw05_recross60_abs075_125_ask35": {
        "raw_min": 0.05,
        "recross_max": 0.60,
        "abs_min": 0.75,
        "abs_max": 1.25,
        "ask_min": 0.35,
    },
    "abs_floor_raw03_recross50_abs075_ask35": {
        "raw_min": 0.03,
        "recross_max": 0.50,
        "abs_min": 0.75,
        "abs_max": None,
        "ask_min": 0.35,
    },
    "abs_floor_raw05_recross60_abs075_ask35": {
        "raw_min": 0.05,
        "recross_max": 0.60,
        "abs_min": 0.75,
        "abs_max": None,
        "ask_min": 0.35,
    },
    "upper_abs_tail_raw03_recross50_abs125_ask35": {
        "raw_min": 0.03,
        "recross_max": 0.50,
        "abs_min": 1.25,
        "abs_max": None,
        "ask_min": 0.35,
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def possible_market_windows_since(freeze_ts: str) -> int:
    parsed = parse_ts(freeze_ts)
    if parsed is None:
        return 0
    elapsed = max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds())
    return int(elapsed // (MARKET_INTERVAL_MINUTES * 60))


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_middle_distance_observable_core",
        "physics": (
            "Low-abs-distance repair rows behave like boundary-noise filler. "
            "The abs 0.75-1.25 pocket has enough distance from the strike to avoid "
            "the worst recross noise while avoiding far-tail overpayment."
        ),
        "rules": RULES,
        "promotion_note": (
            "This is a frozen watch lane only. It cannot be live-tested until its own "
            "post-freeze rows clear sample, source, net, cushion, and controlled live-test gates."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    ask_cents = as_float(row.get("ask_cents"))
    return ask_cents / 100.0 if ask_cents is not None else None


def abs_d(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("abs_d_sigma"))
    return abs(value) if value is not None else None


def side_won(row: dict[str, Any]) -> Any:
    return row.get("side_won")


def live_net_cents() -> float:
    if not LIVE_SUMMARY_JSON.exists():
        return 0.0
    payload = load_json(LIVE_SUMMARY_JSON)
    return 100.0 * fnum(payload.get("net_pnl_total_dollars"))


def passes_rule(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    row_abs = abs_d(row)
    ask = ask_prob(row)
    if edge is None or row_recross is None or row_abs is None or ask is None:
        return False
    if edge < rule["raw_min"] or row_recross > rule["recross_max"]:
        return False
    if row_abs < rule["abs_min"]:
        return False
    abs_max = rule.get("abs_max")
    if abs_max is not None and row_abs >= float(abs_max):
        return False
    if ask < rule["ask_min"]:
        return False
    return True


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "side_won": side_won(row),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": abs_d(row),
        "ask_prob": ask_prob(row),
        "seconds_to_close": row.get("seconds_to_close"),
        "eligible_depth": row.get("eligible_depth"),
    }


def blockers(summary: dict[str, Any], share: float | None, live_net: float, broad_required: bool) -> list[str]:
    settled = int(fnum(summary.get("settled")))
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = fnum(summary.get("net_cents"))
    out: list[str] = []
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if broad_required and (coverage is None or coverage < TARGET_COVERAGE_MIN):
        out.append("coverage_too_low")
    if net_cents <= 0:
        out.append("net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if math.floor(max(0.0, net_cents) / 100.0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    if net_cents <= live_net:
        out.append("does_not_beat_refreshed_live_baseline")
    return out


def summarize_rule(
    name: str,
    rows: list[dict[str, Any]],
    denominator: int,
    live_net: float,
    broad_required: bool,
) -> dict[str, Any]:
    selected = best_per_market([row for row in rows if passes_rule(row, RULES[name])])
    selected_summary = summarize(selected, denominator)
    counts = dict(Counter(source(row) for row in selected))
    share = reconstructed_share(counts)
    row_nets = [net(row) for row in selected if side_won(row) is not None]
    top_win = max(row_nets) if row_nets else 0.0
    result = {
        "rule": name,
        "rule_params": RULES[name],
        "future_denominator": denominator,
        "summary": selected_summary,
        "source_counts": counts,
        "reconstructed_share": share,
        "full_loss_cushion_estimate": math.floor(max(0.0, fnum(selected_summary.get("net_cents"))) / 100.0),
        "delta_vs_live_cents": fnum(selected_summary.get("net_cents")) - live_net,
        "top_win_cents": top_win,
        "net_without_top_win_cents": fnum(selected_summary.get("net_cents")) - top_win,
        "rows": [compact_row(row) for row in sorted(selected, key=lambda item: net(item))],
    }
    result["blockers"] = blockers(selected_summary, share, live_net, broad_required)
    result["live_ready"] = not result["blockers"]
    return result


def evaluate_lane(
    label: str,
    rows: list[dict[str, Any]],
    denominator: int,
    live_net: float,
    broad_required: bool,
) -> dict[str, Any]:
    evaluated = [
        summarize_rule(name, rows, int(denominator or 0), live_net, broad_required)
        for name in RULES
    ]
    evaluated.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -fnum((row.get("summary") or {}).get("net_cents")),
            -fnum((row.get("summary") or {}).get("coverage_pct")),
            row.get("rule"),
        )
    )
    return {
        "lane": label,
        "future_denominator": int(denominator or 0),
        "broad_required": broad_required,
        "rules": evaluated,
    }


def presample_rule(name: str) -> dict[str, Any]:
    return {
        "rule": name,
        "rule_params": RULES[name],
        "future_denominator": 0,
        "summary": {
            "entries": 0,
            "settled": 0,
            "wins": 0,
            "losses": 0,
            "coverage_pct": 0.0,
            "net_cents": 0.0,
        },
        "source_counts": {},
        "reconstructed_share": None,
        "full_loss_cushion_estimate": 0,
        "delta_vs_live_cents": 0.0,
        "top_win_cents": 0.0,
        "net_without_top_win_cents": 0.0,
        "rows": [],
        "blockers": ["own_freeze_presample_window_lt_30", "settled_lt_30"],
        "live_ready": False,
    }


def presample_lane(label: str) -> dict[str, Any]:
    return {
        "lane": label,
        "future_denominator": 0,
        "broad_required": False,
        "rules": [presample_rule(name) for name in RULES],
    }


def interpretation(lanes: list[dict[str, Any]], live_net: float) -> list[str]:
    notes = [
        "Research-only middle-distance core watch; no live bot changes or orders.",
        f"Live baseline for delta math is {live_net:.0f}c.",
    ]
    for lane in lanes:
        best = (lane.get("rules") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best rule {best.get('rule')} has "
            f"{summary.get('settled')} settled, W/L {summary.get('wins')}/{summary.get('losses')}, "
            f"{summary.get('coverage_pct')}% coverage, {summary.get('net_cents')}c net, "
            f"source share {best.get('reconstructed_share')}, blockers {best.get('blockers')}."
        )
    return notes


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    feature_state = load_json(FEATURE_STATE_JSON)
    feature_freeze = str(feature_state.get("freeze_ts_utc") or state["freeze_ts_utc"])
    watch_freeze = str(state["freeze_ts_utc"])
    live_net = live_net_cents()
    possible_windows = possible_market_windows_since(watch_freeze)
    if possible_windows < MIN_SETTLED:
        lanes = [
            presample_lane("post_middle_core_freeze_entry"),
            presample_lane("post_middle_core_freeze_bridge"),
        ]
        return {
            "generated_at_utc": utc_now_iso(),
            "state": state,
            "feature_gate_freeze_ts_utc": feature_freeze,
            "live_baseline_cents": live_net,
            "possible_market_windows_since_watch_freeze": possible_windows,
            "pre_sample_short_circuit": True,
            "lanes": lanes,
            "interpretation": [
                "Research-only middle-distance core watch; no live bot changes or orders.",
                f"Own-freeze watch has only {possible_windows} possible 15m windows since birth, so heavy replay was skipped.",
                "This cannot be live-ready until at least 30 post-freeze market windows exist and then clear sample/source/PnL/cushion/live-baseline gates.",
            ],
        }
    feature_entry_rows, _, feature_entry_denominator = entry_surfaces(feature_freeze)
    feature_bridge_rows, _, feature_bridge_denominator = bridge_surfaces(feature_freeze)
    watch_entry_rows, _, watch_entry_denominator = entry_surfaces(watch_freeze)
    watch_bridge_rows, _, watch_bridge_denominator = bridge_surfaces(watch_freeze)
    lanes = [
        evaluate_lane(
            "diagnostic_feature_window_entry",
            feature_entry_rows,
            int(feature_entry_denominator or 0),
            live_net,
            broad_required=False,
        ),
        evaluate_lane(
            "diagnostic_feature_window_bridge",
            feature_bridge_rows,
            int(feature_bridge_denominator or 0),
            live_net,
            broad_required=False,
        ),
        evaluate_lane(
            "post_middle_core_freeze_entry",
            watch_entry_rows,
            int(watch_entry_denominator or 0),
            live_net,
            broad_required=False,
        ),
        evaluate_lane(
            "post_middle_core_freeze_bridge",
            watch_bridge_rows,
            int(watch_bridge_denominator or 0),
            live_net,
            broad_required=False,
        ),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "feature_gate_freeze_ts_utc": feature_freeze,
        "live_baseline_cents": live_net,
        "possible_market_windows_since_watch_freeze": possible_windows,
        "pre_sample_short_circuit": False,
        "lanes": lanes,
        "interpretation": interpretation(lanes, live_net),
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Middle-Distance Core Watch",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Watch freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Feature-gate parent freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        f"- Possible 15m windows since watch freeze: `{report.get('possible_market_windows_since_watch_freeze')}`",
        f"- Pre-sample short-circuit: `{report.get('pre_sample_short_circuit')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                f"- Broad coverage required in this report: `{lane.get('broad_required')}`",
                "",
                "| rank | rule | entries | settled | W/L | coverage | net c | delta live c | source share | cushion | no-top-win c | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(lane.get("rules") or [], 1):
            summary = row.get("summary") or {}
            blockers_text = ", ".join(row.get("blockers") or []) or "none"
            lines.append(
                f"| {idx} | `{row.get('rule')}` | {summary.get('entries')} | {summary.get('settled')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))}% | "
                f"{fmt(summary.get('net_cents'))} | {fmt(row.get('delta_vs_live_cents'))} | "
                f"{fmt(row.get('reconstructed_share'))} | {row.get('full_loss_cushion_estimate')} | "
                f"{fmt(row.get('net_without_top_win_cents'))} | {blockers_text} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
