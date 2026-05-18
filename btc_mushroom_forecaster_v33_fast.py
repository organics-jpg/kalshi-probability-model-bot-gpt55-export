"""BTC Mushroom Forecaster v0.33 research candidate.

v33 is a probability-surface experiment, not a live-bot patch.

The v32 surface improved the settlement-average clock, but residual scans still
showed a small short-memory path effect. Naively projecting recent velocity as
momentum was not stable. The more defensible physical prior is weaker and
opposite: very short BTC moves tend to partially mean-revert before a 15-minute
boundary settles.

This candidate keeps v32 intact, then blends a small 3-minute anti-persistence
Brownian anchor into the posterior. The drift term is strongly damped by
remaining time so it cannot dominate near expiry or become a broad trend model.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

import numpy as np

from btc_mushroom_forecaster_v25_fast import FastPredictionBatch, _logit_np, _normal_cdf_np, _sigmoid_np
from btc_mushroom_forecaster_v32_fast import FastMushroomFVEngineV32, FastMushroomV32Config


@dataclass
class FastMushroomV33Config(FastMushroomV32Config):
    # Conservative physical correction: fade 3-minute velocity, do not chase it.
    anti_persistence_lag_minutes: int = 3
    anti_persistence_velocity_weight: float = -0.50
    anti_persistence_time_damp_power: float = 2.0
    anti_persistence_sigma_mult: float = 1.00
    anti_persistence_logit_weight: float = 0.05
    posterior_temperature: float = 0.98


class FastMushroomFVEngineV33(FastMushroomFVEngineV32):
    """v0.33 FV engine with a small short-memory anti-persistence posterior."""

    def __init__(self, config: FastMushroomV33Config | None = None) -> None:
        super().__init__(config or FastMushroomV33Config())

    def predict_many(self, *, strikes: Iterable[float] | np.ndarray, horizon_seconds: float) -> FastPredictionBatch:
        base = super().predict_many(strikes=strikes, horizon_seconds=horizon_seconds)
        cfg = self.config
        lag_minutes = max(1, int(getattr(cfg, "anti_persistence_lag_minutes", 3)))
        lag_close = self.get_close_lag(lag_minutes)
        spot = float(base.spot)
        if not (isfinite(lag_close) and lag_close > 0.0 and spot > 0.0):
            return base

        horizon = max(float(horizon_seconds), 0.0)
        velocity_dps = (spot - float(lag_close)) / float(lag_minutes * 60)
        time_damp = float(np.clip(horizon / 900.0, 0.0, 1.0)) ** max(
            float(getattr(cfg, "anti_persistence_time_damp_power", 2.0)),
            0.0,
        )
        drift_shift = (
            float(getattr(cfg, "anti_persistence_velocity_weight", -0.50))
            * velocity_dps
            * horizon
            * time_damp
        )
        sigma = max(
            float(base.sigma_t_dollars) * max(float(getattr(cfg, "anti_persistence_sigma_mult", 1.0)), 1e-6),
            1e-9,
        )
        drift_anchor = _normal_cdf_np((spot - base.strikes + drift_shift) / sigma)
        drift_anchor = np.clip(np.asarray(drift_anchor, dtype=float), 1e-8, 1.0 - 1e-8)

        weight = float(np.clip(getattr(cfg, "anti_persistence_logit_weight", 0.05), 0.0, 1.0))
        temperature = max(float(getattr(cfg, "posterior_temperature", 0.98)), 1e-6)
        ell = (1.0 - weight) * _logit_np(base.p_yes) + weight * _logit_np(drift_anchor)
        p_yes = _sigmoid_np(ell / temperature)
        p_yes = np.clip(np.asarray(p_yes, dtype=float), 1e-8, 1.0 - 1e-8)
        p_no = 1.0 - p_yes

        components = {
            **base.components,
            "p_anti_persistence_anchor": drift_anchor,
            "anti_persistence_velocity_dps": float(velocity_dps),
            "anti_persistence_shift_dollars": float(drift_shift),
            "anti_persistence_time_damp": float(time_damp),
            "anti_persistence_lag_minutes": float(lag_minutes),
            "anti_persistence_logit_weight": float(weight),
            "posterior_temperature": float(temperature),
        }
        return FastPredictionBatch(
            strikes=base.strikes,
            horizon_seconds=base.horizon_seconds,
            horizon_minutes=base.horizon_minutes,
            spot=base.spot,
            p_yes=p_yes,
            p_no=p_no,
            fair_yes_cents=100.0 * p_yes,
            fair_no_cents=100.0 * p_no,
            sigma_t_dollars=base.sigma_t_dollars,
            d_sigma=base.d_sigma,
            side_probability=np.maximum(p_yes, p_no),
            components=components,
        )


FastMushroomConfig = FastMushroomV33Config
FastMushroomFVEngine = FastMushroomFVEngineV33
