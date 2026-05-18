from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import logging
import os
import signal
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import websockets

from kalshi_btc15m_bot_ws import (
    ALLOWED_SERIES_TICKER,
    Config,
    KalshiClient,
    LiveOrderBook,
    derive_ws_url,
    extract_price_cents,
    parse_btc_strike_from_market,
    parse_iso,
    utc_now,
)


ROOT = Path(__file__).resolve().parent
RECORDER_VERSION = "native-passive-ws-v1"


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def local_recv_ns(dt: datetime) -> int:
    return int(dt.timestamp() * 1_000_000_000)


def day_hour(dt: datetime) -> tuple[str, str]:
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y-%m-%d"), dt_utc.strftime("%H")


def json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return iso(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=json_default) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def append_ndjson(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=json_default) + "\n")


def raw_event_path(root: Path, event_type: str, dt_utc: datetime, run_id: str) -> Path:
    day, hour = day_hour(dt_utc)
    return root / f"type={event_type}" / f"day={day}" / f"hour={hour}" / f"part-native-passive-{run_id}.ndjson"


def checkpoint_path(root: Path, market: str, dt_utc: datetime, run_id: str) -> Path:
    day = dt_utc.astimezone(timezone.utc).strftime("%Y-%m-%d")
    safe_market = market or "unknown-market"
    return root / f"day={day}" / f"market={safe_market}" / f"part-native-passive-{run_id}.ndjson"


def env_path(name: str, default: str = "") -> Path:
    value = os.getenv(name, default).strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return Path(value).expanduser()


def load_passive_config() -> Config:
    api_key_id = os.getenv("KALSHI_API_KEY_ID", "").strip()
    if not api_key_id:
        raise RuntimeError("Missing required environment variable: KALSHI_API_KEY_ID")
    private_key_path = env_path("KALSHI_PRIVATE_KEY_PATH")
    base_url = os.getenv("KALSHI_BASE_URL", "https://api.elections.kalshi.com/trade-api/v2").strip().rstrip("/")
    ws_url = os.getenv("KALSHI_WS_URL", derive_ws_url(base_url)).strip().rstrip("/")
    series = os.getenv("KALSHI_SERIES_TICKER", ALLOWED_SERIES_TICKER).strip()
    return Config(
        api_key_id=api_key_id,
        private_key_path=private_key_path,
        base_url=base_url,
        ws_url=ws_url,
        series_ticker=series,
    )


def current_feature_set_version(metadata_root: Path) -> str:
    pipeline_status = read_json(metadata_root / "pipeline_status.json")
    value = str(pipeline_status.get("feature_set_version") or "")
    if value.startswith("research-lab-features-v"):
        return value
    manifest = read_json(metadata_root / "dataset_manifest.json")
    value = str(manifest.get("feature_set_version") or "")
    if value.startswith("research-lab-features-v"):
        return value
    return "research-lab-features-v3-online-neighbor"


def any_parquet_rows(root: Path) -> bool:
    return root.exists() and any(root.rglob("*.parquet"))


def any_raw_type(dataset_root: Path, prefix: str) -> bool:
    raw_root = dataset_root / "raw_events"
    return raw_root.exists() and any(path.name.startswith(f"type={prefix}") for path in raw_root.iterdir() if path.is_dir())


def sorted_book(book: dict[int, Decimal], max_depth: int) -> tuple[list[int], list[float]]:
    items = sorted(book.items(), key=lambda item: item[0], reverse=True)[:max_depth]
    return [int(price) for price, _ in items], [float(qty) for _, qty in items]


def enriched_ticker_payload(message: dict[str, Any]) -> dict[str, Any]:
    payload = dict(message)
    for key in ("yes_bid", "yes_ask", "no_bid", "no_ask"):
        cents = extract_price_cents(payload, key)
        if cents is not None:
            payload[key] = cents

    yes_bid = payload.get("yes_bid") if isinstance(payload.get("yes_bid"), int) else None
    yes_ask = payload.get("yes_ask") if isinstance(payload.get("yes_ask"), int) else None
    no_bid = payload.get("no_bid") if isinstance(payload.get("no_bid"), int) else None
    no_ask = payload.get("no_ask") if isinstance(payload.get("no_ask"), int) else None
    if no_bid is None and yes_ask is not None:
        payload["no_bid"] = 100 - yes_ask
        payload.setdefault("no_bid_size_fp", payload.get("yes_ask_size_fp"))
    if no_ask is None and yes_bid is not None:
        payload["no_ask"] = 100 - yes_bid
        payload.setdefault("no_ask_size_fp", payload.get("yes_bid_size_fp"))
    if yes_bid is None and no_ask is not None:
        payload["yes_bid"] = 100 - no_ask
        payload.setdefault("yes_bid_size_fp", payload.get("no_ask_size_fp"))
    if yes_ask is None and no_bid is not None:
        payload["yes_ask"] = 100 - no_bid
        payload.setdefault("yes_ask_size_fp", payload.get("no_bid_size_fp"))
    return payload


def enriched_delta_payload(message: dict[str, Any]) -> dict[str, Any]:
    payload = dict(message)
    price_cents = extract_price_cents(payload, "price")
    if price_cents is not None:
        payload["price_cents"] = price_cents
    return payload


class NativePassiveRecorder:
    def __init__(
        self,
        *,
        dataset_tag: str,
        strategy_tag: str,
        bot_tag: str,
        checkpoint_interval_seconds: float,
        market_refresh_seconds: float,
        checkpoint_depth: int,
        status_interval_seconds: float,
        run_id: str,
    ) -> None:
        self.dataset_tag = dataset_tag
        self.strategy_tag = strategy_tag
        self.bot_tag = bot_tag
        self.checkpoint_interval_seconds = checkpoint_interval_seconds
        self.market_refresh_seconds = market_refresh_seconds
        self.checkpoint_depth = checkpoint_depth
        self.status_interval_seconds = status_interval_seconds
        self.run_id = run_id
        self.connection_id = f"native-passive-{run_id}"
        self.dataset_root = ROOT / "research_data" / dataset_tag
        self.raw_root = self.dataset_root / "raw_events"
        self.checkpoint_root = self.dataset_root / "book_checkpoints"
        self.metadata_root = self.dataset_root / "metadata"
        self.log_root = ROOT / "logs" / dataset_tag
        self.log_root.mkdir(parents=True, exist_ok=True)
        self.config = load_passive_config()
        self.client = KalshiClient(self.config)
        self.orderbook = LiveOrderBook()
        self.shutdown_event = asyncio.Event()
        self.started_at = utc_now()
        self.markets: set[str] = set()
        self.counts: Counter[str] = Counter()
        self.raw_events_written = 0
        self.book_checkpoints_written = 0
        self.last_raw_event_ts = ""
        self.last_checkpoint_ts = ""
        self.last_status_monotonic = 0.0
        self.last_checkpoint_monotonic = 0.0
        self.current_market = ""
        self.current_close_time = ""

    def maybe_write_status(self, *, status: str = "running") -> None:
        now_mono = time.monotonic()
        if now_mono - self.last_status_monotonic >= self.status_interval_seconds:
            self.last_status_monotonic = now_mono
            self.write_metadata(status=status)

    def raw_event(
        self,
        *,
        event_type: str,
        channel: str,
        market_ticker: str,
        payload: dict[str, Any],
        sequence_number: int | None = None,
        trust_state: str | None = None,
        source: str = "native_passive_ws",
    ) -> dict[str, Any]:
        now = utc_now()
        exchange_ts = payload.get("time") or payload.get("ts") or payload.get("exchange_ts")
        record = {
            "channel": channel,
            "connection_id": self.connection_id,
            "dataset_tag": self.dataset_tag,
            "event_type": event_type,
            "exchange_ts": exchange_ts,
            "local_recv_ns": local_recv_ns(now),
            "local_recv_ts": iso(now),
            "market_ticker": market_ticker,
            "payload_json": payload,
            "recorder_type": "native_passive",
            "recorder_version": RECORDER_VERSION,
            "run_id": self.run_id,
            "sequence_number": sequence_number,
            "source": source,
            "storage_tag": self.bot_tag,
            "trust_state": trust_state or self.orderbook.trust.trust_state,
            "ts_wall": iso(now),
        }
        append_ndjson(raw_event_path(self.raw_root, event_type, now, self.run_id), record)
        self.raw_events_written += 1
        self.counts[event_type] += 1
        self.last_raw_event_ts = record["local_recv_ts"]
        return record

    def checkpoint(self, *, market_ticker: str, reason: str, source_event_count: int | None = None) -> None:
        if not self.orderbook.snapshot_ready:
            return
        now = utc_now()
        yes_prices, yes_sizes = sorted_book(self.orderbook.yes_bids, self.checkpoint_depth)
        no_prices, no_sizes = sorted_book(self.orderbook.no_bids, self.checkpoint_depth)
        record = {
            "checkpoint_ts": iso(now),
            "dataset_tag": self.dataset_tag,
            "event_type": "orderbook_checkpoint",
            "market_ticker": market_ticker,
            "no_bid_prices": no_prices,
            "no_bid_sizes": no_sizes,
            "reason": reason,
            "recorder_type": "native_passive",
            "recorder_version": RECORDER_VERSION,
            "run_id": self.run_id,
            "sequence_number": self.orderbook.last_seq,
            "source_event_count": source_event_count,
            "source": "native_passive_ws",
            "ts_wall": iso(now),
            "yes_bid_prices": yes_prices,
            "yes_bid_sizes": yes_sizes,
            "data_quality_flags": ["native_passive_ws", "full_depth_top_checkpoint"],
        }
        append_ndjson(checkpoint_path(self.checkpoint_root, market_ticker, now, self.run_id), record)
        self.book_checkpoints_written += 1
        self.last_checkpoint_ts = record["checkpoint_ts"]
        self.last_checkpoint_monotonic = time.monotonic()

    def write_metadata(self, *, status: str = "running", error: str = "") -> None:
        self.metadata_root.mkdir(parents=True, exist_ok=True)
        feature_set_version = current_feature_set_version(self.metadata_root)
        existing_backfill_status = self.metadata_root / "live_bot_log_backfill_status.json"
        flags = ["native_passive_ws", "passive_no_order_submission", "full_depth_checkpoints"]
        if existing_backfill_status.exists():
            flags.append("contains_legacy_log_backfill_rows_before_native_recorder")
        records_settlement_labels = any_parquet_rows(self.dataset_root / "trade_labels") or any_parquet_rows(self.dataset_root / "outcome_labels")
        records_execution_events = any_raw_type(self.dataset_root, "execution_")
        strategy_tags = [self.strategy_tag] if self.strategy_tag else []
        payload = {
            "dataset_tag": self.dataset_tag,
            "schema_version": "phase1-ndjson-v1",
            "recorder_version": RECORDER_VERSION,
            "feature_set_version": feature_set_version,
            "recorder_type": "native_passive",
            "strategy_tags": strategy_tags,
            "live_bot_run_tag": self.bot_tag,
            "source_dataset_tag": "",
            "source_log_paths": [],
            "started_at_utc": iso(self.started_at),
            "ended_at_utc": iso(utc_now()),
            "market_tickers": sorted(self.markets),
            "market_selection_reason": "KXBTC15M active market REST discovery + native websocket ticker/orderbook_delta stream",
            "records_raw_market_feed": True,
            "records_book_checkpoints": self.book_checkpoints_written > 0,
            "records_strategy_decisions": records_execution_events,
            "records_execution_events": records_execution_events,
            "records_settlement_labels": records_settlement_labels,
            "data_quality_flags": flags,
            "native_passive_capture_status": status,
            "metadata_refresh_source": "research_native_passive_ws_recorder",
            "updated_at_utc": iso(utc_now()),
        }
        write_json(self.metadata_root / "dataset_manifest.json", payload)
        write_json(
            self.metadata_root / "schema_version.json",
            {
                "schema_version": "phase1-ndjson-v1",
                "dataset_tag": self.dataset_tag,
                "updated_at": iso(utc_now()),
                "recorder_version": RECORDER_VERSION,
            },
        )
        write_json(
            self.metadata_root / "native_passive_recorder_status.json",
            {
                "schema_version": "native-passive-recorder-status-v1",
                "dataset_tag": self.dataset_tag,
                "storage_tag": self.bot_tag,
                "strategy_tag": self.strategy_tag,
                "recorder_version": RECORDER_VERSION,
                "run_id": self.run_id,
                "status": status,
                "error": error,
                "generated_at_utc": iso(utc_now()),
                "started_at_utc": iso(self.started_at),
                "current_market": self.current_market,
                "current_close_time": self.current_close_time,
                "raw_events_written": self.raw_events_written,
                "book_checkpoints_written": self.book_checkpoints_written,
                "event_counts": dict(sorted(self.counts.items())),
                "last_raw_event_ts": self.last_raw_event_ts,
                "last_checkpoint_ts": self.last_checkpoint_ts,
                "markets": sorted(self.markets),
                "connection_id": self.connection_id,
            },
        )

    async def discover_market(self) -> dict[str, Any] | None:
        return await asyncio.to_thread(self.client.get_active_btc15m_market)

    async def active_market_ticker(self) -> str:
        try:
            market = await self.discover_market()
        except Exception as exc:  # noqa: BLE001
            logging.warning("Active market refresh failed inside recorder watch loop: %s", exc)
            self.write_metadata(status="running", error=str(exc))
            return ""
        return str((market or {}).get("ticker") or "")

    async def handle_payload(self, payload: dict[str, Any], market_ticker: str) -> bool:
        msg_type = str(payload.get("type") or "")
        msg = payload.get("msg") if isinstance(payload.get("msg"), dict) else {}
        seq = payload.get("seq")
        sequence_number = int(seq) if isinstance(seq, int) else None
        if msg_type == "subscribed":
            self.raw_event(event_type="ws_subscribed", channel="control", market_ticker=market_ticker, payload=payload, sequence_number=sequence_number)
            return True
        if msg_type == "error":
            self.raw_event(event_type="ws_error", channel="control", market_ticker=market_ticker, payload=payload, sequence_number=sequence_number, trust_state="degraded")
            return True
        if msg_type == "ok":
            return True
        if msg_type == "ticker":
            self.raw_event(event_type="ticker", channel="ticker", market_ticker=market_ticker, payload=enriched_ticker_payload(msg), sequence_number=sequence_number)
            self.maybe_write_status()
            return True
        if msg_type == "orderbook_snapshot":
            self.orderbook.apply_snapshot(msg, sequence_number)
            self.raw_event(event_type="orderbook_snapshot", channel="orderbook_delta", market_ticker=market_ticker, payload=msg, sequence_number=sequence_number)
            self.checkpoint(market_ticker=market_ticker, reason="native_snapshot", source_event_count=self.raw_events_written)
            self.maybe_write_status()
            return True
        if msg_type == "orderbook_delta":
            expected = self.orderbook.last_seq + 1 if self.orderbook.last_seq is not None and sequence_number is not None else None
            self.raw_event(event_type="orderbook_delta", channel="orderbook_delta", market_ticker=market_ticker, payload=enriched_delta_payload(msg), sequence_number=sequence_number)
            if expected is not None and sequence_number != expected:
                self.orderbook.mark_sequence_gap()
                self.raw_event(
                    event_type="book_resync",
                    channel="control",
                    market_ticker=market_ticker,
                    payload={"market_ticker": market_ticker, "expected_seq": expected, "got_seq": sequence_number, "reason": "sequence_gap"},
                    sequence_number=sequence_number,
                    trust_state="degraded",
                )
                self.maybe_write_status(status="reconnecting")
                return False
            self.orderbook.apply_delta(msg, sequence_number)
            if time.monotonic() - self.last_checkpoint_monotonic >= self.checkpoint_interval_seconds:
                self.checkpoint(market_ticker=market_ticker, reason="native_periodic", source_event_count=self.raw_events_written)
            self.maybe_write_status()
            return True
        self.raw_event(event_type="ws_unhandled", channel="control", market_ticker=market_ticker, payload=payload, sequence_number=sequence_number)
        return True

    async def watch_market(self, market: dict[str, Any]) -> None:
        market_ticker = str(market.get("ticker") or "")
        if not market_ticker:
            return
        close_time = str(market.get("close_time") or "")
        strike = parse_btc_strike_from_market(market)
        self.current_market = market_ticker
        self.current_close_time = close_time
        self.markets.add(market_ticker)
        self.orderbook.reset(market_ticker, trust_state="cold")
        self.raw_event(
            event_type="watch_market",
            channel="control",
            market_ticker=market_ticker,
            payload={
                "market_ticker": market_ticker,
                "close_time": close_time,
                "status": market.get("status"),
                "strike": strike,
            },
            trust_state="cold",
        )
        self.write_metadata(status="running")
        logging.info("Watching market %s close_time=%s status=%s strike=%s", market_ticker, close_time, market.get("status"), strike)

        last_market_check = 0.0
        while not self.shutdown_event.is_set():
            headers = self.client.websocket_headers()
            try:
                async with websockets.connect(
                    self.config.ws_url,
                    additional_headers=headers,
                    ping_interval=20,
                    ping_timeout=20,
                    max_size=2**20,
                ) as ws:
                    self.raw_event(event_type="ws_connected", channel="control", market_ticker=market_ticker, payload={"market_ticker": market_ticker})
                    sub_msg = {
                        "id": 1,
                        "cmd": "subscribe",
                        "params": {
                            "channels": ["ticker", "orderbook_delta"],
                            "market_ticker": market_ticker,
                        },
                    }
                    await ws.send(json.dumps(sub_msg))
                    while not self.shutdown_event.is_set():
                        now_mono = time.monotonic()
                        if now_mono - last_market_check >= self.market_refresh_seconds:
                            last_market_check = now_mono
                            active_ticker = await self.active_market_ticker()
                            if active_ticker and active_ticker != market_ticker:
                                self.raw_event(
                                    event_type="market_rotated",
                                    channel="control",
                                    market_ticker=market_ticker,
                                    payload={"previous_market_ticker": market_ticker, "active_market_ticker": active_ticker},
                                )
                                return
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        except asyncio.TimeoutError:
                            if now_mono - self.last_status_monotonic >= self.status_interval_seconds:
                                self.last_status_monotonic = now_mono
                                self.write_metadata(status="running")
                            continue
                        msg = json.loads(raw)
                        keep_connection = await self.handle_payload(msg, market_ticker)
                        if not keep_connection:
                            return
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logging.warning("Native passive WS loop error for %s: %s", market_ticker, exc)
                self.write_metadata(status="reconnecting", error=str(exc))
                await asyncio.sleep(1.0)

    async def run(self) -> None:
        self.write_metadata(status="starting")
        while not self.shutdown_event.is_set():
            try:
                market = await self.discover_market()
            except Exception as exc:  # noqa: BLE001
                logging.warning("Market discovery failed. Recorder will retry. error=%s", exc)
                self.raw_event(
                    event_type="market_discovery_error",
                    channel="control",
                    market_ticker="",
                    payload={"series_ticker": self.config.series_ticker, "error": str(exc)},
                    trust_state="cold",
                )
                self.write_metadata(status="waiting_for_market", error=str(exc))
                await asyncio.sleep(max(5.0, self.market_refresh_seconds))
                continue
            if not market:
                self.raw_event(
                    event_type="market_discovery_empty",
                    channel="control",
                    market_ticker="",
                    payload={"series_ticker": self.config.series_ticker},
                    trust_state="cold",
                )
                self.write_metadata(status="waiting_for_market")
                await asyncio.sleep(self.market_refresh_seconds)
                continue
            await self.watch_market(market)
        self.write_metadata(status="stopped")


def setup_logging(dataset_tag: str) -> None:
    log_dir = ROOT / "logs" / dataset_tag
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "native_passive_ws_recorder.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Native passive Kalshi websocket recorder for Research Lab datasets.")
    parser.add_argument("--dataset", default="live_liquidity_dwell_size2")
    parser.add_argument("--strategy-tag", default="liquidity_dwell_p05_q065_hold")
    parser.add_argument("--bot-tag", default="live_liquidity_dwell_size2")
    parser.add_argument("--checkpoint-interval-seconds", type=float, default=5.0)
    parser.add_argument("--market-refresh-seconds", type=float, default=10.0)
    parser.add_argument("--checkpoint-depth", type=int, default=25)
    parser.add_argument("--status-interval-seconds", type=float, default=15.0)
    parser.add_argument("--run-id", default="")
    parser.add_argument(
        "--run-seconds",
        type=float,
        default=None,
        help="Optional research smoke duration; recorder stops itself after this many seconds.",
    )
    return parser.parse_args()


async def async_main() -> int:
    args = parse_args()
    setup_logging(args.dataset)
    run_id = args.run_id or str(uuid.uuid4())
    recorder = NativePassiveRecorder(
        dataset_tag=args.dataset,
        strategy_tag=args.strategy_tag,
        bot_tag=args.bot_tag,
        checkpoint_interval_seconds=max(1.0, args.checkpoint_interval_seconds),
        market_refresh_seconds=max(1.0, args.market_refresh_seconds),
        checkpoint_depth=max(1, args.checkpoint_depth),
        status_interval_seconds=max(1.0, args.status_interval_seconds),
        run_id=run_id,
    )
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, recorder.shutdown_event.set)
    logging.info("Starting native passive recorder. run_id=%s dataset=%s ws_url=%s", run_id, args.dataset, recorder.config.ws_url)
    stop_task: asyncio.Task[None] | None = None
    if args.run_seconds is not None:
        async def stop_after_delay() -> None:
            await asyncio.sleep(max(0.1, float(args.run_seconds)))
            recorder.shutdown_event.set()

        stop_task = asyncio.create_task(stop_after_delay())
    try:
        await recorder.run()
    finally:
        if stop_task is not None:
            stop_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await stop_task
        recorder.write_metadata(status="stopped")
    return 0


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())
