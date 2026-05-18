"""Frozen clean rescue watch for broad delayed-recheck exits.

Research-only; no live bot changes or orders.

This freezes the clean diagnostic rescue found after the base broad delayed
recheck: widen the immediate-drop allowance from 10c to 11c while keeping the
60s recheck and 60c held-bid floor. The wider drop recovers one false-negative
exit without admitting the drop12 row that caused the large post-recheck path
risk in the more aggressive drop15 diagnostic.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from probe_v28_frozen_soft_frontier_midprice_delayed_recheck_exit import (
    ENTRY_LANE,
    ENTRY_POLICY,
    EXIT_SOURCE,
    MIN_FULL_LOSS_CUSHION,
    MIN_ROWS,
    MIN_SUPPRESSED,
    after_freeze,
    fmt,
    summarize,
)
from probe_v28_soft_frontier_midprice_delayed_recheck_exit import (
    BOOK_GAP_JSON,
    MIDPRICE_JSON,
    OUT_DIR,
    REDUCE_JSON,
    evaluate,
    group_exit_rows,
    load_json,
    read_heartbeats,
)


STATE_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_rescue_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_rescue_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_rescue_latest.md"

RECHECK_POLICY = "delay60_bid_ge60_drop_lte11"
RECHECK_RULE = {"name": RECHECK_POLICY, "delay_seconds": 60, "bid_floor": 60, "max_drop": 11}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "soft_frontier_midprice_delayed_recheck_rescue",
        "entry_lane": ENTRY_LANE,
        "entry_policy": ENTRY_POLICY,
        "exit_source": EXIT_SOURCE,
        "recheck_policy": RECHECK_POLICY,
        "rule": "Broad soft-frontier/mid-price entry; on latest v28 exit, wait 60s and suppress only if held bid remains >=60c with <=11c immediate drop.",
        "physics": "The base 10c delayed-recheck avoids blind hold-through risk. The 11c rescue admits only one extra false-negative exit seen in diagnostics, while still rejecting the drop12 row that later fell sharply after recheck.",
        "strict_forward_note": "Rows before this timestamp are diagnostic only.",
        "promotion_note": "This is watch-only until post-birth rows clear the normal live-readiness gates.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def selected_composition() -> dict[str, Any]:
    midprice = load_json(MIDPRICE_JSON)
    book_rows = group_exit_rows(BOOK_GAP_JSON)
    reduce_rows = group_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    for lane in midprice.get("lanes") or []:
        if not isinstance(lane, dict) or lane.get("lane") != ENTRY_LANE:
            continue
        for entry_variant in lane.get("variants") or []:
            if not isinstance(entry_variant, dict) or entry_variant.get("candidate") != ENTRY_POLICY:
                continue
            return evaluate(lane, entry_variant, EXIT_SOURCE, RECHECK_RULE, book_rows, reduce_rows, heartbeats)
    return {}


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    diagnostic = selected_composition()
    rows = [row for row in diagnostic.get("rows") or [] if isinstance(row, dict)]
    post_rows = [row for row in rows if after_freeze(row, freeze_ts)]
    lanes = [
        {"lane": "diagnostic_prefreeze_context", "summary": summarize(rows, False), "rows": rows},
        {"lane": "post_clean_rescue_birth", "summary": summarize(post_rows, True), "rows": post_rows},
    ]
    post = lanes[1]["summary"]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "diagnostic_parent": {key: value for key, value in diagnostic.items() if key != "rows"},
        "lanes": lanes,
        "candidate_live_ready": False,
        "interpretation": [
            "Research-only frozen clean delayed-recheck rescue watch; no live bot changes or orders.",
            f"Post-birth has {post.get('rows')} joined rows, {post.get('suppressed')} suppressions, net {post.get('weighted_candidate_cents')}c.",
            f"Strict gates use MIN_ROWS={MIN_ROWS}, MIN_SUPPRESSED={MIN_SUPPRESSED}, MIN_FULL_LOSS_CUSHION={MIN_FULL_LOSS_CUSHION}.",
            "Only post-birth rows count as forward evidence.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Soft-Frontier Mid-Price Delayed-Recheck Clean Rescue",
        "",
        "Research-only frozen watch. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Entry: `{state.get('entry_policy')}`",
        f"- Exit source: `{state.get('exit_source')}`",
        f"- Recheck: `{state.get('recheck_policy')}`",
        f"- Rule: `{state.get('rule')}`",
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
            "| lane | rows | suppressed | H/H | current c | candidate c | delta c | W/L | recon | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        lines.append(
            f"| `{lane.get('lane')}` | {summary.get('rows')} | {summary.get('suppressed')} | "
            f"{summary.get('helpful_suppressed')}/{summary.get('harmful_suppressed')} | "
            f"{fmt(summary.get('weighted_current_cents'))} | {fmt(summary.get('weighted_candidate_cents'))} | "
            f"{fmt(summary.get('weighted_delta_cents'))} | {summary.get('candidate_wins')}/{summary.get('candidate_losses')} | "
            f"{fmt(summary.get('reconstructed_share'))} | {summary.get('full_loss_cushion_estimate')} | "
            f"{', '.join(summary.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
