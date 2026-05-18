"""Frozen feature-gate exit-bid delayed-recheck watch.

Research-only; no live bot changes or orders.

This freezes the cautious child of the high-exit-bid repair:
after a selected-side feature-gate exit signal, wait 60 seconds; suppress the
exit only if the held-side bid is still >=60c and the immediate window did not
drop more than 10c from the original exit bid.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_feature_gate_exit_bid_delayed_recheck import (
    OUT_DIR,
    VARIANTS,
    evaluate_row,
    fnum,
    path_points,
    read_heartbeats,
    suppressed_watch_rows,
)
from probe_v28_feature_gate_exit_bid_path_risk import load_json, parse_utc


STATE_JSON = OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_latest.md"

PRIMARY_NAME = "delay60_bid_ge60_drop_lte10"
MIN_SETTLED = 30
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
        "candidate_family": "feature_gate_exit_bid_delayed_recheck",
        "candidate": PRIMARY_NAME,
        "rule": "Delay 60s after selected-side feature-gate exit; suppress only if held-side bid >=60c and window drop <=10c.",
        "physics": "High exit bids can be winner clips, but immediate air pockets are a survival risk. The delayed recheck requires the market to keep supporting the held side before overriding the live exit.",
        "strict_forward_note": "Rows before this timestamp are diagnostic only.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def after_freeze(row: dict[str, Any], freeze_ts: str) -> bool:
    row_ts = parse_utc(row.get("first_exit_ts_utc"))
    freeze = parse_utc(freeze_ts)
    return bool(row_ts and freeze and row_ts >= freeze)


def score_rows(rows: list[dict[str, Any]], variant: dict[str, Any]) -> list[dict[str, Any]]:
    heartbeats = read_heartbeats()
    return [evaluate_row(row, path_points(row, heartbeats), variant) for row in rows]


def summarize(rows: list[dict[str, Any]], strict_forward: bool) -> dict[str, Any]:
    suppressed = [row for row in rows if row.get("delayed_recheck_suppressed")]
    helpful = [row for row in suppressed if fnum(row.get("delayed_recheck_delta_cents")) > 0]
    harmful = [row for row in suppressed if fnum(row.get("delayed_recheck_delta_cents")) < 0]
    live = sum(fnum(row.get("live_selected_net_cents")) for row in rows)
    net = sum(fnum(row.get("delayed_recheck_candidate_cents")) for row in rows)
    blockers = []
    if strict_forward and len(rows) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if strict_forward and len(suppressed) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if net <= 0:
        blockers.append("net_not_positive")
    if net - live <= 0:
        blockers.append("delta_not_positive")
    if harmful:
        blockers.append("suppressed_losers_present")
    if int(max(0.0, net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    return {
        "rows": len(rows),
        "strict_forward": strict_forward,
        "suppressed": len(suppressed),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "live_net_cents": live,
        "candidate_net_cents": net,
        "delta_vs_live_cents": net - live,
        "recovery_cents": sum(fnum(row.get("delayed_recheck_delta_cents")) for row in helpful),
        "loss_cost_cents": sum(fnum(row.get("delayed_recheck_delta_cents")) for row in harmful),
        "candidate_wins": sum(1 for row in rows if fnum(row.get("delayed_recheck_candidate_cents")) >= 0),
        "candidate_losses": sum(1 for row in rows if fnum(row.get("delayed_recheck_candidate_cents")) < 0),
        "full_loss_cushion_estimate": int(max(0.0, net) // 100.0),
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    variant = next(item for item in VARIANTS if item["name"] == PRIMARY_NAME)
    diagnostic_rows = score_rows(suppressed_watch_rows("diagnostic_feature_gate_exit_bid"), variant)
    post_source_rows = [
        row for row in suppressed_watch_rows("post_exit_bid_birth")
        if after_freeze(row, freeze_ts)
    ]
    post_rows = score_rows(post_source_rows, variant)
    lanes = [
        {"lane": "diagnostic_prefreeze_context", "summary": summarize(diagnostic_rows, False), "rows": diagnostic_rows},
        {"lane": "post_delayed_recheck_birth", "summary": summarize(post_rows, True), "rows": post_rows},
    ]
    post = lanes[1]["summary"]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "variant": variant,
        "lanes": lanes,
        "interpretation": [
            "Research-only frozen watch; no live bot changes or orders.",
            f"Post-birth has {post.get('rows')} rows, {post.get('suppressed')} suppressions, net {post.get('candidate_net_cents')}c.",
            "Only post-birth rows count as forward evidence.",
        ],
        "candidate_live_ready": False,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Feature-Gate Exit-Bid Delayed Recheck",
        "",
        "Research-only frozen watch. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Candidate: `{state.get('candidate')}`",
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
            "| lane | rows | suppressed | sup H/H | live c | candidate c | delta c | recovery c | loss cost c | W/L | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        lines.append(
            f"| `{lane.get('lane')}` | {summary.get('rows')} | {summary.get('suppressed')} | "
            f"{summary.get('helpful_suppressed')}/{summary.get('harmful_suppressed')} | "
            f"{fmt(summary.get('live_net_cents'))} | {fmt(summary.get('candidate_net_cents'))} | "
            f"{fmt(summary.get('delta_vs_live_cents'))} | {fmt(summary.get('recovery_cents'))} | "
            f"{fmt(summary.get('loss_cost_cents'))} | {summary.get('candidate_wins')}/{summary.get('candidate_losses')} | "
            f"{summary.get('full_loss_cushion_estimate')} | {', '.join(summary.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
