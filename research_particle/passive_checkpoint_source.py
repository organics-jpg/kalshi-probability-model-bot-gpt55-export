from __future__ import annotations

import argparse
import glob
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .read_only_candidate_source import (
    CandidateSourceError,
    TopOfBookObservation,
    build_raw_candidate_observation,
)


@dataclass(frozen=True)
class PassiveCheckpointContext:
    market_ticker: str
    context_ts_utc: datetime
    strike: float
    settlement_ts_utc: datetime
    spot: float
    current_calibrated_p_yes: float
    position_size: int = 1
    spot_ts_utc: datetime | None = None
    source: str = "passive_checkpoint_source"


def build_observation_from_passive_checkpoint(
    checkpoint: Mapping[str, Any],
    context: PassiveCheckpointContext,
) -> dict[str, Any]:
    market_ticker = str(checkpoint.get("market_ticker") or "")
    if not market_ticker:
        raise CandidateSourceError("checkpoint missing market_ticker")
    if market_ticker != context.market_ticker:
        raise CandidateSourceError("checkpoint/context market_ticker mismatch")
    decision_ts = _checkpoint_ts(checkpoint)
    if context.context_ts_utc > decision_ts:
        raise CandidateSourceError("context_ts_utc cannot be after checkpoint timestamp")
    seconds_to_close = max(0.0, (context.settlement_ts_utc - decision_ts).total_seconds())
    btc_age_ms = None
    if context.spot_ts_utc is not None:
        if context.spot_ts_utc > decision_ts:
            raise CandidateSourceError("spot_ts_utc cannot be after checkpoint timestamp")
        btc_age_ms = max(0.0, 1000.0 * (decision_ts - context.spot_ts_utc).total_seconds())
    yes_bid, yes_depth = _top_level(checkpoint, "yes")
    no_bid, no_depth = _top_level(checkpoint, "no")
    return build_raw_candidate_observation(
        TopOfBookObservation(
            market_ticker=market_ticker,
            decision_ts_utc=decision_ts,
            recv_ts_utc=decision_ts,
            settlement_ts_utc=context.settlement_ts_utc,
            strike=context.strike,
            spot=context.spot,
            yes_bid_cents=yes_bid,
            no_bid_cents=no_bid,
            yes_bid_depth=yes_depth,
            no_bid_depth=no_depth,
            current_calibrated_p_yes=context.current_calibrated_p_yes,
            position_size=context.position_size,
            source=context.source,
            book_age_ms=0.0,
            btc_age_ms=btc_age_ms,
            seconds_to_close=seconds_to_close,
        )
    )


def load_contexts(path: Path) -> dict[str, list[PassiveCheckpointContext]]:
    contexts: dict[str, list[PassiveCheckpointContext]] = {}
    for raw in _read_json_or_jsonl(path):
        context = context_from_mapping(raw)
        contexts.setdefault(context.market_ticker, []).append(context)
    for rows in contexts.values():
        rows.sort(key=lambda context: context.context_ts_utc)
    return contexts


def context_from_mapping(raw: Mapping[str, Any]) -> PassiveCheckpointContext:
    missing = sorted(
        {
            "market_ticker",
            "context_ts_utc",
            "strike",
            "settlement_ts_utc",
            "spot",
            "current_calibrated_p_yes",
        }
        - set(raw)
    )
    if missing:
        raise CandidateSourceError(f"missing context fields: {', '.join(missing)}")
    return PassiveCheckpointContext(
        market_ticker=str(raw["market_ticker"]),
        context_ts_utc=_parse_dt(raw["context_ts_utc"]),
        strike=float(raw["strike"]),
        settlement_ts_utc=_parse_dt(raw["settlement_ts_utc"]),
        spot=float(raw["spot"]),
        current_calibrated_p_yes=float(raw["current_calibrated_p_yes"]),
        position_size=int(raw.get("position_size") or 1),
        spot_ts_utc=(
            _parse_dt(raw["spot_ts_utc"])
            if raw.get("spot_ts_utc") not in (None, "")
            else None
        ),
        source=str(raw.get("source") or "passive_checkpoint_source"),
    )


def convert_passive_checkpoints(
    checkpoint_path: Path,
    context_path: Path,
    output_path: Path,
    issue_path: Path,
) -> tuple[int, int]:
    contexts = load_contexts(context_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    issues = 0
    with output_path.open("w", encoding="utf-8") as out, issue_path.open(
        "w", encoding="utf-8"
    ) as bad:
        for source_path in _checkpoint_files(checkpoint_path):
            with source_path.open("r", encoding="utf-8") as src:
                for line_number, line in enumerate(src, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    raw: Mapping[str, Any] = {}
                    try:
                        payload = json.loads(line)
                        if not isinstance(payload, dict):
                            raise CandidateSourceError("line is not a JSON object")
                        raw = payload
                        market_ticker = str(raw.get("market_ticker") or "")
                        if market_ticker not in contexts:
                            raise CandidateSourceError("missing context for market_ticker")
                        checkpoint_ts = _checkpoint_ts(raw)
                        context = _latest_available_context(contexts[market_ticker], checkpoint_ts)
                        row = build_observation_from_passive_checkpoint(raw, context)
                        out.write(json.dumps(row, sort_keys=True) + "\n")
                        written += 1
                    except Exception as exc:
                        bad.write(
                            json.dumps(
                                {
                                    "line_number": line_number,
                                    "market_ticker": raw.get("market_ticker"),
                                    "reason": str(exc),
                                    "source_path": str(source_path),
                                },
                                sort_keys=True,
                            )
                            + "\n"
                        )
                        issues += 1
    return written, issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert passive orderbook checkpoints plus BTC/model context into strict particle candidate rows."
    )
    parser.add_argument("--checkpoints", required=True, type=Path)
    parser.add_argument("--contexts", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--issues", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written, issues = convert_passive_checkpoints(
        args.checkpoints,
        args.contexts,
        args.output,
        args.issues,
    )
    print(f"written_observations={written}")
    print(f"issue_count={issues}")
    print(f"output={args.output}")
    print(f"issues={args.issues}")
    return 0


def _checkpoint_ts(checkpoint: Mapping[str, Any]) -> datetime:
    for key in ("checkpoint_ts", "ts_wall", "local_recv_ts"):
        if checkpoint.get(key) not in (None, ""):
            return _parse_dt(checkpoint[key])
    raise CandidateSourceError("checkpoint missing checkpoint_ts")


def _checkpoint_files(path: Path) -> list[Path]:
    path_text = str(path)
    if any(marker in path_text for marker in ("*", "?", "[")):
        matches = [Path(match) for match in glob.glob(path_text, recursive=True)]
        files = sorted(match for match in matches if match.is_file())
        if not files:
            raise CandidateSourceError(f"checkpoint glob matched no files: {path_text}")
        return files
    if not path.is_file():
        raise CandidateSourceError(f"checkpoint path is not a file: {path}")
    return [path]


def _top_level(checkpoint: Mapping[str, Any], side: str) -> tuple[float, float]:
    prices = checkpoint.get(f"{side}_bid_prices")
    sizes = checkpoint.get(f"{side}_bid_sizes")
    if not isinstance(prices, list) or not prices:
        raise CandidateSourceError(f"checkpoint missing {side}_bid_prices")
    if not isinstance(sizes, list) or not sizes:
        raise CandidateSourceError(f"checkpoint missing {side}_bid_sizes")
    return float(prices[0]), float(sizes[0])


def _latest_available_context(
    contexts: list[PassiveCheckpointContext],
    checkpoint_ts: datetime,
) -> PassiveCheckpointContext:
    selected: PassiveCheckpointContext | None = None
    for context in contexts:
        if context.context_ts_utc <= checkpoint_ts:
            selected = context
        else:
            break
    if selected is None:
        raise CandidateSourceError("missing timestamp-available context for checkpoint")
    return selected


def _read_json_or_jsonl(path: Path) -> list[Mapping[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    if text.startswith("["):
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise CandidateSourceError("context JSON must be a list or JSONL")
        return [row for row in payload if isinstance(row, dict)]
    rows: list[Mapping[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise CandidateSourceError("context JSONL row is not an object")
        rows.append(payload)
    return rows


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
