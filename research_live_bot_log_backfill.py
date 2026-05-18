from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
LOCAL_TZ = ZoneInfo("America/New_York")
BACKFILL_VERSION = "live-bot-log-backfill-v1"

LOG_TS_RE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| (?P<level>[A-Z]+) \| (?P<msg>.*)$")
KEY_VALUE_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[^\s]+)")
HEARTBEAT_RE = re.compile(
    r"Heartbeat \| watch=(?P<market>\S+) yes_bid=(?P<yes_bid>\S+) yes_ask=(?P<yes_ask>\S+) "
    r"no_bid=(?P<no_bid>\S+) no_ask=(?P<no_ask>\S+) book_ready=(?P<book_ready>\S+) "
    r"position=(?P<position>\S+) pending=(?P<pending>\S+) dry_run=(?P<dry_run>\S+) "
    r"trust=(?P<trust>\S+) run_id=(?P<run_id>\S+)"
)
WATCH_RE = re.compile(
    r"Watching market (?P<market>\S+) close_time=(?P<close_time>\S+) status=(?P<status>\S+)(?: .*?)? run_id=(?P<run_id>\S+)"
)
WS_CONNECTED_RE = re.compile(r"WS connected for (?P<market>\S+)")
SNAPSHOT_READY_RE = re.compile(r"Orderbook snapshot ready for (?P<market>\S+)")


def parse_local_log_ts(value: str) -> datetime | None:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S,%f")
    except ValueError:
        return None
    return parsed.replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def local_recv_ns(dt: datetime) -> int:
    return int(dt.timestamp() * 1_000_000_000)


def parse_int(value: Any) -> int | None:
    if value in (None, "", "None", "null", "nan"):
        return None
    try:
        return int(round(float(str(value))))
    except Exception:
        return None


def parse_float(value: Any) -> float | None:
    if value in (None, "", "None", "null", "nan"):
        return None
    try:
        return float(str(value))
    except Exception:
        return None


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    return None


def day_hour(dt: datetime) -> tuple[str, str]:
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y-%m-%d"), dt_utc.strftime("%H")


def record_path(root: Path, event_type: str, dt: datetime, run_id: str) -> Path:
    day, hour = day_hour(dt)
    safe_run_id = run_id or "unknown-run"
    return root / f"type={event_type}" / f"day={day}" / f"hour={hour}" / f"part-log-backfill-{safe_run_id}.ndjson"


def checkpoint_path(root: Path, market: str, dt: datetime, run_id: str) -> Path:
    day = dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    safe_run_id = run_id or "unknown-run"
    return root / f"day={day}" / f"market={market}" / f"part-log-backfill-{safe_run_id}.ndjson"


def base_raw_event(
    *,
    dataset_tag: str,
    storage_tag: str,
    run_id: str,
    event_type: str,
    channel: str,
    source: str,
    market: str,
    dt_utc: datetime,
    trust_state: str | None,
    payload: dict[str, Any],
    sequence_number: int | None = None,
) -> dict[str, Any]:
    return {
        "channel": channel,
        "connection_id": f"log-backfill-{storage_tag}",
        "dataset_tag": dataset_tag,
        "event_type": event_type,
        "exchange_ts": None,
        "local_recv_ns": local_recv_ns(dt_utc),
        "local_recv_ts": iso(dt_utc),
        "market_ticker": market,
        "payload_json": payload,
        "run_id": run_id,
        "sequence_number": sequence_number,
        "source": source,
        "storage_tag": storage_tag,
        "trust_state": trust_state,
        "ts_wall": iso(dt_utc),
    }


def heartbeat_to_records(dataset_tag: str, storage_tag: str, match: re.Match[str], dt_utc: datetime) -> tuple[dict[str, Any], dict[str, Any]]:
    values = match.groupdict()
    market = values["market"]
    run_id = values.get("run_id") or "unknown-run"
    yes_bid = parse_int(values.get("yes_bid"))
    yes_ask = parse_int(values.get("yes_ask"))
    no_bid = parse_int(values.get("no_bid"))
    no_ask = parse_int(values.get("no_ask"))
    trust = values.get("trust")
    payload = {
        "market_ticker": market,
        "yes_bid": yes_bid,
        "yes_ask": yes_ask,
        "no_bid": no_bid,
        "no_ask": no_ask,
        "book_ready": parse_bool(values.get("book_ready")),
        "position": parse_bool(values.get("position")),
        "pending": parse_bool(values.get("pending")),
        "dry_run": parse_bool(values.get("dry_run")),
        "run_id": run_id,
        "recorder_type": "log_derived_heartbeat",
    }
    raw = base_raw_event(
        dataset_tag=dataset_tag,
        storage_tag=storage_tag,
        run_id=run_id,
        event_type="heartbeat",
        channel="bot",
        source="bot_log_heartbeat",
        market=market,
        dt_utc=dt_utc,
        trust_state=trust,
        payload=payload,
    )
    checkpoint = {
        "checkpoint_ts": iso(dt_utc),
        "dataset_tag": dataset_tag,
        "event_type": "orderbook_checkpoint",
        "market_ticker": market,
        "no_bid_prices": [no_bid] if no_bid is not None else [],
        "no_bid_sizes": [],
        "reason": "log_heartbeat_top_of_book",
        "run_id": run_id,
        "sequence_number": None,
        "source_event_count": None,
        "source": "bot_log_heartbeat",
        "ts_wall": iso(dt_utc),
        "yes_bid_prices": [yes_bid] if yes_bid is not None else [],
        "yes_bid_sizes": [],
        "yes_ask_cents": yes_ask,
        "no_ask_cents": no_ask,
        "data_quality_flags": ["top_of_book_only", "depth_sizes_unavailable", "log_derived"],
    }
    return raw, checkpoint


def generic_log_event(
    *,
    dataset_tag: str,
    storage_tag: str,
    event_type: str,
    market: str,
    run_id: str,
    dt_utc: datetime,
    message: str,
    payload: dict[str, Any],
    trust_state: str | None = None,
) -> dict[str, Any]:
    payload = dict(payload)
    payload.setdefault("message", message)
    payload.setdefault("run_id", run_id)
    payload.setdefault("recorder_type", "log_derived")
    return base_raw_event(
        dataset_tag=dataset_tag,
        storage_tag=storage_tag,
        run_id=run_id,
        event_type=event_type,
        channel="bot",
        source="bot_log",
        market=market,
        dt_utc=dt_utc,
        trust_state=trust_state,
        payload=payload,
    )


def parse_bot_log(bot_log_path: Path, dataset_tag: str, storage_tag: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    raw_events: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    run_ids: set[str] = set()
    markets: set[str] = set()
    first_ts: datetime | None = None
    last_ts: datetime | None = None

    if not bot_log_path.exists():
        return raw_events, checkpoints, {"error": f"missing bot log: {bot_log_path}"}

    with bot_log_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.rstrip("\n")
            m = LOG_TS_RE.match(line)
            if not m:
                continue
            dt_utc = parse_local_log_ts(m.group("ts"))
            if dt_utc is None:
                continue
            first_ts = dt_utc if first_ts is None or dt_utc < first_ts else first_ts
            last_ts = dt_utc if last_ts is None or dt_utc > last_ts else last_ts
            msg = m.group("msg")

            hb = HEARTBEAT_RE.search(msg)
            if hb:
                raw, checkpoint = heartbeat_to_records(dataset_tag, storage_tag, hb, dt_utc)
                raw_events.append(raw)
                checkpoints.append(checkpoint)
                counts["heartbeat"] += 1
                run_ids.add(str(raw.get("run_id") or ""))
                markets.add(str(raw.get("market_ticker") or ""))
                continue

            watch = WATCH_RE.search(msg)
            if watch:
                values = watch.groupdict()
                run_id = values.get("run_id") or "unknown-run"
                market = values.get("market") or ""
                payload = {
                    "market_ticker": market,
                    "close_time": values.get("close_time"),
                    "status": values.get("status"),
                }
                raw_events.append(
                    generic_log_event(
                        dataset_tag=dataset_tag,
                        storage_tag=storage_tag,
                        event_type="watch_market",
                        market=market,
                        run_id=run_id,
                        dt_utc=dt_utc,
                        message=msg,
                        payload=payload,
                        trust_state="cold",
                    )
                )
                counts["watch_market"] += 1
                run_ids.add(run_id)
                markets.add(market)
                continue

            ws = WS_CONNECTED_RE.search(msg)
            if ws:
                market = ws.group("market")
                raw_events.append(
                    generic_log_event(
                        dataset_tag=dataset_tag,
                        storage_tag=storage_tag,
                        event_type="ws_connected",
                        market=market,
                        run_id="unknown-run",
                        dt_utc=dt_utc,
                        message=msg,
                        payload={"market_ticker": market},
                        trust_state="cold",
                    )
                )
                counts["ws_connected"] += 1
                markets.add(market)
                continue

            snap = SNAPSHOT_READY_RE.search(msg)
            if snap:
                market = snap.group("market")
                raw_events.append(
                    generic_log_event(
                        dataset_tag=dataset_tag,
                        storage_tag=storage_tag,
                        event_type="orderbook_snapshot_ready",
                        market=market,
                        run_id="unknown-run",
                        dt_utc=dt_utc,
                        message=msg,
                        payload={"market_ticker": market},
                        trust_state="synced",
                    )
                )
                counts["orderbook_snapshot_ready"] += 1
                markets.add(market)
                continue

            if "Liquidity dwell " in msg or "Execution state |" in msg or "Live fill policy approved |" in msg:
                kv = {match.group("key"): match.group("value") for match in KEY_VALUE_RE.finditer(msg)}
                market = kv.get("market", "")
                run_id = kv.get("run_id", "unknown-run")
                event_type = "strategy_log_event"
                if "Liquidity dwell approved" in msg:
                    event_type = "liquidity_dwell_approved_log"
                elif "Liquidity dwell rejected" in msg:
                    event_type = "liquidity_dwell_rejected_log"
                elif "Liquidity dwell armed" in msg:
                    event_type = "liquidity_dwell_armed_log"
                elif "Live fill policy approved" in msg:
                    event_type = "live_fill_policy_approved_log"
                raw_events.append(
                    generic_log_event(
                        dataset_tag=dataset_tag,
                        storage_tag=storage_tag,
                        event_type=event_type,
                        market=market,
                        run_id=run_id,
                        dt_utc=dt_utc,
                        message=msg,
                        payload=kv,
                        trust_state=kv.get("trust"),
                    )
                )
                counts[event_type] += 1
                if run_id:
                    run_ids.add(run_id)
                if market:
                    markets.add(market)

    return raw_events, checkpoints, {
        "bot_log_path": str(bot_log_path),
        "bot_log_raw_events": len(raw_events),
        "bot_log_checkpoints": len(checkpoints),
        "bot_log_event_counts": dict(counts),
        "run_ids": sorted(run_id for run_id in run_ids if run_id),
        "markets": sorted(market for market in markets if market),
        "first_bot_log_ts": iso(first_ts) if first_ts else None,
        "last_bot_log_ts": iso(last_ts) if last_ts else None,
    }


def parse_execution_events(execution_path: Path, dataset_tag: str, storage_tag: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    markets: set[str] = set()
    run_ids: set[str] = set()

    if not execution_path.exists():
        return rows, {"error": f"missing execution events: {execution_path}"}

    with execution_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            ts_text = event.get("ts_wall")
            try:
                dt_utc = datetime.fromisoformat(str(ts_text).replace("Z", "+00:00")).astimezone(timezone.utc)
            except Exception:
                continue
            event_type = str(event.get("event_type") or "execution_event")
            market = str(event.get("market") or "")
            run_id = str(event.get("run_id") or "unknown-run")
            payload = dict(event)
            payload["recorder_type"] = "log_derived_execution_event"
            rows.append(
                base_raw_event(
                    dataset_tag=dataset_tag,
                    storage_tag=storage_tag,
                    run_id=run_id,
                    event_type=f"execution_{event_type}",
                    channel="execution_events",
                    source="execution_events_ndjson",
                    market=market,
                    dt_utc=dt_utc,
                    trust_state=event.get("trust_state"),
                    payload=payload,
                    sequence_number=parse_int(event.get("last_seq")),
                )
            )
            counts[event_type] += 1
            markets.add(market)
            run_ids.add(run_id)
            first_ts = dt_utc if first_ts is None or dt_utc < first_ts else first_ts
            last_ts = dt_utc if last_ts is None or dt_utc > last_ts else last_ts

    return rows, {
        "execution_events_path": str(execution_path),
        "execution_raw_events": len(rows),
        "execution_event_counts": dict(counts),
        "run_ids": sorted(run_id for run_id in run_ids if run_id),
        "markets": sorted(market for market in markets if market),
        "first_execution_ts": iso(first_ts) if first_ts else None,
        "last_execution_ts": iso(last_ts) if last_ts else None,
    }


def write_grouped_ndjson(rows: list[dict[str, Any]], root: Path, *, checkpoint: bool = False) -> int:
    grouped: dict[Path, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        try:
            dt_utc = datetime.fromisoformat(str(row.get("checkpoint_ts" if checkpoint else "local_recv_ts")).replace("Z", "+00:00")).astimezone(timezone.utc)
        except Exception:
            continue
        run_id = str(row.get("run_id") or "unknown-run")
        if checkpoint:
            path = checkpoint_path(root, str(row.get("market_ticker") or "unknown-market"), dt_utc, run_id)
        else:
            path = record_path(root, str(row.get("event_type") or "unknown_event"), dt_utc, run_id)
        grouped[path].append(row)

    for path, items in grouped.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        items = sorted(items, key=lambda item: str(item.get("checkpoint_ts" if checkpoint else "local_recv_ts") or ""))
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for item in items:
                handle.write(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n")
    return sum(len(items) for items in grouped.values())


def read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def existing_tape_has_rows(root: Path) -> bool:
    return root.exists() and any(root.rglob("*.parquet"))


def current_feature_set_version(metadata_root: Path) -> str:
    pipeline_status = read_json_file(metadata_root / "pipeline_status.json")
    pipeline_feature_set = str(pipeline_status.get("feature_set_version") or "")
    if pipeline_feature_set.startswith("research-lab-features-v"):
        return pipeline_feature_set

    existing_manifest = read_json_file(metadata_root / "dataset_manifest.json")
    existing_feature_set = str(existing_manifest.get("feature_set_version") or "")
    if existing_feature_set.startswith("research-lab-features-v"):
        return existing_feature_set
    return "research-lab-features-v2-gauntlet"


def write_metadata(
    dataset_root: Path,
    *,
    dataset_tag: str,
    storage_tag: str,
    summaries: list[dict[str, Any]],
    raw_written: int,
    checkpoints_written: int,
) -> dict[str, Any]:
    metadata_root = dataset_root / "metadata"
    metadata_root.mkdir(parents=True, exist_ok=True)
    feature_set_version = current_feature_set_version(metadata_root)
    records_settlement_labels = (
        existing_tape_has_rows(dataset_root / "trade_labels")
        or existing_tape_has_rows(dataset_root / "outcome_labels")
    )
    source_paths: list[str] = []
    markets: set[str] = set()
    run_ids: set[str] = set()
    started: list[datetime] = []
    ended: list[datetime] = []
    for summary in summaries:
        for key in ("bot_log_path", "execution_events_path"):
            if summary.get(key):
                source_paths.append(str(summary[key]))
        for market in summary.get("markets", []) or []:
            markets.add(str(market))
        for run_id in summary.get("run_ids", []) or []:
            run_ids.add(str(run_id))
        for key in ("first_bot_log_ts", "first_execution_ts"):
            parsed = parse_iso(summary.get(key))
            if parsed:
                started.append(parsed)
        for key in ("last_bot_log_ts", "last_execution_ts"):
            parsed = parse_iso(summary.get(key))
            if parsed:
                ended.append(parsed)

    started_at = iso(min(started)) if started else ""
    ended_at = iso(max(ended)) if ended else ""
    payload = {
        "dataset_tag": dataset_tag,
        "schema_version": "phase1-ndjson-v1",
        "recorder_version": BACKFILL_VERSION,
        "feature_set_version": feature_set_version,
        "recorder_type": "backfill",
        "strategy_tags": ["liquidity_dwell_p05_q065_hold"] if dataset_tag == "live_liquidity_dwell_size2" else [],
        "live_bot_run_tag": storage_tag,
        "source_dataset_tag": "",
        "source_log_paths": sorted(set(source_paths)),
        "started_at_utc": started_at,
        "ended_at_utc": ended_at,
        "market_tickers": sorted(markets),
        "market_selection_reason": "KXBTC15M live bot log-derived stream",
        "records_raw_market_feed": False,
        "records_book_checkpoints": checkpoints_written > 0,
        "records_strategy_decisions": True,
        "records_execution_events": True,
        "records_settlement_labels": records_settlement_labels,
        "data_quality_flags": [
            "log_derived",
            "not_native_passive_ws",
            "heartbeat_top_of_book_only",
            "book_depth_sizes_unavailable_from_heartbeat",
            "execution_events_preserved_as_raw_events",
        ],
        "native_passive_capture_status": "missing_backfill_only",
        "metadata_refresh_source": "research_live_bot_log_backfill",
        "updated_at_utc": iso(datetime.now(timezone.utc)),
    }
    (metadata_root / "dataset_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status = {
        "schema_version": "live-bot-log-backfill-status-v1",
        "dataset_tag": dataset_tag,
        "storage_tag": storage_tag,
        "backfill_version": BACKFILL_VERSION,
        "generated_at_utc": iso(datetime.now(timezone.utc)),
        "raw_events_written": raw_written,
        "book_checkpoints_written": checkpoints_written,
        "feature_set_version_preserved": feature_set_version,
        "records_settlement_labels": records_settlement_labels,
        "source_summaries": summaries,
    }
    (metadata_root / "live_bot_log_backfill_status.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    schema = {
        "schema_version": "phase1-ndjson-v1",
        "dataset_tag": dataset_tag,
        "updated_at": iso(datetime.now(timezone.utc)),
        "recorder_version": BACKFILL_VERSION,
    }
    schema_path = metadata_root / "schema_version.json"
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return status


def parse_iso(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def run_once(dataset_tag: str, storage_tag: str) -> dict[str, Any]:
    dataset_root = ROOT / "research_data" / dataset_tag
    raw_root = dataset_root / "raw_events"
    checkpoint_root = dataset_root / "book_checkpoints"
    bot_log_path = ROOT / "logs" / storage_tag / "bot.log"
    execution_path = ROOT / "logs" / storage_tag / "execution_events.ndjson"

    log_raw, checkpoints, log_summary = parse_bot_log(bot_log_path, dataset_tag, storage_tag)
    execution_raw, execution_summary = parse_execution_events(execution_path, dataset_tag, storage_tag)
    raw_rows = log_raw + execution_raw

    raw_written = write_grouped_ndjson(raw_rows, raw_root, checkpoint=False)
    checkpoints_written = write_grouped_ndjson(checkpoints, checkpoint_root, checkpoint=True)
    status = write_metadata(
        dataset_root,
        dataset_tag=dataset_tag,
        storage_tag=storage_tag,
        summaries=[log_summary, execution_summary],
        raw_written=raw_written,
        checkpoints_written=checkpoints_written,
    )
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill a live bot log stream into Research Lab raw_events/book_checkpoints.")
    parser.add_argument("--dataset", default="live_liquidity_dwell_size2")
    parser.add_argument("--storage-tag", default="live_liquidity_dwell_size2")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval-seconds", type=int, default=30)
    args = parser.parse_args()

    if not args.watch:
        print(json.dumps(run_once(args.dataset, args.storage_tag), indent=2, sort_keys=True))
        return

    while True:
        status = run_once(args.dataset, args.storage_tag)
        print(json.dumps(status, indent=2, sort_keys=True), flush=True)
        time.sleep(max(args.interval_seconds, 5))


if __name__ == "__main__":
    main()
