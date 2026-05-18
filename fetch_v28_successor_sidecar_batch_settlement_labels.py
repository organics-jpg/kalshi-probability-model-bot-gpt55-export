"""Fetch settlement labels for sidecar batch frozen rows.

Research-only. This reads the non-canonical sidecar batch frozen ledger,
fetches public Kalshi market results after close, and writes a separate label
CSV for the sidecar batch label-join handoff. It does not touch live bot state,
orders, thresholds, secrets, or processes.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from join_v28_successor_forward_labels import parse_ts, read_csv_rows, sha256_file
from run_v28_successor_sidecar_bundle_batch_handoff import BATCH_FROZEN_CSV


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

DEFAULT_KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

BATCH_SETTLEMENT_LABELS_CSV = OUT_DIR / "sidecar_bundle_batch_settlement_labels_latest.csv"
BATCH_SETTLEMENT_LABELS_JSON = OUT_DIR / "sidecar_bundle_batch_settlement_labels_latest.json"
AUDIT_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_batch_settlement_labels_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_sidecar_bundle_batch_settlement_labels_latest.md"

LABEL_FIELDS = [
    "market_ticker",
    "y_yes_win",
    "binary_result",
    "settlement_ts_utc",
    "label_available_ts_utc",
    "settlement_price",
    "strike",
    "label_source",
    "market_status",
]


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


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


def http_json(url: str, *, timeout_seconds: float) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "v28-successor-research-label-fetcher/1.0"})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(base_url: str, endpoint: str, params: dict[str, Any] | None = None, *, timeout_seconds: float) -> Any:
    query = urllib.parse.urlencode({key: value for key, value in (params or {}).items() if value is not None})
    url = base_url.rstrip("/") + endpoint
    if query:
        url = f"{url}?{query}"
    return http_json(url, timeout_seconds=timeout_seconds)


def fetch_market(base_url: str, ticker: str, *, timeout_seconds: float) -> dict[str, Any] | None:
    try:
        payload = get_json(base_url, f"/markets/{urllib.parse.quote(ticker, safe='')}", timeout_seconds=timeout_seconds)
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
    else:
        market = payload.get("market") if isinstance(payload, dict) else None
        if isinstance(market, dict) and str(market.get("ticker") or "").strip() == ticker:
            return market

    payload = get_json(base_url, "/markets", {"tickers": ticker, "limit": 10}, timeout_seconds=timeout_seconds)
    markets = payload.get("markets") if isinstance(payload, dict) else None
    if not isinstance(markets, list):
        markets = []
    for market in markets:
        if isinstance(market, dict) and str(market.get("ticker") or "").strip() == ticker:
            return market
    try:
        payload = get_json(base_url, f"/historical/markets/{urllib.parse.quote(ticker, safe='')}", timeout_seconds=timeout_seconds)
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        return None
    market = payload.get("market") if isinstance(payload, dict) else None
    if isinstance(market, dict) and str(market.get("ticker") or "").strip() == ticker:
        return market
    return None


def fetch_market_with_retries(
    base_url: str,
    ticker: str,
    *,
    timeout_seconds: float,
    max_attempts: int,
    retry_429_sleep_seconds: float,
) -> dict[str, Any] | None:
    attempts = max(1, max_attempts)
    for attempt in range(attempts):
        try:
            return fetch_market(base_url, ticker, timeout_seconds=timeout_seconds)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt >= attempts - 1:
                raise
            time.sleep(max(0.0, retry_429_sleep_seconds))
    return None


def frozen_market_rows(frozen_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_market: dict[str, dict[str, Any]] = {}
    for row in frozen_rows:
        ticker = str(row.get("market_ticker") or "").strip()
        if not ticker:
            continue
        existing = by_market.get(ticker)
        if existing is None:
            by_market[ticker] = row
            continue
        old_decision = parse_ts(existing.get("decision_ts_utc"))
        new_decision = parse_ts(row.get("decision_ts_utc"))
        if old_decision is None or (new_decision is not None and new_decision < old_decision):
            by_market[ticker] = row
    return by_market


def label_from_market(
    *,
    market: dict[str, Any],
    frozen: dict[str, Any],
    now_utc: datetime,
) -> tuple[dict[str, Any] | None, str]:
    ticker = str(frozen.get("market_ticker") or "")
    close_ts = parse_ts(frozen.get("market_close_ts_utc") or market.get("close_time"))
    if close_ts is None:
        return None, "missing_close_ts"
    if now_utc <= close_ts:
        return None, "market_not_closed"
    result = str(market.get("result") or "").strip().lower()
    status = str(market.get("status") or "").strip().lower()
    if result not in {"yes", "no"}:
        if status == "closed":
            return None, "market_closed_awaiting_determination"
        if status in {"determined", "finalized", "settled"}:
            return None, f"missing_result_after_determination_status:{status}"
        return None, f"missing_result_status:{status or 'unknown'}"
    settlement_ts = parse_ts(market.get("settlement_ts") or market.get("updated_time") or market.get("close_time")) or now_utc
    label_available_ts = max(now_utc, settlement_ts)
    settlement_price = as_float(market.get("expiration_value") or market.get("settlement_price") or market.get("settlement_value"))
    return (
        {
            "market_ticker": ticker,
            "y_yes_win": "1" if result == "yes" else "0",
            "binary_result": result,
            "settlement_ts_utc": iso_z(settlement_ts),
            "label_available_ts_utc": iso_z(label_available_ts),
            "settlement_price": "" if settlement_price is None else f"{settlement_price:.8g}",
            "strike": frozen.get("strike", ""),
            "label_source": "kalshi_public_market_result",
            "market_status": status,
        },
        "",
    )


def label_is_valid_for_frozen_market(label: dict[str, Any], frozen: dict[str, Any]) -> bool:
    if str(label.get("market_ticker") or "").strip() != str(frozen.get("market_ticker") or "").strip():
        return False
    if str(label.get("y_yes_win") or "").strip() not in {"0", "1", "0.0", "1.0"}:
        return False
    close_ts = parse_ts(frozen.get("market_close_ts_utc"))
    settlement_ts = parse_ts(label.get("settlement_ts_utc"))
    available_ts = parse_ts(label.get("label_available_ts_utc"))
    if close_ts is None or settlement_ts is None or available_ts is None:
        return False
    if settlement_ts < close_ts or available_ts < close_ts:
        return False
    if available_ts < settlement_ts:
        return False
    return True


def merge_preserved_labels(
    *,
    fetched_labels: list[dict[str, Any]],
    existing_labels: list[dict[str, Any]],
    frozen_by_market: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    merged_by_market: dict[str, dict[str, Any]] = {}
    invalid_existing = 0
    duplicate_existing = 0
    deduped_or_invalid_fetched = 0

    for label in existing_labels:
        ticker = str(label.get("market_ticker") or "").strip()
        frozen = frozen_by_market.get(ticker)
        if frozen is None or not label_is_valid_for_frozen_market(label, frozen):
            invalid_existing += 1
            continue
        existing = merged_by_market.get(ticker)
        if existing is not None:
            duplicate_existing += 1
            old_ts = parse_ts(existing.get("label_available_ts_utc"))
            new_ts = parse_ts(label.get("label_available_ts_utc"))
            if old_ts is not None and (new_ts is None or old_ts <= new_ts):
                continue
        merged_by_market[ticker] = {field: label.get(field, "") for field in LABEL_FIELDS}

    for label in fetched_labels:
        ticker = str(label.get("market_ticker") or "").strip()
        frozen = frozen_by_market.get(ticker)
        if frozen is None or not label_is_valid_for_frozen_market(label, frozen):
            deduped_or_invalid_fetched += 1
            continue
        existing = merged_by_market.get(ticker)
        if existing is not None:
            deduped_or_invalid_fetched += 1
            old_ts = parse_ts(existing.get("label_available_ts_utc"))
            new_ts = parse_ts(label.get("label_available_ts_utc"))
            if old_ts is not None and (new_ts is None or old_ts <= new_ts):
                continue
        merged_by_market[ticker] = {field: label.get(field, "") for field in LABEL_FIELDS}

    return [merged_by_market[ticker] for ticker in sorted(merged_by_market)], {
        "existing_label_rows": len(existing_labels),
        "valid_existing_label_rows": len(existing_labels) - invalid_existing,
        "invalid_existing_label_rows": invalid_existing,
        "duplicate_existing_label_rows": duplicate_existing,
        "fetched_label_rows": len(fetched_labels),
        "deduped_or_invalid_fetched_label_rows": deduped_or_invalid_fetched,
        "merged_label_rows": len(merged_by_market),
    }


def build(
    *,
    frozen_csv: Path = BATCH_FROZEN_CSV,
    existing_labels_csv: Path | None = None,
    kalshi_base_url: str = DEFAULT_KALSHI_BASE_URL,
    now_utc: datetime | None = None,
    timeout_seconds: float = 10.0,
    request_sleep_seconds: float = 0.25,
    max_fetch_attempts: int = 2,
    retry_429_sleep_seconds: float = 3.0,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    now_utc = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    frozen_rows = read_csv_rows(frozen_csv)
    markets = frozen_market_rows(frozen_rows)
    preserve_existing = existing_labels_csv is not None or frozen_csv == BATCH_FROZEN_CSV
    existing_labels_path = existing_labels_csv or (BATCH_SETTLEMENT_LABELS_CSV if preserve_existing else None)
    existing_labels = read_csv_rows(existing_labels_path) if existing_labels_path is not None else []
    fetched_labels: list[dict[str, Any]] = []
    market_reports: list[dict[str, Any]] = []
    blockers: Counter[str] = Counter()
    fetch_attempts = 0

    for ticker, frozen in sorted(markets.items()):
        close_ts = parse_ts(frozen.get("market_close_ts_utc"))
        if close_ts is not None and now_utc <= close_ts:
            blockers["market_not_closed"] += 1
            market_reports.append(
                {
                    "market_ticker": ticker,
                    "status": "blocked",
                    "blocker": "market_not_closed",
                    "market_close_ts_utc": iso_z(close_ts),
                }
            )
            continue
        try:
            if fetch_attempts and request_sleep_seconds > 0:
                time.sleep(request_sleep_seconds)
            fetch_attempts += 1
            market = fetch_market_with_retries(
                kalshi_base_url,
                ticker,
                timeout_seconds=timeout_seconds,
                max_attempts=max_fetch_attempts,
                retry_429_sleep_seconds=retry_429_sleep_seconds,
            )
        except Exception as exc:  # noqa: BLE001
            blockers["market_fetch_error"] += 1
            market_reports.append({"market_ticker": ticker, "status": "blocked", "blocker": "market_fetch_error", "error": str(exc)})
            continue
        if market is None:
            blockers["market_not_found"] += 1
            market_reports.append({"market_ticker": ticker, "status": "blocked", "blocker": "market_not_found"})
            continue
        label, blocker = label_from_market(market=market, frozen=frozen, now_utc=now_utc)
        if blocker:
            blockers[blocker] += 1
            market_reports.append(
                {
                    "market_ticker": ticker,
                    "status": "blocked",
                    "blocker": blocker,
                    "market_status": market.get("status"),
                    "result": market.get("result"),
                    "close_time": market.get("close_time"),
                    "expected_expiration_time": market.get("expected_expiration_time"),
                    "expiration_time": market.get("expiration_time"),
                    "updated_time": market.get("updated_time"),
                    "settlement_ts": market.get("settlement_ts"),
                    "settlement_timer_seconds": market.get("settlement_timer_seconds"),
                }
            )
            continue
        assert label is not None
        fetched_labels.append(label)
        market_reports.append(
            {
                "market_ticker": ticker,
                "status": "labeled",
                "market_status": market.get("status"),
                "result": market.get("result"),
                "settlement_ts_utc": label["settlement_ts_utc"],
            }
        )

    labels, preservation_counts = merge_preserved_labels(
        fetched_labels=fetched_labels,
        existing_labels=existing_labels,
        frozen_by_market=markets,
    )

    if not frozen_rows:
        status = "blocked_no_frozen_rows"
        blockers["no_frozen_rows"] += 1
    elif not markets:
        status = "blocked_no_frozen_markets"
        blockers["no_frozen_markets"] += 1
    elif labels:
        status = "settlement_labels_available"
    elif blockers.get("market_not_closed"):
        status = "blocked_waiting_for_market_close"
    else:
        status = "blocked_no_resolved_labels"

    summary = {
        "generated_utc": iso_z(now_utc.replace(microsecond=0)),
        "builder_script": Path(__file__).name,
        "label_fetch_status": status,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "settlement labels are necessary but not sufficient; joined forward evidence, source contract, coverage, and promotion verifier must still pass",
        },
        "frozen_rows": len(frozen_rows),
        "frozen_markets": len(markets),
        "label_rows": len(labels),
        "label_markets": len({row["market_ticker"] for row in labels}),
        "fetched_label_rows": len(fetched_labels),
        "preserved_existing_label_rows": preservation_counts["valid_existing_label_rows"],
        "preservation": {
            "enabled": preserve_existing,
            "existing_labels_csv": rel_path(existing_labels_path) if existing_labels_path is not None else None,
            **preservation_counts,
        },
        "blocker_counts": dict(sorted(blockers.items())),
        "inputs": {
            "frozen_csv": rel_path(frozen_csv),
            "frozen_hash": sha256_file(frozen_csv),
            "kalshi_base_url": kalshi_base_url,
            "request_sleep_seconds": request_sleep_seconds,
            "max_fetch_attempts": max_fetch_attempts,
            "retry_429_sleep_seconds": retry_429_sleep_seconds,
        },
        "outputs": {
            "labels_csv": rel_path(BATCH_SETTLEMENT_LABELS_CSV),
            "labels_json": rel_path(BATCH_SETTLEMENT_LABELS_JSON),
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
        },
    }
    return {"summary": summary, "markets": market_reports}, labels


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LABEL_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Sidecar Batch Settlement Labels",
        "",
        "Research-only label fetch for sidecar batch frozen rows. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Label fetch status: `{summary['label_fetch_status']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Frozen rows: `{summary['frozen_rows']}`",
        f"- Frozen markets: `{summary['frozen_markets']}`",
        f"- Label rows: `{summary['label_rows']}`",
        f"- Label markets: `{summary['label_markets']}`",
        f"- Fetched label rows this run: `{summary['fetched_label_rows']}`",
        f"- Preserved existing label rows: `{summary['preserved_existing_label_rows']}`",
        "",
        "## Blockers",
        "",
    ]
    blockers = summary.get("blocker_counts") or {}
    if blockers:
        for blocker, count in blockers.items():
            lines.append(f"- `{blocker}`: `{count}`")
    else:
        lines.append("- None recorded by this fetcher.")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The fetcher refuses to label markets before their frozen close time.",
            "- Labels are written to a sidecar batch file, not the canonical promotion ledger.",
            "- A label row still needs label-join validation, source contract, evidence scoring, and promotion verification.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, BATCH_SETTLEMENT_LABELS_CSV)
    BATCH_SETTLEMENT_LABELS_JSON.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-csv", type=Path, default=BATCH_FROZEN_CSV)
    parser.add_argument("--existing-labels-csv", type=Path, default=None)
    parser.add_argument("--kalshi-base-url", default=DEFAULT_KALSHI_BASE_URL)
    parser.add_argument("--now-utc", default="")
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--request-sleep-seconds", type=float, default=0.25)
    parser.add_argument("--max-fetch-attempts", type=int, default=2)
    parser.add_argument("--retry-429-sleep-seconds", type=float, default=3.0)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    report, labels = build(
        frozen_csv=args.frozen_csv,
        existing_labels_csv=args.existing_labels_csv,
        kalshi_base_url=args.kalshi_base_url,
        now_utc=parse_ts(args.now_utc) if args.now_utc else None,
        timeout_seconds=args.timeout_seconds,
        request_sleep_seconds=args.request_sleep_seconds,
        max_fetch_attempts=args.max_fetch_attempts,
        retry_429_sleep_seconds=args.retry_429_sleep_seconds,
    )
    if args.write and not args.dry_run:
        write_outputs(report, labels)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "label_fetch_status": summary["label_fetch_status"],
                "frozen_rows": summary["frozen_rows"],
                "frozen_markets": summary["frozen_markets"],
                "label_rows": summary["label_rows"],
                "label_markets": summary["label_markets"],
                "fetched_label_rows": summary["fetched_label_rows"],
                "preserved_existing_label_rows": summary["preserved_existing_label_rows"],
                "promotion_allowed": summary["promotion_allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
