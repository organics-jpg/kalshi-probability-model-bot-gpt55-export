"""Build v28 successor sidecar input bundles for active BTC15M markets.

Research-only. Fixture mode is deterministic and writes no promotion evidence.
Public REST mode fetches the active Kalshi BTC 15m boundary market set, one
orderbook per selected market, and one shared BTC candle window, then writes
non-simulated sidecar input bundle JSON files that can be frozen before close.

This script never reads or writes live bot state, thresholds, secrets, orders,
or processes.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from build_v28_successor_public_rest_sidecar_bundle import (
    DEFAULT_BUNDLE_DIR,
    DEFAULT_COINBASE_BASE_URL,
    DEFAULT_KALSHI_BASE_URL,
    DEFAULT_SERIES_TICKER,
    as_float,
    build_bundle_from_inputs,
    fetch_coinbase_candles,
    fetch_orderbook,
    fixture_payloads,
    get_json,
    iso_z,
    market_close_ts,
    market_ticker,
    output_bundle_path,
    parse_btc_strike,
    parse_ts,
    rel_path,
)
from collect_v28_successor_forward_packets import packet_rows_from_input_bundle
from validate_v28_successor_sidecar_input_bundle import validate_bundle


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

DEMO_BATCH_JSON = OUT_DIR / "public_rest_sidecar_batch_demo_latest.json"
AUDIT_JSON = EDGE_DIR / "v28_successor_public_rest_sidecar_batch_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_public_rest_sidecar_batch_latest.md"
NEW_YORK_TZ = ZoneInfo("America/New_York")
MAX_FETCH_ATTEMPTS = 3
RETRY_429_SLEEP_SECONDS = 3.0


def with_429_retry(call, *, max_attempts: int = MAX_FETCH_ATTEMPTS, sleep_seconds: float = RETRY_429_SLEEP_SECONDS) -> Any:
    attempts = max(1, int(max_attempts))
    for attempt in range(attempts):
        try:
            return call()
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt + 1 >= attempts:
                raise
            time.sleep(max(0.0, float(sleep_seconds)))
    raise RuntimeError("unreachable retry state")


def get_json_with_429_retry(
    base_url: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
    *,
    timeout_seconds: float = 10.0,
) -> Any:
    return with_429_retry(
        lambda: get_json(base_url, endpoint, params, timeout_seconds=timeout_seconds),
    )


def fetch_orderbook_with_429_retry(*, kalshi_base_url: str, ticker: str, timeout_seconds: float) -> dict[str, Any]:
    return with_429_retry(
        lambda: fetch_orderbook(kalshi_base_url=kalshi_base_url, ticker=ticker, timeout_seconds=timeout_seconds),
    )


def previous_btc15m_ticker_from_open_time(market: dict[str, Any]) -> str:
    open_ts = parse_ts(market.get("open_time"))
    if open_ts is None:
        close_ts = parse_ts(market_close_ts(market))
        if close_ts is None:
            return ""
        open_ts = close_ts - timedelta(minutes=15)
    local_open = open_ts.astimezone(NEW_YORK_TZ)
    return f"KXBTC15M-{local_open.strftime('%y%b%d%H%M').upper()}-{local_open.strftime('%M')}"


def official_previous_expiration_strike(
    market: dict[str, Any],
    *,
    kalshi_base_url: str,
    timeout_seconds: float,
) -> tuple[float | None, dict[str, Any]]:
    previous_ticker = previous_btc15m_ticker_from_open_time(market)
    if not previous_ticker:
        return None, {}
    try:
        payload = get_json_with_429_retry(kalshi_base_url, f"/markets/{previous_ticker}", timeout_seconds=timeout_seconds)
    except Exception:  # noqa: BLE001 - source-quality fallback must be best-effort only.
        return None, {"strike_source_market_ticker": previous_ticker}
    previous_market = payload.get("market") if isinstance(payload, dict) else None
    if not isinstance(previous_market, dict):
        return None, {"strike_source_market_ticker": previous_ticker}
    strike = as_float(previous_market.get("expiration_value"))
    if strike is None:
        return None, {"strike_source_market_ticker": previous_ticker}
    return strike, {
        "strike_source": "previous_market_expiration_value_official_public_rest",
        "strike_source_market_ticker": previous_ticker,
        "strike_source_market_close_ts_utc": market_close_ts(previous_market),
        "strike_source_market_status": previous_market.get("status"),
    }


def enrich_missing_tbd_strikes_from_previous_market(
    markets: list[dict[str, Any]],
    *,
    kalshi_base_url: str,
    now_utc: datetime,
    timeout_seconds: float,
    max_seconds_to_close: float = 20 * 60,
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for market in markets:
        if parse_btc_strike(market) is not None:
            enriched.append(market)
            continue
        ticker = market_ticker(market)
        close_ts = parse_ts(market_close_ts(market))
        if not ticker.startswith("KXBTC15M-") or close_ts is None:
            enriched.append(market)
            continue
        seconds_to_close = (close_ts - now_utc).total_seconds()
        if seconds_to_close <= 0 or seconds_to_close > max_seconds_to_close:
            enriched.append(market)
            continue
        strike, metadata = official_previous_expiration_strike(
            market,
            kalshi_base_url=kalshi_base_url,
            timeout_seconds=timeout_seconds,
        )
        if strike is None:
            enriched.append(market)
            continue
        row = dict(market)
        row["strike"] = strike
        row.update(metadata)
        enriched.append(row)
    return enriched


def active_market_rows(
    markets_payload: Any,
    *,
    now_utc: datetime,
    nearest_close_only: bool = True,
    max_markets: int = 80,
) -> list[dict[str, Any]]:
    markets = markets_payload.get("markets") if isinstance(markets_payload, dict) else markets_payload
    if not isinstance(markets, list):
        return []
    candidates: list[tuple[datetime, float, str, dict[str, Any]]] = []
    for row in markets:
        if not isinstance(row, dict):
            continue
        ticker = market_ticker(row)
        if not ticker.startswith("KXBTC15M-"):
            continue
        close_ts = parse_ts(market_close_ts(row))
        strike = parse_btc_strike(row)
        if close_ts is None or close_ts <= now_utc or strike is None:
            continue
        candidates.append((close_ts, float(strike), ticker, row))
    if not candidates:
        return []
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    if nearest_close_only:
        nearest_close = candidates[0][0]
        candidates = [item for item in candidates if item[0] == nearest_close]
    return [row for _close_ts, _strike, _ticker, row in candidates[: max(1, max_markets)]]


def fetch_active_markets(
    *,
    kalshi_base_url: str,
    series_ticker: str,
    now_utc: datetime,
    timeout_seconds: float,
    nearest_close_only: bool,
    max_markets: int,
    max_pages: int = 5,
) -> list[dict[str, Any]]:
    combined: list[dict[str, Any]] = []
    seen: set[str] = set()
    for status in ("active", "open", "initialized", None):
        cursor = None
        for _page in range(max_pages):
            try:
                payload = get_json_with_429_retry(
                    kalshi_base_url,
                    "/markets",
                    {
                        "series_ticker": series_ticker,
                        "status": status,
                        "limit": 200,
                        "cursor": cursor,
                    },
                    timeout_seconds=timeout_seconds,
                )
            except urllib.error.HTTPError:
                if status is not None:
                    break
                raise
            markets = payload.get("markets") if isinstance(payload, dict) else payload
            if isinstance(markets, list):
                for market in markets:
                    ticker = market_ticker(market) if isinstance(market, dict) else ""
                    if ticker and ticker not in seen:
                        seen.add(ticker)
                        combined.append(market)
            cursor = payload.get("cursor") if isinstance(payload, dict) else None
            if not cursor:
                break
        enriched = enrich_missing_tbd_strikes_from_previous_market(
            combined,
            kalshi_base_url=kalshi_base_url,
            now_utc=now_utc,
            timeout_seconds=timeout_seconds,
        )
        selected = active_market_rows(
            enriched,
            now_utc=now_utc,
            nearest_close_only=nearest_close_only,
            max_markets=max_markets,
        )
        if selected and nearest_close_only:
            return selected
    enriched = enrich_missing_tbd_strikes_from_previous_market(
        combined,
        kalshi_base_url=kalshi_base_url,
        now_utc=now_utc,
        timeout_seconds=timeout_seconds,
    )
    selected = active_market_rows(
        enriched,
        now_utc=now_utc,
        nearest_close_only=nearest_close_only,
        max_markets=max_markets,
    )
    if selected:
        return selected
    return []


def fixture_market_payloads() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], list[Any], datetime]:
    market, orderbook, candles, now_utc = fixture_payloads()
    second = json.loads(json.dumps(market))
    second["ticker"] = "KXBTC15M-26MAY111210-100500"
    second["strike"] = as_float(market.get("strike")) + 500.0 if as_float(market.get("strike")) is not None else 100500.0
    second_orderbook = {"yes": [[41, 90]], "no": [[57, 110]], "sequence_number": "fixture-batch-2"}
    return [market, second], {market_ticker(market): orderbook, market_ticker(second): second_orderbook}, candles, now_utc


def bundle_write_path(bundle: dict[str, Any], *, output_dir: Path, mode: str, index: int) -> Path:
    if mode == "fixture":
        return OUT_DIR / f"public_rest_sidecar_batch_demo_{index + 1}.json"
    return output_bundle_path(bundle, output_dir=output_dir)


def build_bundles_from_inputs(
    *,
    market_payloads: list[dict[str, Any]],
    orderbooks_by_ticker: dict[str, dict[str, Any]],
    candle_payload: list[Any],
    now_utc: datetime,
    simulated: bool,
    diagnostic_only: bool,
    mode: str,
    output_dir: Path = DEFAULT_BUNDLE_DIR,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    bundles: list[dict[str, Any]] = []
    market_reports: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    total_packet_rows = 0

    for index, market_payload in enumerate(market_payloads):
        ticker = market_ticker(market_payload)
        orderbook_payload = orderbooks_by_ticker.get(ticker)
        packet_rows: list[dict[str, Any]] = []
        packet_error = ""
        bundle: dict[str, Any] | None = None
        close_ts = parse_ts(market_close_ts(market_payload))
        if not simulated and (close_ts is None or close_ts <= now_utc):
            details = []
            contract_summary = {
                "bundle_status": "blocked",
                "bundle_ready": False,
                "blocker_counts": {"market_not_preclose_at_collection": 1},
            }
        elif orderbook_payload is None:
            details: list[dict[str, Any]] = []
            contract_summary = {"bundle_status": "blocked", "bundle_ready": False, "blocker_counts": {"missing_orderbook_payload": 1}}
        else:
            try:
                bundle = build_bundle_from_inputs(
                    market_payload=market_payload,
                    orderbook_payload=orderbook_payload,
                    candle_payload=candle_payload,
                    now_utc=now_utc,
                    simulated=simulated,
                    diagnostic_only=diagnostic_only,
                )
                details, contract_summary = validate_bundle(bundle)
                if contract_summary.get("bundle_ready"):
                    packet_rows = packet_rows_from_input_bundle(
                        input_bundle=bundle,
                        source_file="public_rest_sidecar_batch",
                        source_line_or_offset=str(index),
                    )
            except Exception as exc:  # noqa: BLE001
                packet_error = str(exc)
                details = []
                contract_summary = {"bundle_status": "blocked_exception", "bundle_ready": False, "blocker_counts": {"exception": 1}}
        status = str(contract_summary.get("bundle_status") or "unknown")
        if packet_error:
            status = "blocked_exception"
        status_counts[status] += 1
        for blocker, count in (contract_summary.get("blocker_counts") or {}).items():
            blocker_counts[str(blocker)] += int(count)
        total_packet_rows += len(packet_rows)
        output_path = bundle_write_path(
            bundle or {"registered_utc": iso_z(now_utc), "market": {"market_ticker": ticker}},
            output_dir=output_dir,
            mode=mode,
            index=index,
        )
        market_reports.append(
            {
                "market_ticker": ticker,
                "market_close_ts_utc": market_close_ts(market_payload),
                "strike": parse_btc_strike(market_payload),
                "bundle_status": status,
                "bundle_ready": bool(contract_summary.get("bundle_ready")) and not packet_error,
                "packet_rows": len(packet_rows),
                "packet_error": packet_error,
                "output_bundle_json": rel_path(output_path),
                "blocker_counts": contract_summary.get("blocker_counts") or {},
                "contract_detail_count": len(details),
            }
        )
        if bundle is not None:
            bundles.append({"bundle": bundle, "output_path": output_path})

    summary = {
        "generated_utc": iso_z(datetime.now(timezone.utc).replace(microsecond=0)),
        "builder_script": Path(__file__).name,
        "mode": mode,
        "batch_status": "batch_bundles_ready_for_freeze" if total_packet_rows and not simulated else "contract_demo_ready_not_evidence" if simulated else "blocked_no_ready_batch_bundles",
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "public REST sidecar batch bundles are collector inputs only; promotion requires pre-close freeze, post-resolution labels, source contract, coverage, evidence scoring, and verifier approval",
        },
        "markets_selected": len(market_payloads),
        "bundle_ready_files": sum(1 for row in market_reports if row["bundle_ready"]),
        "packet_rows": total_packet_rows,
        "packet_markets": len({row["market_ticker"] for row in market_reports if row["packet_rows"]}),
        "simulated": simulated,
        "diagnostic_only": diagnostic_only,
        "status_counts": dict(sorted(status_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "outputs": {
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
            "demo_batch_json": rel_path(DEMO_BATCH_JSON),
        },
    }
    return {"summary": summary, "markets": market_reports}, bundles


def build(
    *,
    mode: str = "fixture",
    kalshi_base_url: str = DEFAULT_KALSHI_BASE_URL,
    coinbase_base_url: str = DEFAULT_COINBASE_BASE_URL,
    series_ticker: str = DEFAULT_SERIES_TICKER,
    now_utc: datetime | None = None,
    btc_minutes: int = 300,
    timeout_seconds: float = 10.0,
    output_dir: Path = DEFAULT_BUNDLE_DIR,
    nearest_close_only: bool = True,
    max_markets: int = 80,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    now_utc = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if mode == "fixture":
        market_payloads, orderbooks_by_ticker, candle_payload, fixture_now = fixture_market_payloads()
        now_utc = fixture_now
        simulated = True
        diagnostic_only = True
    elif mode == "public_rest":
        market_payloads = fetch_active_markets(
            kalshi_base_url=kalshi_base_url,
            series_ticker=series_ticker,
            now_utc=now_utc,
            timeout_seconds=timeout_seconds,
            nearest_close_only=nearest_close_only,
            max_markets=max_markets,
        )
        if not market_payloads:
            raise RuntimeError("no active BTC15M markets found in public Kalshi response")
        candle_payload = fetch_coinbase_candles(
            coinbase_base_url=coinbase_base_url,
            now_utc=now_utc,
            minutes=btc_minutes,
            timeout_seconds=timeout_seconds,
        )
        orderbooks_by_ticker = {
            market_ticker(market): fetch_orderbook_with_429_retry(
                kalshi_base_url=kalshi_base_url,
                ticker=market_ticker(market),
                timeout_seconds=timeout_seconds,
            )
            for market in market_payloads
        }
        simulated = False
        diagnostic_only = False
    else:
        raise ValueError("mode must be fixture or public_rest")

    return build_bundles_from_inputs(
        market_payloads=market_payloads,
        orderbooks_by_ticker=orderbooks_by_ticker,
        candle_payload=candle_payload,
        now_utc=now_utc,
        simulated=simulated,
        diagnostic_only=diagnostic_only,
        mode=mode,
        output_dir=output_dir,
    )


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Public REST Sidecar Batch",
        "",
        "Research-only batch sidecar bundle builder. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Mode: `{summary['mode']}`",
        f"- Batch status: `{summary['batch_status']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Markets selected: `{summary['markets_selected']}`",
        f"- Ready bundle files: `{summary['bundle_ready_files']}`",
        f"- Packet rows: `{summary['packet_rows']}`",
        f"- Packet markets: `{summary['packet_markets']}`",
        "",
        "## Markets",
        "",
        "| market | close | strike | status | packet rows | output |",
        "|---|---|---:|---|---:|---|",
    ]
    for row in report["markets"]:
        lines.append(
            f"| `{row['market_ticker']}` | `{row['market_close_ts_utc']}` | {row['strike']} | "
            f"`{row['bundle_status']}` | {row['packet_rows']} | `{row['output_bundle_json']}` |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Fixture mode is deterministic and diagnostic only.",
            "- Public REST mode is explicit and writes real non-simulated bundles for later pre-close freezing.",
            "- A ready batch still must be frozen before close, labeled after resolution, scored, source-checked, and verifier-approved.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any], bundles: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    if report["summary"].get("mode") == "fixture":
        DEMO_BATCH_JSON.write_text(json.dumps({"bundles": [item["bundle"] for item in bundles]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        for item in bundles:
            output_path = Path(item["output_path"])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(item["bundle"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_BUNDLE_DIR)
    parser.add_argument("--all-open-closes", action="store_true", help="Collect all open BTC15M markets returned by the API, not only the nearest close.")
    parser.add_argument("--max-markets", type=int, default=80)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now_utc = parse_ts(args.now_utc) if args.now_utc else None
    report, bundles = build(
        mode=args.mode.replace("-", "_"),
        kalshi_base_url=args.kalshi_base_url,
        coinbase_base_url=args.coinbase_base_url,
        series_ticker=args.series_ticker,
        now_utc=now_utc,
        btc_minutes=args.btc_minutes,
        timeout_seconds=args.timeout_seconds,
        output_dir=args.output_dir,
        nearest_close_only=not args.all_open_closes,
        max_markets=args.max_markets,
    )
    if args.write and not args.dry_run:
        write_outputs(report, bundles)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "mode": summary["mode"],
                "batch_status": summary["batch_status"],
                "markets_selected": summary["markets_selected"],
                "bundle_ready_files": summary["bundle_ready_files"],
                "packet_rows": summary["packet_rows"],
                "packet_markets": summary["packet_markets"],
                "promotion_allowed": summary["promotion_allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
