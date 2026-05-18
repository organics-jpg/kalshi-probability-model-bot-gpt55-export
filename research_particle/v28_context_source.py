from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping


class V28ContextSourceError(ValueError):
    pass


OLD_MUSHROOM_REQUIRED_FIELDS = (
    "ts_wall",
    "mushroom_v28_strike",
    "mushroom_v28_btc_price",
    "mushroom_v28_p_yes",
)
TOUCH90_REQUIRED_FIELDS = (
    "v28_p_yes",
    "seconds_to_close",
)
TOUCH90_EVENT_TYPES = {"v28_90_touch_policy_eval"}


def v28_context_event_schema(event: Mapping[str, Any]) -> str:
    if all(event.get(name) not in (None, "") for name in OLD_MUSHROOM_REQUIRED_FIELDS):
        return "mushroom_v28"
    event_type = str(event.get("event_type") or "")
    if event_type in TOUCH90_EVENT_TYPES and _event_market(event) and _event_ts_value(event) not in (None, ""):
        if all(event.get(name) not in (None, "") for name in TOUCH90_REQUIRED_FIELDS):
            return "v28_90_touch_policy_eval"
    return ""


def is_supported_v28_context_event(event: Mapping[str, Any]) -> bool:
    return bool(v28_context_event_schema(event))


def context_from_v28_event(
    event: Mapping[str, Any],
    *,
    market_ticker: str | None = None,
    settlement_ts_utc: datetime | None = None,
    market_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    schema = v28_context_event_schema(event)
    if schema == "mushroom_v28":
        return _context_from_mushroom_v28_event(
            event,
            market_ticker=market_ticker,
            settlement_ts_utc=settlement_ts_utc,
        )
    if schema == "v28_90_touch_policy_eval":
        return _context_from_touch90_event(
            event,
            market_ticker=market_ticker,
            settlement_ts_utc=settlement_ts_utc,
            market_metadata=market_metadata,
        )
    raise V28ContextSourceError("unsupported v28 context event schema")


def _context_from_mushroom_v28_event(
    event: Mapping[str, Any],
    *,
    market_ticker: str | None,
    settlement_ts_utc: datetime | None,
) -> dict[str, Any]:
    market = _event_market(event)
    if market_ticker and market != market_ticker:
        raise V28ContextSourceError("market_ticker does not match requested market")
    missing = sorted(
        name
        for name in OLD_MUSHROOM_REQUIRED_FIELDS
        if event.get(name) in (None, "")
    )
    if missing:
        raise V28ContextSourceError(f"missing v28 context fields: {', '.join(missing)}")
    context_ts = _parse_dt(_event_ts_value(event))
    seconds_to_close = _optional_float(event, "mushroom_v28_seconds_to_close")
    if settlement_ts_utc is None:
        if seconds_to_close is None:
            raise V28ContextSourceError("missing settlement_ts_utc override or mushroom_v28_seconds_to_close")
        settlement_ts = context_ts + timedelta(seconds=max(0.0, seconds_to_close))
    else:
        settlement_ts = _parse_dt(settlement_ts_utc)
    spot_ts = None
    btc_age_ms = _optional_float(event, "mushroom_v28_btc_age_ms")
    if btc_age_ms is not None and btc_age_ms >= 0.0:
        spot_ts = context_ts - timedelta(milliseconds=btc_age_ms)
    return {
        "market_ticker": market,
        "context_ts_utc": context_ts.isoformat(),
        "strike": float(event["mushroom_v28_strike"]),
        "settlement_ts_utc": settlement_ts.isoformat(),
        "spot": float(event["mushroom_v28_btc_price"]),
        "spot_ts_utc": spot_ts.isoformat() if spot_ts else context_ts.isoformat(),
        "current_calibrated_p_yes": _prob(event["mushroom_v28_p_yes"], "mushroom_v28_p_yes"),
        "position_size": 1,
        "source": "v28_execution_context_only",
    }


def _context_from_touch90_event(
    event: Mapping[str, Any],
    *,
    market_ticker: str | None,
    settlement_ts_utc: datetime | None,
    market_metadata: Mapping[str, Any] | None,
) -> dict[str, Any]:
    market = _event_market(event)
    if market_ticker and market != market_ticker:
        raise V28ContextSourceError("market_ticker does not match requested market")
    context_ts = _parse_dt(_event_ts_value(event))
    seconds_to_close = _optional_float(event, "seconds_to_close")
    if seconds_to_close is None:
        raise V28ContextSourceError("missing v28_90_touch seconds_to_close")

    metadata = market_metadata or {}
    strike = _first_float(event, ("strike", "mushroom_v28_strike"))
    if strike is None:
        strike = _market_metadata_strike(metadata)
    if strike is None:
        raise V28ContextSourceError("missing v28_90_touch strike and market metadata strike")

    if settlement_ts_utc is None:
        metadata_close = metadata.get("close_time") or metadata.get("expiration_time") or metadata.get("settlement_ts_utc")
        settlement_ts = _parse_dt(metadata_close) if metadata_close not in (None, "") else (
            context_ts + timedelta(seconds=max(0.0, seconds_to_close))
        )
    else:
        settlement_ts = _parse_dt(settlement_ts_utc)

    context: dict[str, Any] = {
        "market_ticker": market,
        "context_ts_utc": context_ts.isoformat(),
        "strike": float(strike),
        "settlement_ts_utc": settlement_ts.isoformat(),
        "current_calibrated_p_yes": _prob(event["v28_p_yes"], "v28_p_yes"),
        "position_size": int(float(event.get("position_size") or 1)),
        "source": "v28_90_touch_policy_eval_context",
        "context_event_schema": "v28_90_touch_policy_eval",
    }

    spot = _first_float(event, ("btc_price", "mushroom_v28_btc_price"))
    if spot is not None:
        context["spot"] = float(spot)
        btc_age_ms = _first_float(event, ("btc_age_ms", "mushroom_v28_btc_age_ms"))
        if btc_age_ms is not None and btc_age_ms >= 0.0:
            context["spot_ts_utc"] = (context_ts - timedelta(milliseconds=btc_age_ms)).isoformat()
        else:
            context["spot_ts_utc"] = context_ts.isoformat()
    else:
        context["requires_independent_spot"] = True
        context["spot_source"] = "missing_in_v28_90_touch_policy_eval"
    return context


def convert_v28_events_to_passive_contexts(
    input_path: Path,
    output_path: Path,
    issue_path: Path,
    *,
    market_ticker: str | None = None,
    start_ts_utc: datetime | None = None,
    end_ts_utc: datetime | None = None,
    settlement_ts_utc: datetime | None = None,
) -> tuple[int, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    start = _parse_dt(start_ts_utc) if start_ts_utc else None
    end = _parse_dt(end_ts_utc) if end_ts_utc else None
    settlement_ts = _parse_dt(settlement_ts_utc) if settlement_ts_utc else None
    written = 0
    issues = 0
    with input_path.open("r", encoding="utf-8", errors="replace") as src, output_path.open(
        "w", encoding="utf-8"
    ) as out, issue_path.open("w", encoding="utf-8") as bad:
        for line_number, line in enumerate(src, start=1):
            line = line.strip().lstrip("\ufeff")
            if not line:
                continue
            raw: Mapping[str, Any] = {}
            try:
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    raise V28ContextSourceError("line is not a JSON object")
                raw = payload
                context_ts = _parse_dt(raw.get("ts_wall"))
                if start and context_ts < start:
                    continue
                if end and context_ts > end:
                    continue
                context = context_from_v28_event(
                    raw,
                    market_ticker=market_ticker,
                    settlement_ts_utc=settlement_ts,
                )
                out.write(json.dumps(context, sort_keys=True) + "\n")
                written += 1
            except Exception as exc:
                market = raw.get("market") if raw else None
                if market_ticker and market not in (None, "", market_ticker):
                    continue
                bad.write(
                    json.dumps(
                        {
                            "line_number": line_number,
                            "market_ticker": market,
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
        description="Extract timestamped BTC/model context from v28 execution events for passive particle checkpoints."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--issues", required=True, type=Path)
    parser.add_argument("--market-ticker")
    parser.add_argument("--start-ts-utc")
    parser.add_argument("--end-ts-utc")
    parser.add_argument("--settlement-ts-utc")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written, issues = convert_v28_events_to_passive_contexts(
        args.input,
        args.output,
        args.issues,
        market_ticker=args.market_ticker,
        start_ts_utc=_parse_dt(args.start_ts_utc) if args.start_ts_utc else None,
        end_ts_utc=_parse_dt(args.end_ts_utc) if args.end_ts_utc else None,
        settlement_ts_utc=_parse_dt(args.settlement_ts_utc) if args.settlement_ts_utc else None,
    )
    print(f"written_contexts={written}")
    print(f"issue_count={issues}")
    print(f"output={args.output}")
    print(f"issues={args.issues}")
    return 0


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        if value in (None, ""):
            raise V28ContextSourceError("missing timestamp")
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _prob(value: Any, name: str) -> float:
    p = float(value)
    if not 0.0 <= p <= 1.0:
        raise V28ContextSourceError(f"{name} must be in [0, 1]")
    return p


def _optional_float(raw: Mapping[str, Any], name: str) -> float | None:
    if raw.get(name) in (None, ""):
        return None
    return float(raw[name])


def _event_market(event: Mapping[str, Any]) -> str:
    return str(event.get("market") or event.get("market_ticker") or "")


def _event_ts_value(event: Mapping[str, Any]) -> Any:
    return event.get("ts_wall") or event.get("decision_ts_utc")


def _first_float(raw: Mapping[str, Any], names: tuple[str, ...]) -> float | None:
    for name in names:
        if raw.get(name) not in (None, ""):
            return float(raw[name])
    return None


def _market_metadata_strike(market: Mapping[str, Any]) -> float | None:
    preferred_keys = (
        "strike",
        "custom_strike",
        "floor_strike",
        "cap_strike",
        "target_strike",
        "target_price",
        "price_level",
    )
    for key in preferred_keys:
        strike = _coerce_btc_strike(market.get(key))
        if strike is not None:
            return strike
    for key, value in market.items():
        key_l = str(key).lower()
        if "strike" not in key_l and "target" not in key_l:
            continue
        strike = _coerce_btc_strike(value)
        if strike is not None:
            return strike
    text_keys = (
        "title",
        "subtitle",
        "yes_sub_title",
        "no_sub_title",
        "rules_primary",
        "rules_secondary",
    )
    for key in text_keys:
        text = str(market.get(key) or "")
        for match in re.findall(r"\$?\b\d{2,3}(?:,\d{3})+(?:\.\d+)?\b|\$?\b\d{5,6}(?:\.\d+)?\b", text):
            strike = _coerce_btc_strike(match)
            if strike is not None:
                return strike
    return None


def _coerce_btc_strike(value: Any) -> float | None:
    if value in (None, ""):
        return None
    text = str(value).strip().replace("$", "").replace(",", "")
    try:
        strike = float(text)
    except (TypeError, ValueError):
        return None
    if 1_000.0 <= strike <= 1_000_000.0:
        return strike
    return None


if __name__ == "__main__":
    raise SystemExit(main())
