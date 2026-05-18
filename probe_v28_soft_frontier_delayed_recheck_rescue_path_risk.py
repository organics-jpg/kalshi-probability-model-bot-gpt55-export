"""Path-risk audit for the best delayed-recheck rescue relax.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from datetime import timedelta
from typing import Any

from probe_v28_feature_gate_exit_bid_path_risk import OUT_DIR, fnum, load_json, parse_utc, to_eastern_naive, utc_now_iso
from probe_v28_post_exit_path import btc15m_close_time_from_ticker, held_bid, read_heartbeats


FRONTIER_JSON = OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_frontier_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_path_risk_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_path_risk_latest.md"
PRIMARY_VARIANT = "drop15_bid60"


def variant_rows() -> list[dict[str, Any]]:
    payload = load_json(FRONTIER_JSON)
    for item in payload.get("variants") or []:
        if (item.get("variant") or {}).get("name") == PRIMARY_VARIANT:
            return [
                row for row in item.get("scored_rows") or []
                if isinstance(row, dict) and row.get("frontier_suppressed")
            ]
    return []


def path_for_row(row: dict[str, Any], heartbeats: list[dict[str, Any]]) -> dict[str, Any]:
    market = str(row.get("market") or "")
    side = str(row.get("side") or "")
    exit_ts = to_eastern_naive(parse_utc(row.get("exit_ts")))
    recheck_ts = None if exit_ts is None else exit_ts + timedelta(seconds=60)
    close_ts = to_eastern_naive(btc15m_close_time_from_ticker(market))
    points = [
        {**hb, "held_bid": held_bid(hb, side)}
        for hb in heartbeats
        if hb["market"] == market
        and exit_ts is not None
        and hb["ts"] >= exit_ts
        and (close_ts is None or hb["ts"] < close_ts)
    ]
    after_recheck = [point for point in points if recheck_ts is not None and point["ts"] >= recheck_ts]
    exit_bid = fnum(row.get("exit_bid"), None)
    recheck_bid = fnum(row.get("recheck_bid"), None)
    bids = [fnum(point.get("held_bid")) for point in points]
    recheck_bids = [fnum(point.get("held_bid")) for point in after_recheck]
    min_after_exit = None if not bids or exit_bid is None else min(bids) - exit_bid
    min_after_recheck = None if not recheck_bids or recheck_bid is None else min(recheck_bids) - recheck_bid
    return {
        "market": market,
        "side": side,
        "source": row.get("source"),
        "exit_reason": row.get("exit_reason"),
        "exit_bid": exit_bid,
        "recheck_bid": recheck_bid,
        "window_drop_cents": row.get("window_drop_cents"),
        "weighted_delta_cents": row.get("frontier_weighted_delta_cents"),
        "points_after_recheck": len(after_recheck),
        "min_bid_after_recheck": min(recheck_bids) if recheck_bids else None,
        "last_bid_after_recheck": recheck_bids[-1] if recheck_bids else None,
        "min_after_exit_bid_cents": min_after_exit,
        "min_after_recheck_bid_cents": min_after_recheck,
        "adverse_recheck_10c": min_after_recheck is not None and min_after_recheck <= -10.0,
        "adverse_recheck_25c": min_after_recheck is not None and min_after_recheck <= -25.0,
        "adverse_recheck_50c": min_after_recheck is not None and min_after_recheck <= -50.0,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    with_path = [row for row in rows if row.get("points_after_recheck")]
    min_exit = [fnum(row.get("min_after_exit_bid_cents")) for row in with_path if row.get("min_after_exit_bid_cents") is not None]
    min_recheck = [fnum(row.get("min_after_recheck_bid_cents")) for row in with_path if row.get("min_after_recheck_bid_cents") is not None]
    blockers = []
    if len(rows) < 30:
        blockers.append("suppressed_rows_lt_30")
    if any(row.get("adverse_recheck_25c") for row in with_path):
        blockers.append("large_post_recheck_adverse_marks_present")
    return {
        "variant": PRIMARY_VARIANT,
        "suppressed_rows": len(rows),
        "rows_with_post_recheck_path": len(with_path),
        "weighted_delta_cents": sum(fnum(row.get("weighted_delta_cents")) for row in rows),
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
    rows = [path_for_row(row, read_heartbeats()) for row in variant_rows()]
    rows.sort(key=lambda row: fnum(row.get("min_after_recheck_bid_cents"), 999.0))
    summary = summarize(rows)
    return {
        "generated_at_utc": utc_now_iso(),
        "frontier_source": str(FRONTIER_JSON),
        "summary": summary,
        "rows": rows,
        "interpretation": [
            "Research-only path-risk audit; no live bot changes or orders.",
            (
                f"{PRIMARY_VARIANT} has {summary.get('suppressed_rows')} suppressed rows, "
                f"worst post-recheck excursion {summary.get('worst_min_after_recheck_bid_cents')}c, "
                f"adverse 10/25/50 rows {summary.get('adverse_recheck_10c_rows')}/"
                f"{summary.get('adverse_recheck_25c_rows')}/{summary.get('adverse_recheck_50c_rows')}."
            ),
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Soft-Frontier Delayed-Recheck Rescue Path Risk",
        "",
        "Research-only path-risk audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
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
            f"- Variant: `{summary.get('variant')}`",
            f"- Suppressed rows: `{summary.get('suppressed_rows')}`",
            f"- Helpful/harmful rows: `{summary.get('helpful_rows')}/{summary.get('harmful_rows')}`",
            f"- Weighted delta: `{fmt(summary.get('weighted_delta_cents'))}c`",
            f"- Worst min after exit bid: `{fmt(summary.get('worst_min_after_exit_bid_cents'))}c`",
            f"- Worst min after recheck bid: `{fmt(summary.get('worst_min_after_recheck_bid_cents'))}c`",
            f"- Adverse after recheck 10/25/50c rows: `{summary.get('adverse_recheck_10c_rows')} / {summary.get('adverse_recheck_25c_rows')} / {summary.get('adverse_recheck_50c_rows')}`",
            f"- Blockers: `{summary.get('blockers')}`",
            "",
            "## Worst Rows",
            "",
            "| market | side | source | reason | exit bid | recheck bid | drop | min bid post-recheck | last bid | min-after recheck c | delta c |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in (report.get("rows") or [])[:30]:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('exit_bid'))} | {fmt(row.get('recheck_bid'))} | {fmt(row.get('window_drop_cents'))} | "
            f"{fmt(row.get('min_bid_after_recheck'))} | {fmt(row.get('last_bid_after_recheck'))} | "
            f"{fmt(row.get('min_after_recheck_bid_cents'))} | {fmt(row.get('weighted_delta_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
