"""Opportunity audit for the frozen matched-unchanged loss guard watch.

Research-only; no live bot changes or orders.

The frozen matched-unchanged loss guard has strict post-freeze scored rows but
no selected rows. This probe explains whether that is true opportunity scarcity
or one/two rule gates excluding near-miss rows.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_common_clock_watch import build_scored_rows
from probe_v28_frozen_matched_unchanged_loss_guard_watch import (
    OUT_DIR,
    RULE,
    STATE_JSON,
    after_freeze,
    fnum,
    hold_delta,
    load_json,
    row_feature,
    should_suppress,
)


OUT_JSON = OUT_DIR / "v28_matched_unchanged_loss_guard_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_matched_unchanged_loss_guard_opportunity_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fail_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    abs_d = row_feature(row, "abs_d_sigma")
    exit_cents = row_feature(row, "exit_cents")
    depth = row_feature(row, "eligible_depth")
    p_hold = row_feature(row, "exit_p_hold")
    if abs_d is None:
        reasons.append("missing_abs_d_sigma")
    elif abs_d > RULE["abs_d_sigma_max"]:
        reasons.append("abs_d_sigma_above_max")
    if exit_cents is None:
        reasons.append("missing_exit_cents")
    elif exit_cents < RULE["exit_cents_min"]:
        reasons.append("exit_cents_below_min")
    if depth is None:
        reasons.append("missing_eligible_depth")
    elif depth > RULE["eligible_depth_max"]:
        reasons.append("eligible_depth_above_max")
    if p_hold is None:
        reasons.append("missing_exit_p_hold")
    elif p_hold < RULE["exit_p_hold_min"]:
        reasons.append("exit_p_hold_below_min")
    return reasons


def compact(row: dict[str, Any]) -> dict[str, Any]:
    current = fnum(row.get("actual_gross_cents")) or 0.0
    hold = fnum(row.get("hold_gross_cents")) or 0.0
    reasons = fail_reasons(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": row.get("exit_reason"),
        "current_cents": current,
        "hold_cents": hold,
        "hold_delta_cents": hold - current,
        "would_suppress": should_suppress(row),
        "fail_reasons": reasons,
        "fail_count": len(reasons),
        "abs_d_sigma": row_feature(row, "abs_d_sigma"),
        "eligible_depth": row_feature(row, "eligible_depth"),
        "exit_cents": row_feature(row, "exit_cents"),
        "exit_p_hold": row_feature(row, "exit_p_hold"),
        "exit_fair_drawdown_cents": row_feature(row, "exit_fair_drawdown_cents"),
        "hold_book_gap": row_feature(row, "hold_book_gap"),
        "ask_cents": row_feature(row, "ask_cents"),
        "p_side": row_feature(row, "p_side"),
        "raw_edge_cents": row_feature(row, "raw_edge_cents"),
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = state.get("freeze_ts_utc")
    scored = [row for row in build_scored_rows() if hold_delta(row) is not None]
    post = [row for row in scored if after_freeze(row, freeze_ts)]
    selected = [row for row in post if should_suppress(row)]
    nonselected = [row for row in post if not should_suppress(row)]
    near = [row for row in nonselected if 0 < len(fail_reasons(row)) <= 2]
    fail_counter = Counter(reason for row in nonselected for reason in fail_reasons(row))
    fail_combo_counter = Counter("+".join(fail_reasons(row)) or "selected" for row in nonselected)
    selected_delta = sum(hold_delta(row) or 0.0 for row in selected)
    near_delta = sum(hold_delta(row) or 0.0 for row in near)
    post_current = sum(fnum(row.get("actual_gross_cents")) or 0.0 for row in post)
    post_hold = sum(fnum(row.get("hold_gross_cents")) or 0.0 for row in post)
    blockers: list[str] = []
    if len(post) < 30:
        blockers.append("post_rows_lt_30")
    if len(selected) < 30:
        blockers.append("selected_rows_lt_30")
    if not selected:
        blockers.append("rule_has_not_fired")
    if selected_delta <= 0.0:
        blockers.append("selected_delta_not_positive")
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "post_freeze_rows": len(post),
        "selected_rows": len(selected),
        "near_miss_rows": len(near),
        "post_current_cents": post_current,
        "post_hold_cents": post_hold,
        "post_hold_delta_cents": post_hold - post_current,
        "selected_hold_delta_cents": selected_delta,
        "near_miss_hold_delta_cents": near_delta,
        "fail_reason_counts": dict(fail_counter),
        "fail_combo_counts": dict(fail_combo_counter),
        "selected_examples": [compact(row) for row in selected[:12]],
        "near_miss_examples": sorted(
            [compact(row) for row in near],
            key=lambda item: (item.get("fail_count") or 99, -(fnum(item.get("hold_delta_cents")) or 0.0)),
        )[:12],
        "all_post_rows": [compact(row) for row in post],
        "blockers": blockers,
        "live_ready": False,
        "interpretation": [
            "Research-only opportunity audit; no live bot logic changes or orders.",
            (
                f"Post-freeze has {len(post)} scored rows and {len(selected)} selected rows. "
                "This is still a no-fire watch, not a failed positive/negative rule."
            ),
            (
                f"Near-miss rows with one or two failed rule gates: {len(near)}, "
                f"combined hold delta {near_delta}c."
            ),
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    state = report.get("state") or {}
    lines = [
        "# v28 Matched-Unchanged Loss Guard Opportunity",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Rule: `{state.get('rule')}`",
        f"- Post-freeze scored rows: `{report.get('post_freeze_rows')}`",
        f"- Selected rows: `{report.get('selected_rows')}`",
        f"- Near-miss rows: `{report.get('near_miss_rows')}`",
        f"- Post current/hold/delta: `{fmt(report.get('post_current_cents'))}/{fmt(report.get('post_hold_cents'))}/{fmt(report.get('post_hold_delta_cents'))}c`",
        f"- Selected hold delta: `{fmt(report.get('selected_hold_delta_cents'))}c`",
        f"- Near-miss hold delta: `{fmt(report.get('near_miss_hold_delta_cents'))}c`",
        f"- Fail reasons: `{report.get('fail_reason_counts')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Near Misses",
        "",
        "| market | side/result | current | hold | delta | exit | p_hold | abs d | depth | failed gates |",
        "|---|---|---:|---:|---:|---|---:|---:|---:|---|",
    ])
    for row in report.get("near_miss_examples") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')}/{row.get('result')} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | {fmt(row.get('hold_delta_cents'))} | "
            f"{row.get('exit_reason')}@{fmt(row.get('exit_cents'))} | {fmt(row.get('exit_p_hold'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('eligible_depth'))} | "
            f"{', '.join(row.get('fail_reasons') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
