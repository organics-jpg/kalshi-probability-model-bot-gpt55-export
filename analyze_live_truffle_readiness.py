from __future__ import annotations

import argparse
import collections
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_BOT_LOG = ROOT / "logs" / "live_90_78_shadow_size2" / "bot.log"
DEFAULT_SHADOW_LOG = ROOT / "logs" / "live_90_78_shadow_size2" / "truffle_post_entry_shadow.ndjson"
DEFAULT_OUTPUT = ROOT / "logs" / "live_truffle_readiness_latest.json"

BOT_TS_RE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\|\s+(?P<level>\w+)\s+\|\s+(?P<msg>.*)$")


def parse_bot_ts(raw: str) -> datetime | None:
    match = BOT_TS_RE.match(raw)
    if not match:
        return None
    try:
        return datetime.strptime(match.group("ts"), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def parse_iso(raw: Any) -> datetime | None:
    if not raw:
        return None
    text = str(raw)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def read_tail_lines(path: Path, *, max_lines: int = 5000) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-max_lines:]


def iter_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows


def file_snapshot(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    stat = path.stat()
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_local": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
    }


def analyze_bot_log(path: Path) -> dict[str, Any]:
    lines = read_tail_lines(path)
    parsed = []
    for line in lines:
        match = BOT_TS_RE.match(line)
        if match:
            parsed.append({"ts": parse_bot_ts(line), "level": match.group("level"), "msg": match.group("msg"), "line": line})
    last = parsed[-1] if parsed else {}
    refresh_errors = [row for row in parsed if "Market refresh failed" in str(row.get("msg") or "")]
    status_filter_errors = [row for row in refresh_errors if "invalid status filter" in str(row.get("msg") or "").lower()]
    heartbeats = [row for row in parsed if str(row.get("msg") or "").startswith("Heartbeat |")]
    watch_rows = [row for row in parsed if str(row.get("msg") or "").startswith("Watching market ")]
    start_rows = [row for row in parsed if str(row.get("msg") or "").startswith("Starting WS bot.")]
    last_ts = last.get("ts") if isinstance(last.get("ts"), datetime) else None
    last_watch_ts = watch_rows[-1].get("ts") if watch_rows and isinstance(watch_rows[-1].get("ts"), datetime) else None
    last_start_ts = start_rows[-1].get("ts") if start_rows and isinstance(start_rows[-1].get("ts"), datetime) else None
    last_status_error_ts = (
        status_filter_errors[-1].get("ts")
        if status_filter_errors and isinstance(status_filter_errors[-1].get("ts"), datetime)
        else None
    )
    now_local = datetime.now()
    invalid_status_filter_active = bool(
        last_status_error_ts is not None
        and (last_watch_ts is None or last_status_error_ts > last_watch_ts)
    )
    return {
        "file": file_snapshot(path),
        "tail_line_count": int(len(lines)),
        "last_log_ts_local": last_ts.isoformat(timespec="seconds") if last_ts else None,
        "last_log_age_seconds": round((now_local - last_ts).total_seconds(), 1) if last_ts else None,
        "last_log_line": last.get("line"),
        "last_heartbeat_line": heartbeats[-1]["line"] if heartbeats else None,
        "last_start_line": start_rows[-1]["line"] if start_rows else None,
        "last_start_ts_local": last_start_ts.isoformat(timespec="seconds") if last_start_ts else None,
        "last_watch_line": watch_rows[-1]["line"] if watch_rows else None,
        "last_watch_ts_local": last_watch_ts.isoformat(timespec="seconds") if last_watch_ts else None,
        "last_invalid_status_filter_ts_local": last_status_error_ts.isoformat(timespec="seconds") if last_status_error_ts else None,
        "market_refresh_error_tail_count": int(len(refresh_errors)),
        "invalid_status_filter_tail_count": int(len(status_filter_errors)),
        "last_market_refresh_error": refresh_errors[-1]["line"] if refresh_errors else None,
        "invalid_status_filter_active": invalid_status_filter_active,
    }


def decision_schema(row: dict[str, Any]) -> str:
    decision = row.get("decision") if isinstance(row.get("decision"), dict) else {}
    schema = str(row.get("decision_schema") or decision.get("decision_schema") or "").strip()
    if schema:
        return schema
    version = str(decision.get("schema_version") or row.get("schema_version") or "").strip()
    exit_decision = str(decision.get("decision") or "").strip().upper()
    if exit_decision in {"HOLD", "EXIT_NOW"}:
        return "exit_supervisor"
    if version == "post_entry_shadow_decision_v1":
        return "legacy_reversal_shadow"
    return version or "unknown"


def analyze_shadow_log(path: Path) -> dict[str, Any]:
    rows = iter_ndjson(path)
    events = collections.Counter(str(row.get("event_type") or "unknown") for row in rows)
    decisions = [row for row in rows if row.get("event_type") == "post_entry_shadow_decision"]
    outcomes = [row for row in rows if row.get("event_type") == "post_entry_shadow_outcome"]
    scheduled = [row for row in rows if row.get("event_type") == "post_entry_shadow_scheduled"]
    schema_counts = collections.Counter(decision_schema(row) for row in decisions)
    delay_counts = collections.Counter(str(row.get("shadow_delay_seconds") or row.get("seconds_since_entry") or "") for row in scheduled + decisions)
    decisions_sorted = sorted(
        decisions,
        key=lambda row: parse_iso(row.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc),
    )
    invalid = [row for row in decisions_sorted if not bool(row.get("valid"))]
    last_decision = decisions_sorted[-1] if decisions_sorted else {}
    last_decision_ts = parse_iso(last_decision.get("ts_wall"))
    now_utc = datetime.now(timezone.utc)
    shadow_evals = [
        row.get("shadow_exit_eval")
        for row in outcomes
        if isinstance(row.get("shadow_exit_eval"), dict) and row["shadow_exit_eval"].get("available")
    ]
    exit_supervisor_count = int(sum(count for schema, count in schema_counts.items() if schema == "exit_supervisor"))
    return {
        "file": file_snapshot(path),
        "event_count": int(len(rows)),
        "event_counts": dict(events),
        "decision_count": int(len(decisions)),
        "outcome_count": int(len(outcomes)),
        "schema_counts": dict(schema_counts),
        "delay_counts": dict(delay_counts),
        "invalid_decision_count": int(len(invalid)),
        "latest_parse_error": invalid[-1].get("parse_error") if invalid else "",
        "latest_invalid_decision_ts_utc": parse_iso(invalid[-1].get("ts_wall")).isoformat(timespec="seconds") if invalid and parse_iso(invalid[-1].get("ts_wall")) else None,
        "last_decision_ts_utc": last_decision_ts.isoformat(timespec="seconds") if last_decision_ts else None,
        "last_decision_age_minutes": round((now_utc - last_decision_ts.astimezone(timezone.utc)).total_seconds() / 60.0, 2) if last_decision_ts else None,
        "last_decision_schema": decision_schema(last_decision) if last_decision else None,
        "last_decision_market": last_decision.get("market"),
        "last_decision_valid": bool(last_decision.get("valid")) if last_decision else None,
        "last_decision_parse_error": last_decision.get("parse_error") or "",
        "last_decision_candidate_slice_tags": last_decision.get("candidate_slice_tags") or [],
        "exit_supervisor_decision_count": exit_supervisor_count,
        "shadow_exit_eval_available_count": int(len(shadow_evals)),
    }


def build_readiness(bot: dict[str, Any], shadow: dict[str, Any]) -> dict[str, Any]:
    actions: list[str] = []
    last_start = parse_iso(bot.get("last_start_ts_local"))
    last_decision = parse_iso(shadow.get("last_decision_ts_utc"))
    restart_after_last_shadow_decision = bool(
        last_start is not None
        and last_decision is not None
        and last_start > last_decision.astimezone().replace(tzinfo=None)
    )
    if bot.get("invalid_status_filter_active"):
        actions.append("Restart with patched market discovery before trusting live collection; current process is stuck on an invalid Kalshi status filter.")
    if not shadow.get("exit_supervisor_decision_count"):
        if restart_after_last_shadow_decision:
            actions.append("Waiting for the first new post-entry shadow decision after restart; no new live entry has triggered Qwen 3.6 yet.")
        else:
            actions.append("Restart is required before Qwen 3.6 HOLD/EXIT_NOW exit-supervisor evidence is collected.")
    if not shadow.get("shadow_exit_eval_available_count"):
        actions.append("No live shadow_exit_eval rows are available yet; do not score exit-supervisor economics from live logs.")
    if shadow.get("last_decision_parse_error") and not restart_after_last_shadow_decision:
        actions.append("Resolve latest Truffle endpoint/parse error before treating shadow decisions as reliable.")
    ready = not actions
    return {
        "ready_for_live_action": False,
        "ready_for_shadow_exit_supervisor_collection": bool(
            (shadow.get("exit_supervisor_decision_count") or restart_after_last_shadow_decision)
            and not bot.get("invalid_status_filter_active")
        ),
        "needs_operator_restart": bool(
            bot.get("invalid_status_filter_active")
            or (not shadow.get("exit_supervisor_decision_count") and not restart_after_last_shadow_decision)
        ),
        "restart_after_last_shadow_decision": restart_after_last_shadow_decision,
        "actions": actions,
        "summary": "ok" if ready else "not_ready",
    }


def analyze(bot_log: Path, shadow_log: Path) -> dict[str, Any]:
    bot = analyze_bot_log(bot_log)
    shadow = analyze_shadow_log(shadow_log)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "bot_log": bot,
        "shadow_log": shadow,
        "readiness": build_readiness(bot, shadow),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Report whether the live bot is collecting useful Truffle exit-supervisor evidence.")
    parser.add_argument("--bot-log", default=str(DEFAULT_BOT_LOG))
    parser.add_argument("--shadow-log", default=str(DEFAULT_SHADOW_LOG))
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    bot_log = Path(args.bot_log)
    shadow_log = Path(args.shadow_log)
    output_path = Path(args.output_path)
    if not bot_log.is_absolute():
        bot_log = ROOT / bot_log
    if not shadow_log.is_absolute():
        shadow_log = ROOT / shadow_log
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    payload = analyze(bot_log, shadow_log)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved live Truffle readiness to {output_path}")
    print(json.dumps(payload["readiness"], indent=2))


if __name__ == "__main__":
    main()
