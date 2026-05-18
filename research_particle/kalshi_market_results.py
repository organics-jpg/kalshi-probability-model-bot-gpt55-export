from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


PROD_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"


class KalshiMarketResultError(ValueError):
    pass


def market_result_row_from_market(market: Mapping[str, Any]) -> dict[str, Any] | None:
    ticker = str(market.get("ticker") or market.get("market_ticker") or "")
    result = str(market.get("result") or "").lower()
    if not ticker:
        raise KalshiMarketResultError("market payload missing ticker")
    if result not in {"yes", "no"}:
        return None
    close_time = str(market.get("close_time") or "")
    if not close_time:
        raise KalshiMarketResultError(f"{ticker} missing close_time")
    return {
        "market": ticker,
        "result": result,
        "close_time": close_time,
        "status": market.get("status"),
        "source": market.get("_result_source") or "kalshi_public_markets",
    }


def fetch_market_payload(ticker: str, *, base_url: str = PROD_BASE_URL) -> Mapping[str, Any]:
    errors: list[str] = []
    first_market: dict[str, Any] | None = None
    for source, path in _market_payload_paths(ticker):
        try:
            payload = _get_json(f"{base_url.rstrip('/')}{path}")
            market = _market_from_payload(payload, ticker)
            market["_result_source"] = source
            if first_market is None:
                first_market = market
            if str(market.get("result") or "").lower() in {"yes", "no"}:
                return market
        except HTTPError as exc:
            errors.append(f"{source}: HTTP {exc.code}")
        except Exception as exc:
            errors.append(f"{source}: {exc}")
    if first_market is not None:
        return first_market
    raise KalshiMarketResultError(f"market not found: {ticker}; " + "; ".join(errors))


def _market_payload_paths(ticker: str) -> list[tuple[str, str]]:
    query = urlencode({"tickers": ticker, "limit": 10})
    quoted_ticker = quote(ticker)
    return [
        ("kalshi_public_markets", f"/markets?{query}"),
        ("kalshi_public_market", f"/markets/{quoted_ticker}"),
        ("kalshi_historical_market", f"/historical/markets/{quoted_ticker}"),
    ]


def _get_json(url: str) -> dict[str, Any]:
    request = Request(
        url,
        headers={"User-Agent": "particle-research-market-results/1.1"},
        method="GET",
    )
    with urlopen(request, timeout=20) as response:  # noqa: S310 - fixed Kalshi public endpoint by default.
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise KalshiMarketResultError("JSON object response expected")
    return payload


def _market_from_payload(payload: Mapping[str, Any], ticker: str) -> dict[str, Any]:
    if isinstance(payload.get("market"), Mapping):
        market = dict(payload["market"])
        if str(market.get("ticker") or "").upper() == ticker.upper():
            return market
        raise KalshiMarketResultError(f"market payload ticker mismatch: {market.get('ticker')}")
    for market in payload.get("markets", []):
        if isinstance(market, Mapping) and str(market.get("ticker") or "").upper() == ticker.upper():
            return dict(market)
    raise KalshiMarketResultError(f"market not found in response: {ticker}")


def fetch_market_results(
    tickers: list[str],
    output_path: Path,
    issue_path: Path,
    *,
    base_url: str = PROD_BASE_URL,
) -> tuple[int, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for ticker in tickers:
        try:
            market = fetch_market_payload(ticker, base_url=base_url)
            row = market_result_row_from_market(market)
            if row is None:
                issues.append(
                    {
                        "market": ticker,
                        "reason": "market not resolved",
                        "result": market.get("result"),
                        "source": market.get("_result_source"),
                        "status": market.get("status"),
                    }
                )
            else:
                rows.append(row)
        except Exception as exc:
            issues.append({"market": ticker, "reason": str(exc)})
    output_path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    issue_path.write_text(json.dumps(issues, indent=2, sort_keys=True), encoding="utf-8")
    return len(rows), len(issues)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch resolved public Kalshi market results for particle replay labels."
    )
    parser.add_argument("--ticker", action="append", dest="tickers", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--issues", required=True, type=Path)
    parser.add_argument("--base-url", default=PROD_BASE_URL)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written, issues = fetch_market_results(
        args.tickers,
        args.output,
        args.issues,
        base_url=args.base_url,
    )
    print(f"written_results={written}")
    print(f"issue_count={issues}")
    print(f"output={args.output}")
    print(f"issues={args.issues}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
