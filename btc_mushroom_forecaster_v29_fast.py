"""BTC Mushroom Forecaster v0.29 research candidate.

v29 is a probability-surface experiment, not a live-bot patch.

The v28 engine is strong and fast, but two physics assumptions are worth
questioning directly:

1. Histogram transport is symmetric: each realized standardized return Z is
   stored as both Z and -Z. That is stable for tail width, but it discards
   signed regime skew.
2. Kalshi BTC 15m settlement is a final averaging process, while the default
   live engine still uses close-to-close horizon variance unless configured
   otherwise.

This candidate keeps v28's Brownian anchor and symmetric transport, then adds a
small gated signed-residual transport term and turns on effective final-average
horizon adjustment. High-volatility shock also softens probability temperature
instead of letting an unstable tail state become overconfident.

No network, auth, order, or bot-control code lives here.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Iterable

import numpy as np

from btc_mushroom_forecaster_v25_fast import (
    EdgeBatch,
    FastPredictionBatch,
    _clip_scalar,
    _logit_np,
    _normal_cdf_np,
    _sigmoid_np,
)
from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config


class SignedHistogramTransportBuffer:
    """Fixed-grid raw signed residual transport.

    Unlike the v25/v28 symmetric buffer, this stores Z only. It answers
    P(Z > d), with a standard-normal prior for shrinkage when the sample is
    sparse. This intentionally has small weights in v29 because signed drift is
    regime-fragile.
    """

    def __init__(
        self,
        recent_window: int,
        long_window: int,
        *,
        bins: int = 1001,
        zmax: float = 8.0,
        recent_prior_count: float = 96.0,
        long_prior_count: float = 384.0,
    ) -> None:
        self.recent_window = int(recent_window)
        self.long_window = int(long_window)
        self.bins = int(max(101, bins))
        if self.bins % 2 == 0:
            self.bins += 1
        self.zmax = float(max(2.0, zmax))
        self.recent_prior_count = float(max(0.0, recent_prior_count))
        self.long_prior_count = float(max(0.0, long_prior_count))

        self.edges = np.linspace(-self.zmax, self.zmax, self.bins + 1, dtype=float)
        self.mids = 0.5 * (self.edges[:-1] + self.edges[1:])
        prior_cdf_hi = _normal_cdf_np(self.edges[1:])
        prior_cdf_lo = _normal_cdf_np(self.edges[:-1])
        pm = np.asarray(prior_cdf_hi - prior_cdf_lo, dtype=float)
        pm = np.maximum(pm, 0.0)
        total = float(pm.sum())
        self.prior_mass = pm / total if total > 0 else np.full(self.bins, 1.0 / self.bins)
        self.prior_cum = np.cumsum(self.prior_mass)

        self.recent_queue = deque()
        self.long_queue = deque()
        self.recent_hist = np.zeros(self.bins, dtype=float)
        self.long_hist = np.zeros(self.bins, dtype=float)
        self.recent_n = 0
        self.long_n = 0
        self._version = 0
        self._cache_version = -1
        self._recent_cum: np.ndarray | None = None
        self._long_cum: np.ndarray | None = None

    def _bin_index(self, z: float) -> int:
        zc = float(_clip_scalar(z, -self.zmax + 1e-12, self.zmax - 1e-12))
        idx = int((zc + self.zmax) / (2.0 * self.zmax) * self.bins)
        return int(max(0, min(self.bins - 1, idx)))

    def append(self, z: float) -> None:
        if not isfinite(z):
            return
        idx = self._bin_index(float(_clip_scalar(z, -12.0, 12.0)))

        self.recent_queue.append(idx)
        self.recent_hist[idx] += 1.0
        self.recent_n += 1
        if self.recent_n > self.recent_window:
            old = self.recent_queue.popleft()
            self.recent_hist[old] -= 1.0
            self.recent_n -= 1

        self.long_queue.append(idx)
        self.long_hist[idx] += 1.0
        self.long_n += 1
        if self.long_n > self.long_window:
            old = self.long_queue.popleft()
            self.long_hist[old] -= 1.0
            self.long_n -= 1

        self._version += 1

    def _refresh(self) -> None:
        if self._cache_version == self._version:
            return
        self._recent_cum = np.cumsum(np.maximum(self.recent_hist, 0.0))
        self._long_cum = np.cumsum(np.maximum(self.long_hist, 0.0))
        self._cache_version = self._version

    def _tail_from_hist(
        self,
        d: np.ndarray,
        hist: np.ndarray,
        cum: np.ndarray,
        n: int,
        min_n: int,
        prior_count: float,
    ) -> np.ndarray | None:
        if int(n) < int(min_n):
            return None
        d = np.asarray(d, dtype=float)
        idx = np.searchsorted(self.mids, d, side="right")
        idx_clip = np.clip(idx, 0, self.bins)
        emp_le = np.zeros_like(d, dtype=float)
        mask_mid = idx_clip > 0
        emp_le[mask_mid] = cum[idx_clip[mask_mid] - 1]
        emp_tail = np.clip((float(n) - emp_le) / max(float(n), 1.0), 0.0, 1.0)
        if prior_count <= 0:
            return emp_tail

        prior_le = np.zeros_like(d, dtype=float)
        prior_le[mask_mid] = self.prior_cum[idx_clip[mask_mid] - 1]
        prior_tail = np.clip(1.0 - prior_le, 0.0, 1.0)
        alpha = float(prior_count)
        return np.clip((float(n) * emp_tail + alpha * prior_tail) / (float(n) + alpha), 1e-8, 1.0 - 1e-8)

    def tail_prob(self, d: np.ndarray, min_recent: int, min_long: int) -> tuple[np.ndarray | None, np.ndarray | None, int, int]:
        self._refresh()
        d = np.asarray(d, dtype=float)
        recent = self._tail_from_hist(
            d,
            self.recent_hist,
            self._recent_cum if self._recent_cum is not None else np.zeros(self.bins),
            self.recent_n,
            min_recent,
            self.recent_prior_count,
        )
        long = self._tail_from_hist(
            d,
            self.long_hist,
            self._long_cum if self._long_cum is not None else np.zeros(self.bins),
            self.long_n,
            min_long,
            self.long_prior_count,
        )
        return recent, long, int(self.recent_n), int(self.long_n)


@dataclass
class FastMushroomV29Config(FastMushroomV28Config):
    settlement_average_seconds: float = 90.0
    transport_temperature: float = 1.04
    signed_transport_recent_weight: float = 0.10
    signed_transport_long_weight: float = 0.04
    signed_transport_gate_center: float = 0.35
    signed_transport_gate_steepness: float = 4.0
    signed_transport_min_recent: int = 240
    signed_transport_min_long: int = 1440
    signed_transport_recent_prior_count: float = 96.0
    signed_transport_long_prior_count: float = 384.0
    volshock_temperature_strength: float = 0.05


class FastMushroomFVEngineV29(FastMushroomFVEngineV28):
    """v0.29 research fair-value engine."""

    def __init__(self, config: FastMushroomV29Config | None = None) -> None:
        cfg = config or FastMushroomV29Config()
        super().__init__(cfg)
        self.config = cfg
        self.signed_transport = {
            h: SignedHistogramTransportBuffer(
                self.config.recent_transport_window,
                self.config.long_transport_window,
                bins=self.config.transport_hist_bins,
                zmax=self.config.transport_hist_zmax,
                recent_prior_count=self.config.signed_transport_recent_prior_count,
                long_prior_count=self.config.signed_transport_long_prior_count,
            )
            for h in self.horizons
        }

    def _harvest_resolved_returns(self, current_abs: int, current_close: float) -> None:
        super()._harvest_resolved_returns(current_abs=current_abs, current_close=current_close)
        if self.count < self.config.min_bars:
            return
        for h in self.horizons:
            start_abs = current_abs - h
            slot = self._slot_for_abs(start_abs)
            if slot is None:
                continue
            start_close = float(self.close[slot])
            sigma_start = float(self.sigma_snapshot[slot, self.hidx[h]])
            if start_close > 0 and sigma_start > 0 and isfinite(sigma_start):
                z = (float(current_close) - start_close) / sigma_start
                self.signed_transport[h].append(z)

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

        signed_tb = self.signed_transport.get(learned_h)
        if signed_tb is not None:
            p_signed_recent, p_signed_long, signed_n_recent, signed_n_long = signed_tb.tail_prob(
                d,
                self.config.signed_transport_min_recent,
                self.config.signed_transport_min_long,
            )
        else:
            p_signed_recent, p_signed_long, signed_n_recent, signed_n_long = None, None, 0, 0
        if p_signed_recent is None:
            p_signed_recent = p_anchor
        if p_signed_long is None:
            p_signed_long = p_anchor

        signed_pressure_gate = 1.0 / (
            1.0
            + np.exp(
                -self.config.signed_transport_gate_steepness
                * (abs(float(arrow)) - self.config.signed_transport_gate_center)
            )
        )
        signed_gate = static_gate * edge_gate * float(signed_pressure_gate)
        ell_transport = (
            ell_transport
            + signed_gate
            * self.config.signed_transport_recent_weight
            * (_logit_np(p_signed_recent) - ell_anchor)
            + signed_gate
            * self.config.signed_transport_long_weight
            * (_logit_np(p_signed_long) - ell_anchor)
        )

        effective_temperature = max(
            1e-6,
            float(self.config.transport_temperature)
            * float(np.exp(max(0.0, float(volshock)) * self.config.volshock_temperature_strength)),
        )
        p_yes = _sigmoid_np(ell_transport / effective_temperature)
        p_yes = np.clip(p_yes, 1e-8, 1.0 - 1e-8)
        p_no = 1.0 - p_yes
        side_probability = np.maximum(p_yes, p_no)

        components = {
            "p_anchor": p_anchor,
            "p_static_boundary_field": p_static,
            "p_recent_transport": p_recent,
            "p_long_transport": p_long,
            "p_signed_recent_transport": p_signed_recent,
            "p_signed_long_transport": p_signed_long,
            "edge_gate": edge_gate,
            "signed_gate": signed_gate,
            "signed_pressure_gate": float(signed_pressure_gate),
            "arrow": float(arrow),
            "static_gate": static_gate,
            "volshock": float(volshock),
            "effective_temperature": float(effective_temperature),
            "transport_recent_n": float(n_recent),
            "transport_long_n": float(n_long),
            "signed_transport_recent_n": float(signed_n_recent),
            "signed_transport_long_n": float(signed_n_long),
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


FastMushroomConfig = FastMushroomV29Config
FastMushroomFVEngine = FastMushroomFVEngineV29
