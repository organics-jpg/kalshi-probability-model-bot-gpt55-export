"""Bridge v28 probability calibration to realized trading profitability.

Research-only; no live bot changes or orders.

The active goal is not just calibrated settlement probability; it is profitable
trading at broad BTC 15m coverage. This report buckets actual v28-approved
entries by probability/edge/book-disagreement and compares binary settlement
accuracy with realized exit P&L and exit value versus hold-to-settlement.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_forward_physics_registry import build_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_probability_profit_bridge_latest.json"
OUT_MD = OUT_DIR / "v28_probability_profit_bridge_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def book_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_cents"))
    return None if ask is None else ask / 100.0


def raw_book_gap(row: dict[str, Any]) -> float | None:
    p = as_float(row.get("p_side"))
    b = book_prob(row)
    return None if p is None or b is None else p - b


def bucket_probability(row: dict[str, Any]) -> str:
    p = as_float(row.get("p_side"))
    if p is None:
        return "p_missing"
    if p < 0.85:
        return "p_lt_85"
    if p < 0.875:
        return "p_85_875"
    if p < 0.90:
        return "p_875_90"
    if p < 0.95:
        return "p_90_95"
    return "p_ge_95"


def bucket_edge(row: dict[str, Any]) -> str:
    edge = as_float(row.get("edge_cents"))
    if edge is None:
        return "edge_missing"
    if edge < 2.0:
        return "edge_lt_2c"
    if edge < 4.0:
        return "edge_2_4c"
    if edge < 8.0:
        return "edge_4_8c"
    if edge < 16.0:
        return "edge_8_16c"
    return "edge_ge_16c"


def bucket_gap(row: dict[str, Any]) -> str:
    gap = raw_book_gap(row)
    if gap is None:
        return "gap_missing"
    if gap < -0.05:
        return "book_above_raw_gt_5pp"
    if gap <= 0.05:
        return "raw_book_near"
    if gap <= 0.15:
        return "raw_above_book_5_15pp"
    if gap <= 0.30:
        return "raw_above_book_15_30pp"
    return "raw_above_book_gt_30pp"


def bucket_reentry(row: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    prior = [
        other for other in rows
        if other is not row
        and str(other.get("market")) == str(row.get("market"))
        and str(other.get("side")) == str(row.get("side"))
        and str(other.get("entry_ts") or "") < str(row.get("entry_ts") or "")
    ]
    return "same_side_reentry" if prior else "first_same_side"


def summarize(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    p_values = [as_float(row.get("p_side")) for row in settled]
    p_values = [p for p in p_values if p is not None]
    outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in settled]
    actual_rows = [row for row in settled if row.get("actual_gross_cents") is not None]
    hold_rows = [row for row in settled if row.get("hold_gross_cents") is not None]
    exit_value_rows = [row for row in settled if row.get("exit_value_cents") is not None]
    gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in actual_rows)
    hold = sum(float(row.get("hold_gross_cents") or 0.0) for row in hold_rows)
    exit_value = sum(float(row.get("exit_value_cents") or 0.0) for row in exit_value_rows)
    return {
        "bucket": name,
        "rows": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "avg_p": avg(p_values),
        "win_rate": avg(outcomes),
        "calibration_error": None if avg(outcomes) is None or avg(p_values) is None else avg(outcomes) - avg(p_values),
        "actual_gross_cents": gross,
        "hold_gross_cents": hold,
        "exit_value_cents": exit_value,
        "avg_actual_gross_cents": gross / len(actual_rows) if actual_rows else None,
        "avg_hold_gross_cents": hold / len(hold_rows) if hold_rows else None,
        "avg_exit_value_cents": exit_value / len(exit_value_rows) if exit_value_rows else None,
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def by_bucket(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], str]) -> list[dict[str, Any]]:
    buckets = sorted({fn(row) for row in rows})
    return [summarize(bucket, [row for row in rows if fn(row) == bucket]) for bucket in buckets]


def build_report() -> dict[str, Any]:
    rows = build_rows()
    settled = [row for row in rows if row.get("side_won") is not None]
    return {
        "surface": "actual_v28_approved_entries",
        "rows": len(rows),
        "settled": len(settled),
        "overall": summarize("all", rows),
        "by_probability": by_bucket(rows, "probability", bucket_probability),
        "by_edge": by_bucket(rows, "edge", bucket_edge),
        "by_raw_book_gap": by_bucket(rows, "raw_book_gap", bucket_gap),
        "by_reentry": by_bucket(rows, "reentry", lambda row: bucket_reentry(row, rows)),
        "interpretation": current_read(rows),
    }


def current_read(rows: list[dict[str, Any]]) -> list[str]:
    overall = summarize("all", rows)
    gap_rows = by_bucket(rows, "raw_book_gap", bucket_gap)
    reentry_rows = by_bucket(rows, "reentry", lambda row: bucket_reentry(row, rows))
    notes = [
        f"Overall settled win rate is {overall.get('win_rate')} with avg p {overall.get('avg_p')}, actual gross {overall.get('actual_gross_cents')}c, and exit value {overall.get('exit_value_cents')}c.",
    ]
    worst_gap = min(gap_rows, key=lambda row: float(row.get("actual_gross_cents") or 0.0), default=None)
    if worst_gap:
        notes.append(
            f"Worst raw/book gap bucket by actual gross is {worst_gap.get('bucket')} with {worst_gap.get('settled')} settled rows and {worst_gap.get('actual_gross_cents')}c."
        )
    for row in reentry_rows:
        notes.append(
            f"Reentry bucket {row.get('bucket')} has {row.get('settled')} settled rows, gross {row.get('actual_gross_cents')}c, hold {row.get('hold_gross_cents')}c."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def table(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "",
        f"## {title}",
        "",
        "| bucket | settled | W/L | avg p | win rate | cal err | actual c | hold c | exit value c | avg actual c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in rows:
        lines.append(
            f"| `{row.get('bucket')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('calibration_error'))} | "
            f"{fmt(row.get('actual_gross_cents'))} | {fmt(row.get('hold_gross_cents'))} | "
            f"{fmt(row.get('exit_value_cents'))} | {fmt(row.get('avg_actual_gross_cents'))} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    overall = report.get("overall") or {}
    lines = [
        "# v28 Probability Profit Bridge",
        "",
        "Maps settlement probability buckets to realized exit P&L and hold-to-settlement P&L.",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Rows/settled: `{report.get('rows')}/{report.get('settled')}`",
        f"- Overall actual/hold/exit value: `{fmt(overall.get('actual_gross_cents'))}c/{fmt(overall.get('hold_gross_cents'))}c/{fmt(overall.get('exit_value_cents'))}c`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    table(lines, "By Probability", report.get("by_probability") or [])
    table(lines, "By Edge", report.get("by_edge") or [])
    table(lines, "By Raw Book Gap", report.get("by_raw_book_gap") or [])
    table(lines, "By Reentry", report.get("by_reentry") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
