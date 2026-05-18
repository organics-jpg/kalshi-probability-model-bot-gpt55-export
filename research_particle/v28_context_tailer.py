from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .v28_context_source import (
    V28ContextSourceError,
    context_from_v28_event,
    is_supported_v28_context_event,
)


DEFAULT_KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"


@dataclass(frozen=True)
class V28ContextTailerStatus:
    schema_version: str
    source_input: str
    output: str
    issues: str
    status: str
    market_ticker: str | None
    contexts_written: int
    seeded_contexts: int
    issue_count: int
    skipped_other_market: int
    skipped_unsupported_schema: int
    last_context_ts_utc: str
    generated_at_utc: str


def run_v28_context_tailer(
    *,
    input_path: Path,
    output_path: Path,
    issue_path: Path,
    status_path: Path,
    market_ticker: str | None = None,
    settlement_ts_utc: datetime | None = None,
    follow: bool = False,
    start_at_end: bool = False,
    poll_seconds: float = 0.5,
    run_seconds: float | None = None,
    max_rows: int | None = None,
    append_ok: bool = False,
    seed_last_contexts: bool = False,
    enrich_missing_market_metadata: bool = False,
    kalshi_base_url: str | None = None,
    market_lookup_timeout_seconds: float = 5.0,
) -> V28ContextTailerStatus:
    if output_path.exists() and not append_ok:
        raise FileExistsError(f"{output_path} already exists; use --append-ok or a fresh output path")
    if not input_path.exists() and not follow:
        raise FileNotFoundError(f"{input_path} does not exist; use --follow to wait for it")
    if seed_last_contexts and not start_at_end:
        raise ValueError("seed_last_contexts requires start_at_end to avoid duplicate historical context rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    contexts_written = 0
    seeded_contexts = 0
    issue_count = 0
    skipped_other_market = 0
    skipped_unsupported_schema = 0
    last_context_ts = ""
    started = time.monotonic()
    offset = 0
    line_number = 0
    market_metadata_cache: dict[str, dict[str, Any]] = {}
    base_url = (kalshi_base_url or _get_env_value("KALSHI_BASE_URL") or DEFAULT_KALSHI_BASE_URL).rstrip("/")
    if start_at_end and input_path.exists():
        offset = input_path.stat().st_size
    mode = "a" if append_ok else "w"
    with output_path.open(mode, encoding="utf-8") as out, issue_path.open(
        mode, encoding="utf-8"
    ) as bad:
        if seed_last_contexts and input_path.exists():
            for context in _seed_latest_contexts(
                input_path,
                market_ticker=market_ticker,
                settlement_ts_utc=settlement_ts_utc,
                enrich_missing_market_metadata=enrich_missing_market_metadata,
                kalshi_base_url=base_url,
                market_lookup_timeout_seconds=market_lookup_timeout_seconds,
                market_metadata_cache=market_metadata_cache,
            ):
                out.write(json.dumps(context, sort_keys=True) + "\n")
                contexts_written += 1
                seeded_contexts += 1
                last_context_ts = str(context["context_ts_utc"])
                if max_rows is not None and contexts_written >= max_rows:
                    return _write_status(
                        status_path,
                        input_path=input_path,
                        output_path=output_path,
                        issue_path=issue_path,
                        status="max_rows_reached",
                        market_ticker=market_ticker,
                        contexts_written=contexts_written,
                        seeded_contexts=seeded_contexts,
                        issue_count=issue_count,
                        skipped_other_market=skipped_other_market,
                        skipped_unsupported_schema=skipped_unsupported_schema,
                        last_context_ts=last_context_ts,
                    )
        while True:
            if input_path.exists():
                if input_path.stat().st_size < offset:
                    offset = 0
                    line_number = 0
                with input_path.open("r", encoding="utf-8", errors="replace") as src:
                    src.seek(offset)
                    while True:
                        line = src.readline()
                        if not line:
                            break
                        line_number += 1
                        offset = src.tell()
                        line = line.strip().lstrip("\ufeff")
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                            if not isinstance(payload, dict):
                                raise V28ContextSourceError("line is not a JSON object")
                            event_market = str(payload.get("market") or payload.get("market_ticker") or "")
                            if market_ticker and event_market != market_ticker:
                                skipped_other_market += 1
                                continue
                            if not is_supported_v28_context_event(payload):
                                skipped_unsupported_schema += 1
                                continue
                            market_metadata = _market_metadata_for_event(
                                payload,
                                enrich_missing_market_metadata=enrich_missing_market_metadata,
                                kalshi_base_url=base_url,
                                market_lookup_timeout_seconds=market_lookup_timeout_seconds,
                                market_metadata_cache=market_metadata_cache,
                            )
                            context = context_from_v28_event(
                                payload,
                                market_ticker=market_ticker,
                                settlement_ts_utc=settlement_ts_utc,
                                market_metadata=market_metadata,
                            )
                            context["source"] = "v28_context_tailer"
                            out.write(json.dumps(context, sort_keys=True) + "\n")
                            contexts_written += 1
                            last_context_ts = str(context["context_ts_utc"])
                            if max_rows is not None and contexts_written >= max_rows:
                                return _write_status(
                                    status_path,
                                    input_path=input_path,
                                    output_path=output_path,
                                    issue_path=issue_path,
                                    status="max_rows_reached",
                                    market_ticker=market_ticker,
                                    contexts_written=contexts_written,
                                    seeded_contexts=seeded_contexts,
                                    issue_count=issue_count,
                                    skipped_other_market=skipped_other_market,
                                    skipped_unsupported_schema=skipped_unsupported_schema,
                                    last_context_ts=last_context_ts,
                                )
                        except Exception as exc:
                            issue_count += 1
                            bad.write(
                                json.dumps(
                                    {
                                        "line_number": line_number,
                                        "reason": str(exc),
                                    },
                                    sort_keys=True,
                                )
                                + "\n"
                            )
            if not follow:
                break
            if run_seconds is not None and time.monotonic() - started >= run_seconds:
                break
            time.sleep(max(0.05, float(poll_seconds)))
    return _write_status(
        status_path,
        input_path=input_path,
        output_path=output_path,
        issue_path=issue_path,
        status="stopped",
        market_ticker=market_ticker,
        contexts_written=contexts_written,
        seeded_contexts=seeded_contexts,
        issue_count=issue_count,
        skipped_other_market=skipped_other_market,
        skipped_unsupported_schema=skipped_unsupported_schema,
        last_context_ts=last_context_ts,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only tailer that records timestamped passive context rows from v28 telemetry."
    )
    parser.add_argument("--input", required=True, type=Path, help="v28 execution_events.ndjson path")
    parser.add_argument("--output", required=True, type=Path, help="passive_contexts.ndjson output")
    parser.add_argument("--issues", required=True, type=Path)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--market-ticker")
    parser.add_argument("--settlement-ts-utc")
    parser.add_argument("--follow", action="store_true")
    parser.add_argument("--start-at-end", action="store_true")
    parser.add_argument("--poll-seconds", default=0.5, type=float)
    parser.add_argument("--run-seconds", default=None, type=float)
    parser.add_argument("--max-rows", default=None, type=int)
    parser.add_argument("--append-ok", action="store_true")
    parser.add_argument(
        "--seed-last-contexts",
        action="store_true",
        help="With --start-at-end, seed the latest valid pre-existing v28 context per market before following.",
    )
    parser.add_argument(
        "--enrich-missing-market-metadata",
        action="store_true",
        help="Use public Kalshi market metadata for context rows, such as 90-touch policy eval rows, that lack strike.",
    )
    parser.add_argument("--kalshi-base-url", default="")
    parser.add_argument("--market-lookup-timeout-seconds", default=5.0, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    status = run_v28_context_tailer(
        input_path=args.input,
        output_path=args.output,
        issue_path=args.issues,
        status_path=args.status,
        market_ticker=args.market_ticker,
        settlement_ts_utc=_parse_dt(args.settlement_ts_utc) if args.settlement_ts_utc else None,
        follow=bool(args.follow),
        start_at_end=bool(args.start_at_end),
        poll_seconds=args.poll_seconds,
        run_seconds=args.run_seconds,
        max_rows=args.max_rows,
        append_ok=bool(args.append_ok),
        seed_last_contexts=bool(args.seed_last_contexts),
        enrich_missing_market_metadata=bool(args.enrich_missing_market_metadata),
        kalshi_base_url=args.kalshi_base_url or None,
        market_lookup_timeout_seconds=args.market_lookup_timeout_seconds,
    )
    print(f"contexts_written={status.contexts_written}")
    print(f"seeded_contexts={status.seeded_contexts}")
    print(f"issue_count={status.issue_count}")
    print(f"skipped_other_market={status.skipped_other_market}")
    print(f"skipped_unsupported_schema={status.skipped_unsupported_schema}")
    print(f"status={status.status}")
    print(f"output={status.output}")
    print(f"issues={status.issues}")
    print(f"status_path={args.status}")
    return 0


def _write_status(
    status_path: Path,
    *,
    input_path: Path,
    output_path: Path,
    issue_path: Path,
    status: str,
    market_ticker: str | None,
    contexts_written: int,
    seeded_contexts: int,
    issue_count: int,
    skipped_other_market: int,
    skipped_unsupported_schema: int,
    last_context_ts: str,
) -> V28ContextTailerStatus:
    payload = V28ContextTailerStatus(
        schema_version="v28-context-tailer-status-v1",
        source_input=str(input_path),
        output=str(output_path),
        issues=str(issue_path),
        status=status,
        market_ticker=market_ticker,
        contexts_written=contexts_written,
        seeded_contexts=seeded_contexts,
        issue_count=issue_count,
        skipped_other_market=skipped_other_market,
        skipped_unsupported_schema=skipped_unsupported_schema,
        last_context_ts_utc=last_context_ts,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    status_path.write_text(json.dumps(asdict(payload), indent=2, sort_keys=True), encoding="utf-8")
    return payload


def _seed_latest_contexts(
    input_path: Path,
    *,
    market_ticker: str | None,
    settlement_ts_utc: datetime | None,
    enrich_missing_market_metadata: bool,
    kalshi_base_url: str,
    market_lookup_timeout_seconds: float,
    market_metadata_cache: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    latest_by_market: dict[str, dict[str, Any]] = {}
    with input_path.open("r", encoding="utf-8", errors="replace") as src:
        for line in src:
            line = line.strip().lstrip("\ufeff")
            if not line:
                continue
            try:
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    continue
                event_market = str(payload.get("market") or payload.get("market_ticker") or "")
                if market_ticker and event_market != market_ticker:
                    continue
                if not is_supported_v28_context_event(payload):
                    continue
                market_metadata = _market_metadata_for_event(
                    payload,
                    enrich_missing_market_metadata=enrich_missing_market_metadata,
                    kalshi_base_url=kalshi_base_url,
                    market_lookup_timeout_seconds=market_lookup_timeout_seconds,
                    market_metadata_cache=market_metadata_cache,
                )
                context = context_from_v28_event(
                    payload,
                    market_ticker=market_ticker,
                    settlement_ts_utc=settlement_ts_utc,
                    market_metadata=market_metadata,
                )
                context["source"] = "v28_context_tailer_seed"
                latest_by_market[str(context["market_ticker"])] = context
            except Exception:
                continue
    return [latest_by_market[market] for market in sorted(latest_by_market)]


def _market_metadata_for_event(
    payload: dict[str, Any],
    *,
    enrich_missing_market_metadata: bool,
    kalshi_base_url: str,
    market_lookup_timeout_seconds: float,
    market_metadata_cache: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    if not enrich_missing_market_metadata:
        return None
    if payload.get("strike") not in (None, "") or payload.get("mushroom_v28_strike") not in (None, ""):
        return None
    market = str(payload.get("market") or payload.get("market_ticker") or "")
    if not market:
        return None
    if market not in market_metadata_cache:
        market_metadata_cache[market] = _fetch_market_metadata(
            kalshi_base_url,
            market,
            timeout_seconds=market_lookup_timeout_seconds,
        )
    return market_metadata_cache.get(market) or None


def _fetch_market_metadata(base_url: str, ticker: str, *, timeout_seconds: float) -> dict[str, Any]:
    query = urllib.parse.urlencode({"tickers": ticker, "limit": 10})
    url = f"{base_url.rstrip('/')}/markets?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "rv600-v28-context-tailer/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=max(1.0, float(timeout_seconds))) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return {}
    for market in payload.get("markets") or []:
        if str(market.get("ticker") or "") == ticker:
            return dict(market)
    return {}


def _get_env_value(key: str) -> str:
    value = os.getenv(key, "").strip()
    if value:
        return value
    env_path = Path(".env")
    if not env_path.exists():
        return ""
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        name, raw_value = raw.split("=", 1)
        if name.strip() == key:
            return raw_value.strip().strip('"').strip("'")
    return ""


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


if __name__ == "__main__":
    raise SystemExit(main())
