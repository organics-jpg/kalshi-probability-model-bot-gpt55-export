"""Opportunity denominator for frozen book-gap loss-guard v3.

Research-only; no live bot changes or orders.

V3 is a newly frozen extreme-probability relaxation of v2. This report explains
whether post-freeze rows are missing, non-soft, soft-but-not-suppressible, or
would have fired under v3, and whether those opportunities are v3-only versus
also accepted by v2.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import exit_bid_prob, fair_drawdown, exit_reason, hold_book_gap, is_soft_exit, p_hold
from probe_v28_exit_policy_candidates import build_rows, current_exit, hold_to_settlement
from probe_v28_frozen_exit_book_gap_loss_guard import is_probability_reduce, is_value_over_hold
from probe_v28_frozen_exit_book_gap_loss_guard_v2 import (
    STATE_JSON as V2_STATE_JSON,
    should_suppress as v2_should_suppress,
)
from probe_v28_frozen_exit_book_gap_loss_guard_v3 import (
    STATE_JSON,
    parse_ts,
    should_suppress,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_book_gap_loss_guard_v3_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_exit_book_gap_loss_guard_v3_opportunity_latest.md"


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


def future_rows(freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows: list[dict[str, Any]] = []
    for row in build_rows():
        exit_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and exit_dt is not None and exit_dt < freeze_dt:
            continue
        rows.append(row)
    return rows


def fail_reasons(row: dict[str, Any], state: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not is_soft_exit(row):
        reasons.append("not_soft_exit")
        return reasons
    p = p_hold(row)
    gap = hold_book_gap(row)
    drawdown = fair_drawdown(row)
    if is_value_over_hold(row):
        p_floor = float(state.get("value_p_hold_floor") or 0.85)
        extreme_floor = float(state.get("value_extreme_p_hold_floor") or 0.95)
        gap_floor = float(state.get("value_gap_floor") or 0.0)
        drawdown_floor = float(state.get("value_fair_drawdown_floor_cents") or -5.0)
        if gap is None:
            reasons.append("value_gap_missing")
        elif gap < gap_floor:
            reasons.append("value_gap_below_floor")
        if p is None:
            reasons.append("value_p_hold_missing")
        elif p < p_floor:
            reasons.append("value_p_hold_below_floor")
        if drawdown is None:
            reasons.append("value_fair_drawdown_missing")
        elif drawdown < drawdown_floor:
            reasons.append("value_fair_drawdown_too_deep")
        if p is None or p < extreme_floor:
            reasons.append("value_extreme_p_hold_below_floor")
        return [] if should_suppress(row, state) else reasons
    if is_probability_reduce(row):
        p_floor = float(state.get("reduce_p_hold_floor") or 0.79)
        gap_floor = float(state.get("reduce_gap_floor") or 0.0)
        if p is None:
            reasons.append("reduce_p_hold_missing")
        elif p < p_floor:
            reasons.append("reduce_p_hold_below_floor")
        if gap is None:
            reasons.append("reduce_gap_missing")
        elif gap < gap_floor:
            reasons.append("reduce_gap_below_floor")
        return [] if should_suppress(row, state) else reasons
    reasons.append("unsupported_soft_exit_reason")
    return reasons


def compact(row: dict[str, Any], state: dict[str, Any], v2_state: dict[str, Any]) -> dict[str, Any]:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    v3_suppress = should_suppress(row, state)
    v2_suppress = v2_should_suppress(row, v2_state)
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
        "fair_drawdown_cents": fair_drawdown(row),
        "current_cents": cur,
        "hold_cents": hold,
        "delta_if_suppressed_cents": None if cur is None or hold is None else float(hold) - float(cur),
        "would_suppress_v2": v2_suppress,
        "would_suppress_v3": v3_suppress,
        "v3_only": v3_suppress and not v2_suppress,
        "fail_reasons": fail_reasons(row, state),
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    v2_state = load_json(V2_STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or utc_now_iso())
    rows = future_rows(freeze_ts)
    soft_rows = [row for row in rows if is_soft_exit(row)]
    value_rows = [row for row in rows if is_value_over_hold(row)]
    reduce_rows = [row for row in rows if is_probability_reduce(row)]
    would_suppress = [row for row in rows if should_suppress(row, state)]
    v2_would_suppress = [row for row in rows if v2_should_suppress(row, v2_state)]
    v3_only = [row for row in would_suppress if not v2_should_suppress(row, v2_state)]
    reason_counts = Counter()
    for row in rows:
        for reason in fail_reasons(row, state):
            reason_counts[reason] += 1
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "candidate": state.get("candidate"),
        "total_rows": len(rows),
        "soft_exit_rows": len(soft_rows),
        "value_over_hold_rows": len(value_rows),
        "probability_reduce_rows": len(reduce_rows),
        "would_suppress_rows": len(would_suppress),
        "v2_would_suppress_rows": len(v2_would_suppress),
        "v3_only_would_suppress_rows": len(v3_only),
        "would_suppress_delta_cents": sum(
            float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
            for row in would_suppress
        ),
        "v3_only_delta_cents": sum(
            float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
            for row in v3_only
        ),
        "fail_reason_counts": dict(sorted(reason_counts.items())),
        "would_suppress_examples": [compact(row, state, v2_state) for row in would_suppress[:12]],
        "v3_only_examples": [compact(row, state, v2_state) for row in v3_only[:12]],
        "near_miss_examples": [compact(row, state, v2_state) for row in soft_rows if not should_suppress(row, state)][:12],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    return [
        "This report explains opportunity availability only; it does not change the frozen v3 loss guard.",
        (
            f"Post-freeze rows {report.get('total_rows')}, soft exits {report.get('soft_exit_rows')}, "
            f"value-over-hold exits {report.get('value_over_hold_rows')}, probability-reduce exits "
            f"{report.get('probability_reduce_rows')}, v3 would-suppress rows {report.get('would_suppress_rows')}."
        ),
        (
            f"V3-only would-suppress rows {report.get('v3_only_would_suppress_rows')} for "
            f"{report.get('v3_only_delta_cents')}c; this is the strict-forward cost/benefit of relaxing v2."
        ),
        f"Fail reasons are {report.get('fail_reason_counts')}.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def append_examples(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "",
        f"## {title}",
        "",
        "| market | side | result | reason | entry | exit | p_hold | bid | gap | drawdown | current c | hold c | delta if suppressed | v2/v3 | fail reasons |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('exit_bid_prob'))} | {fmt(row.get('hold_book_gap'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('delta_if_suppressed_cents'))} | {row.get('would_suppress_v2')}/{row.get('would_suppress_v3')} | "
            f"{', '.join(row.get('fail_reasons') or [])} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Book-Gap Loss-Guard V3 Opportunity Denominator",
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
    lines.extend([
        "",
        "## Summary",
        "",
        "| rows | soft exits | value exits | reduce exits | v2 suppress | v3 suppress | v3-only | v3 delta | v3-only delta | fail reasons |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        (
            f"| {report.get('total_rows')} | {report.get('soft_exit_rows')} | "
            f"{report.get('value_over_hold_rows')} | {report.get('probability_reduce_rows')} | "
            f"{report.get('v2_would_suppress_rows')} | {report.get('would_suppress_rows')} | "
            f"{report.get('v3_only_would_suppress_rows')} | {fmt(report.get('would_suppress_delta_cents'))} | "
            f"{fmt(report.get('v3_only_delta_cents'))} | {report.get('fail_reason_counts')} |"
        ),
    ])
    append_examples(lines, "V3-Only Opportunities", report.get("v3_only_examples") or [])
    append_examples(lines, "Near Misses", report.get("near_miss_examples") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
