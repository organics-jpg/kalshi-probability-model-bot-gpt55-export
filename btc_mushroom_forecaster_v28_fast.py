
"""
BTC Mushroom Forecaster v0.28 — Calibrated Fast Histogram Transport

v0.28 is a conservative refinement of v0.25 for live websocket fair-value use.

Changes vs v0.25
----------------
1. Retunes only four low-risk global constants using a chronological split test:
   - boundary_arrow_strength: 0.25 -> 0.125
   - transport_recent_weight: 0.30 -> 0.40
   - transport_long_weight:   0.30 -> 0.40
   - transport_temperature:   1.03 -> 0.95

   Interpretation: the weak signed time-mirror arrow was too strong relative to
   the useful boundary-shape transport. The CDF transport can be trusted slightly
   more; the directional arrow should be quieter.

2. Keeps the v0.25 fixed-grid histogram transport, which was faster and more
   robust than the v0.27 smooth cloud histogram in the Jan-2024 split test.

3. Removes unnecessary list(...) conversions inside predict_many / edge_many when
   numpy arrays are passed from the live worker.

This file intentionally depends on btc_mushroom_forecaster_v25_fast.py and keeps
its public API compatible.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable

import numpy as np

from btc_mushroom_forecaster_v25_fast import (
    FastMushroomV25Config,
    FastMushroomFVEngineV25,
    FastPredictionBatch,
    EdgeBatch,
    _clip_scalar,
    _normal_cdf_np,
    _logit_np,
    _sigmoid_np,
)


@dataclass
class FastMushroomV28Config(FastMushroomV25Config):
    # v28 split-test calibration
    boundary_arrow_strength: float = 0.125
    transport_recent_weight: float = 0.40
    transport_long_weight: float = 0.40
    transport_temperature: float = 0.95


class FastMushroomFVEngineV28(FastMushroomFVEngineV25):
    """v0.28 calibrated fast histogram engine.

    Same lifecycle as v25:
        update_tick(price, ts)
        update_bar(open, high, low, close, volume, ts)
        predict_many(strikes, horizon_seconds)
        edge_many(strikes, horizon_seconds, yes_ask_cents, no_ask_cents)
    """

    def __init__(self, config: FastMushroomV28Config | None = None) -> None:
        super().__init__(config or FastMushroomV28Config())

    @staticmethod
    def _as_1d_float_array(x: Iterable[float] | np.ndarray, *, name: str) -> np.ndarray:
        arr = np.asarray(x, dtype=float)
        if arr.ndim != 1:
            arr = arr.reshape(-1)
        if arr.size == 0:
            raise ValueError(f"{name} must not be empty")
        return arr

    def predict_many(self, *, strikes: Iterable[float] | np.ndarray, horizon_seconds: float) -> FastPredictionBatch:
        if not self.ready():
            raise ValueError(f"Need at least {self.config.min_bars} closed bars before prediction.")

        strikes_arr = self._as_1d_float_array(strikes, name="strikes")

        spot = self.current_spot()
        raw_horizon_minutes = max(1, int(round(float(horizon_seconds) / 60.0)))
        effective_h = self.effective_horizon_minutes(horizon_seconds)
        learned_h = self._nearest_learned_horizon(raw_horizon_minutes)

        var, var_close, volshock = self.current_variance_per_minute()
        sigma = spot * sqrt(max(var * effective_h, 1e-18))
        floor = self.config.vol_floor_dollars_15m * sqrt(effective_h / 15.0)
        ceil = self.config.vol_ceiling_dollars_15m * sqrt(effective_h / 15.0)
        sigma = float(_clip_scalar(sigma, floor, ceil))

        d = (strikes_arr - spot) / max(sigma, 1e-12)
        p_anchor = _normal_cdf_np(-d)
        ell_anchor = _logit_np(p_anchor)

        arrow = self._arrow(raw_horizon_minutes, var_close, spot)
        static_gate = np.exp(-((np.abs(d) / self.config.boundary_arrow_gate_sigma) ** 2))
        ell_static = ell_anchor + self.config.boundary_arrow_strength * static_gate * arrow
        p_static = _sigmoid_np(ell_static)

        tb = self.transport.get(learned_h)
        if tb is not None:
            p_recent, p_long, n_recent, n_long = tb.tail_prob(d, self.config.transport_min_recent, self.config.transport_min_long)
        else:
            p_recent, p_long, n_recent, n_long = None, None, 0, 0
        if p_recent is None:
            p_recent = p_anchor
        if p_long is None:
            p_long = p_anchor

        edge_gate = 1.0 / (1.0 + np.exp(-self.config.transport_edge_gate_steepness * (np.abs(d) - self.config.transport_edge_gate_center)))
        ell_transport = (
            _logit_np(p_static)
            + edge_gate * self.config.transport_recent_weight * (_logit_np(p_recent) - ell_anchor)
            + edge_gate * self.config.transport_long_weight * (_logit_np(p_long) - ell_anchor)
        )
        p_yes = _sigmoid_np(ell_transport / max(self.config.transport_temperature, 1e-6))
        p_yes = np.clip(p_yes, 1e-8, 1.0 - 1e-8)
        p_no = 1.0 - p_yes
        side_probability = np.maximum(p_yes, p_no)

        components = {
            "p_anchor": p_anchor,
            "p_static_boundary_field": p_static,
            "p_recent_transport": p_recent,
            "p_long_transport": p_long,
            "edge_gate": edge_gate,
            "arrow": float(arrow),
            "static_gate": static_gate,
            "volshock": float(volshock),
            "transport_recent_n": float(n_recent),
            "transport_long_n": float(n_long),
            "learned_horizon_minutes": float(learned_h),
            "effective_horizon_minutes": float(effective_h),
        }
        return FastPredictionBatch(
            strikes=strikes_arr,
            horizon_seconds=float(horizon_seconds),
            horizon_minutes=raw_horizon_minutes,
            spot=float(spot),
            p_yes=p_yes,
            p_no=p_no,
            fair_yes_cents=100.0 * p_yes,
            fair_no_cents=100.0 * p_no,
            sigma_t_dollars=float(sigma),
            d_sigma=d,
            side_probability=side_probability,
            components=components,
        )

    def edge_many(
        self,
        *,
        strikes: Iterable[float] | np.ndarray,
        horizon_seconds: float,
        yes_ask_cents: Iterable[float] | np.ndarray,
        no_ask_cents: Iterable[float] | np.ndarray,
        fee_cents: float | None = None,
        slippage_cents: float | None = None,
        model_buffer_cents: float | None = None,
        min_net_edge_cents: float = 2.0,
    ) -> EdgeBatch:
        batch = self.predict_many(strikes=strikes, horizon_seconds=horizon_seconds)
        yes_ask = self._as_1d_float_array(yes_ask_cents, name="yes_ask_cents")
        no_ask = self._as_1d_float_array(no_ask_cents, name="no_ask_cents")
        if yes_ask.shape != batch.strikes.shape or no_ask.shape != batch.strikes.shape:
            raise ValueError("ask arrays must have same length as strikes")

        fee = float(self.config.default_fee_cents if fee_cents is None else fee_cents)
        slip = float(self.config.default_slippage_cents if slippage_cents is None else slippage_cents)
        buff = float(self.config.default_model_buffer_cents if model_buffer_cents is None else model_buffer_cents)
        cost = fee + slip + buff

        yes_edge = batch.fair_yes_cents - yes_ask - cost
        no_edge = batch.fair_no_cents - no_ask - cost
        yes_better = yes_edge >= no_edge
        best_side = np.where(yes_better, "yes", "no")
        best_edge = np.where(yes_better, yes_edge, no_edge)
        best_fair = np.where(yes_better, batch.fair_yes_cents, batch.fair_no_cents)
        tradeable = best_edge >= float(min_net_edge_cents)

        return EdgeBatch(
            strikes=batch.strikes,
            p_yes=batch.p_yes,
            fair_yes_cents=batch.fair_yes_cents,
            fair_no_cents=batch.fair_no_cents,
            yes_net_edge_cents=yes_edge,
            no_net_edge_cents=no_edge,
            best_side=best_side,
            best_edge_cents=best_edge,
            best_fair_cents=best_fair,
            side_probability=batch.side_probability,
            tradeable=tradeable,
            components={**batch.components, "sigma_t_dollars": batch.sigma_t_dollars, "d_sigma": batch.d_sigma},
        )


# Default aliases.
FastMushroomConfig = FastMushroomV28Config
FastMushroomFVEngine = FastMushroomFVEngineV28
