from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

from .calibrators import LabelGatedACICalibrator
from .ev_decision import expected_pnl_cents
from .replay_runner import brownian_probability_from_snapshot, market_probability_from_asks
from .schemas import CandidateSnapshot
from .terminal_projection import simulate_terminal_samples, weighted_probability_yes


@dataclass(frozen=True)
class ParticleEngineConfig:
    annualized_vol: float
    sample_count: int = 2000
    seed: int = 0
    drift_per_second: float = 0.0
    jump_intensity_per_second: float = 0.0
    jump_mean_log_return: float = 0.0
    jump_std_log_return: float = 0.0
    no_fill_penalty_cents: float = 0.0


@dataclass(frozen=True)
class ParticlePrediction:
    particle_p_yes: float
    brownian_p_yes: float
    market_p_yes: float
    particle_calibrated_p_yes: float
    p_low: float
    p_high: float
    ev_yes_cents: float
    ev_no_cents: float
    seconds_to_close: float

    def as_shadow_extra(self, current_calibrated_p_yes: float | None = None) -> dict[str, float | str]:
        current = (
            self.particle_calibrated_p_yes
            if current_calibrated_p_yes is None
            else float(current_calibrated_p_yes)
        )
        source = "particle_calibrator_proxy" if current_calibrated_p_yes is None else "input_baseline"
        return {
            "particle_p_yes": self.particle_p_yes,
            "brownian_p_yes": self.brownian_p_yes,
            "market_p_yes": self.market_p_yes,
            "particle_calibrated_p_yes": self.particle_calibrated_p_yes,
            "current_calibrated_p_yes": current,
            "current_calibrated_p_yes_source": source,
            "p_low": self.p_low,
            "p_high": self.p_high,
            "ev_yes_cents": self.ev_yes_cents,
            "ev_no_cents": self.ev_no_cents,
            "seconds_to_close": self.seconds_to_close,
        }


class NextSecondParticleEngine:
    """Research-only terminal probability engine.

    This MVP uses a Brownian/jump terminal particle sampler. It does not use
    social, pinball, neural, or live execution layers.
    """

    def __init__(
        self,
        config: ParticleEngineConfig,
        calibrator: LabelGatedACICalibrator | None = None,
    ) -> None:
        self.config = config
        self.calibrator = calibrator or LabelGatedACICalibrator()

    def predict(
        self,
        snapshot: CandidateSnapshot,
        *,
        settlement_ts_utc: datetime,
    ) -> ParticlePrediction:
        seconds_to_close_float = (settlement_ts_utc - snapshot.decision_ts_utc).total_seconds()
        seconds_to_close = max(0, int(round(seconds_to_close_float)))
        seed = self._seed_for(snapshot)
        samples = simulate_terminal_samples(
            spot=snapshot.spot,
            seconds_to_close=seconds_to_close,
            annualized_vol=self.config.annualized_vol,
            sample_count=self.config.sample_count,
            seed=seed,
            drift_per_second=self.config.drift_per_second,
            jump_intensity_per_second=self.config.jump_intensity_per_second,
            jump_mean_log_return=self.config.jump_mean_log_return,
            jump_std_log_return=self.config.jump_std_log_return,
        )
        particle_p_yes = weighted_probability_yes(samples, snapshot.strike)
        current_p, (p_low, p_high) = self.calibrator.predict(particle_p_yes)
        ev_yes = expected_pnl_cents(
            p_win=current_p,
            ask_cents=snapshot.yes_ask_cents,
            fee_if_win_cents=snapshot.fee_cents,
            fill_prob=_fill_prob_for(snapshot, "yes"),
            no_fill_penalty_cents=self.config.no_fill_penalty_cents,
        )
        ev_no = expected_pnl_cents(
            p_win=1.0 - current_p,
            ask_cents=snapshot.no_ask_cents,
            fee_if_win_cents=snapshot.fee_cents,
            fill_prob=_fill_prob_for(snapshot, "no"),
            no_fill_penalty_cents=self.config.no_fill_penalty_cents,
        )
        return ParticlePrediction(
            particle_p_yes=particle_p_yes,
            brownian_p_yes=brownian_probability_from_snapshot(
                snapshot,
                settlement_ts_utc=settlement_ts_utc,
                annualized_vol=self.config.annualized_vol,
            ),
            market_p_yes=market_probability_from_asks(snapshot),
            particle_calibrated_p_yes=current_p,
            p_low=p_low,
            p_high=p_high,
            ev_yes_cents=ev_yes,
            ev_no_cents=ev_no,
            seconds_to_close=seconds_to_close_float,
        )

    def update_after_settlement(self, p_raw: float, result_yes: bool) -> None:
        self.calibrator.update_with_label(p_raw, 1 if result_yes else 0)

    def _seed_for(self, snapshot: CandidateSnapshot) -> int:
        # Stable per-candidate seed keeps strict replay deterministic.
        raw = f"{self.config.seed}|{snapshot.market_ticker}|{snapshot.decision_ts_utc.isoformat()}"
        digest = hashlib.sha256(raw.encode("utf-8")).digest()
        return int.from_bytes(digest[:4], "big")


def _fill_prob_for(snapshot: CandidateSnapshot, side: str) -> float:
    if side == "yes" and snapshot.yes_fill_prob is not None:
        return snapshot.yes_fill_prob
    if side == "no" and snapshot.no_fill_prob is not None:
        return snapshot.no_fill_prob
    return snapshot.fill_prob
