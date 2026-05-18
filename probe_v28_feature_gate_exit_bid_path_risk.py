"""Path-risk audit for feature-gate high-exit-bid suppression.

Research-only; no live bot changes or orders.

The high-exit-bid suppression watch is very strong diagnostically, but it uses
a hold-to-settlement counterfactual. This probe measures the observed post-exit
heartbeat path after those suppressed exits so we can separate easy winner
clips from holds that require surviving large adverse marks.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from probe_v28_post_exit_path import btc15m_close_time_from_ticker, held_bid, read_heartbeats


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
WATCH_JSON = OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_exit_bid_path_risk_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_exit_bid_path_risk_latest.md"
EASTERN = ZoneInfo("America/New_York")


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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_utc(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_eastern_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.astimezone(EASTERN).replace(tzinfo=None)


def suppressed_watch_rows(lane_name: str) -> list[dict[str, Any]]:
    payload = load_json(WATCH_JSON)
    for lane in payload.get("lanes") or []:
        if lane.get("lane") == lane_name:
            rows = lane.get("rows") or []
            return [row for row in rows if isinstance(row, dict) and row.get("suppressed")]
    return []


def path_for_row(row: dict[str, Any], heartbeats: list[dict[str, Any]]) -> dict[str, Any]:
    market = str(row.get("market") or "")
    side = str(row.get("side") or "")
    exit_ts_utc = parse_utc(row.get("first_exit_ts_utc"))
    exit_ts = to_eastern_naive(exit_ts_utc)
    close_utc = btc15m_close_time_from_ticker(market)
    close_ts = to_eastern_naive(close_utc)
    future = [
        hb for hb in heartbeats
        if hb["market"] == market
        and exit_ts is not None
        and hb["ts"] >= exit_ts
        and (close_ts is None or hb["ts"] < close_ts)
    ]
    bids = [held_bid(hb, side) for hb in future]
    exit_bid = fnum(row.get("exit_bid_min"), None)
    min_bid = min(bids) if bids else None
    max_bid = max(bids) if bids else None
    last_bid = bids[-1] if bids else None
    min_after = None if min_bid is None or exit_bid is None else float(min_bid) - float(exit_bid)
    max_after = None if max_bid is None or exit_bid is None else float(max_bid) - float(exit_bid)
    adverse_10 = min_after is not None and min_after <= -10.0
    adverse_25 = min_after is not None and min_after <= -25.0
    adverse_50 = min_after is not None and min_after <= -50.0
    return {
        "market": market,
        "source": row.get("source"),
        "side": side,
        "side_won": row.get("side_won"),
        "first_exit_ts_utc": row.get("first_exit_ts_utc"),
        "exit_bid_min": row.get("exit_bid_min"),
        "exit_p_hold_avg": row.get("exit_p_hold_avg"),
        "live_selected_net_cents": row.get("live_selected_net_cents"),
        "hold_to_settlement_net_cents": row.get("hold_to_settlement_net_cents"),
        "delta_vs_live_cents": row.get("delta_vs_live_cents"),
        "post_exit_points": len(future),
        "min_post_exit_bid": min_bid,
        "max_post_exit_bid": max_bid,
        "last_post_exit_bid": last_bid,
        "min_after_exit_bid_cents": min_after,
        "max_after_exit_bid_cents": max_after,
        "adverse_10c": adverse_10,
        "adverse_25c": adverse_25,
        "adverse_50c": adverse_50,
        "exit_reason_counts": row.get("exit_reason_counts"),
    }


def summarize(rows: list[dict[str, Any]], strict_forward: bool) -> dict[str, Any]:
    with_path = [row for row in rows if row.get("post_exit_points")]
    adverse_10 = [row for row in with_path if row.get("adverse_10c")]
    adverse_25 = [row for row in with_path if row.get("adverse_25c")]
    adverse_50 = [row for row in with_path if row.get("adverse_50c")]
    min_values = [fnum(row.get("min_after_exit_bid_cents")) for row in with_path if row.get("min_after_exit_bid_cents") is not None]
    delta = sum(fnum(row.get("delta_vs_live_cents")) for row in rows)
    blockers = []
    if strict_forward:
        blockers.append("post_birth_rows_required")
    if len(rows) < 30:
        blockers.append("suppressed_rows_lt_30")
    if adverse_25:
        blockers.append("large_adverse_marks_present")
    return {
        "suppressed_rows": len(rows),
        "rows_with_post_exit_path": len(with_path),
        "delta_vs_live_cents": delta,
        "helpful_rows": sum(1 for row in rows if fnum(row.get("delta_vs_live_cents")) > 0),
        "harmful_rows": sum(1 for row in rows if fnum(row.get("delta_vs_live_cents")) < 0),
        "avg_min_after_exit_bid_cents": (sum(min_values) / len(min_values)) if min_values else None,
        "worst_min_after_exit_bid_cents": min(min_values) if min_values else None,
        "adverse_10c_rows": len(adverse_10),
        "adverse_25c_rows": len(adverse_25),
        "adverse_50c_rows": len(adverse_50),
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    heartbeats = read_heartbeats()
    lanes = []
    for lane_name, strict_forward in [
        ("diagnostic_feature_gate_exit_bid", False),
        ("post_exit_bid_birth", True),
    ]:
        rows = [path_for_row(row, heartbeats) for row in suppressed_watch_rows(lane_name)]
        rows.sort(key=lambda row: fnum(row.get("min_after_exit_bid_cents")), reverse=False)
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
            f"Diagnostic suppressed rows with path: {diagnostic.get('rows_with_post_exit_path')}/"
            f"{diagnostic.get('suppressed_rows')}; worst post-exit bid excursion "
            f"{diagnostic.get('worst_min_after_exit_bid_cents')}c versus exit bid."
        ),
        (
            "High exit-bid suppression remains a watch-only exit repair. Large adverse marks would require "
            "a deployable disaster guard or delayed-recheck rule before any live-readiness discussion."
        ),
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
        "# v28 Feature-Gate Exit-Bid Path Risk",
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
                f"- Rows with post-exit path: `{summary.get('rows_with_post_exit_path')}`",
                f"- Delta vs live: `{fmt(summary.get('delta_vs_live_cents'))}c`",
                f"- Avg min after exit bid: `{fmt(summary.get('avg_min_after_exit_bid_cents'))}c`",
                f"- Worst min after exit bid: `{fmt(summary.get('worst_min_after_exit_bid_cents'))}c`",
                f"- Adverse 10/25/50c rows: `{summary.get('adverse_10c_rows')} / {summary.get('adverse_25c_rows')} / {summary.get('adverse_50c_rows')}`",
                f"- Blockers: `{summary.get('blockers')}`",
                "",
                "| market | side | won | exit bid | min bid | max bid | last bid | min-after c | max-after c | delta live c | path pts | reasons |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in (lane.get("rows") or [])[:30]:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('exit_bid_min'))} | {fmt(row.get('min_post_exit_bid'))} | "
                f"{fmt(row.get('max_post_exit_bid'))} | {fmt(row.get('last_post_exit_bid'))} | "
                f"{fmt(row.get('min_after_exit_bid_cents'))} | {fmt(row.get('max_after_exit_bid_cents'))} | "
                f"{fmt(row.get('delta_vs_live_cents'))} | {row.get('post_exit_points')} | {row.get('exit_reason_counts')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
