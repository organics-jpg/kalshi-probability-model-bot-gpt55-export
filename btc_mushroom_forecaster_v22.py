"""
BTC Mushroom Forecaster v0.22 — Edge-Zone Transport Field

Purpose
-------
A live-capable physical BTC boundary forecaster focused on the useful Kalshi edge
zone: non-ATM boundaries where spot has meaningful cushion versus the strike.

v0.22 keeps v0.21's range-aware martingale anchor and weak time-mirror boundary
field, then adds a prequential symmetrized-return transport correction. The new
correction is designed to improve probability quality in |d| >= 0.75 and |d| >= 1
zones without forcing fragile directional flips.

Core probability
----------------
Let:

    d = (K - S_t) / sigma_t(h)
    p_anchor = Phi(-d)

v0.21 static field:

    ell_static = logit(p_anchor)
                 + 0.25 * exp(-(abs(d)/1.0)^2) * A_t

where A_t is a weak time-mirror curvature arrow.

v0.22 transport field learns the shape of recently resolved standardized future
returns:

    Z_j(h) = (S_{j+h} - S_j) / sigma_j(h)
    D_h = {Z_j, -Z_j}

    p_recent = P_{Z in recent D_h}(Z > d)
    p_long   = P_{Z in long   D_h}(Z > d)

Final logit:

    ell_22 = ell_static
             + G_edge(|d|) * [wr(logit(p_recent)-logit(p_anchor))
                              + wl(logit(p_long)-logit(p_anchor))]

Default parameters were selected on pre-2026 Bitstamp data and evaluated on
2026/April/last-7-day holdout panels:

    wr = 0.30
    wl = 0.30
    temperature = 1.03

This model is non-abstaining. Every boundary gets a probability. For trading, use
`edge_score`/`side_probability` as sizing and gating diagnostics, not as the
probability itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import erfc, exp, isfinite, log, sqrt
from typing import Literal

import numpy as np

Side = Literal["yes", "no"]


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


def _normal_cdf(z: float) -> float:
    return 0.5 * erfc(-float(z) / sqrt(2.0))


def _logit(p: float) -> float:
    p = _clip(float(p), 1e-10, 1.0 - 1e-10)
    return log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    x = float(x)
    if x >= 0:
        z = exp(-x)
        return 1.0 / (1.0 + z)
    z = exp(x)
    return z / (1.0 + z)


@dataclass
class MushroomConfig:
    max_history: int = 24000
    min_history_points: int = 180

    vol_window_points: int = 600
    range_short_window: int = 60
    range_long_window: int = 360
    range_variance_weight: float = 0.50

    vol_floor_dollars_15m: float = 65.0
    vol_ceiling_dollars_15m: float = 1500.0

    boundary_arrow_strength: float = 0.25
    boundary_arrow_gate_sigma: float = 1.00
    arrow_signal_scale: float = 0.85

    # v0.22 transport parameters.
    transport_recent_weight: float = 0.30
    transport_long_weight: float = 0.30
    transport_temperature: float = 1.03
    transport_edge_gate_center: float = 0.55
    transport_edge_gate_steepness: float = 6.0
    recent_transport_window: int = 1440
    long_transport_window: int = 10080
    transport_min_recent: int = 240
    transport_min_long: int = 1440

    # Horizons for which standardized realized returns are learned online.
    learned_horizons_minutes: tuple[int, ...] = (5, 10, 15, 30, 60)


@dataclass
class Bar:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass
class PhysicalPrediction:
    side: Side
    p_terminal: float
    p_yes: float
    p_side: float
    fair_cents: float
    confidence: float
    uncertainty: float
    boundary_risk: float
    sigma_t_dollars: float
    drift_t_dollars: float
    seconds_to_close: float
    components: dict[str, float] = field(default_factory=dict)


class MushroomForecaster:
    """Stateful v0.22 edge-zone physical forecaster.

    Feed 1-minute bars with `update_bar`. The object automatically harvests
    resolved standardized returns for configured horizons as new bars arrive.
    """

    def __init__(self, config: MushroomConfig | None = None) -> None:
        self.config = config or MushroomConfig()
        self.history: list[Bar] = []
        self._transport_returns: dict[int, list[float]] = {h: [] for h in self.config.learned_horizons_minutes}
        self._harvested_until: dict[int, int] = {h: -1 for h in self.config.learned_horizons_minutes}

    def reset_history(self) -> None:
        self.history.clear()
        self._transport_returns = {h: [] for h in self.config.learned_horizons_minutes}
        self._harvested_until = {h: -1 for h in self.config.learned_horizons_minutes}

    def update_spot(self, price: float, ts: datetime | None = None) -> None:
        self.update_bar(open=price, high=price, low=price, close=price, volume=0.0, ts=ts)

    def update_bar(
        self,
        *,
        close: float,
        ts: datetime | None = None,
        open: float | None = None,
        high: float | None = None,
        low: float | None = None,
        volume: float = 0.0,
    ) -> None:
        close = float(close)
        if not isfinite(close) or close <= 0:
            return
        op = float(open if open is not None else close)
        hi = float(high if high is not None else max(op, close))
        lo = float(low if low is not None else min(op, close))
        if not (isfinite(op) and isfinite(hi) and isfinite(lo)) or hi <= 0 or lo <= 0:
            return
        hi = max(hi, op, close)
        lo = min(lo, op, close)
        self.history.append(Bar(ts=ts or datetime.now(timezone.utc), open=op, high=hi, low=lo, close=close, volume=float(volume or 0.0)))
        if len(self.history) > self.config.max_history:
            drop = len(self.history) - self.config.max_history
            self.history = self.history[-self.config.max_history:]
            # Harvest indices shift after truncation. Reset conservatively; buffers keep learned returns.
            self._harvested_until = {h: max(-1, v - drop) for h, v in self._harvested_until.items()}
        self._harvest_completed_returns()

    def _arrays(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        opens = np.array([b.open for b in self.history], dtype=float)
        highs = np.array([b.high for b in self.history], dtype=float)
        lows = np.array([b.low for b in self.history], dtype=float)
        closes = np.array([b.close for b in self.history], dtype=float)
        vols = np.array([b.volume for b in self.history], dtype=float)
        return opens, highs, lows, closes, vols

    def _variance_per_minute_at(self, end_idx: int | None = None) -> tuple[float, float, float]:
        cfg = self.config
        opens, highs, lows, closes, _ = self._arrays()
        if end_idx is not None:
            end = int(end_idx) + 1
            highs = highs[:end]
            lows = lows[:end]
            closes = closes[:end]
        if len(closes) < 3:
            return 1e-8, 1e-8, 0.0
        logp = np.log(np.maximum(closes, 1e-12))
        rets = np.diff(logp)
        w = min(cfg.vol_window_points, len(rets))
        x = rets[-w:]
        rv = float(np.var(x, ddof=1)) if len(x) > 2 else 1e-8
        rr = np.log(np.maximum(highs, 1e-12) / np.maximum(lows, 1e-12))
        pv = (rr * rr) / (4.0 * log(2.0))
        ws = min(cfg.range_short_window, len(pv))
        wl = min(cfg.range_long_window, len(pv))
        range_short = float(np.mean(pv[-ws:])) if ws > 0 else rv
        range_long = float(np.mean(pv[-wl:])) if wl > 0 else rv
        range_var = 0.5 * range_short + 0.5 * range_long
        blend = (1.0 - cfg.range_variance_weight) * rv + cfg.range_variance_weight * range_var
        volshock = log(max(range_var, 1e-18) / max(rv, 1e-18))
        return max(blend, 1e-18), max(rv, 1e-18), float(_clip(volshock, -3.0, 3.0))

    def _variance_per_minute(self) -> tuple[float, float, float]:
        return self._variance_per_minute_at(None)

    def _sigma_at(self, start_idx: int, horizon_minutes: int) -> float:
        _, _, _, closes, _ = self._arrays()
        spot = float(closes[start_idx])
        var, _, _ = self._variance_per_minute_at(start_idx)
        sigma = spot * sqrt(max(var * horizon_minutes, 1e-18))
        sigma = _clip(
            sigma,
            self.config.vol_floor_dollars_15m * sqrt(horizon_minutes / 15.0),
            self.config.vol_ceiling_dollars_15m * sqrt(horizon_minutes / 15.0),
        )
        return sigma

    def _harvest_completed_returns(self) -> None:
        n = len(self.history)
        if n < self.config.min_history_points:
            return
        _, _, _, closes, _ = self._arrays()
        for h in self.config.learned_horizons_minutes:
            latest_start = n - h - 1
            last = self._harvested_until.get(h, -1)
            if latest_start <= last:
                continue
            # Harvest all missing starts, but avoid excessive looping after long resets.
            for start in range(max(last + 1, self.config.min_history_points), latest_start + 1):
                sigma = self._sigma_at(start, h)
                if sigma <= 0:
                    continue
                z = (float(closes[start + h]) - float(closes[start])) / sigma
                if isfinite(z):
                    buf = self._transport_returns.setdefault(h, [])
                    buf.append(float(_clip(z, -12.0, 12.0)))
                    max_keep = max(self.config.long_transport_window * 2, self.config.recent_transport_window * 3)
                    if len(buf) > max_keep:
                        del buf[: len(buf) - max_keep]
            self._harvested_until[h] = latest_start

    def _zret(self, k: int, var_close: float) -> float:
        _, _, _, closes, _ = self._arrays()
        if len(closes) <= k or k <= 0:
            return 0.0
        r = log(closes[-1] / closes[-1-k])
        return float(_clip(r / sqrt(max(var_close * k, 1e-18)), -4.0, 4.0))

    def _arrow(self, horizon_minutes: int, var_close: float) -> float:
        z30 = self._zret(30, var_close)
        z120 = self._zret(120, var_close)
        z1440 = self._zret(1440, var_close)
        z2h = self._zret(max(2, 2 * horizon_minutes), var_close)
        if horizon_minutes <= 30:
            signal = -0.35 * z2h - 0.35 * z30 - 0.15 * z120 - 0.15 * z1440
        else:
            signal = -0.15 * z30 - 0.25 * z120 - 0.60 * z1440
        return float(np.tanh(self.config.arrow_signal_scale * signal))

    def _transport_probability(self, horizon_minutes: int, d: float) -> tuple[float | None, float | None, int, int]:
        buf = self._transport_returns.get(horizon_minutes, [])
        if not buf:
            return None, None, 0, 0
        arr = np.array(buf, dtype=float)
        cfg = self.config
        def sym_tail(x: np.ndarray) -> float:
            if len(x) == 0:
                return float("nan")
            # D={Z,-Z}; P(D>d)=0.5[P(Z>d)+P(Z<-d)]
            return float(0.5 * (np.mean(x > d) + np.mean(x < -d)))
        p_recent = None
        nr = min(len(arr), cfg.recent_transport_window)
        if nr >= cfg.transport_min_recent:
            p_recent = sym_tail(arr[-nr:])
        p_long = None
        nl = min(len(arr), cfg.long_transport_window)
        if nl >= cfg.transport_min_long:
            p_long = sym_tail(arr[-nl:])
        return p_recent, p_long, nr, nl

    def predict_physical(
        self,
        *,
        side: Side,
        strike: float,
        horizon_seconds: float,
        market_p_yes: float | None = None,
    ) -> PhysicalPrediction:
        cfg = self.config
        if len(self.history) < cfg.min_history_points:
            raise ValueError(f"Need at least {cfg.min_history_points} bars before prediction.")
        _, _, _, closes, _ = self._arrays()
        spot = float(closes[-1])
        horizon_minutes = max(1, int(round(float(horizon_seconds) / 60.0)))
        var, var_close, volshock = self._variance_per_minute()
        sigma = spot * sqrt(max(var * horizon_minutes, 1e-18))
        sigma = _clip(
            sigma,
            cfg.vol_floor_dollars_15m * sqrt(horizon_minutes / 15.0),
            cfg.vol_ceiling_dollars_15m * sqrt(horizon_minutes / 15.0),
        )

        d = (float(strike) - spot) / max(sigma, 1e-12)
        p_anchor = _normal_cdf(-d)
        ell_anchor = _logit(p_anchor)
        arrow = self._arrow(horizon_minutes, var_close)
        static_gate = exp(-((abs(d) / cfg.boundary_arrow_gate_sigma) ** 2))
        ell_static = ell_anchor + cfg.boundary_arrow_strength * static_gate * arrow
        p_static = _sigmoid(ell_static)

        p_recent, p_long, n_recent, n_long = self._transport_probability(horizon_minutes, d)
        if p_recent is None:
            p_recent = p_anchor
        if p_long is None:
            p_long = p_anchor
        edge_gate = 1.0 / (1.0 + exp(-cfg.transport_edge_gate_steepness * (abs(d) - cfg.transport_edge_gate_center)))
        ell_transport = (
            _logit(p_static)
            + edge_gate * cfg.transport_recent_weight * (_logit(p_recent) - ell_anchor)
            + edge_gate * cfg.transport_long_weight * (_logit(p_long) - ell_anchor)
        )
        p_yes = _sigmoid(ell_transport / max(cfg.transport_temperature, 1e-6))

        contradiction = 0.0
        if market_p_yes is not None:
            contradiction = abs(_logit(float(market_p_yes)) - _logit(p_yes))

        p_side = p_yes if side == "yes" else 1.0 - p_yes
        side_probability = max(p_yes, 1.0 - p_yes)
        boundary_risk = exp(-abs(d))
        uncertainty = float(4.0 * p_side * (1.0 - p_side))
        confidence = 1.0 - uncertainty
        components = {
            "spot": spot,
            "strike": float(strike),
            "d_sigma": float(d),
            "abs_d_sigma": float(abs(d)),
            "p_anchor": float(p_anchor),
            "p_static_boundary_field": float(p_static),
            "p_recent_transport": float(p_recent),
            "p_long_transport": float(p_long),
            "p_yes": float(p_yes),
            "side_probability": float(side_probability),
            "edge_gate": float(edge_gate),
            "arrow": float(arrow),
            "static_gate": float(static_gate),
            "transport_recent_n": float(n_recent),
            "transport_long_n": float(n_long),
            "volshock": float(volshock),
            "market_contradiction_logit": float(contradiction),
            "edge_zone_ge_0p75": float(abs(d) >= 0.75),
            "tail_zone_ge_1p0": float(abs(d) >= 1.0),
            "deep_tail_zone_ge_1p5": float(abs(d) >= 1.5),
        }
        return PhysicalPrediction(
            side=side,
            p_terminal=float(p_side),
            p_yes=float(p_yes),
            p_side=float(p_side),
            fair_cents=float(100.0 * p_side),
            confidence=float(confidence),
            uncertainty=float(uncertainty),
            boundary_risk=float(boundary_risk),
            sigma_t_dollars=float(sigma),
            drift_t_dollars=0.0,
            seconds_to_close=float(horizon_seconds),
            components=components,
        )
