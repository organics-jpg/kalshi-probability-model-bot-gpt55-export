from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


def build_label_contexts_from_market_results(
    candidate_snapshots_path: Path,
    market_results_path: Path,
    output_path: Path,
) -> tuple[int, int]:
    strikes = load_candidate_strikes(candidate_snapshots_path)
    results = load_market_results(market_results_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    with output_path.open("w", encoding="utf-8") as out:
        for result in results:
            market = str(result.get("market") or result.get("market_ticker") or "")
            outcome = str(result.get("result") or "").lower()
            if market not in strikes or outcome not in {"yes", "no"}:
                skipped += 1
                continue
            strike = strikes[market]
            settlement_ts = str(result.get("settlement_ts") or result.get("close_time") or "")
            if not settlement_ts:
                skipped += 1
                continue
            label_available_ts = settlement_ts
            settlement_price = strike + 1.0 if outcome == "yes" else strike - 1.0
            out.write(
                json.dumps(
                    {
                        "market_ticker": market,
                        "settlement_ts_utc": _parse_dt(settlement_ts).isoformat(),
                        "label_available_ts_utc": _parse_dt(label_available_ts).isoformat(),
                        "settlement_price": settlement_price,
                        "strike": strike,
                        "binary_result": outcome,
                        "settlement_price_is_binary_proxy": True,
                        "source": result.get("source", "market_results"),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            written += 1
    return written, skipped


def load_candidate_strikes(path: Path) -> dict[str, float]:
    strikes: dict[str, float] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            raw = payload.get("snapshot", payload)
            market = str(raw.get("market_ticker") or "")
            if not market:
                continue
            strikes[market] = float(raw["strike"])
    return strikes


def load_market_results(path: Path) -> list[Mapping[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        return [row for row in value if isinstance(row, Mapping)]
    if isinstance(value, Mapping):
        rows = []
        for key, row in value.items():
            if isinstance(row, Mapping):
                enriched = dict(row)
                enriched.setdefault("market", key)
                rows.append(enriched)
        return rows
    return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build particle settlement label contexts by joining candidate strikes to Kalshi market results."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--market-results", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written, skipped = build_label_contexts_from_market_results(
        args.candidates,
        args.market_results,
        args.output,
    )
    print(f"written_labels={written}")
    print(f"skipped_results={skipped}")
    print(f"output={args.output}")
    return 0


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


if __name__ == "__main__":
    raise SystemExit(main())

