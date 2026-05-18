"""BTC Mushroom Forecaster v0.31 research candidate.

v31 is a probability-surface experiment, not a live-bot patch.

The v30 exact Brownian final-average variance improved the final minute, but it
collapsed uncertainty too early in the 60-90s band when replayed through the
Coinbase 1m candle proxy. v31 keeps the empirically useful 90s effective
settlement horizon before the last minute, then applies the exact Brownian
inside-average variance only once the forecast is within the final 60 seconds.

Interpretation: the live FV surface needs two clocks:
- an effective settlement/proxy horizon, currently 90s;
- a known-final-average clock, currently the last 60s.
"""
from __future__ import annotations

from dataclasses import dataclass

from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config


@dataclass
class FastMushroomV31Config(FastMushroomV28Config):
    settlement_average_seconds: float = 90.0
    exact_average_inside_seconds: float = 60.0


class FastMushroomFVEngineV31(FastMushroomFVEngineV28):
    """v0.31 FV engine with proxy-aware final-average collapse."""

    def __init__(self, config: FastMushroomV31Config | None = None) -> None:
        super().__init__(config or FastMushroomV31Config())

    def effective_horizon_minutes(self, horizon_seconds: float) -> float:
        h_min = max(float(horizon_seconds) / 60.0, 1e-6)
        avg_min = max(float(self.config.settlement_average_seconds), 0.0) / 60.0
        exact_inside_min = max(float(self.config.exact_average_inside_seconds), 0.0) / 60.0
        if avg_min <= 0:
            return h_min

        if exact_inside_min > 0 and h_min <= min(exact_inside_min, avg_min):
            return max((h_min * h_min * h_min) / (3.0 * avg_min * avg_min), 0.002)

        if h_min >= avg_min:
            return max(h_min - (2.0 / 3.0) * avg_min, 0.02)
        return max((h_min * h_min) / max(avg_min, 1e-6), 0.02)


FastMushroomConfig = FastMushroomV31Config
FastMushroomFVEngine = FastMushroomFVEngineV31
