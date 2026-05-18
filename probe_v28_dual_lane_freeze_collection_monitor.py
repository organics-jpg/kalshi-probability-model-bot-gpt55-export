"""Collection monitor for the v28 dual-lane own-freeze watch.

Research-only; no live bot changes and no orders.

The dual-lane overlap can only become live-ready from rows after its own
freeze timestamp. This monitor checks whether shadow observations are arriving
after that timestamp without replaying the heavy strategy surfaces.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_common_clock_watch import parse_ts, row_ts
from probe_v28_reactivated_shadow_status import read_events, reconstruct_trades, score_trade


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_dual_lane_own_freeze_watch_state.json"
OWN_FREEZE_JSON = OUT_DIR / "v28_dual_lane_own_freeze_watch_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_freeze_collection_monitor_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_freeze_collection_monitor_latest.md"

MIN_SETTLED = 30
MARKET_INTERVAL_MINUTES = 15
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


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


def freeze_ts() -> str | None:
    payload = load_json(STATE_JSON)
    ts = payload.get("freeze_ts_utc")
    return str(ts) if ts else None


def local_time_iso(value: str | None) -> str | None:
    parsed = parse_ts(value)
    if parsed is None:
        return None
    return parsed.astimezone().isoformat()


def event_ts(event: dict[str, Any]) -> datetime | None:
    return parse_ts(event.get("ts_wall") or event.get("timestamp") or event.get("ts"))


def is_settled(row: dict[str, Any]) -> bool:
    return row.get("hold_gross_cents") is not None and row.get("actual_gross_cents") is not None


def possible_market_windows_since(freeze: str | None) -> int:
    parsed = parse_ts(freeze)
    if parsed is None:
        return 0
    elapsed = max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds())
    return int(elapsed // (MARKET_INTERVAL_MINUTES * 60))


def earliest_min_sample_time(freeze: str | None) -> str | None:
    parsed = parse_ts(freeze)
    if parsed is None:
        return None
    return (parsed + timedelta(minutes=MIN_SETTLED * MARKET_INTERVAL_MINUTES)).isoformat()


def live_baseline_cents() -> float | None:
    payload = load_json(LIVE_SUMMARY_JSON)
    try:
        return 100.0 * float(payload.get("net_pnl_total_dollars"))
    except (TypeError, ValueError):
        return None


def cents(value: Any) -> str:
    if value is None:
        return ""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{amount:.0f}c (${amount / 100.0:.2f})"


def compact_trade(row: dict[str, Any]) -> dict[str, Any]:
    features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "status": row.get("status"),
        "result": row.get("result"),
        "actual_gross_cents": row.get("actual_gross_cents"),
        "hold_gross_cents": row.get("hold_gross_cents"),
        "exit_reason": features.get("mushroom_v28_exit_reason") or row.get("exit_reason"),
    }


def build_report() -> dict[str, Any]:
    freeze = freeze_ts()
    freeze_dt = parse_ts(freeze)
    possible_windows = possible_market_windows_since(freeze)
    events = read_events()
    trades = [score_trade(trade) for trade in reconstruct_trades(events)]
    if freeze_dt is None:
        post_events: list[dict[str, Any]] = []
        post_entry_rows: list[dict[str, Any]] = []
        post_exit_rows: list[dict[str, Any]] = []
        blocker = "freeze_ts_missing_or_invalid"
    else:
        post_events = [event for event in events if (ts := event_ts(event)) is not None and ts >= freeze_dt]
        post_entry_rows = [
            row for row in trades if (ts := parse_ts(row.get("entry_ts"))) is not None and ts >= freeze_dt
        ]
        post_exit_rows = [
            row for row in trades if (ts := row_ts(row)) is not None and ts >= freeze_dt
        ]
        if possible_windows < MIN_SETTLED:
            blocker = "waiting_for_min_30_market_windows"
        elif not post_events:
            blocker = "no_post_freeze_shadow_events"
        elif not post_entry_rows:
            blocker = "post_freeze_events_without_reconstructed_trades"
        elif not any(is_settled(row) for row in post_exit_rows):
            blocker = "post_freeze_rows_not_settled_yet"
        else:
            blocker = None

    settled_entry = [row for row in post_entry_rows if is_settled(row)]
    settled_exit = [row for row in post_exit_rows if is_settled(row)]
    pending_exit = [row for row in post_exit_rows if not is_settled(row)]
    market_count = len({str(row.get("market") or "") for row in post_entry_rows if row.get("market")})
    event_counts = Counter(str(event.get("event_type") or "<blank>") for event in post_events)
    status_counts = Counter(str(row.get("status") or "<blank>") for row in post_exit_rows)

    own_freeze = load_json(OWN_FREEZE_JSON)
    own_unions = own_freeze.get("unions") if isinstance(own_freeze.get("unions"), list) else []
    own_union_compact = []
    for row in own_unions:
        summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
        own_union_compact.append(
            {
                "policy": ((row.get("sidecar") or {}).get("policy") if isinstance(row.get("sidecar"), dict) else None),
                "settled": summary.get("settled"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents": summary.get("net_cents"),
                "reconstructed_share": summary.get("reconstructed_share"),
                "full_loss_cushion": summary.get("full_loss_cushion"),
                "live_ready": row.get("live_ready"),
                "blockers": row.get("blockers") or [],
            }
        )

    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze,
        "freeze_local_time": local_time_iso(freeze),
        "live_baseline_cents": live_baseline_cents(),
        "requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_min_pct": TARGET_COVERAGE_MIN,
            "coverage_max_pct": TARGET_COVERAGE_MAX,
            "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
        },
        "sample_clock": {
            "possible_market_windows_since_freeze": possible_windows,
            "windows_remaining_to_min_sample": max(0, MIN_SETTLED - possible_windows),
            "earliest_min_sample_utc": earliest_min_sample_time(freeze),
            "earliest_min_sample_local_time": local_time_iso(earliest_min_sample_time(freeze)),
        },
        "shadow_collection": {
            "total_events": len(events),
            "post_freeze_events": len(post_events),
            "post_freeze_event_counts": dict(sorted(event_counts.items())),
            "reconstructed_trades_total": len(trades),
            "post_freeze_entry_rows": len(post_entry_rows),
            "post_freeze_distinct_markets": market_count,
            "post_freeze_exit_clock_rows": len(post_exit_rows),
            "settled_post_entry_rows": len(settled_entry),
            "settled_post_exit_clock_rows": len(settled_exit),
            "pending_post_exit_clock_rows": len(pending_exit),
            "status_counts": dict(sorted(status_counts.items())),
            "recent_post_freeze_rows": [compact_trade(row) for row in post_exit_rows[-12:]],
        },
        "own_freeze_unions": own_union_compact,
        "blocker": blocker,
        "interpretation": [
            "This is a collection monitor, not a strategy scorecard.",
            "The own-freeze scorecard remains authoritative for live readiness.",
            "A waiting-for-min-window blocker means evidence cannot be mature yet, even if shadow events are arriving.",
        ],
    }


def write_report(report: dict[str, Any]) -> None:
    clock = report.get("sample_clock") or {}
    collection = report.get("shadow_collection") or {}
    lines = [
        "# v28 Dual-Lane Freeze Collection Monitor",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Freeze local time: `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{cents(report.get('live_baseline_cents'))}`",
        f"- Blocker: `{report.get('blocker') or 'none'}`",
        "",
        "## Sample Clock",
        "",
        f"- Possible 15m windows since freeze: `{clock.get('possible_market_windows_since_freeze')}`",
        f"- Windows remaining to 30-row gate: `{clock.get('windows_remaining_to_min_sample')}`",
        f"- Earliest possible 30-window sample UTC: `{clock.get('earliest_min_sample_utc')}`",
        f"- Earliest possible 30-window sample local time: `{clock.get('earliest_min_sample_local_time')}`",
        "",
        "## Shadow Collection",
        "",
        f"- Total shadow events: `{collection.get('total_events')}`",
        f"- Post-freeze shadow events: `{collection.get('post_freeze_events')}`",
        f"- Post-freeze reconstructed entry rows: `{collection.get('post_freeze_entry_rows')}`",
        f"- Post-freeze distinct markets: `{collection.get('post_freeze_distinct_markets')}`",
        f"- Post-freeze exit-clock rows: `{collection.get('post_freeze_exit_clock_rows')}`",
        f"- Settled post-freeze exit-clock rows: `{collection.get('settled_post_exit_clock_rows')}`",
        f"- Pending post-freeze exit-clock rows: `{collection.get('pending_post_exit_clock_rows')}`",
        "",
        "## Own-Freeze Score Snapshot",
        "",
        "| policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report.get("own_freeze_unions") or []:
        recon = row.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * float(recon):.2f}%"
        lines.append(
            f"| `{row.get('policy')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{row.get('coverage_pct')}% | {cents(row.get('net_cents'))} | {recon_text} | "
            f"{row.get('full_loss_cushion')} | `{row.get('live_ready')}` | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Recent Post-Freeze Rows",
            "",
            "| market | side | entry UTC | exit UTC | status | result | actual | hold | exit reason |",
            "|---|---|---|---|---|---|---:|---:|---|",
        ]
    )
    for row in collection.get("recent_post_freeze_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | `{row.get('entry_ts')}` | `{row.get('exit_ts')}` | "
            f"{row.get('status')} | {row.get('result')} | {cents(row.get('actual_gross_cents'))} | "
            f"{cents(row.get('hold_gross_cents'))} | {row.get('exit_reason')} |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
