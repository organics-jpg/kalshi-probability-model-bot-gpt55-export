from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


SUPPORTED_EVENT_TYPES = {
    "mushroom_v28_rejected",
    "entry_signal_seen",
    "entry_snapshot_built",
    "entry_capacity_estimated",
    "entry_plan_built",
}


@dataclass(frozen=True)
class AdaptedEvent:
    context: dict[str, Any]
    source_event_type: str


@dataclass(frozen=True)
class AdapterIssue:
    reason: str
    market_ticker: str | None
    event_type: str | None
    ts_wall: str | None


def adapt_v28_event(
    event: Mapping[str, Any],
    *,
    annualized_vol: float | None = None,
) -> AdaptedEvent | AdapterIssue:
    event_type = _str_or_none(event.get("event_type"))
    if event_type not in SUPPORTED_EVENT_TYPES:
        return _issue("unsupported_event_type", event)

    market = _str_or_none(event.get("market_ticker") or event.get("market"))
    ts_wall = _str_or_none(event.get("ts_wall"))
    if not market or not ts_wall:
        return _issue("missing_market_or_ts_wall", event)

    side = _str_or_none(event.get("mushroom_v28_side") or event.get("side"))
    if side not in {"yes", "no"}:
        return _issue("missing_or_invalid_side", event)

    strike = _float_or_none(event.get("mushroom_v28_strike") or event.get("strike"))
    spot = _float_or_none(event.get("mushroom_v28_btc_price") or event.get("btc_price"))
    ask = _float_or_none(event.get("mushroom_v28_ask_cents") or event.get("ask_cents"))
    fee = _float_or_none(event.get("mushroom_v28_fee_cents") or event.get("fee_cents"))
    p_yes = _float_or_none(event.get("mushroom_v28_p_yes") or event.get("p_yes"))
    seconds_to_close = _float_or_none(
        event.get("mushroom_v28_seconds_to_close") or event.get("seconds_to_close")
    )
    if any(v is None for v in (strike, spot, ask, fee, p_yes, seconds_to_close)):
        return _issue("missing_core_v28_fields", event)

    yes_ask, no_ask = _two_sided_asks(event, side, ask)
    if yes_ask is None or no_ask is None:
        return _issue("missing_exact_two_sided_asks", event)

    decision_ts = _parse_dt(ts_wall)
    settlement_ts = decision_ts + timedelta(seconds=max(0.0, float(seconds_to_close)))
    fill_prob = _fill_prob_from_event(event)
    context = {
        "market_ticker": market,
        "decision_ts_utc": decision_ts.isoformat(),
        "recv_ts_utc": decision_ts.isoformat(),
        "settlement_ts_utc": settlement_ts.isoformat(),
        "strike": float(strike),
        "spot": float(spot),
        "yes_ask_cents": float(yes_ask),
        "no_ask_cents": float(no_ask),
        "fee_cents": float(fee),
        "fill_prob": fill_prob,
        "current_calibrated_p_yes": _prob(float(p_yes), "mushroom_v28_p_yes"),
        "source_event_type": event_type,
        "source_decision_reason": event.get("decision_reason") or event.get("mushroom_v28_reject_reason", ""),
        "source_side": side,
    }
    if annualized_vol is not None:
        context["annualized_vol"] = float(annualized_vol)
    return AdaptedEvent(context=context, source_event_type=event_type)


def adapt_v28_events_file(
    input_path: Path,
    output_path: Path,
    issue_path: Path,
    *,
    annualized_vol: float | None = None,
) -> tuple[int, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    adapted_count = 0
    issue_count = 0
    with input_path.open("r", encoding="utf-8") as src, output_path.open(
        "w", encoding="utf-8"
    ) as out, issue_path.open("w", encoding="utf-8") as issues:
        for line in src:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            result = adapt_v28_event(event, annualized_vol=annualized_vol)
            if isinstance(result, AdaptedEvent):
                out.write(json.dumps(result.context, sort_keys=True) + "\n")
                adapted_count += 1
            else:
                issues.write(json.dumps(result.__dict__, sort_keys=True) + "\n")
                issue_count += 1
    return adapted_count, issue_count


def _two_sided_asks(
    event: Mapping[str, Any],
    side: str,
    side_ask: float,
) -> tuple[float | None, float | None]:
    exact_yes = _float_or_none(event.get("yes_ask_cents"))
    exact_no = _float_or_none(event.get("no_ask_cents"))
    if exact_yes is not None and exact_no is not None:
        return exact_yes, exact_no

    # Some v28 candidate rows log only the side under evaluation. Use that
    # exact side ask, but never invent the opposite side quote.
    if side == "yes":
        return side_ask, exact_no
    return exact_yes, side_ask


def _fill_prob_from_event(event: Mapping[str, Any]) -> float:
    if "expected_fill_ratio_at_limit" in event:
        value = _float_or_none(event.get("expected_fill_ratio_at_limit"))
        if value is not None:
            return _prob(value, "expected_fill_ratio_at_limit")
    eligible = _float_or_none(event.get("eligible_depth") or event.get("mushroom_v28_eligible_depth"))
    required = _float_or_none(event.get("depth_required") or event.get("mushroom_v28_target_count"))
    if eligible is not None and required is not None and required > 0:
        return _prob(min(1.0, eligible / required), "fill_prob_from_depth")
    return 1.0


def _issue(reason: str, event: Mapping[str, Any]) -> AdapterIssue:
    return AdapterIssue(
        reason=reason,
        market_ticker=_str_or_none(event.get("market_ticker") or event.get("market")),
        event_type=_str_or_none(event.get("event_type")),
        ts_wall=_str_or_none(event.get("ts_wall")),
    )


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _str_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _prob(value: float, name: str) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return value

