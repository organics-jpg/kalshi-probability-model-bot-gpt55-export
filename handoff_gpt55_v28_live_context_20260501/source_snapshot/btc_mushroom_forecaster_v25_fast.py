
"""
BTC Mushroom Forecaster v0.24 — Fast Realtime FV Engine

Purpose
-------
A production-oriented, low-latency fair-value engine for the Kalshi BTC boundary
model. It keeps the v0.22 edge-zone transport logic but rewrites the state layer
for live websocket use:

- tick -> minute bar aggregation
- fixed-size ring buffers instead of list -> full numpy rebuilds
- rolling volatility gauges updated once per closed bar
- standardized residual transport buffers cached/sorted once per minute
- vectorized multi-strike, multi-market fair-value calls
- side-specific fair value and net edge helpers for Kalshi bid-only books

This is a *fair-value engine*, not an execution bot. It never places orders.

Model ancestry
--------------
v0.22:
    p_anchor = Phi((S_t - K) / sigma_t)
    weak time-mirror boundary field
    mirrored residual transport from resolved future returns

v0.24:
    same probability surface, optimized for speed and live operation.

Latency design
--------------
The expensive work happens only when a minute bar closes:
    - volatility rolling stats update
    - horizon sigma snapshots update
    - newly resolved standardized returns are harvested
    - transport sorted caches are invalidated

Per websocket tick:
    - update current forming bar
    - call predict_many / fair_value_many with vectorized strikes

Expected use:
    engine.update_tick(btc_price, ts)
    preds = engine.predict_many(strikes=[...], horizon_seconds=...)
    edges = engine.edge_many(strikes=[...], yes_ask_cents=[...], no_ask_cents=[...])

No future leakage:
    transport residuals are harvested only after the corresponding future horizon
    has fully resolved.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import exp, isfinite, log, sqrt
from typing import Iterable, Literal, Optional

import bisect
import time

import numpy as np

Side = Literal["yes", "no"]


# -----------------------------
# Numerical helpers
# -----------------------------

def _clip_scalar(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


def _sigmoid_np(x: np.ndarray | float) -> np.ndarray | float:
    x_arr = np.asarray(x, dtype=float)
    out = np.empty_like(x_arr, dtype=float)
    pos = x_arr >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-x_arr[pos]))
    ex = np.exp(x_arr[~pos])
    out[~pos] = ex / (1.0 + ex)
    if np.isscalar(x):
        return float(out)
    return out


def _logit_np(p: np.ndarray | float) -> np.ndarray | float:
    p_arr = np.clip(np.asarray(p, dtype=float), 1e-10, 1.0 - 1e-10)
    out = np.log(p_arr / (1.0 - p_arr))
    if np.isscalar(p):
        return float(out)
    return out


def _erf_approx_np(x: np.ndarray | float) -> np.ndarray | float:
    """Vectorized Abramowitz-Stegun erf approximation, max error about 1.5e-7."""
    x_arr = np.asarray(x, dtype=float)
    sign = np.sign(x_arr)
    ax = np.abs(x_arr)
    t = 1.0 / (1.0 + 0.3275911 * ax)
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    y = 1.0 - (((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * np.exp(-ax * ax))
    out = sign * y
    if np.isscalar(x):
        return float(out)
    return out


def _normal_cdf_np(z: np.ndarray | float) -> np.ndarray | float:
    out = 0.5 * (1.0 + _erf_approx_np(np.asarray(z, dtype=float) / sqrt(2.0)))
    if np.isscalar(z):
        return float(out)
    return out


# -----------------------------
# Config / outputs
# -----------------------------

@dataclass
class FastMushroomConfig:
    max_bars: int = 30000
    min_bars: int = 180

    vol_window_points: int = 600
    range_short_window: int = 60
    range_long_window: int = 360
    range_variance_weight: float = 0.50

    vol_floor_dollars_15m: float = 65.0
    vol_ceiling_dollars_15m: float = 1500.0

    boundary_arrow_strength: float = 0.25
    boundary_arrow_gate_sigma: float = 1.00
    arrow_signal_scale: float = 0.85

    transport_recent_weight: float = 0.30
    transport_long_weight: float = 0.30
    transport_temperature: float = 1.03
    transport_edge_gate_center: float = 0.55
    transport_edge_gate_steepness: float = 6.0
    recent_transport_window: int = 1440
    long_transport_window: int = 10080
    transport_min_recent: int = 240
    transport_min_long: int = 1440
    learned_horizons_minutes: tuple[int, ...] = (5, 10, 15, 30, 60)

    # Kalshi BTC crypto markets settle against a final-minute average. In live use,
    # setting this to 60 shrinks horizon variance slightly before the averaging
    # window begins. Set to 0 to exactly match v0.22 historical close-to-close tests.
    settlement_average_seconds: float = 0.0

    # Fast-fair-value trading diagnostics.
    default_fee_cents: float = 0.75
    default_slippage_cents: float = 0.25
    default_model_buffer_cents: float = 1.00


@dataclass
class FastPredictionBatch:
    strikes: np.ndarray
    horizon_seconds: float
    horizon_minutes: int
    spot: float
    p_yes: np.ndarray
    p_no: np.ndarray
    fair_yes_cents: np.ndarray
    fair_no_cents: np.ndarray
    sigma_t_dollars: float
    d_sigma: np.ndarray
    side_probability: np.ndarray
    components: dict[str, np.ndarray | float] = field(default_factory=dict)


@dataclass
class EdgeBatch:
    strikes: np.ndarray
    p_yes: np.ndarray
    fair_yes_cents: np.ndarray
    fair_no_cents: np.ndarray
    yes_net_edge_cents: np.ndarray
    no_net_edge_cents: np.ndarray
    best_side: np.ndarray
    best_edge_cents: np.ndarray
    best_fair_cents: np.ndarray
    side_probability: np.ndarray
    tradeable: np.ndarray
    components: dict[str, np.ndarray | float] = field(default_factory=dict)


# -----------------------------
# Rolling stats and transport buffers
# -----------------------------

class RollingWindowStats:
    """O(1) rolling mean/variance of log returns."""

    def __init__(self, maxlen: int) -> None:
        self.maxlen = int(maxlen)
        self.buf: list[float] = []
        self.start = 0
        self.count = 0
        self.sum = 0.0
        self.sumsq = 0.0

    def append(self, x: float) -> None:
        x = float(x)
        if self.count < self.maxlen:
            self.buf.append(x)
            self.count += 1
            self.sum += x
            self.sumsq += x * x
            return
        old = self.buf[self.start]
        self.buf[self.start] = x
        self.start = (self.start + 1) % self.maxlen
        self.sum += x - old
        self.sumsq += x * x - old * old

    def mean(self) -> float:
        return self.sum / self.count if self.count else 0.0

    def var(self) -> float:
        if self.count < 2:
            return 1e-12
        mu = self.sum / self.count
        return max((self.sumsq - self.count * mu * mu) / (self.count - 1), 1e-18)

    def n(self) -> int:
        return self.count


class RollingSum:
    """O(1) rolling sum for range variance terms."""

    def __init__(self, maxlen: int) -> None:
        self.maxlen = int(maxlen)
        self.buf: list[float] = []
        self.start = 0
        self.count = 0
        self.sum = 0.0

    def append(self, x: float) -> None:
        x = float(x)
        if self.count < self.maxlen:
            self.buf.append(x)
            self.count += 1
            self.sum += x
            return
        old = self.buf[self.start]
        self.buf[self.start] = x
        self.start = (self.start + 1) % self.maxlen
        self.sum += x - old

    def mean(self) -> float:
        return self.sum / self.count if self.count else 0.0

    def n(self) -> int:
        return self.count


class TransportBuffer:
    """Stores resolved standardized returns and caches sorted recent/long windows."""

    def __init__(self, recent_window: int, long_window: int, max_keep: int | None = None) -> None:
        self.recent_window = int(recent_window)
        self.long_window = int(long_window)
        self.max_keep = int(max_keep or max(long_window * 2, recent_window * 3))
        self.values: list[float] = []
        self._version = 0
        self._cache_version = -1
        self._sorted_recent: np.ndarray | None = None
        self._sorted_long: np.ndarray | None = None

    def append(self, z: float) -> None:
        if not isfinite(z):
            return
        self.values.append(float(_clip_scalar(z, -12.0, 12.0)))
        if len(self.values) > self.max_keep:
            del self.values[: len(self.values) - self.max_keep]
        self._version += 1

    def __len__(self) -> int:
        return len(self.values)

    def _refresh(self) -> None:
        if self._cache_version == self._version:
            return
        if not self.values:
            self._sorted_recent = np.array([], dtype=float)
            self._sorted_long = np.array([], dtype=float)
        else:
            arr = np.asarray(self.values, dtype=float)
            self._sorted_recent = np.sort(arr[-min(len(arr), self.recent_window):])
            self._sorted_long = np.sort(arr[-min(len(arr), self.long_window):])
        self._cache_version = self._version

    def tail_prob(self, d: np.ndarray, min_recent: int, min_long: int) -> tuple[np.ndarray | None, np.ndarray | None, int, int]:
        self._refresh()
        d = np.asarray(d, dtype=float)

        def calc(sorted_arr: np.ndarray, min_n: int) -> np.ndarray | None:
            n = int(len(sorted_arr))
            if n < min_n:
                return None
            # D={Z,-Z}; P(D>d)=0.5[P(Z>d)+P(Z<-d)]
            right = np.searchsorted(sorted_arr, d, side="right")
            count_gt = n - right
            left = np.searchsorted(sorted_arr, -d, side="left")
            count_lt_negd = left
            return 0.5 * (count_gt + count_lt_negd) / max(n, 1)

        sr = self._sorted_recent if self._sorted_recent is not None else np.array([], dtype=float)
        sl = self._sorted_long if self._sorted_long is not None else np.array([], dtype=float)
        return calc(sr, min_recent), calc(sl, min_long), len(sr), len(sl)


# -----------------------------
# Main engine
# -----------------------------

class FastMushroomFVEngine:
    """Fast live fair-value engine for BTC boundary markets.

    Feed 1-minute bars directly or feed websocket ticks via update_tick().
    """

    def __init__(self, config: FastMushroomConfig | None = None) -> None:
        self.config = config or FastMushroomConfig()

        n = self.config.max_bars
        self.open = np.full(n, np.nan, dtype=float)
        self.high = np.full(n, np.nan, dtype=float)
        self.low = np.full(n, np.nan, dtype=float)
        self.close = np.full(n, np.nan, dtype=float)
        self.volume = np.zeros(n, dtype=float)
        self.epoch_sec = np.zeros(n, dtype=np.int64)
        self.abs_index_at_slot = np.full(n, -1, dtype=np.int64)

        self.count = 0
        self.next_slot = 0
        self.abs_index = -1

        self.ret_stats = RollingWindowStats(self.config.vol_window_points)
        self.range_short = RollingSum(self.config.range_short_window)
        self.range_long = RollingSum(self.config.range_long_window)

        self.horizons = tuple(int(h) for h in self.config.learned_horizons_minutes)
        self.hidx = {h: i for i, h in enumerate(self.horizons)}
        self.sigma_snapshot = np.full((n, len(self.horizons)), np.nan, dtype=float)
        self.transport = {
            h: TransportBuffer(
                self.config.recent_transport_window,
                self.config.long_transport_window,
            )
            for h in self.horizons
        }

        self.current_minute: int | None = None
        self.current_open: float | None = None
        self.current_high: float | None = None
        self.current_low: float | None = None
        self.current_close: float | None = None
        self.current_volume: float = 0.0
        self.last_live_price: float | None = None
        self.last_live_ts: datetime | None = None

    # ---------- ingestion ----------

    @staticmethod
    def _to_epoch(ts: datetime | float | int | None) -> int:
        if ts is None:
            return int(time.time())
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return int(ts.timestamp())
        return int(ts)

    def update_tick(self, price: float, ts: datetime | float | int | None = None, volume: float = 0.0) -> bool:
        """Update with a live spot tick.

        Returns True if this tick closed and committed a minute bar.
        """
        price = float(price)
        if not isfinite(price) or price <= 0:
            return False
        epoch = self._to_epoch(ts)
        minute = epoch // 60

        self.last_live_price = price
        self.last_live_ts = datetime.fromtimestamp(epoch, tz=timezone.utc)

        if self.current_minute is None:
            self.current_minute = minute
            self.current_open = self.current_high = self.current_low = self.current_close = price
            self.current_volume = float(volume or 0.0)
            return False

        if minute == self.current_minute:
            self.current_high = max(float(self.current_high), price)
            self.current_low = min(float(self.current_low), price)
            self.current_close = price
            self.current_volume += float(volume or 0.0)
            return False

        # Commit the old minute bar.
        committed = self.update_bar(
            open=float(self.current_open),
            high=float(self.current_high),
            low=float(self.current_low),
            close=float(self.current_close),
            volume=float(self.current_volume),
            ts=self.current_minute * 60,
        )

        # Start new forming minute. We do not fill missing minutes; live websocket
        # feeds should be continuous. If gaps occur, the engine naturally uses the
        # next observed bar and rolling stats remain conservative.
        self.current_minute = minute
        self.current_open = self.current_high = self.current_low = self.current_close = price
        self.current_volume = float(volume or 0.0)
        return committed

    def flush_current_bar(self) -> bool:
        """Commit the forming bar. Useful during tests/shutdown."""
        if self.current_minute is None or self.current_close is None:
            return False
        ok = self.update_bar(
            open=float(self.current_open),
            high=float(self.current_high),
            low=float(self.current_low),
            close=float(self.current_close),
            volume=float(self.current_volume),
            ts=self.current_minute * 60,
        )
        self.current_minute = None
        self.current_open = self.current_high = self.current_low = self.current_close = None
        self.current_volume = 0.0
        return ok

    def update_bar(
        self,
        *,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float = 0.0,
        ts: datetime | float | int | None = None,
    ) -> bool:
        op = float(open)
        hi = float(high)
        lo = float(low)
        cl = float(close)
        if not all(isfinite(x) for x in (op, hi, lo, cl)) or min(op, hi, lo, cl) <= 0:
            return False
        hi = max(hi, op, cl)
        lo = min(lo, op, cl)

        prev_close = self.get_close_lag(0) if self.count > 0 else np.nan

        slot = self.next_slot
        self.abs_index += 1
        self.open[slot] = op
        self.high[slot] = hi
        self.low[slot] = lo
        self.close[slot] = cl
        self.volume[slot] = float(volume or 0.0)
        self.epoch_sec[slot] = self._to_epoch(ts)
        self.abs_index_at_slot[slot] = self.abs_index

        self.next_slot = (self.next_slot + 1) % self.config.max_bars
        self.count = min(self.count + 1, self.config.max_bars)

        if isfinite(prev_close) and prev_close > 0:
            r = log(cl / prev_close)
            self.ret_stats.append(r)
        rr = log(hi / lo)
        rv_range = (rr * rr) / (4.0 * log(2.0))
        self.range_short.append(rv_range)
        self.range_long.append(rv_range)

        # Store current horizon sigma snapshots for future z-return harvesting.
        for h in self.horizons:
            sigma = self.current_sigma_dollars(horizon_minutes=h, spot=cl)
            self.sigma_snapshot[slot, self.hidx[h]] = sigma

        # Harvest any returns that just resolved at this bar.
        self._harvest_resolved_returns(current_abs=self.abs_index, current_close=cl)
        self.last_live_price = cl
        return True

    # ---------- ring lookup ----------

    def _slot_for_abs(self, abs_idx: int) -> int | None:
        if abs_idx < 0 or self.count == 0:
            return None
        # Since abs indices are written sequentially into abs_index % max_bars.
        slot = abs_idx % self.config.max_bars
        if self.abs_index_at_slot[slot] != abs_idx:
            return None
        return int(slot)

    def get_close_lag(self, lag_minutes: int) -> float:
        abs_idx = self.abs_index - int(lag_minutes)
        slot = self._slot_for_abs(abs_idx)
        if slot is None:
            return float("nan")
        return float(self.close[slot])

    # ---------- feature state ----------

    def current_spot(self) -> float:
        if self.last_live_price is not None:
            return float(self.last_live_price)
        if self.count > 0:
            return self.get_close_lag(0)
        raise ValueError("No spot data available yet.")

    def current_variance_per_minute(self) -> tuple[float, float, float]:
        rv_close = self.ret_stats.var()
        rs = self.range_short.mean() if self.range_short.n() else rv_close
        rl = self.range_long.mean() if self.range_long.n() else rv_close
        range_var = 0.5 * rs + 0.5 * rl
        blend = (1.0 - self.config.range_variance_weight) * rv_close + self.config.range_variance_weight * range_var
        volshock = log(max(range_var, 1e-18) / max(rv_close, 1e-18))
        return max(blend, 1e-18), max(rv_close, 1e-18), float(_clip_scalar(volshock, -3.0, 3.0))

    def effective_horizon_minutes(self, horizon_seconds: float) -> float:
        h_min = max(float(horizon_seconds) / 60.0, 1e-6)
        avg_min = max(float(self.config.settlement_average_seconds), 0.0) / 60.0
        if avg_min <= 0:
            return h_min
        # For Brownian path with final averaging interval delta before T:
        # Var(average over [T-delta,T]) = sigma^2 * (T - 2delta/3)
        # as long as T >= delta. Clamp for very late forecasts.
        if h_min >= avg_min:
            return max(h_min - (2.0 / 3.0) * avg_min, 0.05)
        # If already inside the final averaging window, uncertainty decays faster.
        return max(h_min * h_min / max(avg_min, 1e-6), 0.02)

    def current_sigma_dollars(self, horizon_minutes: int | float, spot: float | None = None) -> float:
        spot = float(spot if spot is not None else self.current_spot())
        var, _, _ = self.current_variance_per_minute()
        hm = max(float(horizon_minutes), 1e-6)
        sigma = spot * sqrt(max(var * hm, 1e-18))
        floor = self.config.vol_floor_dollars_15m * sqrt(hm / 15.0)
        ceil = self.config.vol_ceiling_dollars_15m * sqrt(hm / 15.0)
        return float(_clip_scalar(sigma, floor, ceil))

    def _zret(self, k: int, var_close: float, spot: float) -> float:
        if k <= 0:
            return 0.0
        past = self.get_close_lag(k)
        if not isfinite(past) or past <= 0 or spot <= 0:
            return 0.0
        r = log(spot / past)
        return float(_clip_scalar(r / sqrt(max(var_close * k, 1e-18)), -4.0, 4.0))

    def _arrow(self, horizon_minutes: int, var_close: float, spot: float) -> float:
        z30 = self._zret(30, var_close, spot)
        z120 = self._zret(120, var_close, spot)
        z1440 = self._zret(1440, var_close, spot)
        z2h = self._zret(max(2, 2 * int(round(horizon_minutes))), var_close, spot)
        if horizon_minutes <= 30:
            signal = -0.35 * z2h - 0.35 * z30 - 0.15 * z120 - 0.15 * z1440
        else:
            signal = -0.15 * z30 - 0.25 * z120 - 0.60 * z1440
        return float(np.tanh(self.config.arrow_signal_scale * signal))

    def _harvest_resolved_returns(self, current_abs: int, current_close: float) -> None:
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
                self.transport[h].append(z)

    # ---------- prediction ----------

    def ready(self) -> bool:
        return self.count >= self.config.min_bars and self.ret_stats.n() >= 2

    def _nearest_learned_horizon(self, horizon_minutes: int) -> int:
        return min(self.horizons, key=lambda h: abs(h - horizon_minutes))

    def predict_many(self, *, strikes: Iterable[float], horizon_seconds: float) -> FastPredictionBatch:
        if not self.ready():
            raise ValueError(f"Need at least {self.config.min_bars} closed bars before prediction.")

        strikes_arr = np.asarray(list(strikes), dtype=float)
        if strikes_arr.ndim != 1:
            strikes_arr = strikes_arr.reshape(-1)
        if len(strikes_arr) == 0:
            raise ValueError("strikes must not be empty")

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

    def predict_one(self, *, strike: float, horizon_seconds: float, side: Side = "yes") -> dict[str, float | str]:
        batch = self.predict_many(strikes=[strike], horizon_seconds=horizon_seconds)
        p_side = float(batch.p_yes[0] if side == "yes" else batch.p_no[0])
        return {
            "side": side,
            "spot": batch.spot,
            "strike": float(strike),
            "horizon_seconds": float(horizon_seconds),
            "p_yes": float(batch.p_yes[0]),
            "p_no": float(batch.p_no[0]),
            "p_side": p_side,
            "fair_cents": 100.0 * p_side,
            "sigma_t_dollars": batch.sigma_t_dollars,
            "d_sigma": float(batch.d_sigma[0]),
            "side_probability": float(batch.side_probability[0]),
            "arrow": float(batch.components["arrow"]),
        }

    def edge_many(
        self,
        *,
        strikes: Iterable[float],
        horizon_seconds: float,
        yes_ask_cents: Iterable[float],
        no_ask_cents: Iterable[float],
        fee_cents: float | None = None,
        slippage_cents: float | None = None,
        model_buffer_cents: float | None = None,
        min_net_edge_cents: float = 2.0,
    ) -> EdgeBatch:
        batch = self.predict_many(strikes=strikes, horizon_seconds=horizon_seconds)
        yes_ask = np.asarray(list(yes_ask_cents), dtype=float)
        no_ask = np.asarray(list(no_ask_cents), dtype=float)
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
            components={**batch.components, "sigma_t_dollars": float(batch.sigma_t_dollars), "d_sigma": batch.d_sigma},
        )

    @staticmethod
    def asks_from_kalshi_bids(
        *,
        best_yes_bid_cents: Iterable[float],
        best_no_bid_cents: Iterable[float],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Derive asks from Kalshi-style yes/no bid books.

        A NO bid at y implies YES ask = 100-y.
        A YES bid at x implies NO ask = 100-x.
        """
        yes_bid = np.asarray(list(best_yes_bid_cents), dtype=float)
        no_bid = np.asarray(list(best_no_bid_cents), dtype=float)
        yes_ask = 100.0 - no_bid
        no_ask = 100.0 - yes_bid
        return yes_ask, no_ask


# -----------------------------
# Optional final-minute average settlement helper
# -----------------------------

def final_minute_average_probability(
    *,
    side: Side,
    strike: float,
    observed_rti_sum: float,
    observed_count: int,
    current_spot: float,
    sigma_remaining_avg: float,
) -> float:
    """Probability of final 60-second average settling on side after partial RTI samples.

    If n samples from the final 60-second settlement average are already known,
    the remaining r samples need average:

        required_remaining_avg = (60*K - observed_sum) / r

    This helper prices that remaining-average event with a normal approximation.
    It is separate from the main model because live RTI samples may come from
    Kalshi/CFB settlement feed rather than exchange candles.
    """
    n = int(observed_count)
    if n >= 60:
        avg = float(observed_rti_sum) / 60.0
        p_yes = 1.0 if avg >= float(strike) else 0.0
    else:
        r = max(60 - n, 1)
        required = (60.0 * float(strike) - float(observed_rti_sum)) / r
        z = (float(current_spot) - required) / max(float(sigma_remaining_avg), 1e-12)
        p_yes = float(_normal_cdf_np(z))
    return p_yes if side == "yes" else 1.0 - p_yes


# ---------------------------------------------------------------------------
# v0.25 extension — Histogram Transport Accelerator
# ---------------------------------------------------------------------------
#
# v0.24 used exact sorted empirical residual buffers. That is accurate, but
# each cache refresh sorts the recent/long residual windows. In live use this
# is usually acceptable once per closed bar, but in dense research/audit and
# multi-horizon websocket loops it is unnecessary work.
#
# v0.25 replaces exact sorting with fixed-grid mirrored residual histograms:
# every resolved Z adds mass at Z and -Z. Tail probabilities are read from
# cumulative histogram counts with a tiny standard-normal prior. This gives:
#   - O(1) residual update
#   - O(num_bins) cache refresh, independent of window length
#   - smoother tail probabilities, which reduces sampling noise without adding
#     directional overfit
#
# The public API is kept compatible with v0.24.


@dataclass
class FastMushroomV25Config(FastMushroomConfig):
    transport_hist_bins: int = 1001
    transport_hist_zmax: float = 8.0
    transport_recent_prior_count: float = 24.0
    transport_long_prior_count: float = 96.0
    # Blend a small amount of anchor probability into transport deltas in very
    # sparse or unstable histogram states. This is a speed-safe regularizer.
    histogram_anchor_floor_weight: float = 0.04


class HistogramTransportBuffer:
    """Fixed-grid symmetric transport buffer.

    Stores only bin IDs in rolling queues while maintaining recent and long
    histograms over D={Z,-Z}. Query is an empirical-plus-prior P(D>d).
    """

    def __init__(
        self,
        recent_window: int,
        long_window: int,
        *,
        bins: int = 1001,
        zmax: float = 8.0,
        recent_prior_count: float = 24.0,
        long_prior_count: float = 96.0,
    ) -> None:
        from collections import deque

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
        self.bin_width = float(self.edges[1] - self.edges[0])

        # Standard-normal prior mass per histogram bin, symmetrized naturally.
        prior_cdf_hi = _normal_cdf_np(self.edges[1:])
        prior_cdf_lo = _normal_cdf_np(self.edges[:-1])
        pm = np.asarray(prior_cdf_hi - prior_cdf_lo, dtype=float)
        pm = np.maximum(pm, 0.0)
        s = float(pm.sum())
        self.prior_mass = pm / s if s > 0 else np.full(self.bins, 1.0 / self.bins)
        self.prior_cum = np.cumsum(self.prior_mass)

        self.recent_queue = deque()
        self.long_queue = deque()
        self.recent_hist = np.zeros(self.bins, dtype=float)
        self.long_hist = np.zeros(self.bins, dtype=float)
        self.recent_n_z = 0
        self.long_n_z = 0
        self._version = 0
        self._cache_version = -1
        self._recent_cum: np.ndarray | None = None
        self._long_cum: np.ndarray | None = None

    def _bin_index(self, z: float) -> int:
        zc = float(_clip_scalar(z, -self.zmax + 1e-12, self.zmax - 1e-12))
        idx = int((zc + self.zmax) / (2.0 * self.zmax) * self.bins)
        if idx < 0:
            return 0
        if idx >= self.bins:
            return self.bins - 1
        return idx

    def _add_sym(self, hist: np.ndarray, z: float, sign: float) -> tuple[int, int]:
        i = self._bin_index(z)
        j = self._bin_index(-z)
        hist[i] += sign
        hist[j] += sign
        return i, j

    def append(self, z: float) -> None:
        if not isfinite(z):
            return
        z = float(_clip_scalar(z, -12.0, 12.0))

        pair = (self._bin_index(z), self._bin_index(-z))

        self.recent_queue.append(pair)
        self.recent_hist[pair[0]] += 1.0
        self.recent_hist[pair[1]] += 1.0
        self.recent_n_z += 1
        if self.recent_n_z > self.recent_window:
            old = self.recent_queue.popleft()
            self.recent_hist[old[0]] -= 1.0
            self.recent_hist[old[1]] -= 1.0
            self.recent_n_z -= 1

        self.long_queue.append(pair)
        self.long_hist[pair[0]] += 1.0
        self.long_hist[pair[1]] += 1.0
        self.long_n_z += 1
        if self.long_n_z > self.long_window:
            old = self.long_queue.popleft()
            self.long_hist[old[0]] -= 1.0
            self.long_hist[old[1]] -= 1.0
            self.long_n_z -= 1

        self._version += 1

    def __len__(self) -> int:
        return int(self.long_n_z)

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
        n_z: int,
        min_n: int,
        prior_count: float,
    ) -> np.ndarray | None:
        if int(n_z) < int(min_n):
            return None

        d = np.asarray(d, dtype=float)
        total_emp = float(max(2 * int(n_z), 1))

        # Empirical tail using midpoints. This is intentionally smooth-ish and
        # avoids repeated full sorting. Values beyond the grid saturate.
        idx = np.searchsorted(self.mids, d, side="right")
        idx_clip = np.clip(idx, 0, self.bins)
        emp_le = np.zeros_like(d, dtype=float)
        mask_mid = idx_clip > 0
        emp_le[mask_mid] = cum[idx_clip[mask_mid] - 1]
        emp_tail = np.clip((total_emp - emp_le) / total_emp, 0.0, 1.0)

        if prior_count <= 0:
            return emp_tail

        # Histogrammed normal prior tail acts as a small density regularizer.
        # Using the same grid avoids an erf call on every live prediction.
        prior_le = np.zeros_like(d, dtype=float)
        prior_le[mask_mid] = self.prior_cum[idx_clip[mask_mid] - 1]
        prior_tail = np.clip(1.0 - prior_le, 0.0, 1.0)
        alpha = float(prior_count)
        return np.clip((total_emp * emp_tail + alpha * prior_tail) / (total_emp + alpha), 1e-8, 1.0 - 1.0e-8)

    def tail_prob(self, d: np.ndarray, min_recent: int, min_long: int) -> tuple[np.ndarray | None, np.ndarray | None, int, int]:
        self._refresh()
        d = np.asarray(d, dtype=float)
        recent = self._tail_from_hist(
            d,
            self.recent_hist,
            self._recent_cum if self._recent_cum is not None else np.zeros(self.bins),
            self.recent_n_z,
            min_recent,
            self.recent_prior_count,
        )
        long = self._tail_from_hist(
            d,
            self.long_hist,
            self._long_cum if self._long_cum is not None else np.zeros(self.bins),
            self.long_n_z,
            min_long,
            self.long_prior_count,
        )
        return recent, long, int(self.recent_n_z), int(self.long_n_z)


# Preserve v0.24 names for explicit fallback.
FastMushroomFVEngineV24 = FastMushroomFVEngine
FastMushroomConfigV24 = FastMushroomConfig


class FastMushroomFVEngineV25(FastMushroomFVEngineV24):
    """v0.25 low-latency engine using histogram residual transport.

    Same public methods as v0.24:
        update_tick, update_bar, predict_many, edge_many, asks_from_kalshi_bids

    v0.25 is intended as the default live shadow FV engine. It keeps the v0.22
    probability surface but replaces exact sorting with histogram transport.
    """

    def __init__(self, config: FastMushroomV25Config | None = None) -> None:
        cfg = config or FastMushroomV25Config()
        super().__init__(cfg)
        self.config = cfg
        self.transport = {
            h: HistogramTransportBuffer(
                self.config.recent_transport_window,
                self.config.long_transport_window,
                bins=self.config.transport_hist_bins,
                zmax=self.config.transport_hist_zmax,
                recent_prior_count=self.config.transport_recent_prior_count,
                long_prior_count=self.config.transport_long_prior_count,
            )
            for h in self.horizons
        }


# v0.25 default aliases. Code that imports FastMushroomFVEngine from this file
# gets the fast histogram engine by default, while V24 aliases remain available.
FastMushroomConfig = FastMushroomV25Config
FastMushroomFVEngine = FastMushroomFVEngineV25
