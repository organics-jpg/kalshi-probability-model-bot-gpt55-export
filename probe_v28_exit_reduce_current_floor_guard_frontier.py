"""Current-exit floor guard frontier for v28 reduce-depth exit suppression.

Research-only; no live bot changes or orders.

The value/reduce-depth suppressed-loser audit found a repeated p75
probability-reduce false hold that was already negative at exit. This probe
tests whether an observable current-exit floor can keep useful p75/p77
reduce-depth recovery while avoiding already-negative false holds. It does not
freeze or change any candidate.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import fair_drawdown, hold_book_gap, p_hold
from probe_v28_exit_policy_candidates import (
    current_exit,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    is_value_over_hold,
    side_won,
)
from probe_v28_frozen_exit_reduce_depth_gate import entry_depth
from probe_v28_frozen_exit_value_reduce_depth_composite import (
    BOOK_GAP_STATE_JSON,
    REDUCE_STATE_JSON,
    STATE_JSON,
    load_json,
    rows_after,
    suppress_value_v2,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_reduce_current_floor_guard_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_current_floor_guard_frontier_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED_DECISIONS = 30
MIN_FULL_LOSS_CUSHION = 3

VARIANTS = {
    "v2_reduce_p75_depth384": {"p_min": 0.75, "depth_max": 384.0, "current_floor": None},
    "v2_reduce_p75_depth384_current_ge_0": {"p_min": 0.75, "depth_max": 384.0, "current_floor": 0.0},
    "v2_reduce_p75_depth384_current_ge_minus10": {"p_min": 0.75, "depth_max": 384.0, "current_floor": -10.0},
    "v2_reduce_p78_depth384": {"p_min": 0.78, "depth_max": 384.0, "current_floor": None},
    "v2_reduce_p77_depth384_current_ge_0": {"p_min": 0.77, "depth_max": 384.0, "current_floor": 0.0},
    "v2_reduce_p79_depth384": {"p_min": 0.79, "depth_max": 384.0, "current_floor": None},
    "v2_reduce_p795_depth384": {"p_min": 0.795, "depth_max": 384.0, "current_floor": None},
    "v2_reduce_p80_depth384": {"p_min": 0.80, "depth_max": 384.0, "current_floor": None},
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def reduce_suppresses(row: dict[str, Any], variant: dict[str, Any]) -> bool:
    if not is_probability_reduce(row):
        return False
    p = p_hold(row)
    depth = entry_depth(row)
    cur = current_exit(row)
    if p is None or depth is None or cur is None:
        return False
    current_floor = variant.get("current_floor")
    if current_floor is not None and float(cur) < float(current_floor):
        return False
    return p >= float(variant["p_min"]) and depth <= float(variant["depth_max"])


def should_suppress(row: dict[str, Any], variant: dict[str, Any]) -> bool:
    if is_value_over_hold(row):
        return suppress_value_v2(row)
    return reduce_suppresses(row, variant)


def summarize(rows: list[dict[str, Any]], variant: dict[str, Any]) -> dict[str, Any]:
    current_vals = []
    candidate_vals = []
    suppressed = []
    for row in rows:
        cur = current_exit(row)
        hold = hold_to_settlement(row)
        if cur is None or hold is None:
            continue
        cand = hold if should_suppress(row, variant) else cur
        current_vals.append(float(cur))
        candidate_vals.append(float(cand))
        if should_suppress(row, variant):
            suppressed.append(row)
    current_net = sum(current_vals)
    candidate_net = sum(candidate_vals)
    suppressed_delta = [
        fnum(hold_to_settlement(row)) - fnum(current_exit(row))
        for row in suppressed
    ]
    suppressed_winners = [row for row in suppressed if side_won(row) is True]
    suppressed_losers = [row for row in suppressed if side_won(row) is False]
    value_suppressed = [row for row in suppressed if is_value_over_hold(row)]
    reduce_suppressed = [row for row in suppressed if is_probability_reduce(row)]
    return {
        "settled": len(candidate_vals),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_current_cents": candidate_net - current_net,
        "current_wins": sum(1 for value in current_vals if value >= 0.0),
        "current_losses": sum(1 for value in current_vals if value < 0.0),
        "candidate_wins": sum(1 for value in candidate_vals if value >= 0.0),
        "candidate_losses": sum(1 for value in candidate_vals if value < 0.0),
        "suppressed_exits": len(suppressed),
        "value_suppressed": len(value_suppressed),
        "reduce_suppressed": len(reduce_suppressed),
        "suppressed_winners": len(suppressed_winners),
        "suppressed_losers": len(suppressed_losers),
        "winner_clip_recovered_cents": sum(delta for delta in suppressed_delta if delta > 0.0),
        "loss_control_cost_cents": sum(delta for delta in suppressed_delta if delta < 0.0),
        "full_loss_cushion_estimate": int(candidate_net // 100.0) if candidate_net > 0 else 0,
    }


def blockers(summary: dict[str, Any]) -> list[str]:
    out = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        out.append("settled_lt_30")
    if float(summary.get("delta_vs_current_cents") or 0.0) <= 0.0:
        out.append("delta_not_positive")
    if float(summary.get("candidate_net_cents") or 0.0) <= 0.0:
        out.append("net_not_positive")
    if int(summary.get("suppressed_exits") or 0) < MIN_SUPPRESSED_DECISIONS:
        out.append("suppressed_decisions_lt_30")
    if int(summary.get("suppressed_losers") or 0) > 0:
        out.append("suppressed_losers_present")
    if float(summary.get("loss_control_cost_cents") or 0.0) < 0.0:
        out.append("suppressed_loss_control_cost_negative")
    if int(summary.get("full_loss_cushion_estimate") or 0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def compact(row: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "exit_reason": exit_reason(row),
        "entry_depth": entry_depth(row),
        "p_hold": p_hold(row),
        "hold_book_gap": hold_book_gap(row),
        "fair_drawdown_cents": fair_drawdown(row),
        "current_cents": cur,
        "hold_cents": hold,
        "delta_cents": None if cur is None or hold is None else float(hold) - float(cur),
        "suppressed": should_suppress(row, variant),
        "side_won": side_won(row),
    }


def evaluate_lane(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    variants = []
    for name, variant in VARIANTS.items():
        summary = summarize(rows, variant)
        detail = [compact(row, variant) for row in rows if should_suppress(row, variant)]
        variants.append(
            {
                "variant": name,
                "params": variant,
                "summary": summary,
                "blockers": blockers(summary),
                "suppressed_rows": detail,
                "suppressed_loser_rows": [row for row in detail if row.get("side_won") is False],
            }
        )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            int((row.get("summary") or {}).get("suppressed_losers") or 0),
            -float((row.get("summary") or {}).get("delta_vs_current_cents") or -999999.0),
        )
    )
    return {"lane": label, "variants": variants}


def diagnostic_freeze_ts() -> str:
    state = load_json(STATE_JSON)
    reduce_state = load_json(REDUCE_STATE_JSON)
    book_gap_state = load_json(BOOK_GAP_STATE_JSON)
    return min(
        str(reduce_state.get("freeze_ts_utc") or state.get("freeze_ts_utc") or utc_now_iso()),
        str(book_gap_state.get("freeze_ts_utc") or state.get("freeze_ts_utc") or utc_now_iso()),
    )


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    post_freeze = str(state.get("freeze_ts_utc") or utc_now_iso())
    diagnostic_freeze = diagnostic_freeze_ts()
    lanes = [
        evaluate_lane("diagnostic_from_exit_freezes", rows_after(diagnostic_freeze)),
        evaluate_lane("post_composite_birth", rows_after(post_freeze)),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "source_composite_state": str(STATE_JSON),
        "diagnostic_freeze_ts_utc": diagnostic_freeze,
        "post_composite_freeze_ts_utc": post_freeze,
        "variants": VARIANTS,
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Research-only frontier; this does not freeze a child or alter any live/watch logic.",
        "A current-exit floor is observable at the exit decision and tests whether already-negative reduce exits should be excluded from hold suppression.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('variant')} settled {summary.get('settled')}, "
            f"candidate {summary.get('candidate_net_cents')}c, delta {summary.get('delta_vs_current_cents')}c, "
            f"suppressed {summary.get('suppressed_exits')} value/reduce {summary.get('value_suppressed')}/{summary.get('reduce_suppressed')}, "
            f"suppressed W/L {summary.get('suppressed_winners')}/{summary.get('suppressed_losers')}, "
            f"blockers {best.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Reduce Current-Floor Guard Frontier",
        "",
        "Research-only. No live bot changes, no orders, no new frozen rule.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Diagnostic freeze UTC: `{report.get('diagnostic_freeze_ts_utc')}`",
        f"- Post-composite freeze UTC: `{report.get('post_composite_freeze_ts_utc')}`",
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
                "| rank | variant | settled | W/L | current c | candidate c | delta c | suppressed | value/reduce | suppressed W/L | recovery c | loss cost c | cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(lane.get("variants") or [], start=1):
            summary = row.get("summary") or {}
            lines.append(
                f"| {idx} | `{row.get('variant')}` | {summary.get('settled')} | "
                f"{summary.get('candidate_wins')}/{summary.get('candidate_losses')} | "
                f"{fmt(summary.get('current_net_cents'))} | {fmt(summary.get('candidate_net_cents'))} | "
                f"{fmt(summary.get('delta_vs_current_cents'))} | {summary.get('suppressed_exits')} | "
                f"{summary.get('value_suppressed')}/{summary.get('reduce_suppressed')} | "
                f"{summary.get('suppressed_winners')}/{summary.get('suppressed_losers')} | "
                f"{fmt(summary.get('winner_clip_recovered_cents'))} | {fmt(summary.get('loss_control_cost_cents'))} | "
                f"{summary.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
        loser_rows = [
            loser
            for variant in lane.get("variants") or []
            for loser in variant.get("suppressed_loser_rows") or []
        ]
        if loser_rows:
            lines.extend(["", "### Suppressed Loser Rows", ""])
            lines.append("| variant | market | side | reason | current | hold | delta | p_hold | depth | gap | drawdown |")
            lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|")
            seen = set()
            for variant in lane.get("variants") or []:
                for loser in variant.get("suppressed_loser_rows") or []:
                    key = (variant.get("variant"), loser.get("market"), loser.get("side"))
                    if key in seen:
                        continue
                    seen.add(key)
                    lines.append(
                        f"| `{variant.get('variant')}` | `{loser.get('market')}` | `{loser.get('side')}` | `{loser.get('exit_reason')}` | "
                        f"{fmt(loser.get('current_cents'))} | {fmt(loser.get('hold_cents'))} | {fmt(loser.get('delta_cents'))} | "
                        f"{fmt(loser.get('p_hold'))} | {fmt(loser.get('entry_depth'))} | {fmt(loser.get('hold_book_gap'))} | "
                        f"{fmt(loser.get('fair_drawdown_cents'))} |"
                    )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
