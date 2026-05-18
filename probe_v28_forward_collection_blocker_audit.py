"""Forward-evidence collection blocker audit for v28 research.

Research-only; no live bot changes, no process control, no orders.

This separates strategy evidence blockers from the current ability to collect
fresh frozen/live rows. It only reads logs and research scorecards.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LIVE_LOG_DIR = ROOT / "logs" / "live_mushroom_v28_size2"
STATE_DIR = ROOT / "state"

HOURLY_MONITOR = LIVE_LOG_DIR / "hourly_monitor.log"
BOT_LOG = LIVE_LOG_DIR / "bot.log"
EXECUTION_EVENTS = LIVE_LOG_DIR / "execution_events.ndjson"
LIVE_LOCK = STATE_DIR / "live_trading.lock"

SHADOW_AVAILABILITY_JSON = OUT_DIR / "v28_shadow_observation_availability_latest.json"
EXIT_DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
CANDIDATE_VS_LIVE_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
GOAL_AUDIT_JSON = OUT_DIR / "v28_goal_completion_audit_latest.json"
SIDECAR_STATE_JSON = OUT_DIR / "v28_feature_gate_sidecar_live_state_audit_latest.json"

OUT_JSON = OUT_DIR / "v28_forward_collection_blocker_audit_latest.json"
OUT_MD = OUT_DIR / "v28_forward_collection_blocker_audit_latest.md"

ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:\+00:00|Z)?")
LOG_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
LOCAL_TZ = ZoneInfo("America/New_York")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def read_tail_lines(path: Path, max_lines: int = 200, chunk_size: int = 65536) -> list[str]:
    if not path.exists():
        return []
    with path.open("rb") as handle:
        handle.seek(0, 2)
        size = handle.tell()
        handle.seek(max(0, size - chunk_size))
        data = handle.read().decode("utf-8", errors="replace")
    return data.splitlines()[-max_lines:]


def parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def file_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path)}
    stat = path.stat()
    return {
        "exists": True,
        "path": str(path),
        "size_bytes": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


def latest_hourly_monitor() -> dict[str, Any]:
    lines = [line for line in read_tail_lines(HOURLY_MONITOR, 20) if line.strip()]
    latest = lines[-1] if lines else ""
    status = "unknown"
    if "| OK |" in latest:
        status = "OK"
    elif "| RESTART_FAILED |" in latest:
        status = "RESTART_FAILED"
    elif "| UNHEALTHY |" in latest:
        status = "UNHEALTHY"
    elif "| START requested |" in latest:
        status = "START_REQUESTED"
    return {
        "latest_line": latest,
        "latest_status": status,
        "tail": lines[-5:],
        "file": file_info(HOURLY_MONITOR),
    }


def latest_bot_heartbeat() -> dict[str, Any]:
    lines = read_tail_lines(BOT_LOG, 300)
    heartbeat = next((line for line in reversed(lines) if "Heartbeat |" in line), "")
    warning = next((line for line in reversed(lines) if "WARNING" in line or "ERROR" in line), "")
    ts = None
    if heartbeat:
        match = LOG_TS_RE.search(heartbeat)
        if match:
            local = datetime.fromisoformat(match.group(0).replace(" ", "T")).replace(tzinfo=LOCAL_TZ)
            ts = local.astimezone(timezone.utc)
    return {
        "latest_heartbeat_line": heartbeat,
        "latest_heartbeat_utc": ts.isoformat() if ts else None,
        "latest_warning_or_error": warning,
        "file": file_info(BOT_LOG),
    }


def latest_execution_event() -> dict[str, Any]:
    lines = [line for line in read_tail_lines(EXECUTION_EVENTS, 50) if line.strip()]
    latest_payload: dict[str, Any] = {}
    for line in reversed(lines):
        try:
            latest_payload = json.loads(line)
            break
        except json.JSONDecodeError:
            continue
    return {
        "latest_ts_wall": latest_payload.get("ts_wall"),
        "latest_event_type": latest_payload.get("event_type"),
        "latest_market": latest_payload.get("market"),
        "latest_side": latest_payload.get("side"),
        "latest_decision_reason": latest_payload.get("decision_reason"),
        "file": file_info(EXECUTION_EVENTS),
    }


def live_lock_status() -> dict[str, Any]:
    payload = load_json(LIVE_LOCK)
    return {
        "payload": payload,
        "file": file_info(LIVE_LOCK),
    }


def shadow_collection_summary() -> dict[str, Any]:
    data = load_json(SHADOW_AVAILABILITY_JSON)
    clocks = data.get("clocks") or []
    if not isinstance(clocks, list):
        clocks = []
    rows = [row for row in clocks if isinstance(row, dict)]
    status_counts = Counter(str(row.get("blocker") or "collecting") for row in rows)
    top_recent = sorted(rows, key=lambda row: str(row.get("freeze_ts_utc") or ""), reverse=True)[:8]
    return {
        "generated_utc": data.get("generated_utc"),
        "shadow_events": data.get("shadow_events"),
        "shadow_trades": data.get("shadow_trades"),
        "clock_count": len(rows),
        "status_counts": dict(status_counts.most_common()),
        "latest_freeze_clocks": [
            {
                "clock": row.get("clock"),
                "freeze_ts_utc": row.get("freeze_ts_utc"),
                "post_entry_trades": row.get("post_entry_trades"),
                "settled_post_exit_clock_trades": row.get("settled_post_exit_clock_trades"),
                "pending_post_exit_clock_trades": row.get("pending_post_exit_clock_trades"),
                "blocker": row.get("blocker"),
            }
            for row in top_recent
        ],
    }


def exit_watch_summary() -> dict[str, Any]:
    data = load_json(EXIT_DASHBOARD_JSON)
    rows = [row for row in (data.get("rows") or []) if isinstance(row, dict)]
    status_counts = data.get("status_counts") or Counter(str(row.get("status")) for row in rows)
    positive_under_review = [
        row for row in rows
        if row.get("status") in {"forward_positive_under_review", "positive_but_under_sample"}
    ]
    positive_under_review.sort(
        key=lambda row: (
            float(row.get("delta_vs_current_cents") or 0),
            int(row.get("suppressed_exits") or 0),
        ),
        reverse=True,
    )
    closest = []
    for row in positive_under_review[:10]:
        suppressed = int(row.get("suppressed_exits") or 0)
        delta = float(row.get("delta_vs_current_cents") or 0)
        closest.append({
            "lane": row.get("lane"),
            "candidate": row.get("candidate"),
            "status": row.get("status"),
            "settled": row.get("settled"),
            "suppressed_exits": suppressed,
            "suppressed_needed_for_30": max(0, 30 - suppressed),
            "delta_vs_current_cents": delta,
            "candidate_net_cents": row.get("candidate_net_cents"),
            "loss_control_cost_cents": row.get("loss_control_cost_cents"),
            "blockers": row.get("blockers"),
        })
    return {
        "generated_at_utc": data.get("generated_at_utc"),
        "status_counts": status_counts,
        "closest_positive_exit_watches": closest,
    }


def candidate_live_summary() -> dict[str, Any]:
    data = load_json(CANDIDATE_VS_LIVE_JSON)
    return {
        "generated_at_utc": data.get("generated_at_utc"),
        "live_net_cents": data.get("live_net_cents"),
        "candidate_count": data.get("candidate_count"),
        "positive_candidate_count": data.get("positive_candidate_count"),
        "target_coverage_positive_count": data.get("target_coverage_positive_count"),
        "live_ready_count": data.get("live_ready_count"),
    }


def build_report() -> dict[str, Any]:
    monitor = latest_hourly_monitor()
    heartbeat = latest_bot_heartbeat()
    events = latest_execution_event()
    lock = live_lock_status()
    shadow = shadow_collection_summary()
    exits = exit_watch_summary()
    live = candidate_live_summary()
    goal = load_json(GOAL_AUDIT_JSON)
    sidecar = load_json(SIDECAR_STATE_JSON)
    blockers = ["research_only"]
    lock_tag = ((lock.get("payload") or {}).get("strategy_tag") or "")
    if monitor.get("latest_status") == "RESTART_FAILED":
        blockers.append("live_watchdog_restart_failed")
    if "v28" not in str(lock_tag).lower():
        blockers.append("live_lock_not_v28")
    if not events.get("latest_ts_wall"):
        blockers.append("no_execution_event_timestamp")
    if (live.get("live_ready_count") or 0) == 0:
        blockers.append("no_live_ready_candidate_rows")
    if exits.get("closest_positive_exit_watches"):
        blockers.append("exit_watches_still_need_suppression_density_or_cushion")
    if sidecar:
        blockers.append("feature_gate_sidecar_evidence_separate_from_size2_baseline")
        if "no_order_like_events_seen" in (sidecar.get("blockers") or []):
            blockers.append("feature_gate_sidecar_no_order_like_events_seen")
        if "sidecar_live_trade_detected_while_readiness_false" in (sidecar.get("blockers") or []):
            blockers.append("feature_gate_sidecar_live_trade_detected_while_readiness_false")
        if any("RESTART_FAILED" in str(line) for line in sidecar.get("hourly_monitor_tail") or []):
            blockers.append("feature_gate_sidecar_watchdog_restart_failed")
    interpretation = [
        "Promotion remains blocked by strategy gates: no live-ready candidates and exit watches still need suppression density, cushion, or false-hold safety.",
        "Fresh frozen/live evidence collection is also operationally blocked if the latest watchdog status remains RESTART_FAILED.",
        "If a feature-gate size1 sidecar audit exists, keep it separate from the live_mushroom_v28_size2 baseline and do not treat it as candidate-vs-live promotion evidence.",
        "This report is a research status audit only; it does not restart, stop, or modify live trading.",
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "live_monitor": monitor,
        "bot_log": heartbeat,
        "execution_events": events,
        "live_lock": lock,
        "shadow_collection": shadow,
        "exit_watch_summary": exits,
        "candidate_vs_live_summary": live,
        "feature_gate_sidecar_state": sidecar,
        "goal_achieved": goal.get("achieved"),
        "blockers": blockers,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    live = report.get("candidate_vs_live_summary") or {}
    monitor = report.get("live_monitor") or {}
    bot = report.get("bot_log") or {}
    events = report.get("execution_events") or {}
    lock = report.get("live_lock") or {}
    shadow = report.get("shadow_collection") or {}
    exits = report.get("exit_watch_summary") or {}
    sidecar = report.get("feature_gate_sidecar_state") or {}
    sidecar_events = sidecar.get("execution_events") or {}
    sidecar_lock = sidecar.get("live_lock") or {}
    sidecar_process = sidecar.get("process") or {}
    sidecar_trade = sidecar.get("trade_summary") or {}
    lines = [
        "# v28 Forward Collection Blocker Audit",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Goal achieved: `{report.get('goal_achieved')}`",
        f"- Candidate-vs-live generated UTC/live net/live-ready: `{live.get('generated_at_utc')}` / `{live.get('live_net_cents')}c` / `{live.get('live_ready_count')}`",
        f"- Latest hourly monitor status: `{monitor.get('latest_status')}`",
        f"- Latest hourly monitor line: `{monitor.get('latest_line')}`",
        f"- Latest bot heartbeat UTC: `{bot.get('latest_heartbeat_utc')}`",
        f"- Latest execution event: `{events.get('latest_ts_wall')}` / `{events.get('latest_event_type')}` / `{events.get('latest_market')}`",
        f"- Live lock PID/tag: `{((lock.get('payload') or {}).get('pid'))}` / `{((lock.get('payload') or {}).get('strategy_tag'))}`",
        f"- Shadow availability generated UTC/events/trades/clocks: `{shadow.get('generated_utc')}` / `{shadow.get('shadow_events')}` / `{shadow.get('shadow_trades')}` / `{shadow.get('clock_count')}`",
        f"- Exit dashboard generated UTC/status counts: `{exits.get('generated_at_utc')}` / `{exits.get('status_counts')}`",
        f"- Feature-gate sidecar generated UTC/events/order-like/process: `{sidecar.get('generated_at_utc')}` / `{sidecar_events.get('event_counts')}` / `{sidecar_events.get('order_like_count')}` / `{sidecar_process.get('running')}`",
        f"- Feature-gate sidecar trade detected/round trips/net: `{sidecar_trade.get('sidecar_live_trade_detected')}` / `{sidecar_trade.get('completed_round_trips')}` / `{sidecar_trade.get('net_pnl_cents')}c`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Closest Positive Exit Watches",
        "",
        "| lane | status | settled | suppressed | need for 30 | delta | loss-control cost | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in exits.get("closest_positive_exit_watches") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('status')}` | {row.get('settled')} | "
            f"{row.get('suppressed_exits')} | {row.get('suppressed_needed_for_30')} | "
            f"{row.get('delta_vs_current_cents')}c | {row.get('loss_control_cost_cents')}c | "
            f"`{', '.join(row.get('blockers') or [])}` |"
        )
    lines.extend([
        "",
        "## Latest Frozen Clocks",
        "",
        "| clock | freeze UTC | post entries | settled exit rows | pending | blocker |",
        "|---|---|---:|---:|---:|---|",
    ])
    for row in shadow.get("latest_freeze_clocks") or []:
        lines.append(
            f"| `{row.get('clock')}` | `{row.get('freeze_ts_utc')}` | {row.get('post_entry_trades')} | "
            f"{row.get('settled_post_exit_clock_trades')} | {row.get('pending_post_exit_clock_trades')} | "
            f"`{row.get('blocker') or ''}` |"
        )
    if sidecar:
        lines.extend([
            "",
            "## Feature-Gate Size1 Sidecar",
            "",
            f"- Lock PID/tag: `{sidecar_lock.get('pid')}` / `{sidecar_lock.get('strategy_tag')}`",
            f"- Process running/name: `{sidecar_process.get('running')}` / `{sidecar_process.get('Name')}`",
            f"- Event counts: `{sidecar_events.get('event_counts')}`",
            f"- Order-like events: `{sidecar_events.get('order_like_count')}`",
            f"- Live trade detected/entry fills/exit fills: `{sidecar_trade.get('sidecar_live_trade_detected')}` / `{sidecar_trade.get('entry_fill_count')}` / `{sidecar_trade.get('exit_fill_count')}`",
            f"- Score entries/round trips/open/net: `{sidecar_trade.get('entries_total')}` / `{sidecar_trade.get('completed_round_trips')}` / `{sidecar_trade.get('open_positions')}` / `{sidecar_trade.get('net_pnl_cents')}c`",
            f"- Sidecar blockers: `{', '.join(sidecar.get('blockers') or [])}`",
            "- This sidecar state is live-state context only; it is not the size2 baseline and not promotion evidence.",
        ])
    lines.extend([
        "",
        "## Hourly Monitor Tail",
        "",
    ])
    for line in monitor.get("tail") or []:
        lines.append(f"- `{line}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
