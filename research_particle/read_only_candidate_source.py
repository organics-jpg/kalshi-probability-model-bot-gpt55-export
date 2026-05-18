from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


class CandidateSourceError(ValueError):
    pass


@dataclass(frozen=True)
class TopOfBookObservation:
    """Read-only top-of-book observation for all-candidate shadow recording."""

    market_ticker: str
    decision_ts_utc: datetime
    recv_ts_utc: datetime
    settlement_ts_utc: datetime
    strike: float
    spot: float
    yes_bid_cents: float
    no_bid_cents: float
    yes_bid_depth: float
    no_bid_depth: float
    current_calibrated_p_yes: float
    position_size: int = 1
    source: str = "read_only_candidate_source"
    book_age_ms: float | None = None
    btc_age_ms: float | None = None
    seconds_to_close: float | None = None


def build_raw_candidate_observation(observation: TopOfBookObservation) -> dict[str, Any]:
    """Build a strict raw candidate row from exact bid-book state.

    Kalshi binary buys are implied by the opposite side's bid book:
    buying YES consumes NO bids, so YES ask is 100 - best NO bid.
    buying NO consumes YES bids, so NO ask is 100 - best YES bid.
    """

    _validate_timestamp_order(observation.recv_ts_utc, observation.decision_ts_utc)
    yes_bid = _cents(observation.yes_bid_cents, "yes_bid_cents")
    no_bid = _cents(observation.no_bid_cents, "no_bid_cents")
    yes_ask = 100.0 - no_bid
    no_ask = 100.0 - yes_bid
    size = max(1, int(observation.position_size))
    yes_fill_prob = fill_probability_from_visible_depth(observation.no_bid_depth, size)
    no_fill_prob = fill_probability_from_visible_depth(observation.yes_bid_depth, size)
    fee_cents = max(
        estimated_kalshi_order_fee_cents(round(yes_ask), size),
        estimated_kalshi_order_fee_cents(round(no_ask), size),
    ) / float(size)
    row: dict[str, Any] = {
        "market_ticker": str(observation.market_ticker),
        "decision_ts_utc": _iso(observation.decision_ts_utc),
        "recv_ts_utc": _iso(observation.recv_ts_utc),
        "settlement_ts_utc": _iso(observation.settlement_ts_utc),
        "strike": float(observation.strike),
        "spot": _positive_float(observation.spot, "spot"),
        "yes_ask_cents": yes_ask,
        "no_ask_cents": no_ask,
        "fee_cents": fee_cents,
        "fill_prob": min(yes_fill_prob, no_fill_prob),
        "yes_fill_prob": yes_fill_prob,
        "no_fill_prob": no_fill_prob,
        "current_calibrated_p_yes": _prob(
            observation.current_calibrated_p_yes,
            "current_calibrated_p_yes",
        ),
        "yes_bid_cents": yes_bid,
        "no_bid_cents": no_bid,
        "depth_count": min(
            _nonnegative_float(observation.yes_bid_depth, "yes_bid_depth"),
            _nonnegative_float(observation.no_bid_depth, "no_bid_depth"),
        ),
        "position_size": size,
        "source": observation.source,
    }
    if observation.book_age_ms is not None:
        row["book_age_ms"] = _nonnegative_float(observation.book_age_ms, "book_age_ms")
    if observation.btc_age_ms is not None:
        row["btc_age_ms"] = _nonnegative_float(observation.btc_age_ms, "btc_age_ms")
    if observation.seconds_to_close is not None:
        row["seconds_to_close"] = _nonnegative_float(
            observation.seconds_to_close,
            "seconds_to_close",
        )
    return row


def estimated_kalshi_order_fee_cents(price_cents: int | float, count: int) -> int:
    bounded_price = max(1, min(99, int(round(float(price_cents)))))
    size = max(1, int(count))
    numerator = 7 * size * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def fill_probability_from_visible_depth(depth_contracts: float, position_size: int) -> float:
    depth = _nonnegative_float(depth_contracts, "depth_contracts")
    size = max(1, int(position_size))
    return min(1.0, depth / float(size))


def observation_from_mapping(raw: Mapping[str, Any]) -> TopOfBookObservation:
    missing = sorted(
        {
            "market_ticker",
            "decision_ts_utc",
            "recv_ts_utc",
            "settlement_ts_utc",
            "strike",
            "spot",
            "yes_bid_cents",
            "no_bid_cents",
            "yes_bid_depth",
            "no_bid_depth",
            "current_calibrated_p_yes",
        }
        - set(raw)
    )
    if missing:
        raise CandidateSourceError(f"missing required observation fields: {', '.join(missing)}")
    return TopOfBookObservation(
        market_ticker=str(raw["market_ticker"]),
        decision_ts_utc=_parse_dt(raw["decision_ts_utc"]),
        recv_ts_utc=_parse_dt(raw["recv_ts_utc"]),
        settlement_ts_utc=_parse_dt(raw["settlement_ts_utc"]),
        strike=float(raw["strike"]),
        spot=float(raw["spot"]),
        yes_bid_cents=float(raw["yes_bid_cents"]),
        no_bid_cents=float(raw["no_bid_cents"]),
        yes_bid_depth=float(raw["yes_bid_depth"]),
        no_bid_depth=float(raw["no_bid_depth"]),
        current_calibrated_p_yes=float(raw["current_calibrated_p_yes"]),
        position_size=int(raw.get("position_size") or 1),
        source=str(raw.get("source") or "read_only_candidate_source"),
        book_age_ms=_optional_float(raw, "book_age_ms"),
        btc_age_ms=_optional_float(raw, "btc_age_ms"),
        seconds_to_close=_optional_float(raw, "seconds_to_close"),
    )


def convert_observations(input_path: Path, output_path: Path, issue_path: Path) -> tuple[int, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    issues = 0
    with input_path.open("r", encoding="utf-8") as src, output_path.open(
        "w", encoding="utf-8"
    ) as out, issue_path.open("w", encoding="utf-8") as bad:
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
                observation = observation_from_mapping(raw)
                out.write(json.dumps(build_raw_candidate_observation(observation), sort_keys=True) + "\n")
                written += 1
            except Exception as exc:
                bad.write(
                    json.dumps(
                        {
                            "line_number": line_number,
                            "market_ticker": raw.get("market_ticker"),
                            "reason": str(exc),
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
                issues += 1
    return written, issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert read-only top-of-book observations into strict raw candidate rows."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--issues", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written, issues = convert_observations(args.input, args.output, args.issues)
    print(f"written_observations={written}")
    print(f"issue_count={issues}")
    print(f"output={args.output}")
    print(f"issues={args.issues}")
    return 0


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return _parse_dt(dt).isoformat()


def _validate_timestamp_order(recv_ts: datetime, decision_ts: datetime) -> None:
    if _parse_dt(recv_ts) > _parse_dt(decision_ts):
        raise CandidateSourceError("recv_ts_utc cannot be after decision_ts_utc")


def _prob(value: Any, name: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise CandidateSourceError(f"{name} must be in [0, 1]")
    return number


def _cents(value: Any, name: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 100.0:
        raise CandidateSourceError(f"{name} must be in [0, 100]")
    return number


def _positive_float(value: Any, name: str) -> float:
    number = float(value)
    if number <= 0.0:
        raise CandidateSourceError(f"{name} must be positive")
    return number


def _nonnegative_float(value: Any, name: str) -> float:
    number = float(value)
    if number < 0.0:
        raise CandidateSourceError(f"{name} must be non-negative")
    return number


def _optional_float(raw: Mapping[str, Any], name: str) -> float | None:
    if name not in raw or raw[name] in (None, ""):
        return None
    return float(raw[name])


if __name__ == "__main__":
    raise SystemExit(main())
