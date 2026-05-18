"""Frozen broad soft-frontier/mid-price delayed-recheck exit watch.

Research-only; no live bot changes or orders.

This freezes the best diagnostic composition from
probe_v28_soft_frontier_midprice_delayed_recheck_exit.py:
diagnostic_entry_quarter_midprice_boundary with the latest/reduce exit source
and delay60_bid_ge60_drop_lte10. Only rows after this file's freeze timestamp
can count as forward evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_soft_frontier_midprice_delayed_recheck_exit import (
    BOOK_GAP_JSON,
    MIDPRICE_JSON,
    OUT_DIR,
    REDUCE_JSON,
    VARIANTS,
    evaluate,
    fnum,
    group_exit_rows,
    load_json,
    parse_ts,
    read_heartbeats,
)


STATE_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.md"

ENTRY_LANE = "diagnostic_entry"
ENTRY_POLICY = "diagnostic_entry_quarter_midprice_boundary"
EXIT_SOURCE = "latest"
RECHECK_POLICY = "delay60_bid_ge60_drop_lte10"
MIN_ROWS = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3


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
        "candidate_family": "soft_frontier_midprice_delayed_recheck_exit",
        "entry_lane": ENTRY_LANE,
        "entry_policy": ENTRY_POLICY,
        "exit_source": EXIT_SOURCE,
        "recheck_policy": RECHECK_POLICY,
        "rule": "Broad soft-frontier/mid-price entry; on latest v28 exit, wait 60s and suppress only if held bid remains >=60c with <=10c immediate drop.",
        "physics": "A broad v28 entry can be correct while the exit clips a still-supported side. The delayed recheck tries to keep only exits where the post-signal book still supports the held thesis, avoiding blind hold-through air pockets.",
        "strict_forward_note": "Rows before this timestamp are diagnostic only.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def after_freeze(row: dict[str, Any], freeze_ts: str) -> bool:
    ts = parse_ts(row.get("exit_ts"))
    freeze = parse_ts(freeze_ts)
    return bool(ts and freeze and ts >= freeze)


def selected_composition() -> dict[str, Any]:
    midprice = load_json(MIDPRICE_JSON)
    book_rows = group_exit_rows(BOOK_GAP_JSON)
    reduce_rows = group_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    recheck = next(item for item in VARIANTS if item["name"] == RECHECK_POLICY)
    for lane in midprice.get("lanes") or []:
        if not isinstance(lane, dict) or lane.get("lane") != ENTRY_LANE:
            continue
        for entry_variant in lane.get("variants") or []:
            if not isinstance(entry_variant, dict) or entry_variant.get("candidate") != ENTRY_POLICY:
                continue
            return evaluate(lane, entry_variant, EXIT_SOURCE, recheck, book_rows, reduce_rows, heartbeats)
    return {}


def summarize(rows: list[dict[str, Any]], strict_forward: bool) -> dict[str, Any]:
    suppressed = [row for row in rows if row.get("suppressed")]
    helpful = [row for row in suppressed if fnum(row.get("weighted_delta_cents")) > 0]
    harmful = [row for row in suppressed if fnum(row.get("weighted_delta_cents")) < 0]
    current = sum(fnum(row.get("weighted_current_cents")) for row in rows)
    candidate = sum(fnum(row.get("weighted_candidate_cents")) for row in rows)
    source_counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("source") or "unknown")
        source_counts[key] = source_counts.get(key, 0) + 1
    total = sum(source_counts.values())
    reconstructed_share = None if total <= 0 else (total - int(source_counts.get("approved_entry") or 0)) / total
    cushion = int(max(0.0, candidate) // 100.0)
    blockers: list[str] = []
    if strict_forward and len(rows) < MIN_ROWS:
        blockers.append("joined_rows_lt_30")
    if strict_forward and len(suppressed) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if candidate <= 0:
        blockers.append("weighted_net_not_positive")
    if candidate - current <= 0:
        blockers.append("delta_not_positive")
    if harmful:
        blockers.append("suppressed_losers_present")
    if reconstructed_share is not None and reconstructed_share > 0.35:
        blockers.append("reconstructed_share_gt_35pct")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    return {
        "rows": len(rows),
        "strict_forward": strict_forward,
        "suppressed": len(suppressed),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "weighted_current_cents": current,
        "weighted_candidate_cents": candidate,
        "weighted_delta_cents": candidate - current,
        "candidate_wins": sum(1 for row in rows if fnum(row.get("weighted_candidate_cents")) >= 0),
        "candidate_losses": sum(1 for row in rows if fnum(row.get("weighted_candidate_cents")) < 0),
        "source_counts": source_counts,
        "reconstructed_share": reconstructed_share,
        "full_loss_cushion_estimate": cushion,
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    diagnostic = selected_composition()
    rows = [row for row in diagnostic.get("rows") or [] if isinstance(row, dict)]
    post_rows = [row for row in rows if after_freeze(row, freeze_ts)]
    lanes = [
        {"lane": "diagnostic_prefreeze_context", "summary": summarize(rows, False), "rows": rows},
        {"lane": "post_delayed_recheck_birth", "summary": summarize(post_rows, True), "rows": post_rows},
    ]
    post = lanes[1]["summary"]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "diagnostic_parent": {key: value for key, value in diagnostic.items() if key != "rows"},
        "lanes": lanes,
        "candidate_live_ready": False,
        "interpretation": [
            "Research-only frozen broad-entry delayed-recheck exit watch; no live bot changes or orders.",
            f"Post-birth has {post.get('rows')} joined rows, {post.get('suppressed')} suppressions, net {post.get('weighted_candidate_cents')}c.",
            "Only post-birth rows count as forward evidence.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Soft-Frontier Mid-Price Delayed-Recheck Exit",
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
