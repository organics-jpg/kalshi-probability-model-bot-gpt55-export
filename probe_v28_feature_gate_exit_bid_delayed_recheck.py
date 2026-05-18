"""Delayed-recheck frontier for feature-gate high-exit-bid suppression.

Research-only; no live bot changes or orders.

The raw high-exit-bid suppression recovers clipped winners but can require
holding through large adverse marks. This diagnostic tests a deployable shape:
after an exit signal, delay briefly and only suppress the exit if the held-side
bid still looks supported and did not immediately air-pocket.
"""
from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from probe_v28_feature_gate_exit_bid_path_risk import (
    OUT_DIR,
    WATCH_JSON,
    fnum,
    load_json,
    parse_utc,
    to_eastern_naive,
    utc_now_iso,
)
from probe_v28_post_exit_path import btc15m_close_time_from_ticker, held_bid, read_heartbeats


OUT_JSON = OUT_DIR / "v28_feature_gate_exit_bid_delayed_recheck_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_exit_bid_delayed_recheck_latest.md"

VARIANTS = [
    {"name": "delay30_bid_ge60", "delay_seconds": 30, "bid_floor": 60, "max_drop": None},
    {"name": "delay60_bid_ge60", "delay_seconds": 60, "bid_floor": 60, "max_drop": None},
    {"name": "delay120_bid_ge60", "delay_seconds": 120, "bid_floor": 60, "max_drop": None},
    {"name": "delay30_bid_ge60_drop_lte10", "delay_seconds": 30, "bid_floor": 60, "max_drop": 10},
    {"name": "delay60_bid_ge60_drop_lte10", "delay_seconds": 60, "bid_floor": 60, "max_drop": 10},
    {"name": "delay120_bid_ge60_drop_lte10", "delay_seconds": 120, "bid_floor": 60, "max_drop": 10},
    {"name": "delay60_bid_ge65_drop_lte10", "delay_seconds": 60, "bid_floor": 65, "max_drop": 10},
    {"name": "delay60_bid_ge70_drop_lte10", "delay_seconds": 60, "bid_floor": 70, "max_drop": 10},
    {"name": "delay60_bid_ge60_drop_lte20", "delay_seconds": 60, "bid_floor": 60, "max_drop": 20},
]


def suppressed_watch_rows(lane_name: str = "diagnostic_feature_gate_exit_bid") -> list[dict[str, Any]]:
    payload = load_json(WATCH_JSON)
    for lane in payload.get("lanes") or []:
        if lane.get("lane") == lane_name:
            return [
                row for row in (lane.get("rows") or [])
                if isinstance(row, dict) and row.get("suppressed")
            ]
    return []


def path_points(row: dict[str, Any], heartbeats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    market = str(row.get("market") or "")
    side = str(row.get("side") or "")
    exit_ts = to_eastern_naive(parse_utc(row.get("first_exit_ts_utc")))
    close_ts = to_eastern_naive(btc15m_close_time_from_ticker(market))
    points = [
        {**hb, "held_bid": held_bid(hb, side)}
        for hb in heartbeats
        if hb["market"] == market
        and exit_ts is not None
        and hb["ts"] >= exit_ts
        and (close_ts is None or hb["ts"] < close_ts)
    ]
    points.sort(key=lambda item: item["ts"])
    return points


def evaluate_row(row: dict[str, Any], points: list[dict[str, Any]], variant: dict[str, Any]) -> dict[str, Any]:
    exit_ts = to_eastern_naive(parse_utc(row.get("first_exit_ts_utc")))
    if exit_ts is None:
        recheck = None
        window = []
    else:
        recheck_ts = exit_ts + timedelta(seconds=int(variant["delay_seconds"]))
        recheck = next((point for point in points if point["ts"] >= recheck_ts), None)
        window = [point for point in points if point["ts"] <= recheck_ts]
    exit_bid = fnum(row.get("exit_bid_min"))
    recheck_bid = None if recheck is None else fnum(recheck.get("held_bid"))
    min_window_bid = min([fnum(point.get("held_bid")) for point in window], default=None)
    drop = None if min_window_bid is None else exit_bid - min_window_bid
    bid_pass = recheck_bid is not None and recheck_bid >= fnum(variant.get("bid_floor"))
    max_drop = variant.get("max_drop")
    drop_pass = max_drop is None or (drop is not None and drop <= fnum(max_drop))
    suppress = bool(bid_pass and drop_pass)
    live = fnum(row.get("live_selected_net_cents"))
    hold = fnum(row.get("hold_to_settlement_net_cents"))
    candidate = hold if suppress else live
    out = dict(row)
    out.update(
        {
            "variant": variant["name"],
            "recheck_bid": recheck_bid,
            "min_window_bid": min_window_bid,
            "window_drop_cents": drop,
            "delayed_recheck_suppressed": suppress,
            "delayed_recheck_candidate_cents": candidate,
            "delayed_recheck_delta_cents": candidate - live,
            "recheck_missing": recheck is None,
        }
    )
    return out


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    suppressed = [row for row in rows if row.get("delayed_recheck_suppressed")]
    helpful = [row for row in suppressed if fnum(row.get("delayed_recheck_delta_cents")) > 0]
    harmful = [row for row in suppressed if fnum(row.get("delayed_recheck_delta_cents")) < 0]
    candidate_net = sum(fnum(row.get("delayed_recheck_candidate_cents")) for row in rows)
    live_net = sum(fnum(row.get("live_selected_net_cents")) for row in rows)
    blockers = []
    if len(rows) < 30:
        blockers.append("diagnostic_rows_lt_30")
    if len(suppressed) < 30:
        blockers.append("suppressed_decisions_lt_30")
    if harmful:
        blockers.append("suppressed_losers_present")
    if candidate_net <= 0:
        blockers.append("net_not_positive")
    if candidate_net < 300:
        blockers.append("full_loss_cushion_lt_3")
    blockers.append("diagnostic_prefreeze")
    return {
        "rows": len(rows),
        "suppressed": len(suppressed),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "live_net_cents": live_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_live_cents": candidate_net - live_net,
        "suppression_recovery_cents": sum(fnum(row.get("delayed_recheck_delta_cents")) for row in helpful),
        "suppression_loss_cost_cents": sum(fnum(row.get("delayed_recheck_delta_cents")) for row in harmful),
        "recheck_missing_rows": sum(1 for row in rows if row.get("recheck_missing")),
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    heartbeats = read_heartbeats()
    base_rows = suppressed_watch_rows()
    paths = {str(row.get("market")) + "::" + str(row.get("side")) + "::" + str(row.get("first_exit_ts_utc")): path_points(row, heartbeats) for row in base_rows}
    variants = []
    for variant in VARIANTS:
        rows = [
            evaluate_row(
                row,
                paths.get(str(row.get("market")) + "::" + str(row.get("side")) + "::" + str(row.get("first_exit_ts_utc")), []),
                variant,
            )
            for row in base_rows
        ]
        variants.append({"variant": variant, "summary": summarize(rows), "rows": rows})
    variants.sort(key=lambda item: fnum((item.get("summary") or {}).get("candidate_net_cents")), reverse=True)
    best = variants[0] if variants else {}
    interpretation = [
        "Research-only delayed-recheck frontier; no live bot changes or orders.",
        (
            f"Best diagnostic variant {((best.get('variant') or {}).get('name'))} has "
            f"{((best.get('summary') or {}).get('suppressed'))} suppressions and "
            f"{((best.get('summary') or {}).get('candidate_net_cents'))}c candidate net."
        ),
        "All rows are pre-freeze diagnostic; a frozen child would need its own post-birth evidence.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "watch_source": str(WATCH_JSON),
        "interpretation": interpretation,
        "variants": variants,
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
        "# v28 Feature-Gate Exit-Bid Delayed Recheck",
        "",
        "Research-only diagnostic frontier. No live bot changes or orders.",
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
            "## Variants",
            "",
            "| variant | delay | bid floor | max drop | rows | suppressed | sup H/H | live c | candidate c | delta c | recovery c | loss cost c | missing | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for item in report.get("variants") or []:
        variant = item.get("variant") or {}
        summary = item.get("summary") or {}
        lines.append(
            f"| `{variant.get('name')}` | {variant.get('delay_seconds')} | {variant.get('bid_floor')} | "
            f"{variant.get('max_drop')} | {summary.get('rows')} | {summary.get('suppressed')} | "
            f"{summary.get('helpful_suppressed')}/{summary.get('harmful_suppressed')} | "
            f"{fmt(summary.get('live_net_cents'))} | {fmt(summary.get('candidate_net_cents'))} | "
            f"{fmt(summary.get('delta_vs_live_cents'))} | {fmt(summary.get('suppression_recovery_cents'))} | "
            f"{fmt(summary.get('suppression_loss_cost_cents'))} | {summary.get('recheck_missing_rows')} | "
            f"{', '.join(summary.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
