"""BTC Mushroom Forecaster v0.38 research candidate.

v38 is a probability-surface experiment, not a live-bot patch.

v37 fixed a useful short/long tension in the proxy clock and posterior
temperature. The next residual audit showed a smaller but repeatable effect:
large one-hour displacements still leave the surface slightly too confident in
the current location. v38 keeps v37 intact and adds a conservative long-memory
anti-persistence anchor:

- short memory: same materiality-gated 3-minute anti-persistence from v37;
- long memory: 60-minute anti-persistence, only when projected displacement is
  material;
- max long-memory logit weight: 0.10, but the average realized weight in replay
  is below 0.4%, so this is a nudge rather than a new classifier.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

import numpy as np

from btc_mushroom_forecaster_v25_fast import FastPredictionBatch, _logit_np, _normal_cdf_np, _sigmoid_np
from btc_mushroom_forecaster_v37_fast import FastMushroomFVEngineV37, FastMushroomV37Config


@dataclass
class FastMushroomV38Config(FastMushroomV37Config):
    long_anti_persistence_lag_minutes: int = 60
    long_anti_persistence_velocity_weight: float = -0.50
    long_anti_persistence_time_damp_power: float = 1.0
    long_anti_persistence_sigma_mult: float = 1.00
    long_anti_persistence_max_logit_weight: float = 0.10
    long_anti_persistence_shift_gate_center_dollars: float = 80.0
    long_anti_persistence_shift_gate_width_dollars: float = 20.0


class FastMushroomFVEngineV38(FastMushroomFVEngineV37):
    """v0.38 FV engine with v37 plus a gated 60m anti-persistence prior."""

    def __init__(self, config: FastMushroomV38Config | None = None) -> None:
        super().__init__(config or FastMushroomV38Config())

    def predict_many(self, *, strikes: Iterable[float] | np.ndarray, horizon_seconds: float) -> FastPredictionBatch:
        base = super().predict_many(strikes=strikes, horizon_seconds=horizon_seconds)
        cfg = self.config
        lag_minutes = max(1, int(getattr(cfg, "long_anti_persistence_lag_minutes", 60)))
        lag_close = self.get_close_lag(lag_minutes)
        spot = float(base.spot)
        if not (isfinite(lag_close) and lag_close > 0.0 and spot > 0.0):
            return base

        horizon = max(float(horizon_seconds), 0.0)
        velocity_dps = (spot - float(lag_close)) / float(lag_minutes * 60)
        time_damp = float(np.clip(horizon / 900.0, 0.0, 1.0)) ** max(
            float(getattr(cfg, "long_anti_persistence_time_damp_power", 1.0)),
            0.0,
        )
        drift_shift = (
            float(getattr(cfg, "long_anti_persistence_velocity_weight", -0.50))
            * velocity_dps
            * horizon
            * time_damp
        )
        sigma = max(
            float(base.sigma_t_dollars)
            * max(float(getattr(cfg, "long_anti_persistence_sigma_mult", 1.0)), 1e-6),
            1e-9,
        )
        drift_anchor = _normal_cdf_np((spot - base.strikes + drift_shift) / sigma)
        drift_anchor = np.clip(np.asarray(drift_anchor, dtype=float), 1e-8, 1.0 - 1e-8)

        gate_center = float(getattr(cfg, "long_anti_persistence_shift_gate_center_dollars", 80.0))
        gate_width = max(float(getattr(cfg, "long_anti_persistence_shift_gate_width_dollars", 20.0)), 1e-6)
        materiality_gate = float(_sigmoid_np((abs(float(drift_shift)) - gate_center) / gate_width))
        max_weight = float(np.clip(getattr(cfg, "long_anti_persistence_max_logit_weight", 0.10), 0.0, 1.0))
        weight = max_weight * materiality_gate
        ell = (1.0 - weight) * _logit_np(base.p_yes) + weight * _logit_np(drift_anchor)
        p_yes = _sigmoid_np(ell)
        p_yes = np.clip(np.asarray(p_yes, dtype=float), 1e-8, 1.0 - 1e-8)
        p_no = 1.0 - p_yes

        components = {
            **base.components,
            "p_long_anti_persistence_anchor": drift_anchor,
            "long_anti_persistence_velocity_dps": float(velocity_dps),
            "long_anti_persistence_shift_dollars": float(drift_shift),
            "long_anti_persistence_time_damp": float(time_damp),
            "long_anti_persistence_materiality_gate": float(materiality_gate),
            "long_anti_persistence_logit_weight": float(weight),
            "long_anti_persistence_lag_minutes": float(lag_minutes),
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


FastMushroomConfig = FastMushroomV38Config
FastMushroomFVEngine = FastMushroomFVEngineV38
