"""Refresh Kalshi metadata for markets currently present in the live bot log.

Research-only: this reads `logs/live_mushroom_v28_size2/bot.log`, fetches
public market metadata for watched tickers, and updates the local research
metadata cache. It does not import or control the trading bot.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


ROOT = Path(__file__).resolve().parent
BOT_LOG = ROOT / "logs" / "live_mushroom_v28_size2" / "bot.log"
OUT_DIR = ROOT / "logs" / "edge_research"
METADATA_CACHE = OUT_DIR / "kalshi_market_metadata_cache.json"
REPORT_LATEST = OUT_DIR / "watched_market_metadata_refresh_latest.md"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_market_metadata(ticker: str, retries: int = 3) -> Dict[str, Any]:
    url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}"
    last_error = ""
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
            market = payload.get("market") or {}
            return {
                "market": market.get("ticker") or ticker,
                "close_time": market.get("close_time"),
                "floor_strike": market.get("floor_strike"),
                "cap_strike": market.get("cap_strike"),
                "expiration_value": market.get("expiration_value"),
                "yes_sub_title": market.get("yes_sub_title"),
                "no_sub_title": market.get("no_sub_title"),
                "status": market.get("status"),
                "raw_market_type": market.get("market_type"),
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            time.sleep(0.5 * (attempt + 1))
    return {"market": ticker, "fetch_error": last_error, "fetched_at_utc": datetime.now(timezone.utc).isoformat()}


def watched_markets(path: Path) -> Iterable[str]:
    watch_re = re.compile(r"Watching market (?P<market>\S+) ")
    seen: set[str] = set()
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = watch_re.search(line)
            if not match:
                continue
            ticker = match.group("market")
            if ticker in seen:
                continue
            seen.add(ticker)
            yield ticker


def needs_refresh(meta: Optional[Dict[str, Any]]) -> bool:
    if not meta:
        return True
    return meta.get("floor_strike") is None or meta.get("close_time") is None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--latest",
        type=int,
        default=3,
        help="Refresh only the latest N watched markets by default.",
    )
    args = parser.parse_args()

    cache = load_json(METADATA_CACHE)
    all_markets = list(watched_markets(BOT_LOG))
    markets = all_markets[-max(1, int(args.latest)) :]
    fetched = 0
    missing_after = 0
    for ticker in markets:
        if needs_refresh(cache.get(ticker)):
            cache[ticker] = fetch_market_metadata(ticker)
            fetched += 1
            write_json(METADATA_CACHE, cache)
        if needs_refresh(cache.get(ticker)):
            missing_after += 1
    write_json(METADATA_CACHE, cache)

    lines = [
        "# Watched Market Metadata Refresh",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%SZ')}`",
        "",
        f"- Watched markets in log: {len(all_markets)}",
        f"- Watched markets scanned this run: {len(markets)}",
        f"- Metadata records fetched: {fetched}",
        f"- Still missing strike/close metadata: {missing_after}",
        f"- Cache: `{METADATA_CACHE.relative_to(ROOT)}`",
    ]
    latest = markets[-1] if markets else ""
    if latest:
        meta = cache.get(latest) or {}
        lines.extend(
            [
                "",
                "## Latest Watched Market",
                "",
                f"- Market: `{latest}`",
                f"- Close: `{meta.get('close_time')}`",
                f"- Strike: `{meta.get('floor_strike')}`",
                f"- Status: `{meta.get('status')}`",
            ]
        )
    REPORT_LATEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Watched market metadata refresh complete")
    print(f"watched={len(markets)} fetched={fetched} missing_after={missing_after}")
    print(f"report={REPORT_LATEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
