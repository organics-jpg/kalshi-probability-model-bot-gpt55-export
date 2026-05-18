"""Robustness audit for frozen v28 probability-reduce suppression.

Research-only; no live bot changes or orders.

This audit asks whether the frozen forward exit lead is broad enough to keep
shadowing. It deliberately does not promote the rule; the live readiness gate
and 30-settled-row requirement still control that decision.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
THRESHOLD_JSON = OUT_DIR / "v28_exit_reduce_threshold_bakeoff_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_suppression_robustness_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_suppression_robustness_latest.md"

MIN_SETTLED_FOR_PROMOTION = 30
MIN_SETTLED_FOR_SHADOW_INTEREST = 10


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


def leave_one_market(rows: list[dict[str, Any]], full_delta: float) -> list[dict[str, Any]]:
    markets = sorted({str(row.get("market")) for row in rows if row.get("market")})
    out = []
    for market in markets:
        removed_delta = sum(float(row.get("delta_cents") or 0.0) for row in rows if str(row.get("market")) == market)
        kept_rows = [row for row in rows if str(row.get("market")) != market]
        out.append({
            "removed_market": market,
            "remaining_rows": len(kept_rows),
            "removed_delta_cents": removed_delta,
            "remaining_delta_cents": full_delta - removed_delta,
        })
    out.sort(key=lambda row: float(row.get("remaining_delta_cents") or 0.0))
    return out


def leave_one_suppressed(rows: list[dict[str, Any]], full_delta: float) -> list[dict[str, Any]]:
    suppressed = [row for row in rows if row.get("suppressed") is True]
    out = []
    for idx, row in enumerate(suppressed):
        removed_delta = float(row.get("delta_cents") or 0.0)
        out.append({
            "removed_index": idx,
            "market": row.get("market"),
            "side": row.get("side"),
            "p_hold": row.get("p_hold"),
            "removed_delta_cents": removed_delta,
            "remaining_delta_cents": full_delta - removed_delta,
        })
    out.sort(key=lambda row: float(row.get("remaining_delta_cents") or 0.0))
    return out


def threshold_context(threshold_report: dict[str, Any]) -> dict[str, Any]:
    summaries = threshold_report.get("summaries") if isinstance(threshold_report.get("summaries"), list) else []
    frozen = next((row for row in summaries if as_float(row.get("threshold")) == 0.75), {})
    lower = next((row for row in summaries if as_float(row.get("threshold")) == 0.74), {})
    upper = next((row for row in summaries if as_float(row.get("threshold")) == 0.76), {})
    return {
        "frozen_0p75_delta_cents": as_float(frozen.get("delta_vs_current_cents")),
        "frozen_0p75_suppressed_losers": int(as_float(frozen.get("suppressed_losers")) or 0),
        "lower_0p74_delta_cents": as_float(lower.get("delta_vs_current_cents")),
        "lower_0p74_suppressed_losers": int(as_float(lower.get("suppressed_losers")) or 0),
        "upper_0p76_delta_cents": as_float(upper.get("delta_vs_current_cents")),
        "upper_0p76_suppressed_losers": int(as_float(upper.get("suppressed_losers")) or 0),
    }


def build_report() -> dict[str, Any]:
    frozen = load_json(FROZEN_JSON)
    threshold = load_json(THRESHOLD_JSON)
    summary = frozen.get("summary") or {}
    rows = frozen.get("rows") if isinstance(frozen.get("rows"), list) else []
    full_delta = float(summary.get("delta_vs_current_cents") or 0.0)
    leave_market = leave_one_market(rows, full_delta)
    leave_suppressed = leave_one_suppressed(rows, full_delta)
    context = threshold_context(threshold)

    settled = int(as_float(summary.get("settled")) or 0)
    suppressed_exits = int(as_float(summary.get("suppressed_exits")) or 0)
    suppressed_rows = [row for row in rows if row.get("suppressed") is True]
    suppressed_markets = sorted({str(row.get("market")) for row in suppressed_rows if row.get("market")})
    suppressed_sides = sorted({str(row.get("side")) for row in suppressed_rows if row.get("side")})
    suppressed_winners = sum(1 for row in suppressed_rows if row.get("result") == row.get("side"))
    suppressed_losers = len(suppressed_rows) - suppressed_winners
    worst_hold_marks = [
        value for value in (as_float(row.get("worst_post_exit_hold_mark_cents")) for row in suppressed_rows)
        if value is not None
    ]
    worst_suppressed_hold_mark = min(worst_hold_marks) if worst_hold_marks else None
    loss_cost = float(summary.get("loss_control_cost_cents") or 0.0)
    worst_leave_market = as_float((leave_market[0] if leave_market else {}).get("remaining_delta_cents"))
    worst_leave_suppressed = as_float((leave_suppressed[0] if leave_suppressed else {}).get("remaining_delta_cents"))
    blockers = []
    if settled < MIN_SETTLED_FOR_PROMOTION:
        blockers.append("settled_lt_30")
    if full_delta <= 0.0:
        blockers.append("delta_not_positive")
    if suppressed_exits <= 0:
        blockers.append("no_suppressed_exits")
    if loss_cost < 0.0:
        blockers.append("suppressed_loss_cost_negative")
    if worst_leave_market is None or worst_leave_market <= 0.0:
        blockers.append("leave_one_market_not_positive")
    if worst_leave_suppressed is None or worst_leave_suppressed <= 0.0:
        blockers.append("leave_one_suppressed_not_positive")
    if len(suppressed_markets) < 3:
        blockers.append("suppressed_market_count_lt_3")
    if len(suppressed_sides) < 2:
        blockers.append("suppressed_side_diversity_missing")
    if suppressed_losers > 0:
        blockers.append("suppressed_losers_present")

    shadow_interest = (
        settled >= MIN_SETTLED_FOR_SHADOW_INTEREST
        and full_delta > 0.0
        and suppressed_exits > 0
        and loss_cost >= 0.0
        and worst_leave_market is not None
        and worst_leave_market > 0.0
        and worst_leave_suppressed is not None
        and worst_leave_suppressed > 0.0
    )
    yes_only_shadow_interest = shadow_interest and suppressed_sides == ["yes"] and suppressed_losers == 0
    return {
        "freeze": frozen.get("freeze") or {},
        "summary": summary,
        "suppressed_profile": {
            "suppressed_exits": suppressed_exits,
            "suppressed_markets": len(suppressed_markets),
            "suppressed_market_ids": suppressed_markets,
            "suppressed_sides": suppressed_sides,
            "suppressed_winners": suppressed_winners,
            "suppressed_losers": suppressed_losers,
            "worst_suppressed_hold_mark_cents": worst_suppressed_hold_mark,
        },
        "threshold_context": context,
        "leave_one_market": leave_market,
        "leave_one_suppressed": leave_suppressed,
        "promotion_ready": not blockers,
        "shadow_interest": shadow_interest,
        "yes_only_shadow_interest": yes_only_shadow_interest,
        "blockers": blockers,
        "interpretation": [
            f"Frozen forward rows settled={settled}, delta={full_delta}c, suppressed exits={suppressed_exits}.",
            f"Suppressed profile: sides={suppressed_sides}, markets={len(suppressed_markets)}, winners/losers={suppressed_winners}/{suppressed_losers}, worst hold mark={worst_suppressed_hold_mark}c.",
            f"Worst leave-one-market delta is {worst_leave_market}c; worst leave-one-suppressed delta is {worst_leave_suppressed}c.",
            f"Diagnostic threshold context: 0.75 has {context.get('frozen_0p75_suppressed_losers')} suppressed losers; 0.74 has {context.get('lower_0p74_suppressed_losers')}.",
            "Full two-sided promotion remains blocked until sample size and suppressed-loser/loss-cost blockers clear; a YES-only interpretation is tracked separately.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    summary = report.get("summary") or {}
    profile = report.get("suppressed_profile") or {}
    lines = [
        "# v28 Exit Reduce Suppression Robustness",
        "",
        "Research-only: no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Settled rows: `{summary.get('settled')}`",
        f"- Delta vs current: `{summary.get('delta_vs_current_cents')}c`",
        f"- Shadow interest: `{report.get('shadow_interest')}`",
        f"- YES-only shadow interest: `{report.get('yes_only_shadow_interest')}`",
        f"- Promotion ready: `{report.get('promotion_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        f"- Suppressed profile: sides `{profile.get('suppressed_sides')}`, markets `{profile.get('suppressed_markets')}`, W/L `{profile.get('suppressed_winners')}/{profile.get('suppressed_losers')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Leave-One Market",
        "",
        "| removed market | remaining rows | removed delta c | remaining delta c |",
        "|---|---:|---:|---:|",
    ])
    for row in report.get("leave_one_market") or []:
        lines.append(
            f"| {row.get('removed_market')} | {row.get('remaining_rows')} | "
            f"{fmt(row.get('removed_delta_cents'))} | {fmt(row.get('remaining_delta_cents'))} |"
        )
    lines.extend([
        "",
        "## Leave-One Suppressed Exit",
        "",
        "| market | side | p_hold | removed delta c | remaining delta c |",
        "|---|---|---:|---:|---:|",
    ])
    for row in report.get("leave_one_suppressed") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('removed_delta_cents'))} | {fmt(row.get('remaining_delta_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
