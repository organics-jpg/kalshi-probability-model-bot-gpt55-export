from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


REQUIRED_RAW_FIELDS = {
    "market_ticker",
    "decision_ts_utc",
    "recv_ts_utc",
    "strike",
    "spot",
    "yes_ask_cents",
    "no_ask_cents",
    "fee_cents",
    "fill_prob",
    "current_calibrated_p_yes",
}


class CandidateContextError(ValueError):
    pass


def build_candidate_context(raw: Mapping[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED_RAW_FIELDS - set(raw))
    if missing:
        raise CandidateContextError(f"missing required raw fields: {', '.join(missing)}")
    decision_ts = _parse_dt(raw["decision_ts_utc"])
    recv_ts = _parse_dt(raw["recv_ts_utc"])
    if recv_ts > decision_ts:
        raise CandidateContextError("recv_ts_utc cannot be after decision_ts_utc")
    settlement_ts = _settlement_ts(raw, decision_ts)
    yes_ask = _cents(raw["yes_ask_cents"], "yes_ask_cents")
    no_ask = _cents(raw["no_ask_cents"], "no_ask_cents")
    context = {
        "market_ticker": str(raw["market_ticker"]),
        "decision_ts_utc": decision_ts.isoformat(),
        "recv_ts_utc": recv_ts.isoformat(),
        "settlement_ts_utc": settlement_ts.isoformat(),
        "strike": float(raw["strike"]),
        "spot": float(raw["spot"]),
        "yes_ask_cents": yes_ask,
        "no_ask_cents": no_ask,
        "fee_cents": _nonnegative_float(raw["fee_cents"], "fee_cents"),
        "fill_prob": _prob(raw["fill_prob"], "fill_prob"),
        "current_calibrated_p_yes": _prob(
            raw["current_calibrated_p_yes"],
            "current_calibrated_p_yes",
        ),
        "source": raw.get("source", "candidate_contexts"),
    }
    for optional in (
        "book_age_ms",
        "btc_age_ms",
        "yes_bid_cents",
        "no_bid_cents",
        "depth_ratio",
        "depth_count",
        "seconds_to_close",
        "yes_fill_prob",
        "no_fill_prob",
    ):
        if optional in raw and raw[optional] not in (None, ""):
            context[optional] = float(raw[optional])
    for optional_prob in ("yes_fill_prob", "no_fill_prob"):
        if optional_prob in context:
            context[optional_prob] = _prob(context[optional_prob], optional_prob)
    return context


def normalize_candidate_contexts(input_path: Path, output_path: Path, issue_path: Path) -> tuple[int, int]:
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
            raw = json.loads(line)
            try:
                out.write(json.dumps(build_candidate_context(raw), sort_keys=True) + "\n")
                written += 1
            except Exception as exc:
                bad.write(
                    json.dumps(
                        {
                            "line_number": line_number,
                            "reason": str(exc),
                            "market_ticker": raw.get("market_ticker"),
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
                issues += 1
    return written, issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize raw exact two-sided candidate observations into particle candidate context JSONL."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--issues", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written, issues = normalize_candidate_contexts(args.input, args.output, args.issues)
    print(f"written_contexts={written}")
    print(f"issue_count={issues}")
    print(f"output={args.output}")
    print(f"issues={args.issues}")
    return 0


def _settlement_ts(raw: Mapping[str, Any], decision_ts: datetime) -> datetime:
    if raw.get("settlement_ts_utc"):
        return _parse_dt(raw["settlement_ts_utc"])
    if raw.get("seconds_to_close") not in (None, ""):
        return decision_ts + timedelta(seconds=max(0.0, float(raw["seconds_to_close"])))
    raise CandidateContextError("missing settlement_ts_utc or seconds_to_close")


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _prob(value: Any, name: str) -> float:
    p = float(value)
    if not 0.0 <= p <= 1.0:
        raise CandidateContextError(f"{name} must be in [0, 1]")
    return p


def _cents(value: Any, name: str) -> float:
    cents = float(value)
    if not 0.0 <= cents <= 100.0:
        raise CandidateContextError(f"{name} must be in [0, 100]")
    return cents


def _nonnegative_float(value: Any, name: str) -> float:
    number = float(value)
    if number < 0.0:
        raise CandidateContextError(f"{name} must be non-negative")
    return number


if __name__ == "__main__":
    raise SystemExit(main())
