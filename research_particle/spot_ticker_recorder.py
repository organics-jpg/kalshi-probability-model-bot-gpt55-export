from __future__ import annotations

import argparse
import asyncio
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import websockets


BINANCE_BTCUSDT_TRADE_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"
COINBASE_BTCUSD_MATCH_URL = "wss://ws-feed.exchange.coinbase.com"


class SpotTickerRecorderError(ValueError):
    pass


class SpotTickerRecorderSkip(ValueError):
    pass


@dataclass(frozen=True)
class SpotTick:
    schema_version: str
    source: str
    symbol: str
    price: float
    exchange_ts_utc: str
    local_recv_ts_utc: str
    local_recv_ns: int
    trade_id: str
    raw_event_type: str


@dataclass(frozen=True)
class SpotTickerRecorderStatus:
    schema_version: str
    source: str
    url: str
    output: str
    issues: str
    status: str
    ticks_written: int
    issue_count: int
    started_at_utc: str
    ended_at_utc: str
    last_tick_ts_utc: str
    error: str


def parse_binance_trade_message(
    payload: Mapping[str, Any],
    *,
    local_recv_ts_utc: datetime,
    source: str = "binance_btcusdt_trade",
) -> SpotTick:
    event_type = str(payload.get("e") or "")
    if event_type not in {"trade", "aggTrade"}:
        raise SpotTickerRecorderError(f"unsupported Binance event type: {event_type}")
    raw_price = payload.get("p")
    raw_symbol = payload.get("s")
    if raw_price in (None, ""):
        raise SpotTickerRecorderError("Binance trade message missing price")
    if raw_symbol in (None, ""):
        raise SpotTickerRecorderError("Binance trade message missing symbol")
    exchange_ms = payload.get("T") or payload.get("E")
    if exchange_ms in (None, ""):
        raise SpotTickerRecorderError("Binance trade message missing exchange timestamp")
    trade_id = payload.get("t", payload.get("a", ""))
    exchange_ts = datetime.fromtimestamp(float(exchange_ms) / 1000.0, tz=timezone.utc)
    local_ts = _to_utc(local_recv_ts_utc)
    return SpotTick(
        schema_version="spot-tick-v1",
        source=source,
        symbol=str(raw_symbol),
        price=float(raw_price),
        exchange_ts_utc=exchange_ts.isoformat(),
        local_recv_ts_utc=local_ts.isoformat(),
        local_recv_ns=int(local_ts.timestamp() * 1_000_000_000),
        trade_id=str(trade_id),
        raw_event_type=event_type,
    )


def parse_coinbase_match_message(
    payload: Mapping[str, Any],
    *,
    local_recv_ts_utc: datetime,
    source: str = "coinbase_btcusd_matches",
) -> SpotTick:
    event_type = str(payload.get("type") or "")
    if event_type in {"subscriptions", "heartbeat"}:
        raise SpotTickerRecorderSkip(event_type)
    if event_type not in {"match", "last_match"}:
        raise SpotTickerRecorderError(f"unsupported Coinbase event type: {event_type}")
    raw_price = payload.get("price")
    raw_symbol = payload.get("product_id")
    exchange_time = payload.get("time")
    if raw_price in (None, ""):
        raise SpotTickerRecorderError("Coinbase match message missing price")
    if raw_symbol in (None, ""):
        raise SpotTickerRecorderError("Coinbase match message missing product_id")
    if exchange_time in (None, ""):
        raise SpotTickerRecorderError("Coinbase match message missing time")
    exchange_ts = _parse_ts(exchange_time)
    local_ts = _to_utc(local_recv_ts_utc)
    return SpotTick(
        schema_version="spot-tick-v1",
        source=source,
        symbol=str(raw_symbol),
        price=float(raw_price),
        exchange_ts_utc=exchange_ts.isoformat(),
        local_recv_ts_utc=local_ts.isoformat(),
        local_recv_ns=int(local_ts.timestamp() * 1_000_000_000),
        trade_id=str(payload.get("trade_id", "")),
        raw_event_type=event_type,
    )


def parse_spot_message(
    payload: Mapping[str, Any],
    *,
    feed: str,
    local_recv_ts_utc: datetime,
    source: str,
) -> SpotTick:
    if feed == "binance":
        return parse_binance_trade_message(
            payload,
            local_recv_ts_utc=local_recv_ts_utc,
            source=source,
        )
    if feed == "coinbase":
        return parse_coinbase_match_message(
            payload,
            local_recv_ts_utc=local_recv_ts_utc,
            source=source,
        )
    raise SpotTickerRecorderError(f"unsupported spot feed: {feed}")


async def record_spot_ticks(
    *,
    output_path: Path,
    issue_path: Path,
    status_path: Path,
    url: str | None = None,
    source: str | None = None,
    feed: str = "coinbase",
    run_seconds: float = 30.0,
    max_rows: int | None = None,
) -> SpotTickerRecorderStatus:
    url = url or _default_url(feed)
    source = source or _default_source(feed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    ticks_written = 0
    issue_count = 0
    last_tick_ts = ""
    error = ""
    deadline = time.monotonic() + max(0.1, float(run_seconds))
    status = "stopped"
    reconnect_count = 0
    with output_path.open("w", encoding="utf-8", newline="\n") as out, issue_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as bad:
        while time.monotonic() < deadline:
            if max_rows is not None and ticks_written >= max_rows:
                status = "max_rows_reached"
                break
            try:
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=20,
                    max_size=2**20,
                ) as ws:
                    subscribe = _subscribe_payload(feed)
                    if subscribe is not None:
                        await ws.send(json.dumps(subscribe, sort_keys=True))
                    while time.monotonic() < deadline:
                        if max_rows is not None and ticks_written >= max_rows:
                            status = "max_rows_reached"
                            break
                        timeout = max(0.05, min(1.0, deadline - time.monotonic()))
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                        except asyncio.TimeoutError:
                            continue
                        local_recv = datetime.now(timezone.utc)
                        try:
                            payload = json.loads(raw)
                            if not isinstance(payload, dict):
                                raise SpotTickerRecorderError("websocket payload is not a JSON object")
                            tick = parse_spot_message(
                                payload,
                                feed=feed,
                                local_recv_ts_utc=local_recv,
                                source=source,
                            )
                            out.write(json.dumps(asdict(tick), sort_keys=True) + "\n")
                            ticks_written += 1
                            last_tick_ts = tick.exchange_ts_utc
                        except SpotTickerRecorderSkip:
                            continue
                        except Exception as exc:
                            issue_count += 1
                            bad.write(
                                json.dumps(
                                    {
                                        "reason": str(exc),
                                        "raw": raw[:500] if isinstance(raw, str) else "",
                                        "local_recv_ts_utc": local_recv.isoformat(),
                                    },
                                    sort_keys=True,
                                )
                                + "\n"
                            )
                    if status == "max_rows_reached":
                        break
            except Exception as exc:
                reconnect_count += 1
                error = str(exc)
                issue_count += 1
                bad.write(
                    json.dumps(
                        {
                            "phase": "websocket_reconnect",
                            "reason": error,
                            "reconnect_count": reconnect_count,
                            "local_recv_ts_utc": datetime.now(timezone.utc).isoformat(),
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
                if time.monotonic() >= deadline:
                    break
                await asyncio.sleep(min(5.0, max(0.1, deadline - time.monotonic())))
        if status != "max_rows_reached" and error:
            if ticks_written <= 0:
                status = "error"
            else:
                status = "stopped_after_reconnect"
                error = f"reconnect_count={reconnect_count}; last_error={error}"
    return _write_status(
        status_path,
        source=source,
        url=url,
        output_path=output_path,
        issue_path=issue_path,
        status=status,
        ticks_written=ticks_written,
        issue_count=issue_count,
        started_at_utc=started,
        last_tick_ts=last_tick_ts,
        error=error,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only public BTC spot ticker recorder for particle shadow context."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--issues", required=True, type=Path)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--feed", default="coinbase", choices=("coinbase", "binance"))
    parser.add_argument("--url", default=None)
    parser.add_argument("--source", default=None)
    parser.add_argument("--run-seconds", default=30.0, type=float)
    parser.add_argument("--max-rows", default=None, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    status = asyncio.run(
        record_spot_ticks(
            output_path=args.output,
            issue_path=args.issues,
            status_path=args.status,
            url=args.url,
            source=args.source,
            feed=args.feed,
            run_seconds=args.run_seconds,
            max_rows=args.max_rows,
        )
    )
    print(f"status={status.status}")
    print(f"ticks_written={status.ticks_written}")
    print(f"issue_count={status.issue_count}")
    print(f"output={status.output}")
    print(f"issues={status.issues}")
    print(f"status_path={args.status}")
    return 0 if status.status != "error" else 1


def _write_status(
    status_path: Path,
    *,
    source: str,
    url: str,
    output_path: Path,
    issue_path: Path,
    status: str,
    ticks_written: int,
    issue_count: int,
    started_at_utc: datetime,
    last_tick_ts: str,
    error: str,
) -> SpotTickerRecorderStatus:
    payload = SpotTickerRecorderStatus(
        schema_version="spot-ticker-recorder-status-v1",
        source=source,
        url=url,
        output=str(output_path),
        issues=str(issue_path),
        status=status,
        ticks_written=ticks_written,
        issue_count=issue_count,
        started_at_utc=started_at_utc.isoformat(),
        ended_at_utc=datetime.now(timezone.utc).isoformat(),
        last_tick_ts_utc=last_tick_ts,
        error=error,
    )
    status_path.write_text(json.dumps(asdict(payload), indent=2, sort_keys=True), encoding="utf-8")
    return payload


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _parse_ts(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return _to_utc(parsed)


def _default_url(feed: str) -> str:
    if feed == "coinbase":
        return COINBASE_BTCUSD_MATCH_URL
    if feed == "binance":
        return BINANCE_BTCUSDT_TRADE_URL
    raise SpotTickerRecorderError(f"unsupported spot feed: {feed}")


def _default_source(feed: str) -> str:
    if feed == "coinbase":
        return "coinbase_btcusd_matches"
    if feed == "binance":
        return "binance_btcusdt_trade"
    raise SpotTickerRecorderError(f"unsupported spot feed: {feed}")


def _subscribe_payload(feed: str) -> dict[str, Any] | None:
    if feed == "coinbase":
        return {
            "type": "subscribe",
            "product_ids": ["BTC-USD"],
            "channels": ["matches"],
        }
    if feed == "binance":
        return None
    raise SpotTickerRecorderError(f"unsupported spot feed: {feed}")


if __name__ == "__main__":
    raise SystemExit(main())
