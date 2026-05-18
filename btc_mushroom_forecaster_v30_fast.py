"""BTC Mushroom Forecaster v0.30 research candidate.

v30 is a probability-surface experiment, not a live-bot patch.

It keeps v28's Brownian anchor, boundary arrow, and symmetric histogram
transport, but fixes one physics prior in the final settlement-average horizon:
once the forecast is already inside the averaging window, the remaining
variance of the unknown average scales as h^3 / (3 * delta^2), not h^2 / delta.

That keeps the horizon variance continuous at the start of the averaging window
and makes late-window probabilities reflect that most of the settlement average
has already been determined by the path.
"""
from __future__ import annotations

from dataclasses import dataclass

from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config


@dataclass
class FastMushroomV30Config(FastMushroomV28Config):
    settlement_average_seconds: float = 90.0


class FastMushroomFVEngineV30(FastMushroomFVEngineV28):
    """v0.30 FV engine with exact Brownian final-average variance."""

    def __init__(self, config: FastMushroomV30Config | None = None) -> None:
        super().__init__(config or FastMushroomV30Config())

    def effective_horizon_minutes(self, horizon_seconds: float) -> float:
        h_min = max(float(horizon_seconds) / 60.0, 1e-6)
        avg_min = max(float(self.config.settlement_average_seconds), 0.0) / 60.0
        if avg_min <= 0:
            return h_min
        if h_min >= avg_min:
            return max(h_min - (2.0 / 3.0) * avg_min, 0.02)
        return max((h_min * h_min * h_min) / (3.0 * avg_min * avg_min), 0.002)


FastMushroomConfig = FastMushroomV30Config
FastMushroomFVEngine = FastMushroomFVEngineV30
