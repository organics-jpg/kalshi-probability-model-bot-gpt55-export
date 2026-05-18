"""Opportunity denominator for frozen value/reduce-depth composite exits.

Research-only; no live bot changes or orders.

The composite watch combines two different physical exit mechanisms:
value-over-hold clipping and probability-reduce turbulence. This report
explains post-freeze opportunity availability without changing the frozen rule.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import exit_bid_prob, fair_drawdown, hold_book_gap, p_hold
from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    is_value_over_hold,
    side_won,
)
from probe_v28_frozen_exit_reduce_depth_gate import entry_depth
from probe_v28_frozen_exit_value_reduce_depth_composite import (
    RULES,
    STATE_JSON,
    load_json,
    parse_ts,
    should_suppress,
    suppress_value_only_p75,
    suppress_value_v2,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_value_reduce_depth_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_exit_value_reduce_depth_opportunity_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED_DECISIONS = 30
MIN_FULL_LOSS_CUSHION_CENTS = 300.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def future_rows(freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows: list[dict[str, Any]] = []
    for row in build_rows():
        exit_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and exit_dt is not None and exit_dt < freeze_dt:
            continue
        rows.append(row)
    return rows


def reduce_gate_passes(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    if not is_probability_reduce(row):
        return False
    hold_prob = p_hold(row)
    depth = entry_depth(row)
    return (
        hold_prob is not None
        and depth is not None
        and hold_prob >= float(rule.get("reduce_p_hold_min") or 0.0)
        and depth <= float(rule.get("reduce_entry_depth_max") or 0.0)
    )


def fail_reasons(row: dict[str, Any], rule: dict[str, Any]) -> list[str]:
    if should_suppress(row, rule):
        return []
    reason = exit_reason(row)
    if is_value_over_hold(row):
        reasons: list[str] = []
        if rule.get("value_mode") == "v2":
            gap = hold_book_gap(row)
            hold_prob = p_hold(row)
            drawdown = fair_drawdown(row)
            if gap is None:
                reasons.append("value_gap_missing")
            elif gap < 0.0:
                reasons.append("value_gap_negative")
            if hold_prob is None:
                reasons.append("value_p_hold_missing")
            elif hold_prob < 0.85:
                reasons.append("value_p_hold_below_85")
            if drawdown is None:
                reasons.append("value_fair_drawdown_missing")
            elif drawdown < -5.0:
                reasons.append("value_fair_drawdown_too_deep")
            return reasons or ["value_v2_not_suppressed"]
        if rule.get("value_mode") == "value_only_p75":
            gap = hold_book_gap(row)
            hold_prob = p_hold(row)
            if gap is None:
                reasons.append("value_gap_missing")
            elif gap < 0.15:
                reasons.append("value_gap_below_15")
            if hold_prob is None:
                reasons.append("value_p_hold_missing")
            elif hold_prob < 0.75:
                reasons.append("value_p_hold_below_75")
            return reasons or ["value_p75_not_suppressed"]
    if is_probability_reduce(row):
        reasons = []
        hold_prob = p_hold(row)
        depth = entry_depth(row)
        p_floor = float(rule.get("reduce_p_hold_min") or 0.0)
        depth_ceiling = float(rule.get("reduce_entry_depth_max") or 0.0)
        if hold_prob is None:
            reasons.append("reduce_p_hold_missing")
        elif hold_prob < p_floor:
            reasons.append("reduce_p_hold_below_floor")
        if depth is None:
            reasons.append("reduce_entry_depth_missing")
        elif depth > depth_ceiling:
            reasons.append("reduce_entry_depth_above_ceiling")
        return reasons or ["reduce_depth_not_suppressed"]
    if reason == "mushroom_v28_probability_collapse_full":
        return ["collapse_kept_by_composite_rule"]
    return ["not_value_or_reduce_exit"]


def compact(row: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": exit_reason(row),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "entry_depth": entry_depth(row),
        "p_hold": p_hold(row),
        "exit_bid_prob": exit_bid_prob(row),
        "hold_book_gap": hold_book_gap(row),
        "fair_drawdown_cents": fair_drawdown(row),
        "current_cents": cur,
        "hold_cents": hold,
        "delta_if_suppressed_cents": None if cur is None or hold is None else float(hold) - float(cur),
        "would_suppress": should_suppress(row, rule),
        "fail_reasons": fail_reasons(row, rule),
    }


def score_rule(rows: list[dict[str, Any]], rule_name: str, rule: dict[str, Any]) -> dict[str, Any]:
    value_rows = [row for row in rows if is_value_over_hold(row)]
    reduce_rows = [row for row in rows if is_probability_reduce(row)]
    would_suppress = [row for row in rows if should_suppress(row, rule)]
    value_suppress = [row for row in value_rows if should_suppress(row, rule)]
    reduce_suppress = [row for row in reduce_rows if reduce_gate_passes(row, rule)]
    deltas = [
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in would_suppress
    ]
    current_vals = [float(current_exit(row) or 0.0) for row in rows if current_exit(row) is not None]
    candidate_net = sum(current_vals) + sum(deltas)
    reason_counts = Counter()
    for row in rows:
        for reason in fail_reasons(row, rule):
            reason_counts[reason] += 1
    rows_needed = max(0, MIN_SETTLED - len(current_vals))
    suppressions_needed = max(0, MIN_SUPPRESSED_DECISIONS - len(would_suppress))
    cushion_needed = max(0.0, MIN_FULL_LOSS_CUSHION_CENTS - candidate_net)
    return {
        "rule": rule_name,
        "total_rows": len(rows),
        "settled": len(current_vals),
        "value_over_hold_rows": len(value_rows),
        "probability_reduce_rows": len(reduce_rows),
        "value_v2_candidate_rows": sum(1 for row in value_rows if suppress_value_v2(row)),
        "value_p75_candidate_rows": sum(1 for row in value_rows if suppress_value_only_p75(row)),
        "reduce_depth_candidate_rows": len(reduce_suppress),
        "would_suppress_rows": len(would_suppress),
        "would_suppress_value_rows": len(value_suppress),
        "would_suppress_reduce_rows": len(reduce_suppress),
        "would_suppress_winners": sum(1 for row in would_suppress if side_won(row) is True),
        "would_suppress_losers": sum(1 for row in would_suppress if side_won(row) is False),
        "would_suppress_delta_cents": sum(deltas),
        "candidate_net_cents": candidate_net,
        "rows_needed": rows_needed,
        "suppressed_needed": suppressions_needed,
        "net_cents_needed_for_cushion3": cushion_needed,
        "fail_reason_counts": dict(sorted(reason_counts.items())),
        "would_suppress_examples": [compact(row, rule) for row in would_suppress[:12]],
        "near_miss_examples": [
            compact(row, rule)
            for row in rows
            if (is_value_over_hold(row) or is_probability_reduce(row)) and not should_suppress(row, rule)
        ][:12],
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or utc_now_iso())
    primary_rule = str(state.get("candidate") or "value_v2_reduce_depth384")
    rows = future_rows(freeze_ts)
    rules = [score_rule(rows, name, rule) for name, rule in RULES.items()]
    rules.sort(
        key=lambda row: (
            -float(row.get("would_suppress_delta_cents") or 0.0),
            -int(row.get("would_suppress_rows") or 0),
            str(row.get("rule") or ""),
        )
    )
    primary = next((row for row in rules if row.get("rule") == primary_rule), rules[0] if rules else {})
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "primary_rule": primary_rule,
        "primary": primary,
        "rules": rules,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    primary = report.get("primary") or {}
    notes = [
        "This report explains opportunity availability only; it does not change the frozen value/reduce-depth composite.",
        (
            f"Primary {report.get('primary_rule')} has post-freeze rows {primary.get('total_rows')}, "
            f"value exits {primary.get('value_over_hold_rows')}, reduce exits {primary.get('probability_reduce_rows')}, "
            f"would-suppress rows {primary.get('would_suppress_rows')} "
            f"({primary.get('would_suppress_value_rows')}/{primary.get('would_suppress_reduce_rows')} value/reduce), "
            f"and delta {primary.get('would_suppress_delta_cents')}c."
        ),
        (
            f"Promotion runway still needs {primary.get('rows_needed')} settled rows, "
            f"{primary.get('suppressed_needed')} suppressed decisions, and "
            f"{primary.get('net_cents_needed_for_cushion3')}c for a three-full-loss cushion."
        ),
        f"Fail reasons are {primary.get('fail_reason_counts')}.",
    ]
    if int(primary.get("total_rows") or 0) == 0:
        notes.append("No post-freeze rows have reached the composite denominator yet.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Value + Reduce-Depth Opportunity Denominator",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Primary rule: `{report.get('primary_rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Rules",
        "",
        "| rule | rows | value exits | reduce exits | would suppress | value/reduce | delta c | net c | rows needed | suppressions needed | cushion c needed | fail reasons |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rules") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('total_rows')} | {row.get('value_over_hold_rows')} | "
            f"{row.get('probability_reduce_rows')} | {row.get('would_suppress_rows')} | "
            f"{row.get('would_suppress_value_rows')}/{row.get('would_suppress_reduce_rows')} | "
            f"{fmt(row.get('would_suppress_delta_cents'))} | {fmt(row.get('candidate_net_cents'))} | "
            f"{row.get('rows_needed')} | {row.get('suppressed_needed')} | "
            f"{fmt(row.get('net_cents_needed_for_cushion3'))} | {row.get('fail_reason_counts')} |"
        )
    lines.extend([
        "",
        "## Near Misses",
        "",
        "| market | side | result | reason | entry | exit | depth | p_hold | bid | gap | drawdown | current c | hold c | delta if suppressed | fail reasons |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in (report.get("primary") or {}).get("near_miss_examples") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('entry_depth'))} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('exit_bid_prob'))} | {fmt(row.get('hold_book_gap'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('delta_if_suppressed_cents'))} | {', '.join(row.get('fail_reasons') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
