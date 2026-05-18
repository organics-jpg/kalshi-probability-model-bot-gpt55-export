"""BTC Mushroom Forecaster v0.36 research candidate.

v36 is a probability-surface experiment, not a live-bot patch.

v35's longer 150-second settlement/proxy horizon improved recent validation and
holdout, but the stability audit showed damage in older short-time-to-close
blocks. That suggests the longer proxy smoothing is useful before the terminal
window, but too sharp near expiry where the final-average clock should dominate.

v36 therefore uses a piecewise/smooth proxy clock:
- keep the v34 110-second proxy horizon near expiry;
- blend toward the v35 150-second proxy horizon from 120s to 300s before close;
- keep the same materiality-gated 3-minute anti-persistence prior;
- keep the softer 1.02 posterior temperature from v35.
"""
from __future__ import annotations

from dataclasses import dataclass

from btc_mushroom_forecaster_v34_fast import FastMushroomFVEngineV34, FastMushroomV34Config


@dataclass
class FastMushroomV36Config(FastMushroomV34Config):
    short_settlement_average_seconds: float = 110.0
    long_settlement_average_seconds: float = 150.0
    proxy_blend_start_seconds: float = 120.0
    proxy_blend_end_seconds: float = 300.0
    settlement_average_seconds: float = 150.0
    exact_average_inside_seconds: float = 60.0
    anti_persistence_lag_minutes: int = 3
    anti_persistence_velocity_weight: float = -0.50
    anti_persistence_time_damp_power: float = 2.0
    anti_persistence_sigma_mult: float = 1.00
    anti_persistence_max_logit_weight: float = 0.10
    anti_persistence_shift_gate_center_dollars: float = 40.0
    anti_persistence_shift_gate_width_dollars: float = 5.0
    posterior_temperature: float = 1.02


class FastMushroomFVEngineV36(FastMushroomFVEngineV34):
    """v0.36 FV engine with a smooth short/long proxy horizon blend."""

    def __init__(self, config: FastMushroomV36Config | None = None) -> None:
        super().__init__(config or FastMushroomV36Config())

    def _effective_horizon_for_average(self, horizon_seconds: float, average_seconds: float) -> float:
        h_min = max(float(horizon_seconds) / 60.0, 1e-6)
        avg_min = max(float(average_seconds), 0.0) / 60.0
        exact_inside_min = max(float(self.config.exact_average_inside_seconds), 0.0) / 60.0
        if avg_min <= 0:
            return h_min
        if exact_inside_min > 0 and h_min <= min(exact_inside_min, avg_min):
            return max((h_min * h_min * h_min) / (3.0 * avg_min * avg_min), 0.002)
        if h_min >= avg_min:
            return max(h_min - (2.0 / 3.0) * avg_min, 0.02)
        return max((h_min * h_min) / max(avg_min, 1e-6), 0.02)

    def effective_horizon_minutes(self, horizon_seconds: float) -> float:
        cfg = self.config
        short_h = self._effective_horizon_for_average(horizon_seconds, cfg.short_settlement_average_seconds)
        long_h = self._effective_horizon_for_average(horizon_seconds, cfg.long_settlement_average_seconds)
        start = max(float(cfg.proxy_blend_start_seconds), 0.0)
        end = max(float(cfg.proxy_blend_end_seconds), start + 1e-6)
        horizon = max(float(horizon_seconds), 0.0)
        if horizon <= start:
            return short_h
        if horizon >= end:
            return long_h
        u = (horizon - start) / (end - start)
        weight = u * u * (3.0 - 2.0 * u)
        return (1.0 - weight) * short_h + weight * long_h


FastMushroomConfig = FastMushroomV36Config
FastMushroomFVEngine = FastMushroomFVEngineV36
