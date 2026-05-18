"""BTC Mushroom Forecaster v0.39 research candidate.

v39 is a probability-surface experiment, not a live-bot patch.

The v38 surface is the best retrospective pure FV probability model overall,
but horizon diagnostics showed a narrow exception: the old live-v28 surface is
more useful in the 420s-to-600s mid-market band. v39 questions the prior that a
single settlement/proxy surface should dominate every horizon:

- use v38 everywhere by default;
- use the v28 live FV surface in the 420-600 second band;
- keep both engines fully independent and updated with the same bars;
- expose the same low-latency prediction API used by the replay probes.

This is intentionally blunt for auditability. It should only survive if the
official replay and block audits show that the mid-horizon fallback is not a
regime-fit artifact.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from btc_mushroom_forecaster_v25_fast import FastPredictionBatch
from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config
from btc_mushroom_forecaster_v37_fast import FastMushroomV37Config
from btc_mushroom_forecaster_v38_fast import FastMushroomFVEngineV38, FastMushroomV38Config


@dataclass
class FastMushroomV39Config(FastMushroomV38Config):
    mid_horizon_fallback_start_seconds: float = 420.0
    mid_horizon_fallback_end_seconds: float = 600.0


class FastMushroomFVEngineV39:
    """v0.39 FV wrapper using v38 except for a v28 mid-horizon fallback."""

    def __init__(self, config: FastMushroomV39Config | None = None) -> None:
        self.config = config or FastMushroomV39Config()
        self.v38 = FastMushroomFVEngineV38(self.config)
        self.v28 = FastMushroomFVEngineV28(FastMushroomV28Config())

    def update_tick(self, price: float, ts=None, volume: float = 0.0) -> bool:
        committed38 = self.v38.update_tick(price, ts=ts, volume=volume)
        committed28 = self.v28.update_tick(price, ts=ts, volume=volume)
        return bool(committed38 or committed28)

    def flush_current_bar(self) -> bool:
        ok38 = self.v38.flush_current_bar()
        ok28 = self.v28.flush_current_bar()
        return bool(ok38 or ok28)

    def update_bar(
        self,
        *,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float = 0.0,
        ts=None,
    ) -> bool:
        ok38 = self.v38.update_bar(open=open, high=high, low=low, close=close, volume=volume, ts=ts)
        ok28 = self.v28.update_bar(open=open, high=high, low=low, close=close, volume=volume, ts=ts)
        return bool(ok38 and ok28)

    def ready(self) -> bool:
        return bool(self.v38.ready() and self.v28.ready())

    def predict_many(self, *, strikes: Iterable[float] | np.ndarray, horizon_seconds: float) -> FastPredictionBatch:
        pred38 = self.v38.predict_many(strikes=strikes, horizon_seconds=horizon_seconds)
        start = float(self.config.mid_horizon_fallback_start_seconds)
        end = float(self.config.mid_horizon_fallback_end_seconds)
        horizon = float(horizon_seconds)
        if not (start <= horizon <= end):
            components = {
                **pred38.components,
                "v39_mid_horizon_v28_weight": 0.0,
                "v39_p_v38": pred38.p_yes,
                "v39_p_v28": np.full_like(pred38.p_yes, np.nan, dtype=float),
            }
            return FastPredictionBatch(**{**pred38.__dict__, "components": components})

        pred28 = self.v28.predict_many(strikes=strikes, horizon_seconds=horizon_seconds)
        p_yes = np.clip(np.asarray(pred28.p_yes, dtype=float), 1e-8, 1.0 - 1e-8)
        p_no = 1.0 - p_yes
        components = {
            **pred38.components,
            "v39_mid_horizon_v28_weight": 1.0,
            "v39_p_v38": pred38.p_yes,
            "v39_p_v28": pred28.p_yes,
            "v39_v28_sigma_t_dollars": float(pred28.sigma_t_dollars),
            "v39_v38_sigma_t_dollars": float(pred38.sigma_t_dollars),
        }
        return FastPredictionBatch(
            strikes=pred38.strikes,
            horizon_seconds=pred38.horizon_seconds,
            horizon_minutes=pred38.horizon_minutes,
            spot=pred38.spot,
            p_yes=p_yes,
            p_no=p_no,
            fair_yes_cents=100.0 * p_yes,
            fair_no_cents=100.0 * p_no,
            sigma_t_dollars=pred28.sigma_t_dollars,
            d_sigma=pred28.d_sigma,
            side_probability=np.maximum(p_yes, p_no),
            components=components,
        )


FastMushroomConfig = FastMushroomV39Config
FastMushroomFVEngine = FastMushroomFVEngineV39
