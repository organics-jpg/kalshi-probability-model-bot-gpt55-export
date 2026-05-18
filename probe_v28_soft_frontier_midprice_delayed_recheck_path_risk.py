"""Path-risk audit for the broad soft-frontier delayed-recheck exit watch.

Research-only; no live bot changes or orders.

The broad delayed-recheck composition is the new best diagnostic row, but it
still uses a hold counterfactual after suppressing exits. This audit measures
the observed heartbeat path after the original exit signal and after the delayed
recheck, so we can tell whether the rule avoids the large adverse excursions
that blocked blind high-exit-bid suppression.
"""
from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from probe_v28_feature_gate_exit_bid_path_risk import (
    OUT_DIR,
    fnum,
    load_json,
    parse_utc,
    to_eastern_naive,
    utc_now_iso,
)
from probe_v28_post_exit_path import btc15m_close_time_from_ticker, held_bid, read_heartbeats


WATCH_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_delayed_recheck_path_risk_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_delayed_recheck_path_risk_latest.md"


def suppressed_rows(lane_name: str) -> list[dict[str, Any]]:
    payload = load_json(WATCH_JSON)
    for lane in payload.get("lanes") or []:
        if lane.get("lane") == lane_name:
            return [
                row for row in (lane.get("rows") or [])
                if isinstance(row, dict) and row.get("suppressed")
            ]
    return []


def path_for_row(row: dict[str, Any], heartbeats: list[dict[str, Any]]) -> dict[str, Any]:
    market = str(row.get("market") or "")
    side = str(row.get("side") or "")
    exit_ts_utc = parse_utc(row.get("exit_ts"))
    exit_ts = to_eastern_naive(exit_ts_utc)
    close_ts = to_eastern_naive(btc15m_close_time_from_ticker(market))
    recheck_ts = None if exit_ts is None else exit_ts + timedelta(seconds=60)
    future = [
        {**hb, "held_bid": held_bid(hb, side)}
        for hb in heartbeats
        if hb["market"] == market
        and exit_ts is not None
        and hb["ts"] >= exit_ts
        and (close_ts is None or hb["ts"] < close_ts)
    ]
    after_recheck = [
        point for point in future
        if recheck_ts is not None and point["ts"] >= recheck_ts
    ]
    exit_bid = fnum(row.get("exit_bid"), None)
    recheck_bid = fnum(row.get("recheck_bid"), None)
    future_bids = [fnum(point.get("held_bid")) for point in future]
    recheck_bids = [fnum(point.get("held_bid")) for point in after_recheck]
    min_after_exit_bid = None if not future_bids or exit_bid is None else min(future_bids) - exit_bid
    min_after_recheck_bid = None if not recheck_bids or recheck_bid is None else min(recheck_bids) - recheck_bid
    max_after_recheck_bid = None if not recheck_bids or recheck_bid is None else max(recheck_bids) - recheck_bid
    return {
        "market": market,
        "side": side,
        "source": row.get("source"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": row.get("exit_reason"),
        "exit_bid": exit_bid,
        "recheck_bid": recheck_bid,
        "window_drop_cents": row.get("window_drop_cents"),
        "weighted_candidate_cents": row.get("weighted_candidate_cents"),
        "weighted_delta_cents": row.get("weighted_delta_cents"),
        "points_after_exit": len(future),
        "points_after_recheck": len(after_recheck),
        "min_bid_after_exit": min(future_bids) if future_bids else None,
        "min_bid_after_recheck": min(recheck_bids) if recheck_bids else None,
        "last_bid_after_recheck": recheck_bids[-1] if recheck_bids else None,
        "min_after_exit_bid_cents": min_after_exit_bid,
        "min_after_recheck_bid_cents": min_after_recheck_bid,
        "max_after_recheck_bid_cents": max_after_recheck_bid,
        "adverse_recheck_10c": min_after_recheck_bid is not None and min_after_recheck_bid <= -10.0,
        "adverse_recheck_25c": min_after_recheck_bid is not None and min_after_recheck_bid <= -25.0,
        "adverse_recheck_50c": min_after_recheck_bid is not None and min_after_recheck_bid <= -50.0,
    }


def summarize(rows: list[dict[str, Any]], strict_forward: bool) -> dict[str, Any]:
    with_path = [row for row in rows if row.get("points_after_recheck")]
    min_exit = [
        fnum(row.get("min_after_exit_bid_cents"))
        for row in with_path
        if row.get("min_after_exit_bid_cents") is not None
    ]
    min_recheck = [
        fnum(row.get("min_after_recheck_bid_cents"))
        for row in with_path
        if row.get("min_after_recheck_bid_cents") is not None
    ]
    delta = sum(fnum(row.get("weighted_delta_cents")) for row in rows)
    blockers: list[str] = []
    if strict_forward:
        blockers.append("post_birth_rows_required")
    if len(rows) < 30:
        blockers.append("suppressed_rows_lt_30")
    if any(row.get("adverse_recheck_25c") for row in with_path):
        blockers.append("large_post_recheck_adverse_marks_present")
    if any(row.get("adverse_recheck_50c") for row in with_path):
        blockers.append("extreme_post_recheck_adverse_marks_present")
    return {
        "suppressed_rows": len(rows),
        "rows_with_post_recheck_path": len(with_path),
        "weighted_delta_cents": delta,
        "helpful_rows": sum(1 for row in rows if fnum(row.get("weighted_delta_cents")) > 0),
        "harmful_rows": sum(1 for row in rows if fnum(row.get("weighted_delta_cents")) < 0),
        "avg_min_after_exit_bid_cents": (sum(min_exit) / len(min_exit)) if min_exit else None,
        "worst_min_after_exit_bid_cents": min(min_exit) if min_exit else None,
        "avg_min_after_recheck_bid_cents": (sum(min_recheck) / len(min_recheck)) if min_recheck else None,
        "worst_min_after_recheck_bid_cents": min(min_recheck) if min_recheck else None,
        "adverse_recheck_10c_rows": sum(1 for row in with_path if row.get("adverse_recheck_10c")),
        "adverse_recheck_25c_rows": sum(1 for row in with_path if row.get("adverse_recheck_25c")),
        "adverse_recheck_50c_rows": sum(1 for row in with_path if row.get("adverse_recheck_50c")),
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    heartbeats = read_heartbeats()
    lanes = []
    for lane_name, strict_forward in [
        ("diagnostic_prefreeze_context", False),
        ("post_delayed_recheck_birth", True),
    ]:
        rows = [path_for_row(row, heartbeats) for row in suppressed_rows(lane_name)]
        rows.sort(key=lambda row: fnum(row.get("min_after_recheck_bid_cents"), 999.0))
        lanes.append(
            {
                "lane": lane_name,
                "strict_forward": strict_forward,
                "summary": summarize(rows, strict_forward),
                "rows": rows,
            }
        )
    diagnostic = lanes[0]["summary"]
    interpretation = [
        "Research-only path-risk audit; no live bot changes or orders.",
        (
            f"Diagnostic suppressed rows with post-recheck path: "
            f"{diagnostic.get('rows_with_post_recheck_path')}/{diagnostic.get('suppressed_rows')}; "
            f"worst post-recheck bid excursion {diagnostic.get('worst_min_after_recheck_bid_cents')}c."
        ),
        "If large post-recheck adverse marks remain, the candidate needs a disaster guard before live-readiness.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "watch_source": str(WATCH_JSON),
        "interpretation": interpretation,
        "lanes": lanes,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Soft-Frontier Mid-Price Delayed-Recheck Path Risk",
        "",
        "Research-only path-risk audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Suppressed rows: `{summary.get('suppressed_rows')}`",
                f"- Rows with post-recheck path: `{summary.get('rows_with_post_recheck_path')}`",
                f"- Weighted delta: `{fmt(summary.get('weighted_delta_cents'))}c`",
                f"- Avg min after exit bid: `{fmt(summary.get('avg_min_after_exit_bid_cents'))}c`",
                f"- Worst min after exit bid: `{fmt(summary.get('worst_min_after_exit_bid_cents'))}c`",
                f"- Avg min after recheck bid: `{fmt(summary.get('avg_min_after_recheck_bid_cents'))}c`",
                f"- Worst min after recheck bid: `{fmt(summary.get('worst_min_after_recheck_bid_cents'))}c`",
                f"- Adverse after recheck 10/25/50c rows: `{summary.get('adverse_recheck_10c_rows')} / {summary.get('adverse_recheck_25c_rows')} / {summary.get('adverse_recheck_50c_rows')}`",
                f"- Blockers: `{summary.get('blockers')}`",
                "",
                "| market | side | source | reason | exit bid | recheck bid | min bid after recheck | last bid | min-after exit c | min-after recheck c | delta c | pts |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in (lane.get("rows") or [])[:30]:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {row.get('exit_reason')} | "
                f"{fmt(row.get('exit_bid'))} | {fmt(row.get('recheck_bid'))} | "
                f"{fmt(row.get('min_bid_after_recheck'))} | {fmt(row.get('last_bid_after_recheck'))} | "
                f"{fmt(row.get('min_after_exit_bid_cents'))} | {fmt(row.get('min_after_recheck_bid_cents'))} | "
                f"{fmt(row.get('weighted_delta_cents'))} | {row.get('points_after_recheck')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
