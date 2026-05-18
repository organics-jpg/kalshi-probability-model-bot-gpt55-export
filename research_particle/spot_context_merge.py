from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


class SpotContextMergeError(ValueError):
    pass


@dataclass(frozen=True)
class SpotContextMergeResult:
    schema_version: str
    contexts_read: int
    contexts_written: int
    contexts_with_independent_spot: int
    issue_count: int
    max_age_ms: float
    require_spot: bool
    output: str
    issues: str


@dataclass(frozen=True)
class SpotTickRow:
    available_ts_utc: datetime
    exchange_ts_utc: datetime
    price: float
    source: str


def merge_contexts_with_spot(
    *,
    context_path: Path,
    spot_path: Path,
    output_path: Path,
    issue_path: Path,
    max_age_ms: float = 5_000.0,
    require_spot: bool = False,
) -> SpotContextMergeResult:
    ticks = load_spot_ticks(spot_path)
    contexts_read = 0
    contexts_written = 0
    contexts_with_spot = 0
    issues = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as out, issue_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as bad:
        for line_number, context in enumerate(_read_jsonl(context_path), start=1):
            contexts_read += 1
            try:
                context_ts = _parse_dt_required(context, "context_ts_utc")
                tick = _latest_spot_tick(ticks, context_ts)
                if tick is None:
                    raise SpotContextMergeError("no spot tick at or before context timestamp")
                age_ms = 1000.0 * (context_ts - tick.available_ts_utc).total_seconds()
                if age_ms > max_age_ms:
                    raise SpotContextMergeError(
                        f"latest independent spot is too old: age_ms={age_ms:.3f}"
                    )
                merged = dict(context)
                merged["original_spot"] = context.get("spot")
                merged["original_spot_ts_utc"] = context.get("spot_ts_utc")
                merged["spot"] = tick.price
                merged["spot_ts_utc"] = tick.available_ts_utc.isoformat()
                merged["independent_spot_source"] = tick.source
                merged["independent_spot_exchange_ts_utc"] = tick.exchange_ts_utc.isoformat()
                merged["independent_spot_available_ts_utc"] = tick.available_ts_utc.isoformat()
                merged["independent_spot_age_ms"] = age_ms
                merged["source"] = "merged_independent_spot_context"
                out.write(json.dumps(merged, sort_keys=True) + "\n")
                contexts_written += 1
                contexts_with_spot += 1
            except Exception as exc:
                issues += 1
                bad.write(
                    json.dumps(
                        {
                            "line_number": line_number,
                            "market_ticker": context.get("market_ticker"),
                            "reason": str(exc),
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
                if not require_spot:
                    out.write(json.dumps(context, sort_keys=True) + "\n")
                    contexts_written += 1
    return SpotContextMergeResult(
        schema_version="spot-context-merge-result-v1",
        contexts_read=contexts_read,
        contexts_written=contexts_written,
        contexts_with_independent_spot=contexts_with_spot,
        issue_count=issues,
        max_age_ms=float(max_age_ms),
        require_spot=bool(require_spot),
        output=str(output_path),
        issues=str(issue_path),
    )


def load_spot_ticks(path: Path) -> list[SpotTickRow]:
    ticks: list[SpotTickRow] = []
    for raw in _read_jsonl(path):
        available_value = (
            raw.get("local_recv_ts_utc")
            or raw.get("recv_ts_utc")
            or raw.get("ts_utc")
            or raw.get("exchange_ts_utc")
        )
        exchange_value = raw.get("exchange_ts_utc") or available_value
        price = raw.get("price")
        if available_value in (None, "") or exchange_value in (None, "") or price in (None, ""):
            continue
        ticks.append(
            SpotTickRow(
                available_ts_utc=_parse_dt(available_value),
                exchange_ts_utc=_parse_dt(exchange_value),
                price=float(price),
                source=str(raw.get("source") or "spot_tick"),
            )
        )
    ticks.sort(key=lambda tick: tick.available_ts_utc)
    return ticks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merge independent BTC spot ticks into passive particle context rows without future leakage."
    )
    parser.add_argument("--contexts", required=True, type=Path)
    parser.add_argument("--spot-ticks", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--issues", required=True, type=Path)
    parser.add_argument("--max-age-ms", default=5000.0, type=float)
    parser.add_argument("--require-spot", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = merge_contexts_with_spot(
        context_path=args.contexts,
        spot_path=args.spot_ticks,
        output_path=args.output,
        issue_path=args.issues,
        max_age_ms=args.max_age_ms,
        require_spot=bool(args.require_spot),
    )
    print(f"contexts_read={result.contexts_read}")
    print(f"contexts_written={result.contexts_written}")
    print(f"contexts_with_independent_spot={result.contexts_with_independent_spot}")
    print(f"issue_count={result.issue_count}")
    print(f"output={result.output}")
    print(f"issues={result.issues}")
    return 0


def _latest_spot_tick(ticks: list[SpotTickRow], context_ts: datetime) -> SpotTickRow | None:
    selected: SpotTickRow | None = None
    for tick in ticks:
        if tick.available_ts_utc <= context_ts:
            selected = tick
        else:
            break
    return selected


def _read_jsonl(path: Path) -> Iterable[Mapping[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise SpotContextMergeError("JSONL row is not an object")
            yield payload


def _parse_dt_required(row: Mapping[str, Any], key: str) -> datetime:
    if row.get(key) in (None, ""):
        raise SpotContextMergeError(f"context missing {key}")
    return _parse_dt(row[key])


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


if __name__ == "__main__":
    raise SystemExit(main())
