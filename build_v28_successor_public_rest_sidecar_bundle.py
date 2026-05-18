"""Build a v28 successor sidecar input bundle from public REST snapshots.

Research-only. The default mode uses an offline fixture so the normal refresh
pipeline stays deterministic. The optional public REST mode fetches current
Kalshi market/orderbook data and recent BTC candles, computes a local v28
EdgeBatch, and writes a sidecar input bundle that can be frozen before close.

This script never reads or writes live bot state, thresholds, secrets, orders,
or processes.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28
from build_v28_successor_forward_packet_adapter import collection_manifests, demo_btc_history
from collect_v28_successor_forward_packets import demo_market_and_checkpoint, packet_rows_from_input_bundle
from validate_v28_successor_sidecar_input_bundle import serialize_edge_batch, validate_bundle


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

DEFAULT_KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
DEFAULT_COINBASE_BASE_URL = "https://api.exchange.coinbase.com"
DEFAULT_SERIES_TICKER = "KXBTC15M"

DEMO_BUNDLE_JSON = OUT_DIR / "public_rest_sidecar_bundle_demo_latest.json"
AUDIT_JSON = EDGE_DIR / "v28_successor_public_rest_sidecar_bundle_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_public_rest_sidecar_bundle_latest.md"
DEFAULT_BUNDLE_DIR = OUT_DIR / "sidecar_input_bundles"


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def http_json(url: str, *, timeout_seconds: float = 10.0) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "v28-successor-research-sidecar/1.0"})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(base_url: str, endpoint: str, params: dict[str, Any] | None = None, *, timeout_seconds: float = 10.0) -> Any:
    query = urllib.parse.urlencode({key: value for key, value in (params or {}).items() if value is not None})
    url = base_url.rstrip("/") + endpoint
    if query:
        url = f"{url}?{query}"
    return http_json(url, timeout_seconds=timeout_seconds)


def parse_btc_strike(market: dict[str, Any]) -> float | None:
    for key in ("strike", "floor_strike", "cap_strike", "custom_strike", "subtitle"):
        parsed = as_float(market.get(key))
        if parsed is not None:
            return parsed
    ticker = market_ticker(market)
    ticker_match = re.search(r"-T(\d+(?:\.\d+)?)", ticker)
    if ticker_match:
        parsed = as_float(ticker_match.group(1))
        if parsed is not None:
            return parsed
    for key in ("title", "subtitle", "rules_primary", "yes_sub_title", "no_sub_title"):
        text = str(market.get(key) or "")
        for match in re.findall(r"\$?\b\d{2,3}(?:,\d{3})+(?:\.\d+)?\b|\$?\b\d{5,6}(?:\.\d+)?\b", text):
            parsed = as_float(match.replace("$", ""))
            if parsed is not None:
                return parsed
    return None


def market_close_ts(market: dict[str, Any]) -> str:
    for key in ("market_close_ts_utc", "close_time", "close_ts", "expected_expiration_time", "expiration_time"):
        parsed = parse_ts(market.get(key))
        if parsed is not None:
            return iso_z(parsed)
    return ""


def market_ticker(market: dict[str, Any]) -> str:
    return str(market.get("ticker") or market.get("market_ticker") or "").strip()


def select_active_market(markets_payload: Any, *, now_utc: datetime) -> dict[str, Any] | None:
    markets = markets_payload.get("markets") if isinstance(markets_payload, dict) else markets_payload
    if not isinstance(markets, list):
        return None
    candidates: list[tuple[datetime, dict[str, Any]]] = []
    for row in markets:
        if not isinstance(row, dict):
            continue
        ticker = market_ticker(row)
        if not ticker.startswith("KXBTC15M-"):
            continue
        close_ts = parse_ts(market_close_ts(row))
        if close_ts is None or close_ts <= now_utc:
            continue
        if parse_btc_strike(row) is None:
            continue
        candidates.append((close_ts, row))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def fetch_active_market(
    *,
    kalshi_base_url: str,
    series_ticker: str,
    now_utc: datetime,
    timeout_seconds: float,
) -> dict[str, Any]:
    for status in ("active", "open", "initialized", None):
        try:
            payload = get_json(
                kalshi_base_url,
                "/markets",
                {"series_ticker": series_ticker, "status": status, "limit": 100},
                timeout_seconds=timeout_seconds,
            )
        except urllib.error.HTTPError:
            if status is not None:
                continue
            raise
        market = select_active_market(payload, now_utc=now_utc)
        if market is not None:
            return market
    raise RuntimeError("no active BTC 15m market found in public Kalshi response")


def fetch_orderbook(*, kalshi_base_url: str, ticker: str, timeout_seconds: float) -> dict[str, Any]:
    payload = get_json(kalshi_base_url, f"/markets/{urllib.parse.quote(ticker, safe='')}/orderbook", timeout_seconds=timeout_seconds)
    orderbook = payload.get("orderbook") if isinstance(payload, dict) else None
    if not isinstance(orderbook, dict) and isinstance(payload, dict):
        orderbook = payload.get("orderbook_fp")
    if not isinstance(orderbook, dict):
        raise RuntimeError("Kalshi orderbook response missing orderbook object")
    return orderbook


def fetch_coinbase_candles(
    *,
    coinbase_base_url: str,
    now_utc: datetime,
    minutes: int,
    timeout_seconds: float,
) -> list[Any]:
    # Coinbase returns at most 300 buckets per candle request.
    request_minutes = max(1, min(int(minutes), 299))
    start = now_utc - timedelta(minutes=request_minutes)
    payload = get_json(
        coinbase_base_url,
        "/products/BTC-USD/candles",
        {
            "granularity": 60,
            "start": start.isoformat().replace("+00:00", "Z"),
            "end": now_utc.isoformat().replace("+00:00", "Z"),
        },
        timeout_seconds=timeout_seconds,
    )
    if not isinstance(payload, list):
        raise RuntimeError("Coinbase candle response was not a list")
    return payload


def orderbook_side_levels(side: Any) -> list[tuple[float, float]]:
    levels: list[tuple[float, float]] = []
    if not isinstance(side, list):
        return levels
    for level in side:
        price = None
        size = None
        if isinstance(level, list) and len(level) >= 2:
            price = as_float(level[0])
            size = as_float(level[1])
        elif isinstance(level, dict):
            price = as_float(level.get("price") or level.get("price_cents") or level.get("yes_bid") or level.get("no_bid"))
            size = as_float(level.get("quantity") or level.get("count") or level.get("size"))
        if price is None or size is None:
            continue
        if 0.0 < price <= 1.0:
            price *= 100.0
        levels.append((price, size))
    levels.sort(key=lambda item: item[0], reverse=True)
    return levels


def checkpoint_from_orderbook(*, market: dict[str, Any], orderbook: dict[str, Any], now_utc: datetime) -> dict[str, Any]:
    yes_levels = orderbook_side_levels(orderbook.get("yes") or orderbook.get("yes_dollars"))
    no_levels = orderbook_side_levels(orderbook.get("no") or orderbook.get("no_dollars"))
    if not yes_levels:
        yes_levels = [(0.0, 0.0)]
    if not no_levels:
        no_levels = [(0.0, 0.0)]
    return {
        "checkpoint_ts": iso_z(now_utc),
        "market_ticker": market_ticker(market),
        "yes_bid_prices": [price for price, _size in yes_levels],
        "yes_bid_sizes": [size for _price, size in yes_levels],
        "no_bid_prices": [price for price, _size in no_levels],
        "no_bid_sizes": [size for _price, size in no_levels],
        "sequence_number": orderbook.get("sequence_number") or orderbook.get("seq") or "",
        "source_event_count": 1,
        "source": "kalshi_public_rest_orderbook",
    }


def btc_rows_from_candles(candles: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candle in candles:
        if not isinstance(candle, list) or len(candle) < 5:
            continue
        ts = as_float(candle[0])
        low = as_float(candle[1])
        high = as_float(candle[2])
        open_ = as_float(candle[3])
        close = as_float(candle[4])
        volume = as_float(candle[5]) if len(candle) > 5 else 0.0
        if ts is None or low is None or high is None or open_ is None or close is None:
            continue
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        rows.append(
            {
                "ts_utc": iso_z(dt),
                "price": close,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": 0.0 if volume is None else volume,
                "source": "coinbase_public_candles_1m",
            }
        )
    rows.sort(key=lambda row: str(row["ts_utc"]))
    return rows


def edge_batch_from_btc_rows(*, btc_rows: list[dict[str, Any]], market: dict[str, Any], checkpoint: dict[str, Any]) -> Any:
    engine = FastMushroomFVEngineV28()
    for row in btc_rows:
        engine.update_bar(
            open=float(row.get("open") or row.get("price")),
            high=float(row.get("high") or row.get("price")),
            low=float(row.get("low") or row.get("price")),
            close=float(row.get("close") or row.get("price")),
            volume=float(row.get("volume") or 0.0),
            ts=parse_ts(row.get("ts_utc")),
        )
    if not btc_rows:
        raise RuntimeError("missing BTC rows")
    last = btc_rows[-1]
    engine.update_tick(float(last["price"]), parse_ts(last["ts_utc"]), volume=float(last.get("volume") or 0.0))
    if not engine.ready():
        raise RuntimeError(f"v28 engine not ready from BTC rows: rows={len(btc_rows)}")

    strike = parse_btc_strike(market)
    close_ts = parse_ts(market_close_ts(market))
    decision_ts = parse_ts(checkpoint.get("checkpoint_ts"))
    yes_bid = checkpoint["yes_bid_prices"][0] if checkpoint.get("yes_bid_prices") else None
    no_bid = checkpoint["no_bid_prices"][0] if checkpoint.get("no_bid_prices") else None
    if strike is None or close_ts is None or decision_ts is None:
        raise RuntimeError("missing market strike or timestamps for v28 edge batch")
    if yes_bid is None or no_bid is None:
        raise RuntimeError("missing top yes/no bid for v28 edge batch")
    horizon_seconds = max(1.0, (close_ts - decision_ts).total_seconds())
    return engine.edge_many(
        strikes=[float(strike)],
        horizon_seconds=horizon_seconds,
        yes_ask_cents=[100.0 - float(no_bid)],
        no_ask_cents=[100.0 - float(yes_bid)],
    )


def build_bundle_from_inputs(
    *,
    market_payload: dict[str, Any],
    orderbook_payload: dict[str, Any],
    candle_payload: list[Any],
    now_utc: datetime,
    simulated: bool,
    diagnostic_only: bool,
) -> dict[str, Any]:
    market = {
        "market_ticker": market_ticker(market_payload),
        "market_close_ts_utc": market_close_ts(market_payload),
        "strike": parse_btc_strike(market_payload),
        "market_source": "kalshi_public_rest_market",
    }
    for key in (
        "strike_source",
        "strike_source_market_ticker",
        "strike_source_market_close_ts_utc",
        "strike_source_market_status",
    ):
        if market_payload.get(key):
            market[key] = market_payload[key]
    checkpoint = checkpoint_from_orderbook(market=market, orderbook=orderbook_payload, now_utc=now_utc)
    btc_rows = btc_rows_from_candles(candle_payload)
    edge_batch = edge_batch_from_btc_rows(btc_rows=btc_rows, market=market, checkpoint=checkpoint)
    edge_payload = serialize_edge_batch(edge_batch)
    if edge_payload.get("p_no") is None and isinstance(edge_payload.get("p_yes"), list):
        edge_payload["p_no"] = [1.0 - float(value) for value in edge_payload["p_yes"]]
    return {
        "bundle_schema": "v28_successor_sidecar_input_bundle_v1",
        "registered_utc": iso_z(now_utc),
        "simulated": simulated,
        "diagnostic_only": diagnostic_only,
        "source_mode": "public_rest_snapshot",
        "market": market,
        "checkpoint": checkpoint,
        "btc_history_rows": btc_rows,
        "edge_batch": edge_payload,
        "candidate_manifests": collection_manifests(),
        "notes": [
            "Research-only public REST sidecar bundle.",
            "Real rows must be written before close and frozen before resolution.",
            "This bundle alone is not promotion evidence.",
        ],
    }


def fixture_payloads() -> tuple[dict[str, Any], dict[str, Any], list[Any], datetime]:
    market, checkpoint, _registered_utc = demo_market_and_checkpoint()
    decision = parse_ts(checkpoint["checkpoint_ts"]) or datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
    candles: list[Any] = []
    base_price = 99940.0
    for index in range(240):
        ts = decision - timedelta(minutes=239 - index)
        wave = 38.0 * math.sin(index / 13.0) + 18.0 * math.sin(index / 5.0)
        trend = 0.32 * index
        close = base_price + trend + wave
        open_ = close - 2.0 * math.sin(index / 7.0)
        high = max(open_, close) + 8.0
        low = min(open_, close) - 8.0
        candles.append([int(ts.timestamp()), low, high, open_, close, 1.0])
    return (
        {"ticker": market["market_ticker"], "close_time": market["market_close_ts_utc"], "strike": market["strike"]},
        {"yes": [[52, 120]], "no": [[46, 95]], "sequence_number": checkpoint["sequence_number"]},
        candles,
        decision,
    )


def output_bundle_path(bundle: dict[str, Any], *, output_dir: Path = DEFAULT_BUNDLE_DIR) -> Path:
    ticker = re.sub(r"[^A-Za-z0-9_.-]+", "_", str((bundle.get("market") or {}).get("market_ticker") or "unknown"))
    ts = str(bundle.get("registered_utc") or "unknown").replace(":", "").replace("-", "").replace(".", "")
    return output_dir / f"{ts}_{ticker}.json"


def build(
    *,
    mode: str = "fixture",
    kalshi_base_url: str = DEFAULT_KALSHI_BASE_URL,
    coinbase_base_url: str = DEFAULT_COINBASE_BASE_URL,
    series_ticker: str = DEFAULT_SERIES_TICKER,
    now_utc: datetime | None = None,
    btc_minutes: int = 300,
    timeout_seconds: float = 10.0,
    output_json: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    now_utc = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if mode == "fixture":
        market_payload, orderbook_payload, candle_payload, fixture_now = fixture_payloads()
        now_utc = fixture_now
        simulated = True
        diagnostic_only = True
        default_output = DEMO_BUNDLE_JSON
    elif mode == "public_rest":
        market_payload = fetch_active_market(
            kalshi_base_url=kalshi_base_url,
            series_ticker=series_ticker,
            now_utc=now_utc,
            timeout_seconds=timeout_seconds,
        )
        orderbook_payload = fetch_orderbook(kalshi_base_url=kalshi_base_url, ticker=market_ticker(market_payload), timeout_seconds=timeout_seconds)
        candle_payload = fetch_coinbase_candles(
            coinbase_base_url=coinbase_base_url,
            now_utc=now_utc,
            minutes=btc_minutes,
            timeout_seconds=timeout_seconds,
        )
        simulated = False
        diagnostic_only = False
        default_output = output_bundle_path(
            {"registered_utc": iso_z(now_utc), "market": {"market_ticker": market_ticker(market_payload)}},
            output_dir=DEFAULT_BUNDLE_DIR,
        )
    else:
        raise ValueError("mode must be fixture or public_rest")

    bundle = build_bundle_from_inputs(
        market_payload=market_payload,
        orderbook_payload=orderbook_payload,
        candle_payload=candle_payload,
        now_utc=now_utc,
        simulated=simulated,
        diagnostic_only=diagnostic_only,
    )
    details, contract_summary = validate_bundle(bundle)
    packet_rows: list[dict[str, Any]] = []
    packet_error = ""
    if contract_summary.get("bundle_ready"):
        try:
            packet_rows = packet_rows_from_input_bundle(input_bundle=bundle, source_file="public_rest_sidecar_bundle", source_line_or_offset=mode)
        except Exception as exc:  # noqa: BLE001
            packet_error = str(exc)
    output_path = output_json or default_output
    status = contract_summary.get("bundle_status")
    if packet_error:
        status = "blocked_packet_materialization_failed"
    summary = {
        "generated_utc": iso_z(datetime.now(timezone.utc).replace(microsecond=0)),
        "builder_script": Path(__file__).name,
        "mode": mode,
        "bundle_status": status,
        "bundle_ready": contract_summary.get("bundle_ready") and not packet_error,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "public REST sidecar bundles are collector inputs only; promotion requires freeze before close, labels after resolution, source contract, forward evidence scoring, and verifier approval",
        },
        "market_ticker": contract_summary.get("market_ticker"),
        "decision_ts_utc": contract_summary.get("decision_ts_utc"),
        "market_close_ts_utc": contract_summary.get("market_close_ts_utc"),
        "registered_utc": contract_summary.get("registered_utc"),
        "simulated": simulated,
        "diagnostic_only": diagnostic_only,
        "btc_history_rows": contract_summary.get("btc_history_rows"),
        "packet_rows": len(packet_rows),
        "packet_error": packet_error,
        "blocker_counts": contract_summary.get("blocker_counts"),
        "output_bundle_json": rel_path(output_path),
        "public_sources": {
            "kalshi_markets_endpoint": f"{kalshi_base_url.rstrip('/')}/markets",
            "kalshi_orderbook_endpoint": f"{kalshi_base_url.rstrip('/')}/markets/{{ticker}}/orderbook",
            "coinbase_candles_endpoint": f"{coinbase_base_url.rstrip('/')}/products/BTC-USD/candles",
        },
        "outputs": {
            "bundle_json": rel_path(output_path),
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
        },
    }
    return {"summary": summary, "contract_details": details[:100], "contract_summary": contract_summary}, bundle


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Public REST Sidecar Bundle",
        "",
        "Research-only one-shot sidecar bundle builder. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Mode: `{summary['mode']}`",
        f"- Bundle status: `{summary['bundle_status']}`",
        f"- Bundle ready: `{summary['bundle_ready']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Market: `{summary['market_ticker']}`",
        f"- Decision UTC: `{summary['decision_ts_utc']}`",
        f"- Close UTC: `{summary['market_close_ts_utc']}`",
        f"- BTC history rows: `{summary['btc_history_rows']}`",
        f"- Packet rows materialized: `{summary['packet_rows']}`",
        f"- Output bundle: `{summary['output_bundle_json']}`",
        "",
        "## Blockers",
        "",
    ]
    blockers = summary.get("blocker_counts") or {}
    if blockers:
        for blocker, count in blockers.items():
            lines.append(f"- `{blocker}`: `{count}`")
    else:
        lines.append("- None recorded by the bundle contract.")
    if summary.get("packet_error"):
        lines.append(f"- `packet_error`: `{summary['packet_error']}`")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Fixture mode is deterministic and diagnostic only.",
            "- Public REST mode writes non-simulated sidecar bundles only when explicitly requested.",
            "- A ready bundle still must be frozen before close, labeled after resolution, scored, source-checked, and verifier-approved.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any], bundle: dict[str, Any], output_json: Path | None = None) -> None:
    summary = report["summary"]
    bundle_path = output_json or (ROOT / str(summary["output_bundle_json"]))
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["fixture", "public-rest"], default="fixture")
    parser.add_argument("--kalshi-base-url", default=DEFAULT_KALSHI_BASE_URL)
    parser.add_argument("--coinbase-base-url", default=DEFAULT_COINBASE_BASE_URL)
    parser.add_argument("--series-ticker", default=DEFAULT_SERIES_TICKER)
    parser.add_argument("--btc-minutes", type=int, default=300)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--now-utc", default="")
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now_utc = parse_ts(args.now_utc) if args.now_utc else None
    report, bundle = build(
        mode=args.mode.replace("-", "_"),
        kalshi_base_url=args.kalshi_base_url,
        coinbase_base_url=args.coinbase_base_url,
        series_ticker=args.series_ticker,
        now_utc=now_utc,
        btc_minutes=args.btc_minutes,
        timeout_seconds=args.timeout_seconds,
        output_json=args.output_json,
    )
    if args.write and not args.dry_run:
        write_outputs(report, bundle, args.output_json)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "mode": summary["mode"],
                "bundle_status": summary["bundle_status"],
                "bundle_ready": summary["bundle_ready"],
                "market_ticker": summary["market_ticker"],
                "packet_rows": summary["packet_rows"],
                "promotion_allowed": summary["promotion_allowed"],
                "output_bundle_json": summary["output_bundle_json"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
