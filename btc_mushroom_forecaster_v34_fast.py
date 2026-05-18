"""BTC Mushroom Forecaster v0.34 research candidate.

v34 is a probability-surface experiment, not a live-bot patch.

v33 showed that a small 3-minute anti-persistence prior improves the pure FV
surface, but the stability audit showed weak spots when the projected reversion
shift was small or noisy. v34 keeps the same physical idea and adds one
materiality condition: only large projected reversion shifts should move the
posterior.

This is deliberately smoother and less fitted than a distance-to-strike bucket
patch. It asks the model to ignore micro-noise and respond only when recent
motion is large enough to be physically meaningful at the remaining horizon.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

import numpy as np

from btc_mushroom_forecaster_v25_fast import FastPredictionBatch, _logit_np, _normal_cdf_np, _sigmoid_np
from btc_mushroom_forecaster_v32_fast import FastMushroomFVEngineV32, FastMushroomV32Config


@dataclass
class FastMushroomV34Config(FastMushroomV32Config):
    anti_persistence_lag_minutes: int = 3
    anti_persistence_velocity_weight: float = -0.50
    anti_persistence_time_damp_power: float = 2.0
    anti_persistence_sigma_mult: float = 1.00
    anti_persistence_max_logit_weight: float = 0.10
    anti_persistence_shift_gate_center_dollars: float = 40.0
    anti_persistence_shift_gate_width_dollars: float = 5.0
    posterior_temperature: float = 0.98


class FastMushroomFVEngineV34(FastMushroomFVEngineV32):
    """v0.34 FV engine with materiality-gated short-memory anti-persistence."""

    def __init__(self, config: FastMushroomV34Config | None = None) -> None:
        super().__init__(config or FastMushroomV34Config())

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

        gate_center = float(getattr(cfg, "anti_persistence_shift_gate_center_dollars", 40.0))
        gate_width = max(float(getattr(cfg, "anti_persistence_shift_gate_width_dollars", 5.0)), 1e-6)
        materiality_gate = float(_sigmoid_np((abs(float(drift_shift)) - gate_center) / gate_width))
        max_weight = float(np.clip(getattr(cfg, "anti_persistence_max_logit_weight", 0.10), 0.0, 1.0))
        weight = max_weight * materiality_gate
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


FastMushroomConfig = FastMushroomV34Config
FastMushroomFVEngine = FastMushroomFVEngineV34
