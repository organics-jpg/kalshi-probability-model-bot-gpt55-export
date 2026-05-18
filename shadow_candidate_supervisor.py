from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque


SUPERVISOR_ALLOW = "ALLOW"
SUPERVISOR_BLOCK = "BLOCK"


@dataclass(frozen=True)
class ShadowSupervisorConfig:
    profile_name: str
    lookback_markets: int = 4
    previous_day_candidate_net_threshold: float | None = None
    recent_candidate_pnl_threshold: float | None = None
    recent_stale_per_signal_threshold: float | None = None
    recent_exit_exception: int = 99
    market_block_length: int = 1


@dataclass(frozen=True)
class CandidateMarketObservation:
    market_ticker: str
    close_date_local: str
    session: str
    pnl_dollars: float
    outcome_type: str
    signal_count: int = 0
    stale_book_deferral_count: int = 0


@dataclass(frozen=True)
class ShadowSupervisorDecision:
    decision: str
    rationale_code: str
    summary_reason: str
    blocked_markets_remaining: int


@dataclass
class ShadowSupervisorState:
    recent_observations: Deque[CandidateMarketObservation] = field(default_factory=lambda: deque(maxlen=8))
    day_candidate_net_dollars: dict[str, float] = field(default_factory=dict)
    blocked_markets_remaining: int = 0


PROFILE_PRESETS: dict[str, ShadowSupervisorConfig] = {
    "live_90_78": ShadowSupervisorConfig(
        profile_name="live_90_78",
        lookback_markets=4,
        recent_candidate_pnl_threshold=2.5,
        recent_stale_per_signal_threshold=1.25,
        recent_exit_exception=3,
        market_block_length=1,
    ),
    "live_90_70": ShadowSupervisorConfig(
        profile_name="live_90_70",
        lookback_markets=4,
        previous_day_candidate_net_threshold=5.0,
        recent_candidate_pnl_threshold=3.0,
        recent_exit_exception=99,
        market_block_length=1,
    ),
}


def recent_candidate_summary(
    state: ShadowSupervisorState,
    *,
    lookback_markets: int,
) -> dict[str, float | int]:
    recent = list(state.recent_observations)[-max(1, int(lookback_markets)) :]
    recent_signal_count = sum(max(0, int(row.signal_count or 0)) for row in recent)
    return {
        "candidate_pnl_dollars": round(sum(float(row.pnl_dollars or 0.0) for row in recent), 4),
        "exit_count": int(sum(1 for row in recent if str(row.outcome_type or "").strip().lower() == "exit")),
        "signal_count": int(recent_signal_count),
        "stale_book_deferral_count": int(sum(max(0, int(row.stale_book_deferral_count or 0)) for row in recent)),
        "stale_per_signal": round(
            sum(max(0, int(row.stale_book_deferral_count or 0)) for row in recent) / max(1, recent_signal_count),
            4,
        ),
    }


def evaluate_shadow_supervisor(
    state: ShadowSupervisorState,
    config: ShadowSupervisorConfig,
    *,
    next_market_close_date_local: str,
) -> ShadowSupervisorDecision:
    current_day = str(next_market_close_date_local or "").strip()
    completed_prior_days = [day for day in sorted(state.day_candidate_net_dollars) if day < current_day]
    previous_day_net = state.day_candidate_net_dollars.get(completed_prior_days[-1], 0.0) if completed_prior_days else 0.0

    if config.previous_day_candidate_net_threshold is not None and float(previous_day_net or 0.0) >= float(
        config.previous_day_candidate_net_threshold
    ):
        return ShadowSupervisorDecision(
            decision=SUPERVISOR_BLOCK,
            rationale_code="PREVIOUS_DAY_OVERHEATED",
            summary_reason="Previous shadow candidate day net was hot, so the next market is blocked.",
            blocked_markets_remaining=max(0, int(config.market_block_length) - 1),
        )

    if state.blocked_markets_remaining > 0:
        return ShadowSupervisorDecision(
            decision=SUPERVISOR_BLOCK,
            rationale_code="MARKET_COOLDOWN_ACTIVE",
            summary_reason="A short shadow cooldown is still active from a recent hot cluster.",
            blocked_markets_remaining=max(0, int(state.blocked_markets_remaining)),
        )

    summary = recent_candidate_summary(state, lookback_markets=config.lookback_markets)
    recent_candidate_pnl = float(summary["candidate_pnl_dollars"])
    recent_exit_count = int(summary["exit_count"])
    recent_stale_per_signal = float(summary["stale_per_signal"])

    recent_pnl_hot = (
        config.recent_candidate_pnl_threshold is not None
        and recent_candidate_pnl >= float(config.recent_candidate_pnl_threshold)
    )
    recent_stale_hot = (
        config.recent_stale_per_signal_threshold is not None
        and recent_stale_per_signal >= float(config.recent_stale_per_signal_threshold)
    )
    exit_exception_active = recent_exit_count >= int(config.recent_exit_exception)
    if (recent_pnl_hot or recent_stale_hot) and not exit_exception_active:
        rationale = "RECENT_CANDIDATE_PNL_HOT"
        reason = "Recent shadow candidate outcomes are overheated, so the next market is blocked."
        if recent_stale_hot and not recent_pnl_hot:
            rationale = "RECENT_STALE_PRESSURE_HOT"
            reason = "Recent stale pressure is too high, so the next market is blocked."
        elif recent_pnl_hot and recent_stale_hot:
            rationale = "RECENT_PNL_AND_STALE_HOT"
            reason = "Recent shadow candidate PnL and stale pressure are both hot, so the next market is blocked."
        return ShadowSupervisorDecision(
            decision=SUPERVISOR_BLOCK,
            rationale_code=rationale,
            summary_reason=reason,
            blocked_markets_remaining=max(0, int(config.market_block_length) - 1),
        )

    return ShadowSupervisorDecision(
        decision=SUPERVISOR_ALLOW,
        rationale_code="SHADOW_REGIME_OK",
        summary_reason="Recent shadow candidate outcomes do not show an overheated regime.",
        blocked_markets_remaining=0,
    )


def apply_supervisor_decision(state: ShadowSupervisorState, decision: ShadowSupervisorDecision) -> None:
    if decision.decision == SUPERVISOR_BLOCK:
        state.blocked_markets_remaining = max(0, int(decision.blocked_markets_remaining))
    else:
        state.blocked_markets_remaining = 0


def record_candidate_market_outcome(
    state: ShadowSupervisorState,
    observation: CandidateMarketObservation,
) -> None:
    state.recent_observations.append(observation)
    day_key = str(observation.close_date_local or "").strip()
    state.day_candidate_net_dollars[day_key] = round(
        float(state.day_candidate_net_dollars.get(day_key, 0.0)) + float(observation.pnl_dollars or 0.0),
        4,
    )
    if state.blocked_markets_remaining > 0:
        state.blocked_markets_remaining = max(0, int(state.blocked_markets_remaining) - 1)
