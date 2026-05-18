"""Opportunity denominator for frozen value-only book-gap exit suppression.

Research-only; no live bot changes or orders.

The value-only book-gap watch intentionally leaves probability-reduce exits
unchanged. This report separates "no post-freeze exits yet" from
"value-over-hold exits occurred but p_hold/book-gap support did not pass."
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import (
    exit_bid_prob,
    exit_reason,
    hold_book_gap,
    is_collapse,
    is_soft_exit,
    p_hold,
)
from probe_v28_exit_policy_candidates import build_rows, current_exit, hold_to_settlement
from probe_v28_frozen_exit_book_gap_value_only import STATE_JSON, VARIANTS, load_json, parse_ts


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_book_gap_value_only_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_exit_book_gap_value_only_opportunity_latest.md"


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


def is_value_over_hold(row: dict[str, Any]) -> bool:
    return exit_reason(row) == "mushroom_v28_exit_value_over_hold"


def is_probability_reduce(row: dict[str, Any]) -> bool:
    return exit_reason(row) == "mushroom_v28_probability_reduce"


def value_only_suppresses(row: dict[str, Any], variant: dict[str, Any]) -> bool:
    if exit_reason(row) not in variant.get("exit_reasons", set()):
        return False
    gap = hold_book_gap(row)
    hold_prob = p_hold(row)
    gap_floor = as_float(variant.get("gap_floor"))
    p_floor = as_float(variant.get("p_hold_floor"))
    gap_pass = gap_floor is not None and gap is not None and gap >= gap_floor
    p_pass = p_floor is not None and hold_prob is not None and hold_prob >= p_floor
    return gap_pass or p_pass


def fail_reasons(row: dict[str, Any], variant: dict[str, Any]) -> list[str]:
    if value_only_suppresses(row, variant):
        return []
    if is_probability_reduce(row):
        return ["probability_reduce_kept_by_value_only_rule"]
    if is_collapse(row):
        return ["collapse_kept_by_value_only_rule"]
    if not is_value_over_hold(row):
        return ["not_value_over_hold_exit"]

    reasons: list[str] = []
    gap = hold_book_gap(row)
    hold_prob = p_hold(row)
    gap_floor = as_float(variant.get("gap_floor"))
    p_floor = as_float(variant.get("p_hold_floor"))
    if gap_floor is not None:
        if gap is None:
            reasons.append("value_gap_missing")
        elif gap < gap_floor:
            reasons.append("value_gap_below_floor")
    if p_floor is not None:
        if hold_prob is None:
            reasons.append("value_p_hold_missing")
        elif hold_prob < p_floor:
            reasons.append("value_p_hold_below_floor")
    return reasons or ["value_over_hold_not_suppressed"]


def compact(row: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
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
        "p_hold": p_hold(row),
        "exit_bid_prob": exit_bid_prob(row),
        "hold_book_gap": hold_book_gap(row),
        "current_cents": cur,
        "hold_cents": hold,
        "delta_if_suppressed_cents": None if cur is None or hold is None else float(hold) - float(cur),
        "would_suppress": value_only_suppresses(row, variant),
        "fail_reasons": fail_reasons(row, variant),
    }


def side_won(row: dict[str, Any]) -> bool:
    return str(row.get("side") or "").lower() == str(row.get("result") or "").lower()


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or utc_now_iso())
    candidate = str(state.get("candidate") or "value_only_gap15_or_p75")
    variant = VARIANTS.get(candidate) or VARIANTS["value_only_gap15_or_p75"]
    rows = future_rows(freeze_ts)
    value_rows = [row for row in rows if is_value_over_hold(row)]
    reduce_rows = [row for row in rows if is_probability_reduce(row)]
    collapse_rows = [row for row in rows if is_collapse(row)]
    soft_rows = [row for row in rows if is_soft_exit(row)]
    would_suppress = [row for row in rows if value_only_suppresses(row, variant)]
    reason_counts = Counter()
    for row in rows:
        for reason in fail_reasons(row, variant):
            reason_counts[reason] += 1
    deltas = [
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in would_suppress
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "candidate": candidate,
        "rule": {
            "exit_reasons": sorted(variant.get("exit_reasons") or []),
            "gap_floor": variant.get("gap_floor"),
            "p_hold_floor": variant.get("p_hold_floor"),
        },
        "total_rows": len(rows),
        "soft_exit_rows": len(soft_rows),
        "value_over_hold_rows": len(value_rows),
        "probability_reduce_rows": len(reduce_rows),
        "collapse_rows": len(collapse_rows),
        "would_suppress_rows": len(would_suppress),
        "would_suppress_winners": sum(1 for row in would_suppress if side_won(row)),
        "would_suppress_losers": sum(1 for row in would_suppress if not side_won(row)),
        "would_suppress_delta_cents": sum(deltas),
        "fail_reason_counts": dict(sorted(reason_counts.items())),
        "would_suppress_examples": [compact(row, variant) for row in would_suppress[:12]],
        "near_miss_examples": [compact(row, variant) for row in value_rows if not value_only_suppresses(row, variant)][:12],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This report explains opportunity availability only; it does not change the frozen value-only book-gap rule.",
        (
            f"Post-freeze rows {report.get('total_rows')}, soft exits {report.get('soft_exit_rows')}, "
            f"value-over-hold exits {report.get('value_over_hold_rows')}, probability-reduce exits "
            f"{report.get('probability_reduce_rows')}, would-suppress rows {report.get('would_suppress_rows')}."
        ),
        f"Fail reasons are {report.get('fail_reason_counts')}.",
    ]
    if int(report.get("probability_reduce_rows") or 0) > 0:
        notes.append("Probability-reduce rows are expected to stay unsuppressed in this value-only watch.")
    if int(report.get("value_over_hold_rows") or 0) == 0:
        notes.append("No value-over-hold exits have reached the post-freeze denominator yet.")
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
        "# v28 Exit Book-Gap Value-Only Opportunity Denominator",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| rows | soft exits | value exits | reduce exits | collapse exits | would suppress | delta c | suppressed W/L | fail reasons |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            (
                f"| {report.get('total_rows')} | {report.get('soft_exit_rows')} | "
                f"{report.get('value_over_hold_rows')} | {report.get('probability_reduce_rows')} | "
                f"{report.get('collapse_rows')} | {report.get('would_suppress_rows')} | "
                f"{fmt(report.get('would_suppress_delta_cents'))} | "
                f"{report.get('would_suppress_winners')}/{report.get('would_suppress_losers')} | "
                f"{report.get('fail_reason_counts')} |"
            ),
            "",
            "## Near Misses",
            "",
            "| market | side | result | reason | entry | exit | p_hold | bid | gap | current c | hold c | delta if suppressed | fail reasons |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("near_miss_examples") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('exit_bid_prob'))} | {fmt(row.get('hold_book_gap'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('delta_if_suppressed_cents'))} | {', '.join(row.get('fail_reasons') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Would Suppress",
            "",
            "| market | side | result | reason | entry | exit | p_hold | bid | gap | current c | hold c | delta if suppressed |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("would_suppress_examples") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('exit_bid_prob'))} | {fmt(row.get('hold_book_gap'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('delta_if_suppressed_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
