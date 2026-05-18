from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .recorders import CandidateSnapshotRecorder
from .schemas import CandidateSnapshot


class MissingShadowFieldError(ValueError):
    pass


REQUIRED_CONTEXT_FIELDS = {
    "market_ticker",
    "decision_ts_utc",
    "recv_ts_utc",
    "strike",
    "spot",
    "yes_ask_cents",
    "no_ask_cents",
    "fee_cents",
    "fill_prob",
}

REQUIRED_PREDICTION_FIELDS = {
    "particle_p_yes",
    "brownian_p_yes",
    "current_calibrated_p_yes",
}


def snapshot_from_shadow_context(context: Mapping[str, Any]) -> CandidateSnapshot:
    missing = sorted(REQUIRED_CONTEXT_FIELDS - set(context))
    if missing:
        raise MissingShadowFieldError(f"missing required candidate fields: {', '.join(missing)}")
    snapshot = CandidateSnapshot(
        market_ticker=str(context["market_ticker"]),
        decision_ts_utc=_parse_dt(context["decision_ts_utc"]),
        recv_ts_utc=_parse_dt(context["recv_ts_utc"]),
        strike=float(context["strike"]),
        spot=float(context["spot"]),
        yes_ask_cents=float(context["yes_ask_cents"]),
        no_ask_cents=float(context["no_ask_cents"]),
        fee_cents=float(context["fee_cents"]),
        fill_prob=float(context["fill_prob"]),
        yes_fill_prob=_optional_prob(context, "yes_fill_prob"),
        no_fill_prob=_optional_prob(context, "no_fill_prob"),
    )
    if snapshot.recv_ts_utc > snapshot.decision_ts_utc:
        raise ValueError("recv_ts_utc cannot be after decision_ts_utc for strict shadow recording")
    return snapshot


OPTIONAL_EXTRA_FIELDS = {
    "book_age_ms",
    "btc_age_ms",
    "depth_count",
    "depth_ratio",
    "market_p_yes",
    "particle_calibrated_p_yes",
    "current_calibrated_p_yes_source",
    "p_low",
    "p_high",
    "ev_yes_cents",
    "ev_no_cents",
    "seconds_to_close",
    "source_event_type",
    "source_decision_reason",
    "source_side",
}


def prediction_extra_from_shadow_context(context: Mapping[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED_PREDICTION_FIELDS - set(context))
    if missing:
        raise MissingShadowFieldError(f"missing required prediction fields: {', '.join(missing)}")
    extra = {
        "particle_p_yes": _prob(context["particle_p_yes"], "particle_p_yes"),
        "brownian_p_yes": _prob(context["brownian_p_yes"], "brownian_p_yes"),
        "current_calibrated_p_yes": _prob(
            context["current_calibrated_p_yes"],
            "current_calibrated_p_yes",
        ),
    }
    if "market_p_yes" in context:
        extra["market_p_yes"] = _prob(context["market_p_yes"], "market_p_yes")
    for field in OPTIONAL_EXTRA_FIELDS:
        if field in context and field not in extra:
            extra[field] = _extra_value(context[field], field)
    return extra


class ShadowCandidateAdapter:
    """Research-only adapter for future bot/probe candidate contexts."""

    def __init__(self, root: Path) -> None:
        self.recorder = CandidateSnapshotRecorder(root)

    def record_context(
        self,
        context: Mapping[str, Any],
        *,
        decision_shadow: str,
        reason: str,
    ) -> CandidateSnapshot:
        snapshot = snapshot_from_shadow_context(context)
        extra = prediction_extra_from_shadow_context(context)
        self.recorder.record(snapshot, decision_shadow=decision_shadow, reason=reason, extra=extra)
        return snapshot


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
        raise ValueError(f"{name} must be in [0, 1]")
    return p


def _optional_prob(context: Mapping[str, Any], name: str) -> float | None:
    if name not in context or context[name] in (None, ""):
        return None
    return _prob(context[name], name)


def _extra_value(value: Any, name: str) -> Any:
    if name in {"particle_calibrated_p_yes", "p_low", "p_high"}:
        return _prob(value, name)
    if name in {
        "book_age_ms",
        "btc_age_ms",
        "depth_count",
        "depth_ratio",
        "ev_yes_cents",
        "ev_no_cents",
        "seconds_to_close",
    }:
        return float(value)
    return value
