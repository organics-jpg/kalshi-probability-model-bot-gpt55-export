"""BTC Mushroom Forecaster v0.37 research candidate.

v37 is a probability-surface experiment, not a live-bot patch.

v36's piecewise proxy horizon reduced v35's regime damage, but residual scans
showed a remaining tension: a 0.98 posterior temperature is better near expiry,
while 1.02 is better in the longer-proxy region. v37 applies the same smooth
120s-to-300s blend to posterior temperature:

- near expiry: v34-like 0.98 confidence;
- earlier in the market: v36/v35-like 1.02 softness;
- proxy horizon: same v36 110s-to-150s smooth blend;
- anti-persistence: same materiality-gated 3-minute prior.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

import numpy as np

from btc_mushroom_forecaster_v25_fast import FastPredictionBatch, _logit_np, _normal_cdf_np, _sigmoid_np
from btc_mushroom_forecaster_v34_fast import FastMushroomFVEngineV34
from btc_mushroom_forecaster_v36_fast import FastMushroomFVEngineV36, FastMushroomV36Config


@dataclass
class FastMushroomV37Config(FastMushroomV36Config):
    short_posterior_temperature: float = 0.98
    long_posterior_temperature: float = 1.02
    temperature_blend_start_seconds: float = 120.0
    temperature_blend_end_seconds: float = 300.0


class FastMushroomFVEngineV37(FastMushroomFVEngineV36):
    """v0.37 FV engine with dynamic proxy horizon and dynamic temperature."""

    def __init__(self, config: FastMushroomV37Config | None = None) -> None:
        super().__init__(config or FastMushroomV37Config())

    @staticmethod
    def _smooth_blend_weight(horizon_seconds: float, start_seconds: float, end_seconds: float) -> float:
        start = max(float(start_seconds), 0.0)
        end = max(float(end_seconds), start + 1e-6)
        horizon = max(float(horizon_seconds), 0.0)
        if horizon <= start:
            return 0.0
        if horizon >= end:
            return 1.0
        u = (horizon - start) / (end - start)
        return float(u * u * (3.0 - 2.0 * u))

    def posterior_temperature_for_horizon(self, horizon_seconds: float) -> float:
        cfg = self.config
        weight = self._smooth_blend_weight(
            horizon_seconds,
            cfg.temperature_blend_start_seconds,
            cfg.temperature_blend_end_seconds,
        )
        short_t = max(float(cfg.short_posterior_temperature), 1e-6)
        long_t = max(float(cfg.long_posterior_temperature), 1e-6)
        return (1.0 - weight) * short_t + weight * long_t

    def predict_many(self, *, strikes: Iterable[float] | np.ndarray, horizon_seconds: float) -> FastPredictionBatch:
        base = super(FastMushroomFVEngineV34, self).predict_many(
            strikes=strikes,
            horizon_seconds=horizon_seconds,
        )
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

        gate_center = float(getattr(cfg, "anti_persistence_shift_gate_center_dollars", 40.0))
        gate_width = max(float(getattr(cfg, "anti_persistence_shift_gate_width_dollars", 5.0)), 1e-6)
        materiality_gate = float(_sigmoid_np((abs(float(drift_shift)) - gate_center) / gate_width))
        max_weight = float(np.clip(getattr(cfg, "anti_persistence_max_logit_weight", 0.10), 0.0, 1.0))
        weight = max_weight * materiality_gate
        temperature = self.posterior_temperature_for_horizon(horizon_seconds)
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
            "anti_persistence_materiality_gate": float(materiality_gate),
            "anti_persistence_logit_weight": float(weight),
            "anti_persistence_lag_minutes": float(lag_minutes),
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


FastMushroomConfig = FastMushroomV37Config
FastMushroomFVEngine = FastMushroomFVEngineV37
