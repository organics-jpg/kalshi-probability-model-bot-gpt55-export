"""Read-only state audit for the v28 feature-gate size1 live sidecar.

Research-only; no live bot changes, no process control, no orders.

This exists because the sidecar can share the global live lock while the
research scorecards still use the live_mushroom_v28_size2 baseline. Keep the
sidecar evidence explicit so candidate-vs-live comparisons do not drift.
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STORAGE_BY_STRATEGY_TAG = {
    "mushroom_v28_feature_gate_raw05_recross60_abs085_size1_live": "live_mushroom_v28_feature_gate_size1",
    "mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live": "live_mushroom_v28_feature_gate_ask65_size1",
}
KNOWN_VARIANTS = [
    {
        "label": "raw05_recross60_abs085_no_ask_floor",
        "strategy_tag": "mushroom_v28_feature_gate_raw05_recross60_abs085_size1_live",
        "storage_tag": "live_mushroom_v28_feature_gate_size1",
    },
    {
        "label": "raw05_recross60_abs085_ask65",
        "strategy_tag": "mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live",
        "storage_tag": "live_mushroom_v28_feature_gate_ask65_size1",
    },
]
LIVE_LOCK = ROOT / "state" / "live_trading.lock"
LIVE_READINESS = OUT_DIR / "v28_live_trade_readiness_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_sidecar_live_state_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_sidecar_live_state_audit_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def tail_lines(path: Path, limit: int = 12) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]


def process_info(pid: Any) -> dict[str, Any]:
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return {}
    command = (
        "$p = Get-CimInstance Win32_Process | "
        f"Where-Object {{ $_.ProcessId -eq {pid_int} }} | "
        "Select-Object ProcessId,ParentProcessId,Name,CommandLine; "
        "$p | ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return {"pid": pid_int, "running": False, "error": result.stderr.strip()}
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"pid": pid_int, "running": False, "raw": result.stdout.strip()}
    if not isinstance(payload, dict):
        return {"pid": pid_int, "running": False}
    payload["running"] = True
    return payload


def dollars_to_cents(value: Any) -> int | None:
    try:
        return int(round(float(value) * 100))
    except (TypeError, ValueError):
        return None


def paths_for_variant(strategy_tag: str, storage_tag: str) -> dict[str, Path]:
    return {
        "log_dir": ROOT / "logs" / storage_tag,
        "stats": ROOT / "stats" / strategy_tag / "summary.json",
    }


def event_summary(path: Path) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    order_like: list[dict[str, Any]] = []
    fill_events: list[dict[str, Any]] = []
    entry_fill_events: list[dict[str, Any]] = []
    exit_fill_events: list[dict[str, Any]] = []
    recent: list[dict[str, Any]] = []
    if not path.exists():
        return {
            "present": False,
            "event_counts": {},
            "order_like_count": 0,
            "fill_full_count": 0,
            "entry_fill_count": 0,
            "exit_fill_count": 0,
        }
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_type = str(row.get("event_type") or "")
        counts[event_type] += 1
        compact = {
            "ts_wall": row.get("ts_wall"),
            "event_type": event_type,
            "market": row.get("market"),
            "side": row.get("side"),
            "decision_reason": row.get("decision_reason"),
            "actual_fill_price_cents": row.get("actual_fill_price_cents"),
            "fill_count": row.get("fill_count"),
            "order_id": row.get("order_id"),
            "client_order_id": row.get("client_order_id"),
            "result": row.get("result"),
            "exchange_status": row.get("exchange_status"),
            "top_of_book_limit_cents": row.get("top_of_book_limit_cents"),
            "trigger_price_cents": row.get("trigger_price_cents"),
            "position_size": row.get("position_size"),
            "remaining_position_size": row.get("remaining_position_size"),
            "mushroom_v28_p_side": row.get("mushroom_v28_p_side"),
            "mushroom_v28_feature_gate_pass": row.get("mushroom_v28_feature_gate_pass"),
            "mushroom_v28_exit_reason": row.get("mushroom_v28_exit_reason"),
        }
        recent.append(compact)
        if any(token in event_type for token in ("order", "fill", "submit", "accepted", "reconciled")):
            order_like.append(compact)
        if event_type == "fill_full":
            fill_events.append(compact)
            client_id = str(row.get("client_order_id") or "")
            if "exit" in client_id or "exit" in str(row.get("decision_reason") or ""):
                exit_fill_events.append(compact)
            elif "entry" in client_id:
                entry_fill_events.append(compact)
    return {
        "present": True,
        "event_counts": dict(counts.most_common()),
        "order_like_count": len(order_like),
        "fill_full_count": len(fill_events),
        "entry_fill_count": len(entry_fill_events),
        "exit_fill_count": len(exit_fill_events),
        "first_fill_event": fill_events[0] if fill_events else None,
        "last_fill_event": fill_events[-1] if fill_events else None,
        "first_entry_fill_event": entry_fill_events[0] if entry_fill_events else None,
        "last_exit_fill_event": exit_fill_events[-1] if exit_fill_events else None,
        "recent_events": recent[-8:],
        "recent_order_like_events": order_like[-8:],
    }


def variant_summary(variant: dict[str, str]) -> dict[str, Any]:
    strategy_tag = variant["strategy_tag"]
    storage_tag = variant["storage_tag"]
    paths = paths_for_variant(strategy_tag, storage_tag)
    stats = load_json(paths["stats"])
    events = event_summary(paths["log_dir"] / "execution_events.ndjson")
    completed_round_trips = int(stats.get("completed_round_trips") or 0)
    live_trade_detected = (
        int(events.get("entry_fill_count") or 0) > 0
        or completed_round_trips > 0
        or int(stats.get("entries_total") or 0) > 0
    )
    return {
        "label": variant["label"],
        "strategy_tag": strategy_tag,
        "storage_tag": storage_tag,
        "log_dir": str(paths["log_dir"]),
        "stats_path": str(paths["stats"]),
        "event_counts": events.get("event_counts") or {},
        "order_like_count": events.get("order_like_count"),
        "entry_fill_count": events.get("entry_fill_count"),
        "exit_fill_count": events.get("exit_fill_count"),
        "fill_full_count": events.get("fill_full_count"),
        "entries_total": stats.get("entries_total"),
        "completed_round_trips": completed_round_trips,
        "open_positions": stats.get("open_positions"),
        "confirmed_wins_by_sign": stats.get("confirmed_wins_by_sign"),
        "confirmed_losses_by_sign": stats.get("confirmed_losses_by_sign"),
        "gross_cost_basis_cents": dollars_to_cents(stats.get("gross_cost_basis_dollars")),
        "net_pnl_cents": dollars_to_cents(stats.get("net_pnl_total_dollars")),
        "live_trade_detected": live_trade_detected,
        "first_fill_event": events.get("first_fill_event"),
        "last_fill_event": events.get("last_fill_event"),
        "recent_events": events.get("recent_events") or [],
    }


def build_report() -> dict[str, Any]:
    lock = load_json(LIVE_LOCK)
    readiness = load_json(LIVE_READINESS)
    pid = lock.get("pid")
    proc = process_info(pid)
    lock_tag = str(lock.get("strategy_tag") or "")
    active_storage_tag = STORAGE_BY_STRATEGY_TAG.get(lock_tag, "")
    active_variant = next(
        (
            variant
            for variant in KNOWN_VARIANTS
            if variant["strategy_tag"] == lock_tag
        ),
        {
            "label": "unknown_feature_gate_variant",
            "strategy_tag": lock_tag,
            "storage_tag": active_storage_tag,
        },
    )
    active_paths = paths_for_variant(lock_tag, active_storage_tag) if active_storage_tag else {}
    stats = load_json(active_paths.get("stats", Path()))
    active_log_dir = active_paths.get("log_dir", Path())
    hourly_tail = tail_lines(active_log_dir / "hourly_monitor.log", 8)
    bot_tail = tail_lines(active_log_dir / "bot.log", 8)
    events = event_summary(active_log_dir / "execution_events.ndjson")
    completed_round_trips = int(stats.get("completed_round_trips") or 0)
    net_cents = dollars_to_cents(stats.get("net_pnl_total_dollars"))
    lock_is_feature_gate_sidecar = (
        lock_tag.startswith("mushroom_v28_feature_gate_")
        and lock_tag.endswith("_size1_live")
    )
    live_trade_detected = (
        int(events.get("entry_fill_count") or 0) > 0
        or completed_round_trips > 0
        or int(stats.get("entries_total") or 0) > 0
    )
    blockers = ["research_only"]
    if proc.get("running"):
        blockers.append("sidecar_process_running")
    if not lock_is_feature_gate_sidecar:
        blockers.append("live_lock_not_feature_gate_sidecar")
    if readiness.get("any_live_ready") is not True:
        blockers.append("live_readiness_artifact_false")
    if events.get("order_like_count") == 0:
        blockers.append("no_order_like_events_seen")
    else:
        blockers.append("order_like_events_present_review_required")
    if live_trade_detected and readiness.get("any_live_ready") is not True:
        blockers.append("sidecar_live_trade_detected_while_readiness_false")
    variant_summaries = [variant_summary(variant) for variant in KNOWN_VARIANTS]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "active_variant": active_variant,
        "active_log_dir": str(active_log_dir),
        "active_stats_path": str(active_paths.get("stats", "")),
        "live_lock": lock,
        "live_lock_is_feature_gate_sidecar": lock_is_feature_gate_sidecar,
        "process": proc,
        "hourly_monitor_tail": hourly_tail,
        "bot_log_tail": bot_tail,
        "execution_events": events,
        "score_summary": stats,
        "trade_summary": {
            "sidecar_live_trade_detected": live_trade_detected,
            "entries_total": stats.get("entries_total"),
            "completed_round_trips": completed_round_trips,
            "open_positions": stats.get("open_positions"),
            "confirmed_wins_by_sign": stats.get("confirmed_wins_by_sign"),
            "confirmed_losses_by_sign": stats.get("confirmed_losses_by_sign"),
            "gross_cost_basis_cents": dollars_to_cents(stats.get("gross_cost_basis_dollars")),
            "net_pnl_cents": net_cents,
            "net_pnl_dollars": stats.get("net_pnl_total_dollars"),
            "entry_fill_count": events.get("entry_fill_count"),
            "exit_fill_count": events.get("exit_fill_count"),
            "fill_full_count": events.get("fill_full_count"),
        },
        "variant_summaries": variant_summaries,
        "live_readiness_any_live_ready": readiness.get("any_live_ready"),
        "blockers": blockers,
        "interpretation": [
            "This is a read-only sidecar state report; it does not start, stop, or modify any process.",
            "Keep feature-gate size1 sidecar evidence separate from the live_mushroom_v28_size2 baseline.",
            "The active section follows the current live lock; historical variants remain listed below for attribution.",
            "A detected sidecar fill or round trip is operational context only, not promotion evidence.",
            "No order-like execution events were seen if order_like_count is zero.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lock = report.get("live_lock") or {}
    proc = report.get("process") or {}
    events = report.get("execution_events") or {}
    stats = report.get("score_summary") or {}
    trade = report.get("trade_summary") or {}
    active_variant = report.get("active_variant") or {}
    lines = [
        "# v28 Feature-Gate Sidecar Live State Audit",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Active variant: `{active_variant.get('label')}`",
        f"- Active log dir: `{report.get('active_log_dir')}`",
        f"- Active stats path: `{report.get('active_stats_path')}`",
        f"- Lock PID/tag: `{lock.get('pid')}` / `{lock.get('strategy_tag')}`",
        f"- Process running/name: `{proc.get('running')}` / `{proc.get('Name')}`",
        f"- Score entries/round trips/open: `{stats.get('entries_total')}` / `{stats.get('completed_round_trips')}` / `{stats.get('open_positions')}`",
        f"- Sidecar live trade detected: `{trade.get('sidecar_live_trade_detected')}`",
        f"- Entry/exit/full fill counts: `{trade.get('entry_fill_count')}` / `{trade.get('exit_fill_count')}` / `{trade.get('fill_full_count')}`",
        f"- Score net/cost cents: `{trade.get('net_pnl_cents')}` / `{trade.get('gross_cost_basis_cents')}`",
        f"- Event counts: `{events.get('event_counts')}`",
        f"- Order-like events: `{events.get('order_like_count')}`",
        f"- Live-readiness artifact any_live_ready: `{report.get('live_readiness_any_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Filled Trade Evidence", ""])
    lines.append(f"- First entry fill: `{events.get('first_entry_fill_event')}`")
    lines.append(f"- Last exit fill: `{events.get('last_exit_fill_event')}`")
    lines.append(f"- First fill event: `{events.get('first_fill_event')}`")
    lines.append(f"- Last fill event: `{events.get('last_fill_event')}`")
    lines.extend(["", "## Variant Separation", ""])
    lines.append("| label | strategy tag | storage tag | entries | round trips | W/L | net c | fills | order-like | live trade? |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---|")
    for row in report.get("variant_summaries") or []:
        wl = f"{row.get('confirmed_wins_by_sign')}/{row.get('confirmed_losses_by_sign')}"
        fills = f"{row.get('entry_fill_count')}/{row.get('exit_fill_count')}/{row.get('fill_full_count')}"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row.get('label')}`",
                    f"`{row.get('strategy_tag')}`",
                    f"`{row.get('storage_tag')}`",
                    str(row.get("entries_total")),
                    str(row.get("completed_round_trips")),
                    wl,
                    str(row.get("net_pnl_cents")),
                    fills,
                    str(row.get("order_like_count")),
                    str(row.get("live_trade_detected")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Hourly Monitor Tail", ""])
    lines.extend(f"- `{line}`" for line in report.get("hourly_monitor_tail") or [])
    lines.extend(["", "## Recent Events", ""])
    for row in events.get("recent_events") or []:
        lines.append(f"- `{row}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
